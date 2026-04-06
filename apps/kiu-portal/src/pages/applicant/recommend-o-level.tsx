/**
 * recommend-o-level.tsx — O-Level Subject Combination → Program Recommendation
 *
 * Core feature from the project proposal:
 * "Allow input of O-Level subject combinations and grades to receive personalized program
 *  recommendations, complete with entry requirements, fees, duration and
 *  career prospects."
 *
 * Route: /recommend/o-level  (accessible to authenticated applicants)
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

const OLEVEL_SUBJECTS = [
  "English Language", "Mathematics", "Physics", "Chemistry", "Biology",
  "Geography", "History", "Christian Religious Education (CRE)",
  "Islamic Religious Education (IRE)", "Fine Art", "Music",
  "Entrepreneurship Education", "Computer Studies", "Agriculture",
  "Home Economics", "Commerce", "French", "Kiswahili",
  "Literature in English", "Technical Drawing", "Physical Education",
  "Additional Mathematics",
];

// Old Curriculum: D1, D2, C3, C4, C5, C6, P7, P8, F9
const OLEVEL_GRADES_OLD = [
  { label: "D1 – Distinction 1 (best)", value: "D1", points: 1 },
  { label: "D2 – Distinction 2", value: "D2", points: 2 },
  { label: "C3 – Credit 3", value: "C3", points: 3 },
  { label: "C4 – Credit 4", value: "C4", points: 4 },
  { label: "C5 – Credit 5", value: "C5", points: 5 },
  { label: "C6 – Credit 6", value: "C6", points: 6 },
  { label: "P7 – Pass 7", value: "P7", points: 7 },
  { label: "P8 – Pass 8", value: "P8", points: 8 },
  { label: "F9 – Fail", value: "F9", points: 9 },
];

// New Curriculum: D1, D2, D3, D4, D5, D6, D7, D8, F
const OLEVEL_GRADES_NEW = [
  { label: "D1 – Distinction 1 (best)", value: "D1", points: 1 },
  { label: "D2 – Distinction 2", value: "D2", points: 2 },
  { label: "D3 – Distinction 3", value: "D3", points: 3 },
  { label: "D4 – Credit 4", value: "D4", points: 4 },
  { label: "D5 – Credit 5", value: "D5", points: 5 },
  { label: "D6 – Credit 6", value: "D6", points: 6 },
  { label: "D7 – Pass 7", value: "D7", points: 7 },
  { label: "D8 – Pass 8", value: "D8", points: 8 },
  { label: "F – Fail", value: "F", points: 9 },
];

// ── Types ─────────────────────────────────────────────────────────────────────

type SubjectEntry = {
  subject: string;
  grade: string;
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
            <h3 className="font-bold text-lg leading-tight truncate">{program.name}</h3>
            {ncheStatusBadge(program.ncheStatus)}
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
          <p className="text-xs text-muted-foreground mt-1 truncate">
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

export default function RecommendOLevel() {
  const [, setLocation] = useLocation();
  const recommendMutation = useRecommendPrograms();

  const [subjects, setSubjects] = useState<SubjectEntry[]>([
    { subject: "", grade: "" },
    { subject: "", grade: "" },
    { subject: "", grade: "" },
    { subject: "", grade: "" },
    { subject: "", grade: "" },
  ]);
  const [campus, setCampus] = useState<"" | "kampala" | "western">("");
  const [curriculum, setCurriculum] = useState<"" | "uneb" | "cambridge" | "other">("");
  const [oLevelCurriculum, setOLevelCurriculum] = useState<"old" | "new">("old");
  const [result, setResult] = useState<RecommendResult | null>(null);

  // Get correct grade list based on selected curriculum
  const getCurrentGradeList = () => {
    return oLevelCurriculum === "old" ? OLEVEL_GRADES_OLD : OLEVEL_GRADES_NEW;
  };

  // ── Subject management ───────────────────────────────────────────────────

  const addSubject = () => {
    setSubjects((prev) => [
      ...prev,
      { subject: "", grade: "" },
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

  const subjectCount = subjects.filter(
    (s) => s.subject && s.grade
  ).length;
  const subjectsWithoutGrade = subjects.filter(
    (s) => s.subject && !s.grade
  ).length;
  const subjectsWithoutSubject = subjects.filter(
    (s) => !s.subject && s.grade
  ).length;

  // Calculate actual valid passes according to NCHE rules
  const passesCount = subjects
    .filter((s) => s.subject && s.grade)
    .filter((s) => {
      const grade = getCurrentGradeList().find((g: any) => g.value === s.grade);
      const points = grade?.points || 9;
      // ONLY grades 1 through 8 are considered PASSES. Grade 9 is FAIL.
      return points >= 1 && points <= 8;
    }).length;

  const isValid = subjectCount >= 5 && curriculum !== "" && passesCount >= 5;

  // ── Submit ───────────────────────────────────────────────────────────────

  const handleGetRecommendations = () => {
    const filledSubjects = subjects.filter((s) => s.subject && s.grade);
    recommendMutation.mutate(
      {
        alevelSubjects: filledSubjects.map((s) => ({
          subject: s.subject.toLowerCase(),
          grade: s.grade,
          subjectType: "principal",
        })),
        campus: campus || undefined,
        curriculum: curriculum || undefined,
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
    setLocation("/apply/diploma");
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
              Program Recommendation Tool
            </h1>
            <p className="text-muted-foreground">
              Enter your O-Level subjects and grades to find the best-matching
              KIU programs
            </p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Input Panel ──────────────────────────────────────────────── */}
        <div className="lg:col-span-1 space-y-6 min-w-0">
          <Card className="p-6">
            <h2 className="font-bold text-lg mb-1">Your O-Level Subjects</h2>
            <p className="text-xs text-muted-foreground mb-5">
              Add your O-Level subjects and grades. Minimum 5 subjects required.
            </p>

            {/* NCHE Quick Guide */}
              <div className="mb-5 p-3 rounded-xl bg-blue-50 border border-blue-200 flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <div className="text-xs text-blue-700 space-y-1">
                <p className="font-semibold">NCHE OFFICIAL REQUIREMENTS:</p>
                <p>• Minimum 5 PASSES required (D1 to P8)</p>
                <p>• F9 / F grades are considered FAIL</p>
                <p>• Points: D1=1, D2=2, C3=3, C4=4, C5=5, C6=6, P7=7, P8=8, F9/F=9 (FAIL)</p>
                <p className="font-semibold mt-1">Failing grades are NOT counted as passes</p>
              </div>
            </div>

            {/* O-Level Subjects */}
            <div className="mb-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-primary mb-2">
                O-Level Subjects
              </p>
              <div className="space-y-3">
                {subjects
                  .map((s, i) => ({ s, i }))
                  .map(({ s, i }) => (
                    <div key={i} className="flex gap-2 items-center">
                      <select
                        value={s.subject}
                        onChange={(e) =>
                          updateSubject(i, "subject", e.target.value)
                        }
                        className="flex-1 h-9 px-2 rounded-lg border border-border bg-white text-sm min-w-0"
                      >
                        <option value="">Subject…</option>
                        {OLEVEL_SUBJECTS.map((sub) => (
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
                        className="w-24 h-9 px-2 rounded-lg border border-border bg-white text-sm shrink-0"
                      >
                        <option value="">Grade</option>
                        {getCurrentGradeList().map((g: any) => (
                          <option key={g.value} value={g.value}>
                            {g.label}
                          </option>
                        ))}
                      </select>
                      {subjects.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeSubject(i)}
                          className="w-8 h-8 flex items-center justify-center text-muted-foreground hover:text-destructive shrink-0"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
              </div>
              <button
                type="button"
                onClick={() => addSubject()}
                disabled={
                  subjects.length >= OLEVEL_SUBJECTS.length
                }
                className="mt-2 flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/80 disabled:opacity-40"
              >
                  <Plus className="w-3.5 h-3.5" /> Add Subject
              </button>
            </div>

            {/* UNEB Syllabus Version */}
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                UNEB Syllabus Version
              </p>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setOLevelCurriculum("old")}
                  className={`flex-1 h-9 px-3 rounded-lg text-sm font-medium transition-all ${
                    oLevelCurriculum === "old" 
                      ? "bg-primary text-white shadow-sm" 
                      : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                  }`}
                >
                  Old Curriculum
                </button>
                <button
                  type="button"
                  onClick={() => setOLevelCurriculum("new")}
                  className={`flex-1 h-9 px-3 rounded-lg text-sm font-medium transition-all ${
                    oLevelCurriculum === "new" 
                      ? "bg-primary text-white shadow-sm" 
                      : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                  }`}
                >
                  New Curriculum
                </button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {oLevelCurriculum === "old" 
                  ? "Old Curriculum" 
                  : "New Curriculum"}
              </p>
            </div>

            {/* Insert Grades for Subjects */}
            <div className="mb-5 p-4 rounded-xl bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/20">
              <div className="flex items-center gap-2 mb-3">
                <GraduationCap className="w-5 h-5 text-primary" />
                <p className="text-sm font-semibold text-primary">
                  Subject Grades Summary
                </p>
              </div>
              <div className="space-y-2">
                {subjects
                  .map((s, i) => ({ s, i }))
                  .filter(({ s }) => s.subject)
                  .map(({ s, i }) => (
                    <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-white border border-border">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{s.subject}</p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <select
                          value={s.grade}
                          onChange={(e) =>
                            updateSubject(i, "grade", e.target.value)
                          }
                          className={`w-16 h-7 px-1 rounded border text-sm font-semibold ${
                            s.grade 
                              ? "border-primary bg-primary/5 text-primary" 
                              : "border-border bg-white text-muted-foreground"
                          }`}
                        >
                          <option value="">—</option>
                        {getCurrentGradeList().map((g: any) => (
                          <option key={g.value} value={g.value}>
                            {g.value}
                          </option>
                        ))}
                        </select>
                        {s.grade && (
                          <span className="text-xs font-medium text-primary w-12 text-right">
                            ({getCurrentGradeList().find((g: any) => g.value === s.grade)?.points || 0} pts)
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                {subjects.filter(s => s.subject).length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-4">
                    Please select your subjects above
                  </p>
                )}
              </div>
            </div>

            {/* Examination Board */}
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Examination Board <span className="text-destructive">*</span>
              </p>
              <select
                value={curriculum}
                onChange={(e) => setCurriculum(e.target.value as any)}
                className="w-full h-9 px-3 rounded-lg border border-border bg-white text-sm"
              >
                <option value="">Select exam board…</option>
                <option value="uneb">UNEB (Uganda National Examinations Board)</option>
                <option value="cambridge">Cambridge International O-Level</option>
                <option value="other">Other / International</option>
              </select>
              {curriculum && curriculum !== "uneb" && (
                <p className="text-xs text-muted-foreground mt-1">
                  {curriculum === "cambridge" && "Grades: A*=1, A=2, B=3, C=4, D=5, E=6, F=7, G=8, U=9"}
                  {curriculum === "other" && "Contact admissions for grade equivalency"}
                </p>
              )}
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
                  subjectCount >= 5 ? "text-green-600" : "text-muted-foreground"
                }`}
              >
                {subjectCount >= 5 ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                {subjectCount}/5 subjects completed
              </div>
              <div
                className={`flex items-center gap-2 text-xs ${
                  passesCount >= 5 ? "text-green-600" : "text-amber-500"
                }`}
              >
                {passesCount >= 5 ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                {passesCount}/5 valid PASSES achieved
              </div>
              {subjectsWithoutGrade > 0 && (
                <div className="flex items-center gap-2 text-xs text-amber-600">
                  <AlertCircle className="w-4 h-4" />
                  {subjectsWithoutGrade} subject(s) missing grade
                </div>
              )}
              {subjectsWithoutSubject > 0 && (
                <div className="flex items-center gap-2 text-xs text-amber-600">
                  <AlertCircle className="w-4 h-4" />
                  {subjectsWithoutSubject} grade(s) missing subject
                </div>
              )}
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

          {/* Compliance Summary (shown after first result) */}
          {result && (
            <Card className="p-5">
              <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                Compliance Summary
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Total Points
                  </span>
                  <span className="font-bold">
                    {result.ncheCompliance.totalPrincipalPoints}
                  </span>
                </div>
                {result.ncheCompliance.errors.map((e, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-lg bg-destructive/10 text-destructive break-words"
                  >
                    {e}
                  </div>
                ))}
                {result.ncheCompliance.warnings.map((w, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-lg bg-amber-50 text-amber-700 break-words"
                  >
                    {w}
                  </div>
                ))}
                {result.ncheCompliance.errors.length === 0 &&
                  result.ncheCompliance.warnings.length === 0 && (
                    <div className="p-2 rounded-lg bg-green-50 text-green-700 flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Requirements met
                    </div>
                  )}
              </div>
            </Card>
          )}
        </div>

        {/* ── Results Panel ─────────────────────────────────────────────── */}
        <div className="lg:col-span-2 min-w-0" id="results-section">
          {!result && !recommendMutation.isPending && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-muted-foreground py-24">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-20" />
                <p className="font-semibold text-lg">
                  Enter your O-Level subjects
                </p>
                <p className="text-sm mt-2 max-w-xs mx-auto">
                  Fill in at least 5 subjects with grades, then click
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
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="min-w-0">
                  <h2 className="text-xl font-bold">
                    {result.total} Program
                    {result.total !== 1 ? "s" : ""} Found
                  </h2>
                  <p className="text-sm text-muted-foreground truncate">
                    Based on:{" "}
                    <span className="font-medium text-foreground">
                      {result.subjectsAnalyzed.join(", ")}
                    </span>
                  </p>
                </div>
                <Badge variant="outline" className="text-xs shrink-0">
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