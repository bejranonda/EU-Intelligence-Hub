import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format } from 'date-fns';

/**
 * Combine class names using clsx and tailwind-merge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format date string to readable format
 */
export function formatDate(date: string | Date): string {
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return format(dateObj, 'MMM d, yyyy');
  } catch (error) {
    return String(date);
  }
}

/**
 * Format sentiment score to display with sign
 */
export function formatSentiment(score: number | null): string {
  if (score === null) return '0.00';
  const formatted = score.toFixed(2);
  return score > 0 ? `+${formatted}` : formatted;
}

/**
 * Get color class based on sentiment score
 */
export function getSentimentColor(score: number): string {
  if (score > 0.2) return 'text-green-600';
  if (score < -0.2) return 'text-red-600';
  return 'text-gray-600';
}

/**
 * Get sentiment label from classification
 */
export function getSentimentLabel(classification: string | null): string {
  if (!classification) return 'Unknown';

  const labels: { [key: string]: string } = {
    positive: 'Positive',
    negative: 'Negative',
    neutral: 'Neutral',
    mixed: 'Mixed',
  };
  return labels[classification.toLowerCase()] || classification;
}

/**
 * Truncate text to specified length
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}
