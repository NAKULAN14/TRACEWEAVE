import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Activity,
  Plus,
  Play,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { Investigation } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { formatDate } from '../lib/utils';

export const InvestigationsPage: React.FC = () => {
  const { cases, activeCaseId, setActiveCaseId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const caseIdParam = searchParams.get('case_id');
  const effectiveCaseId = caseIdParam || activeCaseId || (cases.length > 0 ? cases[0].case_id : null);

  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStartingId, setIsStartingId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadInvestigations = useCallback(async () => {
    if (!effectiveCaseId) {
      setInvestigations([]);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.listCaseInvestigations(effectiveCaseId);
      setInvestigations(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load investigations');
      setInvestigations([]);
    } finally {
      setIsLoading(false);
    }
  }, [effectiveCaseId]);

  useEffect(() => {
    if (effectiveCaseId && effectiveCaseId !== activeCaseId) {
      setActiveCaseId(effectiveCaseId);
    }
  }, [effectiveCaseId, activeCaseId, setActiveCaseId]);

  useEffect(() => {
    loadInvestigations();
  }, [loadInvestigations]);

  const handleCreate = async () => {
    if (!effectiveCaseId) return;
    setIsCreating(true);
    try {
      const created = await api.createInvestigation(effectiveCaseId);
      setActiveInvestigationId(created.investigation_id);
      await loadInvestigations();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Investigation creation failed');
    } finally {
      setIsCreating(false);
    }
  };

  const handleStart = async (invId: string) => {
    setIsStartingId(invId);
    try {
      await api.startInvestigation(invId);
      await loadInvestigations();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to start investigation');
    } finally {
      setIsStartingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Activity className="w-5 h-5 text-accent-light" />
            INVESTIGATION RUNS
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Reconstruction runs executing the 15-stage TRACEWEAVE pipeline.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {effectiveCaseId && (
            <button
              type="button"
              onClick={handleCreate}
              disabled={isCreating}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors disabled:opacity-50"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{isCreating ? 'Creating...' : 'New Investigation'}</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => loadInvestigations()}
            disabled={isLoading || !effectiveCaseId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh investigations"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Case Scoping Toolbar */}
      <div className="flex items-center justify-between gap-3 bg-surface border border-border p-3 rounded-lg">
        <div className="flex items-center gap-2">
          <span className="text-2xs font-mono uppercase text-foreground-subtle whitespace-nowrap">
            Scoped Case:
          </span>
          <select
            value={effectiveCaseId || ''}
            onChange={(e) => setActiveCaseId(e.target.value)}
            className="px-2.5 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground font-mono focus:outline-none cursor-pointer max-w-xs truncate"
          >
            {cases.map((c) => (
              <option key={c.case_id} value={c.case_id}>
                {c.case_id} — {c.title}
              </option>
            ))}
          </select>
        </div>

        <div className="text-2xs font-mono text-foreground-subtle">
          Total Runs: {investigations.length}
        </div>
      </div>

      {/* Content Area */}
      {isLoading ? (
        <LoadingSpinner label="Querying investigation records..." />
      ) : !effectiveCaseId ? (
        <EmptyState
          icon={Activity}
          title="No Case Selected"
          description="Select an active case to view or launch investigation runs."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : investigations.length === 0 ? (
        <EmptyState
          icon={Activity}
          title="No Investigations Found"
          description={`No investigations have been registered for ${effectiveCaseId}. Initialize a new investigation run to begin pipeline execution.`}
          action={
            <button
              type="button"
              onClick={handleCreate}
              disabled={isCreating}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Initialize First Investigation</span>
            </button>
          }
        />
      ) : (
        <div className="space-y-4">
          <div className="bg-surface border border-border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-border bg-surface-subtle text-2xs uppercase tracking-wider text-foreground-subtle font-mono">
                    <th className="px-4 py-2.5">Investigation ID</th>
                    <th className="px-4 py-2.5">Lifecycle Status</th>
                    <th className="px-4 py-2.5">Pipeline Stage</th>
                    <th className="px-4 py-2.5">Created</th>
                    <th className="px-4 py-2.5">Started</th>
                    <th className="px-4 py-2.5">Completed</th>
                    <th className="px-4 py-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {investigations.map((inv) => (
                    <tr
                      key={inv.investigation_id}
                      onClick={() => {
                        setActiveInvestigationId(inv.investigation_id);
                        navigate(`/investigations/${inv.investigation_id}`);
                      }}
                      className="hover:bg-surface-elevated/60 transition-colors cursor-pointer group"
                    >
                      <td className="px-4 py-3 font-mono font-medium text-accent-light whitespace-nowrap">
                        <div className="flex items-center gap-1">
                          <span>{inv.investigation_id}</span>
                          <CopyButton value={inv.investigation_id} />
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <StatusBadge status={inv.status} type="investigation" size="sm" />
                      </td>
                      <td className="px-4 py-3 font-mono text-2xs whitespace-nowrap">
                        {inv.current_stage ? (
                          <span className="text-amber-300 font-medium">
                            {inv.current_stage}
                          </span>
                        ) : (
                          <span className="text-foreground-subtle">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 font-mono text-2xs text-foreground-muted whitespace-nowrap">
                        {formatDate(inv.created_at)}
                      </td>
                      <td className="px-4 py-3 font-mono text-2xs text-foreground-subtle whitespace-nowrap">
                        {formatDate(inv.started_at)}
                      </td>
                      <td className="px-4 py-3 font-mono text-2xs text-foreground-subtle whitespace-nowrap">
                        {formatDate(inv.completed_at)}
                      </td>
                      <td className="px-4 py-3 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          {inv.status === 'PENDING' && (
                            <button
                              type="button"
                              onClick={() => handleStart(inv.investigation_id)}
                              disabled={isStartingId === inv.investigation_id}
                              className="inline-flex items-center gap-1 px-2.5 py-1 text-2xs font-medium rounded bg-emerald-950 border border-emerald-700 text-emerald-300 hover:bg-emerald-900 transition-colors"
                            >
                              <Play className="w-3 h-3" />
                              <span>{isStartingId === inv.investigation_id ? 'Starting...' : 'Start'}</span>
                            </button>
                          )}
                          <button
                            type="button"
                            onClick={() => {
                              setActiveInvestigationId(inv.investigation_id);
                              navigate(`/investigations/${inv.investigation_id}`);
                            }}
                            className="inline-flex items-center gap-1 px-2.5 py-1 text-2xs font-medium rounded bg-surface-elevated hover:bg-surface-active text-foreground border border-border"
                          >
                            <span>Inspect</span>
                            <ExternalLink className="w-3 h-3 text-foreground-subtle" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
