import { useState } from 'react';
import { useLocation } from 'wouter';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCreateAdmissionApplication, useListPrograms } from '@workspace/api-client-react';
import { Button, Input, Label, Card, Textarea, Badge } from '@/components/ui/shared';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, Trash2, Plus, Info } from 'lucide-react';

const gradeSchema = z.object({
  subject: z.string().min(2, "Subject required"),
  grade: z.string().min(1, "Grade required"),
  points: z.coerce.number().min(0)
});

const applySchema = z.object({
  programId: z.coerce.number().min(1, "Please select a program"),
  examLevel: z.enum(["o_level", "a_level"]),
  examYear: z.coerce.number().min(1990).max(new Date().getFullYear()),
  indexNumber: z.string().min(5, "Index number is required"),
  unebGrades: z.array(gradeSchema).min(1, "At least one grade required"),
  personalStatement: z.string().min(50, "Statement must be at least 50 characters"),
  dateOfBirth: z.string().min(8, "Date of birth required"),
  gender: z.enum(["male", "female", "other"]),
  nationality: z.string().default("Ugandan"),
  district: z.string().min(2, "District is required"),
  nextOfKinName: z.string().min(2, "NOK Name required"),
  nextOfKinPhone: z.string().min(9, "NOK Phone required"),
  nextOfKinRelationship: z.string().min(2, "Relationship required"),
});

type ApplyForm = z.infer<typeof applySchema>;

export default function Apply() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const createMutation = useCreateAdmissionApplication();
  const { data: programsData, isLoading: programsLoading } = useListPrograms();

  const { register, control, handleSubmit, watch, formState: { errors } } = useForm<ApplyForm>({
    resolver: zodResolver(applySchema),
    defaultValues: {
      examLevel: 'o_level',
      nationality: 'Ugandan',
      unebGrades: [{ subject: '', grade: '', points: 0 }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "unebGrades"
  });

  const watchExamLevel = watch("examLevel");

  const onSubmit = (data: ApplyForm) => {
    // Basic validation based on exam level
    if (data.examLevel === 'o_level' && data.unebGrades.length < 8) {
      toast({ title: "Validation Error", description: "O-Level requires at least 8 subjects.", variant: "destructive" });
      return;
    }
    if (data.examLevel === 'a_level' && data.unebGrades.length < 3) {
      toast({ title: "Validation Error", description: "A-Level requires at least 3 principal subjects.", variant: "destructive" });
      return;
    }

    createMutation.mutate({ data }, {
      onSuccess: () => {
        toast({ title: "Application Submitted!", description: "You can track its progress in your dashboard." });
        setLocation('/dashboard');
      },
      onError: (err: any) => {
        toast({ title: "Submission Failed", description: err.message || "An error occurred", variant: "destructive" });
      }
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8 flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => window.history.back()}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-display font-bold text-primary">Admission Application</h1>
          <p className="text-muted-foreground">Complete the form below to apply to KIU</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        
        {/* Section 1: Personal Details */}
        <Card className="p-8">
          <h2 className="text-xl font-bold mb-6 border-b border-border pb-4">Personal Details</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label>Date of Birth</Label>
              <Input type="date" {...register("dateOfBirth")} className={errors.dateOfBirth ? "border-destructive" : ""} />
              {errors.dateOfBirth && <p className="text-xs text-destructive">{errors.dateOfBirth.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Gender</Label>
              <select {...register("gender")} className="flex h-12 w-full rounded-xl border-2 border-border/60 bg-background px-4 py-2 text-sm focus:border-primary focus:ring-4 focus:ring-primary/10">
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
              {errors.gender && <p className="text-xs text-destructive">{errors.gender.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Nationality</Label>
              <Input {...register("nationality")} />
            </div>
            <div className="space-y-2">
              <Label>District / Region</Label>
              <Input {...register("district")} />
              {errors.district && <p className="text-xs text-destructive">{errors.district.message}</p>}
            </div>
          </div>
        </Card>

        {/* Section 2: Next of Kin */}
        <Card className="p-8">
          <h2 className="text-xl font-bold mb-6 border-b border-border pb-4">Next of Kin</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <Label>Full Name</Label>
              <Input {...register("nextOfKinName")} />
              {errors.nextOfKinName && <p className="text-xs text-destructive">{errors.nextOfKinName.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Phone Number</Label>
              <Input {...register("nextOfKinPhone")} />
              {errors.nextOfKinPhone && <p className="text-xs text-destructive">{errors.nextOfKinPhone.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Relationship</Label>
              <Input placeholder="e.g. Father, Mother" {...register("nextOfKinRelationship")} />
              {errors.nextOfKinRelationship && <p className="text-xs text-destructive">{errors.nextOfKinRelationship.message}</p>}
            </div>
          </div>
        </Card>

        {/* Section 3: Academic Details */}
        <Card className="p-8 border-primary/20 shadow-lg shadow-primary/5">
          <h2 className="text-xl font-bold mb-6 border-b border-border pb-4">Academic Qualifications (UNEB)</h2>
          
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="space-y-2 col-span-2">
              <Label>Select Program to Apply For</Label>
              <select {...register("programId")} className="flex h-12 w-full rounded-xl border-2 border-border/60 bg-background px-4 py-2 text-sm focus:border-primary focus:ring-4 focus:ring-primary/10">
                <option value="">-- Select a Program --</option>
                {programsData?.programs?.map(p => (
                  <option key={p.id} value={p.id}>{p.name} ({p.level})</option>
                ))}
              </select>
              {errors.programId && <p className="text-xs text-destructive">{errors.programId.message}</p>}
            </div>

            <div className="space-y-2">
              <Label>Exam Level</Label>
              <select {...register("examLevel")} className="flex h-12 w-full rounded-xl border-2 border-border/60 bg-background px-4 py-2 text-sm focus:border-primary focus:ring-4 focus:ring-primary/10">
                <option value="o_level">O-Level (UCE)</option>
                <option value="a_level">A-Level (UACE)</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label>Exam Year</Label>
              <Input type="number" {...register("examYear")} />
              {errors.examYear && <p className="text-xs text-destructive">{errors.examYear.message}</p>}
            </div>
            <div className="space-y-2 col-span-2">
              <Label>Index Number</Label>
              <Input placeholder="e.g. U0001/001/2023" {...register("indexNumber")} />
              {errors.indexNumber && <p className="text-xs text-destructive">{errors.indexNumber.message}</p>}
            </div>
          </div>

          <div className="bg-secondary/30 p-6 rounded-xl border border-border">
            <div className="flex items-center justify-between mb-4">
              <Label className="text-lg">UNEB Grades</Label>
              <Badge variant="outline" className="bg-white">
                <Info className="w-3 h-3 mr-1" />
                {watchExamLevel === 'o_level' ? 'Min 8 Subjects (D1-D9)' : 'Min 3 Subjects (A-F)'}
              </Badge>
            </div>
            
            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="flex gap-3 items-start">
                  <div className="flex-1">
                    <Input placeholder="Subject Name" {...register(`unebGrades.${index}.subject`)} />
                    {errors.unebGrades?.[index]?.subject && <span className="text-[10px] text-destructive">{errors.unebGrades[index].subject?.message}</span>}
                  </div>
                  <div className="w-24">
                    <Input placeholder="Grade" {...register(`unebGrades.${index}.grade`)} />
                  </div>
                  <div className="w-24">
                    <Input type="number" placeholder="Pts" {...register(`unebGrades.${index}.points`)} />
                  </div>
                  <Button type="button" variant="ghost" size="icon" onClick={() => remove(index)} className="text-destructive hover:bg-destructive/10 shrink-0">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
            
            <Button type="button" variant="outline" size="sm" onClick={() => append({ subject: '', grade: '', points: 0 })} className="mt-4 border-dashed">
              <Plus className="w-4 h-4 mr-2" /> Add Subject
            </Button>
            {errors.unebGrades && <p className="text-xs text-destructive mt-2">{errors.unebGrades.root?.message || errors.unebGrades.message}</p>}
          </div>
        </Card>

        {/* Section 4: Personal Statement */}
        <Card className="p-8">
          <h2 className="text-xl font-bold mb-6 border-b border-border pb-4">Personal Statement</h2>
          <div className="space-y-2">
            <Label>Why do you want to join KIU? (Min 50 chars)</Label>
            <Textarea {...register("personalStatement")} className="h-40" placeholder="Tell us about your academic goals..." />
            {errors.personalStatement && <p className="text-xs text-destructive">{errors.personalStatement.message}</p>}
          </div>
        </Card>

        <div className="flex justify-end gap-4 pb-12">
          <Button type="button" variant="outline" onClick={() => setLocation('/dashboard')}>Cancel</Button>
          <Button type="submit" size="lg" isLoading={createMutation.isPending} className="px-12">Submit Application</Button>
        </div>
      </form>
    </div>
  );
}
