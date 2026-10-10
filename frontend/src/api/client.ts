/**
 * TRACEWEAVE Centralized API Client
 * Connects strictly to verified FastAPI backend endpoints
 */

import {
  Case,
  CaseCreateInput,
  CaseUpdateInput,
  Evidence,
  Investigation,
  InvestigationStatusResponse,
  InvestigationStageStatus,
  InvestigationResultTypesResponse,
  InvestigationResultResponse,
  InfrastructureGraphResponse,
  TimelineResponse,
  RiskAssessmentResponse,
  RecommendationsResponse,
  InvestigationReportResponse,
  ReportFormat,
} from '../types/api';

const DEFAULT_BASE_URL = 'http://127.0.0.1:8000';

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export class TraceweaveApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    // If not passed, use env variable, or fallback to default
    const envUrl = import.meta.env.VITE_API_BASE_URL;
    this.baseUrl = (baseUrl ?? envUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, '');
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

    const defaultHeaders: HeadersInit = {
      Accept: 'application/json',
    };

    if (!(options.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    let response: Response;
    try {
      response = await fetch(url, config);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Network request failed';
      throw new ApiError(
        `Unable to reach TRACEWEAVE backend at ${this.baseUrl}: ${message}. Verify backend server is running.`,
        0
      );
    }

    if (!response.ok) {
      let errorBody: unknown = null;
      let detailMessage = `Request failed with status ${response.status} (${response.statusText})`;

      try {
        errorBody = await response.json();
        if (typeof errorBody === 'object' && errorBody !== null && 'detail' in errorBody) {
          const detail = (errorBody as { detail: unknown }).detail;
          detailMessage = typeof detail === 'string' ? detail : JSON.stringify(detail);
        }
      } catch {
        // Response was not JSON
      }

      throw new ApiError(detailMessage, response.status, errorBody);
    }

    try {
      return (await response.json()) as T;
    } catch {
      return {} as T;
    }
  }

  // --- System ---
  async getHealth(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }

  async getRoot(): Promise<{ message: string; docs: string }> {
    return this.request<{ message: string; docs: string }>('/');
  }

  // --- Cases ---
  async listCases(): Promise<Case[]> {
    return this.request<Case[]>('/api/cases');
  }

  async getCase(caseId: string): Promise<Case> {
    return this.request<Case>(`/api/cases/${encodeURIComponent(caseId)}`);
  }

  async createCase(input: CaseCreateInput): Promise<Case> {
    return this.request<Case>('/api/cases', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  async updateCase(caseId: string, input: CaseUpdateInput): Promise<Case> {
    return this.request<Case>(`/api/cases/${encodeURIComponent(caseId)}`, {
      method: 'PUT',
      body: JSON.stringify(input),
    });
  }

  // --- Evidence ---
  async listEvidence(caseId: string): Promise<Evidence[]> {
    return this.request<Evidence[]>(`/api/cases/${encodeURIComponent(caseId)}/evidence`);
  }

  async getEvidence(caseId: string, evidenceId: string): Promise<Evidence> {
    return this.request<Evidence>(
      `/api/cases/${encodeURIComponent(caseId)}/evidence/${encodeURIComponent(evidenceId)}`
    );
  }

  async uploadEvidence(caseId: string, file: File): Promise<Evidence> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<Evidence>(`/api/cases/${encodeURIComponent(caseId)}/evidence`, {
      method: 'POST',
      body: formData,
    });
  }

  // --- Investigations ---
  async listCaseInvestigations(caseId: string): Promise<Investigation[]> {
    return this.request<Investigation[]>(`/api/cases/${encodeURIComponent(caseId)}/investigations`);
  }

  async getInvestigation(investigationId: string): Promise<Investigation> {
    return this.request<Investigation>(
      `/api/investigations/${encodeURIComponent(investigationId)}`
    );
  }

  async createInvestigation(caseId: string): Promise<Investigation> {
    return this.request<Investigation>(
      `/api/cases/${encodeURIComponent(caseId)}/investigations`,
      {
        method: 'POST',
      }
    );
  }

  async startInvestigation(investigationId: string): Promise<Investigation> {
    return this.request<Investigation>(
      `/api/investigations/${encodeURIComponent(investigationId)}/start`,
      {
        method: 'POST',
      }
    );
  }

  async getInvestigationStatus(investigationId: string): Promise<InvestigationStatusResponse> {
    return this.request<InvestigationStatusResponse>(
      `/api/investigations/${encodeURIComponent(investigationId)}/status`
    );
  }

  async getInvestigationStages(investigationId: string): Promise<InvestigationStageStatus[]> {
    return this.request<InvestigationStageStatus[]>(
      `/api/investigations/${encodeURIComponent(investigationId)}/stages`
    );
  }

  // --- Results ---
  async listResultTypes(investigationId: string): Promise<InvestigationResultTypesResponse> {
    return this.request<InvestigationResultTypesResponse>(
      `/api/investigations/${encodeURIComponent(investigationId)}/results`
    );
  }

  async getInvestigationResult<T = unknown>(
    investigationId: string,
    resultType: string
  ): Promise<InvestigationResultResponse<T>> {
    return this.request<InvestigationResultResponse<T>>(
      `/api/investigations/${encodeURIComponent(investigationId)}/results/${encodeURIComponent(resultType)}`
    );
  }

  // --- Dedicated Correlation Views ---
  async getInfrastructureGraph(investigationId: string): Promise<InfrastructureGraphResponse> {
    return this.request<InfrastructureGraphResponse>(
      `/api/investigations/${encodeURIComponent(investigationId)}/graph`
    );
  }

  async getTimeline(investigationId: string): Promise<TimelineResponse> {
    return this.request<TimelineResponse>(
      `/api/investigations/${encodeURIComponent(investigationId)}/timeline`
    );
  }

  async getRisk(investigationId: string): Promise<RiskAssessmentResponse> {
    return this.request<RiskAssessmentResponse>(
      `/api/investigations/${encodeURIComponent(investigationId)}/risk`
    );
  }

  async getRecommendations(investigationId: string): Promise<RecommendationsResponse> {
    return this.request<RecommendationsResponse>(
      `/api/investigations/${encodeURIComponent(investigationId)}/recommendations`
    );
  }

  async getReport(
    investigationId: string,
    format: ReportFormat = 'json'
  ): Promise<InvestigationReportResponse> {
    return this.request<InvestigationReportResponse>(
      `/api/investigations/${encodeURIComponent(investigationId)}/report?report_format=${encodeURIComponent(format)}`
    );
  }
}

export const api = new TraceweaveApiClient();
