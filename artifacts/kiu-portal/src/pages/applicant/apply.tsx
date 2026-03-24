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

const OLEVEL_GRADES = [
  { label: "D1 – Distinction 1 (best)", value: "D1", points: 1 },
  { label: "D2 – Distinction 2", value: "D2", points: 2 },
  { label: "D3 – Distinction 3", value: "D3", points: 3 },
  { label: "D4 – Credit 4", value: "D4", points: 4 },
  { label: "D5 – Credit 5", value: "D5", points: 5 },
  { label: "D6 – Credit 6", value: "D6", points: 6 },
  { label: "D7 – Pass 7", value: "D7", points: 7 },
  { label: "D8 – Pass 8", value: "D8", points: 8 },
  { label: "D9 – Pass 9", value: "D9", points: 9 },
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

const applySchema = z.object({
  programId: z.coerce.number().min(1, "Please select a program"),
  examLevel: z.enum(["o_level", "a_level"]),
  oLevelYear: z.coerce.number().min(1990).max(new Date().getFullYear()),
  oLevelIndexNumber: z.string().min(5, "O-Level index number is required"),
  oLevelGrades: z.array(oGradeEntry).min(5, "At least 5 O-Level subjects required"),
  aLevelYear: z.coerce.number().min(1990).max(new Date().getFullYear()).optional(),
  aLevelIndexNumber: z.string().optional(),
  aLevelGrades: z.array(aGradeEntry).optional(),
  personalStatement: z.string().min(50, "At least 50 characters required"),
  dateOfBirth: z.string().min(8, "Date of birth required"),
  gender: z.enum(["male", "female", "other"]),
  nationality: z.string().default("Ugandan"),
  district: z.string().min(2, "District required"),
  nextOfKinName: z.string().min(2, "Name required"),
  nextOfKinPhone: z.string().min(9, "Phone required"),
  nextOfKinRelationship: z.string().min(2, "Relationship required"),
});

type ApplyForm = z.infer<typeof applySchema>;

type Step = "program" | "olevel" | "alevel" | "personal" | "upload" | "review";

const STEPS: { key: Step; label: string }[] = [
  { key: "program", label: "Program" },
  { key: "olevel", label: "O-Level Results" },
  { key: "alevel", label: "A-Level Results" },
  { key: "personal", label: "Personal Info" },
  { key: "upload", label: "Certificates" },
  { key: "review", label: "Review & Submit" },
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function Apply() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const { data: programsData, isLoading: programsLoading } = useListPrograms();

  const [step, setStep] = useState<Step>("program");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [applicationId, setApplicationId] = useState<number | null>(null);
  const [olevelFile, setOlevelFile] = useState<File | null>(null);
  const [alevelFile, setAlevelFile] = useState<File | null>(null);
  const [uploadingCerts, setUploadingCerts] = useState(false);
  const olevelInputRef = useRef<HTMLInputElement>(null);
  const alevelInputRef = useRef<HTMLInputElement>(null);

  const programs = (programsData as any)?.programs ?? [];

  const { register, control, handleSubmit, watch, setValue, getValues, formState: { errors } } = useForm<ApplyForm>({
    resolver: zodResolver(applySchema),
    defaultValues: {
      examLevel: "o_level",
      nationality: "Ugandan",
      oLevelYear: new Date().getFullYear() - 2,
      oLevelGrades: [{ subject: "", grade: "", points: 0 }],
      aLevelGrades: [{ subject: "", grade: "", points: 0, subjectType: "principal" }],
    },
  });

  const watchExamLevel = watch("examLevel");
  const watchProgramId = watch("programId");
  const selectedProgram = programs.find((p: any) => p.id === Number(watchProgramId));
  const isDegreeProgram = selectedProgram?.level === "degree";

  // Field arrays
  const oLevelArray = useFieldArray({ control, name: "oLevelGrades" });
  const aLevelArray = useFieldArray({ control, name: "aLevelGrades" as any });

  const stepOrder: Step[] = isDegreeProgram
    ? ["program", "olevel", "alevel", "personal", "upload", "review"]
    : ["program", "olevel", "personal", "upload", "review"];

  const currentIdx = stepOrder.indexOf(step);
  const canGoNext = currentIdx < stepOrder.length - 1;
  const canGoBack = currentIdx > 0;

  const goNext = () => { if (canGoNext) setStep(stepOrder[currentIdx + 1]); };
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
              const found = OLEVEL_GRADES.find((g) => g.value === e.target.value);
              setValue(`oLevelGrades.${index}.grade`, e.target.value);
              setValue(`oLevelGrades.${index}.points`, found?.points ?? 0);
            }}
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm"
          >
            <option value="">Grade…</option>
            {OLEVEL_GRADES.map((gr) => <option key={gr.value} value={gr.value}>{gr.label}</option>)}
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

      const unebGrades: any = {
        olevel: data.oLevelGrades.map((g) => ({ ...g, year: data.oLevelYear, indexNumber: data.oLevelIndexNumber })),
      };
      if (isDegreeProgram && data.aLevelGrades?.length) {
        unebGrades.alevel = data.aLevelGrades.map((g) => ({ ...g, year: data.aLevelYear, indexNumber: data.aLevelIndexNumber }));
      }

      const payload = {
        programId: data.programId,
        examLevel: isDegreeProgram ? "a_level" : "o_level",
        examYear: isDegreeProgram ? data.aLevelYear : data.oLevelYear,
        indexNumber: isDegreeProgram ? (data.aLevelIndexNumber || data.oLevelIndexNumber) : data.oLevelIndexNumber,
        unebGrades,
        personalStatement: data.personalStatement,
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

    const upload = async (file: File, type: "olevel" | "alevel") => {
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
      if (alevelFile) await upload(alevelFile, "alevel");
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
                <p className="text-muted-foreground text-sm mb-6">Select the degree or diploma you are applying for.</p>

                {programsLoading ? (
                  <p className="text-muted-foreground">Loading programs…</p>
                ) : (
                  <div className="space-y-4">
                    {["degree", "diploma"].map((lvl) => (
                      <div key={lvl}>
                        <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                          {lvl === "degree" ? "Undergraduate Degrees" : "Diploma Programs"}
                        </h3>
                        <div className="grid gap-3">
                          {programs.filter((p: any) => p.level === lvl).map((p: any) => (
                            <label
                              key={p.id}
                              className={`flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all
                                ${Number(watchProgramId) === p.id ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"}`}
                            >
                              <input type="radio" value={p.id} {...register("programId")} className="mt-1 accent-primary" />
                              <div className="flex-1 min-w-0">
                                <p className="font-semibold text-sm">{p.name}</p>
                                <p className="text-xs text-muted-foreground">{p.faculty} · {p.duration}</p>
                                <p className="text-xs text-muted-foreground mt-1">{p.entryRequirements}</p>
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {errors.programId && <p className="text-xs text-destructive mt-2">{errors.programId.message}</p>}

                <div className="mt-6 flex justify-end">
                  <Button type="button" onClick={goNext} disabled={!watchProgramId} className="gap-2">
                    Next: O-Level Results <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            )}

            {/* ── STEP: O-Level Results ───────────────────────────────────── */}
            {step === "olevel" && (
              <Card className="p-8">
                <h2 className="text-xl font-bold mb-1">Uganda Certificate of Education (UCE)</h2>
                <p className="text-muted-foreground text-sm mb-6">Enter your O-Level results as they appear on your UNEB certificate. Include at least 5 subjects.</p>

                <div className="grid md:grid-cols-2 gap-5 mb-6">
                  <div className="space-y-2">
                    <Label>Examination Year</Label>
                    <Input type="number" {...register("oLevelYear")} min={1990} max={new Date().getFullYear()} />
                    {errors.oLevelYear && <p className="text-xs text-destructive">{errors.oLevelYear.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>UNEB Index Number</Label>
                    <Input placeholder="e.g. U0001/001" {...register("oLevelIndexNumber")} />
                    {errors.oLevelIndexNumber && <p className="text-xs text-destructive">{errors.oLevelIndexNumber.message}</p>}
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
                  <span><strong>UCE Grading:</strong> D1 (1pt) is the highest. D1–D6 are passes. D7–D9 are weak passes. F is a fail.</span>
                </div>
                {errors.oLevelGrades && <p className="text-xs text-destructive mt-2">{errors.oLevelGrades.message as string}</p>}

                <div className="mt-6 flex justify-end">
                  <Button type="button" onClick={goNext} className="gap-2">
                    Next {isDegreeProgram ? ": A-Level Results" : ": Personal Info"} <ArrowRight className="w-4 h-4" />
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
                    <Label>Examination Year</Label>
                    <Input type="number" {...register("aLevelYear")} min={1990} max={new Date().getFullYear()} />
                  </div>
                  <div className="space-y-2">
                    <Label>UNEB Index Number</Label>
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
                    <Label>Date of Birth</Label>
                    <Input type="date" {...register("dateOfBirth")} max={new Date().toISOString().split("T")[0]} />
                    {errors.dateOfBirth && <p className="text-xs text-destructive">{errors.dateOfBirth.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>Gender</Label>
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
                    <Input {...register("nationality")} defaultValue="Ugandan" />
                  </div>
                </div>

                <div className="space-y-2 mb-5">
                  <Label>District of Origin</Label>
                  <Input {...register("district")} placeholder="e.g. Kampala" />
                  {errors.district && <p className="text-xs text-destructive">{errors.district.message}</p>}
                </div>

                <div className="border-t border-border pt-6 mb-5">
                  <h3 className="font-bold mb-4">Next of Kin</h3>
                  <div className="grid md:grid-cols-3 gap-5">
                    <div className="space-y-2">
                      <Label>Full Name</Label>
                      <Input {...register("nextOfKinName")} />
                      {errors.nextOfKinName && <p className="text-xs text-destructive">{errors.nextOfKinName.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label>Phone</Label>
                      <Input {...register("nextOfKinPhone")} />
                      {errors.nextOfKinPhone && <p className="text-xs text-destructive">{errors.nextOfKinPhone.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label>Relationship</Label>
                      <Input {...register("nextOfKinRelationship")} placeholder="e.g. Father, Mother" />
                      {errors.nextOfKinRelationship && <p className="text-xs text-destructive">{errors.nextOfKinRelationship.message}</p>}
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Personal Statement</Label>
                  <Textarea {...register("personalStatement")} rows={6} placeholder="Tell us about yourself, your motivation for applying to this program, and your future goals…" className={errors.personalStatement ? "border-destructive" : ""} />
                  {errors.personalStatement && <p className="text-xs text-destructive">{errors.personalStatement.message}</p>}
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
                  {/* O-Level Certificate */}
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

                  {/* A-Level Certificate */}
                  {isDegreeProgram && (
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
