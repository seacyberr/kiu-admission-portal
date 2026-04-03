/**
 * API type definitions for KIU Portal.
 */

export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  role: 'applicant' | 'finalist' | 'admin';
  nationalId?: string;
  isVerified: boolean;
  createdAt: string;
}

export interface Program {
  id: number;
  name: string;
  code: string;
  faculty: string;
  department?: string;
  level: 'degree' | 'diploma' | 'hec';
  duration?: string;
  description?: string;
  entryRequirements?: string;
  minOlevelPoints?: number;
  minAlevelPoints?: number;
  availableSlots: number;
  campus: string;
}

export interface AdmissionApplication {
  id: number;
  applicationNumber: string;
  userId: number;
  programId: number;
  program?: Program;
  programChoices: number[];
  status: 'pending' | 'under_review' | 'accepted' | 'rejected' | 'waitlisted';
  examLevel: 'o_level' | 'a_level' | 'diploma' | 'hec';
  examYear: number;
  indexNumber: string;
  unebGrades: {
    olevel?: Array<{ subject: string; grade: string; points: number }>;
    alevel?: Array<{ subject: string; grade: string; points: number; subjectType: string }>;
  };
  personalStatement?: string;
  dateOfBirth: string;
  gender: string;
  nationality: string;
  district?: string;
  adminNotes?: string;
  submittedAt: string;
  updatedAt: string;
}

export interface CareerPath {
  id: number;
  title: string;
  description: string;
  relatedPrograms: string[];
  skills: string[];
  potentialRoles: string[];
  averageSalaryRange?: string;
  growthOutlook?: string;
  industryField: string;
}

export interface Opportunity {
  id: number;
  title: string;
  organization: string;
  type: 'job' | 'internship';
  description: string;
  requirements: string;
  requiredPrograms: string[];
  requiredSkills: string[];
  location?: string;
  salaryRange?: string;
  applicationDeadline: string;
  contactEmail?: string;
  isActive: boolean;
  applicantCount: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  perPage: number;
  pages: number;
}