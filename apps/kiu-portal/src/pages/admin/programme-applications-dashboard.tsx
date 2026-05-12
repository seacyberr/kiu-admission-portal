import React, { useEffect, useMemo, useState } from 'react';
import { useListAdmissionApplications } from '@workspace/api-client-react';
import { Button, Card, Input } from '@/components/ui/shared';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import { Search, Download, Eye, CheckCircle, XCircle, Clock } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { StatusBadge } from '@/components/status-badge';
import type { AdmissionApplication } from '@workspace/api-client-react';
import { useToast } from '@/hooks/use-toast';
import { CardSkeleton, ChartSkeleton, TableSkeleton, Skeleton } from '@/components/ui/skeleton';

const STATUS_BADGE_STATUS: Record<string, 'pending' | 'reviewed' | 'approved' | 'rejected' | 'in_progress'> = {
  pending: 'pending',
  under_review: 'reviewed',
  accepted: 'approved',
  rejected: 'rejected',
  waitlisted: 'in_progress',
};

const statusOptions = [
  { value: 'all', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'under_review', label: 'Under Review' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'waitlisted', label: 'Waitlisted' },
];

export default function AdminProgrammeApplicationsDashboard() {
  const { data: applicationsData, isLoading, error } = useListAdmissionApplications();
  const [applications, setApplications] = useState<AdmissionApplication[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [programmeFilter, setProgrammeFilter] = useState<string>('all');
  const { toast } = useToast();

  useEffect(() => {
    if (applicationsData?.applications) {
      setApplications(applicationsData.applications);
    }
  }, [applicationsData]);

  const filteredApplications = useMemo(() => {
    return applications.filter((app) => {
      const matchesSearch = searchTerm
        ? (app.applicationNumber?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false) ||
          (app.applicantPhone?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false) ||
          (app.program?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false)
        : true;

      const matchesStatus = statusFilter === 'all' || app.status === statusFilter;
      const matchesProgramme = programmeFilter === 'all' || app.program?.name === programmeFilter;

      return matchesSearch && matchesStatus && matchesProgramme;
    });
  }, [applications, programmeFilter, searchTerm, statusFilter]);

  const statusCounts = useMemo(
    () =>
      applications.reduce(
        (acc, app) => {
          acc[app.status] = (acc[app.status] || 0) + 1;
          return acc;
        },
        {
          pending: 0,
          under_review: 0,
          accepted: 0,
          rejected: 0,
          waitlisted: 0,
        } as Record<string, number>
      ),
    [applications]
  );

  const statusData = useMemo(
    () => [
      { name: 'Pending', value: statusCounts.pending, color: '#FFBB28' },
      { name: 'Under Review', value: statusCounts.under_review, color: '#0088FE' },
      { name: 'Accepted', value: statusCounts.accepted, color: '#00C49F' },
      { name: 'Rejected', value: statusCounts.rejected, color: '#FF8042' },
      { name: 'Waitlisted', value: statusCounts.waitlisted, color: '#8884D8' },
    ],
    [statusCounts]
  );

  const programmeData = useMemo(
    () =>
      applications.reduce((acc, app) => {
        const programmeName = app.program?.name || `Program ${app.programId}`;
        const existing = acc.find((item) => item.programme === programmeName);
        if (existing) {
          existing.count += 1;
        } else {
          acc.push({ programme: programmeName, count: 1 });
        }
        return acc;
      }, [] as { programme: string; count: number }[]),
    [applications]
  );

  const programmeOptionsList = useMemo(
    () =>
      Array.from(new Set(applications.map((app) => app.program?.name).filter(Boolean))) as string[],
    [applications]
  );

  const handleStatusChange = async (applicationId: number, newStatus: string) => {
    try {
      const response = await fetch(`/api/admission/applications/${applicationId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      setApplications((prev) =>
        prev.map((app) =>
          app.id === applicationId ? { ...app, status: newStatus as any, updatedAt: new Date().toISOString() } : app
        )
      );

      toast({
        title: 'Status Updated',
        description: `Application status changed to ${newStatus.replace('_', ' ')}`,
      });
    } catch (error) {
      console.error('Error updating application status:', error);
      toast({
        title: 'Update Failed',
        description: 'Failed to update application status. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const getStatusBadgeStatus = (status: string) => STATUS_BADGE_STATUS[status] ?? 'pending';

  // Mock timeline data - in real app, this would come from analytics API
  const timelineData = [
    { month: 'Jan', applications: 45 },
    { month: 'Feb', applications: 52 },
    { month: 'Mar', applications: 38 },
    { month: 'Apr', applications: 61 },
    { month: 'May', applications: 55 },
    { month: 'Jun', applications: 67 },
  ];

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <Skeleton className="h-8 w-96 mb-2" />
          <Skeleton className="h-4 w-80" />
        </div>

        {/* Stats Cards Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>

        {/* Charts Skeleton */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>

        {/* Table Skeleton */}
        <div className="border rounded-xl p-6">
          <Skeleton className="h-6 w-48 mb-4" />
          <TableSkeleton rows={8} columns={5} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <XCircle className="mx-auto h-12 w-12 text-destructive mb-4" />
          <h3 className="text-lg font-semibold text-destructive mb-2">Error Loading Applications</h3>
          <p className="text-muted-foreground">Failed to load application data. Please try again later.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-primary">Programme Applications Dashboard</h1>
        <p className="text-muted-foreground mt-2">Comprehensive overview of admission applications</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
              <Eye className="w-6 h-6" />
            </div>
            <div>
              <p className="text-muted-foreground font-semibold text-sm">Total Applications</p>
              <p className="text-3xl font-bold">{applications.length}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-yellow-100 text-yellow-600 flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <p className="text-muted-foreground font-semibold text-sm">Pending Review</p>
              <p className="text-3xl font-bold">{statusCounts.pending}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-muted-foreground font-semibold text-sm">Accepted</p>
              <p className="text-3xl font-bold">{statusCounts.accepted}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center">
              <XCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-muted-foreground font-semibold text-sm">Rejected</p>
              <p className="text-3xl font-bold">{statusCounts.rejected}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">Application Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">Applications by Programme</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={programmeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="programme" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card className="p-6 mb-8">
        <h3 className="text-xl font-bold mb-4">Application Trends (Last 6 Months)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="applications" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Applications Table */}
      <Card className="p-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search by name, email, or programme..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={programmeFilter} onValueChange={setProgrammeFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by programme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Programmes</SelectItem>
              {programmeOptionsList.map((programme) => (
                <SelectItem key={programme} value={programme}>{programme}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full" role="table" aria-label="Programme applications">
            <thead>
              <tr className="border-b" role="row">
                <th className="text-left py-3 px-4 font-semibold" role="columnheader" scope="col">Applicant</th>
                <th className="text-left py-3 px-4 font-semibold" role="columnheader" scope="col">Programme</th>
                <th className="text-left py-3 px-4 font-semibold" role="columnheader" scope="col">Status</th>
                <th className="text-left py-3 px-4 font-semibold" role="columnheader" scope="col">Submitted</th>
                <th className="text-left py-3 px-4 font-semibold" role="columnheader" scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredApplications.map((application) => (
                <tr key={application.id} className="border-b hover:bg-muted/50" role="row">
                  <td className="py-3 px-4" role="cell">
                    <div>
                      <p className="font-semibold">{application.applicationNumber || `App-${application.id}`}</p>
                      <p className="text-sm text-muted-foreground">{application.applicantPhone || 'No phone'}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4" role="cell">{application.program?.name || `Program ${application.programId}`}</td>
                  <td className="py-3 px-4" role="cell">
                    <StatusBadge status={getStatusBadgeStatus(application.status)} />
                  </td>
                  <td className="py-3 px-4 text-sm text-muted-foreground" role="cell">
                    {application.submittedAt ? new Date(application.submittedAt).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="py-3 px-4" role="cell">
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" aria-label={`View application ${application.applicationNumber}`}>View</Button>
                      <Select
                        value={application.status}
                        onValueChange={(value) => handleStatusChange(application.id, value)}
                      >
                        <SelectTrigger className="w-32" aria-label={`Change status for application ${application.applicationNumber}`}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="pending">Pending</SelectItem>
                          <SelectItem value="under_review">Under Review</SelectItem>
                          <SelectItem value="accepted">Accept</SelectItem>
                          <SelectItem value="rejected">Reject</SelectItem>
                          <SelectItem value="waitlisted">Waitlist</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredApplications.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            No applications found matching your criteria.
          </div>
        )}
      </Card>
    </div>
  );
}