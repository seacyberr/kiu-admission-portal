import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Save, AlertCircle } from "lucide-react";

// Import all step components
import PersonalInformation from "./personal-information";
import ContactLocation from "./contact-location";
import EducationBackground from "./education-background";
import ProgramSelection from "./program-selection";
import DocumentUpload from "./document-upload";
import ReviewSubmit from "./review-submit";

// Application data type
export interface ApplicationData {
  personal?: {
    surname: string;
    firstName: string;
    otherNames?: string;
    dateOfBirth: Date;
    gender: "Male" | "Female";
    nationality: string;
    nationalId: string;
    maritalStatus: "Single" | "Married" | "Divorced" | "Widowed";
    religion: "Christianity" | "Islam" | "Other";
    photoUrl: string | null;
  };
  contact?: {
    residentialAddress: string;
    district: string;
    postalAddress?: string;
    emergencyContactName: string;
    emergencyRelationship: string;
    countryCode?: string;
    emergencyPhone: string;
    emergencyAddress: string;
    sponsorshipType?: "bursary" | "private";
    sponsorshipSource?: string;
  };
  education?: {
    qualificationType: "uace" | "uce" | "hec" | "diploma" | "national_certificate" | "bachelors" | "masters";
    uceSchoolName: string;
    uceIndexNumber: string;
    uceYear: string;
    uceSubjects: Array<{ subject: string; grade: string }>;
    hasUACE: boolean;
    uaceSchoolName?: string;
    uaceIndexNumber?: string;
    uaceYear?: string;
    uaceCurriculum?: "Old" | "New";
    uacePrincipalSubjects: Array<{ subject: string; grade: string }>;
    uaceSubsidiarySubjects: Array<{ subject: string; grade: string }>;
    hasOtherQualifications: boolean;
    otherQualifications: Array<{
      institution: string;
      certificateName: string;
      year: string;
      division: "Distinction" | "Credit" | "Pass" | "Fail";
    }>;
    // HEC data
    hecTrack?: "arts" | "physical" | "biological";
    hecInstitution?: string;
    hecCompletionYear?: number;
    hecGpa?: number;
    // National Certificate data (2-year vocational qualification)
    nationalCertificateInstitution?: string;
    nationalCertificateField?: string;
    nationalCertificateCompletionYear?: number;
    // Diploma data (university qualification)
    diplomaInstitution?: string;
    diplomaProgram?: string;
    diplomaClass?: "Distinction" | "Credit" | "Pass";
    // Previous degree (for postgraduate)
    previousDegreeInstitution?: string;
    previousDegreeProgram?: string;
    previousDegreeGpa?: number;
  };
  program?: {
    applicationType: "first_year" | "diploma_entry" | "direct_entry" | "transfer" | "postgraduate";
    firstChoice: string;
    secondChoice?: string;
    thirdChoice?: string;
    entryLevel: "year_1" | "year_2" | "year_3";
  };
  documents?: {
    files: Record<string, File>;
    declaration: boolean;
  };
}

// Wizard steps configuration
const WIZARD_STEPS = [
  { id: 1, name: "Personal", component: PersonalInformation, icon: "👤" },
  { id: 2, name: "Contact", component: ContactLocation, icon: "📍" },
  { id: 3, name: "Education", component: EducationBackground, icon: "📚" },
  { id: 4, name: "Program", component: ProgramSelection, icon: "🎓" },
  { id: 5, name: "Documents", component: DocumentUpload, icon: "📄" },
  { id: 6, name: "Review", component: ReviewSubmit, icon: "✓" },
];

// Storage key for auto-save
const STORAGE_KEY = "kiu_application_draft";

export default function ApplicationWizard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [applicationData, setApplicationData] = useState<ApplicationData>({
    personal: undefined,
    contact: undefined,
    education: undefined,
    program: undefined,
    documents: undefined,
  });

  // Load saved data on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Restore dates from strings
        if (parsed.personal?.dateOfBirth) {
          parsed.personal.dateOfBirth = new Date(parsed.personal.dateOfBirth);
        }
        setApplicationData(parsed);
        setLastSaved(new Date());
        toast.info("Previous application draft loaded", {
          description: "You can continue where you left off.",
        });
      } catch {
        // Invalid saved data, ignore
      }
    }
  }, []);

  // Navigation handlers
  const goToNext = useCallback(() => {
    if (currentStep < 6) {
      setCurrentStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [currentStep]);

  const goToBack = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [currentStep]);

  const goToStep = useCallback((step: number) => {
    // Only allow going to completed steps or current step
    setCurrentStep(step);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  // Step completion handlers
  const handlePersonalComplete = (data: ApplicationData["personal"]) => {
    updateDataAndSave("personal", data);
    goToNext();
  };

  const handleContactComplete = (data: ApplicationData["contact"]) => {
    updateDataAndSave("contact", data);
    goToNext();
  };

  const handleEducationComplete = (data: any) => {
    updateDataAndSave("education", data);
    goToNext();
  };

  const handleProgramComplete = (data: ApplicationData["program"]) => {
    updateDataAndSave("program", data);
    goToNext();
  };

  const handleDocumentsComplete = (data: ApplicationData["documents"]) => {
    updateDataAndSave("documents", data);
    goToNext();
  };

  // Auto-save draft to backend
  const saveDraftToBackend = useCallback(async (data: ApplicationData) => {
    try {
      const response = await fetch("/api/admission/applications/wizard/save-draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(data),
      });
      
      if (response.ok) {
        setLastSaved(new Date());
      }
    } catch (error) {
      // Silent fail - localStorage is primary backup
    }
  }, []);

  // Enhanced updateData that also saves to backend
  const updateDataAndSave = useCallback((step: keyof ApplicationData, data: any) => {
    const updatedData = { ...applicationData, [step]: data };
    setApplicationData(updatedData);
    // Save to localStorage for backup
    localStorage.setItem('kiu_application_draft', JSON.stringify(updatedData));
    // Also save to backend
    saveDraftToBackend(updatedData);
  }, [applicationData, saveDraftToBackend]);

  // Final submission
  const handleFinalSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      const programChoices = [
        Number(applicationData.program?.firstChoice || 0),
        Number(applicationData.program?.secondChoice || 0),
        Number(applicationData.program?.thirdChoice || 0),
      ].filter((id) => id > 0);

      const education = applicationData.education;
      const wizardPayload = {
        personalInfo: {
          firstName: applicationData.personal?.firstName || "",
          surname: applicationData.personal?.surname || "",
          dateOfBirth: applicationData.personal?.dateOfBirth
            ? new Date(applicationData.personal.dateOfBirth).toISOString().split("T")[0]
            : undefined,
          gender: applicationData.personal?.gender || "",
          nationality: applicationData.personal?.nationality || "Ugandan",
          personalStatement: "",
        },
        contactInfo: {
          district: applicationData.contact?.district || "",
          nextOfKinName: applicationData.contact?.emergencyContactName || "",
          nextOfKinPhone: applicationData.contact?.emergencyPhone || "",
          nextOfKinRelationship: applicationData.contact?.emergencyRelationship || "",
          sessionOfStudy: "day",
        },
        educationInfo: {
          qualificationType: education?.qualificationType || "uace",
          examYear: Number(education?.uaceYear || education?.uceYear || new Date().getFullYear()),
          indexNumber: education?.uaceIndexNumber || education?.uceIndexNumber || "",
          uce: {
            subjects: (education?.uceSubjects || []).map((s) => ({
              subject: s.subject,
              grade: s.grade,
            })),
          },
          uace: {
            subjects: [
              ...(education?.uacePrincipalSubjects || []).map((s) => ({
                subject: s.subject,
                grade: s.grade,
                subjectType: "principal",
              })),
              ...(education?.uaceSubsidiarySubjects || []).map((s) => ({
                subject: s.subject,
                grade: s.grade,
                subjectType: "subsidiary",
              })),
            ],
          },
          hecTrack: education?.hecTrack,
          hecInstitution: education?.hecInstitution,
          hecCompletionYear: education?.hecCompletionYear,
          hecGpa: education?.hecGpa,
          nationalCertificate: {
            institution: education?.nationalCertificateInstitution,
            field: education?.nationalCertificateField,
            completionYear: education?.nationalCertificateCompletionYear,
          },
          diploma: {
            institution: education?.diplomaInstitution,
            program: education?.diplomaProgram,
            completionYear: undefined,
            class: education?.diplomaClass,
          },
          previousDegree: {
            institution: education?.previousDegreeInstitution,
            program: education?.previousDegreeProgram,
            gpa: education?.previousDegreeGpa,
          },
        },
        programChoices,
        documents: {},
      };

      const response = await fetch("/api/admission/applications/wizard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(wizardPayload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Submission failed" }));
        throw new Error(errorData.message || "Failed to submit application");
      }

      // Clear saved drafts on successful submission
      localStorage.removeItem(STORAGE_KEY);
      
      toast.success("Application submitted successfully!");
      
      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "/applicant/dashboard";
      }, 2000);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to submit application. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Load saved draft from backend on mount
  useEffect(() => {
    const loadBackendDraft = async () => {
      try {
        const response = await fetch("/api/v1/applications/wizard/draft", {
          credentials: "include",
        });
        
        if (response.ok) {
        const json = await response.json();
        const draft = json?.data?.draft || json?.draft;
          if (draft && !localStorage.getItem(STORAGE_KEY)) {
            // Only use backend draft if no localStorage data
            // Merge carefully to avoid overwriting local changes
          }
        }
      } catch (error) {
        // Silent fail - localStorage is primary
      }
    };
    
    loadBackendDraft();
  }, []);

  // Render current step component
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <PersonalInformation
            onNext={handlePersonalComplete}
            defaultValues={applicationData.personal}
          />
        );
      case 2:
        return (
          <ContactLocation
            onNext={handleContactComplete}
            onBack={goToBack}
            defaultValues={applicationData.contact}
          />
        );
      case 3:
        return (
          <EducationBackground
            onNext={handleEducationComplete}
            onBack={goToBack}
            defaultValues={applicationData.education}
          />
        );
      case 4:
        return (
          <ProgramSelection
            onNext={handleProgramComplete}
            onBack={goToBack}
            defaultValues={applicationData.program}
          />
        );
      case 5:
        return (
          <DocumentUpload
            onNext={handleDocumentsComplete}
            onBack={goToBack}
            defaultValues={applicationData.documents}
          />
        );
      case 6:
        return (
          <ReviewSubmit
            data={applicationData}
            onBack={goToBack}
            onSubmit={handleFinalSubmit}
            onEdit={goToStep}
            isSubmitting={isSubmitting}
          />
        );
      default:
        return <div>Invalid step</div>;
    }
  };

  return (
    <div className="min-h-screen bg-muted/30 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold">KIU Online Admission Application</h1>
          <p className="mt-2 text-muted-foreground">
            Complete all 6 steps to submit your application
          </p>
          {lastSaved && (
            <p className="mt-2 text-sm text-muted-foreground flex items-center justify-center gap-2">
              <Save className="w-4 h-4" />
              Last auto-saved: {lastSaved.toLocaleTimeString()}
            </p>
          )}
        </div>

        {/* Progress Stepper */}
        <Card className="p-6 mb-8">
          <div className="flex items-center justify-between">
            {WIZARD_STEPS.map((step, index) => {
              const isCompleted = currentStep > step.id;
              const isCurrent = currentStep === step.id;
              const isPending = currentStep < step.id;

              return (
                <div key={step.id} className="flex items-center">
                  {/* Step Circle */}
                  <div
                    className={`flex items-center justify-center w-12 h-12 rounded-full text-lg font-semibold transition-all ${
                      isCompleted
                        ? "bg-green-500 text-white cursor-pointer"
                        : isCurrent
                        ? "bg-primary text-primary-foreground ring-4 ring-primary/20 cursor-pointer"
                        : isPending
                        ? "bg-muted text-muted-foreground opacity-50"
                        : "bg-muted text-muted-foreground cursor-pointer"
                    }`}
                    onClick={() => {
                      if (isCompleted || isCurrent) {
                        goToStep(step.id);
                      }
                    }}
                  >
                    {isCompleted ? "✓" : step.icon}
                  </div>

                  {/* Step Name */}
                  <div
                    className={`hidden lg:block ml-3 text-sm font-medium ${
                      isCurrent ? "text-primary" : isCompleted ? "text-green-600" : "text-muted-foreground"
                    }`}
                  >
                    {step.name}
                  </div>

                  {/* Connector Line */}
                  {index < WIZARD_STEPS.length - 1 && (
                    <div
                      className={`hidden sm:block w-12 h-1 mx-4 rounded transition-all ${
                        isCompleted ? "bg-green-500" : "bg-muted"
                      }`}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </Card>

        {/* Alert for incomplete steps */}
        {currentStep < 6 && (
          <div className="mb-6 p-4 rounded-lg bg-blue-50 text-blue-800 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Your progress is automatically saved</p>
              <p className="text-sm">
                You can leave and return anytime. Your data is stored locally on this device.
              </p>
            </div>
          </div>
        )}

        {/* Step Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderStep()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
