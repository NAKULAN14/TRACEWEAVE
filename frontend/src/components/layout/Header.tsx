import React from 'react';
import { RefreshCw, Folder, Cpu, Plus, AlertCircle } from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { StatusBadge } from '../ui/StatusBadge';

interface HeaderProps {
  onOpenCreateCase?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenCreateCase }) => {
  const {
    cases,
    activeCaseId,
    activeCase,
    investigations,
    activeInvestigationId,
    activeInvestigation,
    setActiveCaseId,
    setActiveInvestigationId,
    refreshCases,
    refreshInvestigations,
    isLoadingCases,
    isLoadingInvestigations,
    backendHealthy,
  } = useInvestigation();

  const handleRefresh = async () => {
    await refreshCases();
    if (activeCaseId) {
      await refreshInvestigations();
    }
  };

  const isRefreshing = isLoadingCases || isLoadingInvestigations;

  return (
    <header className="h-14 bg-surface/90 border-b border-border px-5 flex items-center justify-between gap-4 z-20">
      {/* Investigation Context Controls */}
      <div className="flex items-center gap-3 overflow-x-auto py-1">
        {/* Case Selector */}
        <div className="flex items-center gap-1.5 bg-surface-subtle border border-border px-2.5 py-1 rounded text-xs">
          <Folder className="w-3.5 h-3.5 text-accent-light flex-shrink-0" />
          <span className="text-foreground-subtle text-2xs font-mono uppercase">Case:</span>
          {cases.length > 0 ? (
            <select
              value={activeCaseId || ''}
              onChange={(e) => setActiveCaseId(e.target.value)}
              className="bg-transparent text-foreground font-mono text-xs focus:outline-none cursor-pointer max-w-[200px] truncate"
            >
              {cases.map((c) => (
                <option key={c.case_id} value={c.case_id} className="bg-surface text-foreground font-mono">
                  {c.case_id} — {c.title}
                </option>
              ))}
            </select>
          ) : (
            <span className="text-foreground-muted text-xs italic">No cases</span>
          )}
          {activeCase && (
            <StatusBadge status={activeCase.status} type="case" size="sm" className="ml-1" />
          )}
        </div>

        {/* Investigation Selector */}
        <div className="flex items-center gap-1.5 bg-surface-subtle border border-border px-2.5 py-1 rounded text-xs">
          <Cpu className="w-3.5 h-3.5 text-accent-light flex-shrink-0" />
          <span className="text-foreground-subtle text-2xs font-mono uppercase">Investigation:</span>
          {investigations.length > 0 ? (
            <select
              value={activeInvestigationId || ''}
              onChange={(e) => setActiveInvestigationId(e.target.value)}
              className="bg-transparent text-foreground font-mono text-xs focus:outline-none cursor-pointer max-w-[220px] truncate"
            >
              {investigations.map((i) => (
                <option key={i.investigation_id} value={i.investigation_id} className="bg-surface text-foreground font-mono">
                  {i.investigation_id} ({i.status})
                </option>
              ))}
            </select>
          ) : (
            <span className="text-foreground-muted text-xs italic">
              {activeCaseId ? 'No investigations for this case' : 'Select case first'}
            </span>
          )}
          {activeInvestigation && (
            <StatusBadge status={activeInvestigation.status} type="investigation" size="sm" className="ml-1" />
          )}
        </div>
      </div>

      {/* Actions & Global Status */}
      <div className="flex items-center gap-3 flex-shrink-0">
        {backendHealthy === false && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-rose-950/70 border border-rose-800 text-rose-300 text-2xs font-mono">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Backend Offline (127.0.0.1:8000)</span>
          </div>
        )}

        {onOpenCreateCase && (
          <button
            type="button"
            onClick={onOpenCreateCase}
            className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded bg-surface-elevated hover:bg-surface-active text-foreground border border-border transition-colors"
          >
            <Plus className="w-3.5 h-3.5 text-accent-light" />
            <span>New Case</span>
          </button>
        )}

        <button
          type="button"
          onClick={handleRefresh}
          disabled={isRefreshing}
          title="Refresh current case & investigations"
          className="p-1.5 text-foreground-muted hover:text-foreground hover:bg-surface-elevated rounded border border-border transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-accent-light' : ''}`} />
        </button>
      </div>
    </header>
  );
};
