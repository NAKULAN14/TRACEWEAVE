import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Search,
  Filter,
  Plus,
  RefreshCw,
  ExternalLink,
  Edit2,
  FileArchive,
  Activity,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatDate } from '../lib/utils';
import { api } from '../api/client';
import { Case, CaseStatus } from '../types/api';

const STATUS_OPTIONS: { label: string; value: string }[] = [
  { label: 'All Statuses', value: 'ALL' },
  { label: 'Open', value: 'OPEN' },
  { label: 'Under Investigation', value: 'UNDER_INVESTIGATION' },
  { label: 'Reconstructed', value: 'RECONSTRUCTED' },
  { label: 'Closed', value: 'CLOSED' },
];

export const CasesPage: React.FC = () => {
  const { cases, isLoadingCases, refreshCases, setActiveCaseId } = useInvestigation();
  const navigate = useNavigate();

  // Search and Filter
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Intake Modal
  const [isIntakeOpen, setIsIntakeOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Edit Modal
  const [editingCase, setEditingCase] = useState<Case | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editStatus, setEditStatus] = useState<CaseStatus>('OPEN');
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setIsCreating(true);
    setCreateError(null);
    try {
      const created = await api.createCase({
        title: newTitle.trim(),
        description: newDesc.trim() || undefined,
      });
      await refreshCases();
      setActiveCaseId(created.case_id);
      setIsIntakeOpen(false);
      setNewTitle('');
      setNewDesc('');
      navigate(`/cases/${created.case_id}`);
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : 'Case creation failed');
    } finally {
      setIsCreating(false);
    }
  };

  const handleOpenEdit = (c: Case) => {
    setEditingCase(c);
    setEditTitle(c.title);
    setEditDesc(c.description || '');
    setEditStatus(c.status);
    setUpdateError(null);
  };

  const handleUpdateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingCase) return;

    setIsUpdating(true);
    setUpdateError(null);
    try {
      await api.updateCase(editingCase.case_id, {
        title: editTitle.trim() || undefined,
        description: editDesc.trim() || undefined,
        status: editStatus,
      });
      await refreshCases();
      setEditingCase(null);
    } catch (err: unknown) {
      setUpdateError(err instanceof Error ? err.message : 'Case update failed');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-accent-light" />
            CASE REPOSITORY
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Forensic case dockets managed under TRACEWEAVE investigation lifecycle.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsIntakeOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Case</span>
          </button>
          <button
            type="button"
            onClick={() => refreshCases()}
            disabled={isLoadingCases}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh case list"
          >
            <RefreshCw className={`w-4 h-4 ${isLoadingCases ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-surface border border-border p-3 rounded-lg">
        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-subtle" />
          <input
            type="text"
            placeholder="Search by title, ID, description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-foreground-subtle" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground font-mono focus:outline-none cursor-pointer"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <span className="text-2xs font-mono text-foreground-subtle whitespace-nowrap">
            Showing {filteredCases.length} of {cases.length}
          </span>
        </div>
      </div>

      {/* Case Table / Empty State */}
      {isLoadingCases ? (
        <LoadingSpinner label="Loading case registry..." />
      ) : filteredCases.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title={searchQuery || statusFilter !== 'ALL' ? 'No Matching Cases' : 'No Cases Found'}
          description={
            searchQuery || statusFilter !== 'ALL'
              ? 'No cases match your filter criteria. Try resetting the search or filter.'
              : 'The repository currently has no cases. Click "New Case" to initialize an incident docket.'
          }
          action={
            searchQuery || statusFilter !== 'ALL' ? (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  setStatusFilter('ALL');
                }}
                className="px-3 py-1.5 text-xs rounded bg-surface-elevated border border-border text-foreground hover:bg-surface-active"
              >
                Reset Filters
              </button>
            ) : (
              <button
                type="button"
                onClick={() => setIsIntakeOpen(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-accent text-white hover:bg-accent-hover"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Create First Case</span>
              </button>
            )
          }
        />
      ) : (
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-border bg-surface-subtle text-2xs uppercase tracking-wider text-foreground-subtle font-mono">
                  <th className="px-4 py-2.5">Case ID</th>
                  <th className="px-4 py-2.5">Title & Scope</th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5">Created</th>
                  <th className="px-4 py-2.5">Last Updated</th>
                  <th className="px-4 py-2.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredCases.map((c) => (
                  <tr
                    key={c.case_id}
                    onClick={() => {
                      setActiveCaseId(c.case_id);
                      navigate(`/cases/${c.case_id}`);
                    }}
                    className="hover:bg-surface-elevated/60 transition-colors cursor-pointer group"
                  >
                    <td className="px-4 py-3 font-mono font-medium text-accent-light whitespace-nowrap">
                      <div className="flex items-center gap-1">
                        <span>{c.case_id}</span>
                        <CopyButton value={c.case_id} />
                      </div>
                    </td>
                    <td className="px-4 py-3 max-w-sm">
                      <div className="font-medium text-foreground group-hover:text-accent-light transition-colors">
                        {c.title}
                      </div>
                      {c.description && (
                        <div className="text-2xs text-foreground-muted line-clamp-1 mt-0.5">
                          {c.description}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <StatusBadge status={c.status} type="case" size="sm" />
                    </td>
                    <td className="px-4 py-3 text-foreground-muted font-mono text-2xs whitespace-nowrap">
                      {formatDate(c.created_at)}
                    </td>
                    <td className="px-4 py-3 text-foreground-subtle font-mono text-2xs whitespace-nowrap">
                      {formatDate(c.updated_at)}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          type="button"
                          onClick={() => {
                            setActiveCaseId(c.case_id);
                            navigate(`/evidence?case_id=${c.case_id}`);
                          }}
                          title="View evidence for this case"
                          className="p-1 text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
                        >
                          <FileArchive className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setActiveCaseId(c.case_id);
                            navigate(`/investigations?case_id=${c.case_id}`);
                          }}
                          title="View investigations for this case"
                          className="p-1 text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
                        >
                          <Activity className="w-3.5 h-3.5 text-amber-400" />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleOpenEdit(c)}
                          title="Edit case metadata & status"
                          className="p-1 text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setActiveCaseId(c.case_id);
                            navigate(`/cases/${c.case_id}`);
                          }}
                          title="Open detailed case view"
                          className="p-1 text-accent-light hover:bg-accent/20 rounded border border-accent/40"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* New Case Modal */}
      <Modal
        isOpen={isIntakeOpen}
        onClose={() => setIsIntakeOpen(false)}
        title="Intake New Forensic Case"
        description="Create a case docket in the SQLite forensic repository."
      >
        <form onSubmit={handleCreateCase} className="space-y-4">
          {createError && (
            <div className="p-3 text-xs bg-rose-950/80 border border-rose-800 text-rose-300 rounded font-mono">
              {createError}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-foreground-muted mb-1">
              Case Title <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g., Campaign 2026-QR Phish - Marketing Exec"
              className="w-full px-3 py-2 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground-muted mb-1">
              Investigative Scope / Description
            </label>
            <textarea
              rows={3}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Suspected QR lure delivered via deceptive ICS meeting request..."
              className="w-full px-3 py-2 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
            <button
              type="button"
              onClick={() => setIsIntakeOpen(false)}
              className="px-3 py-1.5 text-xs text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isCreating || !newTitle.trim()}
              className="px-3 py-1.5 text-xs font-medium text-white bg-accent hover:bg-accent-hover rounded transition-colors disabled:opacity-50"
            >
              {isCreating ? 'Saving...' : 'Create Case'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Case Modal */}
      {editingCase && (
        <Modal
          isOpen={!!editingCase}
          onClose={() => setEditingCase(null)}
          title={`Edit Case: ${editingCase.case_id}`}
          description="Update case status and descriptive metadata."
        >
          <form onSubmit={handleUpdateCase} className="space-y-4">
            {updateError && (
              <div className="p-3 text-xs bg-rose-950/80 border border-rose-800 text-rose-300 rounded font-mono">
                {updateError}
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-foreground-muted mb-1">
                Case Title
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
                Investigation Status
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
                Description / Scope
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
                onClick={() => setEditingCase(null)}
                className="px-3 py-1.5 text-xs text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isUpdating}
                className="px-3 py-1.5 text-xs font-medium text-white bg-accent hover:bg-accent-hover rounded transition-colors disabled:opacity-50"
              >
                {isUpdating ? 'Updating...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
