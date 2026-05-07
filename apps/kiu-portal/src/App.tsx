import type { ComponentType } from "react";
import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ErrorBoundary } from "@/components/error-boundary";

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
import MyApplications from "@/pages/finalist/my-applications";
import FinalistProfileEdit from "@/pages/finalist/profile";
import NotificationsPage from "@/pages/notifications";
import AdminDashboard from "@/pages/admin/dashboard";
import AdminProgrammeApplicationsDashboard from "@/pages/admin/programme-applications-dashboard";
import AdminAdmissions from "@/pages/admin/admissions";
import AdminOpportunities from "@/pages/admin/opportunities";
import AdminUsers from "@/pages/admin/users";
import AdminPrograms from "@/pages/admin/programs";
import CareerApplications from "@/pages/admin/career-applications";
import NotFound from "@/pages/not-found";
import { RoleGuard } from "@/components/role-guard";

const queryClient = new QueryClient();

type ProtectedRouteConfig = {
  path: string;
  component?: ComponentType;
  render?: () => JSX.Element;
  roles?: Array<'applicant' | 'finalist' | 'admin'>;
};

const routes: ProtectedRouteConfig[] = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/verify-otp', component: VerifyOtp },
  { path: '/forgot-password', component: ForgotPassword },
  { path: '/reset-password', component: ResetPassword },
  { path: '/dashboard', component: ApplicantDashboard, roles: ['applicant'] },
  { path: '/apply', component: NewApplicant, roles: ['applicant'] },
  { path: '/profile', component: ApplicantProfile, roles: ['applicant'] },
  { path: '/notifications', component: NotificationsPage, roles: ['applicant', 'finalist', 'admin'] },
  { path: '/recommend', component: NCHERecommend, roles: ['applicant'] },
  { path: '/recommend/o-level', component: NCHERecommend, roles: ['applicant'] },
  { path: '/recommend/a-level', component: NCHERecommend, roles: ['applicant'] },
  { path: '/recommend/diploma', component: NCHERecommend, roles: ['applicant'] },
  { path: '/recommend/hec', component: NCHERecommend, roles: ['applicant'] },
  { path: '/recommend/national-cert', component: NCHERecommend, roles: ['applicant'] },
  { path: '/recommend/bachelors', component: NCHERecommend, roles: ['applicant'] },
  { path: '/recommend/tool', component: NCHERecommend, roles: ['applicant'] },
  { path: '/apply/degree', render: () => <ApplyForm target="degree" />, roles: ['applicant'] },
  { path: '/apply/diploma', render: () => <ApplyForm target="diploma" />, roles: ['applicant'] },
  { path: '/apply/hec', render: () => <ApplyForm target="hec" />, roles: ['applicant'] },
  { path: '/apply/masters', render: () => <ApplyForm target="masters" />, roles: ['applicant'] },
  { path: '/apply/phd', render: () => <ApplyForm target="phd" />, roles: ['applicant'] },
  { path: '/recommend-simple', component: SimpleRecommend, roles: ['applicant'] },
  { path: '/realistic-recommend', component: RealisticRecommend, roles: ['applicant'] },
  { path: '/apply/start', component: ApplicationStart, roles: ['applicant'] },
  { path: '/apply/certificate-details', component: CertificateDetails, roles: ['applicant'] },
  { path: '/apply/personal-info', component: PersonalInfo, roles: ['applicant'] },
  { path: '/apply/review', component: ReviewSubmit, roles: ['applicant'] },
  { path: '/career', component: FinalistDashboard, roles: ['finalist'] },
  { path: '/career/profile', component: FinalistProfileEdit, roles: ['finalist'] },
  { path: '/career/applications', component: MyApplications, roles: ['finalist'] },
  { path: '/career/paths', component: CareerPaths, roles: ['finalist'] },
  { path: '/career/opportunities', component: Opportunities, roles: ['finalist'] },
  { path: '/admin', component: AdminDashboard, roles: ['admin'] },
  { path: '/admin/programme-applications-dashboard', component: AdminProgrammeApplicationsDashboard, roles: ['admin'] },
  { path: '/admin/admissions', component: AdminAdmissions, roles: ['admin'] },
  { path: '/admin/opportunities', component: AdminOpportunities, roles: ['admin'] },
  { path: '/admin/career-applications', component: CareerApplications, roles: ['admin'] },
  { path: '/admin/users', component: AdminUsers, roles: ['admin'] },
  { path: '/admin/programs', component: AdminPrograms, roles: ['admin'] },
  { path: '/finalist', component: FinalistDashboard, roles: ['finalist', 'admin'] },
  { path: '/finalist/careers', component: CareerPaths, roles: ['finalist', 'admin'] },
  { path: '/finalist/opportunities', component: Opportunities, roles: ['finalist', 'admin'] },
  { path: '/finalist/my-applications', component: MyApplications, roles: ['finalist', 'admin'] },
  { path: '/finalist/profile', component: FinalistProfileEdit, roles: ['finalist', 'admin'] },
];

function renderRoute(route: ProtectedRouteConfig) {
  const { path, component: Component, render, roles } = route;
  const element = render ? render() : Component ? <Component /> : null;

  return (
    <Route key={path} path={path}>
      {() =>
        roles ? (
          <RoleGuard roles={roles}>{element}</RoleGuard>
        ) : (
          element
        )
      }
    </Route>
  );
}

function Router() {
  return (
    <Layout>
      <Switch>
        {routes.map(renderRoute)}
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
