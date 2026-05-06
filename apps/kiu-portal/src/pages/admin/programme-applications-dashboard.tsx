import React, { useEffect, useState } from 'react';
import { useListAdmissionApplications } from '@workspace/api-client-react';
import { Card } from '@/components/ui/shared';
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
import { Button } from '@/components/ui/shared';
import { Input } from '@/components/ui/shared';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { StatusBadge } from '@/components/status-badge';
import type { AdmissionApplication } from '@workspace/api-client-react';

export default function AdminProgrammeApplicationsDashboard() {
  const { data: applicationsData, isLoading } = useListAdmissionApplications();
  const [applications, setApplications] = useState<AdmissionApplication[]>([]);
  const [filteredApplications, setFilteredApplications] = useState<AdmissionApplication[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [programmeFilter, setProgrammeFilter] = useState<string>('all');

  useEffect(() => {
    if (applicationsData?.applications) {
      setApplications(applicationsData.applications);
      setFilteredApplications(applicationsData.applications);
    }
  }, [applicationsData]);

  useEffect(() => {
    let filtered = applications;

    if (searchTerm) {
      filtered = filtered.filter(app =>
        (app.applicationNumber?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false) ||
        (app.applicantPhone?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false) ||
        (app.program?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false)
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(app => app.status === statusFilter);
    }

    if (programmeFilter !== 'all') {
      filtered = filtered.filter(app => app.program?.name === programmeFilter);
    }

    setFilteredApplications(filtered);
  }, [applications, searchTerm, statusFilter, programmeFilter]);

  // Prepare chart data
  const statusData = [
    { name: 'Pending', value: applications.filter(a => a.status === 'pending').length, color: '#FFBB28' },
    { name: 'Under Review', value: applications.filter(a => a.status === 'under_review').length, color: '#0088FE' },
    { name: 'Accepted', value: applications.filter(a => a.status === 'accepted').length, color: '#00C49F' },
    { name: 'Rejected', value: applications.filter(a => a.status === 'rejected').length, color: '#FF8042' },
    { name: 'Waitlisted', value: applications.filter(a => a.status === 'waitlisted').length, color: '#8884D8' },
  ];

  const programmeData = applications.reduce((acc, app) => {
    const programmeName = app.program?.name || `Program ${app.programId}`;
    const existing = acc.find(item => item.programme === programmeName);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ programme: programmeName, count: 1 });
    }
    return acc;
  }, [] as { programme: string; count: number }[]);

  // Mock timeline data - in real app, this would come from analytics API
  const timelineData = [
    { month: 'Jan', applications: 45 },
    { month: 'Feb', applications: 52 },
    { month: 'Mar', applications: 38 },
    { month: 'Apr', applications: 61 },
    { month: 'May', applications: 55 },
    { month: 'Jun', applications: 67 },
  ];

  const handleStatusChange = async (applicationId: number, newStatus: string) => {
    // In a real app, this would call an API
    setApplications(prev =>
      prev.map(app =>
        app.id === applicationId ? { ...app, status: newStatus as any, updatedAt: new Date().toISOString() } : app
      )
    );
  };

  const getStatusBadgeStatus = (status: string) => {
    switch (status) {
      case 'pending': return 'pending';
      case 'under_review': return 'reviewed';
      case 'accepted': return 'approved';
      case 'rejected': return 'rejected';
      case 'waitlisted': return 'in_progress';
      default: return 'pending';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
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
              <p className="text-3xl font-bold">{applications.filter(a => a.status === 'pending').length}</p>
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
              <p className="text-3xl font-bold">{applications.filter(a => a.status === 'accepted').length}</p>
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
              <p className="text-3xl font-bold">{applications.filter(a => a.status === 'rejected').length}</p>
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
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="under_review">Under Review</SelectItem>
              <SelectItem value="accepted">Accepted</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
            </SelectContent>
          </Select>

          <Select value={programmeFilter} onValueChange={setProgrammeFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by programme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Programmes</SelectItem>
              {Array.from(new Set(applications.map(a => a.program?.name).filter(Boolean))).map(programme => (
                <SelectItem key={programme} value={programme!}>{programme}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-semibold">Applicant</th>
                <th className="text-left py-3 px-4 font-semibold">Programme</th>
                <th className="text-left py-3 px-4 font-semibold">Status</th>
                <th className="text-left py-3 px-4 font-semibold">Submitted</th>
                <th className="text-left py-3 px-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredApplications.map((application) => (
                <tr key={application.id} className="border-b hover:bg-muted/50">
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-semibold">{application.applicationNumber || `App-${application.id}`}</p>
                      <p className="text-sm text-muted-foreground">{application.applicantPhone || 'No phone'}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">{application.program?.name || `Program ${application.programId}`}</td>
                  <td className="py-3 px-4">
                    <StatusBadge status={getStatusBadgeStatus(application.status)} />
                  </td>
                  <td className="py-3 px-4 text-sm text-muted-foreground">
                    {application.submittedAt ? new Date(application.submittedAt).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">View</Button>
                      <Select
                        value={application.status}
                        onValueChange={(value) => handleStatusChange(application.id, value)}
                      >
                        <SelectTrigger className="w-32">
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