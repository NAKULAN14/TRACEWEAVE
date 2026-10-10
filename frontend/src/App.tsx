import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { InvestigationProvider } from './context/InvestigationContext';
import { AppLayout } from './components/layout/AppLayout';

// Feature Pages
import { DashboardPage } from './pages/DashboardPage';
import { CasesPage } from './pages/CasesPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { EvidencePage } from './pages/EvidencePage';
import { InvestigationsPage } from './pages/InvestigationsPage';
import { InvestigationDetailPage } from './pages/InvestigationDetailPage';
import { IocAnalysisPage } from './pages/IocAnalysisPage';
import { ThreatIntelligencePage } from './pages/ThreatIntelligencePage';
import { InfrastructureGraphPage } from './pages/InfrastructureGraphPage';
import { TimelinePage } from './pages/TimelinePage';
import { AttackChainPage } from './pages/AttackChainPage';
import { MitreMappingPage } from './pages/MitreMappingPage';
import { RiskAssessmentPage } from './pages/RiskAssessmentPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { ReportsPage } from './pages/ReportsPage';
import { ArchitecturePage } from './pages/ArchitecturePage';

export const App: React.FC = () => {
  return (
    <InvestigationProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="cases" element={<CasesPage />} />
            <Route path="cases/:caseId" element={<CaseDetailPage />} />
            <Route path="evidence" element={<EvidencePage />} />
            <Route path="investigations" element={<InvestigationsPage />} />
            <Route path="investigations/:investigationId" element={<InvestigationDetailPage />} />
            <Route path="iocs" element={<IocAnalysisPage />} />
            <Route path="threat-intel" element={<ThreatIntelligencePage />} />
            <Route path="graph" element={<InfrastructureGraphPage />} />
            <Route path="timeline" element={<TimelinePage />} />
            <Route path="attack-chain" element={<AttackChainPage />} />
            <Route path="mitre" element={<MitreMappingPage />} />
            <Route path="risk" element={<RiskAssessmentPage />} />
            <Route path="recommendations" element={<RecommendationsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="architecture" element={<ArchitecturePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </InvestigationProvider>
  );
};

export default App;
