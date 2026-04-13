import { useState, useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, ArrowRight, Search, BookOpen, MapPin, Clock, Check, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// Simplified program data - would come from API in production
const KIU_PROGRAMS = [
  // Certificate Programs
  { id: "CERT-NUR", name: "Certificate in Nursing", level: "Certificate", duration: "1.5 years", campus: "Western", faculty: "Health Sciences", fees: "950,000 UGX" },
  { id: "CERT-BA", name: "Certificate in Business Administration", level: "Certificate", duration: "1 year", campus: "Main", faculty: "Business & Management", fees: "750,000 UGX" },
  
  // Diploma Programs
  { id: "DIP-NUR", name: "Diploma in Nursing", level: "Diploma", duration: "2 years", campus: "Western", faculty: "Health Sciences", fees: "1,250,000 UGX" },
  { id: "DIP-BA", name: "Diploma in Business Administration", level: "Diploma", duration: "2 years", campus: "Main", faculty: "Business & Management", fees: "750,000 UGX" },
  { id: "DIP-CS", name: "Diploma in Computer Science", level: "Diploma", duration: "2 years", campus: "Main", faculty: "Computing & IT", fees: "800,000 UGX" },
  
  // Bachelor's - Health Sciences
  { id: "BCH-MBCHB", name: "Bachelor of Medicine & Bachelor of Surgery (MBChB)", level: "Bachelor", duration: "5 years", campus: "Western", faculty: "Health Sciences", fees: "7,085,000 UGX" },
  { id: "BCH-BPHARM", name: "Bachelor of Pharmacy", level: "Bachelor", duration: "4 years", campus: "Western", faculty: "Health Sciences", fees: "5,760,000 UGX" },
  { id: "BCH-BNSC", name: "Bachelor of Nursing Science", level: "Bachelor", duration: "4 years", campus: "Western", faculty: "Health Sciences", fees: "3,215,000 UGX" },
  
  // Bachelor's - Business & Computing
  { id: "BBA-BBA", name: "Bachelor of Business Administration", level: "Bachelor", duration: "3 years", campus: "Main", faculty: "Business & Management", fees: "1,130,000 UGX" },
  { id: "BBA-BCOM", name: "Bachelor of Commerce", level: "Bachelor", duration: "3 years", campus: "Main", faculty: "Business & Management", fees: "1,130,000 UGX" },
  { id: "BIT-BCS", name: "Bachelor of Computer Science", level: "Bachelor", duration: "3 years", campus: "Main", faculty: "Computing & IT", fees: "1,130,000 UGX" },
  { id: "BIT-BIT", name: "Bachelor of Information Technology", level: "Bachelor", duration: "3 years", campus: "Main", faculty: "Computing & IT", fees: "1,130,000 UGX" },
  
  // Bachelor's - Education & Law
  { id: "BED-BAED", name: "Bachelor of Arts with Education", level: "Bachelor", duration: "3 years", campus: "Main", faculty: "Education", fees: "1,130,000 UGX" },
  { id: "BLAW-LLB", name: "Bachelor of Laws (LLB)", level: "Bachelor", duration: "4 years", campus: "Main", faculty: "Law", fees: "1,600,000 UGX" },
  
  // HEC
  { id: "HEC-HEC", name: "Higher Education Certificate (HEC)", level: "HEC", duration: "1 year", campus: "Main", faculty: "Foundation", fees: "600,000 UGX" },
];

const step4Schema = z.object({
  applicationType: z.enum(["first_year", "diploma_entry", "direct_entry", "transfer", "postgraduate"]),
  firstChoice: z.string().min(1, "First choice is required"),
  secondChoice: z.string().optional(),
  thirdChoice: z.string().optional(),
  entryLevel: z.enum(["year_1", "year_2", "year_3"]).default("year_1"),
});

type Step4Data = z.infer<typeof step4Schema>;

interface ProgramSelectionProps {
  onNext: (data: Step4Data) => void;
  onBack: () => void;
  defaultValues?: Partial<Step4Data>;
}

const applicationTypes = [
  { value: "first_year", label: "First Year", description: "Apply for Year 1 with UACE or HEC" },
  { value: "diploma_entry", label: "Diploma/Certificate Entry", description: "Enter with Diploma or Certificate" },
  { value: "direct_entry", label: "Direct Entry (Year 2/3)", description: "Enter Year 2 or 3 with prior qualification" },
  { value: "transfer", label: "Transfer", description: "Transfer from another university" },
  { value: "postgraduate", label: "Postgraduate", description: "Masters or PhD programs" },
];

const faculties = ["All", "Health Sciences", "Business & Management", "Computing & IT", "Education", "Law", "Foundation"];
const campuses = ["All", "Main (Kampala)", "Western (Ishaka)"];
const levels = ["All", "Certificate", "Diploma", "Bachelor", "HEC"];

export default function ProgramSelection({ onNext, onBack, defaultValues }: ProgramSelectionProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFaculty, setSelectedFaculty] = useState("All");
  const [selectedCampus, setSelectedCampus] = useState("All");
  const [selectedLevel, setSelectedLevel] = useState("All");
  
  const { handleSubmit, formState: { errors, isSubmitting }, setValue, watch } = useForm<Step4Data>({
    resolver: zodResolver(step4Schema),
    defaultValues: {
      applicationType: defaultValues?.applicationType || undefined,
      firstChoice: defaultValues?.firstChoice || "",
      secondChoice: defaultValues?.secondChoice || "",
      thirdChoice: defaultValues?.thirdChoice || "",
      entryLevel: defaultValues?.entryLevel || "year_1",
    },
  });

  const applicationType = watch("applicationType");
  const firstChoice = watch("firstChoice");
  const secondChoice = watch("secondChoice");
  const thirdChoice = watch("thirdChoice");
  const entryLevel = watch("entryLevel");

  const filteredPrograms = useMemo(() => {
    return KIU_PROGRAMS.filter((program) => {
      const matchesSearch = program.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFaculty = selectedFaculty === "All" || program.faculty === selectedFaculty;
      const matchesCampus = selectedCampus === "All" || 
        (selectedCampus === "Main (Kampala)" && program.campus === "Main") ||
        (selectedCampus === "Western (Ishaka)" && program.campus === "Western");
      const matchesLevel = selectedLevel === "All" || program.level === selectedLevel;
      return matchesSearch && matchesFaculty && matchesCampus && matchesLevel;
    });
  }, [searchQuery, selectedFaculty, selectedCampus, selectedLevel]);

  const selectedProgramDetails = useMemo(() => {
    return KIU_PROGRAMS.find(p => p.id === firstChoice);
  }, [firstChoice]);

  const getCampusColor = (campus: string) => {
    return campus === "Western" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800";
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case "Certificate": return "bg-orange-100 text-orange-800";
      case "Diploma": return "bg-purple-100 text-purple-800";
      case "Bachelor": return "bg-indigo-100 text-indigo-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const selectProgram = (programId: string, choiceNumber: 1 | 2 | 3) => {
    if (choiceNumber === 1) setValue("firstChoice", programId);
    else if (choiceNumber === 2) setValue("secondChoice", programId);
    else if (choiceNumber === 3) setValue("thirdChoice", programId);
  };

  const clearChoice = (choiceNumber: 1 | 2 | 3) => {
    if (choiceNumber === 1) setValue("firstChoice", "");
    else if (choiceNumber === 2) setValue("secondChoice", "");
    else if (choiceNumber === 3) setValue("thirdChoice", "");
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-6xl mx-auto">
      <Card className="p-8">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-primary/10">
            <BookOpen className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold">Step 4: Program Selection</h1>
          <p className="mt-2 text-muted-foreground">Select your preferred program(s) from 143+ KIU offerings</p>
        </div>

        <div className="mb-8">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-primary">Step 4 of 6</span>
            <span className="text-muted-foreground">Program Selection</span>
          </div>
          <div className="h-2 mt-2 rounded-full bg-muted">
            <div className="h-full w-4/6 rounded-full bg-primary" />
          </div>
        </div>

        <form onSubmit={handleSubmit(onNext)} className="space-y-6">
          {/* Application Type */}
          <div className="p-6 rounded-lg bg-muted/50">
            <Label className="text-base font-semibold">Application Type *</Label>
            <div className="grid gap-4 mt-4 md:grid-cols-2 lg:grid-cols-3">
              {applicationTypes.map((type) => (
                <div
                  key={type.value}
                  onClick={() => setValue("applicationType", type.value as any)}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    applicationType === type.value ? "border-primary bg-primary/5" : "border-muted hover:border-primary/50"
                  }`}
                >
                  <div className="font-semibold">{type.label}</div>
                  <p className="mt-1 text-sm text-muted-foreground">{type.description}</p>
                </div>
              ))}
            </div>
            {errors.applicationType && <p className="mt-2 text-sm text-destructive">{errors.applicationType.message}</p>}
          </div>

          {/* Search & Filters */}
          <div className="p-6 rounded-lg bg-muted/50">
            <div className="grid gap-4 md:grid-cols-4">
              <div className="relative">
                <Search className="absolute w-4 h-4 left-3 top-3 text-muted-foreground" />
                <Input
                  placeholder="Search programs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={selectedFaculty} onValueChange={setSelectedFaculty}>
                <SelectTrigger><SelectValue placeholder="Faculty" /></SelectTrigger>
                <SelectContent>
                  {faculties.map(f => <SelectItem key={f} value={f}>{f}</SelectItem>)}
                </SelectContent>
              </Select>
              <Select value={selectedCampus} onValueChange={setSelectedCampus}>
                <SelectTrigger><SelectValue placeholder="Campus" /></SelectTrigger>
                <SelectContent>
                  {campuses.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
              <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                <SelectTrigger><SelectValue placeholder="Level" /></SelectTrigger>
                <SelectContent>
                  {levels.map(l => <SelectItem key={l} value={l}>{l}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">Showing {filteredPrograms.length} programs</p>
          </div>

          {/* Program Choices */}
          <div className="p-6 rounded-lg bg-muted/50">
            <Label className="text-base font-semibold">Your Program Choices</Label>
            <div className="grid gap-4 mt-4 md:grid-cols-3">
              {/* First Choice */}
              <div className="p-4 border-2 rounded-lg border-primary">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-primary">First Choice *</span>
                  {firstChoice && (
                    <Button type="button" variant="ghost" size="sm" onClick={() => clearChoice(1)}>
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
                {firstChoice ? (
                  <div>
                    <p className="font-medium">{KIU_PROGRAMS.find(p => p.id === firstChoice)?.name}</p>
                    <p className="text-sm text-muted-foreground">{KIU_PROGRAMS.find(p => p.id === firstChoice)?.faculty}</p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Select from list below</p>
                )}
              </div>

              {/* Second Choice */}
              <div className="p-4 border-2 border-dashed rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Second Choice (Optional)</span>
                  {secondChoice && (
                    <Button type="button" variant="ghost" size="sm" onClick={() => clearChoice(2)}>
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
                {secondChoice ? (
                  <div>
                    <p className="font-medium">{KIU_PROGRAMS.find(p => p.id === secondChoice)?.name}</p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Select from list below</p>
                )}
              </div>

              {/* Third Choice */}
              <div className="p-4 border-2 border-dashed rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Third Choice (Optional)</span>
                  {thirdChoice && (
                    <Button type="button" variant="ghost" size="sm" onClick={() => clearChoice(3)}>
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
                {thirdChoice ? (
                  <div>
                    <p className="font-medium">{KIU_PROGRAMS.find(p => p.id === thirdChoice)?.name}</p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Select from list below</p>
                )}
              </div>
            </div>
            {errors.firstChoice && <p className="mt-2 text-sm text-destructive">{errors.firstChoice.message}</p>}
          </div>

          {/* Entry Level */}
          {selectedProgramDetails && (
            <div className="p-6 rounded-lg bg-primary/5 border border-primary/20">
              <Label className="text-base font-semibold">Entry Level</Label>
              <div className="flex gap-4 mt-4">
                {["year_1", "year_2", "year_3"].map((year) => (
                  <div
                    key={year}
                    onClick={() => setValue("entryLevel", year as any)}
                    className={`px-4 py-2 border-2 rounded-lg cursor-pointer ${
                      entryLevel === year ? "border-primary bg-primary/10" : "border-muted"
                    }`}
                  >
                    Year {year.split("_")[1]}
                  </div>
                ))}
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                Suggested entry: Year 1 (based on your education background)
              </p>
            </div>
          )}

          {/* Program List */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Available Programs</Label>
            <div className="grid gap-3 max-h-[400px] overflow-y-auto p-2">
              <AnimatePresence>
                {filteredPrograms.map((program) => (
                  <motion.div
                    key={program.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className={`p-4 border rounded-lg transition-all ${
                      firstChoice === program.id ? "border-primary bg-primary/5" : 
                      secondChoice === program.id ? "border-blue-400 bg-blue-50" :
                      thirdChoice === program.id ? "border-green-400 bg-green-50" :
                      "border-muted hover:border-primary/50"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-semibold">{program.name}</h3>
                          <Badge className={getLevelColor(program.level)}>{program.level}</Badge>
                          <Badge className={getCampusColor(program.campus)}>{program.campus}</Badge>
                        </div>
                        <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> {program.duration}</span>
                          <span className="flex items-center gap-1"><MapPin className="w-4 h-4" /> {program.campus} Campus</span>
                          <span>{program.faculty}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        {!firstChoice && (
                          <Button type="button" size="sm" onClick={() => selectProgram(program.id, 1)}>
                            1st Choice
                          </Button>
                        )}
                        {firstChoice !== program.id && !secondChoice && (
                          <Button type="button" size="sm" variant="outline" onClick={() => selectProgram(program.id, 2)}>
                            2nd
                          </Button>
                        )}
                        {firstChoice !== program.id && secondChoice !== program.id && !thirdChoice && (
                          <Button type="button" size="sm" variant="outline" onClick={() => selectProgram(program.id, 3)}>
                            3rd
                          </Button>
                        )}
                        {(firstChoice === program.id || secondChoice === program.id || thirdChoice === program.id) && (
                          <Check className="w-5 h-5 text-green-600" />
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex justify-between pt-6">
            <Button type="button" variant="outline" onClick={onBack} className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" /> Back
            </Button>
            <Button type="submit" className="flex items-center gap-2 px-8" isLoading={isSubmitting}>
              Next Step <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </form>
      </Card>
    </motion.div>
  );
}
