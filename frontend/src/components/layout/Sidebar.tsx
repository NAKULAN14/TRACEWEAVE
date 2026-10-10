import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  FileArchive,
  Activity,
  ShieldAlert,
  Radio,
  Network,
  Clock,
  GitMerge,
  Target,
  Gauge,
  ListChecks,
  FileText,
  Cpu,
  Layers,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useInvestigation } from '../../context/InvestigationContext';

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    title: 'Overview',
    items: [
      { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    ],
  },
  {
    title: 'Investigation Core',
    items: [
      { name: 'Cases', path: '/cases', icon: Briefcase },
      { name: 'Evidence', path: '/evidence', icon: FileArchive },
      { name: 'Investigations', path: '/investigations', icon: Activity },
    ],
  },
  {
    title: 'Forensic Intelligence',
    items: [
      { name: 'IOC Analysis', path: '/iocs', icon: ShieldAlert },
      { name: 'Threat Intelligence', path: '/threat-intel', icon: Radio },
      { name: 'Infrastructure Graph', path: '/graph', icon: Network },
    ],
  },
  {
    title: 'Reconstruction',
    items: [
      { name: 'Forensic Timeline', path: '/timeline', icon: Clock },
      { name: 'Attack Chain', path: '/attack-chain', icon: GitMerge },
      { name: 'MITRE ATT&CK', path: '/mitre', icon: Target },
    ],
  },
  {
    title: 'Assessment & Output',
    items: [
      { name: 'Risk Assessment', path: '/risk', icon: Gauge },
      { name: 'Recommendations', path: '/recommendations', icon: ListChecks },
      { name: 'Investigation Reports', path: '/reports', icon: FileText },
    ],
  },
  {
    title: 'System',
    items: [
      { name: 'Architecture & Engine', path: '/architecture', icon: Cpu },
    ],
  },
];

export const Sidebar: React.FC = () => {
  const { backendHealthy } = useInvestigation();

  return (
    <aside className="w-64 flex-shrink-0 bg-surface/95 border-r border-border flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="h-14 px-4 flex items-center gap-3 border-b border-border bg-surface-subtle">
        <div className="w-8 h-8 rounded bg-accent/20 border border-accent/40 flex items-center justify-center text-accent-light">
          <Layers className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm font-bold tracking-wider text-foreground">
              TRACEWEAVE
            </span>
            <span className="text-2xs font-mono uppercase px-1 py-0.2 rounded bg-surface-elevated text-accent-light border border-accent/30">
              DFIR
            </span>
          </div>
          <p className="text-2xs text-foreground-subtle font-mono truncate">
            QR Forensic Engine
          </p>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        {navSections.map((section) => (
          <div key={section.title} className="space-y-0.5">
            <div className="px-2.5 pb-1 text-2xs font-mono uppercase tracking-wider text-foreground-subtle">
              {section.title}
            </div>
            {section.items.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-2.5 px-2.5 py-1.5 rounded text-xs transition-colors font-medium',
                      isActive
                        ? 'bg-accent/15 text-accent-light border border-accent/30 font-semibold'
                        : 'text-foreground-muted hover:text-foreground hover:bg-surface-elevated border border-transparent'
                    )
                  }
                >
                  <Icon className="w-4 h-4 flex-shrink-0 opacity-80" />
                  <span className="truncate">{item.name}</span>
                </NavLink>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer System Status */}
      <div className="p-3 border-t border-border bg-surface-subtle/60 text-2xs font-mono space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-foreground-subtle">Backend API</span>
          <div className="flex items-center gap-1.5">
            <span
              className={cn(
                'w-2 h-2 rounded-full',
                backendHealthy === true
                  ? 'bg-emerald-400'
                  : backendHealthy === false
                  ? 'bg-rose-500'
                  : 'bg-amber-400 animate-pulse'
              )}
            />
            <span
              className={cn(
                backendHealthy === true
                  ? 'text-emerald-400'
                  : backendHealthy === false
                  ? 'text-rose-400'
                  : 'text-amber-400'
              )}
            >
              {backendHealthy === true ? 'ONLINE' : backendHealthy === false ? 'OFFLINE' : 'CHECKING'}
            </span>
          </div>
        </div>
        <div className="flex items-center justify-between text-foreground-subtle">
          <span>Pipeline</span>
          <span>15 Stages</span>
        </div>
      </div>
    </aside>
  );
};
