import { useEffect, useState, useCallback } from "react";
import {
  useListAdmissionApplications,
  useUpdateAdmissionStatus,
  type AdmissionApplication,
} from "@workspace/api-client-react";
import { Button, Card, Input, Label, Badge, Textarea } from "@/components/ui/shared";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Filter, 
  Download, 
  MoreHorizontal,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  User
} from "lucide-react";
import { format } from "date-fns";
import { useToast } from "@/hooks/use-toast";

const STATUSES = [
  { value: "pending", label: "Pending", color: "outline" },
  { value: "under_review", label: "Under Review", color: "warning" },
  { value: "accepted", label: "Accepted", color: "success" },
  { value: "rejected", label: "Rejected", color: "danger" },
  { value: "waitlisted", label: "Waitlisted", color: "outline" },
] as const;

const QUALIFICATION_TYPES = [
  { value: "all", label: "All Qualifications" },
  { value: "uace", label: "UACE (A-Level)" },
  { value: "uce", label: "UCE (O-Level)" },
  { value: "hec", label: "HEC" },
  { value: "national_certificate", label: "National Certificate" },
  { value: "diploma", label: "Diploma" },
  { value: "bachelors", label: "Bachelor's" },
  { value: "masters", label: "Master's" },
];

function statusVariant(s: string): "outline" | "danger" | "warning" | "success" {
  switch (s) {
    case "accepted":
      return "success";
    case "rejected":
      return "danger";
    case "under_review":
      return "warning";
    case "pending":
      return "outline";
    default:
      return "outline";
  }
}

interface ApplicationFilters {
  status: string;
  qualificationType: string;
  searchQuery: string;
  dateRange: string;
}

export default function AdminAdmissionsPage() {
  const { toast } = useToast();
  const { data: applicationsData, isLoading, refetch } = useListAdmissionApplications();
  const applications = applicationsData as AdmissionApplication[] | undefined;
  const mutation = useUpdateAdmissionStatus();
  
  // Filters
  const [filters, setFilters] = useState<ApplicationFilters>({
    status: "all",
    qualificationType: "all",
    searchQuery: "",
    dateRange: "all",
  });
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  
  // Detail view
  const [selectedApplication, setSelectedApplication] = useState<AdmissionApplication | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  
  // Stats
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    underReview: 0,
    accepted: 0,
    rejected: 0,
  });

  // Calculate stats
  useEffect(() => {
    if (applications) {
      setStats({
        total: applications.length,
        pending: applications.filter((a: AdmissionApplication) => a.status === "pending").length,
        underReview: applications.filter((a: AdmissionApplication) => a.status === "under_review").length,
        accepted: applications.filter((a: AdmissionApplication) => a.status === "accepted").length,
        rejected: applications.filter((a: AdmissionApplication) => a.status === "rejected").length,
      });
    }
  }, [applications]);

  // Filter applications
  const filteredApplications = useCallback(() => {
    if (!applications) return [];
    
    return applications.filter((app) => {
      // Status filter
      if (filters.status !== "all" && app.status !== filters.status) return false;
      
      // Qualification type filter (check examLevel)
      if (filters.qualificationType !== "all") {
        const qualMap: Record<string, string> = {
          uace: "a_level",
          uce: "o_level",
          hec: "hec",
          national_certificate: "national_certificate",
          diploma: "diploma",
          bachelors: "bachelors",
          masters: "masters",
        };
        if (app.examLevel !== qualMap[filters.qualificationType]) return false;
      }
      
      // Search filter
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        const searchFields = [
          app.applicationNumber,
          app.applicantName,
          app.applicantEmail,
          app.program?.name,
        ].filter(Boolean);
        
        if (!searchFields.some((field) => field?.toLowerCase().includes(query))) {
          return false;
        }
      }
      
      return true;
    });
  }, [applications, filters])();

  // Paginate
  const totalPages = Math.ceil(filteredApplications.length / itemsPerPage);
  const paginatedApplications = filteredApplications.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Export to CSV
  const exportToCSV = () => {
    const headers = [
      "Application Number",
      "Applicant Name",
      "Email",
      "Phone",
      "Program",
      "Qualification Type",
      "Status",
      "Date Submitted",
      "Admin Notes",
    ];
    
    const rows = filteredApplications.map((app: AdmissionApplication) => [
      app.applicationNumber,
      app.applicantName,
      app.applicantEmail,
      app.applicantPhone,
      app.program?.name,
      app.examLevel,
      app.status,
      format(new Date(app.createdAt || new Date()), "yyyy-MM-dd"),
      app.adminNotes || "",
    ]);
    
    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `admissions-export-${format(new Date(), "yyyy-MM-dd")}.csv`;
    link.click();
    
    toast({ title: "Export Complete", description: `${filteredApplications.length} applications exported` });
  };

  // Bulk status update (reserved for future use)
  const _handleBulkAction = async (action: string, applicationIds: number[]) => {
    // Implementation for bulk actions
    toast({ title: "Bulk Action", description: `${action} on ${applicationIds.length} applications` });
  };

  // View application details
  const viewApplicationDetails = (app: AdmissionApplication) => {
    setSelectedApplication(app);
    setIsDetailOpen(true);
  };

  // Update status
  const updateStatus = async (id: number, newStatus: string) => {
    mutation.mutate(
      { id, data: { status: newStatus } },
      {
        onSuccess: () => {
          toast({ title: "Status Updated", description: `Application ${newStatus}` });
          refetch();
        },
      }
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admission Applications</h1>
          <p className="text-muted-foreground">Review and manage student applications</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportToCSV}>
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={() => refetch()}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <div className="text-2xl font-bold">{stats.total}</div>
          <div className="text-sm text-muted-foreground">Total Applications</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
          <div className="text-sm text-muted-foreground">Pending</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-blue-600">{stats.underReview}</div>
          <div className="text-sm text-muted-foreground">Under Review</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-green-600">{stats.accepted}</div>
          <div className="text-sm text-muted-foreground">Accepted</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
          <div className="text-sm text-muted-foreground">Rejected</div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <Label>Search</Label>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, email, or application number..."
                value={filters.searchQuery}
                onChange={(e) => setFilters({ ...filters, searchQuery: e.target.value })}
                className="pl-8"
              />
            </div>
          </div>
          
          <div>
            <Label>Status</Label>
            <Select
              value={filters.status}
              onValueChange={(value: string) => setFilters({ ...filters, status: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {STATUSES.map((s) => (
                  <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>Qualification</Label>
            <Select
              value={filters.qualificationType}
              onValueChange={(value: string) => setFilters({ ...filters, qualificationType: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Qualifications" />
              </SelectTrigger>
              <SelectContent>
                {QUALIFICATION_TYPES.map((q) => (
                  <SelectItem key={q.value} value={q.value}>{q.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <Button 
            variant="outline" 
            onClick={() => setFilters({ status: "all", qualificationType: "all", searchQuery: "", dateRange: "all" })}
          >
            <Filter className="w-4 h-4 mr-2" />
            Clear Filters
          </Button>
        </div>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {paginatedApplications.length} of {filteredApplications.length} applications
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <span className="text-sm">
            Page {currentPage} of {totalPages || 1}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages || totalPages === 0}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Applications Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Application #</TableHead>
              <TableHead>Applicant</TableHead>
              <TableHead>Program</TableHead>
              <TableHead>Qualification</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8">
                  Loading applications...
                </TableCell>
              </TableRow>
            ) : paginatedApplications.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No applications found matching your filters
                </TableCell>
              </TableRow>
            ) : (
              paginatedApplications.map((app) => (
                <TableRow key={app.id}>
                  <TableCell className="font-mono text-xs whitespace-nowrap">
                    {app.applicationNumber}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{app.applicantName ?? "—"}</div>
                    <div className="text-xs text-muted-foreground">{app.applicantEmail}</div>
                  </TableCell>
                  <TableCell className="max-w-[200px]">
                    <div className="text-sm truncate">{app.program?.name ?? "—"}</div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{app.examLevel?.replace(/_/g, " ")}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusVariant(app.status)}>
                      {STATUSES.find((s) => s.value === app.status)?.label || app.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    {app.createdAt ? format(new Date(app.createdAt), "MMM d, yyyy") : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => viewApplicationDetails(app)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => updateStatus(app.id, "under_review")}>
                            <Clock className="w-4 h-4 mr-2" />
                            Mark Under Review
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => updateStatus(app.id, "accepted")}>
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Accept
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => updateStatus(app.id, "rejected")}>
                            <XCircle className="w-4 h-4 mr-2" />
                            Reject
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Application Detail Dialog */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          {selectedApplication && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Application {selectedApplication.applicationNumber}
                </DialogTitle>
                <DialogDescription>
                  Submitted on {selectedApplication.createdAt ? format(new Date(selectedApplication.createdAt), "MMMM d, yyyy 'at' h:mm a") : 'N/A'}
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-6 mt-4">
                {/* Applicant Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Applicant Name</Label>
                    <div className="font-medium">{selectedApplication.applicantName}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Email</Label>
                    <div className="font-medium">{selectedApplication.applicantEmail}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Phone</Label>
                    <div className="font-medium">{selectedApplication.applicantPhone || "—"}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Qualification Type</Label>
                    <Badge variant="outline">{selectedApplication.examLevel?.replace(/_/g, " ")}</Badge>
                  </div>
                </div>

                {/* Program Info */}
                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-2">Program Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-muted-foreground">Selected Program</Label>
                      <div className="font-medium">{selectedApplication.program?.name}</div>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Faculty</Label>
                      <div className="font-medium">{selectedApplication.program?.faculty}</div>
                    </div>
                  </div>
                </div>

                {/* Status & Actions */}
                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-2">Application Status</h3>
                  <div className="flex items-center gap-4 mb-4">
                    <Badge variant={statusVariant(selectedApplication.status)} className="text-lg px-4 py-1">
                      {STATUSES.find((s) => s.value === selectedApplication.status)?.label}
                    </Badge>
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => updateStatus(selectedApplication.id, "under_review")}
                      >
                        <Clock className="w-4 h-4 mr-1" />
                        Under Review
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        className="bg-green-600 text-white hover:bg-green-700"
                        onClick={() => updateStatus(selectedApplication.id, "accepted")}
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Accept
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive"
                        onClick={() => updateStatus(selectedApplication.id, "rejected")}
                      >
                        <XCircle className="w-4 h-4 mr-1" />
                        Reject
                      </Button>
                    </div>
                  </div>

                  {/* Admin Notes */}
                  <div>
                    <Label htmlFor="admin-notes">Admin Notes</Label>
                    <Textarea
                      id="admin-notes"
                      placeholder="Add notes about this application..."
                      defaultValue={selectedApplication.adminNotes || ""}
                      className="mt-1"
                    />
                    <Button 
                      size="sm" 
                      className="mt-2"
                      onClick={() => {
                        const notes = (document.getElementById("admin-notes") as HTMLTextAreaElement)?.value;
                        mutation.mutate(
                          { id: selectedApplication.id, data: { adminNotes: notes, status: selectedApplication.status } },
                          { onSuccess: () => toast({ title: "Notes saved" }) }
                        );
                      }}
                    >
                      Save Notes
                    </Button>
                  </div>
                </div>

                {/* Documents */}
                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Documents
                  </h3>
                  {selectedApplication.documents && selectedApplication.documents.length > 0 ? (
                    <div className="space-y-2">
                      {selectedApplication.documents.map((doc, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 border rounded">
                          <span className="text-sm">{doc.documentType}</span>
                          <a
                            href={doc.fileUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-2 py-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </a>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground text-sm">No documents uploaded</p>
                  )}
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
