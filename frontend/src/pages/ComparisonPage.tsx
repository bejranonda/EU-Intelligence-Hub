/**
 * Keyword comparison page - compare sentiment across multiple keywords
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { apiClient } from '../api/client';
import { Plus, X, TrendingUp } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export function ComparisonPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [keywordIds, setKeywordIds] = useState<number[]>(
    searchParams.get('ids')?.split(',').map(Number) || []
  );
  const [searchQuery, setSearchQuery] = useState('');

  // Search keywords
  const { data: searchResults } = useQuery({
    queryKey: ['keyword-search', searchQuery],
    queryFn: () =>
      apiClient.searchKeywords({
        q: searchQuery,
        page_size: 10,
      }),
    enabled: searchQuery.length > 2,
  });

  // Get comparison data
  const { data: comparisonData, isLoading } = useQuery({
    queryKey: ['keyword-comparison', keywordIds],
    queryFn: () => apiClient.compareKeywordsSentiment(keywordIds),
    enabled: keywordIds.length >= 2,
  });

  const addKeyword = (keywordId: number) => {
    if (keywordIds.length < 6 && !keywordIds.includes(keywordId)) {
      const newIds = [...keywordIds, keywordId];
      setKeywordIds(newIds);
      setSearchParams({ ids: newIds.join(',') });
      setSearchQuery('');
    }
  };

  const removeKeyword = (keywordId: number) => {
    const newIds = keywordIds.filter((id) => id !== keywordId);
    setKeywordIds(newIds);
    if (newIds.length > 0) {
      setSearchParams({ ids: newIds.join(',') });
    } else {
      setSearchParams({});
    }
  };

  // Format timeline data for chart
  const formatTimelineData = () => {
    if (!comparisonData || !comparisonData.timelines) return [];

    const dateMap = new Map<string, any>();

    comparisonData.keywords.forEach((keyword: any) => {
      const timeline = comparisonData.timelines[keyword.id];
      if (timeline && timeline.data_points) {
        timeline.data_points.forEach((point: any) => {
          if (!dateMap.has(point.date)) {
            dateMap.set(point.date, { date: point.date });
          }
          dateMap.get(point.date)[keyword.keyword_en] = point.avg_sentiment;
        });
      }
    });

    return Array.from(dateMap.values()).sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-gray-50 flex flex-col">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Compare Keywords</h1>
          </div>
          <p className="text-gray-600">
            Compare sentiment trends across multiple keywords (up to 6)
          </p>
        </div>

        {/* Keyword Selection */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Selected Keywords ({keywordIds.length}/6)</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Selected Keywords */}
            {keywordIds.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {comparisonData?.keywords.map((keyword: any, index: number) => (
                  <div
                    key={keyword.id}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg border-2"
                    style={{ borderColor: COLORS[index % COLORS.length] }}
                  >
                    <span className="font-medium">{keyword.keyword_en}</span>
                    <button
                      onClick={() => removeKeyword(keyword.id)}
                      className="hover:bg-gray-100 rounded p-1"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Search to Add */}
            {keywordIds.length < 6 && (
              <div className="space-y-3">
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="Search keywords to add..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>

                {/* Search Results */}
                {searchResults && searchResults.results.length > 0 && (
                  <div className="border rounded-lg p-2 max-h-64 overflow-y-auto">
                    {searchResults.results
                      .filter((k: any) => !keywordIds.includes(k.id))
                      .map((keyword: any) => (
                        <button
                          key={keyword.id}
                          onClick={() => addKeyword(keyword.id)}
                          className="w-full text-left px-3 py-2 hover:bg-gray-100 rounded flex items-center justify-between"
                        >
                          <div>
                            <div className="font-medium">{keyword.keyword_en}</div>
                            <div className="text-sm text-gray-600">
                              {keyword.article_count || 0} articles
                            </div>
                          </div>
                          <Plus className="h-5 w-5 text-blue-600" />
                        </button>
                      ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Comparison Results */}
        {keywordIds.length < 2 && (
          <div className="text-center py-16">
            <TrendingUp className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Add keywords to compare
            </h3>
            <p className="text-gray-600">
              Search and select at least 2 keywords to see sentiment comparison
            </p>
          </div>
        )}

        {isLoading && keywordIds.length >= 2 && (
          <div className="text-center py-16">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading comparison data...</p>
          </div>
        )}

        {comparisonData && keywordIds.length >= 2 && (
          <>
            {/* Summary Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {comparisonData.keywords.map((keyword: any, index: number) => (
                <Card key={keyword.id}>
                  <CardContent className="p-6">
                    <div
                      className="w-3 h-3 rounded-full mb-3"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <h3 className="font-semibold text-lg mb-2">{keyword.keyword_en}</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Avg Sentiment:</span>
                        <span className="font-semibold">
                          {keyword.average_sentiment?.toFixed(2) || 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Articles:</span>
                        <span className="font-semibold">{keyword.article_count || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Category:</span>
                        <span className="font-semibold capitalize">{keyword.category}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Timeline Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Sentiment Timeline Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={formatTimelineData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(date) =>
                          new Date(date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                          })
                        }
                      />
                      <YAxis domain={[-1, 1]} />
                      <Tooltip
                        labelFormatter={(date) =>
                          new Date(date).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })
                        }
                        formatter={(value: any) => value?.toFixed(2)}
                      />
                      <Legend />
                      {comparisonData.keywords.map((keyword: any, index: number) => (
                        <Line
                          key={keyword.id}
                          type="monotone"
                          dataKey={keyword.keyword_en}
                          stroke={COLORS[index % COLORS.length]}
                          strokeWidth={2}
                          dot={{ r: 3 }}
                          activeDot={{ r: 5 }}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
