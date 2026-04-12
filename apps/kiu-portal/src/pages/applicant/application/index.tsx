import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
    emergencyPhone: string;
    emergencyAddress: string;
    sponsorshipType: "bursary" | "private";
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

  // Auto-save to localStorage
  const saveToStorage = useCallback((data: ApplicationData) => {
    // Files can't be serialized, so we exclude them from auto-save
    const serializable = {
      ...data,
      documents: data.documents
        ? { ...data.documents, files: {} }
        : undefined,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(serializable));
    setLastSaved(new Date());
  }, []);

  // Update data and auto-save
  const updateData = useCallback(
    (step: keyof ApplicationData, data: any) => {
      setApplicationData((prev) => {
        const updated = { ...prev, [step]: data };
        saveToStorage(updated);
        return updated;
      });
    },
    [saveToStorage]
  );

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
    updateData("personal", data);
    goToNext();
  };

  const handleContactComplete = (data: ApplicationData["contact"]) => {
    updateData("contact", data);
    goToNext();
  };

  const handleEducationComplete = (data: ApplicationData["education"]) => {
    updateData("education", data);
    goToNext();
  };

  const handleProgramComplete = (data: ApplicationData["program"]) => {
    updateData("program", data);
    goToNext();
  };

  const handleDocumentsComplete = (data: ApplicationData["documents"]) => {
    updateData("documents", data);
    goToNext();
  };

  // Auto-save draft to backend
  const saveDraftToBackend = useCallback(async (data: ApplicationData) => {
    try {
      const response = await fetch("/api/v1/applications/wizard/save-draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        console.warn("Failed to save draft to backend");
      }
    } catch (error) {
      // Silent fail - we still have localStorage backup
      console.warn("Draft save error:", error);
    }
  }, []);

  // Enhanced updateData that also saves to backend
  const updateDataAndSave = useCallback((step: keyof ApplicationData, data: any) => {
    updateData(step, data);
    // Also save draft to backend (debounced in production)
    const updatedData = { ...applicationData, [step]: data };
    saveDraftToBackend(updatedData);
  }, [applicationData, saveDraftToBackend]);

  // Final submission
  const handleFinalSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Prepare data for backend API
      const apiData = {
        personalInfo: {
          firstName: applicationData.personal?.firstName,
          lastName: applicationData.personal?.lastName,
          dateOfBirth: applicationData.personal?.dateOfBirth,
          gender: applicationData.personal?.gender,
          nationality: applicationData.personal?.nationality,
          nationalId: applicationData.personal?.nationalId,
          passportNumber: applicationData.personal?.passportNumber,
          personalStatement: applicationData.personal?.personalStatement,
        },
        contactInfo: {
          email: applicationData.contact?.email,
          phoneNumber: applicationData.contact?.phoneNumber,
          address: applicationData.contact?.address,
          district: applicationData.contact?.district,
          country: applicationData.contact?.country,
          sessionOfStudy: applicationData.contact?.sessionOfStudy,
          sponsorshipType: applicationData.contact?.sponsorshipType,
          nextOfKinName: applicationData.contact?.nextOfKin?.name,
          nextOfKinPhone: applicationData.contact?.nextOfKin?.phone,
          nextOfKinRelationship: applicationData.contact?.nextOfKin?.relationship,
        },
        educationInfo: {
          qualificationType: applicationData.education?.qualificationType || "uace",
          // UACE data
          uace: applicationData.education?.uace,
          uce: applicationData.education?.uce,
          examYear: applicationData.education?.uace?.year || applicationData.education?.uce?.year,
          indexNumber: applicationData.education?.uace?.indexNumber || applicationData.education?.uce?.indexNumber,
          // HEC data
          hecTrack: applicationData.education?.hecTrack,
          hecInstitution: applicationData.education?.hecInstitution,
          hecCompletionYear: applicationData.education?.hecCompletionYear,
          hecGpa: applicationData.education?.hecGpa,
          // National Certificate data (vocational qualification)
          nationalCertificate: {
            institution: applicationData.education?.nationalCertificateInstitution,
            field: applicationData.education?.nationalCertificateField,
            completionYear: applicationData.education?.nationalCertificateCompletionYear,
          },
          // Diploma data (university qualification)
          diploma: {
            institution: applicationData.education?.diplomaInstitution,
            program: applicationData.education?.diplomaProgram,
            class: applicationData.education?.diplomaClass,
          },
          // Previous degree (for postgraduate)
          previousDegree: {
            institution: applicationData.education?.previousDegreeInstitution,
            program: applicationData.education?.previousDegreeProgram,
            gpa: applicationData.education?.previousDegreeGpa,
          },
        },
        programChoices: applicationData.program?.choices?.map((p: any) => p.id) || [],
        documents: applicationData.documents,
      };

      // Submit application to backend
      const response = await fetch("/api/v1/applications/wizard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(apiData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Submission failed" }));
        throw new Error(errorData.message || "Failed to submit application");
      }

      const result = await response.json();
      
      // Clear saved drafts on successful submission
      localStorage.removeItem(STORAGE_KEY);
      
      toast.success("Application submitted successfully!");
      
      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "/applicant/dashboard";
      }, 2000);
    } catch (error) {
      console.error("Application submission error:", error);
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
          const { draft } = await response.json();
          if (draft && !localStorage.getItem(STORAGE_KEY)) {
            // Only use backend draft if no localStorage data
            // Merge carefully to avoid overwriting local changes
            console.log("Loaded draft from backend");
          }
        }
      } catch (error) {
        // Silent fail - localStorage is primary
        console.warn("Failed to load backend draft:", error);
      }
    };
    
    loadBackendDraft();
  }, []);

  // Render current step component
  const renderStep = () => {
    const stepConfig = WIZARD_STEPS[currentStep - 1];
    const Component = stepConfig.component;

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
          />
        );
      default:
        return null;
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
                    className={`flex items-center justify-center w-12 h-12 rounded-full text-lg font-semibold transition-all cursor-pointer ${
                      isCompleted
                        ? "bg-green-500 text-white"
                        : isCurrent
                        ? "bg-primary text-primary-foreground ring-4 ring-primary/20"
                        : "bg-muted text-muted-foreground"
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
