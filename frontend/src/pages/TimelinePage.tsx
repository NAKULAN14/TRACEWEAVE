import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Clock,
  RefreshCw,
  Search,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { TimelineResponse } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';
import { formatDate } from '../lib/utils';

export const TimelinePage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [timelineData, setTimelineData] = useState<TimelineResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [classFilter, setClassFilter] = useState<'ALL' | 'OBSERVED' | 'INFERRED'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const loadTimeline = useCallback(async () => {
    if (!effectiveInvId) {
      setTimelineData(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getTimeline(effectiveInvId);
      setTimelineData(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query forensic timeline');
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
    loadTimeline();
  }, [loadTimeline]);

  const rawEvents = timelineData?.events || [];

  const filteredEvents = rawEvents.filter((ev) => {
    const matchesClass =
      classFilter === 'ALL' ||
      (ev.classification && ev.classification.toUpperCase() === classFilter);
    const matchesSearch =
      ev.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.event_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (ev.source_artifact && ev.source_artifact.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesClass && matchesSearch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Clock className="w-5 h-5 text-accent-light" />
            FORENSIC INCIDENT TIMELINE
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Normalized chronological reconstruction differentiating directly observed timestamps from forensic inferences.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadTimeline()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh timeline events"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Investigation Scoper & Filter Toolbar */}
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
          <div className="relative flex-1 sm:w-60">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-subtle" />
            <input
              type="text"
              placeholder="Search event logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-surface-subtle border border-border rounded text-foreground focus:outline-none focus:border-accent"
            />
          </div>

          <div className="flex items-center bg-surface-subtle border border-border rounded p-0.5 text-2xs font-mono">
            <button
              type="button"
              onClick={() => setClassFilter('ALL')}
              className={`px-2 py-1 rounded transition-colors ${
                classFilter === 'ALL' ? 'bg-surface-elevated text-foreground font-bold' : 'text-foreground-muted'
              }`}
            >
              All ({rawEvents.length})
            </button>
            <button
              type="button"
              onClick={() => setClassFilter('OBSERVED')}
              className={`px-2 py-1 rounded transition-colors ${
                classFilter === 'OBSERVED' ? 'bg-cyan-950 text-cyan-300 font-bold border border-cyan-800' : 'text-foreground-muted'
              }`}
            >
              Observed
            </button>
            <button
              type="button"
              onClick={() => setClassFilter('INFERRED')}
              className={`px-2 py-1 rounded transition-colors ${
                classFilter === 'INFERRED' ? 'bg-purple-950 text-purple-300 font-bold border border-purple-800' : 'text-foreground-muted'
              }`}
            >
              Inferred
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <LoadingSpinner label="Querying chronological timeline events..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={Clock}
          title="No Investigation Selected"
          description="Select an investigation to view reconstructed forensic events."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {timelineData?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="Forensic Timeline Output Not Available"
              message={timelineData.message}
              pipelineStage="TIMELINE_RECONSTRUCTION (Stage 11)"
              investigationId={effectiveInvId}
            />
          )}

          {/* Academic Integrity Legend */}
          <div className="bg-surface border border-border rounded-lg p-4 font-mono text-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="text-foreground-subtle text-2xs uppercase">Classification Standards:</span>
              <span className="flex items-center gap-1.5 text-2xs text-cyan-300 bg-cyan-950/50 border border-cyan-800/80 px-2 py-0.5 rounded">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> OBSERVED — Directly extracted from MIME Date or DNS logs
              </span>
              <span className="flex items-center gap-1.5 text-2xs text-purple-300 bg-purple-950/50 border border-purple-800/80 px-2 py-0.5 rounded">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400" /> INFERRED — Deduced via chronological correlation
              </span>
            </div>
            <div className="text-2xs text-foreground-subtle italic">
              Order preserves causal integrity
            </div>
          </div>

          {/* Timeline Stream */}
          {filteredEvents.length > 0 ? (
            <div className="bg-surface border border-border rounded-lg p-5">
              <div className="relative border-l-2 border-border ml-3 pl-6 space-y-6">
                {filteredEvents.map((ev, idx) => (
                  <div key={idx} className="relative group">
                    <span
                      className={`absolute -left-[31px] top-1.5 w-3 h-3 rounded-full border-2 bg-surface ${
                        ev.classification === 'OBSERVED'
                          ? 'border-cyan-400 bg-cyan-950'
                          : 'border-purple-400 bg-purple-950'
                      }`}
                    />
                    <div className="bg-surface-subtle hover:bg-surface-elevated border border-border rounded-lg p-4 transition-colors font-mono text-xs space-y-2">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-foreground font-semibold">{ev.event_type}</span>
                          <StatusBadge
                            status={ev.classification || 'OBSERVED'}
                            type="classification"
                            size="sm"
                          />
                        </div>
                        <span className="text-foreground-muted text-2xs">
                          {formatDate(ev.timestamp)}
                        </span>
                      </div>

                      <p className="text-foreground-muted font-sans text-xs leading-relaxed">
                        {ev.description}
                      </p>

                      {(ev.source_artifact || ev.provenance) && (
                        <div className="pt-2 border-t border-border/50 flex flex-wrap items-center gap-4 text-2xs text-foreground-subtle">
                          {ev.source_artifact && (
                            <span>Source Artifact: <strong className="text-foreground-muted">{ev.source_artifact}</strong></span>
                          )}
                          {ev.provenance && (
                            <span>Provenance: <strong className="text-foreground-muted">{ev.provenance}</strong></span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-12 text-center bg-surface border border-dashed border-border rounded-lg">
              <Clock className="w-8 h-8 text-foreground-subtle mx-auto mb-2 opacity-60" />
              <h3 className="text-xs font-semibold text-foreground font-mono">
                No Chronological Events Generated
              </h3>
              <p className="text-2xs text-foreground-muted max-w-md mx-auto mt-1 leading-relaxed">
                Reconstructed incident milestones will appear in chronological sequence once the timeline
                reconstruction engine executes on the ingested evidence.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
