/**
 * Main application component with routing
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HomePage } from './pages/HomePage';
import { KeywordDetailPage } from './pages/KeywordDetailPage';
import { UploadPage } from './pages/UploadPage';
import { SuggestPage } from './pages/SuggestPage';
import { SearchPage } from './pages/SearchPage';
import { AdminSuggestionsPage } from './pages/AdminSuggestionsPage';
import { AdminSourcesPage } from './pages/AdminSourcesPage';

// Create a React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/keyword/:id" element={<KeywordDetailPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/suggest" element={<SuggestPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/admin/suggestions" element={<AdminSuggestionsPage />} />
          <Route path="/admin/sources" element={<AdminSourcesPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
