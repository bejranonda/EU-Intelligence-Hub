/**
 * Keyword suggestion page
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Send, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { LanguageToggle } from '../components/LanguageToggle';

export function SuggestPage() {
  const [formData, setFormData] = useState({
    keyword_en: '',
    keyword_th: '',
    keyword_de: '',
    keyword_fr: '',
    keyword_es: '',
    keyword_it: '',
    keyword_pl: '',
    keyword_sv: '',
    keyword_nl: '',
    category: '',
    reason: '',
    contact_email: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.keyword_en.trim()) {
      setError('Please enter a keyword in English');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const result = await apiClient.createSuggestion(formData);
      
      // Check for successful response
      if (result.success) {
        setSuccess(true);
        setFormData({
          keyword_en: '',
          keyword_th: '',
          keyword_de: '',
          keyword_fr: '',
          keyword_es: '',
          keyword_it: '',
          keyword_pl: '',
          keyword_sv: '',
          keyword_nl: '',
          category: '',
          reason: '',
          contact_email: '',
        });

        // Reset success message after 5 seconds
        setTimeout(() => setSuccess(false), 5000);
      } else {
        setError(result.message || 'Failed to submit suggestion. Please try again.');
      }
    } catch (err: any) {
      // Extract error message from various response formats
      let errorMessage = 'Failed to submit suggestion. Please try again.';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      console.error('Suggestion submission error:', {
        status: err.response?.status,
        data: err.response?.data,
        message: errorMessage
      });
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Suggest Keyword</h1>
            </div>
            <LanguageToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Suggest a New Keyword</CardTitle>
            <CardDescription>
              Help us expand our coverage by suggesting keywords you'd like to see analyzed
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* English Keyword (Required) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Keyword (English) <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  name="keyword_en"
                  value={formData.keyword_en}
                  onChange={handleChange}
                  placeholder="e.g., Singapore, Vietnam, Climate Change"
                  required
                />
              </div>

              {/* Thai Keyword (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Keyword (Thai) <span className="text-gray-400">(Optional)</span>
                </label>
                <Input
                  type="text"
                  name="keyword_th"
                  value={formData.keyword_th}
                  onChange={handleChange}
                  placeholder="e.g., สิงคโปร์, เวียดนาม"
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keyword (German) <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    name="keyword_de"
                    value={formData.keyword_de}
                    onChange={handleChange}
                    placeholder="e.g., Deutschland"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keyword (French) <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    name="keyword_fr"
                    value={formData.keyword_fr}
                    onChange={handleChange}
                    placeholder="e.g., Climat"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keyword (Spanish) <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    name="keyword_es"
                    value={formData.keyword_es}
                    onChange={handleChange}
                    placeholder="e.g., Energía"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keyword (Italian) <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    name="keyword_it"
                    value={formData.keyword_it}
                    onChange={handleChange}
                    placeholder="e.g., Innovazione"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keyword (Polish) <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    name="keyword_pl"
                    value={formData.keyword_pl}
                    onChange={handleChange}
                    placeholder="e.g., Bezpieczeństwo"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keyword (Swedish) <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    name="keyword_sv"
                    value={formData.keyword_sv}
                    onChange={handleChange}
                    placeholder="e.g., Energi"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keyword (Dutch) <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    name="keyword_nl"
                    value={formData.keyword_nl}
                    onChange={handleChange}
                    placeholder="e.g., Handel"
                  />
                </div>
              </div>

              {/* Category (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category <span className="text-gray-400">(Optional)</span>
                </label>
                <Input
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  placeholder="e.g., country, topic, organization"
                />
              </div>

              {/* Reason (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Why is this keyword important? <span className="text-gray-400">(Optional)</span>
                </label>
                <textarea
                  name="reason"
                  value={formData.reason}
                  onChange={handleChange}
                  rows={4}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  placeholder="Tell us why you think this keyword should be tracked..."
                />
              </div>

              {/* Contact Email (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email <span className="text-gray-400">(Optional)</span>
                </label>
                <Input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleChange}
                  placeholder="your@email.com"
                />
                <p className="mt-1 text-xs text-gray-500">
                  We'll notify you when your suggestion is reviewed
                </p>
              </div>

              {/* Submit Button */}
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Submit Suggestion
                  </>
                )}
              </Button>
            </form>

            {/* Success Message */}
            {success && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-green-900">
                    Thank you for your suggestion!
                  </h3>
                  <p className="text-sm text-green-700 mt-1">
                    Your keyword suggestion has been submitted and will be reviewed by our team.
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
