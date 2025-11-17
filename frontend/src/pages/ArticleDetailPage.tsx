/**
 * Article detail page showing full article content and analysis
 */
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, ExternalLink, Calendar, Tag, TrendingUp } from 'lucide-react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { apiClient } from '../api/client';
import {
  formatDate,
  formatSentiment,
  getSentimentColor,
  getSentimentLabel,
} from '../lib/utils';

export function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const articleId = parseInt(id || '0');

  // Fetch article details
  const { data: article, isLoading, error } = useQuery({
    queryKey: ['article', articleId],
    queryFn: () => apiClient.getArticle(articleId),
  });

  // Fetch article sentiment
  const { data: sentiment } = useQuery({
    queryKey: ['article-sentiment', articleId],
    queryFn: () => apiClient.getArticleSentiment(articleId),
    enabled: !!article,
  });

  // Fetch similar articles
  const { data: similarArticles } = useQuery({
    queryKey: ['similar-articles', articleId],
    queryFn: () => apiClient.getSimilarArticles(articleId, 5),
    enabled: !!article,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading article...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-600 mb-4">Article not found or error loading</p>
            <Link to="/">
              <Button>Return Home</Button>
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1">
        {/* Back Button */}
        <div className="mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => window.history.back()}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        </div>

        {/* Article Header */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-start justify-between gap-6">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">
                  {article.title}
                </h1>

                {/* Meta Information */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <Tag className="h-4 w-4" />
                    <span className="font-medium">{article.source}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    <span>{formatDate(article.published_date)}</span>
                  </div>
                  {article.source_url && (
                    <a
                      href={article.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600 hover:underline"
                    >
                      View Original
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              </div>

              {/* Sentiment Score */}
              {sentiment && (
                <div className="flex flex-col items-end">
                  <div
                    className={`text-4xl font-bold ${getSentimentColor(
                      sentiment.sentiment_overall
                    )}`}
                  >
                    {formatSentiment(sentiment.sentiment_overall)}
                  </div>
                  <span className="text-sm text-gray-600 mt-1">
                    {getSentimentLabel(sentiment.sentiment_classification)}
                  </span>
                  <span className="text-xs text-gray-500 mt-1">
                    {Math.round((sentiment.sentiment_confidence || 0) * 100)}% confidence
                  </span>
                </div>
              )}
            </div>
          </CardHeader>

          <CardContent>
            {/* Summary */}
            {article.summary && (
              <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
                <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
                <p className="text-gray-700 leading-relaxed">{article.summary}</p>
              </div>
            )}

            {/* Full Text */}
            {article.full_text && (
              <div className="prose max-w-none">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Full Article</h3>
                <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {article.full_text}
                </div>
              </div>
            )}

            {!article.full_text && (
              <p className="text-gray-500 italic">
                Full article text not available. Please visit the original source.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Sentiment Analysis Details */}
        {sentiment && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Sentiment Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Overall Sentiment</h4>
                  <div className={`text-2xl font-bold ${getSentimentColor(sentiment.sentiment_overall)}`}>
                    {formatSentiment(sentiment.sentiment_overall)}
                  </div>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Confidence</h4>
                  <div className="text-2xl font-bold text-gray-900">
                    {Math.round((sentiment.sentiment_confidence || 0) * 100)}%
                  </div>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Subjectivity</h4>
                  <div className="text-2xl font-bold text-gray-900">
                    {Math.round((sentiment.sentiment_subjectivity || 0) * 100)}%
                  </div>
                </div>
              </div>

              {/* Emotion Breakdown */}
              {sentiment.emotion_positive !== undefined && (
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Emotion Distribution</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-600 w-20">Positive</span>
                      <div className="flex-1 h-6 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500 transition-all"
                          style={{ width: `${(sentiment.emotion_positive || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-12 text-right">
                        {Math.round((sentiment.emotion_positive || 0) * 100)}%
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-600 w-20">Neutral</span>
                      <div className="flex-1 h-6 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gray-500 transition-all"
                          style={{ width: `${(sentiment.emotion_neutral || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-12 text-right">
                        {Math.round((sentiment.emotion_neutral || 0) * 100)}%
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-600 w-20">Negative</span>
                      <div className="flex-1 h-6 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-red-500 transition-all"
                          style={{ width: `${(sentiment.emotion_negative || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-12 text-right">
                        {Math.round((sentiment.emotion_negative || 0) * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Related Articles */}
        {similarArticles && similarArticles.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Similar Articles</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {similarArticles.map((similar: any) => (
                  <Link
                    key={similar.id}
                    to={`/article/${similar.id}`}
                    className="block p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <h3 className="font-semibold text-gray-900 mb-2">{similar.title}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="font-medium">{similar.source}</span>
                      <span>{formatDate(similar.published_date)}</span>
                      <span className={`font-medium ${getSentimentColor(similar.sentiment.overall)}`}>
                        {formatSentiment(similar.sentiment.overall)}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>

      <Footer />
    </div>
  );
}
