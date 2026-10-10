import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Briefcase,
  FileArchive,
  Activity,
  ArrowLeft,
  Upload,
  Plus,
  RefreshCw,
  Edit2,
  Play,
  Clock,
  HardDrive,
  Hash,
} from 'lucide-react';
import { api } from '../api/client';
import { Case, Evidence, Investigation, CaseStatus } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatDate, formatBytes, truncateHash } from '../lib/utils';
import { useInvestigation } from '../context/InvestigationContext';

export const CaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const { setActiveCaseId, setActiveInvestigationId, refreshCases } = useInvestigation();

  const [currentCase, setCurrentCase] = useState<Case | null>(null);
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [investigationList, setInvestigationList] = useState<Investigation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'evidence' | 'investigations' | 'metadata'>('evidence');

  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Edit modal state
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editStatus, setEditStatus] = useState<CaseStatus>('OPEN');
  const [isUpdating, setIsUpdating] = useState(false);

  // Create investigation state
  const [isCreatingInv, setIsCreatingInv] = useState(false);

  const loadCaseData = useCallback(async () => {
    if (!caseId) return;
    setIsLoading(true);
    setError(null);
    try {
      const [caseData, evidData, invData] = await Promise.all([
        api.getCase(caseId),
        api.listEvidence(caseId).catch(() => []),
        api.listCaseInvestigations(caseId).catch(() => []),
      ]);
      setCurrentCase(caseData);
      setEvidenceList(evidData);
      setInvestigationList(invData);
      setActiveCaseId(caseId);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setIsLoading(false);
    }
  }, [caseId, setActiveCaseId]);

  useEffect(() => {
    loadCaseData();
  }, [loadCaseData]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !selectedFile) return;

    setIsUploading(true);
    setUploadError(null);
    try {
      await api.uploadEvidence(caseId, selectedFile);
      setSelectedFile(null);
      setIsUploadOpen(false);
      await loadCaseData();
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : 'Evidence upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateInvestigation = async () => {
    if (!caseId) return;
    setIsCreatingInv(true);
    try {
      const created = await api.createInvestigation(caseId);
      setActiveInvestigationId(created.investigation_id);
      await loadCaseData();
      setActiveTab('investigations');
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to create investigation');
    } finally {
      setIsCreatingInv(false);
    }
  };

  const handleStartInvestigation = async (invId: string) => {
    try {
      await api.startInvestigation(invId);
      await loadCaseData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to start investigation');
    }
  };

  const handleUpdateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId) return;
    setIsUpdating(true);
    try {
      const updated = await api.updateCase(caseId, {
        title: editTitle.trim() || undefined,
        description: editDesc.trim() || undefined,
        status: editStatus,
      });
      setCurrentCase(updated);
      await refreshCases();
      setIsEditOpen(false);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Update failed');
    } finally {
      setIsUpdating(false);
    }
  };

  const openEditModal = () => {
    if (!currentCase) return;
    setEditTitle(currentCase.title);
    setEditDesc(currentCase.description || '');
    setEditStatus(currentCase.status);
    setIsEditOpen(true);
  };

  if (isLoading) {
    return <LoadingSpinner label="Loading case docket..." />;
  }

  if (error || !currentCase) {
    return (
      <div className="space-y-4 max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/cases')}
          className="inline-flex items-center gap-1.5 text-xs text-foreground-muted hover:text-foreground font-mono"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Cases
        </button>
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error || 'Case not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-mono text-foreground-subtle">
          <Link to="/cases" className="hover:text-foreground flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Cases
          </Link>
          <span>/</span>
          <span className="text-foreground-muted">{currentCase.case_id}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={openEditModal}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs rounded bg-surface border border-border text-foreground hover:bg-surface-elevated transition-colors"
          >
            <Edit2 className="w-3.5 h-3.5" />
            <span>Edit Case</span>
          </button>
          <button
            type="button"
            onClick={() => loadCaseData()}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh case details"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Case Header Card */}
      <div className="bg-surface border border-border rounded-lg p-5">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-accent-light">
                {currentCase.case_id}
              </span>
              <CopyButton value={currentCase.case_id} />
              <StatusBadge status={currentCase.status} type="case" />
            </div>
            <h1 className="text-lg font-bold text-foreground tracking-tight">
              {currentCase.title}
            </h1>
            <p className="text-xs text-foreground-muted leading-relaxed max-w-3xl">
              {currentCase.description || 'No investigative description supplied.'}
            </p>
          </div>

          <div className="flex flex-col items-start md:items-end gap-1.5 text-2xs font-mono text-foreground-subtle border-t md:border-t-0 pt-3 md:pt-0 border-border">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              <span>Created: {formatDate(currentCase.created_at)}</span>
            </div>
            <div>Updated: {formatDate(currentCase.updated_at)}</div>
          </div>
        </div>

        {/* Quick Metrics Bar */}
        <div className="mt-5 pt-4 border-t border-border grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-foreground-subtle text-2xs block uppercase">Evidence Items</span>
            <span className="text-base font-bold text-foreground">{evidenceList.length}</span>
          </div>
          <div>
            <span className="text-foreground-subtle text-2xs block uppercase">Investigations</span>
            <span className="text-base font-bold text-foreground">{investigationList.length}</span>
          </div>
          <div>
            <span className="text-foreground-subtle text-2xs block uppercase">Running Stage</span>
            <span className="text-base font-bold text-amber-400">
              {investigationList.find((i) => i.status === 'RUNNING')?.current_stage || 'None'}
            </span>
          </div>
          <div>
            <span className="text-foreground-subtle text-2xs block uppercase">Case Health</span>
            <span className="text-base font-bold text-emerald-400">Active</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('evidence')}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeTab === 'evidence'
                ? 'border-accent text-accent-light font-semibold'
                : 'border-transparent text-foreground-muted hover:text-foreground'
            }`}
          >
            <FileArchive className="w-3.5 h-3.5" />
            <span>Evidence Artifacts ({evidenceList.length})</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('investigations')}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeTab === 'investigations'
                ? 'border-accent text-accent-light font-semibold'
                : 'border-transparent text-foreground-muted hover:text-foreground'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Investigations ({investigationList.length})</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('metadata')}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeTab === 'metadata'
                ? 'border-accent text-accent-light font-semibold'
                : 'border-transparent text-foreground-muted hover:text-foreground'
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            <span>Docket Metadata</span>
          </button>
        </div>

        {/* Tab specific actions */}
        <div>
          {activeTab === 'evidence' && (
            <button
              type="button"
              onClick={() => setIsUploadOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Upload Evidence</span>
            </button>
          )}
          {activeTab === 'investigations' && (
            <button
              type="button"
              onClick={handleCreateInvestigation}
              disabled={isCreatingInv}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors disabled:opacity-50"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{isCreatingInv ? 'Creating...' : 'New Investigation'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Tab 1: Evidence */}
      {activeTab === 'evidence' && (
        <div>
          {evidenceList.length === 0 ? (
            <EmptyState
              icon={FileArchive}
              title="No Evidence Attached to this Case"
              description="Ingest digital artifacts (such as email messages, ICS calendar files, or QR code images) to initiate forensic processing."
              action={
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(true)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload First Evidence File</span>
                </button>
              }
            />
          ) : (
            <div className="bg-surface border border-border rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-border bg-surface-subtle text-2xs uppercase tracking-wider text-foreground-subtle font-mono">
                    <th className="px-4 py-2.5">Evidence ID</th>
                    <th className="px-4 py-2.5">Original Filename</th>
                    <th className="px-4 py-2.5">MIME / Type</th>
                    <th className="px-4 py-2.5">File Size</th>
                    <th className="px-4 py-2.5">SHA-256 Hash</th>
                    <th className="px-4 py-2.5">Imported At</th>
                    <th className="px-4 py-2.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {evidenceList.map((ev) => (
                    <tr key={ev.evidence_id} className="hover:bg-surface-elevated/60 transition-colors">
                      <td className="px-4 py-3 font-mono font-medium text-accent-light whitespace-nowrap">
                        <div className="flex items-center gap-1">
                          <span>{ev.evidence_id}</span>
                          <CopyButton value={ev.evidence_id} />
                        </div>
                      </td>
                      <td className="px-4 py-3 font-medium text-foreground">
                        {ev.original_filename}
                      </td>
                      <td className="px-4 py-3 font-mono text-2xs text-foreground-muted">
                        {ev.mime_type || ev.extension || 'binary/octet-stream'}
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
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Investigations */}
      {activeTab === 'investigations' && (
        <div>
          {investigationList.length === 0 ? (
            <EmptyState
              icon={Activity}
              title="No Investigations Initialized"
              description="Create an investigation run for this case to trigger the TRACEWEAVE 15-stage reconstruction pipeline."
              action={
                <button
                  type="button"
                  onClick={handleCreateInvestigation}
                  disabled={isCreatingInv}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Initialize Investigation</span>
                </button>
              }
            />
          ) : (
            <div className="bg-surface border border-border rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-border bg-surface-subtle text-2xs uppercase tracking-wider text-foreground-subtle font-mono">
                    <th className="px-4 py-2.5">Investigation ID</th>
                    <th className="px-4 py-2.5">Status</th>
                    <th className="px-4 py-2.5">Current Stage</th>
                    <th className="px-4 py-2.5">Created</th>
                    <th className="px-4 py-2.5">Started</th>
                    <th className="px-4 py-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {investigationList.map((inv) => (
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
                      <td className="px-4 py-3 font-mono text-2xs text-amber-300">
                        {inv.current_stage || '—'}
                      </td>
                      <td className="px-4 py-3 font-mono text-2xs text-foreground-muted whitespace-nowrap">
                        {formatDate(inv.created_at)}
                      </td>
                      <td className="px-4 py-3 font-mono text-2xs text-foreground-subtle whitespace-nowrap">
                        {formatDate(inv.started_at)}
                      </td>
                      <td className="px-4 py-3 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          {inv.status === 'PENDING' && (
                            <button
                              type="button"
                              onClick={() => handleStartInvestigation(inv.investigation_id)}
                              className="inline-flex items-center gap-1 px-2.5 py-1 text-2xs font-medium rounded bg-emerald-950 border border-emerald-700 text-emerald-300 hover:bg-emerald-900 transition-colors"
                            >
                              <Play className="w-3 h-3" />
                              <span>Start Run</span>
                            </button>
                          )}
                          <button
                            type="button"
                            onClick={() => {
                              setActiveInvestigationId(inv.investigation_id);
                              navigate(`/investigations/${inv.investigation_id}`);
                            }}
                            className="px-2.5 py-1 text-2xs font-medium rounded bg-surface-elevated hover:bg-surface-active text-foreground border border-border"
                          >
                            Inspect Run
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Metadata */}
      {activeTab === 'metadata' && (
        <div className="bg-surface border border-border rounded-lg p-5 space-y-4">
          <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-foreground">
            SQLite Database Record
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3 bg-surface-subtle border border-border rounded">
              <span className="text-foreground-subtle text-2xs block">case_id</span>
              <span className="text-accent-light font-bold">{currentCase.case_id}</span>
            </div>
            <div className="p-3 bg-surface-subtle border border-border rounded">
              <span className="text-foreground-subtle text-2xs block">status</span>
              <span className="text-foreground font-bold">{currentCase.status}</span>
            </div>
            <div className="p-3 bg-surface-subtle border border-border rounded">
              <span className="text-foreground-subtle text-2xs block">created_at</span>
              <span className="text-foreground">{currentCase.created_at}</span>
            </div>
            <div className="p-3 bg-surface-subtle border border-border rounded">
              <span className="text-foreground-subtle text-2xs block">updated_at</span>
              <span className="text-foreground">{currentCase.updated_at}</span>
            </div>
          </div>
        </div>
      )}

      {/* Upload Evidence Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        title={`Upload Evidence to ${currentCase.case_id}`}
        description="Attach digital artifacts. File will be ingested and stored in backend/storage/evidence/."
      >
        <form onSubmit={handleUpload} className="space-y-4">
          {uploadError && (
            <div className="p-3 text-xs bg-rose-950/80 border border-rose-800 text-rose-300 rounded font-mono">
              {uploadError}
            </div>
          )}

          <div
            className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-accent/60 transition-colors cursor-pointer bg-surface-subtle"
            onClick={() => document.getElementById('case-file-input')?.click()}
          >
            <input
              id="case-file-input"
              type="file"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setSelectedFile(e.target.files[0]);
                }
              }}
            />
            <HardDrive className="w-8 h-8 text-foreground-subtle mx-auto mb-2" />
            <p className="text-xs font-medium text-foreground">
              {selectedFile ? selectedFile.name : 'Click to select evidence file or drag and drop'}
            </p>
            <p className="text-2xs text-foreground-muted mt-1 font-mono">
              Accepts .eml, .ics, .png, .jpg, .qr, or any forensic artifact
            </p>
            {selectedFile && (
              <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-elevated border border-border text-2xs font-mono text-accent-light">
                <span>{selectedFile.name}</span>
                <span>({formatBytes(selectedFile.size)})</span>
              </div>
            )}
          </div>

          <div className="p-3 rounded bg-surface-subtle border border-border text-2xs text-foreground-muted font-mono space-y-1">
            <div className="flex items-center gap-1.5 text-foreground">
              <Hash className="w-3 h-3 text-accent-light" />
              <span>Forensic Ingestion Notice</span>
            </div>
            <p>
              The backend automatically computes cryptographic SHA-256 hashes, extracts MIME types,
              and writes an immutable record to the forensic evidence store.
            </p>
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
              {isUploading ? 'Ingesting...' : 'Upload & Hash'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        title="Edit Case Docket"
      >
        <form onSubmit={handleUpdateCase} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-foreground-muted mb-1">
              Title
            </label>
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground-muted mb-1">
              Status
            </label>
            <select
              value={editStatus}
              onChange={(e) => setEditStatus(e.target.value as CaseStatus)}
              className="w-full px-3 py-2 text-xs bg-surface-subtle border border-border rounded text-foreground font-mono focus:outline-none focus:border-accent"
            >
              <option value="OPEN">OPEN</option>
              <option value="UNDER_INVESTIGATION">UNDER_INVESTIGATION</option>
              <option value="RECONSTRUCTED">RECONSTRUCTED</option>
              <option value="CLOSED">CLOSED</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground-muted mb-1">
              Description
            </label>
            <textarea
              rows={3}
              value={editDesc}
              onChange={(e) => setEditDesc(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
            <button
              type="button"
              onClick={() => setIsEditOpen(false)}
              className="px-3 py-1.5 text-xs text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUpdating}
              className="px-3 py-1.5 text-xs font-medium text-white bg-accent hover:bg-accent-hover rounded"
            >
              {isUpdating ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
