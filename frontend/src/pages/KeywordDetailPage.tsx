/**
 * Keyword detail page with articles and sentiment analysis
 */
import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import { apiClient } from '../api/client';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { SentimentOverview } from '../components/SentimentOverview';
import { SentimentTimeline } from '../components/SentimentTimeline';
import { MindMap } from '../components/MindMap';
import { LanguageToggle } from '../components/LanguageToggle';
import { useLanguageStore } from '../store/languageStore';
import {
  formatDate,
  formatSentiment,
  getSentimentColor,
  getSentimentLabel,
  truncate,
} from '../lib/utils';

export function KeywordDetailPage() {
  const { id } = useParams<{ id: string }>();
  const keywordId = parseInt(id || '0');
  const { language } = useLanguageStore();
  const [articlePage, setArticlePage] = useState(1);
  const [sortBy, setSortBy] = useState<'date' | 'sentiment'>('date');

  // Fetch keyword details
  const { data: keyword } = useQuery({
    queryKey: ['keyword', keywordId, language],
    queryFn: () => apiClient.getKeyword(keywordId, language),
  });

  // Fetch sentiment data
  const { data: sentiment } = useQuery({
    queryKey: ['keyword-sentiment', keywordId],
    queryFn: () => apiClient.getKeywordSentiment(keywordId),
  });

  // Fetch timeline data
  const { data: timeline } = useQuery({
    queryKey: ['keyword-timeline', keywordId],
    queryFn: () => apiClient.getKeywordSentimentTimeline(keywordId, 30),
  });

  // Fetch relations
  const { data: relations } = useQuery({
    queryKey: ['keyword-relations', keywordId],
    queryFn: () => apiClient.getKeywordRelations(keywordId),
  });

  // Fetch articles
  const { data: articlesData, isLoading: articlesLoading } = useQuery({
    queryKey: ['keyword-articles', keywordId, articlePage, sortBy],
    queryFn: () =>
      apiClient.getKeywordArticles(keywordId, {
        page: articlePage,
        page_size: 10,
        sort_by: sortBy,
      }),
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {keyword?.keyword}
                </h1>
                {keyword?.category && (
                  <span className="inline-block mt-1 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                    {keyword.category}
                  </span>
                )}
              </div>
            </div>
            <LanguageToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Sentiment Analysis */}
          <div className="lg:col-span-1">
            {sentiment && <SentimentOverview data={sentiment} />}
          </div>

          {/* Right Column - Timeline and Articles */}
          <div className="lg:col-span-2 space-y-8">
            {/* Sentiment Timeline */}
            {timeline && <SentimentTimeline data={timeline} />}

            {/* Mind Map */}
            {relations && relations.nodes.length > 0 && (
              <MindMap data={relations} />
            )}

            {/* Articles List */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Articles</CardTitle>
                  <div className="flex gap-2">
                    <Button
                      variant={sortBy === 'date' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSortBy('date')}
                    >
                      By Date
                    </Button>
                    <Button
                      variant={sortBy === 'sentiment' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSortBy('sentiment')}
                    >
                      By Sentiment
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {articlesLoading && (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                )}

                {articlesData && (
                  <>
                    <div className="space-y-4">
                      {articlesData.results.map((article: any) => (
                        <div
                          key={article.id}
                          className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg mb-2">
                                {article.title}
                              </h3>
                              <p className="text-sm text-gray-600 mb-3">
                                {truncate(article.summary, 200)}
                              </p>
                              <div className="flex items-center gap-4 text-sm text-gray-500">
                                <span className="font-medium">{article.source}</span>
                                <span>{formatDate(article.published_date)}</span>
                                {article.source_url && (
                                  <a
                                    href={article.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-1 text-blue-600 hover:underline"
                                  >
                                    Read more
                                    <ExternalLink className="h-3 w-3" />
                                  </a>
                                )}
                              </div>
                            </div>
                            <div className="flex flex-col items-end gap-2">
                              <div
                                className={`text-2xl font-bold ${getSentimentColor(
                                  article.sentiment.overall
                                )}`}
                              >
                                {formatSentiment(article.sentiment.overall)}
                              </div>
                              <span className="text-xs text-gray-600">
                                {getSentimentLabel(article.sentiment.classification)}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Pagination */}
                    {articlesData.pagination.total_pages > 1 && (
                      <div className="mt-6 flex items-center justify-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setArticlePage(articlePage - 1)}
                          disabled={articlePage === 1}
                        >
                          Previous
                        </Button>
                        <span className="text-sm text-gray-600">
                          Page {articlesData.pagination.page} of{' '}
                          {articlesData.pagination.total_pages}
                        </span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setArticlePage(articlePage + 1)}
                          disabled={
                            articlePage === articlesData.pagination.total_pages
                          }
                        >
                          Next
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
