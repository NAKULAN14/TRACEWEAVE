import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Target,
  RefreshCw,
  Search,
  ExternalLink,
  Shield,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { InvestigationResultResponse } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

interface MatrixTechnique {
  id: string;
  name: string;
  tactic: string;
  description: string;
  appliesTo: string;
}

const RELEVANT_MITRE_TECHNIQUES: MatrixTechnique[] = [
  {
    id: 'T1566.002',
    name: 'Spearphishing Link',
    tactic: 'Initial Access',
    description: 'Adversary sends targeted spearphishing links directing victims to malicious web destinations.',
    appliesTo: 'Decoded QR URLs & embedded hyperlinks in ICS files',
  },
  {
    id: 'T1566.001',
    name: 'Spearphishing Attachment',
    tactic: 'Initial Access',
    description: 'Adversary sends emails with malicious attachments disguised as legitimate files.',
    appliesTo: 'ICS meeting files (.ics) or image attachments (.png/.jpg)',
  },
  {
    id: 'T1204.001',
    name: 'User Execution: Malicious Link',
    tactic: 'Execution',
    description: 'Victim interacts with the link by scanning the QR code with mobile camera or browser.',
    appliesTo: 'Physical scanning transduction boundary',
  },
  {
    id: 'T1071.001',
    name: 'Web Protocols',
    tactic: 'Command & Control',
    description: 'Adversary communicates using HTTP/HTTPS to host phishing portals or harvest input.',
    appliesTo: 'Adversary landing infrastructure and TLS domains',
  },
  {
    id: 'T1584.001',
    name: 'Compromise Infrastructure: Domains',
    tactic: 'Resource Development',
    description: 'Adversary acquires or compromises legitimate domains to evade standard reputation filters.',
    appliesTo: 'Newly registered or typosquatted domain IOCs',
  },
];

export const MitreMappingPage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [result, setResult] = useState<InvestigationResultResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const loadMitre = useCallback(async () => {
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
      setError(err instanceof Error ? err.message : 'Failed to query MITRE mappings');
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
    loadMitre();
  }, [loadMitre]);

  const filteredTechniques = RELEVANT_MITRE_TECHNIQUES.filter(
    (t) =>
      t.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.tactic.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Target className="w-5 h-5 text-accent-light" />
            MITRE ATT&CK FRAMEWORK MAPPING
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Grounded adversary technique attribution based strictly on corroborated forensic evidence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadMitre()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh MITRE mapping"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Scoper & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-surface border border-border p-3 rounded-lg">
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

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-subtle" />
          <input
            type="text"
            placeholder="Search ATT&CK ID or tactic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
          />
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <LoadingSpinner label="Querying MITRE ATT&CK technique mappings..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={Target}
          title="No Investigation Selected"
          description="Select an investigation run to evaluate MITRE ATT&CK mappings."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {result?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="MITRE ATT&CK Technique Mapping Not Available"
              message={result.message}
              pipelineStage="MITRE_MAPPING (Stage 13)"
              investigationId={effectiveInvId}
            />
          )}

          {/* Academic Attribution Integrity Card */}
          <div className="p-4 rounded-lg bg-surface border border-border font-mono text-xs space-y-2">
            <div className="flex items-center gap-2 text-foreground font-semibold">
              <Shield className="w-4 h-4 text-accent-light" />
              <span>Evidence-Supported Attribution Rule</span>
            </div>
            <p className="text-2xs text-foreground-muted leading-relaxed font-sans">
              TRACEWEAVE requires verified provenance before assigning ATT&CK techniques.
              An attack technique is never claimed merely because an artifact is present;
              corroborating forensic evidence (such as decoded QR payload URI, calendar organizer spoofing,
              or confirmed TLS redirection) must validate the behavior.
            </p>
          </div>

          {/* Technique Reference Table */}
          <div className="bg-surface border border-border rounded-lg overflow-hidden">
            <div className="px-5 py-3 border-b border-border bg-surface-subtle flex items-center justify-between">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground font-mono">
                Relevant Enterprise ATT&CK Matrix Techniques
              </h3>
              <span className="text-2xs font-mono text-foreground-subtle">
                v15.1 Evaluation Matrix
              </span>
            </div>

            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-border bg-surface-subtle/50 text-2xs uppercase tracking-wider text-foreground-subtle">
                  <th className="px-5 py-2.5">Technique ID</th>
                  <th className="px-5 py-2.5">Technique Name</th>
                  <th className="px-5 py-2.5">Tactic</th>
                  <th className="px-5 py-2.5">Investigative Applicability</th>
                  <th className="px-5 py-2.5">Attribution Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredTechniques.map((item) => (
                  <tr key={item.id} className="hover:bg-surface-elevated/60 transition-colors">
                    <td className="px-5 py-3 font-bold text-accent-light whitespace-nowrap">
                      <a
                        href={`https://attack.mitre.org/techniques/${item.id.replace('.', '/')}/`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 hover:underline"
                      >
                        <span>{item.id}</span>
                        <ExternalLink className="w-3 h-3 text-foreground-subtle" />
                      </a>
                    </td>
                    <td className="px-5 py-3 text-foreground font-medium">
                      {item.name}
                    </td>
                    <td className="px-5 py-3 text-foreground-muted whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded bg-surface-subtle border border-border text-2xs">
                        {item.tactic}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-foreground-muted font-sans text-xs">
                      {item.appliesTo}
                    </td>
                    <td className="px-5 py-3 whitespace-nowrap">
                      <StatusBadge status="NOT_AVAILABLE" size="sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
