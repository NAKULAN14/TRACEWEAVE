import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Case, Investigation } from '../types/api';
import { api } from '../api/client';

interface InvestigationContextType {
  cases: Case[];
  activeCaseId: string | null;
  activeCase: Case | null;
  investigations: Investigation[];
  activeInvestigationId: string | null;
  activeInvestigation: Investigation | null;
  backendHealthy: boolean | null;
  isLoadingCases: boolean;
  isLoadingInvestigations: boolean;
  error: string | null;
  setActiveCaseId: (caseId: string | null) => void;
  setActiveInvestigationId: (invId: string | null) => void;
  refreshCases: () => Promise<void>;
  refreshInvestigations: () => Promise<void>;
  checkHealth: () => Promise<void>;
}

const InvestigationContext = createContext<InvestigationContextType | undefined>(undefined);

export const InvestigationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [activeCaseId, setActiveCaseIdState] = useState<string | null>(() => {
    return localStorage.getItem('traceweave_active_case_id') || null;
  });
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [activeInvestigationId, setActiveInvestigationIdState] = useState<string | null>(() => {
    return localStorage.getItem('traceweave_active_inv_id') || null;
  });
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const [isLoadingCases, setIsLoadingCases] = useState<boolean>(false);
  const [isLoadingInvestigations, setIsLoadingInvestigations] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Health check
  const checkHealth = useCallback(async () => {
    try {
      const res = await api.getHealth();
      setBackendHealthy(res.status === 'healthy');
    } catch {
      setBackendHealthy(false);
    }
  }, []);

  // Fetch Cases
  const refreshCases = useCallback(async () => {
    setIsLoadingCases(true);
    setError(null);
    try {
      const caseList = await api.listCases();
      setCases(caseList);

      // If no active case selected or active case is not in list, pick the first one
      if (caseList.length > 0) {
        if (!activeCaseId || !caseList.some((c) => c.case_id === activeCaseId)) {
          setActiveCaseIdState(caseList[0].case_id);
          localStorage.setItem('traceweave_active_case_id', caseList[0].case_id);
        }
      } else {
        setActiveCaseIdState(null);
        localStorage.removeItem('traceweave_active_case_id');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch cases';
      setError(msg);
    } finally {
      setIsLoadingCases(false);
    }
  }, [activeCaseId]);

  // Fetch Investigations for current active case
  const refreshInvestigations = useCallback(async () => {
    if (!activeCaseId) {
      setInvestigations([]);
      setActiveInvestigationIdState(null);
      localStorage.removeItem('traceweave_active_inv_id');
      return;
    }

    setIsLoadingInvestigations(true);
    try {
      const invList = await api.listCaseInvestigations(activeCaseId);
      setInvestigations(invList);

      if (invList.length > 0) {
        if (!activeInvestigationId || !invList.some((i) => i.investigation_id === activeInvestigationId)) {
          setActiveInvestigationIdState(invList[0].investigation_id);
          localStorage.setItem('traceweave_active_inv_id', invList[0].investigation_id);
        }
      } else {
        setActiveInvestigationIdState(null);
        localStorage.removeItem('traceweave_active_inv_id');
      }
    } catch (err: unknown) {
      console.warn('Failed to fetch investigations:', err);
      setInvestigations([]);
    } finally {
      setIsLoadingInvestigations(false);
    }
  }, [activeCaseId, activeInvestigationId]);

  // Handlers for switching
  const setActiveCaseId = (caseId: string | null) => {
    setActiveCaseIdState(caseId);
    if (caseId) {
      localStorage.setItem('traceweave_active_case_id', caseId);
    } else {
      localStorage.removeItem('traceweave_active_case_id');
    }
    // Reset investigation on case switch
    setActiveInvestigationIdState(null);
    localStorage.removeItem('traceweave_active_inv_id');
  };

  const setActiveInvestigationId = (invId: string | null) => {
    setActiveInvestigationIdState(invId);
    if (invId) {
      localStorage.setItem('traceweave_active_inv_id', invId);
    } else {
      localStorage.removeItem('traceweave_active_inv_id');
    }
  };

  useEffect(() => {
    checkHealth();
    refreshCases();
  }, [checkHealth, refreshCases]);

  useEffect(() => {
    if (activeCaseId) {
      refreshInvestigations();
    }
  }, [activeCaseId, refreshInvestigations]);

  const activeCase = cases.find((c) => c.case_id === activeCaseId) || null;
  const activeInvestigation = investigations.find((i) => i.investigation_id === activeInvestigationId) || null;

  return (
    <InvestigationContext.Provider
      value={{
        cases,
        activeCaseId,
        activeCase,
        investigations,
        activeInvestigationId,
        activeInvestigation,
        backendHealthy,
        isLoadingCases,
        isLoadingInvestigations,
        error,
        setActiveCaseId,
        setActiveInvestigationId,
        refreshCases,
        refreshInvestigations,
        checkHealth,
      }}
    >
      {children}
    </InvestigationContext.Provider>
  );
};

export const useInvestigation = () => {
  const context = useContext(InvestigationContext);
  if (!context) {
    throw new Error('useInvestigation must be used within an InvestigationProvider');
  }
  return context;
};
