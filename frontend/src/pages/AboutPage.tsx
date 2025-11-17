/**
 * About page component
 */
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { TrendingUp, Target, Users, Zap } from 'lucide-react';

export function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-gray-50 flex flex-col">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1">
        {/* Hero */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-6">
            <TrendingUp className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            About EU Intelligence Hub
          </h1>
          <p className="text-xl text-gray-600">
            Bringing clarity to European news through AI-powered sentiment analysis
          </p>
        </div>

        {/* Mission */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Mission</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            The European News Intelligence Hub is an AI-powered platform designed to help researchers,
            journalists, policymakers, and curious citizens understand how European news media covers
            geopolitical topics and events.
          </p>
          <p className="text-gray-700 leading-relaxed">
            In an era of information overload, we believe that understanding the sentiment and tone
            of news coverage is just as important as the facts themselves. Our platform aggregates
            and analyzes news from 12 major European sources, providing real-time insights into
            how different topics are perceived across the continent.
          </p>
        </section>

        {/* What We Do */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">What We Do</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Target className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Track Sentiment</h3>
              <p className="text-gray-600">
                Monitor how sentiment changes over time across different topics,
                identifying trends and shifts in media coverage.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Analysis</h3>
              <p className="text-gray-600">
                Dual-layer sentiment analysis combining VADER's speed with Google Gemini's
                nuanced understanding for accurate results.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Multi-Source</h3>
              <p className="text-gray-600">
                Aggregate news from 12 reputable European sources including BBC, Reuters,
                Deutsche Welle, France24, and more.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Discover Relationships</h3>
              <p className="text-gray-600">
                Interactive mind maps reveal connections between topics, helping you
                understand the broader context of news coverage.
              </p>
            </div>
          </div>
        </section>

        {/* Key Features */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Key Features</h2>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-sm">✓</span>
              </div>
              <div>
                <strong className="text-gray-900">Real-Time Monitoring:</strong>{' '}
                <span className="text-gray-700">
                  Hourly scraping of news sources ensures up-to-date sentiment tracking
                </span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-sm">✓</span>
              </div>
              <div>
                <strong className="text-gray-900">Semantic Search:</strong>{' '}
                <span className="text-gray-700">
                  384-dimensional vector embeddings enable intelligent article discovery
                </span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-sm">✓</span>
              </div>
              <div>
                <strong className="text-gray-900">Multi-Language Support:</strong>{' '}
                <span className="text-gray-700">
                  Interface and analysis available in 9 European languages
                </span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-sm">✓</span>
              </div>
              <div>
                <strong className="text-gray-900">Interactive Visualizations:</strong>{' '}
                <span className="text-gray-700">
                  Timeline charts and relationship mind maps make complex data accessible
                </span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-sm">✓</span>
              </div>
              <div>
                <strong className="text-gray-900">Document Analysis:</strong>{' '}
                <span className="text-gray-700">
                  Upload your own documents for sentiment analysis and keyword extraction
                </span>
              </div>
            </li>
          </ul>
        </section>

        {/* Technology Stack */}
        <section className="mb-12 bg-gray-50 p-6 rounded-lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Technology</h2>
          <p className="text-gray-700 mb-4">
            Built with modern technologies for speed, accuracy, and scalability:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white p-3 rounded border">
              <strong className="text-gray-900">Backend:</strong>
              <p className="text-gray-600">FastAPI + Python 3.11</p>
            </div>
            <div className="bg-white p-3 rounded border">
              <strong className="text-gray-900">Frontend:</strong>
              <p className="text-gray-600">React + TypeScript</p>
            </div>
            <div className="bg-white p-3 rounded border">
              <strong className="text-gray-900">Database:</strong>
              <p className="text-gray-600">PostgreSQL + pgvector</p>
            </div>
            <div className="bg-white p-3 rounded border">
              <strong className="text-gray-900">AI/ML:</strong>
              <p className="text-gray-600">Google Gemini + VADER</p>
            </div>
            <div className="bg-white p-3 rounded border">
              <strong className="text-gray-900">Task Queue:</strong>
              <p className="text-gray-600">Celery + Redis</p>
            </div>
            <div className="bg-white p-3 rounded border">
              <strong className="text-gray-900">Deployment:</strong>
              <p className="text-gray-600">Docker + Nginx</p>
            </div>
          </div>
        </section>

        {/* Contact */}
        <section className="bg-blue-50 p-8 rounded-lg text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Get in Touch</h2>
          <p className="text-gray-700 mb-6">
            Have questions, suggestions, or want to contribute? We'd love to hear from you.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="mailto:contact@eu-intelligence-hub.com"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Contact Us
            </a>
            <a
              href="https://github.com/ChildWerapol/EU-Intelligence-Hub"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-white text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
            >
              View on GitHub
            </a>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
