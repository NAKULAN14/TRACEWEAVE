import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Modal } from '../ui/Modal';
import { api } from '../../api/client';
import { useInvestigation } from '../../context/InvestigationContext';

export const AppLayout: React.FC = () => {
  const [isCreateCaseOpen, setIsCreateCaseOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const { refreshCases, setActiveCaseId } = useInvestigation();
  const navigate = useNavigate();

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    setCreateError(null);
    try {
      const newCase = await api.createCase({
        title: title.trim(),
        description: description.trim() || undefined,
      });
      await refreshCases();
      setActiveCaseId(newCase.case_id);
      setIsCreateCaseOpen(false);
      setTitle('');
      setDescription('');
      navigate(`/cases/${newCase.case_id}`);
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create case');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header onOpenCreateCase={() => setIsCreateCaseOpen(true)} />
        <main className="flex-1 overflow-y-auto p-6 bg-background/50">
          <Outlet />
        </main>
      </div>

      {/* Global Create Case Modal */}
      <Modal
        isOpen={isCreateCaseOpen}
        onClose={() => setIsCreateCaseOpen(false)}
        title="Intake New Forensic Case"
        description="Initialize an investigation docket in the TRACEWEAVE database."
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
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Incident 2026-QR-0842 Phishing Lure"
              className="w-full px-3 py-2 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-foreground-muted mb-1">
              Description / Investigative Scope
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Suspected QR code vector delivered via deceptive calendar invite or email attachment..."
              className="w-full px-3 py-2 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
            <button
              type="button"
              onClick={() => setIsCreateCaseOpen(false)}
              className="px-3 py-1.5 text-xs text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim()}
              className="px-3 py-1.5 text-xs font-medium text-white bg-accent hover:bg-accent-hover rounded transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Creating...' : 'Create Case'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
