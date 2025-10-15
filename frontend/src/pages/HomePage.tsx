/**
 * Homepage component
 */
import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { KeywordCard } from '../components/KeywordCard';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { LanguageToggle } from '../components/LanguageToggle';
import { useLanguageStore } from '../store/languageStore';
import { Keyword } from '../types';

export function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const { language } = useLanguageStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['keywords', searchQuery, page, language],
    queryFn: () =>
      apiClient.searchKeywords({
        q: searchQuery || undefined,
        language,
        page,
        page_size: 20,
      }),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                European News Intelligence Hub
              </h1>
              <p className="text-gray-600 mt-1">
                AI-powered sentiment analysis of European media coverage
              </p>
            </div>
            <LanguageToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="mb-8 flex gap-4 justify-end">
          <Link to="/upload">
            <Button variant="outline">
              Upload Document
            </Button>
          </Link>
          <Link to="/suggest">
            <Button variant="outline">
              Suggest Keyword
            </Button>
          </Link>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Search keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button type="submit">Search</Button>
          </form>
        </div>

        {/* Keywords Grid */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading keywords...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-12">
            <p className="text-red-600">Error loading keywords. Please try again.</p>
          </div>
        )}

        {data && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {data.results.map((keyword: Keyword) => (
                <KeywordCard key={keyword.id} keyword={keyword} />
              ))}
            </div>

            {/* Pagination */}
            {data.pagination.total_pages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-600">
                  Page {data.pagination.page} of {data.pagination.total_pages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setPage(page + 1)}
                  disabled={page === data.pagination.total_pages}
                >
                  Next
                </Button>
              </div>
            )}

            {/* Results Count */}
            <p className="text-center mt-4 text-sm text-gray-500">
              Showing {data.results.length} of {data.pagination.total} keywords
            </p>
          </>
        )}
      </main>
    </div>
  );
}
