import { useState, useRef } from 'react';
import { useLocation } from 'wouter';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useListPrograms } from '@workspace/api-client-react';
import { Button, Input, Label, Card, Textarea } from '@/components/ui/shared';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, ArrowRight, Upload, CheckCircle, Plus, Trash2, Info, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

// ── Countries List ────────────────────────────────────────────────────────────

const COUNTRIES = [
  "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
  "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
  "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia",
  "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica",
  "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador",
  "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France",
  "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
  "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland",
  "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo",
  "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania",
  "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius",
  "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia",
  "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
  "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland",
  "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino",
  "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands",
  "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland",
  "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey",
  "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu",
  "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
];

// ── UNEB Subject lists ────────────────────────────────────────────────────────

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

const ALEVEL_PRINCIPAL_SUBJECTS = [
  "Mathematics", "Physics", "Chemistry", "Biology", "Geography",
  "History", "Literature in English", "Economics",
  "Entrepreneurship Education", "Art & Design", "Technical Drawing",
  "Christian Religious Education (CRE)", "Islamic Religious Education (IRE)",
  "Divinity", "Fine Art", "Music",
];

const ALEVEL_SUBSIDIARY_SUBJECTS = [
  "General Paper", "Subsidiary ICT", "Subsidiary Mathematics",
];

const ALEVEL_GRADES = [
  { label: "A – 6 points", value: "A", points: 6 },
  { label: "B – 5 points", value: "B", points: 5 },
  { label: "C – 4 points", value: "C", points: 4 },
  { label: "D – 3 points", value: "D", points: 3 },
  { label: "E – 2 points", value: "E", points: 2 },
  { label: "O – 1 point", value: "O", points: 1 },
  { label: "F – Fail (0 points)", value: "F", points: 0 },
];

// ── Schemas ───────────────────────────────────────────────────────────────────

const oGradeEntry = z.object({
  subject: z.string().min(1, "Subject required"),
  grade: z.string().min(1, "Grade required"),
  points: z.coerce.number(),
});

const aGradeEntry = z.object({
  subject: z.string().min(1, "Subject required"),
  grade: z.string().min(1, "Grade required"),
  points: z.coerce.number(),
  subjectType: z.enum(["principal", "subsidiary"]),
});

const applySchema = z
  .object({
    programId: z.coerce.number().min(1, "Please select a program"),
    examLevel: z.enum(["o_level", "a_level", "diploma", "hec"]),

    // O-Level inputs (required when examLevel is o_level or a_level)
    oLevelYear: z.coerce.number().min(1990).max(new Date().getFullYear()).optional(),
    oLevelIndexNumber: z.string().optional(),
    oLevelGrades: z.array(oGradeEntry).optional(),
    oLevelCurriculum: z.enum(["old", "new"]).optional(),

    // A-Level inputs (required when examLevel is a_level)
    aLevelYear: z.coerce.number().min(1990).max(new Date().getFullYear()).optional(),
    aLevelIndexNumber: z.string().optional(),
    aLevelGrades: z.array(aGradeEntry).optional(),

    // Certificate-only inputs for degree qualification via diploma/hec
    certYear: z.coerce.number().min(1990).max(new Date().getFullYear()).optional(),
    certIndexNumber: z.string().optional(),

    dateOfBirth: z.string().optional(),
    gender: z.enum(["male", "female", "other"]),
    nationality: z.string().default("Ugandan"),
    district: z.string().optional(),
    nextOfKinName: z.string().optional(),
    nextOfKinPhone: z.string().optional(),
    nextOfKinRelationship: z.string().optional(),
  });

type ApplyForm = z.infer<typeof applySchema>;

type Step = "program" | "olevel" | "alevel" | "cert" | "personal" | "upload" | "review";

const STEPS: { key: Step; label: string }[] = [
  { key: "program", label: "Program" },
  { key: "olevel", label: "O-Level Results" },
  { key: "alevel", label: "A-Level Results" },
  { key: "cert", label: "Certificate Details" },
  { key: "personal", label: "Personal Info" },
  { key: "upload", label: "Certificates" },
  { key: "review", label: "Review & Submit" },
];

// ── Component ─────────────────────────────────────────────────────────────────

type ApplyTarget = "degree" | "diploma" | "hec";
type DegreeQualification = "a_level" | "diploma" | "hec";
type ExamLevel = "o_level" | "a_level" | "diploma" | "hec";
type Campus = "kampala" | "western";

function readDegreeQualificationFromUrl(): DegreeQualification {
  if (typeof window === "undefined") return "a_level";
  const sp = new URLSearchParams(window.location.search);
  const q = sp.get("qualification");
  if (q === "a_level" || q === "diploma" || q === "hec") return q;
  return "a_level";
}

export default function Apply({ target }: { target: ApplyTarget }) {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [selectedCampus, setSelectedCampus] = useState<Campus | "all">("kampala");
  const { data: programsData, isLoading: programsLoading } = useListPrograms();

  const [step, setStep] = useState<Step>("program");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [applicationId, setApplicationId] = useState<number | null>(null);
  const [olevelFile, setOlevelFile] = useState<File | null>(null);
  const [alevelFile, setAlevelFile] = useState<File | null>(null);
  const [diplomaFile, setDiplomaFile] = useState<File | null>(null);
  const [hecFile, setHecFile] = useState<File | null>(null);
  const [uploadingCerts, setUploadingCerts] = useState(false);
  const olevelInputRef = useRef<HTMLInputElement>(null);
  const alevelInputRef = useRef<HTMLInputElement>(null);
  const diplomaInputRef = useRef<HTMLInputElement>(null);
  const hecInputRef = useRef<HTMLInputElement>(null);

  const allPrograms = (programsData as any)?.programs ?? [];
  const programs = allPrograms.filter((p: any) => p.campus === selectedCampus);

  const degreeQualification = readDegreeQualificationFromUrl();
  const examLevel: ExamLevel = target === "degree" ? degreeQualification : "o_level";
  const shouldShowALevel = examLevel === "a_level";
  const shouldShowOlevel = examLevel === "o_level";
  const shouldShowCert = examLevel === "diploma" || examLevel === "hec";

  const { register, control, handleSubmit, watch, setValue, getValues, formState: { errors } } = useForm<ApplyForm>({
    resolver: zodResolver(applySchema),
    defaultValues: {
      examLevel,
      nationality: "Ugandan",
      oLevelYear: new Date().getFullYear() - 2,
      oLevelCurriculum: "new",
      oLevelGrades: [{ subject: "", grade: "", points: 0 }],
      aLevelGrades: [{ subject: "", grade: "", points: 0, subjectType: "principal" }],
    },
  });

  const watchExamLevel = watch("examLevel");
  const watchProgramId = watch("programId");
  const watchCurriculum = watch("oLevelCurriculum");
  const selectedProgram = programs.find((p: any) => p.id === Number(watchProgramId));

  // Get the correct O-Level grades based on curriculum
  const oLevelGrades = watchCurriculum === "old" ? OLEVEL_GRADES_OLD : OLEVEL_GRADES_NEW;

  // Field arrays
  const oLevelArray = useFieldArray({ control, name: "oLevelGrades" });
  const aLevelArray = useFieldArray({ control, name: "aLevelGrades" as any });

  const stepOrder: Step[] = shouldShowALevel
    ? ["program", "olevel", "alevel", "personal", "upload", "review"]
    : shouldShowOlevel
      ? ["program", "olevel", "personal", "upload", "review"]
      : ["program", "cert", "personal", "upload", "review"];

  const currentIdx = stepOrder.indexOf(step);
  const canGoNext = currentIdx < stepOrder.length - 1;
  const canGoBack = currentIdx > 0;

  // Validate current step before proceeding
  const validateCurrentStep = (): boolean => {
    const values = getValues();
    
    switch (step) {
      case "program":
        if (!values.programId || values.programId < 1) {
          toast({ title: "Please select a program", variant: "destructive" });
          return false;
        }
        break;
      case "olevel":
        if (!values.oLevelYear || !values.oLevelIndexNumber || !values.oLevelGrades || values.oLevelGrades.length < 5) {
          toast({ title: "Please complete all O-Level fields", description: "Year, index number, and at least 5 subjects are required", variant: "destructive" });
          return false;
        }
        break;
      case "alevel":
        if (!values.aLevelYear || !values.aLevelGrades || values.aLevelGrades.length < 1) {
          toast({ title: "Please complete all A-Level fields", description: "Year and at least 1 subject are required", variant: "destructive" });
          return false;
        }
        break;
      case "cert":
        if (!values.certYear || !values.certIndexNumber) {
          toast({ title: "Please complete certificate details", variant: "destructive" });
          return false;
        }
        break;
      case "personal":
        if (!values.dateOfBirth || !values.gender || !values.district || !values.nextOfKinName || !values.nextOfKinPhone || !values.nextOfKinRelationship) {
          toast({ title: "Please complete all personal information", description: "All fields are required", variant: "destructive" });
          return false;
        }
        break;
    }
    return true;
  };

  const goNext = () => { 
    if (canGoNext && validateCurrentStep()) {
      setStep(stepOrder[currentIdx + 1]); 
    }
  };
  const goBack = () => { if (canGoBack) setStep(stepOrder[currentIdx - 1]); };

  // ── O-Level grade entry helper ─────────────────────────────────────────────
  function OLevelRow({ index }: { index: number }) {
    const g = watch(`oLevelGrades.${index}.grade`);
    return (
      <div className="grid grid-cols-[1fr_1fr_auto] gap-3 items-end">
        <div className="space-y-1">
          {index === 0 && <Label className="text-xs">Subject</Label>}
          <select {...register(`oLevelGrades.${index}.subject`)} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm">
            <option value="">Select subject…</option>
            {OLEVEL_SUBJECTS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="space-y-1">
          {index === 0 && <Label className="text-xs">Grade</Label>}
          <select
            {...register(`oLevelGrades.${index}.grade`)}
            onChange={(e) => {
              const found = oLevelGrades.find((g) => g.value === e.target.value);
              setValue(`oLevelGrades.${index}.grade`, e.target.value);
              setValue(`oLevelGrades.${index}.points`, found?.points ?? 0);
            }}
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm"
          >
            <option value="">Grade…</option>
            {oLevelGrades.map((gr) => <option key={gr.value} value={gr.value}>{gr.label}</option>)}
          </select>
        </div>
        <button type="button" onClick={() => oLevelArray.remove(index)} disabled={oLevelArray.fields.length <= 1} className="h-10 w-10 flex items-center justify-center text-muted-foreground hover:text-destructive disabled:opacity-30">
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    );
  }

  // ── A-Level grade entry helper ─────────────────────────────────────────────
  function ALevelRow({ index }: { index: number }) {
    const subjectType = watch(`aLevelGrades.${index}.subjectType` as any);
    const subjects = subjectType === "principal" ? ALEVEL_PRINCIPAL_SUBJECTS : ALEVEL_SUBSIDIARY_SUBJECTS;
    return (
      <div className="grid grid-cols-[1fr_100px_1fr_auto] gap-3 items-end">
        <div className="space-y-1">
          {index === 0 && <Label className="text-xs">Subject</Label>}
          <select {...register(`aLevelGrades.${index}.subject` as any)} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm">
            <option value="">Select…</option>
            {subjects.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="space-y-1">
          {index === 0 && <Label className="text-xs">Type</Label>}
          <select
            {...register(`aLevelGrades.${index}.subjectType` as any)}
            onChange={(e) => {
              setValue(`aLevelGrades.${index}.subject` as any, "");
              setValue(`aLevelGrades.${index}.subjectType` as any, e.target.value);
            }}
            className="h-10 px-2 rounded-lg border border-border bg-white text-xs"
          >
            <option value="principal">Principal</option>
            <option value="subsidiary">Subsidiary</option>
          </select>
        </div>
        <div className="space-y-1">
          {index === 0 && <Label className="text-xs">Grade</Label>}
          <select
            {...register(`aLevelGrades.${index}.grade` as any)}
            onChange={(e) => {
              const found = ALEVEL_GRADES.find((g) => g.value === e.target.value);
              setValue(`aLevelGrades.${index}.grade` as any, e.target.value);
              setValue(`aLevelGrades.${index}.points` as any, found?.points ?? 0);
            }}
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm"
          >
            <option value="">Grade…</option>
            {ALEVEL_GRADES.map((gr) => <option key={gr.value} value={gr.value}>{gr.label}</option>)}
          </select>
        </div>
        <button type="button" onClick={() => aLevelArray.remove(index)} disabled={(aLevelArray.fields as any).length <= 1} className="h-10 w-10 flex items-center justify-center text-muted-foreground hover:text-destructive disabled:opacity-30">
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    );
  }

  // ── Form submit ────────────────────────────────────────────────────────────
  const onSubmit = async (data: ApplyForm) => {
    setIsSubmitting(true);
    try {
      const token = localStorage.getItem("kiu_token");

      const unebGrades: any = {};
      if (examLevel === "o_level" || examLevel === "a_level") {
        unebGrades.olevel = (data.oLevelGrades ?? []).map((g) => ({
          ...g,
          year: data.oLevelYear,
          indexNumber: data.oLevelIndexNumber,
          curriculum: data.oLevelCurriculum,
        }));
      }
      if (examLevel === "a_level" && data.aLevelGrades?.length) {
        unebGrades.alevel = data.aLevelGrades.map((g) => ({
          ...g,
          year: data.aLevelYear,
          indexNumber: data.aLevelIndexNumber,
        }));
      }

      const examYear =
        examLevel === "a_level"
          ? data.aLevelYear
          : examLevel === "o_level"
            ? data.oLevelYear
            : data.certYear;

      const indexNumber =
        examLevel === "a_level"
          ? data.aLevelIndexNumber || data.oLevelIndexNumber
          : examLevel === "o_level"
            ? data.oLevelIndexNumber
            : data.certIndexNumber;

      const payload = {
        programIds: [data.programId],
        examLevel,
        examYear,
        indexNumber,
        unebGrades,
        dateOfBirth: data.dateOfBirth,
        gender: data.gender,
        nationality: data.nationality,
        district: data.district,
        nextOfKinName: data.nextOfKinName,
        nextOfKinPhone: data.nextOfKinPhone,
        nextOfKinRelationship: data.nextOfKinRelationship,
      };

      const res = await fetch(`${BASE}/api/admission/applications`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.message || "Submission failed");

      setApplicationId(json.id);
      setStep("upload");
    } catch (err: any) {
      toast({ title: "Submission failed", description: err.message, variant: "destructive" });
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Certificate upload ─────────────────────────────────────────────────────
  const uploadCertificates = async () => {
    if (!applicationId) return;
    setUploadingCerts(true);
    const token = localStorage.getItem("kiu_token");
    let allOk = true;

    const upload = async (file: File, type: "olevel" | "alevel" | "diploma" | "hec") => {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("type", type);
      const res = await fetch(`${BASE}/api/admission/applications/${applicationId}/certificate`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      if (!res.ok) allOk = false;
    };

    try {
      if (olevelFile) await upload(olevelFile, "olevel");
      if (examLevel === "a_level" && alevelFile) await upload(alevelFile, "alevel");
      if (examLevel === "diploma" && diplomaFile) await upload(diplomaFile, "diploma");
      if (examLevel === "hec" && hecFile) await upload(hecFile, "hec");
    } catch {
      allOk = false;
    }

    setUploadingCerts(false);
    if (allOk) {
      toast({ title: "Application Submitted!", description: "Track your status in the dashboard." });
      setLocation("/dashboard");
    } else {
      toast({ title: "Upload issue", description: "Application saved but some certificates failed to upload.", variant: "destructive" });
      setLocation("/dashboard");
    }
  };

  // ── Progress bar ───────────────────────────────────────────────────────────
  const visibleSteps = STEPS.filter((s) => stepOrder.includes(s.key));
  const stepProgress = ((currentIdx + 1) / stepOrder.length) * 100;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8">
        <button onClick={() => (currentIdx === 0 ? setLocation("/dashboard") : goBack())} className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> {currentIdx === 0 ? "Back to Dashboard" : "Previous Step"}
        </button>
        <h1 className="text-3xl font-display font-bold text-primary">Admission Application</h1>
        <p className="text-muted-foreground mt-1">KIU Online Admissions — {new Date().getFullYear()}/{new Date().getFullYear() + 1} Academic Year</p>
      </div>

      {/* Progress */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          {visibleSteps.map((s, i) => (
            <div key={s.key} className="flex flex-col items-center gap-1 flex-1">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all
                ${stepOrder.indexOf(step) >= i ? "bg-primary border-primary text-white" : "border-border text-muted-foreground bg-white"}`}>
                {stepOrder.indexOf(step) > i ? <CheckCircle className="w-4 h-4" /> : i + 1}
              </div>
              <span className="text-[10px] text-center text-muted-foreground hidden sm:block">{s.label}</span>
            </div>
          ))}
        </div>
        <div className="h-1.5 bg-secondary rounded-full">
          <div className="h-full bg-primary rounded-full transition-all duration-500" style={{ width: `${stepProgress}%` }} />
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >

            {/* ── STEP: Program Selection ─────────────────────────────────── */}
            {step === "program" && (
              <Card className="p-8">
                <h2 className="text-xl font-bold mb-2">Choose Your Program</h2>
                <p className="text-muted-foreground text-sm mb-6">Select the program you are applying for.</p>

                {/* Campus Selection */}
                <div className="mb-6">
                  <Label className="text-sm font-semibold mb-3 block">Select Campus</Label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setSelectedCampus("kampala")}
                      className={`p-3 rounded-xl border-2 text-sm font-medium transition-all
                        ${selectedCampus === "kampala" ? "border-primary bg-primary/5 text-primary" : "border-border hover:border-primary/30"}`}
                    >
                      Kampala Campus
                    </button>
                    <button
                      type="button"
                      onClick={() => setSelectedCampus("western")}
                      className={`p-3 rounded-xl border-2 text-sm font-medium transition-all
                        ${selectedCampus === "western" ? "border-primary bg-primary/5 text-primary" : "border-border hover:border-primary/30"}`}
                    >
                      Western Campus
                    </button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {selectedCampus === "kampala" && "📍 Kampala Campus (Main) - Kansanga, Kampala"}
                    {selectedCampus === "western" && "📍 Western Campus - Ishaka, Bushenyi (Medical programs)"}
                  </p>
                </div>

                {programsLoading ? (
                  <p className="text-muted-foreground">Loading programs…</p>
                ) : (
                  <div className="space-y-4">
                    {(() => {
                      const allowedLevel = target === "degree" ? "degree" : target; // diploma | hec
                      const levelLabel =
                        allowedLevel === "degree"
                          ? "Undergraduate Degrees"
                          : allowedLevel === "diploma"
                            ? "Diploma Programmes"
                            : "HEC Programmes";

                      // Group programs by campus
                      const kampalaPrograms = programs.filter((p: any) => p.level === allowedLevel && p.campus === "kampala");
                      const westernPrograms = programs.filter((p: any) => p.level === allowedLevel && p.campus === "western");

                      const renderProgramList = (programList: any[], campusName: string) => (
                        <div className="grid gap-3">
                          {programList.map((p: any) => (
                            <label
                              key={p.id}
                              className={`flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all
                                ${Number(watchProgramId) === p.id ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"}`}
                            >
                              <input
                                type="radio"
                                value={p.id}
                                {...register("programId")}
                                className="mt-1 accent-primary"
                              />
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <p className="font-semibold text-sm">{p.name}</p>
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium
                                    ${p.campus === "kampala" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"}`}>
                                    {p.campus === "kampala" ? "Kampala" : "Western"}
                                  </span>
                                </div>
                                <p className="text-xs text-muted-foreground">
                                  {p.faculty} · {p.duration}
                                </p>
                                {p.entryRequirements && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    {p.entryRequirements}
                                  </p>
                                )}
                              </div>
                            </label>
                          ))}
                        </div>
                      );

                      return (
                        <div className="space-y-6">
                          {selectedCampus === "kampala" && kampalaPrograms.length > 0 && (
                            <div>
                              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-2">
                                {levelLabel} - Kampala Campus
                                <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">📍 Kansanga</span>
                              </h3>
                              {renderProgramList(kampalaPrograms, "Kampala")}
                            </div>
                          )}
                          
                          {selectedCampus === "western" && westernPrograms.length > 0 && (
                            <div>
                              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-2">
                                {levelLabel} - Western Campus
                                <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-100 text-green-700">📍 Ishaka</span>
                              </h3>
                              {renderProgramList(westernPrograms, "Western")}
                            </div>
                          )}

                          {kampalaPrograms.length === 0 && westernPrograms.length === 0 && (
                            <p className="text-muted-foreground text-sm">No programs available for the selected criteria.</p>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                )}
                {errors.programId && <p className="text-xs text-destructive mt-2">{errors.programId.message}</p>}

                <div className="mt-6 flex justify-end">
                  <Button type="button" onClick={goNext} disabled={!watchProgramId} className="gap-2">
                    Next: {(shouldShowOlevel || shouldShowALevel) ? "O-Level Results" : "Certificate Details"}{" "}
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            )}

            {/* ── STEP: O-Level Results ───────────────────────────────────── */}
            {step === "olevel" && (
              <Card className="p-8">
                <h2 className="text-xl font-bold mb-1">Uganda Certificate of Education (UCE)</h2>
                <p className="text-muted-foreground text-sm mb-6">Enter your O-Level results as they appear on your UNEB certificate. Include at least 5 subjects.</p>

                <div className="grid md:grid-cols-3 gap-5 mb-6">
                  <div className="space-y-2">
                    <Label>Examination Year <span className="text-primary">(Required)</span></Label>
                    <Input type="number" {...register("oLevelYear")} min={1990} max={new Date().getFullYear()} />
                    {errors.oLevelYear && <p className="text-xs text-destructive">{errors.oLevelYear.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>UNEB Index Number <span className="text-primary">(Required)</span></Label>
                    <Input placeholder="e.g. U0001/001" {...register("oLevelIndexNumber")} />
                    {errors.oLevelIndexNumber && <p className="text-xs text-destructive">{errors.oLevelIndexNumber.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>Curriculum Type</Label>
                    <select {...register("oLevelCurriculum")} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm">
                      <option value="new">New Curriculum (D1-D8, F)</option>
                      <option value="old">Old Curriculum (D1, D2, C3-C6, P7, P8, F9)</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-3">
                  {oLevelArray.fields.map((_, i) => (
                    <OLevelRow key={i} index={i} />
                  ))}
                </div>

                <button
                  type="button"
                  onClick={() => oLevelArray.append({ subject: "", grade: "", points: 0 })}
                  disabled={oLevelArray.fields.length >= OLEVEL_SUBJECTS.length}
                  className="mt-4 flex items-center gap-2 text-sm font-semibold text-primary hover:text-primary/80 disabled:opacity-40"
                >
                  <Plus className="w-4 h-4" /> Add Subject
                </button>

                <div className="mt-3 flex items-start gap-2 bg-blue-50 text-blue-700 p-3 rounded-lg text-xs">
                  <Info className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>
                    <strong>UCE Grading:</strong>{" "}
                    {watchCurriculum === "old" 
                      ? "Old: D1, D2 (Distinctions), C3-C6 (Credits), P7, P8 (Passes), F9 (Fail)" 
                      : "New: D1, D2 (Distinctions), D3-D6 (Credits), D7, D8 (Passes), F (Fail)"}
                  </span>
                </div>
                {errors.oLevelGrades && <p className="text-xs text-destructive mt-2">{errors.oLevelGrades.message as string}</p>}

                <div className="mt-6 flex justify-end">
                  <Button type="button" onClick={goNext} className="gap-2">
                    Next {shouldShowALevel ? ": A-Level Results" : ": Personal Info"} <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            )}

            {/* ── STEP: Certificate Details ─────────────────────────────────── */}
            {step === "cert" && (
              <Card className="p-8">
                <h2 className="text-xl font-bold mb-1">Certificate Details</h2>
                <p className="text-muted-foreground text-sm mb-6">
                  Enter your {examLevel === "diploma" ? "Diploma" : "HEC"} certificate year and index number.
                </p>

                <div className="grid md:grid-cols-2 gap-5 mb-6">
                  <div className="space-y-2">
                    <Label>Certificate Year <span className="text-primary">(Required)</span></Label>
                    <Input type="number" {...register("certYear")} min={1990} max={new Date().getFullYear()} />
                    {errors.certYear && <p className="text-xs text-destructive">{errors.certYear.message as string}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>Certificate Index Number <span className="text-primary">(Required)</span></Label>
                    <Input
                      placeholder={examLevel === "diploma" ? "e.g. D0001/001" : "e.g. H0001/001"}
                      {...register("certIndexNumber")}
                    />
                    {errors.certIndexNumber && <p className="text-xs text-destructive">{errors.certIndexNumber.message as string}</p>}
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <Button type="button" onClick={goNext} className="gap-2">
                    Next: Personal Info <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            )}

            {/* ── STEP: A-Level Results ───────────────────────────────────── */}
            {step === "alevel" && (
              <Card className="p-8">
                <h2 className="text-xl font-bold mb-1">Uganda Advanced Certificate of Education (UACE)</h2>
                <p className="text-muted-foreground text-sm mb-6">Enter your A-Level results. Degree programs require at least 2 principal subjects.</p>

                <div className="grid md:grid-cols-2 gap-5 mb-6">
                  <div className="space-y-2">
                    <Label>Examination Year <span className="text-primary">(Required)</span></Label>
                    <Input type="number" {...register("aLevelYear")} min={1990} max={new Date().getFullYear()} />
                  </div>
                  <div className="space-y-2">
                    <Label>UNEB Index Number <span className="text-primary">(Required)</span></Label>
                    <Input placeholder="e.g. A001/001" {...register("aLevelIndexNumber")} />
                  </div>
                </div>

                <div className="space-y-3">
                  {(aLevelArray.fields as any).map((_: any, i: number) => (
                    <ALevelRow key={i} index={i} />
                  ))}
                </div>

                <button
                  type="button"
                  onClick={() => (aLevelArray.append as any)({ subject: "", grade: "", points: 0, subjectType: "principal" })}
                  className="mt-4 flex items-center gap-2 text-sm font-semibold text-primary hover:text-primary/80"
                >
                  <Plus className="w-4 h-4" /> Add Subject
                </button>

                <div className="mt-3 flex items-start gap-2 bg-blue-50 text-blue-700 p-3 rounded-lg text-xs">
                  <Info className="w-4 h-4 mt-0.5 shrink-0" />
                  <span><strong>UACE Grading:</strong> A=6, B=5, C=4, D=3, E=2, O=1, F=0. You must have General Paper as subsidiary.</span>
                </div>

                <div className="mt-6 flex justify-end">
                  <Button type="button" onClick={goNext} className="gap-2">
                    Next: Personal Info <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            )}

            {/* ── STEP: Personal Info ─────────────────────────────────────── */}
            {step === "personal" && (
              <Card className="p-8">
                <h2 className="text-xl font-bold mb-6">Personal Information</h2>

                <div className="grid md:grid-cols-3 gap-5 mb-5">
                  <div className="space-y-2">
                    <Label>Date of Birth <span className="text-primary">(Required)</span></Label>
                    <Input type="date" {...register("dateOfBirth")} max={new Date().toISOString().split("T")[0]} />
                    {errors.dateOfBirth && <p className="text-xs text-destructive">{errors.dateOfBirth.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>Gender <span className="text-primary">(Required)</span></Label>
                    <select {...register("gender")} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm">
                      <option value="">Select…</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                    {errors.gender && <p className="text-xs text-destructive">{errors.gender.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>Nationality</Label>
                    <select {...register("nationality")} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm">
                      {COUNTRIES.map((country) => (
                        <option key={country} value={country}>{country}</option>
                      ))}
                    </select>
                    {errors.nationality && <p className="text-xs text-destructive">{errors.nationality.message}</p>}
                  </div>
                </div>

                <div className="space-y-2 mb-5">
                  <Label>District of Origin <span className="text-primary">(Required)</span></Label>
                  <Input {...register("district")} placeholder="e.g. Kampala" />
                  {errors.district && <p className="text-xs text-destructive">{errors.district.message}</p>}
                </div>

                <div className="border-t border-border pt-6 mb-5">
                  <h3 className="font-bold mb-4">Next of Kin</h3>
                  <div className="grid md:grid-cols-3 gap-5">
                    <div className="space-y-2">
                      <Label>Full Name <span className="text-primary">(Required)</span></Label>
                      <Input {...register("nextOfKinName")} />
                      {errors.nextOfKinName && <p className="text-xs text-destructive">{errors.nextOfKinName.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label>Phone <span className="text-primary">(Required)</span></Label>
                      <Input {...register("nextOfKinPhone")} />
                      {errors.nextOfKinPhone && <p className="text-xs text-destructive">{errors.nextOfKinPhone.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label>Relationship <span className="text-primary">(Required)</span></Label>
                      <Input {...register("nextOfKinRelationship")} placeholder="e.g. Father, Mother" />
                      {errors.nextOfKinRelationship && <p className="text-xs text-destructive">{errors.nextOfKinRelationship.message}</p>}
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <Button type="submit" isLoading={isSubmitting} className="gap-2">
                    Save & Continue to Certificates <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            )}

            {/* ── STEP: Certificate Upload ────────────────────────────────── */}
            {step === "upload" && (
              <Card className="p-8">
                <div className="flex items-center gap-3 mb-2">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  <h2 className="text-xl font-bold">Upload Academic Certificates</h2>
                </div>
                <p className="text-muted-foreground text-sm mb-8">
                  Upload scanned copies of your UNEB certificates. Accepted formats: PDF, JPG, PNG (max 5MB each). You can skip and upload later from your dashboard.
                </p>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* O-Level Certificate (required for o_level and a_level modes) */}
                  {(examLevel === "o_level" || examLevel === "a_level") && (
                    <div
                      onClick={() => olevelInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-2xl p-6 cursor-pointer transition-all text-center
                        ${olevelFile ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-secondary/50"}`}
                    >
                      <FileText className={`w-10 h-10 mx-auto mb-3 ${olevelFile ? "text-primary" : "text-muted-foreground"}`} />
                      <p className="font-semibold text-sm mb-1">O-Level (UCE) Certificate</p>
                      {olevelFile ? (
                        <p className="text-xs text-primary font-medium truncate">{olevelFile.name}</p>
                      ) : (
                        <p className="text-xs text-muted-foreground">Click to upload PDF/JPG/PNG</p>
                      )}
                      <input ref={olevelInputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" onChange={(e) => setOlevelFile(e.target.files?.[0] ?? null)} />
                    </div>
                  )}

                  {/* A-Level Certificate (Degree with A-Level qualification) */}
                  {examLevel === "a_level" && (
                    <div
                      onClick={() => alevelInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-2xl p-6 cursor-pointer transition-all text-center
                        ${alevelFile ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-secondary/50"}`}
                    >
                      <FileText className={`w-10 h-10 mx-auto mb-3 ${alevelFile ? "text-primary" : "text-muted-foreground"}`} />
                      <p className="font-semibold text-sm mb-1">A-Level (UACE) Certificate</p>
                      {alevelFile ? (
                        <p className="text-xs text-primary font-medium truncate">{alevelFile.name}</p>
                      ) : (
                        <p className="text-xs text-muted-foreground">Click to upload PDF/JPG/PNG</p>
                      )}
                      <input ref={alevelInputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" onChange={(e) => setAlevelFile(e.target.files?.[0] ?? null)} />
                    </div>
                  )}

                  {/* Diploma Certificate (Degree with Diploma qualification) */}
                  {examLevel === "diploma" && (
                    <div
                      onClick={() => diplomaInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-2xl p-6 cursor-pointer transition-all text-center
                        ${diplomaFile ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-secondary/50"}`}
                    >
                      <FileText className={`w-10 h-10 mx-auto mb-3 ${diplomaFile ? "text-primary" : "text-muted-foreground"}`} />
                      <p className="font-semibold text-sm mb-1">Diploma Certificate</p>
                      {diplomaFile ? (
                        <p className="text-xs text-primary font-medium truncate">{diplomaFile.name}</p>
                      ) : (
                        <p className="text-xs text-muted-foreground">Click to upload PDF/JPG/PNG</p>
                      )}
                      <input ref={diplomaInputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" onChange={(e) => setDiplomaFile(e.target.files?.[0] ?? null)} />
                    </div>
                  )}

                  {/* HEC Certificate (Degree with HEC qualification) */}
                  {examLevel === "hec" && (
                    <div
                      onClick={() => hecInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-2xl p-6 cursor-pointer transition-all text-center
                        ${hecFile ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-secondary/50"}`}
                    >
                      <FileText className={`w-10 h-10 mx-auto mb-3 ${hecFile ? "text-primary" : "text-muted-foreground"}`} />
                      <p className="font-semibold text-sm mb-1">HEC Certificate</p>
                      {hecFile ? (
                        <p className="text-xs text-primary font-medium truncate">{hecFile.name}</p>
                      ) : (
                        <p className="text-xs text-muted-foreground">Click to upload PDF/JPG/PNG</p>
                      )}
                      <input ref={hecInputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" onChange={(e) => setHecFile(e.target.files?.[0] ?? null)} />
                    </div>
                  )}
                </div>

                <div className="mt-8 flex gap-3 justify-end">
                  <Button type="button" variant="outline" onClick={() => setLocation("/dashboard")}>
                    Skip for Now
                  </Button>
                  <Button type="button" isLoading={uploadingCerts} onClick={uploadCertificates} className="gap-2">
                    <Upload className="w-4 h-4" /> Submit Application
                  </Button>
                </div>
              </Card>
            )}

          </motion.div>
        </AnimatePresence>
      </form>
    </div>
  );
}