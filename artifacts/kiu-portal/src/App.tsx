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
import ApplicantDashboard from "@/pages/applicant/dashboard";
import ApplyForm from "@/pages/applicant/apply";
import FinalistDashboard from "@/pages/finalist/dashboard";
import CareerPaths from "@/pages/finalist/career-paths";
import Opportunities from "@/pages/finalist/opportunities";
import AdminDashboard from "@/pages/admin/dashboard";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Home} />
        <Route path="/login" component={Login} />
        <Route path="/register" component={Register} />
        <Route path="/verify-otp" component={VerifyOtp} />

        {/* Applicant */}
        <Route path="/dashboard" component={ApplicantDashboard} />
        <Route path="/apply" component={ApplyForm} />

        {/* Finalist */}
        <Route path="/career" component={FinalistDashboard} />
        <Route path="/career/paths" component={CareerPaths} />
        <Route path="/career/opportunities" component={Opportunities} />

        {/* Admin */}
        <Route path="/admin" component={AdminDashboard} />

        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
