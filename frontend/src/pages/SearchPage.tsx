import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Search as SearchIcon } from 'lucide-react';

import { apiClient } from '../api/client';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';

type SearchResult = {
  id: number;
  title: string;
  summary: string;
  source: string;
  source_url: string;
  published_date?: string;
  similarity_score: number;
  sentiment: {
    overall?: number;
    classification?: string;
  };
  language?: string;
  keywords: string[];
};

type SearchResponse = {
  results: SearchResult[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
};

type SortOption = 'relevance' | 'date_desc' | 'date_asc' | 'sentiment_desc' | 'sentiment_asc';

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'date_desc', label: 'Date (Newest)' },
  { value: 'date_asc', label: 'Date (Oldest)' },
  { value: 'sentiment_desc', label: 'Sentiment (High)' },
  { value: 'sentiment_asc', label: 'Sentiment (Low)' },
];

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    minSimilarity: 0.5,
    source: '',
    language: '',
    sortBy: 'relevance' as SortOption,
  });

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['article-search', query, page, filters],
    queryFn: () =>
      apiClient.semanticSearch({
        q: query || 'europe',
        page,
        min_similarity: filters.minSimilarity,
        source: filters.source || undefined,
        language: filters.language || undefined,
        sort_by: filters.sortBy,
      }),
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setPage(1);
  };

  const results = (data as SearchResponse | undefined)?.results ?? [];
  const pagination = (data as SearchResponse | undefined)?.pagination;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <h1 className="text-2xl font-semibold text-slate-900">Article Search</h1>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <form onSubmit={handleSubmit} className="rounded-lg border bg-white p-4 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-end">
            <div className="flex-1">
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Search Query
              </label>
              <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                <Input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Find articles about policy, climate, finance, ..."
                  className="pl-10"
                />
              </div>
            </div>

            <div className="w-full md:w-48">
              <label className="mb-2 block text-sm font-medium text-slate-700">Sort By</label>
              <select
                value={filters.sortBy}
                onChange={(event) => {
                  const value = event.target.value as SortOption;
                  setFilters((prev) => ({ ...prev, sortBy: value }));
                  setPage(1);
                }}
                className="w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {SORT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="w-full md:w-40">
              <label className="mb-2 block text-sm font-medium text-slate-700">Min Similarity</label>
              <Input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={filters.minSimilarity}
                onChange={(event) => {
                  setFilters((prev) => ({
                    ...prev,
                    minSimilarity: parseFloat(event.target.value) || 0,
                  }));
                  setPage(1);
                }}
              />
            </div>

            <Button type="submit" className="w-full md:w-auto" disabled={isFetching}>
              Search
            </Button>
          </div>

          <div className="mt-4 flex flex-wrap gap-4">
            <div className="w-full md:w-48">
              <label className="mb-2 block text-sm font-medium text-slate-700">Source</label>
              <Input
                placeholder="e.g., Reuters"
                value={filters.source}
                onChange={(event) => {
                  setFilters((prev) => ({ ...prev, source: event.target.value }));
                  setPage(1);
                }}
              />
            </div>
            <div className="w-full md:w-48">
              <label className="mb-2 block text-sm font-medium text-slate-700">Language</label>
              <Input
                placeholder="en"
                value={filters.language}
                onChange={(event) => {
                  setFilters((prev) => ({ ...prev, language: event.target.value }));
                  setPage(1);
                }}
              />
            </div>
          </div>
        </form>

        <section className="mt-8 space-y-4">
          {isLoading && (
            <p className="text-sm text-slate-500">Loading results…</p>
          )}

          {!isLoading && results.length === 0 && (
            <div className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-center text-sm text-slate-500">
              No articles found. Try adjusting your filters.
            </div>
          )}

          {results.map((result) => {
            const published = result.published_date
              ? format(new Date(result.published_date), 'dd MMM yyyy')
              : 'Unknown';

            return (
              <article key={result.id} className="rounded-lg border bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="space-y-2">
                    <h2 className="text-xl font-semibold text-slate-900">{result.title}</h2>
                    <p className="text-sm text-slate-600">{result.summary}</p>
                    <div className="flex flex-wrap gap-3 text-xs text-slate-500">
                      <span className="rounded bg-slate-100 px-2 py-0.5">Source: {result.source}</span>
                      <span className="rounded bg-slate-100 px-2 py-0.5">Published: {published}</span>
                      {typeof result.sentiment.overall === 'number' && (
                        <span className="rounded bg-slate-100 px-2 py-0.5">
                          Sentiment: {result.sentiment.overall.toFixed(2)} ({result.sentiment.classification})
                        </span>
                      )}
                      {result.language && (
                        <span className="rounded bg-slate-100 px-2 py-0.5">Lang: {result.language}</span>
                      )}
                    </div>
                    {result.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {result.keywords.map((keyword) => (
                          <span key={keyword} className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end gap-2 text-right">
                    <span className="text-sm font-medium text-slate-600">
                      Similarity
                    </span>
                    <span className="text-lg font-semibold text-blue-600">
                      {result.similarity_score.toFixed(2)}
                    </span>
                    <a
                      href={result.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      View Article
                    </a>
                  </div>
                </div>
              </article>
            );
          })}
        </section>

        {pagination && pagination.total_pages > 1 && (
          <div className="mt-8 flex items-center justify-center gap-4">
            <Button
              variant="outline"
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={page === 1 || isFetching}
            >
              Previous
            </Button>
            <span className="text-sm text-slate-600">
              Page {pagination.page} of {pagination.total_pages}
            </span>
            <Button
              variant="outline"
              onClick={() => setPage((prev) => (pagination.total_pages ? Math.min(pagination.total_pages, prev + 1) : prev + 1))}
              disabled={pagination.total_pages ? page >= pagination.total_pages : false || isFetching}
            >
              Next
            </Button>
          </div>
        )}
      </main>
    </div>
  );
}
