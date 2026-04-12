import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, ArrowRight, FileText, Upload, X, Check, AlertCircle, FileCheck } from "lucide-react";
import { motion } from "framer-motion";
import { useState, useCallback } from "react";

// Document types with requirements
const REQUIRED_DOCUMENTS = [
  {
    id: "national_id",
    name: "National ID / Passport",
    description: "National ID card (Ugandan students) or International Passport (bio-data page for international students)",
    required: true,
    acceptedTypes: [".pdf", ".jpg", ".jpeg", ".png"],
    maxSize: 5,
  },
  {
    id: "uce_certificate",
    name: "UCE Certificate / Result Slip",
    description: "UNEB UCE certificate or provisional result slip (required for First Year/HEC applicants)",
    required: false,
    acceptedTypes: [".pdf", ".jpg", ".jpeg", ".png"],
    maxSize: 5,
  },
  {
    id: "uace_certificate",
    name: "UACE Certificate / Result Slip",
    description: "UNEB UACE certificate or provisional result slip (where applicable)",
    required: false,
    acceptedTypes: [".pdf", ".jpg", ".jpeg", ".png"],
    maxSize: 5,
  },
  {
    id: "diploma_certificate",
    name: "Diploma / National Certificate",
    description: "Diploma or National Certificate (for Diploma/Certificate entry or Direct Entry applicants)",
    required: false,
    acceptedTypes: [".pdf", ".jpg", ".jpeg", ".png"],
    maxSize: 5,
  },
  {
    id: "hec_certificate",
    name: "HEC Certificate / Result Slip",
    description: "Higher Education Certificate result slip (for HEC entry applicants)",
    required: false,
    acceptedTypes: [".pdf", ".jpg", ".jpeg", ".png"],
    maxSize: 5,
  },
  {
    id: "recommendation_letter",
    name: "Recommendation Letter",
    description: "Letter from school headteacher, employer, or community leader (required for scholarship/bursary applicants)",
    required: false,
    acceptedTypes: [".pdf", ".jpg", ".jpeg", ".png"],
    maxSize: 5,
  },
  {
    id: "passport_photo",
    name: "Passport Size Photo",
    description: "Recent passport photo with white background (optional - can be uploaded later)",
    required: false,
    acceptedTypes: [".jpg", ".jpeg", ".png"],
    maxSize: 2,
  },
];

// Validation schema
const documentSchema = z.object({
  documents: z.record(
    z.object({
      file: z.instanceof(File).optional(),
      uploaded: z.boolean().default(false),
    })
  ),
  declaration: z.boolean().refine((val) => val === true, {
    message: "You must accept the declaration",
  }),
});

export type DocumentData = z.infer<typeof documentSchema>;

interface DocumentUploadProps {
  onNext: (data: DocumentData & { files: Record<string, File> }) => void;
  onBack: () => void;
  defaultValues?: Partial<DocumentData>;
}

interface UploadFile {
  file: File | null;
  error: string | null;
  uploaded: boolean;
}

export default function DocumentUpload({ onNext, onBack, defaultValues }: DocumentUploadProps) {
  const [files, setFiles] = useState<Record<string, UploadFile>>({});
  const [declaration, setDeclaration] = useState(false);

  // Initialize files state
  const handleFileChange = useCallback((docId: string, file: File | null) => {
    const docConfig = REQUIRED_DOCUMENTS.find((d) => d.id === docId);
    if (!docConfig || !file) {
      setFiles((prev) => ({
        ...prev,
        [docId]: { file: null, error: null, uploaded: false },
      }));
      return;
    }

    // Validate file type
    const fileExtension = `.${file.name.split(".").pop()?.toLowerCase()}`;
    if (!docConfig.acceptedTypes.includes(fileExtension)) {
      setFiles((prev) => ({
        ...prev,
        [docId]: {
          file: null,
          error: `Invalid file type. Accept: ${docConfig.acceptedTypes.join(", ")}`,
          uploaded: false,
        },
      }));
      return;
    }

    // Validate file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > docConfig.maxSize) {
      setFiles((prev) => ({
        ...prev,
        [docId]: {
          file: null,
          error: `File too large. Max: ${docConfig.maxSize}MB`,
          uploaded: false,
        },
      }));
      return;
    }

    setFiles((prev) => ({
      ...prev,
      [docId]: { file, error: null, uploaded: true },
    }));
  }, []);

  const clearFile = (docId: string) => {
    setFiles((prev) => ({
      ...prev,
      [docId]: { file: null, error: null, uploaded: false },
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Check required documents
    const missingRequired = REQUIRED_DOCUMENTS.filter(
      (doc) => doc.required && !files[doc.id]?.uploaded
    );

    if (missingRequired.length > 0) {
      // Show errors for missing required docs
      const newFiles = { ...files };
      missingRequired.forEach((doc) => {
        newFiles[doc.id] = {
          file: null,
          error: "This document is required",
          uploaded: false,
        };
      });
      setFiles(newFiles);
      return;
    }

    if (!declaration) {
      return;
    }

    // Collect all uploaded files
    const uploadedFiles: Record<string, File> = {};
    Object.entries(files).forEach(([docId, fileData]) => {
      if (fileData.file) {
        uploadedFiles[docId] = fileData.file;
      }
    });

    onNext({
      documents: files,
      declaration,
      files: uploadedFiles,
    });
  };

  const requiredCount = REQUIRED_DOCUMENTS.filter((d) => d.required).length;
  const uploadedRequiredCount = REQUIRED_DOCUMENTS.filter(
    (d) => d.required && files[d.id]?.uploaded
  ).length;
  const uploadedOptionalCount = REQUIRED_DOCUMENTS.filter(
    (d) => !d.required && files[d.id]?.uploaded
  ).length;

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
            <FileText className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold">Step 5: Document Upload</h1>
          <p className="mt-2 text-muted-foreground">
            Upload all required documents for your application. Accepted formats: PDF, JPG, PNG.
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-primary">Step 5 of 6</span>
            <span className="text-muted-foreground">Document Upload</span>
          </div>
          <div className="h-2 mt-2 rounded-full bg-muted">
            <div className="h-full w-5/6 rounded-full bg-primary" />
          </div>
        </div>

        {/* Upload Summary */}
        <div className="p-4 mb-6 rounded-lg bg-muted/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold">Upload Progress</p>
              <p className="text-sm text-muted-foreground">
                {uploadedRequiredCount} of {requiredCount} required documents uploaded
                {uploadedOptionalCount > 0 && `, ${uploadedOptionalCount} optional`}
              </p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold text-primary">
                {Math.round((uploadedRequiredCount / requiredCount) * 100)}%
              </span>
            </div>
          </div>
          <div className="h-2 mt-3 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${(uploadedRequiredCount / requiredCount) * 100}%` }}
            />
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Document Upload Grid */}
          <div className="grid gap-4 md:grid-cols-2">
            {REQUIRED_DOCUMENTS.map((doc) => {
              const fileData = files[doc.id];
              const isUploaded = fileData?.uploaded;
              const hasError = fileData?.error;

              return (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className={`p-4 border-2 rounded-lg transition-all ${
                    isUploaded
                      ? "border-green-500 bg-green-50"
                      : hasError
                      ? "border-destructive bg-destructive/5"
                      : doc.required
                      ? "border-orange-300"
                      : "border-muted"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2 rounded-lg ${
                        isUploaded
                          ? "bg-green-100"
                          : doc.required
                          ? "bg-orange-100"
                          : "bg-muted"
                      }`}
                    >
                      {isUploaded ? (
                        <FileCheck className="w-5 h-5 text-green-600" />
                      ) : (
                        <FileText className="w-5 h-5 text-muted-foreground" />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">
                          {doc.name}
                          {doc.required && (
                            <span className="ml-1 text-destructive">*</span>
                          )}
                        </h3>
                        {isUploaded && (
                          <Check className="w-4 h-4 text-green-600" />
                        )}
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {doc.description}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Max: {doc.maxSize}MB | {doc.acceptedTypes.join(", ")}
                      </p>

                      {hasError && (
                        <div className="flex items-center gap-1 mt-2 text-sm text-destructive">
                          <AlertCircle className="w-4 h-4" />
                          {hasError}
                        </div>
                      )}

                      {isUploaded && fileData.file && (
                        <div className="flex items-center gap-2 mt-2 text-sm text-green-700">
                          <span className="truncate">{fileData.file.name}</span>
                          <span className="text-muted-foreground">
                            ({(fileData.file.size / 1024 / 1024).toFixed(2)} MB)
                          </span>
                        </div>
                      )}

                      <div className="flex items-center gap-2 mt-3">
                        <input
                          type="file"
                          id={`file-${doc.id}`}
                          accept={doc.acceptedTypes.join(",")}
                          onChange={(e) =>
                            handleFileChange(doc.id, e.target.files?.[0] || null)
                          }
                          className="hidden"
                        />

                        {isUploaded ? (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => clearFile(doc.id)}
                          >
                            <X className="w-4 h-4 mr-2" />
                            Remove
                          </Button>
                        ) : (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              document.getElementById(`file-${doc.id}`)?.click()
                            }
                          >
                            <Upload className="w-4 h-4 mr-2" />
                            Upload
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Declaration */}
          <div className="p-6 border-2 rounded-lg border-primary/20 bg-primary/5">
            <div className="flex items-start gap-3">
              <Checkbox
                id="declaration"
                checked={declaration}
                onCheckedChange={(checked) => setDeclaration(checked as boolean)}
                className="mt-1"
              />
              <div>
                <Label htmlFor="declaration" className="font-semibold cursor-pointer">
                  Declaration & Consent *
                </Label>
                <p className="mt-2 text-sm text-muted-foreground">
                  I hereby declare that all the information and documents provided in this
                  application are true, complete, and accurate to the best of my knowledge.
                  I understand that providing false information or forged documents may result
                  in the rejection of my application, cancellation of admission, or disciplinary
                  action. I consent to KIU verifying my academic credentials with UNEB and
                  other relevant authorities.
                </p>
                {!declaration && (
                  <p className="mt-2 text-sm text-destructive">
                    You must accept the declaration to continue
                  </p>
                )}
              </div>
            </div>
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
              disabled={uploadedRequiredCount < requiredCount || !declaration}
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
