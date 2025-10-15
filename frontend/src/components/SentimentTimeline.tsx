/**
 * Sentiment timeline chart component
 */
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
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { SentimentTimeline as TimelineData } from '../types';
import { formatDate } from '../lib/utils';

interface SentimentTimelineProps {
  data: TimelineData;
}

export function SentimentTimeline({ data }: SentimentTimelineProps) {
  const chartData = data.timeline.map((point) => ({
    date: formatDate(point.date),
    sentiment: point.average_sentiment,
    positive: point.positive_count,
    negative: point.negative_count,
    neutral: point.neutral_count,
  }));

  const getTrendIcon = () => {
    switch (data.trend.direction) {
      case 'improving':
        return '📈';
      case 'declining':
        return '📉';
      case 'stable':
        return '➡️';
      default:
        return '❓';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Sentiment Timeline ({data.period.days} days)</span>
          <span className="text-sm font-normal text-gray-600">
            {getTrendIcon()} {data.trend.direction}{' '}
            {data.trend.change_percent !== 0 && (
              <span className={data.trend.change_percent > 0 ? 'text-green-600' : 'text-red-600'}>
                ({data.trend.change_percent > 0 ? '+' : ''}
                {data.trend.change_percent.toFixed(1)}%)
              </span>
            )}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis domain={[-1, 1]} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-4 border rounded shadow-lg">
                      <p className="font-semibold">{data.date}</p>
                      <p className="text-sm">
                        Sentiment:{' '}
                        <span
                          className={
                            data.sentiment >= 0 ? 'text-green-600' : 'text-red-600'
                          }
                        >
                          {data.sentiment?.toFixed(2)}
                        </span>
                      </p>
                      <div className="mt-2 text-sm space-y-1">
                        <p className="text-green-600">Positive: {data.positive}</p>
                        <p className="text-gray-600">Neutral: {data.neutral}</p>
                        <p className="text-red-600">Negative: {data.negative}</p>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="sentiment"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Average Sentiment"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
