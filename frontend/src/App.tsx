import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => {
        setApiStatus(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to fetch API status:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🌍 European News Intelligence Hub
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered sentiment analysis of European media coverage about Thailand
          </p>
        </div>

        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-xl p-8">
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-3 text-gray-800">
                API Status
              </h3>
              {loading ? (
                <p className="text-gray-500">Loading...</p>
              ) : apiStatus ? (
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className={`font-semibold ${
                      apiStatus.status === 'healthy' ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {apiStatus.status || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Database:</span>
                    <span className={`font-semibold ${
                      apiStatus.database === 'healthy' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {apiStatus.database || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Environment:</span>
                    <span className="font-semibold text-blue-600">
                      {apiStatus.environment || 'Unknown'}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-red-500">Failed to connect to API</p>
              )}
            </div>

            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-3 text-gray-800">
                Features
              </h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <span className="mr-2">😊</span>
                  Sentiment Analysis
                </li>
                <li className="flex items-center">
                  <span className="mr-2">🗺️</span>
                  Mind Map Visualization
                </li>
                <li className="flex items-center">
                  <span className="mr-2">🔍</span>
                  Semantic Search
                </li>
                <li className="flex items-center">
                  <span className="mr-2">📊</span>
                  Trend Tracking
                </li>
                <li className="flex items-center">
                  <span className="mr-2">🌐</span>
                  Bilingual Support (EN/TH)
                </li>
              </ul>
            </div>
          </div>

          <div className="text-center">
            <p className="text-gray-600 mb-4">
              Phase 1: Foundation Complete ✅
            </p>
            <p className="text-sm text-gray-500">
              Full UI will be implemented in Phase 4
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
