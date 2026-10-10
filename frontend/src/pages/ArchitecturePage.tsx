import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Layers,
  BookOpen,
} from 'lucide-react';
import { api } from '../api/client';
import { PIPELINE_STAGES } from '../types/api';

export const ArchitecturePage: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<string | null>(null);

  useEffect(() => {
    api.getHealth()
      .then((h) => setHealthStatus(h.status))
      .catch(() => setHealthStatus('unreachable'));
  }, []);

  const endpointMap = [
    { method: 'GET', path: '/', feature: 'API Root & Discovery', status: 'LIVE', backend: 'FastAPI Main' },
    { method: 'GET', path: '/health', feature: 'Health Telemetry', status: 'LIVE', backend: 'FastAPI Main' },
    { method: 'POST', path: '/api/cases', feature: 'Case Intake', status: 'LIVE', backend: 'SQLAlchemy / SQLite' },
    { method: 'GET', path: '/api/cases', feature: 'Case Docket Listing', status: 'LIVE', backend: 'SQLAlchemy / SQLite' },
    { method: 'GET', path: '/api/cases/{case_id}', feature: 'Case Inspection', status: 'LIVE', backend: 'SQLAlchemy / SQLite' },
    { method: 'PUT', path: '/api/cases/{case_id}', feature: 'Case State Mutation', status: 'LIVE', backend: 'SQLAlchemy / SQLite' },
    { method: 'POST', path: '/api/cases/{case_id}/evidence', feature: 'Evidence Upload & Hash', status: 'LIVE', backend: 'Forensic Ingest Engine' },
    { method: 'GET', path: '/api/cases/{case_id}/evidence', feature: 'Case Evidence Retrieval', status: 'LIVE', backend: 'SQLAlchemy / SQLite' },
    { method: 'GET', path: '/api/cases/{case_id}/evidence/{evidence_id}', feature: 'Artifact Hash Inspection', status: 'LIVE', backend: 'SQLAlchemy / SQLite' },
    { method: 'POST', path: '/api/cases/{case_id}/investigations', feature: 'Investigation Run Intake', status: 'LIVE', backend: 'Investigation Service' },
    { method: 'GET', path: '/api/cases/{case_id}/investigations', feature: 'Investigation Run Listing', status: 'LIVE', backend: 'Investigation Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}', feature: 'Run Lifecycle State', status: 'LIVE', backend: 'Investigation Service' },
    { method: 'POST', path: '/api/investigations/{investigation_id}/start', feature: 'Run Execution Trigger', status: 'LIVE', backend: 'Investigation Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/status', feature: '15-Stage Status Aggregator', status: 'LIVE', backend: 'Stage Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/stages', feature: 'Pipeline Stage Sequences', status: 'LIVE', backend: 'Stage Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/results', feature: 'Result Type Registry', status: 'REGISTERED', backend: 'Results Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/results/{type}', feature: 'IOC / Attack Chain Results', status: 'REGISTERED', backend: 'Forensic Output Adapter' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/graph', feature: 'Infrastructure Graph', status: 'REGISTERED', backend: 'Graph Timeline Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/timeline', feature: 'Reconstructed Timeline', status: 'REGISTERED', backend: 'Graph Timeline Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/risk', feature: 'Composite Risk Assessment', status: 'REGISTERED', backend: 'Risk Recommendation Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/recommendations', feature: 'Response Recommendations', status: 'REGISTERED', backend: 'Risk Recommendation Service' },
    { method: 'GET', path: '/api/investigations/{investigation_id}/report', feature: 'Deliverable Export (JSON/HTML/MD)', status: 'REGISTERED', backend: 'Report Service' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Cpu className="w-5 h-5 text-accent-light" />
            SYSTEM ARCHITECTURE & FORENSIC PIPELINE
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Technical specifications, academic research context, and backend integration registry.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-2xs">
          <span className="text-foreground-subtle">API Health:</span>
          <span className={`px-2 py-0.5 rounded border ${
            healthStatus === 'healthy'
              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
              : 'bg-zinc-900 text-zinc-400 border-zinc-700'
          }`}>
            {healthStatus || 'CHECKING'}
          </span>
        </div>
      </div>

      {/* Research Paper Context Card */}
      <div className="bg-surface border border-border rounded-lg p-5 font-mono text-xs space-y-3">
        <div className="flex items-center gap-2 text-accent-light font-semibold">
          <BookOpen className="w-4 h-4" />
          <span>Academic Research Title</span>
        </div>
        <p className="text-sm font-bold text-foreground font-sans leading-snug">
          "Cross-Layer Forensic Reconstruction of QR-Mediated Social Engineering Incidents from Structurally Deceptive Digital Artifacts"
        </p>
        <p className="text-2xs text-foreground-muted leading-relaxed font-sans">
          TRACEWEAVE is designed to provide rigorous digital forensic and incident response capabilities for
          complex phishing lures that bridge protocol boundaries—specifically email bodies, ICS calendar
          invitations, and optical QR code transduction into mobile web execution environments.
        </p>
      </div>

      {/* Pipeline 15-Stage Specification */}
      <div className="bg-surface border border-border rounded-lg p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-foreground font-mono flex items-center gap-2">
            <Layers className="w-4 h-4 text-accent-light" />
            Sequential 15-Stage Investigation Pipeline
          </h2>
          <span className="text-2xs font-mono text-foreground-subtle">
            backend/app/services/investigation_stages.py
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 font-mono text-2xs">
          {PIPELINE_STAGES.map((stage, idx) => (
            <div
              key={stage}
              className="p-2.5 rounded bg-surface-subtle border border-border flex items-center gap-2"
            >
              <span className="w-5 h-5 rounded bg-surface-elevated text-accent-light flex items-center justify-center font-bold flex-shrink-0">
                {idx + 1}
              </span>
              <span className="truncate font-medium text-foreground">{stage}</span>
            </div>
          ))}
        </div>
      </div>

      {/* API Integration Verification Matrix */}
      <div className="bg-surface border border-border rounded-lg overflow-hidden">
        <div className="px-5 py-3 border-b border-border bg-surface-subtle flex items-center justify-between font-mono text-xs">
          <div>
            <h3 className="font-semibold uppercase tracking-wider text-foreground">
              Verified FastAPI REST Endpoints Matrix
            </h3>
            <p className="text-2xs text-foreground-muted">
              Validated against backend OpenAPI schema (22 endpoints)
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xs text-foreground-subtle">Backend URL:</span>
            <code className="px-1.5 py-0.5 rounded bg-surface-elevated text-accent-light text-2xs">
              {api.getBaseUrl()}
            </code>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-border bg-surface-subtle/50 text-2xs uppercase tracking-wider text-foreground-subtle">
                <th className="px-4 py-2.5">Method</th>
                <th className="px-4 py-2.5">Endpoint Path</th>
                <th className="px-4 py-2.5">Feature Responsibility</th>
                <th className="px-4 py-2.5">Backend Service</th>
                <th className="px-4 py-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {endpointMap.map((ep, idx) => (
                <tr key={idx} className="hover:bg-surface-elevated/60 transition-colors">
                  <td className="px-4 py-2.5 font-bold whitespace-nowrap">
                    <span
                      className={`px-1.5 py-0.5 rounded text-2xs ${
                        ep.method === 'GET'
                          ? 'bg-sky-950 text-sky-400 border border-sky-800'
                          : ep.method === 'POST'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : 'bg-amber-950 text-amber-400 border border-amber-800'
                      }`}
                    >
                      {ep.method}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-accent-light font-medium whitespace-nowrap">
                    {ep.path}
                  </td>
                  <td className="px-4 py-2.5 text-foreground">{ep.feature}</td>
                  <td className="px-4 py-2.5 text-foreground-muted text-2xs">{ep.backend}</td>
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    <span
                      className={`px-1.5 py-0.5 rounded text-2xs font-semibold ${
                        ep.status === 'LIVE'
                          ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                          : 'bg-zinc-900 text-zinc-400 border border-zinc-700'
                      }`}
                    >
                      {ep.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
