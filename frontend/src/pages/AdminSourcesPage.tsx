import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchJSON, postJSON } from '../api/client';

type NewsSource = {
  id: number;
  name: string;
  base_url: string;
  enabled: boolean;
  language: string;
  country?: string | null;
  priority: number;
  parser?: string | null;
  tags: string[];
  created_at?: string | null;
  updated_at?: string | null;
};

type IngestionEntry = {
  id: number;
  last_run_at: string | null;
  articles_ingested: number;
  success: boolean;
  notes?: string | null;
};

async function loadSources(): Promise<NewsSource[]> {
  const payload = await fetchJSON('/admin/sources');
  return payload.sources ?? [];
}

async function loadIngestionHistory(sourceId: number): Promise<IngestionEntry[]> {
  const payload = await fetchJSON(`/admin/sources/${sourceId}/ingestion?limit=20`);
  return payload.history ?? [];
}

export function AdminSourcesPage() {
  const queryClient = useQueryClient();
  const [activeSourceId, setActiveSourceId] = useState<number | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    base_url: '',
    language: 'en',
    country: '',
    priority: 0,
    parser: '',
    tags: '',
  });

  const { data: sources = [], isLoading, isError } = useQuery({
    queryKey: ['admin-sources'],
    queryFn: loadSources,
  });

  const activeSource = useMemo(
    () => sources.find((source) => source.id === activeSourceId) ?? null,
    [sources, activeSourceId],
  );

  const { data: history = [], isLoading: historyLoading } = useQuery({
    queryKey: ['admin-source-history', activeSourceId],
    queryFn: () => (activeSourceId ? loadIngestionHistory(activeSourceId) : Promise.resolve([])),
    enabled: activeSourceId !== null,
  });

  const toggleMutation = useMutation({
    mutationFn: async ({ sourceId, enabled }: { sourceId: number; enabled: boolean }) =>
      postJSON(`/admin/sources/${sourceId}/toggle?enabled=${enabled}`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-sources'] }),
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        name: formData.name,
        base_url: formData.base_url,
        language: formData.language || undefined,
        country: formData.country || undefined,
        priority: Number(formData.priority) || 0,
        parser: formData.parser || undefined,
        tags: formData.tags
          .split(',')
          .map((tag) => tag.trim())
          .filter(Boolean),
      };
      return postJSON('/admin/sources', payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-sources'] });
      setFormData({ name: '', base_url: '', language: 'en', country: '', priority: 0, parser: '', tags: '' });
      setShowCreate(false);
    },
  });

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">News Sources</h1>
          <p className="mt-2 text-sm text-slate-600">Manage scraping sources, priorities, and ingestion history.</p>
        </div>
        <button
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          onClick={() => setShowCreate((value) => !value)}
        >
          {showCreate ? 'Close' : 'Add Source'}
        </button>
      </div>

      {showCreate && (
        <form
          className="mb-8 grid gap-4 rounded border border-slate-200 bg-white p-4 shadow"
          onSubmit={(event) => {
            event.preventDefault();
            createMutation.mutate();
          }}
        >
          <div className="grid gap-1">
            <label className="text-xs font-medium text-slate-500">Name</label>
            <input
              className="rounded border border-slate-300 px-2 py-1 text-sm"
              value={formData.name}
              onChange={(event) => setFormData((prev) => ({ ...prev, name: event.target.value }))}
              required
            />
          </div>
          <div className="grid gap-1">
            <label className="text-xs font-medium text-slate-500">Base URL</label>
            <input
              className="rounded border border-slate-300 px-2 py-1 text-sm"
              value={formData.base_url}
              onChange={(event) => setFormData((prev) => ({ ...prev, base_url: event.target.value }))}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-1">
              <label className="text-xs font-medium text-slate-500">Language</label>
              <input
                className="rounded border border-slate-300 px-2 py-1 text-sm"
                value={formData.language}
                onChange={(event) => setFormData((prev) => ({ ...prev, language: event.target.value }))}
              />
            </div>
            <div className="grid gap-1">
              <label className="text-xs font-medium text-slate-500">Country</label>
              <input
                className="rounded border border-slate-300 px-2 py-1 text-sm"
                value={formData.country}
                onChange={(event) => setFormData((prev) => ({ ...prev, country: event.target.value }))}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-1">
              <label className="text-xs font-medium text-slate-500">Priority</label>
              <input
                type="number"
                className="rounded border border-slate-300 px-2 py-1 text-sm"
                value={formData.priority}
                onChange={(event) => setFormData((prev) => ({ ...prev, priority: Number(event.target.value) }))}
              />
            </div>
            <div className="grid gap-1">
              <label className="text-xs font-medium text-slate-500">Parser</label>
              <input
                className="rounded border border-slate-300 px-2 py-1 text-sm"
                value={formData.parser}
                onChange={(event) => setFormData((prev) => ({ ...prev, parser: event.target.value }))}
              />
            </div>
          </div>
          <div className="grid gap-1">
            <label className="text-xs font-medium text-slate-500">Tags (comma separated)</label>
            <input
              className="rounded border border-slate-300 px-2 py-1 text-sm"
              value={formData.tags}
              onChange={(event) => setFormData((prev) => ({ ...prev, tags: event.target.value }))}
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              type="button"
              className="rounded border border-slate-300 px-4 py-2 text-sm"
              onClick={() => {
                setShowCreate(false);
                setFormData({ name: '', base_url: '', language: 'en', country: '', priority: 0, parser: '', tags: '' });
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Creating…' : 'Create source'}
            </button>
          </div>
        </form>
      )}

      {isLoading && <p className="text-sm text-slate-500">Loading sources…</p>}
      {isError && <p className="text-sm text-red-600">Unable to load sources.</p>}

      <div className="grid gap-4">
        {sources.map((source) => (
          <div key={source.id} className="rounded border border-slate-200 bg-white p-4 shadow">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-xl font-semibold text-slate-900">{source.name}</h2>
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                    Priority {source.priority}
                  </span>
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-medium ${source.enabled ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-600'}`}
                  >
                    {source.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-600">{source.base_url}</p>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  {source.language && <span className="rounded bg-slate-100 px-2 py-0.5">Lang: {source.language}</span>}
                  {source.country && <span className="rounded bg-slate-100 px-2 py-0.5">Country: {source.country}</span>}
                  {source.parser && <span className="rounded bg-slate-100 px-2 py-0.5">Parser: {source.parser}</span>}
                  {source.tags.map((tag) => (
                    <span key={tag} className="rounded bg-blue-50 px-2 py-0.5 text-blue-700">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                <button
                  className="rounded bg-slate-200 px-3 py-1 text-xs font-medium text-slate-800 hover:bg-slate-300"
                  onClick={() => setActiveSourceId((value) => (value === source.id ? null : source.id))}
                >
                  {activeSourceId === source.id ? 'Hide history' : 'View history'}
                </button>
                <button
                  className="rounded bg-blue-600 px-3 py-1 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                  onClick={() => toggleMutation.mutate({ sourceId: source.id, enabled: !source.enabled })}
                  disabled={toggleMutation.isPending}
                >
                  {source.enabled ? 'Disable source' : 'Enable source'}
                </button>
              </div>
            </div>

            {activeSourceId === source.id && (
              <div className="mt-4 rounded border border-slate-100 bg-slate-50 p-3">
                <h3 className="text-sm font-semibold text-slate-700">Recent ingestion runs</h3>
                {historyLoading && <p className="mt-2 text-xs text-slate-500">Loading…</p>}
                {!historyLoading && history.length === 0 && <p className="mt-2 text-xs text-slate-500">No history recorded.</p>}
                <ul className="mt-2 space-y-2 text-xs text-slate-600">
                  {history.map((entry) => (
                    <li key={entry.id} className="flex items-center justify-between rounded bg-white px-3 py-2 shadow">
                      <div>
                        <p className="font-medium">
                          {entry.last_run_at ? new Date(entry.last_run_at).toLocaleString() : 'Unknown time'}
                        </p>
                        <p className="mt-1 text-[11px] text-slate-500">{entry.notes || 'No notes recorded.'}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span>{entry.articles_ingested} articles</span>
                        <span className={entry.success ? 'text-green-600' : 'text-red-600'}>
                          {entry.success ? 'Success' : 'Failed'}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
