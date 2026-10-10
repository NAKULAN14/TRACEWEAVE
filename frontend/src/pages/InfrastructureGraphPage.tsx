import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import {
  Network,
  RefreshCw,
} from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { api } from '../api/client';
import { InfrastructureGraphResponse, GraphNode } from '../types/api';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { NotAvailableBanner } from '../components/ui/NotAvailableBanner';

export const InfrastructureGraphPage: React.FC = () => {
  const { investigations, activeInvestigationId, setActiveInvestigationId } = useInvestigation();
  const [searchParams] = useSearchParams();

  const invParam = searchParams.get('investigation_id');
  const effectiveInvId = invParam || activeInvestigationId || (investigations.length > 0 ? investigations[0].investigation_id : null);

  const [graphData, setGraphData] = useState<InfrastructureGraphResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const loadGraph = useCallback(async () => {
    if (!effectiveInvId) {
      setGraphData(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getInfrastructureGraph(effectiveInvId);
      setGraphData(data);

      // Convert backend nodes & relationships to React Flow nodes & edges
      if (data.nodes && data.nodes.length > 0) {
        const flowNodes: Node[] = data.nodes.map((n, idx) => ({
          id: n.id,
          type: 'default',
          position: { x: (idx % 4) * 220 + 50, y: Math.floor(idx / 4) * 150 + 50 },
          data: { label: `${n.type}: ${n.label}` },
          style: {
            background: '#141b29',
            color: '#e6edf3',
            border: '1px solid #2f4160',
            borderRadius: '6px',
            fontSize: '11px',
            fontFamily: 'monospace',
            padding: '8px 12px',
          },
        }));
        setNodes(flowNodes);
      } else {
        setNodes([]);
      }

      if (data.relationships && data.relationships.length > 0) {
        const flowEdges: Edge[] = data.relationships.map((rel, idx) => ({
          id: rel.id || `edge-${idx}`,
          source: rel.source,
          target: rel.target,
          label: rel.type || rel.label,
          type: 'smoothstep',
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed, color: '#38bdf8' },
          style: { stroke: '#0284c7' },
        }));
        setEdges(flowEdges);
      } else {
        setEdges([]);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve infrastructure graph');
    } finally {
      setIsLoading(false);
    }
  }, [effectiveInvId, setNodes, setEdges]);

  useEffect(() => {
    if (effectiveInvId && effectiveInvId !== activeInvestigationId) {
      setActiveInvestigationId(effectiveInvId);
    }
  }, [effectiveInvId, activeInvestigationId, setActiveInvestigationId]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto flex flex-col h-[calc(100vh-6rem)]">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground font-mono flex items-center gap-2">
            <Network className="w-5 h-5 text-accent-light" />
            INFRASTRUCTURE CORRELATION GRAPH
          </h1>
          <p className="text-xs text-foreground-muted mt-1">
            Topological correlation mapping DNS records, IP addresses, TLS certificates, and domain assets.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => loadGraph()}
            disabled={isLoading || !effectiveInvId}
            className="p-1.5 text-foreground-muted hover:text-foreground bg-surface border border-border rounded transition-colors"
            title="Refresh infrastructure graph"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Investigation Scoper & Legend */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-surface border border-border p-3 rounded-lg flex-shrink-0">
        <div className="flex items-center gap-2">
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

        {/* Legend */}
        <div className="flex items-center gap-3 text-2xs font-mono text-foreground-muted">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400" /> Domain
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-400" /> IP Address
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> TLS Cert
          </span>
        </div>
      </div>

      {/* Main View Area */}
      {isLoading ? (
        <LoadingSpinner label="Loading infrastructure graph topology..." />
      ) : !effectiveInvId ? (
        <EmptyState
          icon={Network}
          title="No Investigation Selected"
          description="Select an investigation to display the infrastructure correlation graph."
        />
      ) : error ? (
        <div className="p-4 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="flex-1 flex flex-col min-h-0 space-y-4">
          {graphData?.status === 'NOT_AVAILABLE' && (
            <NotAvailableBanner
              title="Infrastructure Graph Output Not Available"
              message={graphData.message}
              pipelineStage="INFRASTRUCTURE_CORRELATION (Stage 9)"
              investigationId={effectiveInvId}
            />
          )}

          {nodes.length > 0 ? (
            <div className="flex-1 bg-surface border border-border rounded-lg relative overflow-hidden">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={(_, node) => {
                  const match = graphData?.nodes?.find((n) => n.id === node.id);
                  setSelectedNode(match || null);
                }}
                fitView
              >
                <Background color="#1f293d" gap={16} />
                <Controls className="bg-surface border border-border text-foreground" />
                <MiniMap
                  className="bg-surface border border-border rounded"
                  nodeColor={() => '#0284c7'}
                />
              </ReactFlow>

              {/* Node Inspector Panel */}
              {selectedNode && (
                <div className="absolute top-4 right-4 w-72 bg-surface/95 border border-border rounded-lg p-4 font-mono text-xs shadow-xl backdrop-blur-sm">
                  <div className="flex items-center justify-between pb-2 border-b border-border mb-2">
                    <span className="font-bold text-accent-light">{selectedNode.type}</span>
                    <button
                      type="button"
                      onClick={() => setSelectedNode(null)}
                      className="text-foreground-muted hover:text-foreground"
                    >
                      ×
                    </button>
                  </div>
                  <div className="text-foreground font-semibold break-all mb-2">
                    {selectedNode.label}
                  </div>
                  {selectedNode.properties && (
                    <div className="space-y-1 text-2xs text-foreground-muted">
                      {Object.entries(selectedNode.properties).map(([k, v]) => (
                        <div key={k} className="flex justify-between">
                          <span className="text-foreground-subtle">{k}:</span>
                          <span>{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 bg-surface border border-dashed border-border rounded-lg flex flex-col items-center justify-center p-8 text-center">
              <Network className="w-10 h-10 text-foreground-subtle mb-3 opacity-60" />
              <h3 className="text-sm font-semibold text-foreground font-mono">
                No Graph Nodes Available
              </h3>
              <p className="text-xs text-foreground-muted max-w-md mt-1 leading-relaxed">
                The TRACEWEAVE infrastructure correlation engine connects domains to DNS records,
                TLS certificates, and ASNs. Currently, the backend returned 0 nodes and 0 edges.
              </p>
              <div className="mt-4 p-3 bg-surface-subtle border border-border rounded text-2xs font-mono text-foreground-subtle max-w-md">
                <strong>Forensic Integrity Note:</strong> No synthetic or mock nodes are generated
                to fabricate infrastructure relationships.
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
