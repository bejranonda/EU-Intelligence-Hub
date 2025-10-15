/**
 * Keyword card component for displaying keyword tiles
 */
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Keyword } from '../types';
import { FileText } from 'lucide-react';

interface KeywordCardProps {
  keyword: Keyword;
}

export function KeywordCard({ keyword }: KeywordCardProps) {
  return (
    <Link to={`/keyword/${keyword.id}`} className="block">
      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">{keyword.keyword_en}</CardTitle>
          {keyword.keyword_th && (
            <p className="text-sm text-muted-foreground">{keyword.keyword_th}</p>
          )}
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <FileText className="h-4 w-4" />
            <span>{keyword.article_count || 0} articles</span>
          </div>
          <div className="mt-2">
            <span className="inline-block px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
              {keyword.category}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
