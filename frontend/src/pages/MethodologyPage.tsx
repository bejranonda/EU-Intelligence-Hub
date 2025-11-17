/**
 * Methodology page explaining how the platform works
 */
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { BookOpen, Brain, Database, RefreshCw, Search, TrendingUp } from 'lucide-react';

export function MethodologyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-gray-50 flex flex-col">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1">
        {/* Hero */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-6">
            <BookOpen className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            How It Works
          </h1>
          <p className="text-xl text-gray-600">
            Understanding our methodology for AI-powered sentiment analysis
          </p>
        </div>

        {/* Overview */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Overview</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            The EU Intelligence Hub uses a multi-layered approach to collect, analyze, and present
            sentiment data from European news sources. Our methodology combines automated data
            collection, dual-layer AI analysis, and semantic search to provide comprehensive
            insights into media coverage.
          </p>
        </section>

        {/* Process Steps */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">The Process</h2>

          {/* Step 1 */}
          <div className="flex gap-6 mb-8">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                1
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <RefreshCw className="h-6 w-6 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-900">Data Collection</h3>
              </div>
              <p className="text-gray-700 mb-3">
                Our system automatically scrapes news from 12 European sources every hour,
                including BBC, Reuters, Deutsche Welle, France24, and others.
              </p>
              <div className="bg-gray-50 p-4 rounded-lg text-sm">
                <strong className="text-gray-900">Sources Include:</strong>
                <ul className="mt-2 grid grid-cols-2 gap-2 text-gray-600">
                  <li>• BBC (UK)</li>
                  <li>• Reuters (International)</li>
                  <li>• Deutsche Welle (Germany)</li>
                  <li>• France24 (France)</li>
                  <li>• EuroNews (Pan-European)</li>
                  <li>• And 7 more...</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="flex gap-6 mb-8">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                2
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <Brain className="h-6 w-6 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-900">Dual-Layer Sentiment Analysis</h3>
              </div>
              <p className="text-gray-700 mb-3">
                Each article undergoes a two-stage analysis process combining speed and accuracy:
              </p>

              <div className="space-y-3">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Layer 1: VADER Analysis</h4>
                  <p className="text-sm text-gray-700">
                    VADER (Valence Aware Dictionary and sEntiment Reasoner) provides fast baseline
                    sentiment scoring. It's particularly effective for social media and news text,
                    understanding context like negations and intensity modifiers.
                  </p>
                </div>

                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Layer 2: Google Gemini AI</h4>
                  <p className="text-sm text-gray-700">
                    Google's Gemini model provides nuanced analysis, understanding context, irony,
                    and subtle sentiment that rule-based systems might miss. It also provides
                    confidence scores and identifies emotional tones.
                  </p>
                </div>
              </div>

              <div className="mt-4 bg-gray-50 p-4 rounded-lg text-sm">
                <strong className="text-gray-900">Hybrid Scoring:</strong>
                <p className="text-gray-600 mt-2">
                  Final sentiment scores are calculated using a confidence-weighted combination:
                  <br />
                  <code className="bg-white px-2 py-1 rounded mt-2 inline-block">
                    sentiment = vader × (1 - confidence) + gemini × confidence
                  </code>
                </p>
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="flex gap-6 mb-8">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                3
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <Search className="h-6 w-6 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-900">Semantic Embeddings</h3>
              </div>
              <p className="text-gray-700 mb-3">
                Every article is converted into a 384-dimensional vector using Sentence Transformers,
                enabling semantic search that understands meaning, not just keywords.
              </p>
              <div className="bg-gray-50 p-4 rounded-lg text-sm">
                <strong className="text-gray-900">What This Means:</strong>
                <p className="text-gray-600 mt-2">
                  You can search for "climate crisis" and find articles about "environmental emergency"
                  or "global warming" because the system understands conceptual relationships.
                </p>
              </div>
            </div>
          </div>

          {/* Step 4 */}
          <div className="flex gap-6 mb-8">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                4
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <Database className="h-6 w-6 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-900">Data Aggregation</h3>
              </div>
              <p className="text-gray-700 mb-3">
                Daily aggregation tasks compute sentiment trends, identify relationships between
                keywords, and precompute statistics for fast retrieval.
              </p>
              <div className="bg-gray-50 p-4 rounded-lg text-sm">
                <ul className="space-y-2 text-gray-600">
                  <li>• <strong>Sentiment Trends:</strong> Daily average sentiment by keyword</li>
                  <li>• <strong>Keyword Relations:</strong> Topics that frequently appear together</li>
                  <li>• <strong>Source Analysis:</strong> Sentiment distribution by news source</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Step 5 */}
          <div className="flex gap-6">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                5
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <TrendingUp className="h-6 w-6 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-900">Visualization & Insights</h3>
              </div>
              <p className="text-gray-700 mb-3">
                The analyzed data is presented through interactive visualizations including
                timeline charts, sentiment distributions, and relationship mind maps.
              </p>
            </div>
          </div>
        </section>

        {/* Sentiment Scale */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Understanding Sentiment Scores</h2>
          <p className="text-gray-700 mb-6">
            Sentiment scores range from -1.0 (very negative) to +1.0 (very positive):
          </p>

          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <div className="w-32 text-right font-semibold text-gray-700">
                +0.3 to +1.0
              </div>
              <div className="flex-1 h-8 bg-green-500 rounded flex items-center px-4 text-white font-medium">
                Positive
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-32 text-right font-semibold text-gray-700">
                -0.3 to +0.3
              </div>
              <div className="flex-1 h-8 bg-gray-400 rounded flex items-center px-4 text-white font-medium">
                Neutral
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-32 text-right font-semibold text-gray-700">
                -1.0 to -0.3
              </div>
              <div className="flex-1 h-8 bg-red-500 rounded flex items-center px-4 text-white font-medium">
                Negative
              </div>
            </div>
          </div>

          <div className="mt-6 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
            <strong className="text-yellow-900">Important Note:</strong>
            <p className="text-yellow-800 text-sm mt-2">
              Sentiment analysis measures the tone and emotion of the text, not the factual accuracy
              or objectivity. A negative sentiment score doesn't mean the news is "bad" – it might
              be reporting on serious topics appropriately.
            </p>
          </div>
        </section>

        {/* Limitations */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Limitations & Considerations</h2>
          <div className="space-y-3 text-gray-700">
            <p>
              While our system is highly accurate, it's important to understand its limitations:
            </p>
            <ul className="space-y-2 ml-6">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>
                  <strong>Context Dependency:</strong> AI models may misinterpret sarcasm, irony,
                  or cultural references
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>
                  <strong>Source Diversity:</strong> Our analysis is limited to the 12 news sources
                  we monitor
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>
                  <strong>Language Variations:</strong> Sentiment analysis accuracy varies slightly
                  across different languages
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>
                  <strong>Timeliness:</strong> There's a delay of up to 1 hour between article
                  publication and analysis
                </span>
              </li>
            </ul>
          </div>
        </section>

        {/* Transparency */}
        <section className="bg-blue-50 p-8 rounded-lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Transparency & Ethics</h2>
          <p className="text-gray-700 mb-4">
            We believe in transparency about how our system works:
          </p>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>All sentiment scores include confidence levels</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Source attribution is always provided</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Our codebase is open source on GitHub</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>We don't editorialize or filter results based on sentiment</span>
            </li>
          </ul>
        </section>
      </main>

      <Footer />
    </div>
  );
}
