import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Search, Loader2, Database, FileText, Lightbulb, Globe } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

type KeywordResult = {
  id: number;
  keyword_en: string;
  keyword_th?: string;
  keyword_de?: string;
  keyword_fr?: string;
  keyword_es?: string;
  keyword_it?: string;
  keyword_pl?: string;
  keyword_sv?: string;
  keyword_nl?: string;
  category?: string;
  popularity_score?: number;
  search_count?: number;
  type: 'keyword';
};

type ArticleResult = {
  id: number;
  title: string;
  summary?: string;
  source: string;
  source_url: string;
  language?: string;
  published_date?: string;
  sentiment_overall?: number;
  sentiment_classification?: string;
  type: 'article';
};

type SuggestionResult = {
  id: number;
  keyword_en: string;
  keyword_th?: string;
  category?: string;
  status: string;
  votes: number;
  reason?: string;
  type: 'suggestion';
};

type SourceResult = {
  id: number;
  name: string;
  base_url: string;
  language: string;
  country?: string;
  enabled: boolean;
  priority: number;
  type: 'source';
};

type SearchResults = {
  query: string;
  total_results: number;
  keywords: KeywordResult[];
  articles: ArticleResult[];
  suggestions: SuggestionResult[];
  sources: SourceResult[];
};

export function AdminSearchPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [searchType, setSearchType] = useState<'all' | 'keywords' | 'articles' | 'suggestions' | 'sources'>('all');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const { data: results, isLoading, isError, error } = useQuery<SearchResults>({
    queryKey: ['admin-search', activeQuery, searchType],
    queryFn: async () => {
      if (!activeQuery) {
        return {
          query: '',
          total_results: 0,
          keywords: [],
          articles: [],
          suggestions: [],
          sources: [],
        };
      }

      return apiClient.adminComprehensiveSearch(
        {
          q: activeQuery,
          search_type: searchType,
          limit: 50,
        },
        { username, password }
      );
    },
    enabled: activeQuery !== '' && isAuthenticated,
  });

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (username && password) {
      setIsAuthenticated(true);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setActiveQuery(searchQuery.trim());
    }
  };

  const getSentimentColor = (sentiment?: number) => {
    if (!sentiment) return 'text-slate-500';
    if (sentiment > 0.2) return 'text-green-600';
    if (sentiment < -0.2) return 'text-red-600';
    return 'text-yellow-600';
  };

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-md px-6 py-20">
        <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-lg">
          <h1 className="mb-6 text-2xl font-semibold text-slate-900">Admin Login</h1>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-semibold text-slate-900">Admin Comprehensive Search</h1>
        <p className="text-sm text-slate-600">
          Search across ALL content and ALL languages: keywords, articles, suggestions, and sources
        </p>
      </div>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search in any language (EN, TH, DE, FR, ES, IT, PL, SV, NL)..."
              className="w-full rounded-lg border border-slate-300 py-3 pl-10 pr-4 text-base focus:border-blue-500 focus:outline-none"
            />
          </div>
          <select
            value={searchType}
            onChange={(e) => setSearchType(e.target.value as typeof searchType)}
            className="rounded-lg border border-slate-300 px-4 py-3 text-base focus:border-blue-500 focus:outline-none"
          >
            <option value="all">All Types</option>
            <option value="keywords">Keywords</option>
            <option value="articles">Articles</option>
            <option value="suggestions">Suggestions</option>
            <option value="sources">Sources</option>
          </select>
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700"
          >
            Search
          </button>
        </div>
      </form>

      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      )}

      {isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          Error: {error instanceof Error ? error.message : 'Failed to perform search'}
        </div>
      )}

      {results && activeQuery && !isLoading && (
        <div className="space-y-6">
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="text-sm text-slate-600">
              Found <span className="font-semibold text-slate-900">{results.total_results}</span> results for "{results.query}"
            </div>
          </div>

          {/* Keywords Section */}
          {results.keywords.length > 0 && (
            <div>
              <div className="mb-3 flex items-center gap-2">
                <Database className="h-5 w-5 text-blue-600" />
                <h2 className="text-xl font-semibold text-slate-900">
                  Keywords ({results.keywords.length})
                </h2>
              </div>
              <div className="space-y-2">
                {results.keywords.map((keyword) => (
                  <div
                    key={keyword.id}
                    onClick={() => navigate(`/keywords/${keyword.id}`)}
                    className="cursor-pointer rounded-lg border border-slate-200 bg-white p-4 transition hover:border-blue-300 hover:shadow-md"
                  >
                    <div className="mb-2 flex items-start justify-between">
                      <h3 className="text-lg font-semibold text-slate-900">{keyword.keyword_en}</h3>
                      <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
                        {keyword.category || 'general'}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-sm text-slate-600">
                      {keyword.keyword_th && <div>🇹🇭 {keyword.keyword_th}</div>}
                      {keyword.keyword_de && <div>🇩🇪 {keyword.keyword_de}</div>}
                      {keyword.keyword_fr && <div>🇫🇷 {keyword.keyword_fr}</div>}
                      {keyword.keyword_es && <div>🇪🇸 {keyword.keyword_es}</div>}
                      {keyword.keyword_it && <div>🇮🇹 {keyword.keyword_it}</div>}
                      {keyword.keyword_pl && <div>🇵🇱 {keyword.keyword_pl}</div>}
                      {keyword.keyword_sv && <div>🇸🇪 {keyword.keyword_sv}</div>}
                      {keyword.keyword_nl && <div>🇳🇱 {keyword.keyword_nl}</div>}
                    </div>
                    <div className="mt-2 flex gap-4 text-xs text-slate-500">
                      <span>Searches: {keyword.search_count || 0}</span>
                      <span>Popularity: {((keyword.popularity_score || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Articles Section */}
          {results.articles.length > 0 && (
            <div>
              <div className="mb-3 flex items-center gap-2">
                <FileText className="h-5 w-5 text-green-600" />
                <h2 className="text-xl font-semibold text-slate-900">
                  Articles ({results.articles.length})
                </h2>
              </div>
              <div className="space-y-2">
                {results.articles.map((article) => (
                  <div
                    key={article.id}
                    onClick={() => navigate(`/articles/${article.id}`)}
                    className="cursor-pointer rounded-lg border border-slate-200 bg-white p-4 transition hover:border-green-300 hover:shadow-md"
                  >
                    <div className="mb-2 flex items-start justify-between">
                      <h3 className="flex-1 text-lg font-semibold text-slate-900">{article.title}</h3>
                      {article.sentiment_overall !== undefined && (
                        <span className={`ml-2 text-sm font-medium ${getSentimentColor(article.sentiment_overall)}`}>
                          {article.sentiment_overall > 0 ? '+' : ''}
                          {article.sentiment_overall.toFixed(2)}
                        </span>
                      )}
                    </div>
                    {article.summary && (
                      <p className="mb-2 text-sm text-slate-600 line-clamp-2">{article.summary}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                      <span className="font-medium">{article.source}</span>
                      {article.language && <span>🌐 {article.language.toUpperCase()}</span>}
                      {article.published_date && (
                        <span>{new Date(article.published_date).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Suggestions Section */}
          {results.suggestions.length > 0 && (
            <div>
              <div className="mb-3 flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-yellow-600" />
                <h2 className="text-xl font-semibold text-slate-900">
                  Suggestions ({results.suggestions.length})
                </h2>
              </div>
              <div className="space-y-2">
                {results.suggestions.map((suggestion) => (
                  <div
                    key={suggestion.id}
                    className="rounded-lg border border-slate-200 bg-white p-4"
                  >
                    <div className="mb-2 flex items-start justify-between">
                      <h3 className="text-lg font-semibold text-slate-900">{suggestion.keyword_en}</h3>
                      <div className="flex gap-2">
                        <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                          suggestion.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                          suggestion.status === 'approved' ? 'bg-green-100 text-green-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {suggestion.status}
                        </span>
                        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                          {suggestion.votes} votes
                        </span>
                      </div>
                    </div>
                    {suggestion.reason && (
                      <p className="text-sm text-slate-600">{suggestion.reason}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sources Section */}
          {results.sources.length > 0 && (
            <div>
              <div className="mb-3 flex items-center gap-2">
                <Globe className="h-5 w-5 text-purple-600" />
                <h2 className="text-xl font-semibold text-slate-900">
                  News Sources ({results.sources.length})
                </h2>
              </div>
              <div className="space-y-2">
                {results.sources.map((source) => (
                  <div
                    key={source.id}
                    className="rounded-lg border border-slate-200 bg-white p-4"
                  >
                    <div className="mb-2 flex items-start justify-between">
                      <h3 className="text-lg font-semibold text-slate-900">{source.name}</h3>
                      <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                        source.enabled ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {source.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-slate-600">
                      <span>🌐 {source.language.toUpperCase()}</span>
                      {source.country && <span>📍 {source.country}</span>}
                      <span>Priority: {source.priority}</span>
                    </div>
                    <a
                      href={source.base_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-block text-xs text-blue-600 hover:underline"
                    >
                      {source.base_url}
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.total_results === 0 && (
            <div className="rounded-lg border border-slate-200 bg-white p-12 text-center">
              <p className="text-slate-600">No results found for "{results.query}"</p>
              <p className="mt-2 text-sm text-slate-500">Try a different search term or filter</p>
            </div>
          )}
        </div>
      )}

      {!activeQuery && !isLoading && (
        <div className="rounded-lg border border-slate-200 bg-white p-12 text-center">
          <Search className="mx-auto mb-4 h-12 w-12 text-slate-400" />
          <p className="text-lg text-slate-600">Enter a search query to get started</p>
          <p className="mt-2 text-sm text-slate-500">
            Search across keywords, articles, suggestions, and sources in all supported languages
          </p>
        </div>
      )}
    </div>
  );
}
