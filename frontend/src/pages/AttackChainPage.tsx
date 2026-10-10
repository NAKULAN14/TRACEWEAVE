import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  GitMerge,
  RefreshCw,
  Layers,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { InvestigationResultResponse } from '../types/api';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

export const AttackChainPage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [result, setResult] = useState<InvestigationResultResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadAttackChain = useCallback(async () => {
    if (!effectiveInvId) {
      setResult(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getInvestigationResult(effectiveInvId, 'attack-chain');
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query attack chain');
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
    loadAttackChain();
  }, [loadAttackChain]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <GitMerge className="w-5 h-5 text-accent-light" />
            ATTACK CHAIN RECONSTRUCTION
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Reconstructed progression of QR-mediated social engineering stages supported by physical forensic evidence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadAttackChain()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh attack chain"
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
          Pipeline Stage: ATTACK_CHAIN (Stage 12)
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingSpinner label="Loading reconstructed attack chain..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={GitMerge}
          title="No Investigation Selected"
          description="Select an investigation to display the reconstructed adversary progression."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {result?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="Attack Chain Analysis Not Available"
              message={result.message}
              pipelineStage="ATTACK_CHAIN (Stage 12)"
              investigationId={effectiveInvId}
            />
          )}

          {/* Research Attack Chain Model Explanation */}
          <div className="bg-surface border border-border rounded-lg p-5 font-mono text-xs space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground flex items-center gap-2">
              <Layers className="w-4 h-4 text-accent-light" />
              TRACEWEAVE Cross-Layer Reconstructed Attack Model
            </h3>
            <p className="text-2xs text-foreground-muted leading-relaxed">
              In QR-mediated phishing incidents, threat actors exploit cross-boundary deception.
              The attack chain is reconstructed through four core phases:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-2xs pt-1">
              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-accent-light font-bold block mb-1">1. Lure Delivery</span>
                <p className="text-foreground-muted">
                  Email message or ICS calendar invite designed to bypass email security gateways via structural evasion.
                </p>
              </div>

              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-amber-400 font-bold block mb-1">2. QR Transduction</span>
                <p className="text-foreground-muted">
                  Visual QR code embedded in body or attached image redirects victim from desktop environment to mobile device.
                </p>
              </div>

              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-rose-400 font-bold block mb-1">3. Credential Harvester</span>
                <p className="text-foreground-muted">
                  Deceptive landing page hosted on adversary-controlled domain harvesting OAuth tokens or enterprise credentials.
                </p>
              </div>

              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-purple-400 font-bold block mb-1">4. Post-Exploitation</span>
                <p className="text-foreground-muted">
                  Session token theft, unauthorized account delegation, or internal lateral phishing.
                </p>
              </div>
            </div>

            <div className="p-3 rounded bg-surface-subtle border border-border text-2xs text-foreground-subtle">
              <strong>Rigorous Mapping Rule:</strong> Stages are only confirmed in TRACEWEAVE when
              grounded by verified email artifacts, decoded QR bitstreams, or correlated network telemetry.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
