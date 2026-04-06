import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

import './lib/fetch-patch';
import { Layout } from "@/components/layout";

import Home from "@/pages/home";
import Login from "@/pages/auth/login";
import Register from "@/pages/auth/register";
import VerifyOtp from "@/pages/auth/verify-otp";
import ForgotPassword from "@/pages/auth/forgot-password";
import ResetPassword from "@/pages/auth/reset-password";
import ApplicantDashboard from "@/pages/applicant/dashboard";
import ApplyForm from "@/pages/applicant/apply";
import NewApplicant from "@/pages/applicant/new-applicant";
import Recommend from "@/pages/applicant/recommend";          // ← NEW
import RecommendALevel from "@/pages/applicant/recommend-a-level";
import RecommendOLevel from "@/pages/applicant/recommend-o-level";
import RecommendDiploma from "@/pages/applicant/recommend-diploma";
import RecommendHec from "@/pages/applicant/recommend-hec";
import FinalistDashboard from "@/pages/finalist/dashboard";
import CareerPaths from "@/pages/finalist/career-paths";
import Opportunities from "@/pages/finalist/opportunities";
import AdminDashboard from "@/pages/admin/dashboard";
import AdminAdmissions from "@/pages/admin/admissions";
import AdminOpportunities from "@/pages/admin/opportunities";
import NotFound from "@/pages/not-found";
import { RoleGuard } from "@/components/role-guard";
import { ErrorBoundary } from "@/components/error-boundary";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Home} />
        <Route path="/login" component={Login} />
        <Route path="/register" component={Register} />
        <Route path="/verify-otp" component={VerifyOtp} />
        <Route path="/forgot-password" component={ForgotPassword} />
        <Route path="/reset-password" component={ResetPassword} />

        {/* Applicant */}
        <Route path="/dashboard">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplicantDashboard />
            </RoleGuard>
          )}
        </Route>
        <Route path="/apply">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NewApplicant />
            </RoleGuard>
          )}
        </Route>

        {/* ── NEW: A-Level Program Recommendation Tool ── */}
        <Route path="/recommend">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <Recommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/a-level">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <RecommendALevel />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/o-level">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <RecommendOLevel />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/diploma">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <RecommendDiploma />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/hec">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <RecommendHec />
            </RoleGuard>
          )}
        </Route>

        <Route path="/apply/degree">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplyForm target="degree" />
            </RoleGuard>
          )}
        </Route>

        <Route path="/apply/diploma">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplyForm target="diploma" />
            </RoleGuard>
          )}
        </Route>

        <Route path="/apply/hec">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplyForm target="hec" />
            </RoleGuard>
          )}
        </Route>

        <Route path="/apply/masters">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplyForm target="masters" />
            </RoleGuard>
          )}
        </Route>

        <Route path="/apply/phd">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplyForm target="phd" />
            </RoleGuard>
          )}
        </Route>

        {/* Finalist */}
        <Route path="/career">
          {() => (
            <RoleGuard roles={["finalist"]}>
              <FinalistDashboard />
            </RoleGuard>
          )}
        </Route>
        <Route path="/career/profile">
          {() => (
            <RoleGuard roles={["finalist"]}>
              <FinalistDashboard />
            </RoleGuard>
          )}
        </Route>
        <Route path="/career/applications">
          {() => (
            <RoleGuard roles={["finalist"]}>
              <Opportunities />
            </RoleGuard>
          )}
        </Route>
        <Route path="/career/paths">
          {() => (
            <RoleGuard roles={["finalist"]}>
              <CareerPaths />
            </RoleGuard>
          )}
        </Route>
        <Route path="/career/opportunities">
          {() => (
            <RoleGuard roles={["finalist"]}>
              <Opportunities />
            </RoleGuard>
          )}
        </Route>

        {/* Admin */}
        <Route path="/admin">
          {() => (
            <RoleGuard roles={["admin"]}>
              <AdminDashboard />
            </RoleGuard>
          )}
        </Route>
        <Route path="/admin/admissions">
          {() => (
            <RoleGuard roles={["admin"]}>
              <AdminAdmissions />
            </RoleGuard>
          )}
        </Route>
        <Route path="/admin/opportunities">
          {() => (
            <RoleGuard roles={["admin"]}>
              <AdminOpportunities />
            </RoleGuard>
          )}
        </Route>

        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <ErrorBoundary>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
            <Router />
          </WouterRouter>
        </ErrorBoundary>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
