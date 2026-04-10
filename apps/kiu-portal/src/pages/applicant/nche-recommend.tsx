import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { CheckCircle, XCircle, AlertTriangle, Award, BookOpen, Users, Target, Shield, FileText } from "lucide-react";

interface NCHESubject {
  name: string;
  grade: string;
  type: "essential" | "relevant" | "desirable";
}

interface NCHEProgramme {
  id: string;
  code: string;
  name: string;
  faculty: string;
  nche_category: string;
  duration_years: number;
  intake_months: number[];
  campus: string[];
  tuition_ugx_per_semester: number;
  tuition_usd_per_semester: number;
  nche_accreditation: {
    status: string;
    accreditation_number: string;
    expiry_date: string;
    programme_level: string;
    credits_required: number;
  };
  admission_quota: {
    government_sponsored: number;
    private_sponsored: number;
    total: number;
    female_minimum: number;
  };
  nche_requirements: {
    essential: string[];
    relevant: string[];
    desirable: string[];
    minimum_points: number;
    minimum_principal_passes: number;
    uce_requirement: string;
  };
  admission_statistics_2024: {
    total_applications: number;
    government_admitted: number;
    private_admitted: number;
    cut_off_points: number;
    average_points_admitted: number;
    female_admitted: number;
  };
  career_prospects: string[];
  professional_registration: string[];
  nche_assessment?: {
    eligible: boolean;
    strong_candidate: boolean;
    admission_category: string;
    meets_nche_minimum: boolean;
    meets_programme_requirements: boolean;
    points_calculation: {
      total_points: number;
      principal_passes: number;
      required_points: number;
      required_principal_passes: number;
    };
    subject_assessment: {
      essential_met: boolean;
      relevant_subjects: string[];
      desirable_subjects: string[];
    };
    nche_compliance: {
      meets_minimum_standards: boolean;
      meets_programme_requirements: boolean;
      meets_quota_requirements: boolean;
    };
    reasons_pass: string[];
    reasons_fail: string[];
    warnings: string[];
    recommendations: string[];
  };
  apply_url?: string;
  direct_application?: boolean;
  nche_compliant?: boolean;
}

// NCHE UACE Principal Subjects (actual UNEB subjects)
const NCHE_UACE_SUBJECTS = [
  // Sciences
  "Mathematics", "Physics", "Chemistry", "Biology", "Agriculture",
  "Technical Drawing", "Foods and Nutrition",
  // Arts & Humanities
  "History", "Geography", "Economics", "Entrepreneurship",
  "Art and Design", "Fine Art", "Music", "Drama", "Performing Arts",
  // Languages
  "Literature in English", "Luganda", "French", "German", "Arabic",
  "Latin", "Kiswahili",
  // Religious Studies
  "Christian Religious Education", "Islamic Religious Education",
  "Divinity",
  // Commercial
  "Commerce", "Principles of Accounts",
  // Technical
  "Metalwork", "Woodwork", "Building Construction",
  "Power and Energy", "Electronics"
];

// NCHE UACE Subsidiary Subjects
const NCHE_UACE_SUBSIDIARY_SUBJECTS = [
  "General Paper",
  "Subsidiary Mathematics",
  "Subsidiary ICT"
];

// NCHE UACE Grades (UNEB grading system)
const NCHE_UACE_GRADES = ["A", "B", "C", "D", "E", "O", "F"];

// NCHE UCE Divisions
const NCHE_UCE_DIVISIONS = [
  "Division 1", "Division 2", "Division 3", "Division 4", 
  "Division 5", "Division 6", "Division 7", "Division 8"
];

// NCHE Recognized Diplomas
const NCHE_DIPLOMAS = [
  "Diploma in Civil Engineering",
  "Diploma in Electrical Engineering", 
  "Diploma in Computer Science",
  "Diploma in Information Technology",
  "Diploma in Business Administration",
  "Diploma in Accounting",
  "Diploma in Nursing",
  "Diploma in Medical Laboratory",
  "Diploma in Pharmacy",
  "Diploma in Clinical Medicine",
  "Diploma in Education",
  "Diploma in Law"
];

export default function NCHERecommendationsPage() {
  const [step, setStep] = useState<"qualification" | "uace" | "uce" | "diploma" | "bachelors" | "results">("qualification");
  const [qualificationType, setQualificationType] = useState<"uce" | "uace" | "diploma" | "bachelors">("uce");
  const [uaceCurriculum, setUaceCurriculum] = useState<"old" | "new">("new");
  const [uceCurriculum, setUceCurriculum] = useState<"old" | "new">("new");
  const [uaceSubjects, setUaceSubjects] = useState<NCHESubject[]>([]);
  const [uceDivision, setUceDivision] = useState<string>("");
  const [uceCredits, setUceCredits] = useState<string[]>([]);
  const [diplomaType, setDiplomaType] = useState<string>("");
  const [diplomaClass, setDiplomaClass] = useState<string>("");
  const [workExperience, setWorkExperience] = useState<number>(0);
  const [bachelorGpa, setBachelorGpa] = useState<number>(3.0);
  const [recommendations, setRecommendations] = useState<NCHEProgramme[]>([]);
  const [loading, setLoading] = useState(false);

  const calculateNCHEPoints = () => {
    const gradePoints: Record<string, number> = { "A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0 };
    return uaceSubjects.reduce((total, subject) => {
      return total + (gradePoints[subject.grade] || 0);
    }, 0);
  };

  const getPrincipalPasses = () => {
    return uaceSubjects.filter(subject => 
      subject.grade && ["A", "B", "C", "D", "E"].includes(subject.grade)
    ).length;
  };

  const addUACESubject = (subjectName: string, grade: string) => {
    // Check if subject already exists
    const existingIndex = uaceSubjects.findIndex(s => s.name === subjectName);
    if (existingIndex >= 0) {
      const updatedSubjects = [...uaceSubjects];
      updatedSubjects[existingIndex] = { name: subjectName, grade, type: "relevant" };
      setUaceSubjects(updatedSubjects);
    } else {
      setUaceSubjects([...uaceSubjects, { name: subjectName, grade, type: "relevant" }]);
    }
  };

  const fetchNCHERecommendations = async () => {
    setLoading(true);
    try {
      const applicantData: any = {
        qualification_type: qualificationType
      };

      if (qualificationType === "uace") {
        applicantData.uace_subjects = uaceSubjects.map(s => s.name);
        applicantData.uace_grades = Object.fromEntries(uaceSubjects.map(s => [s.name, s.grade]));
        applicantData.principal_passes = getPrincipalPasses();
        applicantData.uce_division = uceDivision;
        applicantData.uce_credits = uceCredits;
      } else if (qualificationType === "diploma") {
        applicantData.diploma_type = diplomaType;
        applicantData.diploma_class = diplomaClass;
        applicantData.work_experience = workExperience;
      } else if (qualificationType === "bachelors") {
        applicantData.bachelor_gpa = bachelorGpa;
        applicantData.work_experience = workExperience;
      }

      const response = await fetch("/api/v1/nche/assess", {
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

  const getAdmissionCategoryColor = (category: string) => {
    if (category.includes("Strong")) return "bg-green-500";
    if (category.includes("Eligible")) return "bg-yellow-500";
    return "bg-red-500";
  };

  const renderQualificationStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Select Your Highest Qualification</h2>
        <p className="text-gray-600">NCHE Uganda compliant assessment</p>
      </div>

      <div className="space-y-4">
        {/* O-Level / UCE - Entry Level */}
        <div className="p-4 border rounded-lg cursor-pointer hover:bg-gray-50 bg-blue-50"
             onClick={() => { setQualificationType("uce"); setStep("uce"); }}>
          <div className="flex items-center space-x-3">
            <input
              type="radio"
              name="qualification"
              checked={qualificationType === "uce"}
              onChange={() => setQualificationType("uce")}
              className="w-4 h-4"
            />
            <div>
              <h3 className="font-semibold text-blue-800">UCE (O-Level)</h3>
              <p className="text-sm text-gray-600">Entry level: Certificate, HEC or Diploma</p>
            </div>
          </div>
        </div>

        {/* A-Level / UACE */}
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
              <h3 className="font-semibold">UACE (A-Level)</h3>
              <p className="text-sm text-gray-600">Direct university admission</p>
            </div>
          </div>
        </div>

        {/* Diploma / Certificate */}
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
              <p className="text-sm text-gray-600">NCHE recognized diploma</p>
            </div>
          </div>
        </div>

        <div className="p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
             onClick={() => { setQualificationType("bachelors"); setStep("bachelors"); }}>
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
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Enter UACE Results</h2>
        <p className="text-gray-600">NCHE Uganda standard assessment</p>
      </div>

      {/* Curriculum Selector */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <Label className="font-semibold text-blue-800">Curriculum Type</Label>
        <p className="text-sm text-gray-600 mb-2">Select the curriculum you studied under</p>
        <select
          value={uaceCurriculum}
          onChange={(e) => setUaceCurriculum(e.target.value as "old" | "new")}
          className="w-full p-2 border rounded bg-white"
        >
          <option value="new">New Curriculum (2024+)</option>
          <option value="old">Old Curriculum (Pre-2024)</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          {uaceCurriculum === "new" 
            ? "New Curriculum: 3 Principal Subjects max, Grades A-E (6 points max)" 
            : "Old Curriculum: 3 Principal + 2 Subsidiary max, Different grading system"}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold mb-3">Select Principal Subjects & Grades (Max 5)</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {NCHE_UACE_SUBJECTS.map((subject) => (
              <div key={subject} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={subject}
                  checked={uaceSubjects.some(s => s.name === subject)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      if (uaceSubjects.length < 5) {
                        addUACESubject(subject, "");
                      }
                    } else {
                      setUaceSubjects(uaceSubjects.filter(s => s.name !== subject));
                    }
                  }}
                  className="w-4 h-4"
                />
                <Label htmlFor={subject} className="text-sm">{subject}</Label>
                {uaceSubjects.some(s => s.name === subject) && (
                  <select
                    value={uaceSubjects.find(s => s.name === subject)?.grade || ""}
                    onChange={(e) => addUACESubject(subject, e.target.value)}
                    className="w-20 p-1 border rounded text-sm"
                  >
                    <option value="">Grade</option>
                    {NCHE_UACE_GRADES.map(grade => (
                      <option key={grade} value={grade}>{grade}</option>
                    ))}
                  </select>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-semibold mb-3">Selected Subjects Summary</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {uaceSubjects.map((subject, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">{subject.name}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-bold text-blue-600">{subject.grade}</span>
                  <Badge variant="outline" className="text-xs">
                    {subject.grade && ["A", "B", "C", "D", "E"].includes(subject.grade) ? "Principal" : "Subsidiary"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold mb-2">NCHE Points Calculation</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium">Total Points:</span>
            <div className="text-lg font-bold text-blue-600">{calculateNCHEPoints()}</div>
          </div>
          <div>
            <span className="font-medium">Principal Passes:</span>
            <div className="text-lg font-bold text-blue-600">{getPrincipalPasses()}</div>
          </div>
          <div>
            <span className="font-medium">Subjects:</span>
            <div className="text-lg font-bold text-blue-600">{uaceSubjects.length}</div>
          </div>
          <div>
            <span className="font-medium">NCHE Scale:</span>
            <div className="text-lg font-bold text-blue-600">A=6, B=5, C=4...</div>
          </div>
        </div>
      </div>

      <Button onClick={() => setStep("uce")} disabled={uaceSubjects.length === 0}>
        Continue to UCE Results
      </Button>
    </div>
  );

  const renderUCEStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">UCE Results</h2>
        <p className="text-gray-600">NCHE UCE Division assessment</p>
      </div>

      {/* Curriculum Selector */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <Label className="font-semibold text-blue-800">Curriculum Type</Label>
        <p className="text-sm text-gray-600 mb-2">Select the curriculum you studied under</p>
        <select
          value={uceCurriculum}
          onChange={(e) => setUceCurriculum(e.target.value as "old" | "new")}
          className="w-full p-2 border rounded bg-white"
        >
          <option value="new">New Curriculum (2024+)</option>
          <option value="old">Old Curriculum (Pre-2024)</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          {uceCurriculum === "new" 
            ? "New Curriculum: 9 Subjects, Pass 6 to qualify" 
            : "Old Curriculum: 8 Subjects, Division 1-4 to qualify"}
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <Label>UCE Division</Label>
          <select
            value={uceDivision}
            onChange={(e) => setUceDivision(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Select UCE Division</option>
            {NCHE_UCE_DIVISIONS.map(division => (
              <option key={division} value={division}>{division}</option>
            ))}
          </select>
        </div>

        <div>
          <Label>UCE Credits (Optional)</Label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {["Mathematics", "English", "Biology", "Chemistry", "Physics", "Geography", "History", "Economics"].map(subject => (
              <div key={subject} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={subject}
                  checked={uceCredits.includes(subject)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setUceCredits([...uceCredits, subject]);
                    } else {
                      setUceCredits(uceCredits.filter(c => c !== subject));
                    }
                  }}
                  className="w-4 h-4"
                />
                <Label htmlFor={subject} className="text-sm">{subject}</Label>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setStep("uace")}>
          Back
        </Button>
        <Button onClick={fetchNCHERecommendations} disabled={!uceDivision || loading}>
          {loading ? "Assessing..." : "Get NCHE Assessment"}
        </Button>
      </div>
    </div>
  );

  const renderDiplomaStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Diploma Details</h2>
        <p className="text-gray-600">NCHE recognized diploma assessment</p>
      </div>

      <div className="space-y-4">
        <div>
          <Label>Diploma Type</Label>
          <select
            value={diplomaType}
            onChange={(e) => setDiplomaType(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Select NCHE recognized diploma</option>
            {NCHE_DIPLOMAS.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div>
          <Label>Classification</Label>
          <select
            value={diplomaClass}
            onChange={(e) => setDiplomaClass(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Select classification</option>
            <option value="Distinction">Distinction</option>
            <option value="Credit">Credit</option>
            <option value="Pass">Pass</option>
          </select>
        </div>

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
        <Button onClick={fetchNCHERecommendations} disabled={!diplomaType || loading}>
          {loading ? "Assessing..." : "Get NCHE Assessment"}
        </Button>
      </div>
    </div>
  );

  const renderBachelorsStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Bachelor's Degree Details</h2>
        <p className="text-gray-600">For postgraduate programmes</p>
      </div>

      <div className="space-y-4">
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
        <Button onClick={fetchNCHERecommendations} disabled={loading}>
          {loading ? "Assessing..." : "Get NCHE Assessment"}
        </Button>
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">NCHE Assessment Results</h2>
        <p className="text-gray-600">Based on NCHE Uganda minimum standards</p>
      </div>

      {recommendations.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <XCircle className="w-16 h-16 mx-auto text-red-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">No NCHE-compliant programmes match</h3>
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
                    <div className="flex items-center space-x-2 mt-1">
                      <Shield className="w-4 h-4 text-green-600" />
                      <span className="text-sm text-green-600">NCHE {programme.nche_accreditation.status}</span>
                    </div>
                  </div>
                  <div className="text-right space-y-2">
                    <Badge className={getAdmissionCategoryColor(programme.nche_assessment?.admission_category || "")}>
                      {programme.nche_assessment?.admission_category}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {programme.nche_category.replace("_", " ").title()}
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      <Users className="w-4 h-4 mr-2" />
                      {programme.admission_quota.total} places available
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Target className="w-4 h-4 mr-2" />
                      Cut-off: {programme.admission_statistics_2024.cut_off_points} points
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      {programme.duration_years} years
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Your NCHE Points:</span>
                      <div className="text-lg font-bold text-blue-600">
                        {programme.nche_assessment?.points_calculation?.total_points || 0}
                      </div>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Principal Passes:</span>
                      <div>{programme.nche_assessment?.points_calculation?.principal_passes || 0}</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">NCHE Accreditation:</span>
                      <div className="text-gray-600">{programme.nche_accreditation.accreditation_number}</div>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Credits Required:</span>
                      <div className="text-gray-600">{programme.nche_accreditation.credits_required}</div>
                    </div>
                  </div>
                </div>

                {programme.nche_assessment && (
                  <div className="mb-4 space-y-2">
                    {programme.nche_assessment.reasons_pass.length > 0 && (
                      <div className="p-3 bg-green-50 rounded-lg">
                        <p className="text-sm font-medium text-green-900 mb-1">NCHE Compliance:</p>
                        <ul className="text-sm text-green-800 space-y-1">
                          {programme.nche_assessment.reasons_pass.map((reason, index) => (
                            <li key={index} className="flex items-center">
                              <CheckCircle className="w-3 h-3 mr-2 text-green-600" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {programme.nche_assessment.reasons_fail.length > 0 && (
                      <div className="p-3 bg-red-50 rounded-lg">
                        <p className="text-sm font-medium text-red-900 mb-1">NCHE Issues:</p>
                        <ul className="text-sm text-red-800 space-y-1">
                          {programme.nche_assessment.reasons_fail.map((reason, index) => (
                            <li key={index} className="flex items-center">
                              <XCircle className="w-3 h-3 mr-2 text-red-600" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {programme.nche_assessment.warnings.length > 0 && (
                      <div className="p-3 bg-yellow-50 rounded-lg">
                        <p className="text-sm font-medium text-yellow-900 mb-1">NCHE Considerations:</p>
                        <ul className="text-sm text-yellow-800 space-y-1">
                          {programme.nche_assessment.warnings.map((reason, index) => (
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
                    <div className="flex items-center space-x-2">
                      <Award className="w-4 h-4" />
                      <span>Professional Registration: {programme.professional_registration.join(", ")}</span>
                    </div>
                  </div>
                  <Button asChild disabled={!programme.nche_assessment?.eligible}>
                    <a href={programme.apply_url}>
                      {programme.nche_assessment?.eligible ? "Apply Now" : "Not Eligible"}
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
          <div className="flex items-center justify-center space-x-2 mb-2">
            <Shield className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">
              NCHE Uganda Admission Assessment
            </h1>
          </div>
          <p className="text-gray-600">
            Official NCHE Uganda compliant programme recommendation and direct application system
          </p>
        </div>

        {step === "qualification" && renderQualificationStep()}
        {step === "uace" && renderUACEStep()}
        {step === "uce" && renderUCEStep()}
        {step === "diploma" && renderDiplomaStep()}
        {step === "bachelors" && renderBachelorsStep()}
        {step === "results" && renderResults()}
      </div>
    </div>
  );
}
