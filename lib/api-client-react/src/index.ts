import { useMutation, useQuery, type UseQueryOptions } from "@tanstack/react-query";

// -----------------------------------------------------------------------------
// Shared types used across the portal
// -----------------------------------------------------------------------------

export type ProgramLevel = "degree" | "diploma" | "hec";

export type Program = {
  id: number;
  name: string;
  code?: string;
  faculty?: string | null;
  department?: string | null;
  level: ProgramLevel;
  duration?: string | null;
  description?: string | null;
  entryRequirements?: string | null;
  minOlevelPoints?: number | null;
  minAlevelPoints?: number | null;
  availableSlots?: number | null;
  campus?: string | null;
  feesLocal?: number | null;
  feesInternational?: number | null;
  functionalFeesLocal?: number | null;
  functionalFeesInternational?: number | null;
  tuitionFees?: number | null;
  functionalFees?: number | null;
  totalFees?: number | null;
  feesCurrency?: string | null;
};

export type UserRole = "admin" | "applicant" | "finalist";

export type User = {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string | null;
  role: UserRole | string;
  nationalId?: string | null;
  isVerified?: boolean;
  createdAt?: string | null;
};

export type AdmissionApplicationStatus =
  | "pending"
  | "under_review"
  | "accepted"
  | "rejected"
  | "waitlisted"
  | (string & {});

export type AdmissionApplication = {
  id: number;
  applicationNumber?: string | null;
  userId: number;
  programId: number;
  program?: Program | null;
  programChoices?: number[];
  status: AdmissionApplicationStatus;
  examLevel: string;
  examYear: number;
  indexNumber: string;
  unebGrades?: unknown;

  personalStatement?: string | null;
  dateOfBirth?: string | null;
  gender?: string | null;
  nationality?: string | null;
  district?: string | null;

  isFinalYear?: boolean;
  expectedGraduationYear?: number | null;
  currentYearOfStudy?: number | null;
  studentNumber?: string | null;

  nextOfKinName?: string | null;
  nextOfKinPhone?: string | null;
  nextOfKinRelationship?: string | null;

  adminNotes?: string | null;
  submittedAt?: string | null;
  updatedAt?: string | null;

  applicantName?: string | null;
  applicantEmail?: string | null;
};

export type CareerPath = {
  id: number;
  title: string;
  description: string;
  industryField: string;
  relatedPrograms: string[];
  skills: string[];
  potentialRoles: string[];
  averageSalaryRange?: string | null;
  growthOutlook?: string | null;
};

export type FinalistProfile = {
  id: number;
  userId: number;
  programId: number;
  program?: Program | null;
  studentNumber: string;
  yearOfStudy: number;
  graduationYear?: number | null;
  gpa?: number | null;
  skills: string[];
  bio?: string | null;
  linkedinUrl?: string | null;
  cvUrl?: string | null;
  isFinalist?: boolean;
};

export type Opportunity = {
  id: number;
  title: string;
  organization: string;
  type: string;
  description: string;
  requirements: string;
  requiredPrograms: unknown[];
  requiredSkills: unknown[];
  location?: string | null;
  salaryRange?: string | null;
  applicationDeadline?: string | null;
  contactEmail?: string | null;
  isActive: boolean;
  applicantCount?: number;
  postedAt?: string | null;
  updatedAt?: string | null;
};

// NEW: Recommendation types
export type RecommendedProgram = Program & {
  matchScore: number;
  matchPercentage: number;
  matchedSubjects: string[];
  ncheStatus: "compliant" | "conditional";
  programWarnings: string[];
};

export type NcheCompliance = {
  hasGeneralPaper: boolean;
  gpGrade: string | null;
  totalPrincipalPoints: number;
  errors: string[];
  warnings: string[];
};

export type RecommendResult = {
  recommendations: RecommendedProgram[];
  total: number;
  subjectsAnalyzed: string[];
  ncheCompliance: NcheCompliance;
};

// NEW: Analytics types
export type DropoutRiskApp = {
  applicationId: number;
  applicationNumber: string;
  studentName: string;
  program: string;
  programCode: string;
  totalPoints: number;
  minRequired: number | null;
  riskLevel: "high" | "medium";
  riskFactors: string[];
  status: string;
};

export type MonthlyTrend = {
  month: number;
  monthName: string;
  applications: number;
};

export type TopProgram = {
  name: string;
  code: string;
  faculty: string;
  applications: number;
};

export type Analytics = {
  summary: {
    totalApplications: number;
    byStatus: Record<string, number>;
    byProgram: Array<{ program: string; count: number }>;
  };
  dropoutRisk: {
    totalAtRisk: number;
    highRisk: number;
    mediumRisk: number;
    applications: DropoutRiskApp[];
  };
  programDemand: {
    monthlyTrends: MonthlyTrend[];
    topPrograms: TopProgram[];
  };
  ncheCompliance: {
    withGeneralPaper: number;
    withoutGeneralPaper: number;
    sufficientPoints: number;
    insufficientPoints: number;
  };
  demographics: {
    feeDistribution: { local: number; international: number };
    genderDistribution: Record<string, number>;
    sessionDistribution: Record<string, number>;
  };
  generatedAt: string;
};

// -----------------------------------------------------------------------------
// Internals
// -----------------------------------------------------------------------------

type QueryParams = Record<string, string | number | boolean | undefined | null>;

function getBaseUrl(): string {
  const env = (import.meta as any)?.env ?? {};
  return String(env.BASE_URL ?? "").replace(/\/$/, "");
}

const BASE_URL = getBaseUrl();

/** Primary auth is httpOnly cookie - no localStorage token needed. */
function getToken(): string | null {
  return null;
}

function toQueryString(params?: QueryParams): string {
  if (!params) return "";
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null);
  if (entries.length === 0) return "";
  return entries
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join("&");
}

async function fetchAuthMe(): Promise<User | null> {
  const res = await fetch(`${BASE_URL}/api/auth/me`, {
    method: "GET",
    credentials: "include",
  });
  if (res.status === 401) return null;
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const json = (await res.json()) as { message?: string };
      message = json?.message ?? message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  return (await res.json()) as User;
}

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  try {
    const storedUser = typeof window !== "undefined" ? localStorage.getItem("kiu_user") : null;
    if (!storedUser) return false;
    const res = await fetch(`${BASE_URL}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    });
    if (res.ok) {
      const json = await res.json();
      if (json.user) {
        localStorage.setItem("kiu_user", JSON.stringify(json.user));
      }
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

async function apiFetchJson<T>(path: string, init?: RequestInit & { token?: string | null }): Promise<T> {
  const token = init?.token ?? getToken();
  const headers: Record<string, string> = {
    ...(init?.headers ? (init.headers as Record<string, string>) : {}),
  };
  const hasBody = init?.body !== undefined && init?.body !== null;
  if (hasBody && typeof init.body === "string") {
    headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
  }
  if (token) headers.Authorization = `Bearer ${token}`;

  let res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (res.status === 401 && !init?.token) {
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = refreshAccessToken().finally(() => {
        isRefreshing = false;
        refreshPromise = null;
      });
    }
    const refreshed = await refreshPromise;
    if (refreshed) {
      res = await fetch(`${BASE_URL}${path}`, {
        ...init,
        headers,
        credentials: "include",
      });
    }
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const json = (await res.json()) as any;
      message = json?.message ?? json?.error ?? message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  if (res.status === 204) return undefined as T;
  const text = await res.text();
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

type QueryOverrides<TData> = Partial<
  Omit<UseQueryOptions<TData, Error, TData, readonly unknown[]>, "queryKey" | "queryFn">
>;

function mergeQueryOverrides<TData>(overrides?: QueryOverrides<TData>): QueryOverrides<TData> {
  return (overrides ?? {}) as QueryOverrides<TData>;
}

// -----------------------------------------------------------------------------
// Queries
// -----------------------------------------------------------------------------

export function useListPrograms(params?: { level?: ProgramLevel }) {
  const url = params?.level
    ? `/api/admission/programs?level=${encodeURIComponent(params.level)}`
    : `/api/admission/programs`;
  return useQuery<{ programs: Program[] }, Error>({
    queryKey: ["programs", params?.level ?? null],
    queryFn: () => apiFetchJson<{ programs: Program[] }>(url, { method: "GET" }),
  });
}

export function useGetCurrentUser(options?: { query?: QueryOverrides<User | null> }) {
  const merged = mergeQueryOverrides(options?.query);
  return useQuery<User | null, Error>({
    queryKey: ["me"],
    queryFn: () => fetchAuthMe(),
    ...merged,
    enabled: merged.enabled ?? true,
  });
}

export function useGetMyAdmissionApplication(options?: { query?: QueryOverrides<AdmissionApplication | null> }) {
  const { data: user, isLoading: authLoading } = useGetCurrentUser({ query: { retry: false } });
  const merged = mergeQueryOverrides(options?.query);
  return useQuery<AdmissionApplication | null, Error>({
    queryKey: ["my-admission-application"],
    queryFn: async () => {
      const json = await apiFetchJson<{ application: AdmissionApplication | null }>(
        `/api/admission/applications/mine`,
        { method: "GET" },
      );
      return json.application;
    },
    ...merged,
    enabled: (merged.enabled ?? true) && !authLoading && user?.role === "applicant",
  });
}

export function useListAdmissionApplications(options?: {
  filters?: {
    page?: number;
    perPage?: number;
    status?: string;
    search?: string;
  };
  query?: QueryOverrides<{
    applications: AdmissionApplication[];
    total: number;
    page: number;
    perPage: number;
    pages: number;
  }>;
}) {
  const filters = options?.filters;
  const queryParams: QueryParams = {
    page: filters?.page,
    perPage: filters?.perPage,
    status: filters?.status,
    search: filters?.search,
  };

  type Resp = {
    applications: AdmissionApplication[];
    total: number;
    page: number;
    perPage: number;
    pages: number;
  };
  const { data: user, isLoading: authLoading } = useGetCurrentUser({ query: { retry: false } });
  const merged = mergeQueryOverrides(options?.query);
  return useQuery<Resp, Error>({
    queryKey: ["admin-admission-applications", queryParams],
    queryFn: () =>
      apiFetchJson<Resp>(`/api/admission/applications?${toQueryString(queryParams)}`, { method: "GET" }),
    ...merged,
    enabled: (merged.enabled ?? true) && !authLoading && user?.role === "admin",
  });
}

export function useListOpportunities(options?: {
  type?: string;
  field?: string;
  page?: number;
  limit?: number;
  query?: QueryOverrides<{
    opportunities: Opportunity[];
    total: number;
    page: number;
    limit: number;
  }>;
} | undefined) {
  const queryParams: QueryParams = {
    type: options?.type,
    field: options?.field,
    page: options?.page,
    limit: options?.limit,
  };

  type Resp = {
    opportunities: Opportunity[];
    total: number;
    page: number;
    limit: number;
  };
  return useQuery<Resp, Error>({
    queryKey: ["opportunities", queryParams],
    queryFn: () =>
      apiFetchJson<Resp>(
        `/api/opportunities${toQueryString(queryParams) ? `?${toQueryString(queryParams)}` : ""}`,
        { method: "GET" },
      ),
    ...(options?.query ?? {}),
  });
}

export function useListCareerPaths(options?: {
  program?: string;
  query?: QueryOverrides<{ careerPaths: CareerPath[]; total: number }>;
  faculty?: string;
}) {
  const queryParams: QueryParams = {
    program: options?.program,
    faculty: options?.faculty,
  };

  type Resp = { careerPaths: CareerPath[]; total: number };
  return useQuery<Resp, Error>({
    queryKey: ["careerPaths", queryParams],
    queryFn: () =>
      apiFetchJson<Resp>(
        `/api/career/paths${toQueryString(queryParams) ? `?${toQueryString(queryParams)}` : ""}`,
        { method: "GET" },
      ),
    ...(options?.query ?? {}),
  });
}

export function useGetFinalistProfile(options?: { query?: QueryOverrides<FinalistProfile> }) {
  const { data: user, isLoading: authLoading } = useGetCurrentUser({ query: { retry: false } });
  const merged = mergeQueryOverrides(options?.query);
  return useQuery<FinalistProfile, Error>({
    queryKey: ["my-finalist-profile"],
    queryFn: () => apiFetchJson<FinalistProfile>(`/api/career/my-profile`, { method: "GET" }),
    ...merged,
    enabled: (merged.enabled ?? true) && !authLoading && user?.role === "finalist",
  } as UseQueryOptions<FinalistProfile, Error, FinalistProfile, readonly unknown[]>);
}

/** NEW: Get admin analytics (dropout risk, program demand, NCHE compliance, demographics) */
export function useGetAnalytics(options?: { query?: QueryOverrides<Analytics> }) {
  const { data: user, isLoading: authLoading } = useGetCurrentUser({ query: { retry: false } });
  const merged = mergeQueryOverrides(options?.query);
  return useQuery<Analytics, Error>({
    queryKey: ["admin-analytics"],
    queryFn: () => apiFetchJson<Analytics>(`/api/admission/analytics`, { method: "GET" }),
    ...merged,
    enabled: (merged.enabled ?? true) && !authLoading && user?.role === "admin",
    staleTime: 5 * 60 * 1000, // 5 minutes — analytics are relatively static
  } as UseQueryOptions<Analytics, Error, Analytics, readonly unknown[]>);
}

// -----------------------------------------------------------------------------
// Mutations
// -----------------------------------------------------------------------------

export function useUpdateAdmissionStatus() {
  return useMutation({
    mutationFn: async (vars: {
      id: number;
      data: {
        status: AdmissionApplicationStatus;
        adminNotes?: string | undefined;
        programId?: number | undefined;
      };
    }) => {
      return apiFetchJson<AdmissionApplication>(
        `/api/admission/applications/${vars.id}/status`,
        { method: "PATCH", body: JSON.stringify(vars.data) },
      );
    },
  });
}

export function useCreateOpportunity() {
  return useMutation({
    mutationFn: async (vars: { data: Record<string, unknown> }) => {
      return apiFetchJson<Opportunity>(`/api/opportunities`, {
        method: "POST",
        body: JSON.stringify(vars.data),
      });
    },
  });
}

export function useUpdateOpportunity() {
  return useMutation({
    mutationFn: async (vars: { id: number; data: Record<string, unknown> }) => {
      return apiFetchJson<Opportunity>(`/api/opportunities/${vars.id}`, {
        method: "PATCH",
        body: JSON.stringify(vars.data),
      });
    },
  });
}

export function useDeleteOpportunity() {
  return useMutation({
    mutationFn: async (vars: { id: number }) => {
      const res = await fetch(`${BASE_URL}/api/opportunities/${vars.id}`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!res.ok) throw new Error(`Delete failed (${res.status})`);
      return true;
    },
  });
}

export function useApplyForOpportunity() {
  return useMutation({
    mutationFn: async (vars: {
      id: number;
      data: { coverLetter: string; cvUrl?: string; additionalInfo?: string };
    }) => {
      return apiFetchJson<Opportunity>(`/api/opportunities/${vars.id}/apply`, {
        method: "POST",
        body: JSON.stringify(vars.data),
      });
    },
  });
}

/** NEW: POST /api/admission/recommend — get A-Level based program recommendations */
export function useRecommendPrograms() {
  return useMutation({
    mutationFn: async (vars: {
      alevelSubjects: Array<{
        subject: string;
        grade: string;
        subjectType: "principal" | "subsidiary";
      }>;
      campus?: string;
      curriculum?: string;
    }) => {
      return apiFetchJson<RecommendResult>(`/api/admission/recommend`, {
        method: "POST",
        body: JSON.stringify(vars),
      });
    },
  });
}

export function useLoginUser() {
  return useMutation({
    mutationFn: async (vars: { email: string; password: string }) => {
      return apiFetchJson<any>(`/api/auth/login`, {
        method: "POST",
        body: JSON.stringify(vars),
      });
    },
  });
}

export function useRegisterUser() {
  return useMutation({
    mutationFn: async (vars: { data: Record<string, unknown> }) => {
      return apiFetchJson<any>(`/api/auth/register`, {
        method: "POST",
        body: JSON.stringify(vars.data),
      });
    },
  });
}
