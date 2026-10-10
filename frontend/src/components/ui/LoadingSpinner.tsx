import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

interface LoadingSpinnerProps {
  label?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  label = 'Loading forensic data...',
  className,
  size = 'md',
}) => {
  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={cn('flex flex-col items-center justify-center p-8 text-foreground-muted', className)}>
      <Loader2 className={cn('animate-spin text-accent mb-2', iconSizes[size])} />
      {label && <p className="text-xs font-mono tracking-wide">{label}</p>}
    </div>
  );
};
