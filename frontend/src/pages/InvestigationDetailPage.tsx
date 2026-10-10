import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Play,
  RefreshCw,
  Clock,
  Layers,
  ShieldAlert,
  Radio,
  Network,
  GitMerge,
  FileText,
  AlertCircle,
  CheckCircle2,
  Circle,
} from 'lucide-react';
import { api } from '../api/client';
import { Investigation, InvestigationStageStatus } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatDate } from '../lib/utils';
import { useInvestigation } from '../context/InvestigationContext';

export const InvestigationDetailPage: React.FC = () => {
  const { investigationId } = useParams<{ investigationId: string }>();
  const navigate = useNavigate();
  const { setActiveInvestigationId, setActiveCaseId } = useInvestigation();

  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [stages, setStages] = useState<InvestigationStageStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!investigationId) return;
    setIsLoading(true);
    setError(null);
    try {
      const [inv, stageList] = await Promise.all([
        api.getInvestigation(investigationId),
        api.getInvestigationStages(investigationId).catch(() => []),
      ]);
      setInvestigation(inv);
      setStages(stageList);
      setActiveInvestigationId(inv.investigation_id);
      setActiveCaseId(inv.case_id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load investigation');
    } finally {
      setIsLoading(false);
    }
  }, [investigationId, setActiveInvestigationId, setActiveCaseId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStart = async () => {
    if (!investigationId) return;
    setIsStarting(true);
    try {
      await api.startInvestigation(investigationId);
      await loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to start investigation');
    } finally {
      setIsStarting(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner label="Fetching investigation run status..." />;
  }

  if (error || !investigation) {
    return (
      <div className="space-y-4 max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/investigations')}
          className="inline-flex items-center gap-1.5 text-xs text-foreground-muted hover:text-foreground font-mono"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Investigations
        </button>
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error || 'Investigation not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-mono text-foreground-subtle">
          <Link to="/investigations" className="hover:text-foreground flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Investigations
          </Link>
          <span>/</span>
          <span className="text-foreground-muted">{investigation.investigation_id}</span>
        </div>
        <div className="flex items-center gap-2">
          {investigation.status === 'PENDING' && (
            <button
              type="button"
              onClick={handleStart}
              disabled={isStarting}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-emerald-950 border border-emerald-700 text-emerald-300 hover:bg-emerald-900 transition-colors disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{isStarting ? 'Starting Pipeline...' : 'Start Investigation'}</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => loadData()}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh status"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Investigation Details Card */}
      <div className="bg-surface border border-border rounded-lg p-5">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-accent-light">
                {investigation.investigation_id}
              </span>
              <CopyButton value={investigation.investigation_id} />
              <StatusBadge status={investigation.status} type="investigation" />
            </div>
            <div className="flex items-center gap-2 text-xs font-mono text-foreground-muted">
              <span>Bound to Case:</span>
              <Link
                to={`/cases/${investigation.case_id}`}
                className="text-sky-400 hover:underline font-semibold"
              >
                {investigation.case_id}
              </Link>
            </div>
            {investigation.error_message && (
              <div className="p-2.5 rounded bg-rose-950/70 border border-rose-800 text-rose-300 text-xs font-mono">
                <strong>Error:</strong> {investigation.error_message}
              </div>
            )}
          </div>

          <div className="flex flex-col items-start md:items-end gap-1.5 text-2xs font-mono text-foreground-subtle border-t md:border-t-0 pt-3 md:pt-0 border-border">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              <span>Created: {formatDate(investigation.created_at)}</span>
            </div>
            <div>Started: {formatDate(investigation.started_at)}</div>
            <div>Completed: {formatDate(investigation.completed_at)}</div>
          </div>
        </div>

        {/* Current Stage Indicator */}
        <div className="mt-5 pt-4 border-t border-border flex items-center justify-between text-xs font-mono">
          <div>
            <span className="text-foreground-subtle text-2xs block uppercase">Current Pipeline Stage</span>
            <span className="text-sm font-bold text-amber-400">
              {investigation.current_stage || (investigation.status === 'PENDING' ? 'Awaiting Start' : 'Idle')}
            </span>
          </div>
          <div>
            <span className="text-foreground-subtle text-2xs block uppercase">Total Stages</span>
            <span className="text-sm font-bold text-foreground">15 Stages</span>
          </div>
        </div>
      </div>

      {/* 15-Stage Pipeline Sequence Visualizer */}
      <div className="bg-surface border border-border rounded-lg p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-foreground font-mono flex items-center gap-2">
              <Layers className="w-4 h-4 text-accent-light" />
              15-Stage Forensic Pipeline Execution
            </h2>
            <p className="text-2xs text-foreground-muted mt-0.5">
              Reflects actual execution stages returned from <code className="text-accent-light font-mono">/api/investigations/{'{id}'}/status</code>
            </p>
          </div>
          <span className="text-2xs font-mono text-foreground-subtle">
            Sequence: 1 → 15
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {stages.length > 0 ? (
            stages.map((stg) => {
              const isCurrent = investigation.current_stage === stg.stage;
              const isCompleted = stg.status === 'COMPLETED';
              const isFailed = stg.status === 'FAILED';

              return (
                <div
                  key={stg.sequence}
                  className={`p-3 rounded border text-xs font-mono flex items-center justify-between transition-colors ${
                    isCurrent
                      ? 'bg-amber-950/40 border-amber-600/80 text-amber-200'
                      : isCompleted
                      ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-300'
                      : isFailed
                      ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                      : 'bg-surface-subtle border-border/80 text-foreground-muted'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="w-5 h-5 rounded-full bg-surface-elevated border border-border flex items-center justify-center text-2xs text-foreground-subtle flex-shrink-0">
                      {stg.sequence}
                    </span>
                    <div>
                      <div className="font-semibold">{stg.stage}</div>
                      <div className="text-2xs opacity-70">Stage {stg.sequence} of 15</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : isFailed ? (
                      <AlertCircle className="w-4 h-4 text-rose-400" />
                    ) : isCurrent ? (
                      <span className="inline-block w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
                    ) : (
                      <Circle className="w-3.5 h-3.5 text-foreground-subtle opacity-40" />
                    )}
                    <span className="text-2xs uppercase tracking-tight">{stg.status}</span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-3 text-xs text-foreground-muted p-4 bg-surface-subtle rounded border border-border">
              Pipeline stage statuses not yet populated. Start investigation to engage pipeline.
            </div>
          )}
        </div>
      </div>

      {/* Forensic Findings Navigation Grid */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-foreground font-mono">
          Correlated Forensic Analysis Modules
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <Link
            to={`/iocs?investigation_id=${investigation.investigation_id}`}
            className="p-4 bg-surface hover:bg-surface-elevated border border-border rounded-lg transition-colors group flex items-start gap-3"
          >
            <ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5 group-hover:scale-105 transition-transform" />
            <div>
              <div className="text-xs font-semibold text-foreground group-hover:text-accent-light">
                IOC Analysis
              </div>
              <p className="text-2xs text-foreground-muted mt-0.5">
                Inspect extracted URLs, domains, QR code payloads, and hashes.
              </p>
            </div>
          </Link>

          <Link
            to={`/threat-intel?investigation_id=${investigation.investigation_id}`}
            className="p-4 bg-surface hover:bg-surface-elevated border border-border rounded-lg transition-colors group flex items-start gap-3"
          >
            <Radio className="w-5 h-5 text-sky-400 mt-0.5 group-hover:scale-105 transition-transform" />
            <div>
              <div className="text-xs font-semibold text-foreground group-hover:text-accent-light">
                Threat Intelligence
              </div>
              <p className="text-2xs text-foreground-muted mt-0.5">
                Threat provider reputation queries and indicator verdicts.
              </p>
            </div>
          </Link>

          <Link
            to={`/graph?investigation_id=${investigation.investigation_id}`}
            className="p-4 bg-surface hover:bg-surface-elevated border border-border rounded-lg transition-colors group flex items-start gap-3"
          >
            <Network className="w-5 h-5 text-purple-400 mt-0.5 group-hover:scale-105 transition-transform" />
            <div>
              <div className="text-xs font-semibold text-foreground group-hover:text-accent-light">
                Infrastructure Graph
              </div>
              <p className="text-2xs text-foreground-muted mt-0.5">
                Interactive topology of DNS, IPs, TLS certificates, and domains.
              </p>
            </div>
          </Link>

          <Link
            to={`/timeline?investigation_id=${investigation.investigation_id}`}
            className="p-4 bg-surface hover:bg-surface-elevated border border-border rounded-lg transition-colors group flex items-start gap-3"
          >
            <Clock className="w-5 h-5 text-cyan-400 mt-0.5 group-hover:scale-105 transition-transform" />
            <div>
              <div className="text-xs font-semibold text-foreground group-hover:text-accent-light">
                Forensic Timeline
              </div>
              <p className="text-2xs text-foreground-muted mt-0.5">
                Chronological sequence with observed vs inferred provenance.
              </p>
            </div>
          </Link>

          <Link
            to={`/attack-chain?investigation_id=${investigation.investigation_id}`}
            className="p-4 bg-surface hover:bg-surface-elevated border border-border rounded-lg transition-colors group flex items-start gap-3"
          >
            <GitMerge className="w-5 h-5 text-rose-400 mt-0.5 group-hover:scale-105 transition-transform" />
            <div>
              <div className="text-xs font-semibold text-foreground group-hover:text-accent-light">
                Attack Chain & MITRE
              </div>
              <p className="text-2xs text-foreground-muted mt-0.5">
                Reconstructed social engineering progression mapped to ATT&CK.
              </p>
            </div>
          </Link>

          <Link
            to={`/reports?investigation_id=${investigation.investigation_id}`}
            className="p-4 bg-surface hover:bg-surface-elevated border border-border rounded-lg transition-colors group flex items-start gap-3"
          >
            <FileText className="w-5 h-5 text-emerald-400 mt-0.5 group-hover:scale-105 transition-transform" />
            <div>
              <div className="text-xs font-semibold text-foreground group-hover:text-accent-light">
                Investigation Reports
              </div>
              <p className="text-2xs text-foreground-muted mt-0.5">
                Export forensic deliverables in JSON, HTML, or Markdown.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};
