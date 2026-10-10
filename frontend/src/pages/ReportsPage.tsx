import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileText,
  RefreshCw,
  Download,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { InvestigationReportResponse, ReportFormat } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

export const ReportsPage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [format, setFormat] = useState<ReportFormat>('json');
  const [reportData, setReportData] = useState<InvestigationReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReport = useCallback(async () => {
    if (!effectiveInvId) {
      setReportData(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getReport(effectiveInvId, format);
      setReportData(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query investigation report');
    } finally {
      setIsLoading(false);
    }
  }, [effectiveInvId, format]);

  useEffect(() => {
    if (effectiveInvId && effectiveInvId !== activeInvestigationId) {
      setActiveInvestigationId(effectiveInvId);
    }
  }, [effectiveInvId, activeInvestigationId, setActiveInvestigationId]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  const handleDownload = () => {
    if (!reportData || !reportData.report_content) return;
    const extension = format === 'json' ? 'json' : format === 'html' ? 'html' : 'md';
    const mime =
      format === 'json'
        ? 'application/json'
        : format === 'html'
        ? 'text/html'
        : 'text/markdown';

    const blob = new Blob([reportData.report_content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `traceweave-report-${effectiveInvId}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <FileText className="w-5 h-5 text-accent-light" />
            INVESTIGATION FORENSIC REPORTS
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Reconstruction deliverables formatted for digital forensics reporting and evidentiary presentation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {reportData?.report_content && (
            <button
              type="button"
              onClick={handleDownload}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Report</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => loadReport()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh report data"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Investigation Scoper & Format Selector */}
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

        {/* Format Switcher */}
        <div className="flex items-center bg-surface-subtle border border-border rounded p-0.5 text-2xs font-mono">
          <button
            type="button"
            onClick={() => setFormat('json')}
            className={`px-3 py-1 rounded transition-colors ${
              format === 'json' ? 'bg-surface-elevated text-accent-light font-bold' : 'text-foreground-muted hover:text-foreground'
            }`}
          >
            JSON
          </button>
          <button
            type="button"
            onClick={() => setFormat('html')}
            className={`px-3 py-1 rounded transition-colors ${
              format === 'html' ? 'bg-surface-elevated text-accent-light font-bold' : 'text-foreground-muted hover:text-foreground'
            }`}
          >
            HTML
          </button>
          <button
            type="button"
            onClick={() => setFormat('markdown')}
            className={`px-3 py-1 rounded transition-colors ${
              format === 'markdown' ? 'bg-surface-elevated text-accent-light font-bold' : 'text-foreground-muted hover:text-foreground'
            }`}
          >
            Markdown
          </button>
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <LoadingSpinner label={`Generating ${format.toUpperCase()} report deliverable...`} />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={FileText}
          title="No Investigation Selected"
          description="Select an investigation to inspect generated report artifacts."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {reportData?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="Investigation Report Generation Inactive"
              message={reportData.message}
              pipelineStage="REPORT_GENERATION"
              investigationId={effectiveInvId}
            />
          )}

          {/* Report Viewer / Empty Presentation */}
          <div className="bg-surface border border-border rounded-lg overflow-hidden">
            <div className="px-5 py-3 border-b border-border bg-surface-subtle flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="text-foreground-subtle uppercase text-2xs">Format:</span>
                <span className="text-accent-light font-bold">{format.toUpperCase()}</span>
                <span className="text-foreground-subtle">•</span>
                <span className="text-foreground-subtle uppercase text-2xs">Status:</span>
                <StatusBadge status={reportData?.status || 'NOT_AVAILABLE'} size="sm" />
              </div>
              {reportData?.report_content && (
                <CopyButton value={reportData.report_content} label="Copy Content" />
              )}
            </div>

            {reportData?.report_content ? (
              <div className="p-5 overflow-x-auto">
                {format === 'json' ? (
                  <pre className="font-mono text-xs text-foreground bg-surface-subtle p-4 rounded border border-border overflow-x-auto">
                    {reportData.report_content}
                  </pre>
                ) : format === 'html' ? (
                  <div className="space-y-3">
                    <div className="text-2xs text-amber-400 font-mono bg-amber-950/40 border border-amber-800 p-2 rounded">
                      HTML is displayed with security escaping to avoid cross-site scripting vulnerabilities.
                    </div>
                    <pre className="font-mono text-xs text-foreground bg-surface-subtle p-4 rounded border border-border overflow-x-auto">
                      {reportData.report_content}
                    </pre>
                  </div>
                ) : (
                  <pre className="font-mono text-xs text-foreground bg-surface-subtle p-4 rounded border border-border overflow-x-auto whitespace-pre-wrap">
                    {reportData.report_content}
                  </pre>
                )}
              </div>
            ) : (
              <div className="p-12 text-center bg-surface">
                <FileText className="w-10 h-10 text-foreground-subtle mx-auto mb-3 opacity-60" />
                <h3 className="text-xs font-semibold text-foreground font-mono">
                  Report Content Unavailable
                </h3>
                <p className="text-2xs text-foreground-muted max-w-md mx-auto mt-1 leading-relaxed font-sans">
                  The backend report generation service returned <code className="text-accent-light font-mono">report_content: null</code>.
                  In accordance with TRACEWEAVE research integrity standards, no artificial findings are generated.
                </p>
                <div className="mt-4 inline-flex items-center gap-1.5 px-3 py-1 rounded bg-surface-subtle border border-border text-2xs font-mono text-foreground-subtle">
                  <span>Endpoint:</span>
                  <code className="text-accent-light">/api/investigations/{effectiveInvId}/report?report_format={format}</code>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
