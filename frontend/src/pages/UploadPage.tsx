/**
 * Document upload page
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Upload, FileText, CheckCircle, XCircle, ArrowLeft } from 'lucide-react';
import { apiClient } from '../api/client';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { LanguageToggle } from '../components/LanguageToggle';
import { DocumentUploadResponse } from '../types';
import { formatSentiment, getSentimentColor, getSentimentLabel } from '../lib/utils';

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<DocumentUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.replace(/\.[^/.]+$/, ''));
      }
      setError(null);
      setResult(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (title) {
        formData.append('title', title);
      }
      formData.append('source', 'Manual Upload');

      const response = await apiClient.uploadDocument(formData);
      setResult(response);
      setFile(null);
      setTitle('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
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
              <h1 className="text-2xl font-bold text-gray-900">Upload Document</h1>
            </div>
            <LanguageToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Upload and Analyze Document</CardTitle>
            <CardDescription>
              Upload a PDF, DOCX, or TXT file to extract keywords and analyze sentiment
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document File
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-blue-400 transition-colors">
                  <div className="space-y-1 text-center">
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none"
                      >
                        <span>Upload a file</span>
                        <input
                          id="file-upload"
                          name="file-upload"
                          type="file"
                          className="sr-only"
                          accept=".pdf,.docx,.txt"
                          onChange={handleFileChange}
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">PDF, DOCX, or TXT up to 10MB</p>
                    {file && (
                      <div className="mt-4 flex items-center justify-center gap-2 text-sm text-green-600">
                        <FileText className="h-4 w-4" />
                        <span>{file.name}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Title Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Title (Optional)
                </label>
                <Input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter a custom title..."
                />
              </div>

              {/* Submit Button */}
              <Button type="submit" className="w-full" disabled={!file || uploading}>
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload and Analyze
                  </>
                )}
              </Button>
            </form>

            {/* Error Message */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900">Upload Failed</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            )}

            {/* Success Result */}
            {result && (
              <div className="mt-6 space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-green-900">
                      Document Processed Successfully!
                    </h3>
                    <p className="text-sm text-green-700 mt-1">{result.message}</p>
                  </div>
                </div>

                {/* Document Info */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Document Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600">Title</p>
                      <p className="font-semibold">{result.article.title}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Word Count</p>
                      <p className="font-semibold">{result.article.word_count}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Classification</p>
                      <p className="font-semibold">{result.classification}</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Sentiment Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Sentiment Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Overall Sentiment</p>
                        <p
                          className={`text-3xl font-bold ${getSentimentColor(
                            result.sentiment.overall
                          )}`}
                        >
                          {formatSentiment(result.sentiment.overall)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Classification</p>
                        <p className="font-semibold">
                          {getSentimentLabel(result.sentiment.classification)}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          Confidence: {(result.sentiment.confidence * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Extracted Keywords */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">
                      Extracted Keywords ({result.keywords.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {result.keywords.map((keyword) => (
                        <Link
                          key={keyword.id}
                          to={`/keyword/${keyword.id}`}
                          className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-sm hover:bg-blue-200 transition-colors"
                        >
                          {keyword.keyword}
                        </Link>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
