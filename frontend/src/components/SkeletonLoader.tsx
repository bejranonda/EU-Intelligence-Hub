/**
 * Skeleton loader components for better loading states
 */
import { Card, CardContent, CardHeader } from './ui/card';

export function KeywordCardSkeleton() {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="h-6 bg-gray-200 rounded animate-pulse mb-2"></div>
        <div className="h-4 bg-gray-100 rounded animate-pulse w-2/3"></div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2 mb-2">
          <div className="h-4 w-4 bg-gray-200 rounded animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded animate-pulse w-20"></div>
        </div>
        <div className="h-6 bg-gray-100 rounded-full animate-pulse w-24"></div>
      </CardContent>
    </Card>
  );
}

export function KeywordGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <KeywordCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function ArticleListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i}>
          <CardContent className="p-4">
            <div className="h-6 bg-gray-200 rounded animate-pulse mb-3"></div>
            <div className="h-4 bg-gray-100 rounded animate-pulse mb-2"></div>
            <div className="h-4 bg-gray-100 rounded animate-pulse w-5/6 mb-3"></div>
            <div className="flex gap-2">
              <div className="h-5 bg-gray-200 rounded-full animate-pulse w-16"></div>
              <div className="h-5 bg-gray-200 rounded-full animate-pulse w-20"></div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="w-full h-64 bg-gray-100 rounded-lg animate-pulse flex items-center justify-center">
      <div className="text-gray-400 text-sm">Loading chart...</div>
    </div>
  );
}

export function StatsSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="p-4 bg-gray-50 rounded-lg">
          <div className="h-4 bg-gray-200 rounded animate-pulse mb-2 w-20"></div>
          <div className="h-8 bg-gray-300 rounded animate-pulse w-16"></div>
        </div>
      ))}
    </div>
  );
}
