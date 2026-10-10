import React from 'react';
import { AlertCircle, Terminal, Layers } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface NotAvailableBannerProps {
  title: string;
  message?: string | null;
  pipelineStage?: string;
  investigationId?: string;
}

export const NotAvailableBanner: React.FC<NotAvailableBannerProps> = ({
  title,
  message,
  pipelineStage,
  investigationId,
}) => {
  return (
    <div className="border border-border/80 bg-surface-subtle/70 rounded-lg p-5 my-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded bg-surface-elevated border border-border text-amber-400 mt-0.5">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-sm font-semibold text-foreground">{title}</h4>
              <StatusBadge status="NOT_AVAILABLE" size="sm" />
            </div>
            <p className="text-xs text-foreground-muted leading-relaxed max-w-2xl">
              {message ||
                'This forensic capability is registered in the TRACEWEAVE backend, but execution results are not yet connected to the active investigation pipeline.'}
            </p>
          </div>
        </div>

        {pipelineStage && (
          <div className="hidden sm:flex flex-col items-end text-right">
            <span className="text-2xs uppercase tracking-wider text-foreground-subtle font-mono flex items-center gap-1">
              <Layers className="w-3 h-3" /> Pipeline Stage
            </span>
            <span className="text-xs font-mono text-accent-light">{pipelineStage}</span>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-border/50 flex flex-wrap items-center justify-between gap-2 text-2xs font-mono text-foreground-subtle">
        <div className="flex items-center gap-2">
          <Terminal className="w-3 h-3 text-foreground-muted" />
          <span>Status verified via TRACEWEAVE REST API</span>
          {investigationId && (
            <span>• Scoped to: <strong className="text-foreground-muted">{investigationId}</strong></span>
          )}
        </div>
        <div className="text-foreground-subtle italic">
          No synthetic or fabricated findings are displayed.
        </div>
      </div>
    </div>
  );
};
