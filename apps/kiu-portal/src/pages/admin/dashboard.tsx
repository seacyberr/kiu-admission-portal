// BUG FIX: removed unused imports Users and TrendingUp that caused TypeScript
// noUnusedLocals warnings and cluttered the bundle.
import { useListAdmissionApplications, useListOpportunities } from '@workspace/api-client-react';
import { Card } from '@/components/ui/shared';
import { FileText, Briefcase, Clock } from 'lucide-react';
import { Link } from 'wouter';

export default function AdminDashboard() {
  const { data: admissions, isLoading: admissionsLoading } = useListAdmissionApplications();
  const { data: opportunities, isLoading: opportunitiesLoading } = useListOpportunities();

  if (admissionsLoading || opportunitiesLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
        <Clock className="animate-spin text-primary w-12 h-12" />
        <p className="text-muted-foreground">Loading admin dashboard...</p>
      </div>
    );
  }

  const pendingAdmissions =
    admissions?.applications.filter((a: any) => a.status === 'pending').length || 0;
  const activeJobs =
    opportunities?.opportunities.filter((o: any) => o.isActive).length || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-primary">Admin Overview</h1>
        <p className="text-muted-foreground mt-2">Admissions and opportunities management</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
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
            <Clock className="w-6 h-6" />
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
            <Link
              href="/admin/admissions"
              className="block p-4 rounded-xl border border-border hover:border-primary hover:bg-primary/5 transition-all"
            >
              <div className="font-semibold text-primary mb-1">Review Admissions</div>
              <p className="text-sm text-muted-foreground">Process incoming student applications.</p>
            </Link>
            <Link
              href="/admin/opportunities"
              className="block p-4 rounded-xl border border-border hover:border-accent hover:bg-accent/5 transition-all"
            >
              <div className="font-semibold text-accent-foreground mb-1">
                Manage Jobs & Internships
              </div>
              <p className="text-sm text-muted-foreground">Post new roles for finalists.</p>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
