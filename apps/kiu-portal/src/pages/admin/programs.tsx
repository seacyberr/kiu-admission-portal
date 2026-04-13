import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { BookOpen, Search, RefreshCw, Plus } from "lucide-react";
import { toast } from "sonner";

interface Program {
  id: number;
  name: string;
  category: string;
  description?: string;
  duration?: string;
  fees_local_per_semester: number;
  fees_international_per_semester?: number;
  functional_fees_local?: number;
  functional_fees_international?: number;
  is_active: boolean;
  created_at: string;
}

interface ProgramsResponse {
  programs: Program[];
}

export default function AdminProgramsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");

  const { data, isLoading, error, refetch } = useQuery<ProgramsResponse>({
    queryKey: ["admin-programs", searchTerm, categoryFilter],
    queryFn: async () => {
      return api.get<ProgramsResponse>("/admin/programs");
    },
  });

  useEffect(() => {
    if (error) {
      toast.error("Failed to load programs");
    }
  }, [error]);

  const filteredPrograms = data?.programs?.filter((program) => {
    const matchesSearch =
      program.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      program.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter
      ? program.category === categoryFilter
      : true;
    return matchesSearch && matchesCategory;
  });

  const getCategoryBadgeColor = (category: string) => {
    switch (category?.toLowerCase()) {
      case "certificate":
        return "secondary";
      case "diploma":
        return "default";
      case "bachelors":
        return "default";
      case "masters":
        return "secondary";
      case "phd":
        return "destructive";
      default:
        return "outline";
    }
  };

  const categories = [
    ...new Set(data?.programs?.map((p) => p.category) || []),
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Programs Management</h1>
          <p className="text-muted-foreground">
            Manage academic programs and their details
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => refetch()} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Program
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            All Programs ({filteredPrograms?.length || 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search programs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>
            {categories.length > 0 && (
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="border rounded px-3 py-2"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            )}
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Program Name</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Local Fees</TableHead>
                  <TableHead>International Fees</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredPrograms?.map((program) => (
                  <TableRow key={program.id}>
                    <TableCell className="font-medium">{program.name}</TableCell>
                    <TableCell>
                      <Badge variant={getCategoryBadgeColor(program.category)}>
                        {program.category}
                      </Badge>
                    </TableCell>
                    <TableCell>{program.duration || "-"}</TableCell>
                    <TableCell>
                      {program.fees_local_per_semester
                        ? `UGX ${program.fees_local_per_semester.toLocaleString()}`
                        : "-"}
                    </TableCell>
                    <TableCell>
                      {program.fees_international_per_semester
                        ? `$${program.fees_international_per_semester.toLocaleString()}`
                        : "-"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={program.is_active ? "default" : "destructive"}
                      >
                        {program.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {!isLoading && filteredPrograms?.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No programs found matching your criteria
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
