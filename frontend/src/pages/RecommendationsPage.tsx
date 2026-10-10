import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  ListChecks,
  RefreshCw,
  Search,
  Clock,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { RecommendationsResponse } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

export const RecommendationsPage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [recData, setRecData] = useState<RecommendationsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const loadRecs = useCallback(async () => {
    if (!effectiveInvId) {
      setRecData(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getRecommendations(effectiveInvId);
      setRecData(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query recommendations');
    } finally {
      setIsLoading(false);
    }
  }, [effectiveInvId]);

  useEffect(() => {
    if (effectiveInvId && effectiveInvId !== activeInvestigationId) {
      setActiveInvestigationId(effectiveInvId);
    }
  }, [effectiveInvId, activeInvestigationId, setActiveInvestigationId]);

  useEffect(() => {
    loadRecs();
  }, [loadRecs]);

  const rawRecs = recData?.recommendations || [];

  const filteredRecs = rawRecs.filter((r) => {
    const matchesPriority =
      priorityFilter === 'ALL' ||
      (r.priority && r.priority.toUpperCase() === priorityFilter);
    const matchesSearch =
      r.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.title && r.title.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (r.action_type && r.action_type.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesPriority && matchesSearch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <ListChecks className="w-5 h-5 text-accent-light" />
            INCIDENT RESPONSE RECOMMENDATIONS
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Actionable containment, eradication, and remediation guidance derived from reconstructed findings.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadRecs()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh recommendations"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Investigation Scoper & Filter */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-surface border border-border p-3 rounded-lg">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-2xs font-mono uppercase text-foreground-subtle whitespace-nowrap">
            Investigation:
          </span>
          <select
            value={effectiveInvId || ''}
            onChange={(e) => setActiveInvestigationId(e.target.value)}
            className="px-2.5 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground font-mono focus:outline-none cursor-pointer max-w-xs truncate"
          >
            {investigations.map((i) => (
              <option key={i.investigation_id} value={i.investigation_id}>
                {i.investigation_id} ({i.status})
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-60">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-subtle" />
            <input
              type="text"
              placeholder="Search actions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
            />
          </div>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground font-mono focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <LoadingSpinner label="Querying forensic response recommendations..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={ListChecks}
          title="No Investigation Selected"
          description="Select an investigation to inspect forensic response recommendations."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {recData?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="Recommendations Engine Not Connected"
              message={recData.message}
              pipelineStage="RECOMMENDATIONS (Stage 15)"
              investigationId={effectiveInvId}
            />
          )}

          {/* Operational Advisory Warning */}
          <div className="bg-surface border border-border rounded-lg p-4 font-mono text-xs flex items-start gap-3">
            <Clock className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
            <div className="space-y-1 text-2xs leading-relaxed">
              <strong className="text-foreground">Advisory vs Completed Action Distinction:</strong>
              <p className="text-foreground-muted">
                Items listed in this view represent recommended containment and remediation procedures
                synthesized by TRACEWEAVE. Listing a recommendation does NOT indicate that the mitigation
                has been executed in active enterprise infrastructure.
              </p>
            </div>
          </div>

          {/* Recommendations List / State */}
          {filteredRecs.length > 0 ? (
            <div className="space-y-3">
              {filteredRecs.map((rec, idx) => (
                <div
                  key={idx}
                  className="bg-surface border border-border rounded-lg p-4 font-mono text-xs space-y-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-foreground">{rec.title || `Action ${idx + 1}`}</span>
                      <StatusBadge status={rec.priority || 'MEDIUM'} type="priority" size="sm" />
                    </div>
                    {rec.action_type && (
                      <span className="px-2 py-0.5 rounded bg-surface-subtle text-accent-light border border-border text-2xs">
                        {rec.action_type}
                      </span>
                    )}
                  </div>
                  <p className="text-foreground-muted font-sans text-xs leading-relaxed">
                    {rec.description}
                  </p>
                  {rec.evidence_ref && (
                    <div className="pt-2 border-t border-border/50 text-2xs text-foreground-subtle">
                      Supporting Evidence: <span className="text-foreground-muted">{rec.evidence_ref}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-10 text-center bg-surface border border-dashed border-border rounded-lg">
              <ListChecks className="w-8 h-8 text-foreground-subtle mx-auto mb-2 opacity-60" />
              <h3 className="text-xs font-semibold text-foreground font-mono">
                No Recommendations Available
              </h3>
              <p className="text-2xs text-foreground-muted max-w-md mx-auto mt-1 leading-relaxed">
                Stage 15 recommendations will be populated once the forensic reconstruction pipeline concludes.
                Currently, the backend returned 0 recommendation objects.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
