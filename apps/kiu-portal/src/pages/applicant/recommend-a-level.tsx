/**
 * recommend-a-level.tsx — A-Level Subject Combination → Program Recommendation
 *
 * Core feature from the project proposal:
 * "Allow input of Advanced Level subject combinations, grades, General Paper,
 *  and subsidiary subjects (pass/fail) to receive personalized program
 *  recommendations, complete with entry requirements, fees, duration and
 *  career prospects."
 *
 * Route: /recommend/a-level  (accessible to authenticated applicants)
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

export default function RecommendALevel() {
  const [, setLocation] = useLocation();
  const recommendMutation = useRecommendPrograms();

  const [subjects, setSubjects] = useState<SubjectEntry[]>([
    { subject: "", grade: "", subjectType: "principal" },
    { subject: "", grade: "", subjectType: "principal" },
    { subject: "", grade: "", subjectType: "principal" },
    { subject: "", grade: "", subjectType: "subsidiary" }, // GP slot
    { subject: "", grade: "", subjectType: "subsidiary" }, // 2nd subsidiary
  ]);
  const [campus, setCampus] = useState<"" | "kampala" | "western">("");
  const [curriculum, setCurriculum] = useState<"" | "uneb" | "cambridge" | "other">("");
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

  const principalSubjects = subjects.filter(
    (s) => s.subjectType === "principal"
  );
  const principalCount = principalSubjects.filter(
    (s) => s.subject && s.grade
  ).length;
  const principalSubjectsWithoutGrade = principalSubjects.filter(
    (s) => s.subject && !s.grade
  ).length;
  const principalSubjectsWithoutSubject = principalSubjects.filter(
    (s) => !s.subject && s.grade
  ).length;
  const hasGP = subjects.some(
    (s) => s.subject === "General Paper" && s.subjectType === "subsidiary"
  );
  // Calculate actual valid passes
  const principalPasses = principalSubjects
    .filter(s => s.subject && s.grade)
    .filter(s => {
      const grade = ALEVEL_GRADES.find(g => g.value === s.grade);
      const points = grade?.points || 0;
      return points >= 1;
    }).length;

  const subsidiaryPasses = subjects
    .filter(s => s.subjectType === "subsidiary" && s.subject && s.grade)
    .filter(s => {
      const grade = ALEVEL_GRADES.find(g => g.value === s.grade);
      const points = grade?.points || 0;
      return points >= 1;
    }).length;

  // NCHE Strict requirements:
  // Minimum 3 PRINCIPAL SUBJECTS with grades + subsidiaries
  const isValid = principalCount >= 3 && curriculum !== "" && principalPasses >= 2;

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
    setLocation("/apply/degree?qualification=a_level");
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
              Enter your A-Level subjects and grades to find the best-matching
              KIU programs
            </p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Input Panel ──────────────────────────────────────────────── */}
        <div className="lg:col-span-1 space-y-6 min-w-0">
          <Card className="p-6">
            <h2 className="font-bold text-lg mb-1">Your A-Level Subjects</h2>
            <p className="text-xs text-muted-foreground mb-5">
              Add your principal subjects and at least General Paper (GP) as
              subsidiary.
            </p>

            {/* Official UHEQF Requirements */}
            <div className="mb-5 p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex items-center gap-2 mb-3">
                <GraduationCap className="w-4 h-4 text-slate-700" />
                <p className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Official UHEQF Entry Requirements
                </p>
              </div>
              <div className="grid grid-cols-1 gap-3">
                <div className="p-3 rounded-lg bg-green-50 border border-green-200">
                  <p className="text-xs font-bold text-green-800 mb-1">✅ A-Level (UACE) Level 3</p>
                  <ul className="text-xs text-green-700 space-y-0.5">
                    <li>• 2 Principal Passes <strong>OR</strong></li>
                    <li>• 1 Principal + 2 Subsidiary Passes</li>
                    <li>• Eligible for <strong>Direct Bachelor Degree Entry</strong></li>
                  </ul>
                </div>
                <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                  <p className="text-xs font-bold text-blue-800 mb-1">✅ Higher Education Certificate (HEC) Level 4</p>
                  <ul className="text-xs text-blue-700 space-y-0.5">
                    <li>• 1 Principal Pass <strong>OR</strong> 2 Subsidiary Passes</li>
                    <li>• 1 Year bridging program</li>
                    <li>• Progress to Diploma / Degree</li>
                  </ul>
                </div>
                <div className="p-3 rounded-lg bg-amber-50 border border-amber-200">
                  <p className="text-xs font-bold text-amber-800 mb-1">✅ Diploma Level 5</p>
                  <ul className="text-xs text-amber-700 space-y-0.5">
                    <li>• 1 Principal + 2 Subsidiary Passes</li>
                    <li>• 70-75% practical focus</li>
                    <li>• Progress to Bachelor Degree</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* NCHE Quick Guide */}
            <div className="mb-5 p-3 rounded-xl bg-blue-50 border border-blue-200 flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <div className="text-xs text-blue-700 space-y-1">
                <p className="font-semibold">Grade Point Values:</p>
                <p>• A=6, B=5, C=4, D=3, E=2, O=1, F=0</p>
                <p>• General Paper recommended for all programs</p>
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
                     <div key={i} className="grid grid-cols-12 gap-3 items-center w-full">
                       <select
                         value={s.subject}
                         onChange={(e) =>
                           updateSubject(i, "subject", e.target.value)
                         }
                         className="col-span-8 h-10 px-3 rounded-lg border border-border bg-white text-sm w-full"
                       >
                         <option value="">Select Subject…</option>
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
                         className="col-span-3 h-10 px-3 rounded-lg border border-border bg-white text-sm w-full"
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
                           className="col-span-1 h-10 flex items-center justify-center text-muted-foreground hover:text-destructive w-full rounded-lg border border-transparent hover:border-destructive/30 hover:bg-destructive/5"
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

            {/* Insert Grades for Principal Subjects */}
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
                  .filter(({ s }) => s.subjectType === "principal" && s.subject)
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
                        {ALEVEL_GRADES.map((g) => (
                          <option key={g.value} value={g.value}>
                            {g.value}
                          </option>
                        ))}
                        </select>
                        {s.grade && (
                          <span className="text-xs font-medium text-primary w-12 text-right">
                            ({ALEVEL_GRADES.find(g => g.value === s.grade)?.points || 0} pts)
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                {subjects.filter(s => s.subjectType === "principal" && s.subject).length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-4">
                    Please select your principal subjects above
                  </p>
                )}
              </div>
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
                    <div key={i} className="grid grid-cols-12 gap-3 items-center w-full">
                      <select
                        value={s.subject}
                        onChange={(e) =>
                          updateSubject(i, "subject", e.target.value)
                        }
                        className="col-span-8 h-10 px-3 rounded-lg border border-border bg-white text-sm w-full"
                      >
                        <option value="">Select Subject…</option>
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
                        className="col-span-3 h-10 px-3 rounded-lg border border-border bg-white text-sm w-full"
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
                        className="col-span-1 h-10 flex items-center justify-center text-muted-foreground hover:text-destructive w-full rounded-lg border border-transparent hover:border-destructive/30 hover:bg-destructive/5"
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

            {/* Curriculum Type */}
            <div className="mb-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                A-Level Curriculum <span className="text-destructive">*</span>
              </p>
              <select
                value={curriculum}
                onChange={(e) => setCurriculum(e.target.value as any)}
                className="w-full h-9 px-3 rounded-lg border border-border bg-white text-sm"
              >
                <option value="">Select curriculum…</option>
                <option value="uneb">UNEB (Uganda National Examinations Board)</option>
                <option value="cambridge">Cambridge International A-Level</option>
                <option value="other">Other / International</option>
              </select>
              {curriculum && (
                <p className="text-xs text-muted-foreground mt-1">
                  {curriculum === "uneb" && "Grades: A (6pts), B (5pts), C (4pts), D (3pts), E (2pts), O (1pt), F (0pt)"}
                  {curriculum === "cambridge" && "Grades: A* (6pts), A (5pts), B (4pts), C (3pts), D (2pts), E (1pt)"}
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
                  principalCount >= 3 ? "text-green-600" : "text-muted-foreground"
                }`}
              >
                {principalCount >= 3 ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                {principalCount}/3 principal subjects with grades
              </div>
              {principalSubjectsWithoutGrade > 0 && (
                <div className="flex items-center gap-2 text-xs text-amber-600">
                  <AlertCircle className="w-4 h-4" />
                  {principalSubjectsWithoutGrade} subject(s) missing grade
                </div>
              )}
              {principalSubjectsWithoutSubject > 0 && (
                <div className="flex items-center gap-2 text-xs text-amber-600">
                  <AlertCircle className="w-4 h-4" />
                  {principalSubjectsWithoutSubject} grade(s) missing subject
                </div>
              )}
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
            <>
            {/* ✅ QUALIFICATION STATUS - THIS WAS COMPLETELY MISSING */}
            <Card className="p-5 mb-4">
              <h3 className="font-bold text-sm mb-4 flex items-center gap-2">
                {result.qualificationCheck.alevel?.eligible ? <CheckCircle className="w-5 h-5 text-green-600" /> : <AlertCircle className="w-5 h-5 text-amber-600" />}
                Qualification Status
              </h3>

              <div className="space-y-4">
                {/* Overall Status */}
                <div className={`p-3 rounded-lg ${result.qualificationCheck.alevel?.eligible ? 'bg-green-50 border border-green-200' : 'bg-amber-50 border border-amber-200'}`}>
                  <p className={`font-semibold text-sm ${result.qualificationCheck.alevel?.eligible ? 'text-green-800' : 'text-amber-800'}`}>
                    {result.qualificationCheck.alevel?.message}
                  </p>
                </div>

                {/* Requirements Met */}
                {result.qualificationCheck.alevel?.requirementsMet && result.qualificationCheck.alevel.requirementsMet.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-green-700 mb-2">✅ Requirements Met:</p>
                    <ul className="space-y-1">
                      {result.qualificationCheck.alevel.requirementsMet.map((req, i) => (
                        <li key={i} className="text-xs text-green-700 pl-1">{req}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Requirements Missing */}
                {result.qualificationCheck.alevel?.requirementsMissing && result.qualificationCheck.alevel.requirementsMissing.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-red-700 mb-2">❌ Missing Requirements:</p>
                    <ul className="space-y-1">
                      {result.qualificationCheck.alevel.requirementsMissing.map((req, i) => (
                        <li key={i} className="text-xs text-red-700 pl-1">{req}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Eligible Program Levels */}
                <div className="grid grid-cols-3 gap-2">
                  {['degree', 'diploma', 'hec'].map(level => (
                    <div key={level} className={`p-2 rounded text-center text-xs font-medium ${
                      result.allowedProgramLevels.includes(level)
                        ? 'bg-green-100 text-green-800 border border-green-200'
                        : 'bg-slate-100 text-slate-500 border border-slate-200'
                    }`}>
                      {result.allowedProgramLevels.includes(level) ? '✅ ' : '❌ '}
                      {level.toUpperCase()}
                    </div>
                  ))}
                </div>

                {/* Transparency Stats */}
                <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-lg">
                  <div>
                    <p className="text-xs text-muted-foreground">Programs Scanned</p>
                    <p className="text-lg font-bold">{result.totalProgramsScanned}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Excluded (Not Qualified)</p>
                    <p className="text-lg font-bold text-amber-600">{result.programsExcludedByQualification}</p>
                  </div>
                </div>

                {/* Next Steps */}
                {result.qualificationCheck.nextSteps.length > 0 && (
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                    <p className="text-xs font-semibold text-blue-800 mb-2">📋 Recommended Next Steps:</p>
                    <ul className="space-y-1">
                      {result.qualificationCheck.nextSteps.map((step, i) => (
                        <li key={i} className="text-xs text-blue-700 pl-1">• {step}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Card>

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
                      NCHE requirements met
                    </div>
                  )}
              </div>
            </Card>
            </>
          )}
        </div>

        {/* ── Results Panel ─────────────────────────────────────────────── */}
        <div className="lg:col-span-2 min-w-0" id="results-section">
          {!result && !recommendMutation.isPending && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-muted-foreground py-24">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-20" />
                <p className="font-semibold text-lg">
                  Enter your A-Level subjects
                </p>
                <p className="text-sm mt-2 max-w-xs mx-auto">
                  Fill in at least 3 principal subjects with grades, then click
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