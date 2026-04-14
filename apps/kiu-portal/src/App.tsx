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
// Note: Legacy recommendation routes now use NCHERecommend directly
import NCHERecommend from "@/pages/applicant/nche-recommend";
import SimpleRecommend from "@/pages/applicant/recommend-simple";
import RealisticRecommend from "@/pages/applicant/realistic-recommend";
import ApplicationStart from "@/pages/applicant/application-start";
import CertificateDetails from "@/pages/applicant/certificate-details";
import PersonalInfo from "@/pages/applicant/personal-info";
import ReviewSubmit from "@/pages/applicant/review-submit";
import ApplicantProfile from "@/pages/applicant/profile";
import FinalistDashboard from "@/pages/finalist/dashboard";
import CareerPaths from "@/pages/finalist/career-paths";
import Opportunities from "@/pages/finalist/opportunities";
import FinalistProfileEdit from "@/pages/finalist/profile";
import AdminDashboard from "@/pages/admin/dashboard";
import AdminAdmissions from "@/pages/admin/admissions";
import AdminOpportunities from "@/pages/admin/opportunities";
import AdminUsers from "@/pages/admin/users";
import AdminPrograms from "@/pages/admin/programs";
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
        <Route path="/profile">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplicantProfile />
            </RoleGuard>
          )}
        </Route>

        {/* LEGACY RECOMMENDATION ROUTES - All redirect to NCHE System */}
        <Route path="/recommend">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/o-level">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/a-level">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/diploma">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/hec">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/national-cert">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/bachelors">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/masters">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/phd">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/recommend/tool">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
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

        {/* NCHE-Based Recommendation System (Primary) */}
        <Route path="/nche-recommend">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <NCHERecommend />
            </RoleGuard>
          )}
        </Route>
        
        {/* Alternative Recommendation Systems */}
        <Route path="/recommend-simple">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <SimpleRecommend />
            </RoleGuard>
          )}
        </Route>
        <Route path="/realistic-recommend">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <RealisticRecommend />
            </RoleGuard>
          )}
        </Route>

        {/* New Application Workflow */}
        <Route path="/apply/start">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ApplicationStart />
            </RoleGuard>
          )}
        </Route>
        <Route path="/apply/certificate-details">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <CertificateDetails />
            </RoleGuard>
          )}
        </Route>
        <Route path="/apply/personal-info">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <PersonalInfo />
            </RoleGuard>
          )}
        </Route>
        <Route path="/apply/review">
          {() => (
            <RoleGuard roles={["applicant"]}>
              <ReviewSubmit />
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
              <FinalistProfileEdit />
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
        <Route path="/admin/users">
          {() => (
            <RoleGuard roles={["admin"]}>
              <AdminUsers />
            </RoleGuard>
          )}
        </Route>
        <Route path="/admin/programs">
          {() => (
            <RoleGuard roles={["admin"]}>
              <AdminPrograms />
            </RoleGuard>
          )}
        </Route>

        {/* Finalist */}
        <Route path="/finalist">
          {() => (
            <RoleGuard roles={["finalist", "admin"]}>
              <FinalistDashboard />
            </RoleGuard>
          )}
        </Route>
        <Route path="/finalist/careers">
          {() => (
            <RoleGuard roles={["finalist", "admin"]}>
              <CareerPaths />
            </RoleGuard>
          )}
        </Route>
        <Route path="/finalist/opportunities">
          {() => (
            <RoleGuard roles={["finalist", "admin"]}>
              <Opportunities />
            </RoleGuard>
          )}
        </Route>
        <Route path="/finalist/profile">
          {() => (
            <RoleGuard roles={["finalist", "admin"]}>
              <FinalistProfileEdit />
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
