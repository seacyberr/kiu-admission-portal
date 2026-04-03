import { useState } from "react";
import { Link } from "wouter";
import {
  useListOpportunities,
  useCreateOpportunity,
  useUpdateOpportunity,
  useDeleteOpportunity,
} from "@workspace/api-client-react";
import { Button, Card, Input, Label, Textarea, Badge } from "@/components/ui/shared";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, Plus, Trash2, ToggleLeft, ToggleRight } from "lucide-react";
import { format } from "date-fns";
import { useToast } from "@/hooks/use-toast";

export default function AdminOpportunities() {
  const { toast } = useToast();
  const { data, isLoading } = useListOpportunities();
  const createMut = useCreateOpportunity();
  const updateMut = useUpdateOpportunity();
  const deleteMut = useDeleteOpportunity();

  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [organization, setOrganization] = useState("");
  const [type, setType] = useState("job");
  const [description, setDescription] = useState("");
  const [requirements, setRequirements] = useState("");
  const [applicationDeadline, setApplicationDeadline] = useState("");
  const [location, setLocation] = useState("");
  const [contactEmail, setContactEmail] = useState("");

  const resetForm = () => {
    setTitle("");
    setOrganization("");
    setType("job");
    setDescription("");
    setRequirements("");
    setApplicationDeadline("");
    setLocation("");
    setContactEmail("");
  };

  const submitCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !organization.trim() || !description.trim() || !requirements.trim() || !applicationDeadline) {
      toast({ title: "Missing fields", description: "Fill all required fields.", variant: "destructive" });
      return;
    }
    createMut.mutate(
      {
        data: {
          title: title.trim(),
          organization: organization.trim(),
          type,
          description: description.trim(),
          requirements: requirements.trim(),
          applicationDeadline,
          location: location.trim() || undefined,
          contactEmail: contactEmail.trim() || undefined,
          isActive: true,
        },
      },
      {
        onSuccess: () => {
          toast({ title: "Opportunity created" });
          resetForm();
          setShowForm(false);
        },
        onError: (err: Error) =>
          toast({ title: "Failed", description: err.message, variant: "destructive" }),
      },
    );
  };

  const toggleActive = (id: number, isActive: boolean) => {
    updateMut.mutate(
      { id, data: { isActive: !isActive } },
      {
        onError: (err: Error) =>
          toast({ title: "Update failed", description: err.message, variant: "destructive" }),
      },
    );
  };

  const remove = (id: number, titleStr: string) => {
    if (!window.confirm(`Delete “${titleStr}”? This cannot be undone.`)) return;
    deleteMut.mutate(
      { id },
      {
        onSuccess: () => toast({ title: "Deleted" }),
        onError: (err: Error) =>
          toast({ title: "Delete failed", description: err.message, variant: "destructive" }),
      },
    );
  };

  const opps = data?.opportunities ?? [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <Link
        href="/admin"
        className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to overview
      </Link>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-primary">Opportunities</h1>
          <p className="text-muted-foreground mt-1">Jobs and internships for finalists</p>
        </div>
        <Button onClick={() => setShowForm((s) => !s)} variant={showForm ? "secondary" : "accent"}>
          <Plus className="w-4 h-4 mr-2" />
          {showForm ? "Hide form" : "New opportunity"}
        </Button>
      </div>

      {showForm && (
        <Card className="p-6 mb-8 border-accent/30">
          <h2 className="text-lg font-bold mb-4">Create opportunity</h2>
          <form onSubmit={submitCreate} className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2 md:col-span-2">
              <Label>Title</Label>
              <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label>Organization</Label>
              <Input value={organization} onChange={(e) => setOrganization(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full h-12 rounded-xl border-2 border-border/60 bg-background px-4 text-sm"
              >
                <option value="job">Job</option>
                <option value="internship">Internship</option>
              </select>
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label>Description</Label>
              <Textarea value={description} onChange={(e) => setDescription(e.target.value)} required />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label>Requirements</Label>
              <Textarea value={requirements} onChange={(e) => setRequirements(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label>Application deadline</Label>
              <Input
                type="date"
                value={applicationDeadline}
                onChange={(e) => setApplicationDeadline(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Location (optional)</Label>
              <Input value={location} onChange={(e) => setLocation(e.target.value)} />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label>Contact email (optional)</Label>
              <Input type="email" value={contactEmail} onChange={(e) => setContactEmail(e.target.value)} />
            </div>
            <div className="md:col-span-2 flex gap-3">
              <Button type="submit" isLoading={createMut.isPending}>
                Publish
              </Button>
              <Button type="button" variant="outline" onClick={() => { resetForm(); setShowForm(false); }}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      <Card className="p-0 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-muted-foreground">Loading…</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Role</TableHead>
                <TableHead>Organization</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Deadline</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {opps.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-10 text-muted-foreground">
                    No opportunities yet. Create one above.
                  </TableCell>
                </TableRow>
              ) : (
                opps.map((o: any) => (
                  <TableRow key={o.id}>
                    <TableCell className="font-medium max-w-[200px]">{o.title}</TableCell>
                    <TableCell>{o.organization}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{o.type}</Badge>
                    </TableCell>
                    <TableCell className="text-sm whitespace-nowrap">
                      {o.applicationDeadline
                        ? format(new Date(o.applicationDeadline), "MMM d, yyyy")
                        : "—"}
                    </TableCell>
                    <TableCell>
                      {o.isActive ? (
                        <Badge variant="success">Active</Badge>
                      ) : (
                        <Badge variant="danger">Inactive</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          title={o.isActive ? "Deactivate" : "Activate"}
                          onClick={() => toggleActive(o.id, o.isActive)}
                          disabled={updateMut.isPending}
                        >
                          {o.isActive ? (
                            <ToggleRight className="w-5 h-5 text-success" />
                          ) : (
                            <ToggleLeft className="w-5 h-5 text-muted-foreground" />
                          )}
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-destructive"
                          onClick={() => remove(o.id, o.title)}
                          disabled={deleteMut.isPending}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
