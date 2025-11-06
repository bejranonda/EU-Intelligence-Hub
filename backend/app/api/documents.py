"""Document upload and processing API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import logging
import io
from datetime import datetime

from app.database import get_db
from app.models.models import Article, Keyword, KeywordArticle
from app.services.sentiment import SentimentAnalyzer
from app.services.keyword_extractor import KeywordExtractor
from app.services.embeddings import get_embedding_generator

logger = logging.getLogger(__name__)

router = APIRouter()


async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text from uploaded file.

    Supports: .txt, .pdf, .docx

    Args:
        file: Uploaded file

    Returns:
        str: Extracted text
    """
    content = await file.read()

    # Text files
    if file.filename.endswith(".txt"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")

    # PDF files
    elif file.filename.endswith(".pdf"):
        try:
            import PyPDF2

            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    # DOCX files
    elif file.filename.endswith(".docx"):
        try:
            import docx

            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: .txt, .pdf, .docx",
        )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    source: Optional[str] = Form("Manual Upload"),
    db: Session = Depends(get_db),
):
    """
    Upload a document and extract keywords with sentiment analysis.

    Supports .txt, .pdf, and .docx files.

    Args:
        file: Document file
        title: Optional custom title (uses filename if not provided)
        source: Source attribution
        db: Database session

    Returns:
        dict: Extracted keywords and sentiment analysis
    """
    try:
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

        # Reset file pointer
        await file.seek(0)

        # Extract text
        text = await extract_text_from_file(file)

        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400, detail="Document is too short or empty"
            )

        # Use filename as title if not provided
        doc_title = title or file.filename

        # Create summary (first 500 characters)
        summary = text[:500] + "..." if len(text) > 500 else text

        # Initialize services
        sentiment_analyzer = SentimentAnalyzer()
        keyword_extractor = KeywordExtractor()
        embedding_service = get_embedding_generator()

        # Analyze sentiment
        sentiment_result = await sentiment_analyzer.analyze_article(text)

        # Extract keywords
        keyword_result = await keyword_extractor.extract_all(text)

        # Generate embedding
        embedding = embedding_service.generate_embedding(text)

        # Create article record
        article = Article(
            title=doc_title,
            summary=summary,
            full_text=text,
            source=source,
            source_url=None,
            published_date=datetime.utcnow(),
            sentiment_overall=sentiment_result.get("overall_polarity"),
            sentiment_confidence=sentiment_result.get("confidence"),
            sentiment_classification=sentiment_result.get("classification"),
            sentiment_subjectivity=sentiment_result.get("subjectivity"),
            emotion_positive=sentiment_result.get("emotions", {}).get("positive"),
            emotion_negative=sentiment_result.get("emotions", {}).get("negative"),
            emotion_neutral=sentiment_result.get("emotions", {}).get("neutral"),
            classification=keyword_result.get("classification", "MIXED"),
            embedding=embedding,
        )

        db.add(article)
        db.flush()  # Get article ID

        # Process and associate keywords
        extracted_keywords = []
        for kw_data in keyword_result.get("keywords", []):
            keyword_text = (
                kw_data.get("text", kw_data) if isinstance(kw_data, dict) else kw_data
            )

            # Check if keyword exists
            keyword = (
                db.query(Keyword).filter(Keyword.keyword_en == keyword_text).first()
            )

            if not keyword:
                # Create new keyword
                keyword = Keyword(
                    keyword_en=keyword_text,
                    keyword_th=keyword_text,  # TODO: Add translation
                    category="general",
                )
                db.add(keyword)
                db.flush()

            # Associate with article
            keyword_article = KeywordArticle(
                keyword_id=keyword.id, article_id=article.id
            )
            db.add(keyword_article)

            extracted_keywords.append(
                {
                    "id": keyword.id,
                    "keyword": keyword.keyword_en,
                    "category": keyword.category,
                }
            )

        db.commit()

        return {
            "success": True,
            "article": {
                "id": article.id,
                "title": article.title,
                "source": article.source,
                "word_count": len(text.split()),
            },
            "sentiment": {
                "overall": sentiment_result.get("overall_polarity"),
                "classification": sentiment_result.get("classification"),
                "confidence": sentiment_result.get("confidence"),
            },
            "keywords": extracted_keywords,
            "classification": keyword_result.get("classification"),
            "message": f"Document processed successfully. Extracted {len(extracted_keywords)} keywords.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )
