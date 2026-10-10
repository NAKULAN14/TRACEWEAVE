import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  RefreshCw,
  Globe,
  Radio,
  Mail,
  Hash,
  Link2,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { InvestigationResultResponse, IocItem } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

export const IocAnalysisPage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [result, setResult] = useState<InvestigationResultResponse<IocItem[]> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const loadIocs = useCallback(async () => {
    if (!effectiveInvId) {
      setResult(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getInvestigationResult<IocItem[]>(effectiveInvId, 'iocs');
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query IOC analysis');
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
    loadIocs();
  }, [loadIocs]);

  const iocList = Array.isArray(result?.data) ? result.data : [];

  const filteredIocs = iocList.filter((item) => {
    const matchesType = typeFilter === 'ALL' || item.type === typeFilter;
    const matchesSearch =
      item.value.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.source && item.source.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-accent-light" />
            INDICATORS OF COMPROMISE (IOCs)
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Normalized digital artifacts extracted from email headers, ICS attachments, and decoded QR codes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadIocs()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh IOC results"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Investigation Scoping Toolbar */}
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
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-subtle" />
            <input
              type="text"
              placeholder="Search indicators..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
            />
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground font-mono focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Types</option>
            <option value="URL">URLs</option>
            <option value="DOMAIN">Domains</option>
            <option value="IP">IP Addresses</option>
            <option value="EMAIL">Email Addresses</option>
            <option value="HASH">Hashes</option>
          </select>
        </div>
      </div>

      {/* Content Rendering */}
      {isLoading ? (
        <LoadingSpinner label="Querying IOC analysis endpoint..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={ShieldAlert}
          title="No Investigation Selected"
          description="Select an active investigation from the selector above to query IOC analysis results."
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
              title="Forensic IOC Analysis Pipeline Inactive"
              message={result.message}
              pipelineStage="IOC_ANALYSIS (Stage 7)"
              investigationId={effectiveInvId}
            />
          )}

          {/* IOC Extraction Architecture Overview */}
          <div className="bg-surface border border-border rounded-lg p-4 text-xs font-mono">
            <div className="flex items-center justify-between pb-3 border-b border-border mb-3">
              <span className="text-foreground-subtle uppercase text-2xs tracking-wider">
                Forensic Classification Specifications
              </span>
              <span className="text-2xs text-accent-light">RFC-822 / URI / IP / QR Specifications</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-2xs">
              <div className="p-2.5 rounded bg-surface-subtle border border-border">
                <span className="text-accent-light flex items-center gap-1 font-semibold mb-1">
                  <Link2 className="w-3.5 h-3.5" /> URL Targets
                </span>
                <span className="text-foreground-muted">Extracted from decoded QR or email bodies</span>
              </div>
              <div className="p-2.5 rounded bg-surface-subtle border border-border">
                <span className="text-purple-400 flex items-center gap-1 font-semibold mb-1">
                  <Globe className="w-3.5 h-3.5" /> Domains
                </span>
                <span className="text-foreground-muted">FQDNs parsed from deceptive hyperlinks</span>
              </div>
              <div className="p-2.5 rounded bg-surface-subtle border border-border">
                <span className="text-cyan-400 flex items-center gap-1 font-semibold mb-1">
                  <Radio className="w-3.5 h-3.5" /> IP Addresses
                </span>
                <span className="text-foreground-muted">Resolved hosting and SMTP relay nodes</span>
              </div>
              <div className="p-2.5 rounded bg-surface-subtle border border-border">
                <span className="text-amber-400 flex items-center gap-1 font-semibold mb-1">
                  <Mail className="w-3.5 h-3.5" /> Sender Email
                </span>
                <span className="text-foreground-muted">Deceptive calendar organizers & From headers</span>
              </div>
              <div className="p-2.5 rounded bg-surface-subtle border border-border">
                <span className="text-emerald-400 flex items-center gap-1 font-semibold mb-1">
                  <Hash className="w-3.5 h-3.5" /> Cryptographic Hashes
                </span>
                <span className="text-foreground-muted">SHA-256 signatures of raw attachments</span>
              </div>
            </div>
          </div>

          {/* Results Table if populated */}
          {filteredIocs.length > 0 ? (
            <div className="bg-surface border border-border rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-border bg-surface-subtle text-2xs uppercase tracking-wider text-foreground-subtle font-mono">
                    <th className="px-4 py-2.5">Indicator Type</th>
                    <th className="px-4 py-2.5">Indicator Value</th>
                    <th className="px-4 py-2.5">Provenance</th>
                    <th className="px-4 py-2.5">Verdict</th>
                    <th className="px-4 py-2.5">Enrichment</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {filteredIocs.map((item, idx) => (
                    <tr key={idx} className="hover:bg-surface-elevated/60 transition-colors font-mono">
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className="px-1.5 py-0.5 rounded bg-surface-subtle text-accent-light border border-border text-2xs font-bold">
                          {item.type}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium text-foreground">
                        <div className="flex items-center gap-1">
                          <span className="break-all">{item.value}</span>
                          <CopyButton value={item.value} />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-foreground-muted text-2xs whitespace-nowrap">
                        {item.source || item.provenance || 'Observed Artifact'}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <StatusBadge status={item.verdict || 'NOT_AVAILABLE'} type="verdict" size="sm" />
                      </td>
                      <td className="px-4 py-3 text-2xs text-foreground-subtle whitespace-nowrap">
                        {item.enrichment_status || 'Unprocessed'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center bg-surface border border-dashed border-border rounded-lg">
              <ShieldAlert className="w-8 h-8 text-foreground-subtle mx-auto mb-2 opacity-60" />
              <h3 className="text-xs font-semibold text-foreground font-mono">
                No IOC Records Ingested
              </h3>
              <p className="text-2xs text-foreground-muted max-w-md mx-auto mt-1 leading-relaxed">
                When forensic engines run on uploaded .eml or .ics files, parsed indicators will appear here.
                Currently, the backend returned <code className="text-accent-light">status: "{result?.status || 'NOT_AVAILABLE'}"</code>.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
