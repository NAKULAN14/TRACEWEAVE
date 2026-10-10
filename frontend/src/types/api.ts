/**
 * TRACEWEAVE API Type Definitions
 * Matches backend schemas from backend/app/schemas/
 */

export type CaseStatus = 'OPEN' | 'UNDER_INVESTIGATION' | 'RECONSTRUCTED' | 'CLOSED';

export interface Case {
  case_id: string;
  title: string;
  description: string | null;
  status: CaseStatus;
  created_at: string;
  updated_at: string;
}

export interface CaseCreateInput {
  title: string;
  description?: string;
}

export interface CaseUpdateInput {
  title?: string;
  description?: string;
  status?: CaseStatus;
}

export interface Evidence {
  evidence_id: string;
  case_id: string;
  original_filename: string;
  stored_filename: string;
  storage_path: string;
  file_size: number;
  sha256: string;
  mime_type: string | null;
  extension: string | null;
  imported_at: string;
  status: string;
}

export type InvestigationStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface Investigation {
  investigation_id: string;
  case_id: string;
  status: InvestigationStatus;
  current_stage: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface InvestigationStageStatus {
  sequence: number;
  stage: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | string;
}

export interface InvestigationStatusResponse {
  investigation_id: string;
  case_id: string;
  status: InvestigationStatus;
  current_stage: string | null;
  stages: InvestigationStageStatus[];
}

export interface InvestigationResultTypesResponse {
  investigation_id: string;
  case_id: string;
  available_result_types: string[];
  status: string;
  message: string;
}

export interface InvestigationResultResponse<T = unknown> {
  investigation_id: string;
  case_id: string;
  result_type: string;
  status: string; // usually "NOT_AVAILABLE" when not connected
  data: T | null;
  message: string | null;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'DOMAIN' | 'IP' | 'TLS_CERT' | 'EMAIL' | 'URL' | 'HOST' | string;
  properties?: Record<string, unknown>;
}

export interface GraphRelationship {
  id?: string;
  source: string;
  target: string;
  type: string;
  label?: string;
}

export interface InfrastructureGraphResponse {
  investigation_id: string;
  case_id: string;
  status: string;
  nodes: GraphNode[];
  relationships: GraphRelationship[];
  message: string | null;
}

export interface TimelineEvent {
  id?: string;
  timestamp: string;
  event_type: string;
  description: string;
  source_artifact?: string;
  provenance?: string;
  classification?: 'OBSERVED' | 'INFERRED' | string;
}

export interface TimelineResponse {
  investigation_id: string;
  case_id: string;
  status: string;
  events: TimelineEvent[];
  message: string | null;
}

export interface RiskFactor {
  factor: string;
  score?: number;
  severity?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  rationale?: string;
}

export interface RiskAssessmentResponse {
  investigation_id: string;
  case_id: string;
  status: string;
  overall_risk: string | null;
  risk_score: number | null;
  factors: RiskFactor[];
  message: string | null;
}

export interface RecommendationItem {
  id?: string;
  title?: string;
  description: string;
  priority?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | string;
  action_type?: string;
  evidence_ref?: string;
}

export interface RecommendationsResponse {
  investigation_id: string;
  case_id: string;
  status: string;
  recommendations: RecommendationItem[];
  message: string | null;
}

export type ReportFormat = 'json' | 'html' | 'markdown';

export interface InvestigationReportResponse {
  investigation_id: string;
  case_id: string;
  status: string;
  report_format: ReportFormat;
  report_content: string | null;
  message: string | null;
}

export interface IocItem {
  id?: string;
  type: 'URL' | 'DOMAIN' | 'IP' | 'EMAIL' | 'HASH' | string;
  value: string;
  source?: string;
  provenance?: string;
  verdict?: 'MALICIOUS' | 'SUSPICIOUS' | 'BENIGN' | 'NOT_FOUND' | 'UNKNOWN' | 'NOT_AVAILABLE' | string;
  enrichment_status?: string;
}

export interface MitreTechniqueMapping {
  technique_id: string;
  technique_name: string;
  tactic: string;
  confidence?: 'HIGH' | 'MEDIUM' | 'LOW' | string;
  evidence_ref?: string;
  description?: string;
}

export const PIPELINE_STAGES: readonly string[] = [
  'INGESTION',
  'EMAIL_ANALYSIS',
  'ATTACHMENT_EXTRACTION',
  'ICS_ANALYSIS',
  'QR_ANALYSIS',
  'URL_ANALYSIS',
  'IOC_ANALYSIS',
  'THREAT_INTELLIGENCE',
  'INFRASTRUCTURE_CORRELATION',
  'INCIDENT_RECONSTRUCTION',
  'TIMELINE_RECONSTRUCTION',
  'ATTACK_CHAIN',
  'MITRE_MAPPING',
  'RISK_ASSESSMENT',
  'RECOMMENDATIONS',
] as const;
