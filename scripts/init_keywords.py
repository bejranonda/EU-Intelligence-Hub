#!/usr/bin/env python3
"""
Initialize database with sample keywords.

Ensures the database has initial keywords for the application to work properly.
Run this script to populate the database with demo data.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.models.models import Base, Keyword
from app.database import engine

settings = get_settings()

# Sample keywords for initialization
INITIAL_KEYWORDS = [
    {"keyword_en": "Thailand", "keyword_th": "ประเทศไทย", "category": "Country"},
    {"keyword_en": "Vietnam", "keyword_th": "เวียดนาม", "category": "Country"},
    {"keyword_en": "Singapore", "keyword_th": "สิงคโปร์", "category": "Country"},
    {"keyword_en": "Indonesia", "keyword_th": "อินโดนีเซีย", "category": "Country"},
    {"keyword_en": "Myanmar", "keyword_th": "พม่า", "category": "Country"},
    {"keyword_en": "Philippines", "keyword_th": "ฟิลิปปินส์", "category": "Country"},
    {"keyword_en": "Malaysia", "keyword_th": "มาเลเซีย", "category": "Country"},
    {"keyword_en": "Laos", "keyword_th": "ลาว", "category": "Country"},
    {"keyword_en": "Cambodia", "keyword_th": "กัมพูชา", "category": "Country"},
    {"keyword_en": "Brunei", "keyword_th": "บรูไนดารุสซาลาม", "category": "Country"},
    {"keyword_en": "ASEAN", "keyword_th": "อาเซียน", "category": "Organization"},
    {"keyword_en": "COVID-19", "keyword_th": "โควิด-19", "category": "Health"},
    {"keyword_en": "Climate Change", "keyword_th": "การเปลี่ยนแปลงสภาพอากาศ", "category": "Environment"},
    {"keyword_en": "Trade", "keyword_th": "การค้า", "category": "Economics"},
    {"keyword_en": "Technology", "keyword_th": "เทคโนโลยี", "category": "Technology"},
    {"keyword_en": "Politics", "keyword_th": "การเมือง", "category": "Politics"},
    {"keyword_en": "Democracy", "keyword_th": "ประชาธิปไตย", "category": "Politics"},
    {"keyword_en": "Human Rights", "keyword_th": "สิทธิมนุษยชน", "category": "Rights"},
    {"keyword_en": "Education", "keyword_th": "การศึกษา", "category": "Social"},
    {"keyword_en": "Healthcare", "keyword_th": "สุขภาพ", "category": "Health"},
]


def init_keywords():
    """Initialize database with sample keywords."""
    try:
        print("Initializing keywords database...")
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created/verified")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check existing keywords
        existing_count = db.query(Keyword).count()
        print(f"✓ Found {existing_count} existing keywords")
        
        # Add new keywords
        added_count = 0
        for kw_data in INITIAL_KEYWORDS:
            # Check if keyword already exists
            existing = db.query(Keyword).filter(
                Keyword.keyword_en == kw_data["keyword_en"]
            ).first()
            
            if not existing:
                keyword = Keyword(
                    keyword_en=kw_data["keyword_en"],
                    keyword_th=kw_data.get("keyword_th"),
                    category=kw_data.get("category", "general"),
                    popularity_score=0
                )
                db.add(keyword)
                added_count += 1
        
        if added_count > 0:
            db.commit()
            print(f"✓ Added {added_count} new keywords")
        else:
            print("✓ All keywords already exist")
        
        # Verify
        total = db.query(Keyword).count()
        print(f"✓ Total keywords in database: {total}")
        
        # List all keywords
        print("\nKeywords in database:")
        for keyword in db.query(Keyword).order_by(Keyword.keyword_en).all():
            print(f"  - {keyword.keyword_en} ({keyword.keyword_th}) [{keyword.category}]")
        
        db.close()
        print("\n✓ Keyword initialization complete!")
        return True
        
    except Exception as e:
        print(f"✗ Error initializing keywords: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_keywords()
    sys.exit(0 if success else 1)
