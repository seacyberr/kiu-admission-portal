import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CalendarIcon, Upload, User } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { useState, useRef } from "react";
import { motion } from "framer-motion";

// Validation schema for Step 1
const step1Schema = z.object({
  surname: z.string().min(2, "Surname must be at least 2 characters"),
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  otherNames: z.string().optional(),
  dateOfBirth: z.date({
    required_error: "Date of birth is required",
  }),
  gender: z.enum(["Male", "Female"], {
    required_error: "Gender is required",
  }),
  nationality: z.string().min(2, "Nationality is required"),
  nationalId: z.string().min(5, "National ID/Passport is required"),
  maritalStatus: z.enum(["Single", "Married", "Divorced", "Widowed"], {
    required_error: "Marital status is required",
  }),
  religion: z.enum(["Christianity", "Islam", "Other"], {
    required_error: "Religion is required",
  }),
});

export type Step1Data = z.infer<typeof step1Schema>;

// List of common nationalities (can be expanded)
const nationalities = [
  "Ugandan",
  "Kenyan",
  "Tanzanian",
  "Rwandan",
  "Burundian",
  "South Sudanese",
  "Congolese",
  "Nigerian",
  "Ghanaian",
  "Ethiopian",
  "Eritrean",
  "Somali",
  "Sudanese",
  "Other",
];

interface PersonalInformationProps {
  onNext: (data: Step1Data & { photoUrl: string | null }) => void;
  defaultValues?: Partial<Step1Data & { photoUrl: string | null }>;
}

export default function PersonalInformation({ onNext, defaultValues }: PersonalInformationProps) {
  const [photoUrl, setPhotoUrl] = useState<string | null>(defaultValues?.photoUrl || null);
  const [photoError, setPhotoError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
    defaultValues: {
      surname: defaultValues?.surname || "",
      firstName: defaultValues?.firstName || "",
      otherNames: defaultValues?.otherNames || "",
      gender: defaultValues?.gender || undefined,
      nationality: defaultValues?.nationality || "",
      nationalId: defaultValues?.nationalId || "",
      maritalStatus: defaultValues?.maritalStatus || undefined,
      religion: defaultValues?.religion || undefined,
    },
  });

  const dateOfBirth = watch("dateOfBirth");
  const gender = watch("gender");
  const maritalStatus = watch("maritalStatus");
  const religion = watch("religion");
  const nationality = watch("nationality");

  // Handle photo upload
  const handlePhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      setPhotoError("Please upload an image file (JPG or PNG)");
      return;
    }

    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      setPhotoError("Photo must be less than 2MB");
      return;
    }

    // Create preview URL
    const reader = new FileReader();
    reader.onloadend = () => {
      setPhotoUrl(reader.result as string);
      setPhotoError(null);
    };
    reader.readAsDataURL(file);
  };

  const onSubmit = (data: Step1Data) => {
    // Photo is optional - can be uploaded later
    onNext({ ...data, photoUrl });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto"
    >
      <Card className="p-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-primary/10">
            <User className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold">Step 1: Personal Information</h1>
          <p className="mt-2 text-muted-foreground">
            Please provide your bio data. All fields marked with * are required.
          </p>
        </div>

        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-primary">Step 1 of 6</span>
            <span className="text-muted-foreground">Personal Information</span>
          </div>
          <div className="h-2 mt-2 rounded-full bg-muted">
            <div className="h-full w-1/6 rounded-full bg-primary" />
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Photo Upload Section */}
          <div className="p-6 border-2 border-dashed rounded-lg border-muted-foreground/25">
            <Label className="text-base font-semibold">Passport Photo (Optional)</Label>
            <p className="mt-1 text-sm text-muted-foreground">
              Recent passport size photo with white background. Max 2MB (JPG/PNG). Can be uploaded later.
            </p>

            <div className="flex flex-col items-center gap-4 mt-4 sm:flex-row">
              {photoUrl ? (
                <div className="relative">
                  <img
                    src={photoUrl}
                    alt="Passport preview"
                    className="object-cover w-32 h-40 border-2 rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setPhotoUrl(null);
                      if (fileInputRef.current) fileInputRef.current.value = "";
                    }}
                    className="absolute top-0 right-0 p-1 text-white bg-red-500 rounded-full -mt-2 -mr-2 hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-center w-32 h-40 border-2 border-dashed rounded-lg bg-muted">
                  <Upload className="w-8 h-8 text-muted-foreground" />
                </div>
              )}

              <div className="flex-1">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png"
                  onChange={handlePhotoUpload}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full sm:w-auto"
                >
                  {photoUrl ? "Change Photo" : "Upload Photo"}
                </Button>
                {photoError && (
                  <p className="mt-2 text-sm text-destructive">{photoError}</p>
                )}
              </div>
            </div>
          </div>

          {/* Name Fields */}
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="surname">Surname *</Label>
              <Input
                id="surname"
                placeholder="e.g., Ochieng"
                {...register("surname")}
                className={errors.surname ? "border-destructive" : ""}
              />
              {errors.surname && (
                <p className="text-xs text-destructive">{errors.surname.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="firstName">First Name *</Label>
              <Input
                id="firstName"
                placeholder="e.g., John"
                {...register("firstName")}
                className={errors.firstName ? "border-destructive" : ""}
              />
              {errors.firstName && (
                <p className="text-xs text-destructive">{errors.firstName.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="otherNames">Other Names</Label>
              <Input
                id="otherNames"
                placeholder="e.g., Peter (optional)"
                {...register("otherNames")}
              />
            </div>
          </div>

          {/* Date of Birth & Gender */}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Date of Birth *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !dateOfBirth && "text-muted-foreground",
                      errors.dateOfBirth && "border-destructive"
                    )}
                  >
                    <CalendarIcon className="w-4 h-4 mr-2" />
                    {dateOfBirth ? format(dateOfBirth, "PPP") : "Select date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={dateOfBirth}
                    onSelect={(date) => date && setValue("dateOfBirth", date)}
                    disabled={(date) => {
                      const today = new Date();
                      const minAge = new Date(today.getFullYear() - 16, today.getMonth(), today.getDate());
                      return date > minAge;
                    }}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              {errors.dateOfBirth && (
                <p className="text-xs text-destructive">{errors.dateOfBirth.message}</p>
              )}
              <p className="text-xs text-muted-foreground">Must be at least 16 years old</p>
            </div>

            <div className="space-y-2">
              <Label>Gender *</Label>
              <Select
                value={gender}
                onValueChange={(value: "Male" | "Female") => setValue("gender", value)}
              >
                <SelectTrigger className={errors.gender ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Male">Male</SelectItem>
                  <SelectItem value="Female">Female</SelectItem>
                </SelectContent>
              </Select>
              {errors.gender && (
                <p className="text-xs text-destructive">{errors.gender.message}</p>
              )}
            </div>
          </div>

          {/* Nationality & National ID */}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Nationality *</Label>
              <Select
                value={nationality}
                onValueChange={(value) => setValue("nationality", value)}
              >
                <SelectTrigger className={errors.nationality ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select nationality" />
                </SelectTrigger>
                <SelectContent>
                  {nationalities.map((nation) => (
                    <SelectItem key={nation} value={nation}>
                      {nation}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.nationality && (
                <p className="text-xs text-destructive">{errors.nationality.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="nationalId">National ID / Passport Number *</Label>
              <Input
                id="nationalId"
                placeholder="e.g., CM123456789 or AB123456"
                {...register("nationalId")}
                className={errors.nationalId ? "border-destructive" : ""}
              />
              {errors.nationalId && (
                <p className="text-xs text-destructive">{errors.nationalId.message}</p>
              )}
            </div>
          </div>

          {/* Marital Status & Religion */}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Marital Status *</Label>
              <Select
                value={maritalStatus}
                onValueChange={(value) => setValue("maritalStatus", value as any)}
              >
                <SelectTrigger className={errors.maritalStatus ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Single">Single</SelectItem>
                  <SelectItem value="Married">Married</SelectItem>
                  <SelectItem value="Divorced">Divorced</SelectItem>
                  <SelectItem value="Widowed">Widowed</SelectItem>
                </SelectContent>
              </Select>
              {errors.maritalStatus && (
                <p className="text-xs text-destructive">{errors.maritalStatus.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Religion *</Label>
              <Select
                value={religion}
                onValueChange={(value) => setValue("religion", value as any)}
              >
                <SelectTrigger className={errors.religion ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select religion" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Christianity">Christianity</SelectItem>
                  <SelectItem value="Islam">Islam</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
              {errors.religion && (
                <p className="text-xs text-destructive">{errors.religion.message}</p>
              )}
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-end pt-6">
            <Button
              type="submit"
              className="px-8"
              isLoading={isSubmitting}
            >
              Next Step →
            </Button>
          </div>
        </form>
      </Card>
    </motion.div>
  );
}
