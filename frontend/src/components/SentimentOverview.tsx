/**
 * Sentiment overview component
 */
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { SentimentData } from '../types';
import {
  formatSentiment,
  getSentimentColor,
  getSentimentBgColor,
  getSentimentLabel,
} from '../lib/utils';
import { TrendingUp, TrendingDown, FileText } from 'lucide-react';

interface SentimentOverviewProps {
  data: SentimentData;
}

export function SentimentOverview({ data }: SentimentOverviewProps) {
  const total =
    data.sentiment_distribution.strongly_positive +
    data.sentiment_distribution.positive +
    data.sentiment_distribution.neutral +
    data.sentiment_distribution.negative +
    data.sentiment_distribution.strongly_negative;

  const getPercentage = (count: number) => {
    return total > 0 ? ((count / total) * 100).toFixed(1) : '0.0';
  };

  return (
    <div className="space-y-6">
      {/* Overall Sentiment Card */}
      <Card>
        <CardHeader>
          <CardTitle>Overall Sentiment</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-4xl font-bold">
                <span className={getSentimentColor(data.average_sentiment || 0)}>
                  {formatSentiment(data.average_sentiment)}
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-1">Average Sentiment Score</p>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-gray-400" />
              <span className="text-2xl font-semibold">{data.total_articles}</span>
              <span className="text-sm text-gray-600">articles</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Distribution Card */}
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {/* Strongly Positive */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Strongly Positive</span>
                <span className="text-sm text-gray-600">
                  {data.sentiment_distribution.strongly_positive} (
                  {getPercentage(data.sentiment_distribution.strongly_positive)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{
                    width: `${getPercentage(
                      data.sentiment_distribution.strongly_positive
                    )}%`,
                  }}
                />
              </div>
            </div>

            {/* Positive */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Positive</span>
                <span className="text-sm text-gray-600">
                  {data.sentiment_distribution.positive} (
                  {getPercentage(data.sentiment_distribution.positive)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-400 h-2 rounded-full"
                  style={{
                    width: `${getPercentage(data.sentiment_distribution.positive)}%`,
                  }}
                />
              </div>
            </div>

            {/* Neutral */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Neutral</span>
                <span className="text-sm text-gray-600">
                  {data.sentiment_distribution.neutral} (
                  {getPercentage(data.sentiment_distribution.neutral)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gray-400 h-2 rounded-full"
                  style={{
                    width: `${getPercentage(data.sentiment_distribution.neutral)}%`,
                  }}
                />
              </div>
            </div>

            {/* Negative */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Negative</span>
                <span className="text-sm text-gray-600">
                  {data.sentiment_distribution.negative} (
                  {getPercentage(data.sentiment_distribution.negative)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-400 h-2 rounded-full"
                  style={{
                    width: `${getPercentage(data.sentiment_distribution.negative)}%`,
                  }}
                />
              </div>
            </div>

            {/* Strongly Negative */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Strongly Negative</span>
                <span className="text-sm text-gray-600">
                  {data.sentiment_distribution.strongly_negative} (
                  {getPercentage(data.sentiment_distribution.strongly_negative)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-600 h-2 rounded-full"
                  style={{
                    width: `${getPercentage(
                      data.sentiment_distribution.strongly_negative
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Source Sentiment Card */}
      {data.by_source && (
        <Card>
          <CardHeader>
            <CardTitle>Top Sources</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {data.by_source.most_positive && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="font-medium">{data.by_source.most_positive.source}</p>
                    <p className="text-xs text-gray-600">Most Positive</p>
                  </div>
                </div>
                <span className="text-green-600 font-semibold">
                  {formatSentiment(data.by_source.most_positive.average_sentiment)}
                </span>
              </div>
            )}

            {data.by_source.most_negative && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingDown className="h-5 w-5 text-red-600" />
                  <div>
                    <p className="font-medium">{data.by_source.most_negative.source}</p>
                    <p className="text-xs text-gray-600">Most Negative</p>
                  </div>
                </div>
                <span className="text-red-600 font-semibold">
                  {formatSentiment(data.by_source.most_negative.average_sentiment)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
