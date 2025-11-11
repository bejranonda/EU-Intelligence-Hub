import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { fetchJSON, postJSON } from '../api/client';

type EvaluationMetadata = {
  searchability_score: number;
  significance_score: number;
  specificity: string;
  decision: string;
  reasoning: string;
  created_at: string;
};

type AdminSuggestion = {
  id: number;
  keyword_en: string;
  keyword_th?: string;
  keyword_de?: string;
  keyword_fr?: string;
  keyword_es?: string;
  keyword_it?: string;
  keyword_pl?: string;
  keyword_sv?: string;
  keyword_nl?: string;
  category: string;
  reason?: string;
  votes: number;
  status: string;
  created_at: string;
  latest_evaluation?: EvaluationMetadata;
};

async function loadPendingSuggestions(): Promise<AdminSuggestion[]> {
  const data = await fetchJSON('/admin/keywords/suggestions/pending?limit=100') as { pending_suggestions?: AdminSuggestion[] };
  const suggestions: AdminSuggestion[] = data.pending_suggestions ?? [];

  const evaluationRequests = suggestions.map((s) =>
    fetchJSON(`/admin/keywords/suggestions/${s.id}/evaluations`).catch(() => null),
  );

  const evaluations = await Promise.all(evaluationRequests);

  return suggestions.map((suggestion, index) => {
    const evaluationPayload = evaluations[index] as { evaluations?: any[] } | null;
    const latest = evaluationPayload?.evaluations?.[0];
    const latestEval = latest
      ? {
          searchability_score: latest.searchability_score,
          significance_score: latest.significance_score,
          specificity: latest.specificity,
          decision: latest.decision,
          reasoning: latest.reasoning,
          created_at: latest.created_at,
        }
      : undefined;

    return { ...suggestion, latest_evaluation: latestEval };
  });
}

async function mutateSuggestion(
  suggestionId: number,
  action: 'process' | 'approve' | 'reject',
  payload?: Record<string, unknown>,
) {
  let url = `/admin/keywords/suggestions/${suggestionId}/${action}`;
  if (action === 'process') {
    url = `/admin/keywords/suggestions/${suggestionId}/process`;
  }
  return postJSON(url, payload ?? {});
}

function ScoreBadge({ label, value }: { label: string; value?: number }) {
  if (typeof value !== 'number') return null;
  const color = value >= 7 ? 'bg-green-100 text-green-800' : value >= 5 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800';
  return (
    <span className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium ${color}`}>
      <span>{label}</span>
      <span>{value}</span>
    </span>
  );
}

export function AdminSuggestionsPage() {
  const queryClient = useQueryClient();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-suggestions'],
    queryFn: loadPendingSuggestions,
  });

  const processMutation = useMutation({
    mutationFn: (suggestionId: number) => mutateSuggestion(suggestionId, 'process'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-suggestions'] }),
  });

  const approveMutation = useMutation({
    mutationFn: (suggestionId: number) => mutateSuggestion(suggestionId, 'approve'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-suggestions'] }),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ suggestionId, reason }: { suggestionId: number; reason?: string }) =>
      mutateSuggestion(suggestionId, 'reject', reason ? { reason } : undefined),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-suggestions'] }),
  });

  const filteredSuggestions = (data ?? []).filter((suggestion) =>
    selectedCategory === 'all' ? true : suggestion.category === selectedCategory,
  );

  const categories = Array.from(new Set((data ?? []).map((s) => s.category))).sort();

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Pending Suggestions</h1>
          <p className="mt-2 text-sm text-slate-600">
            Review AI scoring, approve strong candidates, or send items to manual review queue.
          </p>
        </div>
        <select
          value={selectedCategory}
          onChange={(event) => setSelectedCategory(event.target.value)}
          className="rounded border border-slate-300 px-3 py-1 text-sm focus:border-blue-500 focus:outline-none"
        >
          <option value="all">All categories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p className="text-sm text-slate-500">Loading suggestions…</p>}
      {isError && <p className="text-sm text-red-600">Unable to load suggestions.</p>}

      <div className="space-y-4">
        {filteredSuggestions.map((suggestion) => {
          const evaluation = suggestion.latest_evaluation;
          return (
            <div key={suggestion.id} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-semibold text-slate-900">{suggestion.keyword_en}</h2>
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-xs uppercase tracking-wide text-slate-600">
                      {suggestion.category}
                    </span>
                    <span className="rounded bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                      Votes: {suggestion.votes}
                    </span>
                  </div>
                  {suggestion.reason && <p className="text-sm text-slate-600">{suggestion.reason}</p>}
                  {evaluation ? (
                    <div className="flex flex-wrap items-center gap-2 text-xs text-slate-600">
                      <ScoreBadge label="Searchability" value={evaluation.searchability_score} />
                      <ScoreBadge label="Significance" value={evaluation.significance_score} />
                      <span className="rounded bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                        Specificity: {evaluation.specificity}
                      </span>
                      <span className="rounded bg-purple-100 px-2 py-0.5 font-medium text-purple-700">
                        Decision: {evaluation.decision}
                      </span>
                      <span className="text-slate-500">{new Date(evaluation.created_at).toLocaleString()}</span>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">Awaiting AI evaluation</p>
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    className="rounded bg-blue-600 px-3 py-1 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                    onClick={() => processMutation.mutate(suggestion.id)}
                    disabled={processMutation.isPending}
                  >
                    Re-run AI Evaluation
                  </button>
                  <button
                    className="rounded bg-green-600 px-3 py-1 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
                    onClick={() => approveMutation.mutate(suggestion.id)}
                    disabled={approveMutation.isPending}
                  >
                    Approve & Publish
                  </button>
                  <button
                    className="rounded bg-red-600 px-3 py-1 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                    onClick={() => rejectMutation.mutate({ suggestionId: suggestion.id })}
                    disabled={rejectMutation.isPending}
                  >
                    Reject
                  </button>
                </div>
              </div>

              {evaluation?.reasoning && (
                <div className="mt-3 rounded bg-slate-50 p-3 text-sm text-slate-700">
                  <p className="font-medium text-slate-900">Reasoning</p>
                  <p className="mt-1 leading-relaxed">{evaluation.reasoning}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
