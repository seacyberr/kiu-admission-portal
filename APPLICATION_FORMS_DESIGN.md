# Uganda Education System - Application Form Design

## Overview
Multi-step application forms designed for Uganda's dual curriculum (Old: Pre-2024, New: 2024+) and all education pathways.

---

## 1. EDUCATION LEVEL SELECTION (Step 1)

### Select Highest Qualification
```typescript
const HIGHEST_EDUCATION_LEVELS = [
  { value: "olevel", label: "O-Level (UCE) Only", appliesFor: ["national_certificate", "certificate"] },
  { value: "national_certificate", label: "National Certificate (TVET)", appliesFor: ["diploma", "hec", "national_certificate"] },
  { value: "alevel", label: "A-Level (UACE)", appliesFor: ["hec", "diploma", "bachelor"] },
  { value: "hec", label: "Higher Education Certificate (HEC)", appliesFor: ["bachelor"] },
  { value: "diploma", label: "Diploma", appliesFor: ["bachelor", "diploma"] },
  { value: "bachelor", label: "Bachelor's Degree", appliesFor: ["masters", "bachelor_2nd"] },
  { value: "masters", label: "Masters Degree", appliesFor: ["phd", "masters_2nd"] },
  { value: "phd", label: "PhD (Doctorate)", appliesFor: ["postdoc"] }
];
```

**UI Component:**
```tsx
<Card className="p-6">
  <h2 className="text-xl font-bold mb-4">What is your highest level of education?</h2>
  <RadioGroup value={highestEducation} onValueChange={setHighestEducation}>
    {HIGHEST_EDUCATION_LEVELS.map((level) => (
      <div key={level.value} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50">
        <RadioGroupItem value={level.value} id={level.value} />
        <Label htmlFor={level.value} className="flex-1 cursor-pointer">
          <div className="font-medium">{level.label}</div>
          <div className="text-sm text-gray-500">
            Can apply for: {level.appliesFor.join(", ")}
          </div>
        </Label>
      </div>
    ))}
  </RadioGroup>
</Card>
```

---

## 2. CURRICULUM SELECTION (Step 2)

### Uganda Dual Curriculum System (2024-2025 Transition)

```typescript
const CURRICULUM_OPTIONS = {
  olevel: [
    { value: "old", label: "Old Curriculum (Pre-2024)", grades: ["D1", "D2", "C3", "C4", "C5", "C6", "P7", "P8", "F9"] },
    { value: "new", label: "New Curriculum (2024+)", grades: ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "F"] }
  ],
  alevel: [
    { value: "old", label: "Standard Grading (A, B, C, D, E, O, F)" }
    // A-Level unchanged across curriculums
  ]
};
```

**Grade Conversion Reference:**
| New Curriculum | Old Curriculum | Points |
|----------------|----------------|--------|
| D1 | D1/D2 | 1 |
| D2 | D1/D2 | 2 |
| D3 | C3/C4 | 3 |
| D4 | C3/C4 | 4 |
| D5 | C5/C6 | 5 |
| D6 | C5/C6 | 6 |
| D7 | P7/P8 | 7 |
| D8 | P7/P8 | 8 |
| F | F9 | 9 |

**UI Component:**
```tsx
<div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-6">
  <div className="flex items-start space-x-3">
    <Info className="w-5 h-5 text-yellow-600 mt-0.5" />
    <div>
      <h3 className="font-medium text-yellow-800">Uganda Curriculum Transition</h3>
      <p className="text-sm text-yellow-700 mt-1">
        Did you sit for UCE in 2024 or later? Select "New Curriculum". 
        Before 2024? Select "Old Curriculum". The system will convert grades automatically.
      </p>
    </div>
  </div>
</div>

<Select value={curriculumVersion} onValueChange={setCurriculumVersion}>
  <SelectTrigger>
    <SelectValue placeholder="Select your UCE curriculum" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="old">Old Curriculum (D1-D2-C3...P8-F9) - Pre-2024</SelectItem>
    <SelectItem value="new">New Curriculum (D1-D2-D3...D8-F) - 2024+</SelectItem>
  </SelectContent>
</Select>
```

---

## 3. O-LEVEL (UCE) FORM SECTION

### Index Number Format
```typescript
// UCE Index Number: XXXXXXXXX/YYYY
// Example: U0145/023 or 2023/U/0145/023
const UCE_INDEX_REGEX = /^[Uu]?\d{4,6}\/\d{2,4}$/;

<Input 
  placeholder="U0145/023 or 2023/U/0145/023"
  pattern="^[Uu]?\d{4,6}\/\d{2,4}$"
/>
```

### Subject Entry (Dynamic based on curriculum)

```typescript
interface OLevelGrade {
  subject: string;
  grade: string;  // D1, D2, C3... for old OR D1, D2, D3... for new
  curriculum: "old" | "new";
}

const OLEVEL_SUBJECTS_UGANDA = [
  "English Language",
  "Mathematics",
  "Physics",
  "Chemistry",
  "Biology",
  "Geography",
  "History",
  "Christian Religious Education (CRE)",
  "Islamic Religious Education (IRE)",
  "Entrepreneurship Education",
  "Computer Studies",
  "Agriculture",
  "Commerce",
  "Fine Art",
  "Literature in English",
  "Kiswahili",
  "French",
  "Technical Drawing",
  "Home Economics",
  "Music",
  "Physical Education"
];
```

**UI Component:**
```tsx
<div className="space-y-4">
  <div className="flex justify-between items-center">
    <h3 className="font-semibold">UACE Subjects & Grades</h3>
    <Badge variant="outline">Curriculum: {curriculumVersion === "old" ? "Old (D1-C6-P8)" : "New (D1-D8)"}</Badge>
  </div>
  
  {oLevelGrades.map((entry, index) => (
    <div key={index} className="grid grid-cols-12 gap-2 items-center">
      <div className="col-span-6">
        <Select value={entry.subject} onValueChange={(v) => updateSubject(index, v)}>
          <SelectTrigger>
            <SelectValue placeholder="Select subject" />
          </SelectTrigger>
          <SelectContent>
            {OLEVEL_SUBJECTS_UGANDA.map((subject) => (
              <SelectItem key={subject} value={subject}>{subject}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="col-span-4">
        <Select value={entry.grade} onValueChange={(v) => updateGrade(index, v)}>
          <SelectTrigger>
            <SelectValue placeholder="Grade" />
          </SelectTrigger>
          <SelectContent>
            {(curriculumVersion === "old" ? OLEVEL_GRADES_OLD : OLEVEL_GRADES_NEW).map((g) => (
              <SelectItem key={g.value} value={g.value}>
                {g.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="col-span-2">
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => removeSubject(index)}
          disabled={oLevelGrades.length <= 1}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  ))}
  
  <Button 
    variant="outline" 
    onClick={addSubject}
    disabled={oLevelGrades.length >= 10}
  >
    <Plus className="w-4 h-4 mr-2" />
    Add Subject
  </Button>
</div>

{/* O-Level Certificate Upload */}
<div className="mt-6">
  <Label className="font-semibold">Upload UCE Result Slip</Label>
  <p className="text-sm text-gray-500 mb-2">UNEB result slip or provisional result</p>
  <FileUpload 
    accept=".pdf,.jpg,.jpeg,.png"
    maxSize={5 * 1024 * 1024}
    onUpload={(file) => setOlevelCertificate(file)}
  />
</div>
```

---

## 4. A-LEVEL (UACE) FORM SECTION

### Index Number Format
```typescript
// UACE Index Number: XXXXXXXXX/YYYY
const UACE_INDEX_REGEX = /^[Uu]?\d{4,6}\/\d{2,4}$/;
```

### Principal & Subsidiary Subjects

```typescript
const ALEVEL_PRINCIPAL_SUBJECTS = [
  "Mathematics",
  "Physics",
  "Chemistry",
  "Biology",
  "Geography",
  "History",
  "Economics",
  "Literature in English",
  "Divinity",
  "Entrepreneurship",
  "Art & Design",
  "Technical Drawing",
  "Computer Studies",
  "Agriculture",
  "Food & Nutrition"
];

const ALEVEL_SUBSIDIARY_SUBJECTS = [
  "General Paper",
  "Subsidiary Mathematics",
  "Subsidiary ICT"
];

const ALEVEL_PRINCIPAL_GRADES = [
  { label: "A - 6 points", value: "A", points: 6 },
  { label: "B - 5 points", value: "B", points: 5 },
  { label: "C - 4 points", value: "C", points: 4 },
  { label: "D - 3 points", value: "D", points: 3 },
  { label: "E - 2 points", value: "E", points: 2 },
  { label: "O - 1 point (Subsidiary)", value: "O", points: 1 },
  { label: "F - Fail", value: "F", points: 0 }
];

interface ALevelGrade {
  subject: string;
  grade: string;
  subjectType: "principal" | "subsidiary";
  points: number;
}
```

**UI Component - Principal Subjects:**
```tsx
<Card className="p-4">
  <h3 className="font-semibold mb-4">Principal Subjects (3 max)</h3>
  <p className="text-sm text-gray-500 mb-4">
    Minimum 2 principal passes required for degree programs. 
    1 principal + 2 subsidiaries for diploma.
  </p>
  
  {principalSubjects.map((entry, index) => (
    <div key={index} className="grid grid-cols-12 gap-2 mb-3 items-center">
      <div className="col-span-1">
        <Badge variant="secondary">P{index + 1}</Badge>
      </div>
      <div className="col-span-5">
        <Select value={entry.subject} onValueChange={(v) => updatePrincipalSubject(index, v)}>
          <SelectTrigger>
            <SelectValue placeholder="Subject" />
          </SelectTrigger>
          <SelectContent>
            {ALEVEL_PRINCIPAL_SUBJECTS.map((s) => (
              <SelectItem key={s} value={s}>{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="col-span-4">
        <Select value={entry.grade} onValueChange={(v) => updatePrincipalGrade(index, v)}>
          <SelectTrigger>
            <SelectValue placeholder="Grade" />
          </SelectTrigger>
          <SelectContent>
            {ALEVEL_PRINCIPAL_GRADES.map((g) => (
              <SelectItem key={g.value} value={g.value}>{g.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="col-span-2 text-right">
        <span className="font-bold text-blue-600">{entry.points} pts</span>
      </div>
    </div>
  ))}
  
  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
    <div className="flex justify-between">
      <span className="text-sm">Total Principal Passes:</span>
      <Badge>{principalPasses} / 3</Badge>
    </div>
    <div className="flex justify-between mt-2">
      <span className="text-sm">Total Points:</span>
      <Badge variant="outline">{totalPoints} points</Badge>
    </div>
    <div className="flex justify-between mt-2">
      <span className="text-sm">Eligibility:</span>
      <Badge className={isEligibleForBachelor ? "bg-green-500" : "bg-yellow-500"}>
        {isEligibleForBachelor ? "Bachelor Eligible" : "HEC/Diploma Pathway"}
      </Badge>
    </div>
  </div>
</Card>
```

**UI Component - Subsidiary Subjects:**
```tsx
<Card className="p-4 mt-4">
  <h3 className="font-semibold mb-4">Subsidiary Subjects</h3>
  
  <div className="grid grid-cols-12 gap-2 mb-3 items-center">
    <div className="col-span-1">
      <Badge variant="secondary">S1</Badge>
    </div>
    <div className="col-span-5">
      <Select 
        value={generalPaper.subject} 
        onValueChange={(v) => setGeneralPaper({...generalPaper, subject: v})}
      >
        <SelectTrigger>
          <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="General Paper">General Paper (Required for most programs)</SelectItem>
          </SelectContent>
        </Select>
    </div>
    <div className="col-span-4">
      <Select 
        value={generalPaper.grade} 
        onValueChange={(v) => setGeneralPaper({...generalPaper, grade: v})}
      >
        <SelectTrigger>
          <SelectValue placeholder="Grade" />
          </SelectTrigger>
          <SelectContent>
            {ALEVEL_PRINCIPAL_GRADES.map((g) => (
              <SelectItem key={g.value} value={g.value}>{g.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
    </div>
    <div className="col-span-2 text-right">
      <span className="text-sm text-gray-500">1 pt if pass</span>
    </div>
  </div>
  
  {subsidiarySubjects.map((entry, index) => (
    <div key={index} className="grid grid-cols-12 gap-2 mb-3 items-center">
      <div className="col-span-1">
        <Badge variant="secondary">S{index + 2}</Badge>
      </div>
      <div className="col-span-5">
        <Select value={entry.subject} onValueChange={(v) => updateSubsidiarySubject(index, v)}>
          <SelectTrigger>
            <SelectValue placeholder="Subject" />
            </SelectTrigger>
            <SelectContent>
              {ALEVEL_SUBSIDIARY_SUBJECTS.slice(1).map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
      </div>
      <div className="col-span-4">
        <Select value={entry.grade} onValueChange={(v) => updateSubsidiaryGrade(index, v)}>
          <SelectTrigger>
            <SelectValue placeholder="Grade" />
            </SelectTrigger>
            <SelectContent>
              {ALEVEL_PRINCIPAL_GRADES.map((g) => (
                <SelectItem key={g.value} value={g.value}>{g.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
      </div>
    </div>
  ))}
</Card>
```

---

## 5. HEC (HIGHER EDUCATION CERTIFICATE) FORM SECTION

```typescript
interface HECInfo {
  hec_track: "arts" | "biological" | "physical";
  institution: string;
  completion_year: number;
  gpa?: number;
  certificate_number?: string;
}

const HEC_TRACKS = [
  {
    value: "arts",
    label: "HEC Arts (Humanities)",
    description: "For Law, Business, Social Sciences, Education",
    subjects: ["History", "Geography", "Economics", "Divinity", "Literature"]
  },
  {
    value: "biological",
    label: "HEC Biological Sciences",
    description: "For Medicine, Nursing, Pharmacy, Agriculture",
    subjects: ["Biology", "Chemistry"]
  },
  {
    value: "physical",
    label: "HEC Physical Sciences",
    description: "For Engineering, Computer Science, Mathematics",
    subjects: ["Mathematics", "Physics"]
  }
];
```

**UI Component:**
```tsx
<Card className="p-6">
  <h2 className="text-xl font-bold mb-4">Higher Education Certificate (HEC) Details</h2>
  
  <div className="space-y-4">
    <div>
      <Label>HEC Track</Label>
      <RadioGroup value={hecTrack} onValueChange={setHecTrack} className="grid grid-cols-1 gap-4 mt-2">
        {HEC_TRACKS.map((track) => (
          <div key={track.value} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-gray-50">
            <RadioGroupItem value={track.value} id={track.value} />
            <Label htmlFor={track.value} className="flex-1 cursor-pointer">
              <div className="font-semibold">{track.label}</div>
              <div className="text-sm text-gray-500 mt-1">{track.description}</div>
              <div className="text-xs text-blue-600 mt-2">
                Key subjects: {track.subjects.join(", ")}
              </div>
            </Label>
          </div>
        ))}
      </RadioGroup>
    </div>
    
    <div className="grid grid-cols-2 gap-4">
      <div>
        <Label>Institution Attended</Label>
        <Input placeholder="e.g., KIU, Muni University, etc." />
      </div>
      <div>
        <Label>Year of Completion</Label>
        <Input type="number" min="2020" max="2026" />
      </div>
    </div>
    
    <div className="grid grid-cols-2 gap-4">
      <div>
        <Label>GPA (if applicable)</Label>
        <Input type="number" step="0.01" min="0" max="5" placeholder="e.g., 3.5" />
      </div>
      <div>
        <Label>Certificate Number</Label>
        <Input placeholder="HEC Certificate Number" />
      </div>
    </div>
    
    <div>
      <Label>Upload HEC Certificate</Label>
      <p className="text-sm text-gray-500 mb-2">Official HEC completion certificate</p>
      <FileUpload accept=".pdf,.jpg,.jpeg,.png" maxSize={5 * 1024 * 1024} />
    </div>
  </div>
</Card>

{/* HEC Progression Info */}
<Alert className="mt-4">
  <Info className="w-4 h-4" />
  <AlertTitle>HEC Progression</AlertTitle>
  <AlertDescription>
    With HEC {hecTrack} completion, you can progress directly to Bachelor programs in:
    {hecTrack === "arts" && " Law, Business, Social Sciences, Education"}
    {hecTrack === "biological" && " Medicine, Nursing, Pharmacy, Agriculture"}
    {hecTrack === "physical" && " Engineering, Computer Science, Mathematics"}
  </AlertDescription>
</Alert>
```

---

## 6. DIPLOMA FORM SECTION

```typescript
interface DiplomaInfo {
  diploma_program: string;
  institution: string;
  completion_year: number;
  diploma_class: "distinction" | "credit" | "pass";
  is_relevant_to_degree: boolean;
}

const DIPLOMA_CLASSES = [
  { value: "distinction", label: "Distinction (70-100%)", eligibleForDegree: true, creditTransfer: true },
  { value: "credit", label: "Credit (60-69%)", eligibleForDegree: true, creditTransfer: true },
  { value: "pass", label: "Pass (50-59%)", eligibleForDegree: true, creditTransfer: false, note: "May require additional requirements" }
];
```

**UI Component:**
```tsx
<Card className="p-6">
  <h2 className="text-xl font-bold mb-4">Diploma Information</h2>
  
  <div className="space-y-4">
    <div>
      <Label>Diploma Program</Label>
      <Input placeholder="e.g., Diploma in Nursing, Diploma in Business Administration" />
    </div>
    
    <div className="grid grid-cols-2 gap-4">
      <div>
        <Label>Institution</Label>
        <Input placeholder="e.g., KIU, Mulago School of Nursing, etc." />
      </div>
      <div>
        <Label>Year of Completion</Label>
        <Input type="number" min="2015" max="2026" />
      </div>
    </div>
    
    <div>
      <Label>Class/Division Achieved</Label>
      <Select value={diplomaClass} onValueChange={setDiplomaClass}>
        <SelectTrigger>
          <SelectValue placeholder="Select class/division" />
        </SelectTrigger>
        <SelectContent>
          {DIPLOMA_CLASSES.map((cls) => (
            <SelectItem key={cls.value} value={cls.value}>
              <div className="flex flex-col">
                <span>{cls.label}</span>
                <span className="text-xs text-gray-500">
                  {cls.eligibleForDegree ? "Eligible for degree entry" : "Not eligible"}
                  {cls.creditTransfer && " + Credit transfer"}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
    
    <div>
      <Label>Is your diploma relevant to the degree program you're applying for?</Label>
      <RadioGroup value={isRelevant} onValueChange={setIsRelevant} className="flex gap-4 mt-2">
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="yes" id="yes" />
          <Label htmlFor="yes">Yes, directly related</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="no" id="no" />
          <Label htmlFor="no">No, different field</Label>
        </div>
      </RadioGroup>
    </div>
    
    <div>
      <Label>Upload Diploma Certificate + Transcript</Label>
      <p className="text-sm text-gray-500 mb-2">Both certificate and official transcript required</p>
      <div className="grid grid-cols-2 gap-4">
        <FileUpload label="Diploma Certificate" accept=".pdf,.jpg,.jpeg,.png" />
        <FileUpload label="Official Transcript" accept=".pdf,.jpg,.jpeg,.png" />
      </div>
    </div>
  </div>
</Card>

{/* Diploma Progression Info */}
<Alert className="mt-4" variant={diplomaClass === "distinction" || diplomaClass === "credit" ? "default" : "warning"}>
  <Info className="w-4 h-4" />
  <AlertTitle>Degree Entry Eligibility</AlertTitle>
  <AlertDescription>
    {diplomaClass === "distinction" && "Distinction: Direct entry to Year 2 or 3 of degree with full credit transfer"}
    {diplomaClass === "credit" && "Credit: Direct entry to degree program, credit transfer possible"}
    {diplomaClass === "pass" && "Pass: May enter degree program but credit transfer not guaranteed. Additional requirements may apply."}
  </AlertDescription>
</Alert>
```

---

## 7. DEGREE/MASTERS/PHD FORM SECTION

```typescript
interface PreviousDegreeInfo {
  degree_type: "bachelor" | "masters";
  program: string;
  institution: string;
  completion_year: number;
  degree_class: "first" | "second_upper" | "second_lower" | "pass";
  gpa?: number;
}

const DEGREE_CLASSES = [
  { value: "first", label: "First Class Honours", eligibleForMasters: true },
  { value: "second_upper", label: "Second Class Upper Division (2:1)", eligibleForMasters: true },
  { value: "second_lower", label: "Second Class Lower Division (2:2)", eligibleForMasters: true },
  { value: "pass", label: "Pass", eligibleForMasters: false, note: "May not meet postgraduate requirements" }
];
```

**UI Component:**
```tsx
<Card className="p-6">
  <h2 className="text-xl font-bold mb-4">
    {applyingForLevel === "masters" ? "Bachelor's Degree Information" : "Masters Degree Information"}
  </h2>
  
  <div className="space-y-4">
    <div>
      <Label>Program Name</Label>
      <Input placeholder={applyingForLevel === "masters" ? "e.g., Bachelor of Medicine and Bachelor of Surgery" : "e.g., Master of Business Administration"} />
    </div>
    
    <div className="grid grid-cols-2 gap-4">
      <div>
        <Label>University/Institution</Label>
        <Input placeholder="e.g., KIU, Makerere University, etc." />
      </div>
      <div>
        <Label>Year of Graduation</Label>
        <Input type="number" min="2000" max="2026" />
      </div>
    </div>
    
    <div className="grid grid-cols-2 gap-4">
      <div>
        <Label>Class/Division/GPA</Label>
        <Select value={degreeClass} onValueChange={setDegreeClass}>
          <SelectTrigger>
            <SelectValue placeholder="Select class" />
          </SelectTrigger>
          <SelectContent>
            {DEGREE_CLASSES.map((cls) => (
              <SelectItem key={cls.value} value={cls.value}>
                <div className="flex flex-col">
                  <span>{cls.label}</span>
                  {applyingForLevel === "masters" && (
                    <span className="text-xs text-gray-500">
                      {cls.eligibleForMasters ? "Eligible for Masters" : "May not meet requirements"}
                    </span>
                  )}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label>GPA (out of 5.0 or 4.0)</Label>
        <Input type="number" step="0.01" min="0" max="5" placeholder="e.g., 3.5" />
      </div>
    </div>
    
    <div>
      <Label>Upload Degree Certificate + Transcript</Label>
      <p className="text-sm text-gray-500 mb-2">Both certificate and official transcript required</p>
      <div className="grid grid-cols-2 gap-4">
        <FileUpload label="Degree Certificate" accept=".pdf,.jpg,.jpeg,.png" />
        <FileUpload label="Official Transcript" accept=".pdf,.jpg,.jpeg,.png" />
      </div>
    </div>
    
    {applyingForLevel === "phd" && (
      <div>
        <Label>Research Proposal</Label>
        <p className="text-sm text-gray-500 mb-2">Brief description of proposed research area</p>
        <Textarea 
          placeholder="Describe your proposed research topic, objectives, and methodology..."
          rows={5}
        />
      </div>
    )}
  </div>
</Card>
```

---

## 8. NATIONAL CERTIFICATE (TVET) FORM SECTION

```typescript
interface NationalCertificateInfo {
  certificate_type: string;
  institution: string;
  completion_year: number;
  awarding_body: "DIT" | "UBTEB" | "other";
  certificate_number?: string;
}

const NC_TYPES = [
  { value: "business", label: "National Certificate in Business Administration" },
  { value: "it", label: "National Certificate in Information Technology" },
  { value: "agriculture", label: "National Certificate in Agriculture" },
  { value: "education", label: "National Certificate in Primary Education" },
  { value: "engineering", label: "National Certificate in Engineering" },
  { value: "health", label: "National Certificate in Health Sciences" }
];

const AWARDING_BODIES = [
  { value: "DIT", label: "DIT - Directorate of Industrial Training" },
  { value: "UBTEB", label: "UBTEB - Uganda Business and Technical Examinations Board" },
  { value: "other", label: "Other recognized body" }
];
```

**UI Component:**
```tsx
<Card className="p-6">
  <h2 className="text-xl font-bold mb-4">National Certificate (TVET) Information</h2>
  
  <div className="space-y-4">
    <div>
      <Label>Certificate Type</Label>
      <Select value={ncType} onValueChange={setNcType}>
        <SelectTrigger>
          <SelectValue placeholder="Select certificate type" />
        </SelectTrigger>
        <SelectContent>
          {NC_TYPES.map((type) => (
            <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
    
    <div>
      <Label>Awarding Body</Label>
      <Select value={awardingBody} onValueChange={setAwardingBody}>
        <SelectTrigger>
          <SelectValue placeholder="Select awarding body" />
        </SelectTrigger>
        <SelectContent>
          {AWARDING_BODIES.map((body) => (
            <SelectItem key={body.value} value={body.value}>{body.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
    
    <div className="grid grid-cols-2 gap-4">
      <div>
        <Label>Institution</Label>
        <Input placeholder="e.g., KIU, YMCA, etc." />
      </div>
      <div>
        <Label>Year of Completion</Label>
        <Input type="number" min="2015" max="2026" />
      </div>
    </div>
    
    <div>
      <Label>Certificate Number</Label>
      <Input placeholder="TVET Certificate Number" />
    </div>
    
    <div>
      <Label>Upload National Certificate</Label>
      <FileUpload accept=".pdf,.jpg,.jpeg,.png" maxSize={5 * 1024 * 1024} />
    </div>
  </div>
</Card>

<Alert className="mt-4">
  <Info className="w-4 h-4" />
  <AlertTitle>Progression Options</AlertTitle>
  <AlertDescription>
    With a National Certificate, you can apply for:
    <ul className="list-disc list-inside mt-2">
      <li>Diploma programs in related field</li>
      <li>HEC (if you meet A-Level requirements)</li>
      <li>Higher National Certificate programs</li>
    </ul>
  </AlertDescription>
</Alert>
```

---

## 9. DOCUMENT UPLOAD SUMMARY (Final Step)

**Required Documents by Entry Level:**

| Entry Level | Required Documents |
|-------------|-------------------|
| **National Certificate** | O-Level Result Slip, Birth Certificate, Passport Photo |
| **HEC** | A-Level Result Slip, O-Level Result Slip, Passport Photo |
| **Diploma** | A-Level Result Slip, O-Level Result Slip, Passport Photo |
| **Bachelor (Direct)** | A-Level Result Slip, O-Level Result Slip, Birth Certificate, Medical Certificate, Passport Photo |
| **Bachelor (Diploma Entry)** | Diploma Certificate + Transcript, A-Level/O-Level Results |
| **Bachelor (HEC Entry)** | HEC Certificate, A-Level/O-Level Results |
| **Masters** | Degree Certificate + Transcript, CV, Recommendation Letters, Research Proposal |
| **PhD** | Masters Certificate + Transcript, Research Proposal, Publication List |

**UI Component:**
```tsx
<Card className="p-6">
  <h2 className="text-xl font-bold mb-4">Document Upload Checklist</h2>
  
  <div className="space-y-4">
    {/* Dynamically show required docs based on entry level */}
    
    {entryLevel === "bachelor" && qualificationPath === "direct" && (
      <>
        <DocumentUploadItem 
          label="UACE Result Slip (A-Level)" 
          required={true}
          description="UNEB official result slip"
        />
        <DocumentUploadItem 
          label="UCE Result Slip (O-Level)" 
          required={true}
          description="UNEB official result slip"
        />
        <DocumentUploadItem 
          label="Birth Certificate" 
          required={true}
          description="National ID or passport also acceptable"
        />
        <DocumentUploadItem 
          label="Medical Certificate" 
          required={true}
          description="From government hospital or recognized clinic"
        />
        <DocumentUploadItem 
          label="Passport Photos (2)" 
          required={true}
          description="Recent, colored, white background"
        />
      </>
    )}
    
    {entryLevel === "bachelor" && qualificationPath === "diploma" && (
      <>
        <DocumentUploadItem 
          label="Diploma Certificate" 
          required={true}
        />
        <DocumentUploadItem 
          label="Diploma Transcript" 
          required={true}
        />
        <DocumentUploadItem 
          label="UACE/UCE Result Slips" 
          required={true}
        />
        <DocumentUploadItem 
          label="Institution Accreditation" 
          required={true}
          description="Proof diploma institution is NCHE-recognized"
        />
      </>
    )}
    
    {entryLevel === "bachelor" && qualificationPath === "hec" && (
      <>
        <DocumentUploadItem 
          label="HEC Completion Certificate" 
          required={true}
        />
        <DocumentUploadItem 
          label="UACE/UCE Result Slips" 
          required={true}
        />
      </>
    )}
    
    {/* Progress indicator */}
    <div className="mt-6 p-4 bg-blue-50 rounded-lg">
      <div className="flex justify-between mb-2">
        <span>Documents Uploaded:</span>
        <span className="font-bold">{uploadedCount} / {requiredCount}</span>
      </div>
      <Progress value={(uploadedCount / requiredCount) * 100} />
      {uploadedCount < requiredCount && (
        <p className="text-sm text-red-600 mt-2">
          Please upload all required documents to proceed
        </p>
      )}
    </div>
  </div>
</Card>
```

---

## 10. COMPLETE APPLICATION FLOW

```
Step 1: Select Highest Education
    ↓
Step 2: Select Curriculum (if O/A-Level)
    ↓
Step 3: Enter Qualification Details
    ├── O-Level Only → O-Level Form → Certificate Programs
    ├── A-Level → A-Level Form → HEC/Diploma/Bachelor
    ├── National Certificate → NC Form → Diploma/HEC
    ├── HEC → HEC Form → Bachelor
    ├── Diploma → Diploma Form → Bachelor
    ├── Bachelor → Degree Form → Masters
    └── Masters → Masters Form → PhD
    ↓
Step 4: Select Program to Apply For
    (Filtered by qualification eligibility)
    ↓
Step 5: Personal Information
    (Name, DOB, Gender, Nationality, District, Contact)
    ↓
Step 6: Document Upload
    (Dynamically generated based on entry level)
    ↓
Step 7: Review & Submit
    (Summary of all information + payment)
```

---

## Implementation Notes

1. **Dynamic Form Rendering**: Use `highestEducation` state to conditionally render appropriate form sections
2. **Real-time Validation**: Validate UNEB index numbers and grades as user types
3. **Curriculum Detection**: Auto-detect curriculum based on exam year (before 2024 = old, 2024+ = new)
4. **Eligibility Check**: Show real-time eligibility status as user enters grades
5. **Credit Transfer**: For diploma holders, calculate possible credit transfer to degree
6. **File Validation**: Ensure all uploads are valid PDF/images and within size limits
7. **Save Progress**: Allow saving partial applications and resuming later

This design handles all Uganda education pathways while maintaining NCHE compliance and supporting the 2024 curriculum transition.
