import { useListAdmissionApplications, useListOpportunities } from '@workspace/api-client-react';
import { Card } from '@/components/ui/shared';
import { Users, FileText, Briefcase, TrendingUp } from 'lucide-react';
import { Link } from 'wouter';

export default function AdminDashboard() {
  const { data: admissions } = useListAdmissionApplications();
  const { data: opportunities } = useListOpportunities();

  const pendingAdmissions = admissions?.applications.filter(a => a.status === 'pending').length || 0;
  const activeJobs = opportunities?.opportunities.filter(o => o.isActive).length || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex flex-col items-center text-center mb-8">
        <img
          src={`${import.meta.env.BASE_URL}images/logo.png`}
          alt="KIU Logo"
          className="w-16 h-16 object-contain drop-shadow"
        />
        <h1 className="text-3xl font-display font-bold text-primary mt-4">Admin Overview</h1>
        <p className="text-muted-foreground mt-2">
          Admissions and opportunities management
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <Card className="p-6 flex items-center gap-4 bg-primary text-primary-foreground border-none">
          <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <p className="text-primary-foreground/80 font-semibold text-sm">Total Applications</p>
            <p className="text-3xl font-bold">{admissions?.total || 0}</p>
          </div>
        </Card>
        
        <Card className="p-6 flex items-center gap-4 border-accent/30 bg-accent/5">
          <div className="w-12 h-12 rounded-full bg-accent/20 text-accent-foreground flex items-center justify-center">
            <ClockIcon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-muted-foreground font-semibold text-sm">Pending Review</p>
            <p className="text-3xl font-bold text-accent-foreground">{pendingAdmissions}</p>
          </div>
        </Card>

        <Card className="p-6 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-success/10 text-success flex items-center justify-center">
            <Briefcase className="w-6 h-6" />
          </div>
          <div>
            <p className="text-muted-foreground font-semibold text-sm">Active Opportunities</p>
            <p className="text-3xl font-bold">{activeJobs}</p>
          </div>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <Card className="p-8">
          <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
          <div className="space-y-4">
            <Link href="/admin/admissions" className="block p-4 rounded-xl border border-border hover:border-primary hover:bg-primary/5 transition-all">
              <div className="font-semibold text-primary mb-1">Review Admissions</div>
              <p className="text-sm text-muted-foreground">Process incoming student applications.</p>
            </Link>
            <Link href="/admin/opportunities" className="block p-4 rounded-xl border border-border hover:border-accent hover:bg-accent/5 transition-all">
              <div className="font-semibold text-accent-foreground mb-1">Manage Jobs & Internships</div>
              <p className="text-sm text-muted-foreground">Post new roles for finalists.</p>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}

function ClockIcon(props: any) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
    </svg>
  )
}
