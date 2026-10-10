import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Radio,
  RefreshCw,
  AlertTriangle,
  ShieldCheck,
  HelpCircle,
  AlertCircle,
  Database,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { InvestigationResultResponse } from '../types/api';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

export const ThreatIntelligencePage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [result, setResult] = useState<InvestigationResultResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadIntel = useCallback(async () => {
    if (!effectiveInvId) {
      setResult(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getInvestigationResult(effectiveInvId, 'iocs');
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query threat intelligence');
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
    loadIntel();
  }, [loadIntel]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Radio className="w-5 h-5 text-accent-light" />
            THREAT INTELLIGENCE ENRICHMENT
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            External reputation verdicts, domain categorization, and infrastructure telemetry enrichment.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadIntel()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh threat intelligence"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Investigation Scoping Toolbar */}
      <div className="flex items-center justify-between gap-3 bg-surface border border-border p-3 rounded-lg">
        <div className="flex items-center gap-2">
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

        <div className="text-2xs font-mono text-foreground-subtle">
          Pipeline Stage: THREAT_INTELLIGENCE (Stage 8)
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingSpinner label="Querying threat intelligence feeds..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={Radio}
          title="No Investigation Selected"
          description="Select an investigation to evaluate threat intelligence enrichment verdicts."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {/* Truthful Not Available Banner */}
          {result?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="Threat Intelligence Pipeline Output Not Available"
              message={result.message}
              pipelineStage="THREAT_INTELLIGENCE (Stage 8)"
              investigationId={effectiveInvId}
            />
          )}

          {/* Academic & DFIR Verdict Clarification Card */}
          <div className="bg-surface border border-border rounded-lg p-5 font-mono text-xs space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground flex items-center gap-2">
              <Database className="w-4 h-4 text-accent-light" />
              Forensic Verdict Taxonomy & Integrity Rules
            </h3>
            <p className="text-2xs text-foreground-muted leading-relaxed">
              TRACEWEAVE upholds forensic integrity in verdict reporting. To avoid confirmation bias:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-2xs pt-2">
              <div className="p-3 bg-surface-subtle border border-border rounded space-y-1">
                <div className="flex items-center gap-2 text-rose-400 font-bold">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>MALICIOUS</span>
                </div>
                <p className="text-foreground-muted">
                  Corroborated by high-confidence threat feeds, blocklists, or definitive malicious telemetry.
                </p>
              </div>

              <div className="p-3 bg-surface-subtle border border-border rounded space-y-1">
                <div className="flex items-center gap-2 text-amber-400 font-bold">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>NOT_FOUND ≠ BENIGN</span>
                </div>
                <p className="text-foreground-muted">
                  <strong>Critical Principle:</strong> Absence of threat feed flags indicates newly registered
                  infrastructure or evasion, NOT verified benign status.
                </p>
              </div>

              <div className="p-3 bg-surface-subtle border border-border rounded space-y-1">
                <div className="flex items-center gap-2 text-emerald-400 font-bold">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>BENIGN</span>
                </div>
                <p className="text-foreground-muted">
                  Only assigned when verified against trusted organizational or authoritative infrastructure.
                </p>
              </div>

              <div className="p-3 bg-surface-subtle border border-border rounded space-y-1">
                <div className="flex items-center gap-2 text-slate-400 font-bold">
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>UNKNOWN / NOT_AVAILABLE</span>
                </div>
                <p className="text-foreground-muted">
                  External feed unqueried, API keys unconfigured, or telemetry pending pipeline execution.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
