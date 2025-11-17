/**
 * Enhanced Homepage component with hero section and improved UX
 */
import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Search, TrendingUp, Sparkles, ArrowRight, BarChart3, Globe2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { KeywordCard } from '../components/KeywordCard';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { KeywordGridSkeleton } from '../components/SkeletonLoader';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { useLanguageStore } from '../store/languageStore';
import { Keyword } from '../types';

export function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'popularity' | 'recent'>('popularity');
  const { language } = useLanguageStore();

  // Update search query from URL params
  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setSearchQuery(q);
    }
  }, [searchParams]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['keywords', searchQuery, page, language, category, sortBy],
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
    if (searchQuery) {
      setSearchParams({ q: searchQuery });
    } else {
      setSearchParams({});
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchParams({});
    setPage(1);
  };

  // Filter and sort keywords client-side
  const filteredKeywords = data?.results.filter((keyword: Keyword) => {
    if (category === 'all') return true;
    return keyword.category === category;
  }).sort((a: Keyword, b: Keyword) => {
    if (sortBy === 'popularity') {
      return (b.popularity_score || 0) - (a.popularity_score || 0);
    }
    return 0; // Default ordering from API
  }) || [];

  // Get unique categories
  const categories = ['all', ...new Set(data?.results.map((k: Keyword) => k.category) || [])];

  const showHero = !searchQuery && page === 1;

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-gray-50 flex flex-col">
      <Header />

      {/* Hero Section - Only show on initial load */}
      {showHero && (
        <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16 md:py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-4xl mx-auto">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-700 bg-opacity-50 rounded-full text-sm mb-6">
                <Sparkles className="h-4 w-4" />
                <span>AI-Powered Intelligence Platform</span>
              </div>

              <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                Understand European News
                <span className="block text-blue-200">Through AI Sentiment Analysis</span>
              </h1>

              <p className="text-xl md:text-2xl text-blue-100 mb-8 leading-relaxed">
                Track sentiment trends across 12 major European news sources.
                Analyze geopolitical topics with dual-layer AI analysis powered by VADER and Google Gemini.
              </p>

              {/* Key Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6 text-left">
                  <TrendingUp className="h-8 w-8 mb-3 text-blue-200" />
                  <h3 className="font-semibold mb-2">Real-Time Tracking</h3>
                  <p className="text-sm text-blue-100">Monitor sentiment changes across topics in real-time</p>
                </div>

                <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6 text-left">
                  <BarChart3 className="h-8 w-8 mb-3 text-blue-200" />
                  <h3 className="font-semibold mb-2">AI Analysis</h3>
                  <p className="text-sm text-blue-100">Dual-layer sentiment analysis with confidence scoring</p>
                </div>

                <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6 text-left">
                  <Globe2 className="h-8 w-8 mb-3 text-blue-200" />
                  <h3 className="font-semibold mb-2">Multi-Language</h3>
                  <p className="text-sm text-blue-100">Supporting 9 European languages</p>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/search">
                  <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 gap-2">
                    <Search className="h-5 w-5" />
                    Start Exploring
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/methodology">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
                    Learn How It Works
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1">
        {/* Search Bar */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Search keywords... (e.g., Climate Change, EU Policy, Ukraine)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-20"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500 hover:text-gray-700"
                >
                  Clear
                </button>
              )}
            </div>
            <Button type="submit" className="gap-2">
              <Search className="h-4 w-4" />
              Search
            </Button>
          </form>
        </div>

        {/* Filters and Sort */}
        {data && data.results.length > 0 && (
          <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <Button
                  key={cat}
                  variant={category === cat ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => {
                    setCategory(cat);
                    setPage(1);
                  }}
                  className="capitalize"
                >
                  {cat === 'all' ? 'All Categories' : cat}
                </Button>
              ))}
            </div>

            {/* Sort Options */}
            <div className="flex gap-2 items-center">
              <span className="text-sm text-gray-600">Sort by:</span>
              <Button
                variant={sortBy === 'popularity' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSortBy('popularity')}
              >
                Popularity
              </Button>
              <Button
                variant={sortBy === 'recent' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSortBy('recent')}
              >
                Recent
              </Button>
            </div>
          </div>
        )}

        {/* Trending Keywords Section */}
        {showHero && !isLoading && data && (
          <div className="mb-12">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-6 w-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Trending Topics</h2>
            </div>
            <p className="text-gray-600 mb-6">
              Most analyzed keywords with recent activity
            </p>
          </div>
        )}

        {/* Keywords Grid */}
        {isLoading && <KeywordGridSkeleton count={8} />}

        {error && (
          <div className="text-center py-12 bg-red-50 rounded-lg">
            <p className="text-red-600 font-medium">Error loading keywords</p>
            <p className="text-red-500 text-sm mt-2">Please try again or contact support if the issue persists.</p>
          </div>
        )}

        {data && filteredKeywords.length === 0 && (
          <div className="text-center py-16">
            <div className="text-gray-400 mb-4">
              <Search className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No keywords found</h3>
            <p className="text-gray-600 mb-6">
              Try adjusting your search or browse all available topics
            </p>
            <Button onClick={clearSearch} variant="outline">
              Clear Search
            </Button>
          </div>
        )}

        {data && filteredKeywords.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-8">
              {filteredKeywords.map((keyword: Keyword) => (
                <KeywordCard key={keyword.id} keyword={keyword} />
              ))}
            </div>

            {/* Pagination */}
            {data.pagination.total_pages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setPage(page - 1);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-600 px-4">
                  Page {data.pagination.page} of {data.pagination.total_pages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => {
                    setPage(page + 1);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                  disabled={page === data.pagination.total_pages}
                >
                  Next
                </Button>
              </div>
            )}

            {/* Results Count */}
            <p className="text-center mt-4 text-sm text-gray-500">
              Showing {filteredKeywords.length} of {data.pagination.total} keywords
            </p>
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
