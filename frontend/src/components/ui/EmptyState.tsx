import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';
import { cn } from '../../lib/utils';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-lg bg-surface/40',
        className
      )}
    >
      <div className="p-3 bg-surface-elevated border border-border/80 rounded-md text-foreground-muted mb-3">
        <Icon className="w-6 h-6 text-foreground-subtle" />
      </div>
      <h3 className="text-sm font-semibold text-foreground tracking-tight mb-1">{title}</h3>
      <p className="text-xs text-foreground-muted max-w-sm mb-4 leading-relaxed">{description}</p>
      {action && <div className="mt-1">{action}</div>}
    </div>
  );
};
