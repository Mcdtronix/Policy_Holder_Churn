import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import PolicyHoldersPage from "./pages/PolicyHoldersPage";
import ChurnAnalyticsPage from "./pages/ChurnAnalyticsPage";
import ReportsPage from "./pages/ReportsPage";
import PolicyRegistrationPage from "./pages/PolicyRegistrationPage";
import ClaimFormPage from "./pages/ClaimFormPage";
import ClaimsManagementPage from "./pages/ClaimsManagementPage";
import MaturedPoliciesPage from "./pages/MaturedPoliciesPage";
import PaymentUpdatesPage from "./pages/PaymentUpdatesPage";
import ChurnPredictionPage from "./pages/ChurnPredictionPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/login" element={<Navigate to="/" replace />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            <Route path="/policyholders" element={
              <ProtectedRoute>
                <PolicyHoldersPage />
              </ProtectedRoute>
            } />
            <Route path="/churn" element={
              <ProtectedRoute>
                <ChurnAnalyticsPage />
              </ProtectedRoute>
            } />
            <Route path="/reports" element={
              <ProtectedRoute>
                <ReportsPage />
              </ProtectedRoute>
            } />
            <Route path="/register-policy" element={
              <ProtectedRoute>
                <PolicyRegistrationPage />
              </ProtectedRoute>
            } />
            <Route path="/claims/new" element={
              <ProtectedRoute>
                <ClaimFormPage />
              </ProtectedRoute>
            } />
            <Route path="/claims" element={
              <ProtectedRoute>
                <ClaimsManagementPage />
              </ProtectedRoute>
            } />
            <Route path="/matured" element={
              <ProtectedRoute>
                <MaturedPoliciesPage />
              </ProtectedRoute>
            } />
            <Route path="/payments" element={
              <ProtectedRoute>
                <PaymentUpdatesPage />
              </ProtectedRoute>
            } />
            <Route path="/churn-prediction" element={
              <ProtectedRoute>
                <ChurnPredictionPage />
              </ProtectedRoute>
            } />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
