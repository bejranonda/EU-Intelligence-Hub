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
    try {
      const response = await this.client.get('/api/keywords/', { params });
      
      // Ensure response has required structure
      if (!response.data.results) {
        console.warn('API response missing results key:', response.data);
        return {
          results: [],
          pagination: {
            page: params.page || 1,
            page_size: params.page_size || 20,
            total: 0,
            total_pages: 0
          }
        };
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching keywords:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      throw error;
    }
  }

  async getAdminSources() {
    const response = await this.client.get('/admin/sources');
    return response.data;
  }

  async getAdminSourceHistory(sourceId: number, limit = 20) {
    const response = await this.client.get(`/admin/sources/${sourceId}/ingestion`, {
      params: { limit },
    });
    return response.data;
  }

  async toggleAdminSource(sourceId: number, enabled: boolean) {
    const response = await this.client.post(`/admin/sources/${sourceId}/toggle`, null, {
      params: { enabled },
    });
    return response.data;
  }

  async createAdminSource(data: {
    name: string;
    base_url: string;
    language?: string;
    country?: string;
    priority?: number;
    parser?: string;
    tags?: string[];
    enabled?: boolean;
  }) {
    const response = await this.client.post('/admin/sources', data);
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
    keyword_de?: string;
    keyword_fr?: string;
    keyword_es?: string;
    keyword_it?: string;
    keyword_pl?: string;
    keyword_sv?: string;
    keyword_nl?: string;
    category?: string;
    reason?: string;
    contact_email?: string;
  }) {
    try {
      console.log('Submitting suggestion:', data);
      const response = await this.client.post('/api/suggestions/', data);
      console.log('Suggestion response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error submitting suggestion:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      throw error;
    }
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

export async function fetchJSON<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function postJSON<T>(url: string, body: unknown): Promise<T> {
  return fetchJSON<T>(url, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
