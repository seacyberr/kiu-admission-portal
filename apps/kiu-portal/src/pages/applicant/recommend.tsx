/**
 * apps/kiu-portal/src/pages/applicant/RecommendationsPage.tsx
 *
 * NCHE-compliant programme recommendation engine UI.
 * Entry routes: UACE Direct | Diploma | Postgraduate (Bachelors)
 *
 * KIU admits 3 intakes: Aug/Sep · Dec/Jan · Mar/Apr
 */

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useLocation } from "wouter";

// ── Types ──────────────────────────────────────────────────────────────────

type EntryRoute = "uce_direct" | "uace_direct" | "hec" | "national_cert" | "diploma" | "bachelors" | "masters" | "phd";

// Map recommendation entry routes to application form qualification types
const mapEntryRouteToQualification = (route: EntryRoute): string => {
  switch (route) {
    case "uce_direct": return "o-level";
    case "uace_direct": return "a-level";
    case "hec": return "hec";
    case "national_cert": return "diploma";
    case "diploma": return "diploma";
    case "bachelors": return "degree";
    case "masters": return "masters";
    case "phd": return "phd";
    default: return "a-level";
  }
};

interface Intake {
  name: string;
  year: number;
  application_deadline: string;
}

interface Eligibility {
  eligible: boolean;
  strong_match: boolean;
  route: string;
  reasons_pass: string[];
  reasons_fail: string[];
  reasons_warn: string[];
}

interface Programme {
  id: string;
  code: string;
  name: string;
  faculty: string;
  level: string;
  duration_years: number;
  campus: string[];
  tuition_ugx_per_semester: number;
  tuition_usd_per_semester: number;
  career_prospects: string[];
  accreditation: string;
  next_intakes: Intake[];
  eligibility: Eligibility;
  match_score: number;
}

interface RecommendationResult {
  recommended: Programme[];
  partially_eligible: Programme[];
  not_eligible: Programme[];
  total_programmes: number;
  entry_route: string;
  nche_note: string;
  kiu_intakes: string[];
}

// ── Validation schemas ─────────────────────────────────────────────────────

const UACE_SUBJECTS = [
  "Mathematics", "Physics", "Chemistry", "Biology",
  "Computer Studies", "Agriculture", "History", "Literature in English",
  "French", "Divinity", "Geography", "Economics", "Government",
  "Entrepreneurship", "Physical Education", "Fine Art", "Music",
  "Technical Drawing", "Subsidiary Mathematics", "General Paper",
];


// ── Helper components ──────────────────────────────────────────────────────

function Badge({ variant, children }: { variant: "green" | "amber" | "red" | "blue" | "gray"; children: React.ReactNode }) {
  const styles = {
    green: "bg-green-100 text-green-800 border-green-200",
    amber: "bg-amber-100 text-amber-800 border-amber-200",
    red: "bg-red-100 text-red-800 border-red-200",
    blue: "bg-blue-100 text-blue-800 border-blue-200",
    gray: "bg-gray-100 text-gray-700 border-gray-200",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[variant]}`}>
      {children}
    </span>
  );
}

function ProgrammeCard({ programme, rank }: { programme: Programme; rank?: number }) {
  const [expanded, setExpanded] = useState(false);
  const { eligibility } = programme;
  const fmtUGX = (n: number) => `UGX ${(n / 1_000_000).toFixed(1)}M`;

  const borderColor = eligibility.strong_match
    ? "border-green-200 bg-green-50/30"
    : eligibility.eligible
    ? "border-amber-200 bg-amber-50/30"
    : "border-red-200 bg-red-50/10";

  return (
    <div className={`border rounded-xl p-5 ${borderColor} transition-all`}>
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            {rank && (
              <span className="text-xs font-bold text-blue-600 bg-blue-50 border border-blue-200 rounded-full px-2 py-0.5">
                #{rank}
              </span>
            )}
            <span className="text-xs font-mono text-gray-500">{programme.code}</span>
            <Badge variant={programme.level === "postgraduate" ? "blue" : "gray"}>
              {programme.level === "postgraduate" ? "Postgraduate" : "Undergraduate"}
            </Badge>
          </div>
          <h3 className="text-base font-semibold text-gray-900 leading-snug">{programme.name}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{programme.faculty}</p>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <Badge variant={eligibility.strong_match ? "green" : eligibility.eligible ? "amber" : "red"}>
            {eligibility.strong_match ? "✓ Fully Eligible" : eligibility.eligible ? "⚠ Conditionally Eligible" : "✗ Not Eligible"}
          </Badge>
          <span className="text-xs text-gray-500">{programme.duration_years} year{programme.duration_years > 1 ? "s" : ""}</span>
        </div>
      </div>

      {/* Quick info row */}
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600">
        <span>📍 {programme.campus.join(" · ")}</span>
        <span>💰 {fmtUGX(programme.tuition_ugx_per_semester)}/semester (USD {programme.tuition_usd_per_semester.toLocaleString()})</span>
        <span>🎓 {programme.accreditation}</span>
      </div>

      {/* Next intakes */}
      {programme.next_intakes.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {programme.next_intakes.map((intake) => (
            <div key={`${intake.name}-${intake.year}`} className="text-xs bg-white border border-gray-200 rounded-lg px-2.5 py-1.5">
              <span className="font-medium text-gray-800">{intake.name}</span>
              <span className="text-gray-400 ml-1">· apply by {intake.application_deadline}</span>
            </div>
          ))}
        </div>
      )}

      {/* Eligibility reasons summary */}
      <div className="mt-3 space-y-1">
        {eligibility.reasons_pass.map((r, i) => (
          <div key={i} className="flex items-start gap-1.5 text-xs text-green-700">
            <span className="mt-0.5 shrink-0">✓</span><span>{r}</span>
          </div>
        ))}
        {eligibility.reasons_warn.map((r, i) => (
          <div key={i} className="flex items-start gap-1.5 text-xs text-amber-700">
            <span className="mt-0.5 shrink-0">⚠</span><span>{r}</span>
          </div>
        ))}
        {eligibility.reasons_fail.slice(0, expanded ? undefined : 2).map((r, i) => (
          <div key={i} className="flex items-start gap-1.5 text-xs text-red-600">
            <span className="mt-0.5 shrink-0">✗</span><span>{r}</span>
          </div>
        ))}
      </div>

      {/* Expandable details */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-3 text-xs text-blue-600 hover:text-blue-800 font-medium"
      >
        {expanded ? "Show less ▲" : "Show career prospects & details ▼"}
      </button>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
          <div>
            <p className="text-xs font-semibold text-gray-700 mb-1">Career Prospects</p>
            <div className="flex flex-wrap gap-1.5">
              {programme.career_prospects.map((c) => (
                <Badge key={c} variant="blue">{c}</Badge>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Section({ title, icon, count, children, defaultOpen = true }:
  { title: string; icon: string; count: number; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  if (count === 0) return null;
  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between mb-3 group"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <h2 className="text-base font-semibold text-gray-900">{title}</h2>
          <Badge variant="gray">{count}</Badge>
        </div>
        <span className="text-gray-400 group-hover:text-gray-600">{open ? "▲" : "▼"}</span>
      </button>
      {open && <div className="space-y-3">{children}</div>}
    </div>
  );
}

// ── Main form ──────────────────────────────────────────────────────────────

function QualificationsForm({ onSubmit, loading, qualificationType }: {
  onSubmit: (data: Record<string, unknown>) => void;
  loading: boolean;
  qualificationType: string | null;
}) {
  const [route, setRoute] = useState<EntryRoute>("uace_direct");
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);

  useEffect(() => {
    if (qualificationType) {
      switch (qualificationType) {
        case 'o-level': setRoute("uce_direct"); break;
        case 'a-level': setRoute("uace_direct"); break;
        case 'hec': setRoute("hec"); break;
        case 'national-cert': setRoute("national_cert"); break;
        case 'diploma': setRoute("diploma"); break;
        case 'bachelors': setRoute("bachelors"); break;
        case 'masters': setRoute("masters"); break;
        case 'phd': setRoute("phd"); break;
      }
    }
  }, [qualificationType]);

const { register, handleSubmit, formState: { errors } } = useForm<Record<string, unknown>>({
  defaultValues: { entry_route: route },
  values: { entry_route: route },
});

useEffect(() => {
  if (qualificationType) {
    switch (qualificationType) {
      case 'o-level': setRoute("uce_direct"); break;
      case 'a-level': setRoute("uace_direct"); break;
      case 'hec': setRoute("hec"); break;
      case 'national-cert': setRoute("national_cert"); break;
      case 'diploma': setRoute("diploma"); break;
      case 'bachelors': setRoute("bachelors"); break;
      case 'masters': setRoute("masters"); break;
      case 'phd': setRoute("phd"); break;
    }
  }
}, [qualificationType]);

  const toggleSubject = (subj: string) => {
    setSelectedSubjects((prev) =>
      prev.includes(subj) ? prev.filter((s) => s !== subj) : [...prev, subj]
    );
  };

  const submit = (data: Record<string, unknown>) => {
    // Basic validation - let backend handle detailed validation
    onSubmit({ ...data, entry_route: route, uace_subjects: selectedSubjects });
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-5">
      {/* Entry Route (only shown when no qualification type specified) */}
      {!qualificationType && (
        <div>
          <label className="text-sm font-medium text-gray-700 block mb-2">Entry Route</label>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
            {([
              ["uce_direct", "O-Level (UCE)", "Apply for HEC or Diploma"],
              ["uace_direct", "A-Level (UACE)", "Answer 2 quick questions"],
              ["diploma", "Diploma", "Apply for Degree"],
              ["hec", "HEC", "Apply for Degree"],
              ["bachelors", "Bachelor's Degree", "Bachelor's degree holder"],
              ["masters", "Master's Degree", "Master's degree holder"],
              ["phd", "PhD", "Master's degree holder"],
            ] as const).map(([val, label, sub]) => (
              <button
                key={val}
                type="button"
                onClick={() => setRoute(val)}
                className={`p-3 rounded-lg border-2 text-left transition-all ${
                  route === val
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="text-sm font-semibold text-gray-800">{label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{sub}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* UACE Direct fields */}
      {route === "uace_direct" && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                UCE Passes <span className="text-red-500">*</span>
                <span className="font-normal text-gray-400 ml-1">(min 5 required by NCHE)</span>
              </label>
              <input
                type="number" min={1} max={10}
                {...register("uce_passes", { valueAsNumber: true, required: true, min: 5 })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g. 7"
              />
              {errors.uce_passes && (
                <p className="text-xs text-red-500 mt-1">NCHE requires minimum 5 UCE passes</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                UACE Principal Passes <span className="text-red-500">*</span>
              </label>
              <select
                {...register("uace_principal_passes", { valueAsNumber: true })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[0, 1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>{n} principal pass{n !== 1 ? "es" : ""}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">UACE Points (optional)</label>
              <input
                type="number" min={0} max={30}
                {...register("uace_points", { valueAsNumber: true })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g. 15"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">UACE Year (optional)</label>
              <input
                type="number" min={2000} max={new Date().getFullYear()}
                {...register("uace_year", { valueAsNumber: true })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={String(new Date().getFullYear())}
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              UACE Subjects <span className="text-red-500">*</span>
              <span className="font-normal text-gray-400 ml-1">({selectedSubjects.length} selected)</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-48 overflow-y-auto p-2 border border-gray-200 rounded-lg bg-gray-50">
              {UACE_SUBJECTS.map((subj) => (
                <label key={subj} className="flex items-center gap-2 cursor-pointer hover:bg-white rounded px-2 py-1">
                  <input
                    type="checkbox"
                    checked={selectedSubjects.includes(subj)}
                    onChange={() => toggleSubject(subj)}
                    className="accent-blue-600"
                  />
                  <span className="text-xs text-gray-700">{subj}</span>
                </label>
              ))}
            </div>
            {selectedSubjects.length < 2 && (
              <p className="text-xs text-amber-600 mt-1">Select at least 2 subjects for accurate recommendations</p>
            )}
          </div>
        </>
      )}

      {/* Diploma fields */}
      {route === "diploma" && (
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Diploma Class <span className="text-red-500">*</span></label>
            <select
              {...register("diploma_class", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select class...</option>
              <option value="Pass">Pass</option>
              <option value="Credit">Credit</option>
              <option value="Distinction">Distinction</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Diploma Field/Course <span className="text-red-500">*</span></label>
            <input
              {...register("diploma_field", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Computer Science, Clinical Medicine, Business Administration"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Institution</label>
            <input
              {...register("diploma_institution")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Uganda Polytechnic Kyambogo"
            />
          </div>
        </div>
      )}

      {/* National Certificate fields */}
      {route === "national_cert" && (
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Certificate Class <span className="text-red-500">*</span></label>
            <select
              {...register("national_cert_class", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select class...</option>
              <option value="Pass">Pass</option>
              <option value="Credit">Credit</option>
              <option value="Distinction">Distinction</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Certificate Field/Course <span className="text-red-500">*</span></label>
            <input
              {...register("national_cert_field", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Electrical Installation, Plumbing, Catering"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Institution</label>
            <input
              {...register("national_cert_institution")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Uganda Technical College"
            />
          </div>
        </div>
      )}

      {/* Bachelors/Postgraduate fields */}
      {route === "bachelors" && (
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Degree Class <span className="text-red-500">*</span></label>
            <select
              {...register("bachelors_class", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select class...</option>
              <option value="First Class">First Class</option>
              <option value="Second Class Upper">Second Class Upper (2:1)</option>
              <option value="Second Class Lower">Second Class Lower (2:2)</option>
              <option value="Third Class">Third Class</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Degree Field <span className="text-red-500">*</span></label>
            <input
              {...register("bachelors_field", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Business Administration, Computer Science"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Years of Work Experience</label>
            <input
              type="number" min={0} max={50}
              {...register("work_experience_years", { valueAsNumber: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. 3"
            />
          </div>
        </div>
      )}

      {/* Masters fields */}
      {route === "masters" && (
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Master's Degree Class <span className="text-red-500">*</span></label>
            <select
              {...register("masters_class", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select class...</option>
              <option value="Distinction">Distinction</option>
              <option value="Merit">Merit</option>
              <option value="Pass">Pass</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Master's Field <span className="text-red-500">*</span></label>
            <input
              {...register("masters_field", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Business Administration, Computer Science"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Years of Work Experience</label>
            <input
              type="number" min={0} max={50}
              {...register("work_experience_years", { valueAsNumber: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. 5"
            />
          </div>
        </div>
      )}

      {/* PhD fields */}
      {route === "phd" && (
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">PhD Field <span className="text-red-500">*</span></label>
            <input
              {...register("phd_field", { required: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Computer Science, Business Administration"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Research Experience (years)</label>
            <input
              type="number" min={0} max={50}
              {...register("research_experience_years", { valueAsNumber: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. 3"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-1">Publications (optional)</label>
            <input
              type="number" min={0}
              {...register("publications_count", { valueAsNumber: true })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. 5"
            />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 rounded-xl text-sm transition-colors"
      >
        {loading ? "Finding programmes…" : "Find Matching Programmes"}
      </button>
    </form>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function RecommendationsPage() {
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiError, setApiError] = useState<{ message: string; detail?: string } | null>(null);

  const [location] = useLocation();
  // Extract qualification type from URL path (e.g., /recommend/o-level -> o-level)
  const pathParts = location.split('/');
  const qualificationType = pathParts.length > 2 ? pathParts[2] : null;

  const handleSubmit = async (data: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    setApiError(null);
    setResult(null);

    try {
      const res = await fetch("/api/v1/recommendations", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const json = await res.json();

      if (!res.ok) {
        setApiError({
          message: json.error || "Could not fetch recommendations",
          detail: json.alternative || json.code,
        });
        return;
      }

      setResult(json);
    } catch (err) {
      setError("Network error. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">

        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">🎓</span>
            <h1 className="text-2xl font-bold text-gray-900">Programme Recommendations</h1>
          </div>
          <p className="text-sm text-gray-500 leading-relaxed">
            Enter your qualifications to see which KIU programmes you're eligible for,
            matched against <strong>NCHE Uganda minimum entry requirements</strong>.
          </p>
        </div>

        {/* NCHE info banner */}
        <div className="flex gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl text-sm">
          <span className="text-xl shrink-0">ℹ️</span>
          <div className="text-blue-800">
            <p className="font-semibold mb-1">KIU Admission Routes (NCHE-Approved)</p>
            <ul className="text-xs space-y-0.5 list-disc list-inside">
              <li><strong>UACE Direct:</strong> UCE ≥5 passes + UACE ≥2 principal passes (same sitting)</li>
              <li><strong>Diploma Entry:</strong> Credit/Pass Diploma from NCHE-recognised institution</li>
              <li><strong>Postgraduate:</strong> Bachelor's degree (2nd Class Lower or above)</li>
            </ul>
            <p className="text-xs mt-2 text-blue-600">
              KIU admits 3 times/year: <strong>August</strong> · <strong>January</strong> · <strong>March</strong>
            </p>
          </div>
        </div>

         {/* Form */}
         <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
           <h2 className="text-base font-semibold text-gray-900 mb-5">Your Qualifications</h2>
           {qualificationType && (
             <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
               Mode: <span className="font-semibold capitalize">{qualificationType}</span>
             </div>
           )}
           <QualificationsForm onSubmit={handleSubmit} loading={loading} qualificationType={qualificationType} />
         </div>

        {/* API Error (e.g. UCE insufficient) */}
        {apiError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <div className="flex items-start gap-3">
              <span className="text-xl shrink-0">❌</span>
              <div>
                <p className="font-semibold text-red-800 text-sm">{apiError.message}</p>
                {apiError.detail && (
                  <p className="text-xs text-red-600 mt-1">{apiError.detail}</p>
                )}
                <p className="text-xs text-red-500 mt-2">
                  Contact KIU Admissions: <strong>admissions@kiu.ac.ug</strong> · +256-760-502660
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Network error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-8">
            {/* Summary bar */}
            <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-green-400 inline-block" />
                  <span className="font-semibold text-green-700">{result.recommended.length} Fully Eligible</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-amber-400 inline-block" />
                  <span className="font-semibold text-amber-700">{result.partially_eligible.length} Conditionally Eligible</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-400 inline-block" />
                  <span className="text-red-600">{result.not_eligible.length} Not Currently Eligible</span>
                </div>
              </div>

              <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500">
                {result.nche_note}
              </div>
            </div>

            {/* Recommended */}
            <Section title="Recommended Programmes" icon="✅" count={result.recommended.length} defaultOpen>
              {result.recommended.map((p, i) => (
                <ProgrammeCard key={p.id} programme={p} rank={i + 1} />
              ))}
            </Section>

            {/* Conditionally eligible */}
            <Section title="Conditionally Eligible" icon="⚠️" count={result.partially_eligible.length} defaultOpen>
              {result.partially_eligible.map((p) => (
                <ProgrammeCard key={p.id} programme={p} />
              ))}
            </Section>

            {/* Not eligible */}
            <Section title="Not Currently Eligible" icon="❌" count={result.not_eligible.length} defaultOpen={false}>
              {result.not_eligible.map((p) => (
                <ProgrammeCard key={p.id} programme={p} />
              ))}
            </Section>

            {/* Apply CTA */}
            {result.recommended.length > 0 && (
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-6 text-white text-center">
                <h3 className="text-lg font-bold mb-1">Ready to Apply?</h3>
                <p className="text-blue-100 text-sm mb-4">
                  You qualify for {result.recommended.length} programme{result.recommended.length > 1 ? "s" : ""}. Next intake applications are open now.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <a
                    href={`/apply/${mapEntryRouteToQualification((result?.entry_route as EntryRoute) || "uace_direct")}`}
                    className="bg-white text-blue-700 font-semibold px-6 py-2.5 rounded-xl text-sm hover:bg-blue-50 transition-colors"
                  >
                    Start Application
                  </a>
                  <a
                    href="mailto:admissions@kiu.ac.ug"
                    className="border border-blue-300 text-white font-medium px-6 py-2.5 rounded-xl text-sm hover:bg-blue-500 transition-colors"
                  >
                    Contact Admissions
                  </a>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
