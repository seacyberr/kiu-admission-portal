import { useState } from "react";
import { Link } from "wouter";
import { Card, Button, Input, Label, Textarea } from "@/components/ui/shared";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowLeft, Search, User, Mail, Briefcase } from "lucide-react";

// Mock data - in production, fetch from API
interface Application {
  id: number;
  opportunityId: number;
  opportunityTitle: string;
  opportunityOrganization: string;
  userId: number;
  applicantName: string;
  applicantEmail: string;
  status: string;
  coverLetter: string;
  appliedAt: string;
  adminNotes: string;
}

const mockApplications: Application[] = [
  {
    id: 1,
    opportunityId: 1,
    opportunityTitle: "Software Developer Intern",
    opportunityOrganization: "Tech Solutions Ltd",
    userId: 5,
    applicantName: "John Doe",
    applicantEmail: "john.doe@kiu.ac.ug",
    status: "applied",
    coverLetter: "I am excited to apply for this position...",
    appliedAt: "2026-04-15T10:00:00Z",
    adminNotes: "",
  },
  {
    id: 2,
    opportunityId: 1,
    opportunityTitle: "Software Developer Intern",
    opportunityOrganization: "Tech Solutions Ltd",
    userId: 6,
    applicantName: "Jane Smith",
    applicantEmail: "jane.smith@kiu.ac.ug",
    status: "shortlisted",
    coverLetter: "Passionate about software development...",
    appliedAt: "2026-04-16T14:00:00Z",
    adminNotes: "Strong candidate, good grades",
  },
  {
    id: 3,
    opportunityId: 2,
    opportunityTitle: "Marketing Assistant",
    opportunityOrganization: "Brand Masters",
    userId: 7,
    applicantName: "Bob Wilson",
    applicantEmail: "bob.wilson@kiu.ac.ug",
    status: "interview_scheduled",
    coverLetter: "Creative marketer with internship experience...",
    appliedAt: "2026-04-17T09:00:00Z",
    adminNotes: "Interview scheduled for April 25",
  },
];

const STATUS_OPTIONS = [
  { value: "applied", label: "Applied" },
  { value: "reviewed", label: "Reviewed" },
  { value: "shortlisted", label: "Shortlisted" },
  { value: "interview_scheduled", label: "Interview Scheduled" },
  { value: "interviewed", label: "Interviewed" },
  { value: "placed", label: "Placed" },
  { value: "accepted", label: "Accepted" },
  { value: "rejected", label: "Rejected" },
];

const STATUS_COLORS: Record<string, string> = {
  applied: "bg-blue-100 text-blue-800",
  reviewed: "bg-indigo-100 text-indigo-800",
  shortlisted: "bg-yellow-100 text-yellow-800",
  interview_scheduled: "bg-orange-100 text-orange-800",
  interviewed: "bg-purple-100 text-purple-800",
  placed: "bg-green-100 text-green-800",
  accepted: "bg-green-200 text-green-900",
  rejected: "bg-red-100 text-red-800",
};

export default function CareerApplications() {
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterJob] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [newStatus, setNewStatus] = useState<string>("");
  const [adminNotes, setAdminNotes] = useState<string>("");

  const filteredApps = mockApplications.filter(app => {
    if (filterStatus && app.status !== filterStatus) return false;
    if (filterJob && app.opportunityId.toString() !== filterJob) return false;
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return (
        app.applicantName.toLowerCase().includes(search) ||
        app.applicantEmail.toLowerCase().includes(search) ||
        app.opportunityTitle.toLowerCase().includes(search)
      );
    }
    return true;
  });

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-UG', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const handleStatusUpdate = (appId: number) => {
    // In production, call API to update status
    console.log(`Updating app ${appId} to status ${newStatus} with notes: ${adminNotes}`);
    setSelectedApp(null);
    setNewStatus("");
    setAdminNotes("");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link href="/admin" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Admin Dashboard
        </Link>
        <h1 className="text-3xl font-display font-bold text-primary">Career Applications</h1>
        <p className="text-muted-foreground mt-2">Manage job and internship applications</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search by name, email, or job title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <select 
          value={filterStatus} 
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 border rounded-md"
        >
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Applications Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Applicant</TableHead>
              <TableHead>Opportunity</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Applied</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredApps.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                  No applications found
                </TableCell>
              </TableRow>
            ) : (
              filteredApps.map(app => (
                <TableRow key={app.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{app.applicantName}</p>
                        <p className="text-sm text-muted-foreground flex items-center gap-1">
                          <Mail className="w-3 h-3" /> {app.applicantEmail}
                        </p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{app.opportunityTitle}</p>
                        <p className="text-sm text-muted-foreground">{app.opportunityOrganization}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[app.status]}`}>
                      {STATUS_OPTIONS.find(o => o.value === app.status)?.label || app.status}
                    </span>
                  </TableCell>
                  <TableCell>{formatDate(app.appliedAt)}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setSelectedApp(app);
                          setNewStatus(app.status);
                          setAdminNotes(app.adminNotes);
                        }}
                      >
                        Review
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Review Modal */}
      {selectedApp && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold mb-4">Review Application</h2>
              
              <div className="space-y-4">
                <div>
                  <Label className="text-muted-foreground">Applicant</Label>
                  <p className="font-medium">{selectedApp.applicantName}</p>
                  <p className="text-sm text-muted-foreground">{selectedApp.applicantEmail}</p>
                </div>

                <div>
                  <Label className="text-muted-foreground">Opportunity</Label>
                  <p className="font-medium">{selectedApp.opportunityTitle}</p>
                  <p className="text-sm text-muted-foreground">{selectedApp.opportunityOrganization}</p>
                </div>

                <div>
                  <Label className="text-muted-foreground">Cover Letter</Label>
                  <p className="text-sm bg-muted p-3 rounded-md mt-1">{selectedApp.coverLetter}</p>
                </div>

                <div>
                  <Label>Update Status</Label>
                  <select 
                    value={newStatus} 
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="mt-1 px-3 py-2 border rounded-md w-full"
                  >
                    {STATUS_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <Label>Admin Notes</Label>
                  <Textarea
                    value={adminNotes}
                    onChange={(e) => setAdminNotes(e.target.value)}
                    placeholder="Add notes about this applicant..."
                    className="mt-1"
                    rows={3}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button onClick={() => handleStatusUpdate(selectedApp.id)}>
                    Update Status
                  </Button>
                  <Button variant="outline" onClick={() => setSelectedApp(null)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
