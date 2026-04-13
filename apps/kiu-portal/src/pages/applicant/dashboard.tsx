import { Link } from 'wouter';
import { useGetMyAdmissionApplication, useGetCurrentUser } from '@workspace/api-client-react';
import { Card, Button, Badge } from '@/components/ui/shared';
import { FileText, Clock, AlertCircle, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function ApplicantDashboard() {
  const { data: user, isLoading: userLoading } = useGetCurrentUser();
  const { data: application, isLoading: appLoading, error } = useGetMyAdmissionApplication({ query: { retry: false } });

  if (userLoading || appLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
        <Clock className="animate-spin text-primary w-12 h-12" />
        <p className="text-muted-foreground">Loading your dashboard...</p>
      </div>
    );
  }

  // Show error if API call failed
  if (error) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4 px-4">
        <AlertCircle className="text-destructive w-12 h-12" />
        <div className="text-center max-w-md">
          <h2 className="text-xl font-bold text-destructive mb-2">Error Loading Dashboard</h2>
          <p className="text-muted-foreground mb-4">
            {error instanceof Error ? error.message : "Failed to load your application data"}
          </p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  const hasApplication = !!application && !error;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted': return 'success';
      case 'rejected': return 'danger';
      case 'under_review': return 'warning';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-primary">Applicant Dashboard</h1>
        <p className="text-muted-foreground mt-2">Welcome back, {user?.firstName}. Manage your admission journey here.</p>
      </div>

      {!hasApplication ? (
        <Card className="p-12 text-center border-dashed border-2 bg-secondary/30">
          <div className="w-20 h-20 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-6">
            <FileText className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-bold mb-4">No Application Found</h2>
          <p className="text-muted-foreground max-w-md mx-auto mb-8">
            You haven't submitted an application for admission yet. Start your journey by filling out the application form.
          </p>
          <Link href="/apply">
            <Button size="lg" className="px-8 shadow-xl">Start Application Process</Button>
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Card className="p-8 bg-gradient-to-br from-primary to-primary/90 text-primary-foreground border-none shadow-xl">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                  <Badge variant={getStatusColor(application.status)} className="mb-4 bg-white/20 text-white border-none">
                    Status: {getStatusText(application.status)}
                  </Badge>
                  <h2 className="text-2xl font-bold text-white mb-2">
                    {application.program?.name || 'Program Under Review'}
                  </h2>
                  <p className="text-primary-foreground/80 flex items-center gap-2">
                    <span className="font-mono bg-black/20 px-2 py-1 rounded">App #{application.applicationNumber}</span>
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-primary-foreground/70 mb-1">Submitted on</p>
                  <p className="font-semibold flex items-center gap-2 text-white">
                    <Calendar className="w-4 h-4" />
                    {application.submittedAt ? format(new Date(application.submittedAt), 'MMMM d, yyyy') : 'N/A'}
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-8">
              <h3 className="text-xl font-bold mb-6 border-b border-border pb-4">Application Details</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-6 gap-x-8">
                <div>
                  <p className="text-sm text-muted-foreground font-semibold">Entry Level</p>
                  <p className="text-foreground capitalize">{application.examLevel.replace('_', ' ')}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground font-semibold">Exam Year</p>
                  <p className="text-foreground">{application.examYear}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground font-semibold">Index Number</p>
                  <p className="text-foreground font-mono">{application.indexNumber}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground font-semibold">Program Code</p>
                  <p className="text-foreground">{application.program?.code || 'N/A'}</p>
                </div>
              </div>
            </Card>
          </div>

          <div className="space-y-8">
            <Card className="p-6 bg-secondary/30">
              <h3 className="font-bold mb-6">Application Timeline</h3>
              <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-border">
                {/* Timeline item 1 */}
                <div className="relative flex items-center gap-4">
                  <div className="z-10 w-4 h-4 rounded-full bg-success flex items-center justify-center shrink-0 ml-3 md:ml-0 md:absolute md:left-1/2 md:-translate-x-1/2"></div>
                  <div className="flex-1 bg-card rounded-xl p-4 shadow-sm border">
                    <h4 className="font-bold text-sm">Application Submitted</h4>
                    <p className="text-xs text-muted-foreground mt-1">We received your application.</p>
                  </div>
                </div>
                {/* Timeline item 2 */}
                <div className="relative flex items-center gap-4">
                  <div className={`z-10 w-4 h-4 rounded-full flex items-center justify-center shrink-0 ml-3 md:ml-0 md:absolute md:left-1/2 md:-translate-x-1/2 ${application.status !== 'pending' ? 'bg-success' : 'bg-primary/20 border-2 border-primary'}`}></div>
                  <div className="flex-1 bg-card rounded-xl p-4 shadow-sm border">
                    <h4 className="font-bold text-sm">Under Review</h4>
                    <p className="text-xs text-muted-foreground mt-1">Admissions team is reviewing your grades.</p>
                  </div>
                </div>
                {/* Timeline item 3 */}
                <div className="relative flex items-center gap-4">
                  <div className={`z-10 w-4 h-4 rounded-full flex items-center justify-center shrink-0 ml-3 md:ml-0 md:absolute md:left-1/2 md:-translate-x-1/2 ${application.status === 'accepted' ? 'bg-success' : application.status === 'rejected' ? 'bg-destructive' : 'bg-border'}`}></div>
                  <div className="flex-1 bg-card rounded-xl p-4 shadow-sm border">
                    <h4 className="font-bold text-sm">Decision</h4>
                    <p className="text-xs text-muted-foreground mt-1">Final decision on your application.</p>
                  </div>
                </div>
              </div>
            </Card>

            {application.adminNotes && (
              <Card className="p-6 border-accent bg-accent/5">
                <h3 className="font-bold flex items-center gap-2 text-accent-foreground mb-3">
                  <AlertCircle className="w-5 h-5" /> Admissions Note
                </h3>
                <p className="text-sm text-foreground/80">{application.adminNotes}</p>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
