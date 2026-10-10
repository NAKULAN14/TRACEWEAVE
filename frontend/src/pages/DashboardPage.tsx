import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Activity,
  FileArchive,
  Layers,
  ArrowRight,
  Plus,
  RefreshCw,
  FolderGit2,
  FileText,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { StatusBadge } from '../components/ui/StatusBadge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { formatDate } from '../lib/utils';
import { api } from '../api/client';
import { Investigation } from '../types/api';

export const DashboardPage: React.FC = () => {
  const { cases, isLoadingCases, refreshCases, setActiveCaseId } = useInvestigation();
  const [allInvestigations, setAllInvestigations] = useState<Investigation[]>([]);
  const [isLoadingInv, setIsLoadingInv] = useState(false);
  const navigate = useNavigate();

  // Load all investigations across cases to compute accurate global counts
  useEffect(() => {
    let isMounted = true;
    const fetchAllInv = async () => {
      if (cases.length === 0) {
        setAllInvestigations([]);
        return;
      }
      setIsLoadingInv(true);
      try {
        const invPromises = cases.map((c) => api.listCaseInvestigations(c.case_id).catch(() => []));
        const results = await Promise.all(invPromises);
        if (isMounted) {
          setAllInvestigations(results.flat());
        }
      } catch {
        // Fallback
      } finally {
        if (isMounted) setIsLoadingInv(false);
      }
    };
    fetchAllInv();
    return () => {
      isMounted = false;
    };
  }, [cases]);

  // Case counts by status
  const caseCounts = {
    total: cases.length,
    open: cases.filter((c) => c.status === 'OPEN').length,
    underInvestigation: cases.filter((c) => c.status === 'UNDER_INVESTIGATION').length,
    reconstructed: cases.filter((c) => c.status === 'RECONSTRUCTED').length,
    closed: cases.filter((c) => c.status === 'CLOSED').length,
  };

  // Investigation counts
  const invCounts = {
    total: allInvestigations.length,
    pending: allInvestigations.filter((i) => i.status === 'PENDING').length,
    running: allInvestigations.filter((i) => i.status === 'RUNNING').length,
    completed: allInvestigations.filter((i) => i.status === 'COMPLETED').length,
    failed: allInvestigations.filter((i) => i.status === 'FAILED').length,
  };

  const handleOpenCase = (caseId: string) => {
    setActiveCaseId(caseId);
    navigate(`/cases/${caseId}`);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Title & Context Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono">
            OPERATIONAL OVERVIEW
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Forensic intake, reconstruction pipeline health, and active incident telemetry.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/cases"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Manage Cases</span>
          </Link>
          <button
            type="button"
            onClick={() => refreshCases()}
            disabled={isLoadingCases}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh overview metrics"
          >
            <RefreshCw className={`w-4 h-4 ${isLoadingCases ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {isLoadingCases ? (
        <LoadingSpinner label="Querying case telemetry from database..." />
      ) : cases.length === 0 ? (
        <EmptyState
          icon={FolderGit2}
          title="No Forensic Cases Registered"
          description="The TRACEWEAVE database currently contains no cases. Create an initial case docket to begin evidence intake and forensic reconstruction."
          action={
            <Link
              to="/cases"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create First Case</span>
            </Link>
          }
        />
      ) : (
        <>
          {/* Key Metric Blocks */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Cases */}
            <div className="bg-surface border border-border rounded-lg p-4">
              <div className="flex items-center justify-between text-foreground-subtle mb-2">
                <span className="text-2xs font-mono uppercase tracking-wider">Active Cases</span>
                <Briefcase className="w-4 h-4 text-sky-400" />
              </div>
              <div className="text-2xl font-bold font-mono text-foreground">{caseCounts.total}</div>
              <div className="mt-2 text-2xs font-mono text-foreground-muted flex items-center gap-2">
                <span className="text-sky-400">{caseCounts.open} Open</span>
                <span>•</span>
                <span className="text-amber-400">{caseCounts.underInvestigation} In Progress</span>
              </div>
            </div>

            {/* Investigations */}
            <div className="bg-surface border border-border rounded-lg p-4">
              <div className="flex items-center justify-between text-foreground-subtle mb-2">
                <span className="text-2xs font-mono uppercase tracking-wider">Investigations</span>
                <Activity className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-bold font-mono text-foreground">
                {isLoadingInv ? '...' : invCounts.total}
              </div>
              <div className="mt-2 text-2xs font-mono text-foreground-muted flex items-center gap-2">
                <span className="text-amber-400">{invCounts.running} Running</span>
                <span>•</span>
                <span className="text-slate-400">{invCounts.pending} Pending</span>
                <span>•</span>
                <span className="text-emerald-400">{invCounts.completed} Done</span>
              </div>
            </div>

            {/* Reconstruction Status */}
            <div className="bg-surface border border-border rounded-lg p-4">
              <div className="flex items-center justify-between text-foreground-subtle mb-2">
                <span className="text-2xs font-mono uppercase tracking-wider">Reconstructed</span>
                <Layers className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold font-mono text-foreground">
                {caseCounts.reconstructed}
              </div>
              <div className="mt-2 text-2xs font-mono text-foreground-muted">
                {caseCounts.closed} Closed cases archived
              </div>
            </div>

            {/* Pipeline Engines */}
            <div className="bg-surface border border-border rounded-lg p-4">
              <div className="flex items-center justify-between text-foreground-subtle mb-2">
                <span className="text-2xs font-mono uppercase tracking-wider">Pipeline Engine</span>
                <FileArchive className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-bold font-mono text-foreground">15 Stages</div>
              <div className="mt-2 text-2xs font-mono text-foreground-muted">
                Intake → QR Decode → ATT&CK
              </div>
            </div>
          </div>

          {/* Quick Investigation Workflows & Guidance */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/evidence"
              className="bg-surface-subtle hover:bg-surface border border-border hover:border-accent/40 rounded-lg p-4 transition-colors group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <FileArchive className="w-4 h-4 text-accent-light" />
                  Evidence Ingestion
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-foreground-subtle group-hover:text-accent-light group-hover:translate-x-0.5 transition-all" />
              </div>
              <p className="text-2xs text-foreground-muted leading-relaxed">
                Upload `.eml`, `.ics`, or QR image artifacts. Computes SHA-256 hashes and imports for analysis.
              </p>
            </Link>

            <Link
              to="/investigations"
              className="bg-surface-subtle hover:bg-surface border border-border hover:border-accent/40 rounded-lg p-4 transition-colors group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <Activity className="w-4 h-4 text-amber-400" />
                  Investigation Stages
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-foreground-subtle group-hover:text-accent-light group-hover:translate-x-0.5 transition-all" />
              </div>
              <p className="text-2xs text-foreground-muted leading-relaxed">
                Monitor 15 sequential pipeline stages from attachment extraction through MITRE mapping.
              </p>
            </Link>

            <Link
              to="/reports"
              className="bg-surface-subtle hover:bg-surface border border-border hover:border-accent/40 rounded-lg p-4 transition-colors group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  Investigation Reports
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-foreground-subtle group-hover:text-accent-light group-hover:translate-x-0.5 transition-all" />
              </div>
              <p className="text-2xs text-foreground-muted leading-relaxed">
                Export verified forensic reconstruction deliverables in JSON, HTML, or Markdown formats.
              </p>
            </Link>
          </div>

          {/* Recent Cases Table */}
          <div className="bg-surface border border-border rounded-lg overflow-hidden">
            <div className="px-5 py-3 border-b border-border bg-surface-subtle flex items-center justify-between">
              <div>
                <h2 className="text-xs font-semibold uppercase tracking-wider text-foreground font-mono">
                  Recent Case Dockets
                </h2>
                <p className="text-2xs text-foreground-muted">
                  Cases persisted in SQLite repository
                </p>
              </div>
              <Link
                to="/cases"
                className="text-xs text-accent-light hover:underline font-mono inline-flex items-center gap-1"
              >
                View all cases ({cases.length}) <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-border bg-surface-subtle/50 text-2xs uppercase tracking-wider text-foreground-subtle font-mono">
                    <th className="px-5 py-2.5">Case ID</th>
                    <th className="px-5 py-2.5">Title</th>
                    <th className="px-5 py-2.5">Status</th>
                    <th className="px-5 py-2.5">Created At</th>
                    <th className="px-5 py-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {cases.slice(0, 5).map((c) => (
                    <tr
                      key={c.case_id}
                      onClick={() => handleOpenCase(c.case_id)}
                      className="hover:bg-surface-elevated/60 transition-colors cursor-pointer"
                    >
                      <td className="px-5 py-3 font-mono font-medium text-accent-light">
                        {c.case_id}
                      </td>
                      <td className="px-5 py-3 text-foreground font-medium max-w-xs truncate">
                        {c.title}
                        {c.description && (
                          <div className="text-2xs text-foreground-muted truncate">
                            {c.description}
                          </div>
                        )}
                      </td>
                      <td className="px-5 py-3">
                        <StatusBadge status={c.status} type="case" size="sm" />
                      </td>
                      <td className="px-5 py-3 text-foreground-muted font-mono text-2xs">
                        {formatDate(c.created_at)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenCase(c.case_id);
                          }}
                          className="px-2.5 py-1 text-2xs font-medium rounded bg-surface-elevated hover:bg-surface-active text-foreground border border-border"
                        >
                          Open Docket
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
