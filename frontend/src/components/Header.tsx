/**
 * Global navigation header component with i18n support
 */
import { Link, useLocation } from 'react-router-dom';
import { Search, TrendingUp, Upload, Lightbulb, Home, BarChart2 } from 'lucide-react';
import { Button } from './ui/button';
import { LanguageToggle } from './LanguageToggle';
import { useState } from 'react';
import { Input } from './ui/input';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const handleQuickSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/?q=${encodeURIComponent(searchQuery)}`);
      setSearchQuery('');
    }
  };

  return (
    <header className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Bar */}
        <div className="flex items-center justify-between py-4">
          {/* Logo and Title */}
          <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="bg-blue-600 p-2 rounded-lg">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-gray-900">
                {t('header.title')}
              </h1>
              <p className="text-xs text-gray-600">
                {t('header.subtitle')}
              </p>
            </div>
          </Link>

          {/* Quick Search - Desktop */}
          <div className="hidden md:block flex-1 max-w-md mx-8">
            <form onSubmit={handleQuickSearch} className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder={t('home.searchPlaceholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 text-sm"
              />
            </form>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-2">
            <LanguageToggle />

            {/* Mobile Menu Toggle */}
            <button
              className="md:hidden p-2 rounded-lg hover:bg-gray-100"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Navigation Menu - Desktop */}
        <nav className="hidden md:flex items-center gap-1 pb-2 border-t pt-2">
          <Link to="/">
            <Button
              variant={isActive('/') ? 'default' : 'ghost'}
              size="sm"
              className="gap-2"
            >
              <Home className="h-4 w-4" />
              {t('header.home')}
            </Button>
          </Link>

          <Link to="/search">
            <Button
              variant={isActive('/search') ? 'default' : 'ghost'}
              size="sm"
              className="gap-2"
            >
              <Search className="h-4 w-4" />
              {t('header.search')}
            </Button>
          </Link>

          <Link to="/compare">
            <Button
              variant={isActive('/compare') ? 'default' : 'ghost'}
              size="sm"
              className="gap-2"
            >
              <BarChart2 className="h-4 w-4" />
              {t('header.compare')}
            </Button>
          </Link>

          <Link to="/upload">
            <Button
              variant={isActive('/upload') ? 'default' : 'ghost'}
              size="sm"
              className="gap-2"
            >
              <Upload className="h-4 w-4" />
              {t('header.upload')}
            </Button>
          </Link>

          <Link to="/suggest">
            <Button
              variant={isActive('/suggest') ? 'default' : 'ghost'}
              size="sm"
              className="gap-2"
            >
              <Lightbulb className="h-4 w-4" />
              {t('header.suggest')}
            </Button>
          </Link>

          <div className="flex-1"></div>

          <Link to="/about">
            <Button variant="ghost" size="sm">
              {t('header.about')}
            </Button>
          </Link>

          <Link to="/methodology">
            <Button variant="ghost" size="sm">
              {t('header.methodology')}
            </Button>
          </Link>
        </nav>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <nav className="md:hidden py-4 border-t">
            {/* Mobile Quick Search */}
            <form onSubmit={handleQuickSearch} className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder={t('home.searchPlaceholder')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </form>

            <div className="flex flex-col gap-2">
              <Link to="/" onClick={() => setIsMobileMenuOpen(false)}>
                <Button
                  variant={isActive('/') ? 'default' : 'ghost'}
                  className="w-full justify-start gap-2"
                >
                  <Home className="h-4 w-4" />
                  {t('header.home')}
                </Button>
              </Link>

              <Link to="/search" onClick={() => setIsMobileMenuOpen(false)}>
                <Button
                  variant={isActive('/search') ? 'default' : 'ghost'}
                  className="w-full justify-start gap-2"
                >
                  <Search className="h-4 w-4" />
                  {t('header.search')}
                </Button>
              </Link>

              <Link to="/compare" onClick={() => setIsMobileMenuOpen(false)}>
                <Button
                  variant={isActive('/compare') ? 'default' : 'ghost'}
                  className="w-full justify-start gap-2"
                >
                  <BarChart2 className="h-4 w-4" />
                  {t('header.compare')}
                </Button>
              </Link>

              <Link to="/upload" onClick={() => setIsMobileMenuOpen(false)}>
                <Button
                  variant={isActive('/upload') ? 'default' : 'ghost'}
                  className="w-full justify-start gap-2"
                >
                  <Upload className="h-4 w-4" />
                  {t('header.upload')}
                </Button>
              </Link>

              <Link to="/suggest" onClick={() => setIsMobileMenuOpen(false)}>
                <Button
                  variant={isActive('/suggest') ? 'default' : 'ghost'}
                  className="w-full justify-start gap-2"
                >
                  <Lightbulb className="h-4 w-4" />
                  {t('header.suggest')}
                </Button>
              </Link>

              <div className="border-t my-2"></div>

              <Link to="/about" onClick={() => setIsMobileMenuOpen(false)}>
                <Button variant="ghost" className="w-full justify-start">
                  {t('header.about')}
                </Button>
              </Link>

              <Link to="/methodology" onClick={() => setIsMobileMenuOpen(false)}>
                <Button variant="ghost" className="w-full justify-start">
                  {t('header.methodology')}
                </Button>
              </Link>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
