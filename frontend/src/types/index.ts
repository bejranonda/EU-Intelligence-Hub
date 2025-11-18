/**
 * Type definitions for the application
 */

export interface Keyword {
  id: number;
  keyword_en: string;
  keyword_th?: string;
  keyword_de?: string;
  keyword_da?: string;
  category: string;
  article_count?: number;
  popularity_score?: number;
  average_sentiment?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface Article {
  id: number;
  title: string;
  summary: string;
  source: string;
  source_url: string;
  published_date: string;
  sentiment: {
    overall: number;
    confidence: number;
    classification: string;
    subjectivity?: number;
  };
  classification: string;
  keywords?: string[];
}

export interface SentimentData {
  keyword_id: number;
  keyword_en: string;
  total_articles: number;
  average_sentiment: number | null;
  sentiment_distribution: {
    strongly_positive: number;
    positive: number;
    neutral: number;
    negative: number;
    strongly_negative: number;
  };
  by_source?: {
    most_positive: {
      source: string;
      average_sentiment: number;
    } | null;
    most_negative: {
      source: string;
      average_sentiment: number;
    } | null;
  };
}

export interface TimelinePoint {
  date: string;
  average_sentiment: number | null;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  total_articles: number;
  top_sources?: Record<string, any>;
}

export interface SentimentTimeline {
  keyword_id: number;
  keyword_en: string;
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  timeline: TimelinePoint[];
  trend: {
    direction: 'improving' | 'declining' | 'stable' | 'insufficient_data' | 'unknown';
    change_percent: number;
  };
}

export interface MindMapNode {
  id: string;
  label: string;
  type: 'central' | 'related';
  category: string;
}

export interface MindMapEdge {
  source: string;
  target: string;
  strength: number;
  relationship_type: string;
}

export interface KeywordRelations {
  keyword_id: number;
  keyword_en: string;
  nodes: MindMapNode[];
  edges: MindMapEdge[];
  total_relations: number;
}

export interface Suggestion {
  id: number;
  keyword_en: string;
  keyword_th?: string;
  category: string;
  reason?: string;
  status: 'pending' | 'approved' | 'rejected';
  votes: number;
  created_at: string;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface SearchResponse<T> {
  results: T[];
  pagination: PaginationMeta;
}

export interface DocumentUploadResponse {
  success: boolean;
  article: {
    id: number;
    title: string;
    source: string;
    word_count: number;
  };
  sentiment: {
    overall: number;
    classification: string;
    confidence: number;
  };
  keywords: Array<{
    id: number;
    keyword: string;
    category: string;
  }>;
  classification: string;
  message: string;
}

export type Language = 'en' | 'th' | 'de' | 'da';

export type SentimentClassification =
  | 'STRONGLY_POSITIVE'
  | 'POSITIVE'
  | 'NEUTRAL'
  | 'NEGATIVE'
  | 'STRONGLY_NEGATIVE';
