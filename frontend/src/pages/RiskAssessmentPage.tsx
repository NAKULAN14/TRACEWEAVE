import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Gauge,
  RefreshCw,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { RiskAssessmentResponse } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

export const RiskAssessmentPage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [riskData, setRiskData] = useState<RiskAssessmentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRisk = useCallback(async () => {
    if (!effectiveInvId) {
      setRiskData(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getRisk(effectiveInvId);
      setRiskData(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query risk assessment');
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
    loadRisk();
  }, [loadRisk]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Gauge className="w-5 h-5 text-accent-light" />
            INCIDENT RISK ASSESSMENT
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Quantified incident severity and composite risk score evaluated from multi-layer forensic signals.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadRisk()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh risk assessment"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Investigation Scoper */}
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
          Pipeline Stage: RISK_ASSESSMENT (Stage 14)
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <LoadingSpinner label="Querying risk assessment endpoint..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={Gauge}
          title="No Investigation Selected"
          description="Select an investigation to view calculated risk scores and contributing factors."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {riskData?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="Risk Assessment Model Not Available"
              message={riskData.message}
              pipelineStage="RISK_ASSESSMENT (Stage 14)"
              investigationId={effectiveInvId}
            />
          )}

          {/* Risk Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-surface border border-border rounded-lg p-5">
              <span className="text-foreground-subtle text-2xs uppercase tracking-wider font-mono block mb-1">
                Composite Risk Score
              </span>
              <div className="text-3xl font-bold font-mono text-foreground">
                {riskData?.risk_score !== null && riskData?.risk_score !== undefined
                  ? `${riskData.risk_score} / 100`
                  : '—'}
              </div>
              <div className="mt-2 text-2xs font-mono text-foreground-muted">
                {riskData?.risk_score !== null && riskData?.risk_score !== undefined
                  ? 'Computed from multi-factor telemetry'
                  : 'Evaluation pending pipeline execution'}
              </div>
            </div>

            <div className="bg-surface border border-border rounded-lg p-5">
              <span className="text-foreground-subtle text-2xs uppercase tracking-wider font-mono block mb-1">
                Assessed Severity Level
              </span>
              <div className="mt-1">
                {riskData?.overall_risk ? (
                  <StatusBadge status={riskData.overall_risk} type="priority" size="md" />
                ) : (
                  <span className="text-sm font-mono text-foreground-subtle">NOT EVALUATED</span>
                )}
              </div>
              <div className="mt-3 text-2xs font-mono text-foreground-muted">
                Categorized per incident severity matrix
              </div>
            </div>

            <div className="bg-surface border border-border rounded-lg p-5">
              <span className="text-foreground-subtle text-2xs uppercase tracking-wider font-mono block mb-1">
                Contributing Risk Factors
              </span>
              <div className="text-3xl font-bold font-mono text-foreground">
                {riskData?.factors?.length || 0}
              </div>
              <div className="mt-2 text-2xs font-mono text-foreground-muted">
                Active weighting parameters identified
              </div>
            </div>
          </div>

          {/* Contributing Factors Table / State */}
          <div className="bg-surface border border-border rounded-lg p-5 space-y-3 font-mono text-xs">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground">
              Evaluated Contributing Risk Factors
            </h3>

            {riskData?.factors && riskData.factors.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-border bg-surface-subtle text-2xs uppercase text-foreground-subtle">
                      <th className="px-4 py-2">Factor</th>
                      <th className="px-4 py-2">Severity</th>
                      <th className="px-4 py-2">Score Impact</th>
                      <th className="px-4 py-2">Rationale</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/60">
                    {riskData.factors.map((f, idx) => (
                      <tr key={idx} className="hover:bg-surface-elevated/60">
                        <td className="px-4 py-2.5 font-semibold text-foreground">{f.factor}</td>
                        <td className="px-4 py-2.5">
                          <StatusBadge status={f.severity || 'MEDIUM'} type="priority" size="sm" />
                        </td>
                        <td className="px-4 py-2.5 text-accent-light font-bold">
                          {f.score !== undefined ? `+${f.score}` : '—'}
                        </td>
                        <td className="px-4 py-2.5 text-foreground-muted font-sans text-xs">
                          {f.rationale || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center bg-surface-subtle border border-dashed border-border rounded">
                <p className="text-2xs text-foreground-muted">
                  No risk factors currently generated by backend. Score is not synthesized on the client.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
