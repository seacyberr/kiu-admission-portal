import { useEffect, useState } from "react";
import { Link } from "wouter";
import {
  useListAdmissionApplications,
  useUpdateAdmissionStatus,
  type AdmissionApplication,
} from "@workspace/api-client-react";
import { Button, Card, Input, Label, Badge, Textarea } from "@/components/ui/shared";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, ChevronLeft, ChevronRight, Search } from "lucide-react";
import { format } from "date-fns";
import { useToast } from "@/hooks/use-toast";

const STATUSES = [
  "pending",
  "under_review",
  "accepted",
  "rejected",
  "waitlisted",
] as const;

function statusVariant(s: string): "default" | "success" | "warning" | "danger" | "outline" {
  switch (s) {
    case "accepted":
      return "success";
    case "rejected":
      return "danger";
    case "under_review":
      return "warning";
    default:
      return "outline";
  }
}

function ApplicationRow({ app }: { app: AdmissionApplication }) {
  const { toast } = useToast();
  const mutation = useUpdateAdmissionStatus();
  const [status, setStatus] = useState(app.status);
  const [notes, setNotes] = useState(app.adminNotes ?? "");
  const [selectedProgram, setSelectedProgram] = useState(app.programId);

  useEffect(() => {
    setStatus(app.status);
    setNotes(app.adminNotes ?? "");
  }, [app.id, app.status, app.adminNotes]);

  const dirty = status !== app.status || (notes || "") !== (app.adminNotes ?? "") || selectedProgram !== app.programId;

  const save = () => {
    mutation.mutate(
      { id: app.id, data: { status, adminNotes: notes || undefined, programId: selectedProgram } },
      {
        onSuccess: () =>
          toast({ title: "Saved", description: `Application ${app.applicationNumber} updated.` }),
        onError: (e: Error) =>
          toast({
            title: "Update failed",
            description: e.message,
            variant: "destructive",
          }),
      },
    );
  };

  // Get program choices from the application
  const programChoices = (app as any).programChoices || [];
  const primaryProgram = app.program;

  return (
    <TableRow>
      <TableCell className="font-mono text-xs whitespace-nowrap">{app.applicationNumber}</TableCell>
      <TableCell>
        <div className="font-medium">{app.applicantName ?? "—"}</div>
        <div className="text-xs text-muted-foreground">{app.applicantEmail}</div>
      </TableCell>
      <TableCell className="max-w-[300px]">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-primary">1st:</span>
            <span className={`text-sm truncate ${selectedProgram === primaryProgram?.id ? "font-semibold" : ""}`}>
              {primaryProgram?.name ?? "—"}
            </span>
          </div>
          {programChoices.length > 1 && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">2nd:</span>
              <span className={`text-xs truncate ${selectedProgram === programChoices[1]?.id ? "font-semibold" : "text-muted-foreground"}`}>
                {programChoices[1]?.name || `Program #${programChoices[1]}`}
              </span>
            </div>
          )}
          {programChoices.length > 2 && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">3rd:</span>
              <span className={`text-xs truncate ${selectedProgram === programChoices[2]?.id ? "font-semibold" : "text-muted-foreground"}`}>
                {programChoices[2]?.name || `Program #${programChoices[2]}`}
              </span>
            </div>
          )}
        </div>
      </TableCell>
      <TableCell>
        <Badge variant={statusVariant(status)}>{status.replace("_", " ")}</Badge>
      </TableCell>
      <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
        {app.submittedAt
          ? format(new Date(app.submittedAt), "MMM d, yyyy")
          : "—"}
      </TableCell>
      <TableCell>
        <div className="space-y-2 min-w-[200px]">
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full h-9 rounded-lg border border-border bg-background px-2 text-sm"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.replace("_", " ")}
              </option>
            ))}
          </select>
          {programChoices.length > 1 && (
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Assign Program:</Label>
              <select
                value={selectedProgram}
                onChange={(e) => setSelectedProgram(Number(e.target.value))}
                className="w-full h-9 rounded-lg border border-border bg-background px-2 text-sm"
              >
                <option value={primaryProgram?.id}>
                  1st: {primaryProgram?.name}
                </option>
                {programChoices.length > 1 && programChoices[1]?.id && (
                  <option value={programChoices[1].id}>
                    2nd: {programChoices[1].name || `Program #${programChoices[1].id}`}
                  </option>
                )}
                {programChoices.length > 2 && programChoices[2]?.id && (
                  <option value={programChoices[2].id}>
                    3rd: {programChoices[2].name || `Program #${programChoices[2].id}`}
                  </option>
                )}
              </select>
            </div>
          )}
          <Textarea
            placeholder="Admin notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="min-h-[72px] text-xs"
          />
          <Button
            size="sm"
            variant="secondary"
            isLoading={mutation.isPending}
            disabled={!dirty}
            onClick={save}
          >
            Save
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

export default function AdminAdmissions() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");

  const { data, isLoading, error } = useListAdmissionApplications({
    filters: {
      page,
      perPage: 15,
      ...(statusFilter ? { status: statusFilter } : {}),
      ...(search ? { search } : {}),
    },
  });

  const applySearch = () => {
    setSearch(searchInput.trim());
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <Link
        href="/admin"
        className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to overview
      </Link>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-destructive/10 text-destructive text-sm border border-destructive/20">
          {(error as Error).message}
        </div>
      )}

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-primary">Admissions</h1>
          <p className="text-muted-foreground mt-1">Review and update application status</p>
        </div>
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <Label className="mb-1 block">Status</Label>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="h-10 rounded-lg border border-border bg-background px-3 text-sm min-w-[160px]"
            >
              <option value="">All</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="Search name, email, app #"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && applySearch()}
              className="w-[220px]"
            />
            <Button type="button" variant="secondary" onClick={applySearch}>
              <Search className="w-4 h-4 mr-1" /> Search
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                const params = new URLSearchParams();
                if (statusFilter) params.set("status", statusFilter);
                const url = `/api/reports/applications?format=csv${params.toString() ? `&${params.toString()}` : ""}`;
                window.open(url, "_blank");
              }}
            >
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      <Card className="p-0 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-muted-foreground">Loading applications…</div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Application</TableHead>
                  <TableHead>Applicant</TableHead>
                  <TableHead>Program</TableHead>
                  <TableHead>Current</TableHead>
                  <TableHead>Submitted</TableHead>
                  <TableHead className="w-[280px]">Update</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.applications?.length ? (
                  data.applications.map((app: AdmissionApplication) => (
                    <ApplicationRow key={app.id} app={app} />
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-10 text-muted-foreground">
                      No applications match your filters.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
            {data && data.pages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-border text-sm">
                <span className="text-muted-foreground">
                  Page {data.page} of {data.pages} ({data.total} total)
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= data.pages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
}
