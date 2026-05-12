import { useEffect, useMemo, useState } from 'react';
import { Card, Badge, Button } from '@/components/ui/shared';
import { Link } from 'wouter';
import { ArrowLeft, Briefcase, Clock, CheckCircle } from 'lucide-react';

interface Application {
  id: number;
  opportunityId: number;
  opportunity?: {
    title: string;
    organization: string;
    type: string;
    location: string;
  };
  status: string;
  statusLabel: string;
  statusColor: string;
  coverLetter: string;
  appliedAt: string;
  updatedAt: string;
}

const STATUS_PIPELINE = [
  { status: 'applied', label: 'Applied', color: 'bg-blue-100 text-blue-800' },
  { status: 'reviewed', label: 'Reviewed', color: 'bg-indigo-100 text-indigo-800' },
  { status: 'shortlisted', label: 'Shortlisted', color: 'bg-yellow-100 text-yellow-800' },
  { status: 'interview_scheduled', label: 'Interview', color: 'bg-orange-100 text-orange-800' },
  { status: 'interviewed', label: 'Interviewed', color: 'bg-purple-100 text-purple-800' },
  { status: 'placed', label: 'Placed', color: 'bg-green-100 text-green-800' },
  { status: 'accepted', label: 'Accepted', color: 'bg-green-200 text-green-900' },
  { status: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-800' },
];

export default function MyApplications() {
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/opportunities/applications/my', {
          credentials: 'include',
        });
        const json = await response.json();
        const list = json?.data?.applications || [];
        const normalized: Application[] = list.map((app: any) => ({
          id: app.id,
          opportunityId: app.opportunityId,
          opportunity: app.opportunity,
          status: app.status,
          statusLabel: app.status?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()) || 'Applied',
          statusColor: app.status === 'rejected' ? 'danger' : app.status === 'accepted' || app.status === 'placed' ? 'success' : 'warning',
          coverLetter: app.coverLetter,
          appliedAt: app.appliedAt,
          updatedAt: app.updatedAt,
        }));
        setApplications(normalized);
      } catch (e: any) {
        setError(e?.message || 'Failed to load applications');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filteredApps = useMemo(
    () => (filterStatus ? applications.filter((app) => app.status === filterStatus) : applications),
    [applications, filterStatus]
  );

  const getPipelinePosition = (status: string) => {
    return STATUS_PIPELINE.findIndex(s => s.status === status);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-UG', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <Link href="/finalist/dashboard" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
        </Link>
        <h1 className="text-3xl font-display font-bold text-primary">My Applications</h1>
        <p className="text-muted-foreground mt-2">Track your job and internship applications</p>
      </div>

      {error && (
        <Card className="p-4 mb-6 border-destructive/20 bg-destructive/5 text-destructive text-sm">
          {error}
        </Card>
      )}

      {loading && (
        <Card className="p-6 mb-6 text-sm text-muted-foreground">
          Loading your applications...
        </Card>
      )}

      {/* Pipeline Overview */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-muted-foreground mb-3">Application Pipeline</h2>
        <div className="flex items-center justify-between bg-white rounded-lg border p-4 overflow-x-auto">
          {STATUS_PIPELINE.slice(0, 6).map((step) => {
            const count = applications.filter(a => a.status === step.status).length;
            return (
              <div key={step.status} className="flex flex-col items-center min-w-[80px]">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                  count > 0 ? 'bg-primary text-white' : 'bg-gray-100 text-gray-400'
                }`}>
                  {count}
                </div>
                <span className="text-xs mt-2 text-center">{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Filter */}
      <div className="mb-6 flex gap-2 flex-wrap">
        <Button 
          variant={filterStatus === '' ? 'primary' : 'outline'} 
          size="sm"
          onClick={() => setFilterStatus('')}
        >
          All ({applications.length})
        </Button>
        {STATUS_PIPELINE.map(step => {
          const count = applications.filter(a => a.status === step.status).length;
          if (count === 0) return null;
          return (
            <Button
              key={step.status}
              variant={filterStatus === step.status ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilterStatus(step.status)}
            >
              {step.label} ({count})
            </Button>
          );
        })}
      </div>

      {/* Applications List */}
      <div className="space-y-4">
        {filteredApps.length === 0 ? (
          <Card className="p-12 text-center">
            <Briefcase className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No applications yet</h3>
            <p className="text-muted-foreground mb-4">Start applying for jobs and internships</p>
            <Link href="/finalist/opportunities">
              <Button>Browse Opportunities</Button>
            </Link>
          </Card>
        ) : (
          filteredApps.map(app => (
            <Card key={app.id} className="p-6">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-start gap-3 mb-2">
                    <Badge variant={app.opportunity?.type === 'job' ? 'default' : 'warning'}>
                      {app.opportunity?.type}
                    </Badge>
                    <Badge variant={app.statusColor as any}>{app.statusLabel}</Badge>
                  </div>
                  <h3 className="text-xl font-bold">{app.opportunity?.title}</h3>
                  <p className="text-primary font-medium">{app.opportunity?.organization}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    <Clock className="w-4 h-4 inline mr-1" />
                    Applied on {formatDate(app.appliedAt)}
                  </p>
                </div>
                
                <div className="flex flex-col gap-2">
                  <Link href={`/finalist/opportunities/${app.opportunityId}`}>
                    <Button variant="outline" size="sm">View Details</Button>
                  </Link>
                </div>
              </div>
              
              {/* Pipeline Progress */}
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center gap-2 overflow-x-auto pb-2">
                  {STATUS_PIPELINE.map((step, index) => {
                    const currentPos = getPipelinePosition(app.status);
                    const isPast = index < currentPos;
                    const isCurrent = index === currentPos;
                    return (
                      <div key={step.status} className="flex items-center">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                          isPast ? 'bg-green-500 text-white' :
                          isCurrent ? 'bg-blue-500 text-white' :
                          'bg-gray-200 text-gray-500'
                        }`}>
                          {isPast ? <CheckCircle className="w-4 h-4" /> : index + 1}
                        </div>
                        {index < STATUS_PIPELINE.length - 1 && (
                          <div className={`w-8 h-0.5 ${
                            isPast ? 'bg-green-500' : 'bg-gray-200'
                          }`} />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
