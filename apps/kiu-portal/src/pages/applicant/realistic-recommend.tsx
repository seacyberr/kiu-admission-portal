import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { AlertTriangle, CheckCircle, XCircle, Clock, Users, Target } from "lucide-react";

interface Programme {
  id: string;
  code: string;
  name: string;
  faculty: string;
  duration_years: number;
  intake_months: number[];
  campus: string[];
  tuition_ugx_per_semester: number;
  tuition_usd_per_semester: number;
  category: string;
  competition_level: string;
  annual_quota: number;
  nche_requirements: {
    minimum_subjects: string[];
    essential_subjects: string[];
    relevant_subjects: string[];
    minimum_uace_points: number;
    minimum_principal_passes: number;
    minimum_uce_passes: number;
    mandatory_credits: string[];
    diploma_alternative?: {
      eligible: boolean;
      diplomas: string[];
      minimum_class: string;
      work_experience: number;
      professional_registration: boolean;
    };
  };
  admission_statistics: {
    applications_2024: number;
    admitted_2024: number;
    average_uace_points_admitted: number;
    cut_off_points: number;
  };
  career_prospects: string[];
  accreditation: string;
  assessment?: {
    eligible: boolean;
    strong_candidate: boolean;
    admission_chance: string;
    reasons_pass: string[];
    reasons_fail: string[];
    warnings: string[];
    meets_minimum: boolean;
    points_calculation: {
      total_points: number;
      principal_passes: number;
      required_points: number;
      required_principal_passes: number;
    };
  };
  apply_url?: string;
}

const UACE_SUBJECTS = [
  "Mathematics", "Physics", "Chemistry", "Biology", "Geography", "History",
  "Economics", "Literature", "Divinity", "Entrepreneurship", "Computer Studies",
  "Technical Drawing", "Art", "Music", "Agriculture", "General Paper"
];

const UACE_GRADES = ["A", "B", "C", "D", "E", "O", "F"];

const DIPLOMA_TYPES = [
  "Diploma in Clinical Medicine",
  "Diploma in Nursing",
  "Diploma in Medical Laboratory",
  "Diploma in Pharmacy",
  "Diploma in Civil Engineering",
  "Diploma in Electrical Engineering",
  "Diploma in Computer Science",
  "Diploma in Information Technology",
  "Diploma in Business Administration",
  "Diploma in Accounting",
  "Diploma in Law",
  "Diploma in Education"
];

export default function RealisticRecommendationsPage() {
  const [step, setStep] = useState<"qualification" | "uace" | "diploma" | "results">("qualification");
  const [qualificationType, setQualificationType] = useState<"uace" | "diploma" | "bachelors">("uace");
  const [uaceSubjects, setUaceSubjects] = useState<string[]>([]);
  const [uaceGrades, setUaceGrades] = useState<Record<string, string>>({});
  const [ucePasses, setUcePasses] = useState<number>(5);
  const [diplomaType, setDiplomaType] = useState<string>("");
  const [diplomaClass, setDiplomaClass] = useState<string>("");
  const [workExperience, setWorkExperience] = useState<number>(0);
  const [bachelorGpa, setBachelorGpa] = useState<number>(3.0);
  const [recommendations, setRecommendations] = useState<Programme[]>([]);
  const [loading, setLoading] = useState(false);

  const calculatePoints = () => {
    const gradePoints: Record<string, number> = { "A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0 };
    return uaceSubjects.reduce((total, subject) => {
      const grade = uaceGrades[subject];
      return total + (gradePoints[grade] || 0);
    }, 0);
  };

  const getPrincipalPasses = () => {
    return uaceSubjects.filter(subject => {
      const grade = uaceGrades[subject];
      return grade && ["A", "B", "C", "D", "E"].includes(grade);
    }).length;
  };

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const applicantData: any = {
        qualification_type: qualificationType
      };

      if (qualificationType === "uace") {
        applicantData.uace_subjects = uaceSubjects;
        applicantData.uace_grades = uaceGrades;
        applicantData.principal_passes = getPrincipalPasses();
        applicantData.uce_passes = ucePasses;
      } else if (qualificationType === "diploma") {
        applicantData.diploma_type = diplomaType;
        applicantData.diploma_class = diplomaClass;
        applicantData.work_experience = workExperience;
      } else if (qualificationType === "bachelors") {
        applicantData.bachelor_gpa = bachelorGpa;
        applicantData.work_experience = workExperience;
      }

      const response = await fetch("/api/v1/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(applicantData)
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations);
        setStep("results");
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const fmtUGX = (amount: number) => {
    return new Intl.NumberFormat("en-UG", {
      style: "currency",
      currency: "UGX",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getChanceColor = (chance: string) => {
    switch (chance) {
      case "High": return "bg-green-500";
      case "Medium": return "bg-yellow-500";
      case "Low": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getCompetitionColor = (level: string) => {
    switch (level) {
      case "Very High": return "bg-red-100 text-red-800";
      case "High": return "bg-orange-100 text-orange-800";
      case "Medium": return "bg-yellow-100 text-yellow-800";
      case "Low": return "bg-green-100 text-green-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const renderQualificationStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">What is your highest qualification?</h2>
        <p className="text-gray-600">This helps us assess your eligibility accurately</p>
      </div>

      <div className="space-y-4">
        <div className="p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
             onClick={() => { setQualificationType("uace"); setStep("uace"); }}>
          <div className="flex items-center space-x-3">
            <input
              type="radio"
              name="qualification"
              checked={qualificationType === "uace"}
              onChange={() => setQualificationType("uace")}
              className="w-4 h-4"
            />
            <div>
              <h3 className="font-semibold">A-Level (UACE)</h3>
              <p className="text-sm text-gray-600">For direct undergraduate admission</p>
            </div>
          </div>
        </div>

        <div className="p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
             onClick={() => { setQualificationType("diploma"); setStep("diploma"); }}>
          <div className="flex items-center space-x-3">
            <input
              type="radio"
              name="qualification"
              checked={qualificationType === "diploma"}
              onChange={() => setQualificationType("diploma")}
              className="w-4 h-4"
            />
            <div>
              <h3 className="font-semibold">Diploma/Certificate</h3>
              <p className="text-sm text-gray-600">For advanced standing admission</p>
            </div>
          </div>
        </div>

        <div className="p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
             onClick={() => { setQualificationType("bachelors"); setStep("diploma"); }}>
          <div className="flex items-center space-x-3">
            <input
              type="radio"
              name="qualification"
              checked={qualificationType === "bachelors"}
              onChange={() => setQualificationType("bachelors")}
              className="w-4 h-4"
            />
            <div>
              <h3 className="font-semibold">Bachelor's Degree</h3>
              <p className="text-sm text-gray-600">For postgraduate programmes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUACEStep = () => (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Enter your UACE Results</h2>
        <p className="text-gray-600">Provide your subjects and grades for accurate assessment</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold mb-3">Select Subjects (max 3 principal + 2 subsidiary)</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {UACE_SUBJECTS.map((subject) => (
              <div key={subject} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={subject}
                  checked={uaceSubjects.includes(subject)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      if (uaceSubjects.length < 5) {
                        setUaceSubjects([...uaceSubjects, subject]);
                      }
                    } else {
                      setUaceSubjects(uaceSubjects.filter(s => s !== subject));
                      setUaceGrades(prev => {
                        const newGrades = { ...prev };
                        delete newGrades[subject];
                        return newGrades;
                      });
                    }
                  }}
                  className="w-4 h-4"
                />
                <Label htmlFor={subject} className="text-sm">{subject}</Label>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-semibold mb-3">Enter Grades</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {uaceSubjects.map((subject) => (
              <div key={subject} className="flex items-center space-x-2">
                <Label className="text-sm w-32">{subject}:</Label>
                <select
                  value={uaceGrades[subject] || ""}
                  onChange={(e) => setUaceGrades({ ...uaceGrades, [subject]: e.target.value })}
                  className="w-20 p-1 border rounded text-sm"
                >
                  <option value="">Grade</option>
                  {UACE_GRADES.map(grade => (
                    <option key={grade} value={grade}>{grade}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold mb-2">UCE Results</h3>
        <div className="flex items-center space-x-4">
          <Label>Number of UCE passes:</Label>
          <input
            type="number"
            min="0"
            max="8"
            value={ucePasses}
            onChange={(e) => setUcePasses(parseInt(e.target.value) || 0)}
            className="w-20 p-2 border rounded"
          />
        </div>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold mb-2">Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium">Total Points:</span>
            <div className="text-lg font-bold text-blue-600">{calculatePoints()}</div>
          </div>
          <div>
            <span className="font-medium">Principal Passes:</span>
            <div className="text-lg font-bold text-blue-600">{getPrincipalPasses()}</div>
          </div>
          <div>
            <span className="font-medium">UCE Passes:</span>
            <div className="text-lg font-bold text-blue-600">{ucePasses}</div>
          </div>
          <div>
            <span className="font-medium">Subjects:</span>
            <div className="text-lg font-bold text-blue-600">{uaceSubjects.length}</div>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setStep("qualification")}>
          Back
        </Button>
        <Button onClick={fetchRecommendations} disabled={uaceSubjects.length === 0 || loading}>
          {loading ? "Assessing..." : "Get Admission Assessment"}
        </Button>
      </div>
    </div>
  );

  const renderDiplomaStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">
          {qualificationType === "diploma" ? "Diploma Details" : "Bachelor's Degree Details"}
        </h2>
        <p className="text-gray-600">Provide your qualification information</p>
      </div>

      <div className="space-y-4">
        {qualificationType === "diploma" && (
          <div>
            <Label>Diploma Type</Label>
            <select
              value={diplomaType}
              onChange={(e) => setDiplomaType(e.target.value)}
              className="w-full p-2 border rounded"
            >
              <option value="">Select diploma type</option>
              {DIPLOMA_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        )}

        <div>
          <Label>Classification/Class</Label>
          <select
            value={diplomaClass}
            onChange={(e) => setDiplomaClass(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Select classification</option>
            {qualificationType === "diploma" ? (
              <>
                <option value="Distinction">Distinction</option>
                <option value="Credit">Credit</option>
                <option value="Pass">Pass</option>
              </>
            ) : (
              <>
                <option value="First Class">First Class</option>
                <option value="Second Class Upper">Second Class Upper</option>
                <option value="Second Class Lower">Second Class Lower</option>
                <option value="Pass">Pass</option>
              </>
            )}
          </select>
        </div>

        {qualificationType === "bachelors" && (
          <div>
            <Label>GPA (out of 4.0)</Label>
            <input
              type="number"
              min="0"
              max="4"
              step="0.1"
              value={bachelorGpa}
              onChange={(e) => setBachelorGpa(parseFloat(e.target.value) || 0)}
              className="w-full p-2 border rounded"
            />
          </div>
        )}

        <div>
          <Label>Work Experience (years)</Label>
          <input
            type="number"
            min="0"
            value={workExperience}
            onChange={(e) => setWorkExperience(parseInt(e.target.value) || 0)}
            className="w-full p-2 border rounded"
          />
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setStep("qualification")}>
          Back
        </Button>
        <Button onClick={fetchRecommendations} disabled={loading}>
          {loading ? "Assessing..." : "Get Admission Assessment"}
        </Button>
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Admission Assessment Results</h2>
        <p className="text-gray-600">Based on NCHE standards and actual admission statistics</p>
      </div>

      {recommendations.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <XCircle className="w-16 h-16 mx-auto text-red-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">No programmes match your profile</h3>
            <p className="text-gray-600 mb-4">Consider upgrading your qualifications</p>
            <Button onClick={() => setStep("qualification")}>Start Over</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {recommendations.map((programme) => (
            <Card key={programme.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">{programme.name}</h3>
                    <p className="text-gray-600">{programme.faculty}</p>
                  </div>
                  <div className="text-right space-y-2">
                    <Badge className={getChanceColor(programme.assessment?.admission_chance || "Low")}>
                      {programme.assessment?.admission_chance} Chance
                    </Badge>
                    <Badge className={getCompetitionColor(programme.competition_level)}>
                      {programme.competition_level} Competition
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      <Users className="w-4 h-4 mr-2" />
                      {programme.admission_statistics.admitted_2024}/{programme.admission_statistics.applications_2024} admitted
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Target className="w-4 h-4 mr-2" />
                      Cut-off: {programme.admission_statistics.cut_off_points} points
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      {programme.duration_years} years
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Your Points:</span>
                      <div className="text-lg font-bold text-blue-600">
                        {programme.assessment?.points_calculation?.total_points || 0}
                      </div>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Principal Passes:</span>
                      <div>{programme.assessment?.points_calculation?.principal_passes || 0}</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Tuition:</span>
                      <div className="text-gray-600">
                        {fmtUGX(programme.tuition_ugx_per_semester)}/semester
                      </div>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Next Intake:</span>
                      <div className="text-gray-600">
                        {programme.intake_months.map(m => {
                          const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                          return months[m - 1];
                        }).join(", ")}
                      </div>
                    </div>
                  </div>
                </div>

                {programme.assessment && (
                  <div className="mb-4 space-y-2">
                    {programme.assessment.reasons_pass.length > 0 && (
                      <div className="p-3 bg-green-50 rounded-lg">
                        <p className="text-sm font-medium text-green-900 mb-1">Strengths:</p>
                        <ul className="text-sm text-green-800 space-y-1">
                          {programme.assessment.reasons_pass.map((reason, index) => (
                            <li key={index} className="flex items-center">
                              <CheckCircle className="w-3 h-3 mr-2 text-green-600" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {programme.assessment.reasons_fail.length > 0 && (
                      <div className="p-3 bg-red-50 rounded-lg">
                        <p className="text-sm font-medium text-red-900 mb-1">Issues:</p>
                        <ul className="text-sm text-red-800 space-y-1">
                          {programme.assessment.reasons_fail.map((reason, index) => (
                            <li key={index} className="flex items-center">
                              <XCircle className="w-3 h-3 mr-2 text-red-600" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {programme.assessment.warnings.length > 0 && (
                      <div className="p-3 bg-yellow-50 rounded-lg">
                        <p className="text-sm font-medium text-yellow-900 mb-1">Considerations:</p>
                        <ul className="text-sm text-yellow-800 space-y-1">
                          {programme.assessment.warnings.map((reason, index) => (
                            <li key={index} className="flex items-center">
                              <AlertTriangle className="w-3 h-3 mr-2 text-yellow-600" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-500">
                    Accredited by {programme.accreditation}
                  </div>
                  <Button asChild disabled={!programme.assessment?.eligible}>
                    <a href={programme.apply_url}>
                      {programme.assessment?.eligible ? "Apply Now" : "Not Eligible"}
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="text-center">
        <Button variant="outline" onClick={() => setStep("qualification")}>
          Start Over
        </Button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Realistic Admission Assessment
          </h1>
          <p className="text-gray-600">
            Get accurate eligibility assessment based on NCHE standards and actual admission statistics
          </p>
        </div>

        {step === "qualification" && renderQualificationStep()}
        {step === "uace" && renderUACEStep()}
        {step === "diploma" && renderDiplomaStep()}
        {step === "results" && renderResults()}
      </div>
    </div>
  );
}
