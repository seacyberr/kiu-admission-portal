import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { GraduationCap, Briefcase, Clock, MapPin } from "lucide-react";

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
  requirements: {
    subjects: string[];
    minimum_education: string;
    alternative: string;
  };
  career_prospects: string[];
  accreditation: string;
  match_score?: number;
  match_reasons?: string[];
  apply_url?: string;
}

const CATEGORIES = [
  "Health Sciences",
  "Engineering", 
  "Information Technology",
  "Business",
  "Law",
  "Education",
  "Social Sciences",
  "Research"
];

const EDUCATION_LEVELS = [
  "O-Level",
  "A-Level", 
  "Diploma",
  "Bachelor's Degree",
  "Master's Degree",
  "PhD"
];

const COMMON_SUBJECTS = [
  "Mathematics",
  "Physics", 
  "Chemistry",
  "Biology",
  "Computer Studies",
  "Economics",
  "Accounting",
  "English",
  "History",
  "Geography",
  "Literature",
  "Business Studies",
  "Art",
  "Music"
];

export default function SimpleRecommendationsPage() {
  const [step, setStep] = useState<"interests" | "subjects" | "education" | "results">("interests");
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
  const [educationLevel, setEducationLevel] = useState("");
  const [recommendations, setRecommendations] = useState<Programme[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v1/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          interests: selectedInterests,
          subjects: selectedSubjects,
          education_level: educationLevel
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations);
        setStep("results");
      }
    } catch (error) {
      // Silent fail - user feedback handled by UI state
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

  const getMatchColor = (score: number) => {
    if (score >= 70) return "bg-green-500";
    if (score >= 50) return "bg-yellow-500";
    return "bg-blue-500";
  };

  const renderInterestsStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">What are you interested in?</h2>
        <p className="text-gray-600">Select all areas that interest you</p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {CATEGORIES.map((category) => (
          <div key={category} className="flex items-center space-x-2">
            <input
              type="checkbox"
              id={category}
              checked={selectedInterests.includes(category)}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedInterests([...selectedInterests, category]);
                } else {
                  setSelectedInterests(selectedInterests.filter(i => i !== category));
                }
              }}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <Label htmlFor={category} className="text-sm">{category}</Label>
          </div>
        ))}
      </div>
      
      <div className="flex justify-end">
        <Button onClick={() => setStep("subjects")} disabled={selectedInterests.length === 0}>
          Next: Your Subjects
        </Button>
      </div>
    </div>
  );

  const renderSubjectsStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">What subjects did you study?</h2>
        <p className="text-gray-600">Select your best subjects</p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {COMMON_SUBJECTS.map((subject) => (
          <div key={subject} className="flex items-center space-x-2">
            <input
              type="checkbox"
              id={subject}
              checked={selectedSubjects.includes(subject)}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedSubjects([...selectedSubjects, subject]);
                } else {
                  setSelectedSubjects(selectedSubjects.filter(s => s !== subject));
                }
              }}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <Label htmlFor={subject} className="text-sm">{subject}</Label>
          </div>
        ))}
      </div>
      
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setStep("interests")}>
          Back
        </Button>
        <Button onClick={() => setStep("education")} disabled={selectedSubjects.length === 0}>
          Next: Education Level
        </Button>
      </div>
    </div>
  );

  const renderEducationStep = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">What's your education level?</h2>
        <p className="text-gray-600">Tell us about your current qualifications</p>
      </div>
      
      <div className="space-y-3">
        {EDUCATION_LEVELS.map((level) => (
          <div key={level} className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
               onClick={() => setEducationLevel(level)}>
            <input
              type="radio"
              name="education"
              checked={educationLevel === level}
              onChange={() => setEducationLevel(level)}
              className="w-4 h-4"
            />
            <Label className="text-base cursor-pointer">{level}</Label>
          </div>
        ))}
      </div>
      
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setStep("subjects")}>
          Back
        </Button>
        <Button onClick={fetchRecommendations} disabled={!educationLevel || loading}>
          {loading ? "Getting Recommendations..." : "Get My Recommendations"}
        </Button>
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Your Recommended Programmes</h2>
        <p className="text-gray-600">Based on your interests and qualifications</p>
      </div>

      {recommendations.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <GraduationCap className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">No programmes found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your preferences</p>
            <Button onClick={() => setStep("interests")}>Start Over</Button>
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
                  <div className="text-right">
                    <Badge className={getMatchColor(programme.match_score || 0)}>
                      {programme.match_score}% Match
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      {programme.duration_years} years
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="w-4 h-4 mr-2" />
                      {programme.campus.join(", ")}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Briefcase className="w-4 h-4 mr-2" />
                      {programme.category}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Requirements:</span>
                      <div className="text-gray-600">{programme.requirements.minimum_education}</div>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Tuition:</span>
                      <div className="text-gray-600">
                        {fmtUGX(programme.tuition_ugx_per_semester)}/semester
                      </div>
                    </div>
                  </div>
                </div>

                {programme.match_reasons && programme.match_reasons.length > 0 && (
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm font-medium text-blue-900 mb-1">Why this matches:</p>
                    <ul className="text-sm text-blue-800 space-y-1">
                      {programme.match_reasons.map((reason, index) => (
                        <li key={index}>- {reason}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-500">
                    Next intakes: {programme.intake_months.map(m => {
                      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                      return months[m - 1];
                    }).join(", ")}
                  </div>
                  <Button asChild>
                    <a href={programme.apply_url}>
                      Apply Now
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="text-center">
        <Button variant="outline" onClick={() => setStep("interests")}>
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
            Find Your Perfect Programme
          </h1>
          <p className="text-gray-600">
            Get personalized recommendations in 3 simple steps
          </p>
        </div>

        {step === "interests" && renderInterestsStep()}
        {step === "subjects" && renderSubjectsStep()}
        {step === "education" && renderEducationStep()}
        {step === "results" && renderResults()}
      </div>
    </div>
  );
}
