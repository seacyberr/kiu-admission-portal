import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, ArrowRight, GraduationCap, BookOpen, Upload, Plus, Trash2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

// UNEB UACE Subjects
const UACE_SUBJECTS = [
  // Sciences
  "Biology", "Chemistry", "Physics", "Mathematics", "Agriculture", "Technical Drawing",
  // Arts
  "History", "Geography", "Economics", "Entrepreneurship", "Art", "Music",
  // Languages
  "English Language", "Literature in English", "French", "German", "Arabic", "Latin",
  // Humanities
  "Christian Religious Education", "Islamic Religious Education", "Divinity",
  // Technical
  "Food and Nutrition", "Home Management", "Woodwork", "Metalwork", "Building Construction",
  // ICT
  "Computer Studies", "Information Technology"
];

// UNEB UCE Subjects
const UCE_SUBJECTS = [
  "English Language", "Mathematics", "Biology", "Chemistry", "Physics",
  "History", "Geography", "Christian Religious Education", "Islamic Religious Education",
  "Commerce", "Accounting", "Economics", "Agriculture", "Computer Studies",
  "Technical Drawing", "Food and Nutrition", "Home Management", "Woodwork",
  "Metalwork", "Building Construction", "Art", "Music", "French", "German",
  "Arabic", "Latin", "Literature in English", "Entrepreneurship"
];

// UACE Grades
const UACE_GRADES = ["A", "B", "C", "D", "E", "O", "F"];

// UCE Grades
const UCE_GRADES = ["D1", "D2", "C3", "C4", "C5", "C6", "P7", "P8", "F9"];

// Compulsory UCE subjects
const COMPULSORY_UCE = [
  "English Language",
  "Mathematics", 
  "Biology",
  "Chemistry",
  "Physics",
  "History",
  "Geography",
  "Christian Religious Education"
];

// Validation schema
const step3Schema = z.object({
  qualificationType: z.enum(["uace", "uce", "hec", "diploma", "national_certificate", "bachelors", "masters"]).default("uace"),
  // O-Level (UCE) - REQUIRED
  uceSchoolName: z.string().min(3, "School name is required"),
  uceIndexNumber: z.string().regex(/^U\d{4}\/\d{3}$/, "Invalid format. Use: UXXXX/XXX (e.g., U2023/001)"),
  uceYear: z.string().regex(/^20\d{2}$/, "Invalid year. Use format: 20XX"),
  uceSubjects: z.array(z.object({
    subject: z.string().min(1, "Subject is required"),
    grade: z.string().min(1, "Grade is required"),
  })).min(8, "Minimum 8 subjects required"),
  
  // A-Level (UACE) - Optional
  hasUACE: z.boolean().default(false),
  uaceSchoolName: z.string().optional(),
  uaceIndexNumber: z.string().regex(/^A\d{4}\/\d{3}$/, "Invalid format. Use: AXXXX/XXX (e.g., A2023/001)").optional(),
  uaceYear: z.string().regex(/^20\d{2}$/, "Invalid year").optional(),
  uaceCurriculum: z.enum(["Old", "New"]).optional(),
  uacePrincipalSubjects: z.array(z.object({
    subject: z.string(),
    grade: z.string(),
  })).max(3).optional(),
  uaceSubsidiarySubjects: z.array(z.object({
    subject: z.string(),
    grade: z.string(),
  })).max(2).optional(),
  
  // Other Qualifications - Optional
  hasOtherQualifications: z.boolean().default(false),
  otherQualifications: z.array(z.object({
    institution: z.string().min(2, "Institution name is required"),
    certificateName: z.string().min(2, "Certificate name is required"),
    year: z.string().regex(/^20\d{2}$/, "Invalid year"),
    division: z.enum(["Distinction", "Credit", "Pass", "Fail"]),
  })).optional(),
});

type Step3Data = z.infer<typeof step3Schema>;

interface EducationBackgroundProps {
  onNext: (data: Step3Data) => void;
  onBack: () => void;
  defaultValues?: Partial<Step3Data>;
}

export default function EducationBackground({ onNext, onBack, defaultValues }: EducationBackgroundProps) {
  const [uceFile, setUceFile] = useState<File | null>(null);
  const [uaceFile, setUaceFile] = useState<File | null>(null);
  
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<Step3Data>({
    resolver: zodResolver(step3Schema),
    defaultValues: {
      qualificationType: defaultValues?.qualificationType || "uace",
      uceSchoolName: defaultValues?.uceSchoolName || "",
      uceIndexNumber: defaultValues?.uceIndexNumber || "",
      uceYear: defaultValues?.uceYear || "",
      uceSubjects: defaultValues?.uceSubjects || [],
      hasUACE: defaultValues?.hasUACE || false,
      uaceSchoolName: defaultValues?.uaceSchoolName || "",
      uaceIndexNumber: defaultValues?.uaceIndexNumber || "",
      uaceYear: defaultValues?.uaceYear || "",
      uaceCurriculum: defaultValues?.uaceCurriculum || undefined,
      uacePrincipalSubjects: defaultValues?.uacePrincipalSubjects || [],
      uaceSubsidiarySubjects: defaultValues?.uaceSubsidiarySubjects || [],
      hasOtherQualifications: defaultValues?.hasOtherQualifications || false,
      otherQualifications: defaultValues?.otherQualifications || [],
    },
  });

  const qualificationType = watch("qualificationType");
  const hasUACE = watch("hasUACE");
  const hasOtherQualifications = watch("hasOtherQualifications");
  const uceSubjects = watch("uceSubjects") || [];
  const uacePrincipalSubjects = watch("uacePrincipalSubjects") || [];
  const uaceSubsidiarySubjects = watch("uaceSubsidiarySubjects") || [];
  const otherQualifications = watch("otherQualifications") || [];

  // UCE subjects field array
  const {
    fields: uceFields,
    append: appendUce,
    remove: removeUce,
  } = useFieldArray({
    control,
    name: "uceSubjects",
  });

  // UACE Principal subjects field array
  const {
    fields: uacePrincipalFields,
    append: appendUacePrincipal,
    remove: removeUacePrincipal,
  } = useFieldArray({
    control,
    name: "uacePrincipalSubjects",
  });

  // UACE Subsidiary subjects field array
  const {
    fields: uaceSubsidiaryFields,
    append: appendUaceSubsidiary,
    remove: removeUaceSubsidiary,
  } = useFieldArray({
    control,
    name: "uaceSubsidiarySubjects",
  });

  // Other qualifications field array
  const {
    fields: otherQualFields,
    append: appendOtherQual,
    remove: removeOtherQual,
  } = useFieldArray({
    control,
    name: "otherQualifications",
  });

  // Add compulsory UCE subjects if empty
  const addCompulsoryUCE = () => {
    if (uceFields.length === 0) {
      COMPULSORY_UCE.forEach((subject) => {
        appendUce({ subject, grade: "" });
      });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto"
    >
      <Card className="p-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-primary/10">
            <GraduationCap className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold">Step 3: Education Background</h1>
          <p className="mt-2 text-muted-foreground">
            Please provide your academic qualifications. O-Level (UCE) is required.
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-primary">Step 3 of 6</span>
            <span className="text-muted-foreground">Education Background</span>
          </div>
          <div className="h-2 mt-2 rounded-full bg-muted">
            <div className="h-full w-3/6 rounded-full bg-primary" />
          </div>
        </div>

        <form onSubmit={handleSubmit(onNext)} className="space-y-8">
          {/* Qualification Type Selector */}
          <div className="p-6 border rounded-lg bg-muted/30">
            <div className="flex items-center gap-2 mb-4">
              <GraduationCap className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-semibold">Qualification Type</h2>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="qualificationType">Select Your Highest Education Level *</Label>
              <Select
                value={qualificationType}
                onValueChange={(value: string) => setValue("qualificationType", value as any)}
              >
                <SelectTrigger className={errors.qualificationType ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select your qualification type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="uace">UACE (A-Level)</SelectItem>
                  <SelectItem value="uce">UCE (O-Level only)</SelectItem>
                  <SelectItem value="hec">Higher Education Certificate (HEC)</SelectItem>
                  <SelectItem value="diploma">Diploma/Certificate</SelectItem>
                  <SelectItem value="national_certificate">National Certificate</SelectItem>
                  <SelectItem value="bachelors">Bachelor's Degree</SelectItem>
                  <SelectItem value="masters">Master's Degree</SelectItem>
                </SelectContent>
              </Select>
              {errors.qualificationType && (
                <p className="text-xs text-destructive">{errors.qualificationType.message}</p>
              )}
              <p className="text-xs text-muted-foreground">
                This determines which sections you'll need to complete below.
              </p>
            </div>
          </div>

          {/* O-Level (UCE) Section - REQUIRED */}
          <div className="p-6 border-2 rounded-lg border-primary/20 bg-primary/5">
            <div className="flex items-center gap-2 mb-4">
              <BookOpen className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-semibold">O-Level (UCE) - REQUIRED</h2>
            </div>

            <div className="space-y-4">
              {/* School Details */}
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="uceSchoolName">School Name *</Label>
                  <Input
                    id="uceSchoolName"
                    placeholder="e.g., St. Mary's Secondary School"
                    {...register("uceSchoolName")}
                    className={errors.uceSchoolName ? "border-destructive" : ""}
                  />
                  {errors.uceSchoolName && (
                    <p className="text-xs text-destructive">{errors.uceSchoolName.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="uceIndexNumber">Index Number *</Label>
                  <Input
                    id="uceIndexNumber"
                    placeholder="U2023/001"
                    {...register("uceIndexNumber")}
                    className={errors.uceIndexNumber ? "border-destructive" : ""}
                  />
                  {errors.uceIndexNumber && (
                    <p className="text-xs text-destructive">{errors.uceIndexNumber.message}</p>
                  )}
                  <p className="text-xs text-muted-foreground">Format: UXXXX/XXX</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="uceYear">Year of Completion *</Label>
                  <Input
                    id="uceYear"
                    placeholder="2023"
                    {...register("uceYear")}
                    className={errors.uceYear ? "border-destructive" : ""}
                  />
                  {errors.uceYear && (
                    <p className="text-xs text-destructive">{errors.uceYear.message}</p>
                  )}
                </div>
              </div>

              {/* Add Compulsory Subjects Button */}
              {uceFields.length === 0 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={addCompulsoryUCE}
                  className="w-full"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add 8 Compulsory Subjects
                </Button>
              )}

              {/* UCE Subjects */}
              <div className="space-y-3">
                <Label>UCE Subjects (8 Compulsory + Optional) *</Label>
                
                {uceFields.map((field, index) => (
                  <motion.div
                    key={field.id}
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="flex items-center gap-2 p-3 rounded-lg bg-background border"
                  >
                    <Select
                      value={field.subject}
                      onValueChange={(value: string) => {
                        const newSubjects = [...uceSubjects];
                        newSubjects[index] = { ...newSubjects[index], subject: value };
                        setValue("uceSubjects", newSubjects);
                      }}
                    >
                      <SelectTrigger className="flex-1">
                        <SelectValue placeholder="Select subject" />
                      </SelectTrigger>
                      <SelectContent>
                        {UCE_SUBJECTS.map((subject) => (
                          <SelectItem key={subject} value={subject}>
                            {subject}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Select
                      value={field.grade}
                      onValueChange={(value: string) => {
                        const newSubjects = [...uceSubjects];
                        newSubjects[index] = { ...newSubjects[index], grade: value };
                        setValue("uceSubjects", newSubjects);
                      }}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Grade" />
                      </SelectTrigger>
                      <SelectContent>
                        {UCE_GRADES.map((grade) => (
                          <SelectItem key={grade} value={grade}>
                            {grade}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeUce(index)}
                    >
                      <Trash2 className="w-4 h-4 text-destructive" />
                    </Button>
                  </motion.div>
                ))}

                {uceFields.length < 10 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => appendUce({ subject: "", grade: "" })}
                    className="w-full"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Optional Subject ({10 - uceFields.length} remaining)
                  </Button>
                )}

                {errors.uceSubjects && (
                  <p className="text-xs text-destructive">{errors.uceSubjects.message}</p>
                )}
              </div>

              {/* Certificate Upload */}
              <div className="space-y-2">
                <Label>UCE Certificate/Result Slip *</Label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => setUceFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="uce-certificate"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => document.getElementById("uce-certificate")?.click()}
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    {uceFile ? "Change File" : "Upload Certificate"}
                  </Button>
                  {uceFile && (
                    <span className="text-sm text-muted-foreground">
                      {uceFile.name} ({(uceFile.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  Upload PDF or image (JPG/PNG), max 5MB
                </p>
              </div>
            </div>
          </div>

          {/* A-Level (UACE) Section - Optional */}
          <div className="p-6 border rounded-lg bg-muted/30">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-primary" />
                <h2 className="text-lg font-semibold">A-Level (UACE) - Optional</h2>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="hasUACE"
                  checked={hasUACE}
                  onCheckedChange={(checked) => setValue("hasUACE", checked as boolean)}
                />
                <Label htmlFor="hasUACE" className="cursor-pointer">
                  I have UACE results
                </Label>
              </div>
            </div>

            <AnimatePresence>
              {hasUACE && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4"
                >
                  {/* School Details */}
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="space-y-2">
                      <Label htmlFor="uaceSchoolName">School Name</Label>
                      <Input
                        id="uaceSchoolName"
                        placeholder="e.g., St. Mary's Secondary School"
                        {...register("uaceSchoolName")}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="uaceIndexNumber">Index Number</Label>
                      <Input
                        id="uaceIndexNumber"
                        placeholder="A2023/001"
                        {...register("uaceIndexNumber")}
                        className={errors.uaceIndexNumber ? "border-destructive" : ""}
                      />
                      <p className="text-xs text-muted-foreground">Format: AXXXX/XXX</p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="uaceYear">Year of Completion</Label>
                      <Input
                        id="uaceYear"
                        placeholder="2023"
                        {...register("uaceYear")}
                      />
                    </div>
                  </div>

                  {/* Curriculum */}
                  <div className="space-y-2">
                    <Label>Curriculum</Label>
                    <RadioGroup
                      value={watch("uaceCurriculum")}
                      onValueChange={(value: "Old" | "New") => setValue("uaceCurriculum", value)}
                      className="flex gap-4"
                    >
                      <div className="flex items-center gap-2">
                        <RadioGroupItem value="Old" id="old-curriculum" />
                        <Label htmlFor="old-curriculum" className="cursor-pointer">Old Curriculum</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <RadioGroupItem value="New" id="new-curriculum" />
                        <Label htmlFor="new-curriculum" className="cursor-pointer">New Curriculum</Label>
                      </div>
                    </RadioGroup>
                  </div>

                  {/* Principal Subjects */}
                  <div className="space-y-3">
                    <Label>Principal Subjects (Maximum 3)</Label>
                    {uacePrincipalFields.map((field, index) => (
                      <div key={field.id} className="flex items-center gap-2">
                        <Select
                          value={field.subject}
                          onValueChange={(value: string) => {
                            const newSubjects = [...uacePrincipalSubjects];
                            newSubjects[index] = { ...newSubjects[index], subject: value };
                            setValue("uacePrincipalSubjects", newSubjects);
                          }}
                        >
                          <SelectTrigger className="flex-1">
                            <SelectValue placeholder="Select subject" />
                          </SelectTrigger>
                          <SelectContent>
                            {UACE_SUBJECTS.map((subject) => (
                              <SelectItem key={subject} value={subject}>
                                {subject}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        <Select
                          value={field.grade}
                          onValueChange={(value: string) => {
                            const newSubjects = [...uacePrincipalSubjects];
                            newSubjects[index] = { ...newSubjects[index], grade: value };
                            setValue("uacePrincipalSubjects", newSubjects);
                          }}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue placeholder="Grade" />
                          </SelectTrigger>
                          <SelectContent>
                            {UACE_GRADES.map((grade) => (
                              <SelectItem key={grade} value={grade}>
                                {grade}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeUacePrincipal(index)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                    ))}

                    {uacePrincipalFields.length < 3 && (
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => appendUacePrincipal({ subject: "", grade: "" })}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add Principal Subject
                      </Button>
                    )}
                  </div>

                  {/* Subsidiary Subjects */}
                  <div className="space-y-3">
                    <Label>Subsidiary Subjects (Maximum 2)</Label>
                    {uaceSubsidiaryFields.map((field, index) => (
                      <div key={field.id} className="flex items-center gap-2">
                        <Select
                          value={field.subject}
                          onValueChange={(value: string) => {
                            const newSubjects = [...uaceSubsidiarySubjects];
                            newSubjects[index] = { ...newSubjects[index], subject: value };
                            setValue("uaceSubsidiarySubjects", newSubjects);
                          }}
                        >
                          <SelectTrigger className="flex-1">
                            <SelectValue placeholder="Select subject" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="General Paper">General Paper</SelectItem>
                            <SelectItem value="Subsidiary Mathematics">Subsidiary Mathematics</SelectItem>
                            <SelectItem value="Subsidiary ICT">Subsidiary ICT</SelectItem>
                          </SelectContent>
                        </Select>

                        <Select
                          value={field.grade}
                          onValueChange={(value: string) => {
                            const newSubjects = [...uaceSubsidiarySubjects];
                            newSubjects[index] = { ...newSubjects[index], grade: value };
                            setValue("uaceSubsidiarySubjects", newSubjects);
                          }}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue placeholder="Grade" />
                          </SelectTrigger>
                          <SelectContent>
                            {UACE_GRADES.map((grade) => (
                              <SelectItem key={grade} value={grade}>
                                {grade}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeUaceSubsidiary(index)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                    ))}

                    {uaceSubsidiaryFields.length < 2 && (
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => appendUaceSubsidiary({ subject: "", grade: "" })}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add Subsidiary Subject
                      </Button>
                    )}
                  </div>

                  {/* Certificate Upload */}
                  <div className="space-y-2">
                    <Label>UACE Certificate/Result Slip</Label>
                    <div className="flex items-center gap-4">
                      <input
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={(e) => setUaceFile(e.target.files?.[0] || null)}
                        className="hidden"
                        id="uace-certificate"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => document.getElementById("uace-certificate")?.click()}
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        {uaceFile ? "Change File" : "Upload Certificate"}
                      </Button>
                      {uaceFile && (
                        <span className="text-sm text-muted-foreground">
                          {uaceFile.name}
                        </span>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Other Qualifications - Optional */}
          <div className="p-6 border rounded-lg bg-muted/30">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-primary" />
                <h2 className="text-lg font-semibold">Other Qualifications - Optional</h2>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="hasOtherQualifications"
                  checked={hasOtherQualifications}
                  onCheckedChange={(checked) => setValue("hasOtherQualifications", checked as boolean)}
                />
                <Label htmlFor="hasOtherQualifications" className="cursor-pointer">
                  I have Diploma/Certificate (for Direct Entry)
                </Label>
              </div>
            </div>

            <AnimatePresence>
              {hasOtherQualifications && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4"
                >
                  {otherQualFields.map((field, index) => (
                    <div key={field.id} className="p-4 space-y-4 rounded-lg bg-background border">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">Qualification #{index + 1}</h4>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeOtherQual(index)}
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Remove
                        </Button>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                          <Label>Institution Name</Label>
                          <Input
                            placeholder="e.g., Kampala Nursing School"
                            {...register(`otherQualifications.${index}.institution`)}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label>Certificate/Diploma Name</Label>
                          <Input
                            placeholder="e.g., Diploma in Nursing"
                            {...register(`otherQualifications.${index}.certificateName`)}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label>Year of Completion</Label>
                          <Input
                            placeholder="2023"
                            {...register(`otherQualifications.${index}.year`)}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label>Class/Division Obtained</Label>
                          <Select
                            value={field.division}
                            onValueChange={(value: "Distinction" | "Credit" | "Pass" | "Fail") => {
                              const newQuals = [...otherQualifications];
                              newQuals[index] = { ...newQuals[index], division: value };
                              setValue("otherQualifications", newQuals);
                            }}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select division" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="Distinction">Distinction</SelectItem>
                              <SelectItem value="Credit">Credit</SelectItem>
                              <SelectItem value="Pass">Pass</SelectItem>
                              <SelectItem value="Fail">Fail</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  ))}

                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => appendOtherQual({
                      institution: "",
                      certificateName: "",
                      year: "",
                      division: "Pass",
                    })}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Qualification
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Navigation */}
          <div className="flex justify-between pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={onBack}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <Button
              type="submit"
              className="flex items-center gap-2 px-8"
              isLoading={isSubmitting}
            >
              Next Step
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </form>
      </Card>
    </motion.div>
  );
}
