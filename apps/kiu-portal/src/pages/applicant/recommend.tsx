/**
 * recommend.tsx — A-Level Subject Combination → Program Recommendation
 *
 * Core feature from the project proposal:
 * "Allow input of Advanced Level subject combinations, grades, General Paper,
 *  and subsidiary subjects (pass/fail) to receive personalized program
 *  recommendations, complete with entry requirements, fees, duration and
 *  career prospects."
 *
 * Route: /recommend  (accessible to authenticated applicants)
 * Backend: POST /api/admission/recommend
 */

import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useRecommendPrograms } from "@workspace/api-client-react";
import { Button, Card, Badge } from "@/components/ui/shared";
import {
  ArrowLeft,
  ArrowRight,
  Plus,
  Trash2,
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
} from "lucide-react";

// ── Subject lists (same as apply.tsx for consistency) ─────────────────────────

const PRINCIPAL_SUBJECTS = [
  "Mathematics",
  "Physics",
  "Chemistry",
  "Biology",
  "Geography",
  "History",
  "Literature in English",
  "Economics",
  "Entrepreneurship Education",
  "Art & Design",
  "Technical Drawing",
  "Christian Religious Education (CRE)",
  "Islamic Religious Education (IRE)",
  "Divinity",
  "Fine Art",
  "Music",
];

const SUBSIDIARY_SUBJECTS = [
  "General Paper",
  "Subsidiary ICT",
  "Subsidiary Mathematics",
];

const ALEVEL_GRADES = [
  { label: "A – 6 pts", value: "A", points: 6 },
  { label: "B – 5 pts", value: "B", points: 5 },
  { label: "C – 4 pts", value: "C", points: 4 },
  { label: "D – 3 pts", value: "D", points: 3 },
  { label: "E – 2 pts", value: "E", points: 2 },
  { label: "O – 1 pt",  value: "O", points: 1 },
  { label: "F – Fail",  value: "F", points: 0 },
];

// ── Types ─────────────────────────────────────────────────────────────────────

type SubjectEntry = {
  subject: string;
  grade: string;
  subjectType: "principal" | "subsidiary";
};

import type {
  RecommendedProgram as ApiRecommendedProgram,
  NcheCompliance as ApiNcheCompliance,
  RecommendResult as ApiRecommendResult,
} from "@workspace/api-client-react";

type RecommendedProgram = ApiRecommendedProgram;
type NcheCompliance = ApiNcheCompliance;
type RecommendResult = ApiRecommendResult;

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

// ── ProgramCard ───────────────────────────────────────────────────────────────

function ProgramCard({
  program,
  onApply,
}: {
  program: RecommendedProgram;
  onApply: (id: number, name: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="p-6 hover:shadow-lg transition-all border-border">
      {/* Top row */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h3 className="font-bold text-lg leading-tight">{program.name}</h3>
            {ncheStatusBadge(program.ncheStatus)}
          </div>
          <p className="text-sm text-muted-foreground">
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
              <span className="text-[10px] px-2 py-0.5 rounded-full font-medium bg-secondary text-muted-foreground flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {program.duration}
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
            Subject<br />Match
          </span>
        </div>
      </div>

      {/* Match bar */}
      <div className="mb-4">
        {matchBar(program.matchPercentage)}
        {program.matchedSubjects.length > 0 && (
          <p className="text-xs text-muted-foreground mt-1">
            Matched:{" "}
            <span className="font-medium text-primary">
              {program.matchedSubjects.join(", ")}
            </span>
          </p>
        )}
      </div>

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
        <div>
          <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
            <DollarSign className="w-3 h-3" /> Local Tuition
          </p>
          <p className="font-bold text-sm text-primary">
            {formatFee(program.feesLocal, "UGX")}
          </p>
        </div>
        <div>
          <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
            <DollarSign className="w-3 h-3" /> Int'l Tuition
          </p>
          <p className="font-bold text-sm">
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
              <p className="text-muted-foreground leading-relaxed">
                {program.entryRequirements}
              </p>
            </div>
          )}
          {program.description && (
            <div className="p-3 bg-secondary/50 rounded-lg">
              <p className="font-semibold text-xs uppercase tracking-wider text-muted-foreground mb-1">
                About This Program
              </p>
              <p className="text-muted-foreground leading-relaxed">
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

export default function Recommend() {
  const [, setLocation] = useLocation();
  const recommendMutation = useRecommendPrograms();

  const [subjects, setSubjects] = useState<SubjectEntry[]>([
    { subject: "", grade: "", subjectType: "principal" },
    { subject: "", grade: "", subjectType: "principal" },
    { subject: "", grade: "", subjectType: "subsidiary" }, // GP slot
  ]);
  const [campus, setCampus] = useState<"" | "kampala" | "western">("");
  const [result, setResult] = useState<RecommendResult | null>(null);

  // ── Subject management ───────────────────────────────────────────────────

  const addSubject = (type: "principal" | "subsidiary") => {
    setSubjects((prev) => [
      ...prev,
      { subject: "", grade: "", subjectType: type },
    ]);
  };

  const removeSubject = (idx: number) => {
    setSubjects((prev) => prev.filter((_, i) => i !== idx));
  };

  const updateSubject = (
    idx: number,
    field: keyof SubjectEntry,
    value: string
  ) => {
    setSubjects((prev) =>
      prev.map((s, i) =>
        i === idx ? { ...s, [field]: value } : s
      )
    );
  };

  // ── Validation ───────────────────────────────────────────────────────────

  const principalCount = subjects.filter(
    (s) => s.subjectType === "principal" && s.subject && s.grade
  ).length;
  const hasGP = subjects.some(
    (s) => s.subject === "General Paper" && s.subjectType === "subsidiary"
  );
  const isValid = principalCount >= 2;

  // ── Submit ───────────────────────────────────────────────────────────────

  const handleGetRecommendations = () => {
    const filledSubjects = subjects.filter((s) => s.subject && s.grade);
    recommendMutation.mutate(
      {
        alevelSubjects: filledSubjects.map((s) => ({
          subject: s.subject.toLowerCase(),
          grade: s.grade,
          subjectType: s.subjectType,
        })),
        campus: campus || undefined,
      },
      {
        onSuccess: (data: RecommendResult) => {
          setResult(data);
          // Scroll to results
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
    // Store pre-selected program in sessionStorage for the apply form to pick up
    sessionStorage.setItem("recommended_program_id", String(programId));
    sessionStorage.setItem("recommended_program_name", programName);
    setLocation("/apply/degree?qualification=a_level");
  };

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
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
              Program Recommendation Tool
            </h1>
            <p className="text-muted-foreground">
              Enter your A-Level subjects and grades to find the best-matching
              KIU programs
            </p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* ── Input Panel ──────────────────────────────────────────────── */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="p-6">
            <h2 className="font-bold text-lg mb-1">Your A-Level Subjects</h2>
            <p className="text-xs text-muted-foreground mb-5">
              Add your principal subjects and at least General Paper (GP) as
              subsidiary.
            </p>

            {/* NCHE Quick Guide */}
            <div className="mb-5 p-3 rounded-xl bg-blue-50 border border-blue-200 flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <div className="text-xs text-blue-700 space-y-1">
                <p className="font-semibold">NCHE Requirements:</p>
                <p>• Minimum 2 principal subjects</p>
                <p>• General Paper (GP) as subsidiary</p>
                <p>• Points: A=6, B=5, C=4, D=3, E=2, O=1, F=0</p>
              </div>
            </div>

            {/* Principal Subjects */}
            <div className="mb-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-primary mb-2">
                Principal Subjects
              </p>
              <div className="space-y-3">
                {subjects
                  .map((s, i) => ({ s, i }))
                  .filter(({ s }) => s.subjectType === "principal")
                  .map(({ s, i }) => (
                    <div key={i} className="flex gap-2 items-center">
                      <select
                        value={s.subject}
                        onChange={(e) =>
                          updateSubject(i, "subject", e.target.value)
                        }
                        className="flex-1 h-9 px-2 rounded-lg border border-border bg-white text-sm"
                      >
                        <option value="">Subject…</option>
                        {PRINCIPAL_SUBJECTS.map((sub) => (
                          <option key={sub} value={sub}>
                            {sub}
                          </option>
                        ))}
                      </select>
                      <select
                        value={s.grade}
                        onChange={(e) =>
                          updateSubject(i, "grade", e.target.value)
                        }
                        className="w-24 h-9 px-2 rounded-lg border border-border bg-white text-sm"
                      >
                        <option value="">Grade</option>
                        {ALEVEL_GRADES.map((g) => (
                          <option key={g.value} value={g.value}>
                            {g.label}
                          </option>
                        ))}
                      </select>
                      {subjects.filter((x) => x.subjectType === "principal")
                        .length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeSubject(i)}
                          className="w-8 h-8 flex items-center justify-center text-muted-foreground hover:text-destructive"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
              </div>
              <button
                type="button"
                onClick={() => addSubject("principal")}
                disabled={
                  subjects.filter((s) => s.subjectType === "principal")
                    .length >= PRINCIPAL_SUBJECTS.length
                }
                className="mt-2 flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/80 disabled:opacity-40"
              >
                <Plus className="w-3.5 h-3.5" /> Add Principal Subject
              </button>
            </div>

            {/* Subsidiary Subjects */}
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Subsidiary Subjects (incl. GP)
              </p>
              <div className="space-y-3">
                {subjects
                  .map((s, i) => ({ s, i }))
                  .filter(({ s }) => s.subjectType === "subsidiary")
                  .map(({ s, i }) => (
                    <div key={i} className="flex gap-2 items-center">
                      <select
                        value={s.subject}
                        onChange={(e) =>
                          updateSubject(i, "subject", e.target.value)
                        }
                        className="flex-1 h-9 px-2 rounded-lg border border-border bg-white text-sm"
                      >
                        <option value="">Subject…</option>
                        {SUBSIDIARY_SUBJECTS.map((sub) => (
                          <option key={sub} value={sub}>
                            {sub}
                          </option>
                        ))}
                      </select>
                      <select
                        value={s.grade}
                        onChange={(e) =>
                          updateSubject(i, "grade", e.target.value)
                        }
                        className="w-24 h-9 px-2 rounded-lg border border-border bg-white text-sm"
                      >
                        <option value="">Grade</option>
                        {ALEVEL_GRADES.map((g) => (
                          <option key={g.value} value={g.value}>
                            {g.label}
                          </option>
                        ))}
                      </select>
                      <button
                        type="button"
                        onClick={() => removeSubject(i)}
                        className="w-8 h-8 flex items-center justify-center text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
              </div>
              <button
                type="button"
                onClick={() => addSubject("subsidiary")}
                className="mt-2 flex items-center gap-1 text-xs font-semibold text-muted-foreground hover:text-primary disabled:opacity-40"
              >
                <Plus className="w-3.5 h-3.5" /> Add Subsidiary Subject
              </button>
            </div>

            {/* Campus Filter */}
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Campus Preference (optional)
              </p>
              <select
                value={campus}
                onChange={(e) => setCampus(e.target.value as any)}
                className="w-full h-9 px-3 rounded-lg border border-border bg-white text-sm"
              >
                <option value="">All Campuses</option>
                <option value="kampala">Kampala (Kansanga)</option>
                <option value="western">Western (Ishaka)</option>
              </select>
            </div>

            {/* Validation hints */}
            <div className="mb-5 space-y-2">
              <div
                className={`flex items-center gap-2 text-xs ${
                  principalCount >= 2 ? "text-green-600" : "text-muted-foreground"
                }`}
              >
                {principalCount >= 2 ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                {principalCount}/2 principal subjects entered
              </div>
              <div
                className={`flex items-center gap-2 text-xs ${
                  hasGP ? "text-green-600" : "text-amber-500"
                }`}
              >
                {hasGP ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                General Paper {hasGP ? "added ✓" : "not added (recommended)"}
              </div>
            </div>

            <Button
              className="w-full gap-2"
              onClick={handleGetRecommendations}
              isLoading={recommendMutation.isPending}
              disabled={!isValid || recommendMutation.isPending}
            >
              <Sparkles className="w-4 h-4" />
              Get Program Recommendations
            </Button>

            {recommendMutation.isError && (
              <p className="mt-3 text-xs text-destructive text-center">
                {(recommendMutation.error as Error)?.message ||
                  "Failed to get recommendations"}
              </p>
            )}
          </Card>

          {/* NCHE Compliance Summary (shown after first result) */}
          {result && (
            <Card className="p-5">
              <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                NCHE Compliance Summary
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Principal Points
                  </span>
                  <span className="font-bold">
                    {result.ncheCompliance.totalPrincipalPoints}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">General Paper</span>
                  <span
                    className={`font-bold ${
                      result.ncheCompliance.hasGeneralPaper
                        ? "text-green-600"
                        : "text-amber-500"
                    }`}
                  >
                    {result.ncheCompliance.hasGeneralPaper
                      ? `Yes (${result.ncheCompliance.gpGrade})`
                      : "Not added"}
                  </span>
                </div>
                {result.ncheCompliance.errors.map((e, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-lg bg-destructive/10 text-destructive"
                  >
                    {e}
                  </div>
                ))}
                {result.ncheCompliance.warnings.map((w, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-lg bg-amber-50 text-amber-700"
                  >
                    {w}
                  </div>
                ))}
                {result.ncheCompliance.errors.length === 0 &&
                  result.ncheCompliance.warnings.length === 0 && (
                    <div className="p-2 rounded-lg bg-green-50 text-green-700 flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" />
                      NCHE requirements met
                    </div>
                  )}
              </div>
            </Card>
          )}
        </div>

        {/* ── Results Panel ─────────────────────────────────────────────── */}
        <div className="lg:col-span-2" id="results-section">
          {!result && !recommendMutation.isPending && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-muted-foreground py-24">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-20" />
                <p className="font-semibold text-lg">
                  Enter your A-Level subjects
                </p>
                <p className="text-sm mt-2 max-w-xs mx-auto">
                  Fill in at least 2 principal subjects with grades, then click
                  "Get Program Recommendations"
                </p>
              </div>
            </div>
          )}

          {recommendMutation.isPending && (
            <div className="h-64 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Sparkles className="w-10 h-10 mx-auto mb-3 text-primary animate-pulse" />
                <p className="font-semibold">Analysing your subjects…</p>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Summary bar */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold">
                    {result.total} Program
                    {result.total !== 1 ? "s" : ""} Found
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    Based on:{" "}
                    <span className="font-medium text-foreground">
                      {result.subjectsAnalyzed.join(", ")}
                    </span>
                  </p>
                </div>
                <Badge variant="outline" className="text-xs">
                  Sorted by subject match
                </Badge>
              </div>

              {result.total === 0 && (
                <Card className="p-12 text-center">
                  <AlertCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-40" />
                  <p className="font-semibold text-lg mb-2">
                    No matching programs found
                  </p>
                  <p className="text-sm text-muted-foreground mb-6">
                    Try adding more subjects or changing your campus filter.
                    You can still browse all programs or apply directly.
                  </p>
                  <Button
                    variant="secondary"
                    onClick={() => setLocation("/apply")}
                  >
                    Browse All Programs
                  </Button>
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
