/**
 * recommend-hec.tsx — Higher Education Certificate Progression Recommendation
 *
 * Specialized recommendation tool for HEC holders that shows all possible
 * progression pathways: Direct Degree Entry, Diploma Pathways, and Alternative Programs
 *
 * Route: /recommend/hec
 * Backend: POST /api/admission/recommend/hec
 */

import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useRecommendPrograms } from "@workspace/api-client-react";
import { Button, Card, Badge, Input, Label } from "@/components/ui/shared";
import {
  ArrowLeft,
  ArrowRight,
  Sparkles,
  Info,
  CheckCircle,
  AlertCircle,
  BookOpen,
  DollarSign,
  Clock,
  GraduationCap,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Award,
  Zap,
  ArrowUpRight,
  Calendar,
  ShieldCheck,
  Upload,
  Building,
  FileText
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

import type {
  RecommendedProgram,
  RecommendResult
} from "@workspace/api-client-react";

// ── Helpers ───────────────────────────────────────────────────────────────────

function ncheStatusBadge(status: string) {
  if (status === "compliant")
    return <Badge variant="success" className="text-xs">NCHE Compliant</Badge>;
  return <Badge variant="warning" className="text-xs">Conditional</Badge>;
}

function matchBar(pct: number) {
  const color =
    pct >= 75 ? "bg-green-500" : pct >= 50 ? "bg-amber-400" : "bg-slate-300";
  return (
    <div className="w-full bg-secondary rounded-full h-2">
      <div
        className={`h-2 rounded-full ${color} transition-all`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function formatFee(amount: number | null | undefined, currency: string) {
  if (!amount) return "Contact admissions";
  return `${currency} ${amount.toLocaleString()}`;
}

// ── Path Badge Component ──────────────────────────────────────────────────────

function PathBadge({ type }: { type: string }) {
  const config = {
    direct: { label: "Direct Degree Entry", variant: "success", icon: <ShieldCheck className="w-3 h-3" /> },
    progression: { label: "Progression Path", variant: "info", icon: <ArrowUpRight className="w-3 h-3" /> },
    bridge: { label: "Diploma Bridge", variant: "warning", icon: <Zap className="w-3 h-3" /> },
    alternative: { label: "Alternative Option", variant: "outline", icon: <ArrowRight className="w-3 h-3" /> }
  }[type] || { label: type, variant: "outline", icon: <Info className="w-3 h-3" /> };

  return (
    <Badge variant={config.variant as any} className="text-xs flex items-center gap-1">
      {config.icon} {config.label}
    </Badge>
  );
}

// ── ProgramCard Component ─────────────────────────────────────────────────────

function ProgramCard({
  program,
  onApply,
}: {
  program: RecommendedProgram & { pathType?: string; pathExplanation?: string; creditExemptions?: string; entryYear?: number };
  onApply: (id: number, name: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="p-6 hover:shadow-lg transition-all border-border">
      {/* Top row */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h3 className="font-bold text-lg leading-tight truncate">{program.name}</h3>
            {ncheStatusBadge(program.ncheStatus)}
            {program.pathType && <PathBadge type={program.pathType} />}
          </div>
          <p className="text-sm text-muted-foreground truncate">
            {program.faculty}
            {program.department ? ` · ${program.department}` : ""}
          </p>
          <div className="flex flex-wrap gap-2 mt-2">
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-medium
              ${
                program.campus === "kampala"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-green-100 text-green-700"
              }`}
            >
              {program.campus === "kampala"
                ? "Kampala (Kansanga)"
                : "Western (Ishaka)"}
            </span>
            {program.duration && (
              <span className="text-[10px] px-2 py-0.5 rounded-full font-medium bg-secondary text-muted-foreground flex items-center gap-1 truncate">
                <Clock className="w-3 h-3 shrink-0" />
                {program.duration}
              </span>
            )}
            {program.entryYear && (
              <span className="text-[10px] px-2 py-0.5 rounded-full font-medium bg-primary/10 text-primary flex items-center gap-1 truncate">
                <Calendar className="w-3 h-3 shrink-0" />
                Starts Year {program.entryYear}
              </span>
            )}
          </div>
        </div>

        {/* Match score ring */}
        <div className="shrink-0 flex flex-col items-center">
          <div
            className={`w-14 h-14 rounded-full flex items-center justify-center border-4 font-bold text-sm
            ${
              program.matchPercentage >= 75
                ? "border-green-500 text-green-700 bg-green-50"
                : program.matchPercentage >= 50
                ? "border-amber-400 text-amber-700 bg-amber-50"
                : "border-slate-300 text-slate-600 bg-slate-50"
            }`}
          >
            {program.matchPercentage}%
          </div>
          <span className="text-[10px] text-muted-foreground mt-1 text-center">
            Match<br />Score
          </span>
        </div>
      </div>

      {/* Path explanation */}
      {program.pathExplanation && (
        <div className="mb-4 p-3 rounded-lg bg-blue-50 border border-blue-200">
          <p className="text-xs text-blue-700">{program.pathExplanation}</p>
        </div>
      )}

      {/* Match bar */}
      <div className="mb-4">
        {matchBar(program.matchPercentage)}
        {program.matchedSubjects.length > 0 && (
          <p className="text-xs text-muted-foreground mt-1 truncate">
            Matched:{" "}
            <span className="font-medium text-primary">
              {program.matchedSubjects.join(", ")}
            </span>
          </p>
        )}
      </div>

      {/* Credits / Exemptions */}
      {program.creditExemptions && (
        <div className="mb-4 p-3 rounded-lg bg-green-50 border border-green-200">
          <div className="flex items-start gap-2">
            <Award className="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-semibold text-green-800">Credit Exemptions</p>
              <p className="text-xs text-green-700">{program.creditExemptions}</p>
            </div>
          </div>
        </div>
      )}

      {/* Warnings */}
      {program.programWarnings.length > 0 && (
        <div className="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-200 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <ul className="text-xs text-amber-700 space-y-0.5">
            {program.programWarnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Fees row */}
      <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-secondary/50 rounded-xl">
        <div className="min-w-0">
          <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
            <DollarSign className="w-3 h-3 shrink-0" /> Local Tuition
          </p>
          <p className="font-bold text-sm text-primary truncate">
            {formatFee(program.feesLocal, "UGX")}
          </p>
        </div>
        <div className="min-w-0">
          <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
            <DollarSign className="w-3 h-3 shrink-0" /> Int'l Tuition
          </p>
          <p className="font-bold text-sm truncate">
            {formatFee(program.feesInternational, "USD")}
          </p>
        </div>
      </div>

      {/* Expandable details */}
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/80 mb-3"
      >
        {expanded ? (
          <>
            <ChevronUp className="w-3.5 h-3.5" /> Hide details
          </>
        ) : (
          <>
            <ChevronDown className="w-3.5 h-3.5" /> View entry requirements &
            description
          </>
        )}
      </button>

      {expanded && (
        <div className="space-y-3 mb-4 text-sm">
          {program.entryRequirements && (
            <div className="p-3 bg-primary/5 rounded-lg">
              <p className="font-semibold text-xs uppercase tracking-wider text-primary mb-1">
                Entry Requirements
              </p>
              <p className="text-muted-foreground leading-relaxed break-words">
                {program.entryRequirements}
              </p>
            </div>
          )}
          {program.description && (
            <div className="p-3 bg-secondary/50 rounded-lg">
              <p className="font-semibold text-xs uppercase tracking-wider text-muted-foreground mb-1">
                About This Program
              </p>
              <p className="text-muted-foreground leading-relaxed break-words">
                {program.description}
              </p>
            </div>
          )}
        </div>
      )}

      {/* CTA */}
      <Button
        className="w-full gap-2"
        onClick={() => onApply(program.id, program.name)}
      >
        <GraduationCap className="w-4 h-4" />
        Apply for This Program
      </Button>
    </Card>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export default function RecommendHEC() {
  const [, setLocation] = useLocation();
  const recommendMutation = useRecommendPrograms();

  const [institutionName, setInstitutionName] = useState<string>("");
  const [certificateYear, setCertificateYear] = useState<string>("");
  const [hecQualification, setHecQualification] = useState<string>("");
  const [hecGrade, setHecGrade] = useState<string>("");
  const [certificateFile, setCertificateFile] = useState<File | null>(null);
  const [campus, setCampus] = useState<"" | "kampala" | "western">("");
  const [result, setResult] = useState<RecommendResult | null>(null);

  const HEC_QUALIFICATIONS = [
    "Higher Education Certificate (HEC)",
    "Certificate in Business Administration",
    "Certificate in Information Technology",
    "Certificate in Public Administration",
    "Certificate in Nursing",
    "Certificate in Education",
    "Certificate in Law",
    "Other Certificate Qualification"
  ];

  const HEC_GRADES = [
    { label: "Distinction", value: "distinction", points: 3 },
    { label: "Credit", value: "credit", points: 2 },
    { label: "Pass", value: "pass", points: 1 },
    { label: "Fail", value: "fail", points: 0 }
  ];

  const isValid = hecQualification !== "" && hecGrade !== "" && institutionName !== "" && certificateYear !== "";

  // ── Submit ───────────────────────────────────────────────────────────────

  const handleGetRecommendations = () => {
    recommendMutation.mutate(
      {
        qualificationType: "hec",
        qualification: hecQualification,
        grade: hecGrade,
        institution: institutionName,
        year: certificateYear,
        campus: campus || undefined
      },
      {
        onSuccess: (data: RecommendResult) => {
          setResult(data);
          setTimeout(() => {
            document
              .getElementById("results-section")
              ?.scrollIntoView({ behavior: "smooth" });
          }, 100);
        },
      }
    );
  };

  // ── Apply handler ────────────────────────────────────────────────────────

  const handleApply = (programId: number, programName: string) => {
    sessionStorage.setItem("recommended_program_id", String(programId));
    sessionStorage.setItem("recommended_program_name", programName);
    setLocation("/apply");
  };

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-10">
        <Link
          href="/apply"
          className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Link>
        <div className="flex items-center gap-3 mb-3">
          <div className="w-12 h-12 rounded-2xl bg-accent/10 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-accent" />
          </div>
          <div>
            <h1 className="text-3xl font-display font-bold text-primary">
              HEC Progression Advisor
            </h1>
            <p className="text-muted-foreground">
              Find all possible pathways from your Higher Education Certificate
            </p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Input Panel ──────────────────────────────────────────────── */}
        <div className="lg:col-span-1 space-y-6 min-w-0">
          <Card className="p-6">
            <h2 className="font-bold text-lg mb-1">Your HEC Certificate Details</h2>
            <p className="text-xs text-muted-foreground mb-5">
              Enter your certificate details to see all available progression paths
            </p>

            {/* Official UHEQF Progression */}
            <div className="mb-5 p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex items-center gap-2 mb-3">
                <GraduationCap className="w-4 h-4 text-slate-700" />
                <p className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  UHEQF Progression Pathways
                </p>
              </div>
              <div className="grid grid-cols-1 gap-2">
                <div className="p-2 rounded-lg bg-blue-50 border border-blue-200">
                  <p className="text-xs font-bold text-blue-800">✅ Direct Degree Entry</p>
                  <p className="text-xs text-blue-700">With Distinction / Credit</p>
                </div>
                <div className="p-2 rounded-lg bg-amber-50 border border-amber-200">
                  <p className="text-xs font-bold text-amber-800">✅ Diploma Pathway</p>
                  <p className="text-xs text-amber-700">1 year → Advanced standing</p>
                </div>
                <div className="p-2 rounded-lg bg-green-50 border border-green-200">
                  <p className="text-xs font-bold text-green-800">✅ Direct Diploma Entry</p>
                  <p className="text-xs text-green-700">All grades accepted</p>
                </div>
              </div>
            </div>

            {/* Institution */}
            <div className="mb-4">
              <Label htmlFor="institution">
                <Building className="w-3 h-3 inline mr-1" />
                Institution / University <span className="text-destructive">*</span>
              </Label>
              <Input
                id="institution"
                type="text"
                value={institutionName}
                onChange={(e) => setInstitutionName(e.target.value)}
                placeholder="Enter institution name"
                className="h-9 mt-1"
              />
            </div>

            {/* Year */}
            <div className="mb-4">
              <Label htmlFor="year">
                <Calendar className="w-3 h-3 inline mr-1" />
                Year Awarded <span className="text-destructive">*</span>
              </Label>
              <Input
                id="year"
                type="number"
                min="2000"
                max="2030"
                value={certificateYear}
                onChange={(e) => setCertificateYear(e.target.value)}
                placeholder="Year certificate was awarded"
                className="h-9 mt-1"
              />
            </div>

            {/* Qualification Selection */}
            <div className="mb-4">
              <Label htmlFor="qualification">
                <FileText className="w-3 h-3 inline mr-1" />
                HEC Qualification <span className="text-destructive">*</span>
              </Label>
              <select
                id="qualification"
                value={hecQualification}
                onChange={(e) => setHecQualification(e.target.value)}
                className="w-full h-9 px-3 mt-1 rounded-lg border border-border bg-white text-sm"
              >
                <option value="">Select qualification…</option>
                {HEC_QUALIFICATIONS.map((q) => (
                  <option key={q} value={q}>{q}</option>
                ))}
              </select>
            </div>

            {/* Grade Selection */}
            <div className="mb-4">
              <Label htmlFor="grade">
                <Award className="w-3 h-3 inline mr-1" />
                Grade Achieved <span className="text-destructive">*</span>
              </Label>
              <select
                id="grade"
                value={hecGrade}
                onChange={(e) => setHecGrade(e.target.value)}
                className="w-full h-9 px-3 mt-1 rounded-lg border border-border bg-white text-sm"
              >
                <option value="">Select grade…</option>
                {HEC_GRADES.map((g) => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </div>

            {/* Certificate Upload */}
            <div className="mb-5">
              <Label>
                <Upload className="w-3 h-3 inline mr-1" />
                Upload Certificate (Optional)
              </Label>
              <div className="mt-2 border-2 border-dashed border-border rounded-lg p-4 text-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer">
                <input
                  type="file"
                  className="hidden"
                  id="certificate-upload"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setCertificateFile(e.target.files?.[0] || null)}
                />
                <label htmlFor="certificate-upload" className="cursor-pointer block">
                  <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground opacity-50" />
                  <p className="text-xs text-muted-foreground">
                    {certificateFile ? certificateFile.name : "Click to upload certificate"}
                  </p>
                </label>
              </div>
            </div>

            {/* Campus Filter */}
            <div className="mb-5">
              <Label htmlFor="campus">
                Campus Preference (optional)
              </Label>
              <select
                id="campus"
                value={campus}
                onChange={(e) => setCampus(e.target.value as any)}
                className="w-full h-9 px-3 mt-1 rounded-lg border border-border bg-white text-sm"
              >
                <option value="">All Campuses</option>
                <option value="kampala">Kampala (Kansanga)</option>
                <option value="western">Western (Ishaka)</option>
              </select>
            </div>

            {/* Submit Button */}
            <Button
              className="w-full gap-2"
              onClick={handleGetRecommendations}
              isLoading={recommendMutation.isPending}
              disabled={!isValid || recommendMutation.isPending}
            >
              <Sparkles className="w-4 h-4" />
              Find Progression Paths
            </Button>

            {recommendMutation.isError && (
              <p className="mt-3 text-xs text-destructive text-center">
                {(recommendMutation.error as Error)?.message || "Failed to get recommendations"}
              </p>
            )}
          </Card>
        </div>

        {/* ── Results Panel ──────────────────────────────────────────────── */}
        <div className="lg:col-span-2 min-w-0" id="results-section">
          {!result && !recommendMutation.isPending && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-muted-foreground py-24">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-20" />
                <p className="font-semibold text-lg">
                  Enter your HEC certificate details
                </p>
                <p className="text-sm mt-2 max-w-xs mx-auto">
                  Enter your certificate details to see all possible progression pathways including direct degree entry
                </p>
              </div>
            </div>
          )}

          {recommendMutation.isPending && (
            <div className="h-64 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Sparkles className="w-10 h-10 mx-auto mb-3 text-primary animate-pulse" />
                <p className="font-semibold">Analysing progression paths…</p>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Summary bar */}
              <div className="flex items-center justify-between flex-wrap gap-2 mb-4">
                <div className="min-w-0">
                  <h2 className="text-xl font-bold">
                    {result.total} Pathways Found
                  </h2>
                  <p className="text-sm text-muted-foreground truncate">
                    For {hecQualification} with {hecGrade} from {institutionName}
                  </p>
                </div>
              </div>

              {result.total === 0 && (
                <Card className="p-12 text-center">
                  <AlertCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-40" />
                  <p className="font-semibold text-lg mb-2">
                    No matching programs found
                  </p>
                  <p className="text-sm text-muted-foreground mb-6">
                    Try changing your campus filter or contact admissions for advice.
                  </p>
                </Card>
              )}

              {result.recommendations.map((prog) => (
                <ProgramCard
                  key={prog.id}
                  program={prog}
                  onApply={handleApply}
                />
              ))}

              {result.total > 0 && (
                <div className="pt-4 border-t border-border text-center text-sm text-muted-foreground">
                  Don't see the right program?{" "}
                  <Link
                    href="/apply"
                    className="font-semibold text-primary hover:underline"
                  >
                    Browse all programs <ArrowRight className="inline w-3.5 h-3.5" />
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}