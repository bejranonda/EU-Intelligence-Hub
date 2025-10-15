/**
 * API Client for European News Intelligence Hub
 *
 * Provides type-safe methods for communicating with the backend API.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          console.error('API Error:', error.response.data);
        } else if (error.request) {
          console.error('Network Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // Keywords API
  async searchKeywords(params: {
    q?: string;
    language?: string;
    page?: number;
    page_size?: number;
  }) {
    const response = await this.client.get('/api/keywords/', { params });
    return response.data;
  }

  async getKeyword(id: number, language: string = 'en') {
    const response = await this.client.get(`/api/keywords/${id}`, {
      params: { language },
    });
    return response.data;
  }

  async getKeywordArticles(
    id: number,
    params: {
      page?: number;
      page_size?: number;
      sort_by?: 'date' | 'sentiment';
    }
  ) {
    const response = await this.client.get(`/api/keywords/${id}/articles`, {
      params,
    });
    return response.data;
  }

  async getKeywordRelations(id: number, minStrength: number = 0.3) {
    const response = await this.client.get(`/api/keywords/${id}/relations`, {
      params: { min_strength: minStrength },
    });
    return response.data;
  }

  // Search API
  async semanticSearch(params: {
    q: string;
    limit?: number;
    min_similarity?: number;
  }) {
    const response = await this.client.get('/api/search/semantic', { params });
    return response.data;
  }

  async findSimilarArticles(
    articleId: number,
    params: {
      limit?: number;
      min_similarity?: number;
    }
  ) {
    const response = await this.client.get(`/api/search/similar/${articleId}`, {
      params,
    });
    return response.data;
  }

  // Sentiment API
  async getKeywordSentiment(keywordId: number) {
    const response = await this.client.get(
      `/api/sentiment/keywords/${keywordId}/sentiment`
    );
    return response.data;
  }

  async getKeywordSentimentTimeline(keywordId: number, days: number = 30) {
    const response = await this.client.get(
      `/api/sentiment/keywords/${keywordId}/sentiment/timeline`,
      { params: { days } }
    );
    return response.data;
  }

  async compareKeywordsSentiment(keywordIds: number[]) {
    const response = await this.client.get(
      '/api/sentiment/keywords/compare',
      {
        params: { keyword_ids: keywordIds.join(',') },
      }
    );
    return response.data;
  }

  async getArticleSentiment(articleId: number) {
    const response = await this.client.get(
      `/api/sentiment/articles/${articleId}/sentiment`
    );
    return response.data;
  }

  // Documents API
  async uploadDocument(formData: FormData) {
    const response = await this.client.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Suggestions API
  async createSuggestion(data: {
    keyword_en: string;
    keyword_th?: string;
    category?: string;
    reason?: string;
    contact_email?: string;
  }) {
    const response = await this.client.post('/api/suggestions/', data);
    return response.data;
  }

  async getSuggestions(status?: string, limit: number = 50) {
    const response = await this.client.get('/api/suggestions/', {
      params: { status, limit },
    });
    return response.data;
  }

  async getSuggestion(id: number) {
    const response = await this.client.get(`/api/suggestions/${id}`);
    return response.data;
  }

  async voteSuggestion(id: number) {
    const response = await this.client.post(`/api/suggestions/${id}/vote`);
    return response.data;
  }

  // Health Check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
