import React from 'react';
import { cn } from '../../lib/utils';

export interface StatusBadgeProps {
  status: string | null | undefined;
  type?: 'case' | 'investigation' | 'result' | 'verdict' | 'priority' | 'classification' | 'generic';
  className?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  type = 'generic',
  className,
  size = 'md',
}) => {
  if (!status) {
    return <span className="text-foreground-subtle text-xs">—</span>;
  }

  const s = status.toUpperCase();

  let colorClasses = 'bg-surface-elevated text-foreground-muted border-border';

  // Case Statuses
  if (type === 'case' || s === 'OPEN' || s === 'UNDER_INVESTIGATION' || s === 'RECONSTRUCTED' || s === 'CLOSED') {
    switch (s) {
      case 'OPEN':
        colorClasses = 'bg-sky-950/60 text-sky-400 border-sky-800/60';
        break;
      case 'UNDER_INVESTIGATION':
        colorClasses = 'bg-amber-950/60 text-amber-400 border-amber-800/60';
        break;
      case 'RECONSTRUCTED':
        colorClasses = 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60';
        break;
      case 'CLOSED':
        colorClasses = 'bg-slate-900 text-slate-400 border-slate-700/60';
        break;
    }
  }

  // Investigation Statuses
  if (type === 'investigation' || s === 'PENDING' || s === 'RUNNING' || s === 'COMPLETED' || s === 'FAILED') {
    switch (s) {
      case 'PENDING':
        colorClasses = 'bg-slate-900/90 text-slate-300 border-slate-700';
        break;
      case 'RUNNING':
        colorClasses = 'bg-amber-950/80 text-amber-300 border-amber-700 animate-pulse';
        break;
      case 'COMPLETED':
        colorClasses = 'bg-emerald-950/80 text-emerald-300 border-emerald-700';
        break;
      case 'FAILED':
        colorClasses = 'bg-rose-950/80 text-rose-300 border-rose-700';
        break;
    }
  }

  // Result / Provider Statuses
  if (s === 'NOT_AVAILABLE') {
    colorClasses = 'bg-zinc-900 text-zinc-400 border-zinc-700';
  } else if (s === 'AVAILABLE' || s === 'SUCCESS') {
    colorClasses = 'bg-emerald-950/70 text-emerald-300 border-emerald-800';
  }

  // Threat Verdicts
  if (s === 'MALICIOUS' || s === 'CRITICAL') {
    colorClasses = 'bg-rose-950 text-rose-300 border-rose-700';
  } else if (s === 'SUSPICIOUS' || s === 'HIGH') {
    colorClasses = 'bg-amber-950 text-amber-300 border-amber-700';
  } else if (s === 'BENIGN' || s === 'LOW') {
    colorClasses = 'bg-emerald-950/70 text-emerald-400 border-emerald-800';
  } else if (s === 'MEDIUM') {
    colorClasses = 'bg-blue-950 text-blue-300 border-blue-800';
  } else if (s === 'NOT_FOUND' || s === 'UNKNOWN') {
    colorClasses = 'bg-zinc-900 text-zinc-400 border-zinc-700';
  }

  // Classification (Forensic distinction)
  if (s === 'OBSERVED') {
    colorClasses = 'bg-cyan-950/80 text-cyan-300 border-cyan-800';
  } else if (s === 'INFERRED') {
    colorClasses = 'bg-purple-950/80 text-purple-300 border-purple-800';
  }

  return (
    <span
      className={cn(
        'inline-flex items-center font-mono font-medium border rounded tracking-tight',
        size === 'sm' ? 'px-1.5 py-0.5 text-2xs' : 'px-2 py-0.5 text-xs',
        colorClasses,
        className
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-70" />
      {status.replace(/_/g, ' ')}
    </span>
  );
};
