import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileArchive,
  Upload,
  Search,
  RefreshCw,
  HardDrive,
  FileCheck,
  Eye,
  Info,
  ShieldAlert,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { Evidence } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatDate, formatBytes, truncateHash } from '../lib/utils';

export const EvidencePage: React.FC = () => {
  const { cases, activeCaseId, setActiveCaseId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const caseIdParam = searchParams.get('case_id');
  const effectiveCaseId = caseIdParam || activeCaseId || (cases.length > 0 ? cases[0].case_id : null);

  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search
  const [searchQuery, setSearchQuery] = useState('');

  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Inspection modal
  const [inspectingItem, setInspectingItem] = useState<Evidence | null>(null);

  const loadEvidence = useCallback(async () => {
    if (!effectiveCaseId) {
      setEvidenceList([]);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.listEvidence(effectiveCaseId);
      setEvidenceList(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve evidence');
      setEvidenceList([]);
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
    loadEvidence();
  }, [loadEvidence]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!effectiveCaseId || !selectedFile) return;

    setIsUploading(true);
    setUploadError(null);
    try {
      await api.uploadEvidence(effectiveCaseId, selectedFile);
      setSelectedFile(null);
      setIsUploadOpen(false);
      await loadEvidence();
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const filteredEvidence = evidenceList.filter((ev) => {
    const q = searchQuery.toLowerCase();
    return (
      ev.original_filename.toLowerCase().includes(q) ||
      ev.evidence_id.toLowerCase().includes(q) ||
      ev.sha256.toLowerCase().includes(q) ||
      (ev.mime_type && ev.mime_type.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <FileArchive className="w-5 h-5 text-accent-light" />
            EVIDENCE INTAKE & MANAGEMENT
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Forensic artifact repository scoped to case. Computes SHA-256 digests and maintains chain of custody.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {effectiveCaseId && (
            <button
              type="button"
              onClick={() => setIsUploadOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Upload Evidence</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => loadEvidence()}
            disabled={isLoading || !effectiveCaseId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh evidence list"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Case Scoping Selector & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-surface border border-border p-3 rounded-lg">
        <div className="flex items-center gap-2 w-full sm:w-auto">
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

        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-subtle" />
          <input
            type="text"
            placeholder="Search by filename, hash, MIME..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
          />
        </div>
      </div>

      {/* Forensic Chain of Custody Notice */}
      <div className="bg-surface-subtle border border-border rounded-lg p-3 text-2xs text-foreground-muted font-mono flex items-start gap-2.5">
        <Info className="w-4 h-4 text-accent-light flex-shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong>Chain of Custody Standard:</strong> Stored files are ingested into immutable storage
          and cataloged by SHA-256. Importing evidence establishes intake provenance but does not imply
          forensic analysis has concluded. Initiate an investigation run to process stages.
        </div>
      </div>

      {/* Evidence Table */}
      {isLoading ? (
        <LoadingSpinner label="Fetching evidence artifacts..." />
      ) : !effectiveCaseId ? (
        <EmptyState
          icon={FileArchive}
          title="No Case Selected"
          description="Select an active case from the dropdown above to inspect or upload forensic evidence."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : filteredEvidence.length === 0 ? (
        <EmptyState
          icon={HardDrive}
          title={searchQuery ? 'No Matching Evidence' : 'No Evidence Ingested Yet'}
          description={
            searchQuery
              ? 'No artifacts match your query. Try a different search term.'
              : `Case ${effectiveCaseId} has no attached evidence artifacts. Upload an email (.eml), calendar file (.ics), or QR image.`
          }
          action={
            <button
              type="button"
              onClick={() => setIsUploadOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Upload Evidence</span>
            </button>
          }
        />
      ) : (
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-border bg-surface-subtle text-2xs uppercase tracking-wider text-foreground-subtle font-mono">
                  <th className="px-4 py-2.5">Evidence ID</th>
                  <th className="px-4 py-2.5">Original Filename</th>
                  <th className="px-4 py-2.5">MIME / Extension</th>
                  <th className="px-4 py-2.5">Size</th>
                  <th className="px-4 py-2.5">SHA-256 Checksum</th>
                  <th className="px-4 py-2.5">Imported</th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredEvidence.map((ev) => (
                  <tr
                    key={ev.evidence_id}
                    className="hover:bg-surface-elevated/60 transition-colors cursor-pointer"
                    onClick={() => setInspectingItem(ev)}
                  >
                    <td className="px-4 py-3 font-mono font-medium text-accent-light whitespace-nowrap">
                      <div className="flex items-center gap-1">
                        <span>{ev.evidence_id}</span>
                        <CopyButton value={ev.evidence_id} />
                      </div>
                    </td>
                    <td className="px-4 py-3 font-medium text-foreground max-w-xs truncate">
                      {ev.original_filename}
                    </td>
                    <td className="px-4 py-3 font-mono text-2xs text-foreground-muted whitespace-nowrap">
                      {ev.mime_type || ev.extension || 'binary/stream'}
                    </td>
                    <td className="px-4 py-3 font-mono text-2xs text-foreground-muted whitespace-nowrap">
                      {formatBytes(ev.file_size)}
                    </td>
                    <td className="px-4 py-3 font-mono text-2xs text-foreground-muted whitespace-nowrap">
                      <div className="flex items-center gap-1" title={ev.sha256}>
                        <span>{truncateHash(ev.sha256)}</span>
                        <CopyButton value={ev.sha256} />
                      </div>
                    </td>
                    <td className="px-4 py-3 font-mono text-2xs text-foreground-subtle whitespace-nowrap">
                      {formatDate(ev.imported_at)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <StatusBadge status={ev.status} type="generic" size="sm" />
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        onClick={() => setInspectingItem(ev)}
                        className="p-1 text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
                        title="View artifact metadata"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Upload Evidence Modal */}
      {effectiveCaseId && (
        <Modal
          isOpen={isUploadOpen}
          onClose={() => setIsUploadOpen(false)}
          title={`Upload Evidence to ${effectiveCaseId}`}
          description="Select a digital artifact to submit to the TRACEWEAVE ingestion engine."
        >
          <form onSubmit={handleUpload} className="space-y-4">
            {uploadError && (
              <div className="p-3 text-xs bg-rose-950/80 border border-rose-800 text-rose-300 rounded font-mono">
                {uploadError}
              </div>
            )}

            <div
              className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent/60 transition-colors cursor-pointer bg-surface-subtle"
              onClick={() => document.getElementById('evidence-upload-input')?.click()}
            >
              <input
                id="evidence-upload-input"
                type="file"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSelectedFile(e.target.files[0]);
                  }
                }}
              />
              <FileCheck className="w-8 h-8 text-accent-light mx-auto mb-2 opacity-80" />
              <p className="text-xs font-medium text-foreground">
                {selectedFile ? selectedFile.name : 'Click to select or drag and drop artifact'}
              </p>
              <p className="text-2xs text-foreground-muted mt-1 font-mono">
                Supports .eml (Email), .ics (Calendar), .png/.jpg (QR code images), or raw artifacts
              </p>
              {selectedFile && (
                <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded bg-surface-elevated border border-border text-2xs font-mono text-accent-light">
                  <span>{selectedFile.name}</span>
                  <span>({formatBytes(selectedFile.size)})</span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
              <button
                type="button"
                onClick={() => setIsUploadOpen(false)}
                className="px-3 py-1.5 text-xs text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isUploading || !selectedFile}
                className="px-3 py-1.5 text-xs font-medium text-white bg-accent hover:bg-accent-hover rounded transition-colors disabled:opacity-50"
              >
                {isUploading ? 'Ingesting Artifact...' : 'Ingest & Hash'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Inspect Item Modal */}
      {inspectingItem && (
        <Modal
          isOpen={!!inspectingItem}
          onClose={() => setInspectingItem(null)}
          title={`Artifact Details: ${inspectingItem.original_filename}`}
          description={`Evidence ID: ${inspectingItem.evidence_id}`}
          maxWidth="lg"
        >
          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 bg-surface-subtle border border-border rounded">
              <span className="text-2xs text-foreground-subtle block uppercase">SHA-256 Checksum</span>
              <div className="flex items-center justify-between gap-2 mt-1">
                <span className="text-accent-light break-all select-all">{inspectingItem.sha256}</span>
                <CopyButton value={inspectingItem.sha256} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-2xs text-foreground-subtle block uppercase">File Size</span>
                <span className="text-foreground font-semibold">{formatBytes(inspectingItem.file_size)}</span>
                <span className="text-2xs text-foreground-subtle block">({inspectingItem.file_size} bytes)</span>
              </div>
              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-2xs text-foreground-subtle block uppercase">MIME Type</span>
                <span className="text-foreground">{inspectingItem.mime_type || 'Unknown'}</span>
              </div>
              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-2xs text-foreground-subtle block uppercase">Associated Case</span>
                <span className="text-foreground">{inspectingItem.case_id}</span>
              </div>
              <div className="p-3 bg-surface-subtle border border-border rounded">
                <span className="text-2xs text-foreground-subtle block uppercase">Imported At</span>
                <span className="text-foreground">{formatDate(inspectingItem.imported_at)}</span>
              </div>
            </div>

            <div className="p-3 bg-surface-subtle border border-border rounded">
              <span className="text-2xs text-foreground-subtle block uppercase">Intake Status</span>
              <div className="mt-1">
                <StatusBadge status={inspectingItem.status} size="sm" />
              </div>
            </div>

            <div className="p-3 rounded bg-surface border border-border text-2xs text-foreground-muted">
              <span className="text-foreground font-semibold flex items-center gap-1 mb-1">
                <ShieldAlert className="w-3.5 h-3.5 text-accent-light" /> Storage Provenance
              </span>
              Evidence item is archived under TRACEWEAVE storage with cryptographic integrity validation.
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
