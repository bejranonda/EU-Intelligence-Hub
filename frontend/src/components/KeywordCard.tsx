/**
 * Enhanced keyword card component with sentiment indicators and i18n support
 */
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Keyword } from '../types';
import { FileText, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useLanguageStore } from '../store/languageStore';
import { useTranslation } from 'react-i18next';

interface KeywordCardProps {
  keyword: Keyword;
}

export function KeywordCard({ keyword }: KeywordCardProps) {
  const { language } = useLanguageStore();
  const { t } = useTranslation();

  // Get keyword text based on current language
  const getKeywordText = () => {
    switch (language) {
      case 'th':
        return keyword.keyword_th || keyword.keyword_en;
      case 'de':
        return keyword.keyword_de || keyword.keyword_en;
      case 'da':
        return keyword.keyword_da || keyword.keyword_en;
      default:
        return keyword.keyword_en;
    }
  };

  // Determine sentiment icon and color
  const getSentimentIndicator = () => {
    if (!keyword.average_sentiment) {
      return { icon: Minus, color: 'text-gray-400', bg: 'bg-gray-50' };
    }
    if (keyword.average_sentiment > 0.2) {
      return { icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-50' };
    }
    if (keyword.average_sentiment < -0.2) {
      return { icon: TrendingDown, color: 'text-red-600', bg: 'bg-red-50' };
    }
    return { icon: Minus, color: 'text-gray-500', bg: 'bg-gray-50' };
  };

  const sentiment = getSentimentIndicator();
  const SentimentIcon = sentiment.icon;

  return (
    <Link to={`/keyword/${keyword.id}`} className="block group">
      <Card className="hover:shadow-xl hover:border-blue-300 transition-all duration-200 cursor-pointer h-full group-hover:scale-[1.02]">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg group-hover:text-blue-600 transition-colors line-clamp-2">
              {getKeywordText()}
            </CardTitle>
            {keyword.average_sentiment !== undefined && (
              <div className={`flex-shrink-0 p-1.5 rounded-full ${sentiment.bg}`}>
                <SentimentIcon className={`h-4 w-4 ${sentiment.color}`} />
              </div>
            )}
          </div>
          {language !== 'en' && keyword.keyword_en && (
            <p className="text-sm text-muted-foreground line-clamp-1">{keyword.keyword_en}</p>
          )}
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <FileText className="h-4 w-4" />
              <span>{keyword.article_count || 0} {t('keyword.articles')}</span>
            </div>
            {keyword.average_sentiment !== undefined && (
              <div className={`text-sm font-semibold ${sentiment.color}`}>
                {keyword.average_sentiment > 0 ? '+' : ''}
                {keyword.average_sentiment.toFixed(2)}
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 capitalize">
              {t(`categories.${keyword.category}`) || keyword.category}
            </span>
            {keyword.popularity_score && keyword.popularity_score > 0.7 && (
              <span className="inline-block px-2 py-1 text-xs rounded-full bg-orange-100 text-orange-800">
                {t('home.trending')}
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
