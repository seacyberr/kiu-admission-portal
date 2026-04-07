import { useMutation, useQuery, type UseQueryOptions } from "@tanstack/react-query";

// -----------------------------------------------------------------------------
// Shared types
// -----------------------------------------------------------------------------

export type ProgramLevel = "degree" | "diploma" | "hec" | "masters" | "phd";

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

export type RecommendSubjectInput = {
  subject: string;
  grade: string;
  subjectType: "principal" | "subsidiary";
};

export type RecommendProgramsInput = {
  alevelSubjects?: RecommendSubjectInput[];
  campus?: string;
  curriculum?: string;
  qualificationType?: "a_level" | "o_level" | "diploma" | "hec";
  qualification?: string;
  grade?: string;
  institution?: string;
  year?: string;
};

export type NcheCompliance = {
  hasGeneralPaper: boolean;
  gpGrade?: string | null;
  totalPrincipalPoints: number;
  errors: string[];
  warnings: string[];
};

export type RecommendedProgram = Program & {
  matchScore: number;
  matchPercentage: number;
  matchedSubjects: string[];
  ncheStatus: "compliant" | "conditional" | string;
  programWarnings: string[];
  feesLocal?: number | null;
  feesInternational?: number | null;
};

export type QualificationCheckResult = {
  eligible: boolean;
  message: string;
  eligiblePrograms: string[];
  requirementsMet: string[];
  requirementsMissing: string[];
};

export type QualificationResult = {
  olevel: QualificationCheckResult;
  alevel?: QualificationCheckResult;
  recommendedPathways: string[];
  nextSteps: string[];
};

export type RecommendResult = {
  recommendations: RecommendedProgram[];
  total: number;
  qualificationCheck: QualificationResult;
  allowedProgramLevels: string[];
  totalProgramsScanned: number;
  programsExcludedByQualification: number;
  subjectsAnalyzed: string[];
  ncheCompliance: NcheCompliance;
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
    } catch { /* ignore */ }
    throw new Error(message);
  }
  return (await res.json()) as User;
}

// ---------------------------------------------------------------------------
// Token refresh
// BUG FIX: The previous implementation sent an empty {} body to /api/auth/refresh.
// The backend expected { "refreshToken": "..." } but the frontend never stored
// the refresh token anywhere, so refresh always returned 401 and every user was
// effectively logged out after the 15-minute access-token window expired.
//
// The fixed backend now stores the refresh token in a separate httpOnly cookie
// (path=/api/auth/refresh) that the browser sends automatically.  The client
// therefore just needs to POST to the endpoint with credentials:include and an
// empty body — the cookie is sent by the browser without any JS involvement.
// ---------------------------------------------------------------------------

let _refreshInFlight: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  try {
    // The refresh token is in an httpOnly cookie scoped to /api/auth/refresh.
    // credentials: "include" makes the browser attach it automatically.
    const res = await fetch(`${BASE_URL}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}), // body required by some CORS pre-flight configs
    });

    if (res.ok) {
      const json = await res.json();
      if (json.user) {
        localStorage.setItem("kiu_user", JSON.stringify(json.user));
      }
      return true;
    }
    // Refresh token expired or revoked — clear stale local state
    localStorage.removeItem("kiu_user");
    return false;
  } catch {
    return false;
  }
}

async function apiFetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    ...(init?.headers ? (init.headers as Record<string, string>) : {}),
  };
  if (init?.body !== undefined && typeof init.body === "string") {
    headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
  }

  let res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  // On 401, attempt a single token refresh then retry
  if (res.status === 401) {
    if (!_refreshInFlight) {
      _refreshInFlight = refreshAccessToken().finally(() => {
        _refreshInFlight = null;
      });
    }
    const refreshed = await _refreshInFlight;
    if (refreshed) {
      res = await fetch(`${BASE_URL}${path}`, { ...init, headers, credentials: "include" });
    }
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const json = (await res.json()) as any;
      message = json?.message ?? json?.error ?? message;
    } catch { /* ignore */ }
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

export function useGetMyAdmissionApplication(
  options?: { query?: QueryOverrides<AdmissionApplication | null> }
) {
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
  filters?: { page?: number; perPage?: number; status?: string; search?: string };
  query?: QueryOverrides<{
    applications: AdmissionApplication[];
    total: number; page: number; perPage: number; pages: number;
  }>;
}) {
  const filters = options?.filters;
  const queryParams: QueryParams = {
    page: filters?.page, perPage: filters?.perPage,
    status: filters?.status, search: filters?.search,
  };

  type Resp = {
    applications: AdmissionApplication[];
    total: number; page: number; perPage: number; pages: number;
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
  type?: string; field?: string; page?: number; limit?: number;
  query?: QueryOverrides<{ opportunities: Opportunity[]; total: number; page: number; limit: number }>;
} | undefined) {
  const queryParams: QueryParams = {
    type: options?.type, field: options?.field, page: options?.page, limit: options?.limit,
  };
  type Resp = { opportunities: Opportunity[]; total: number; page: number; limit: number };
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
  program?: string; faculty?: string;
  query?: QueryOverrides<{ careerPaths: CareerPath[]; total: number }>;
}) {
  const queryParams: QueryParams = { program: options?.program, faculty: options?.faculty };
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

// -----------------------------------------------------------------------------
// Mutations
// -----------------------------------------------------------------------------

export function useUpdateAdmissionStatus() {
  return useMutation({
    mutationFn: async (vars: {
      id: number;
      data: { status: AdmissionApplicationStatus; adminNotes?: string; programId?: number };
    }) => apiFetchJson<AdmissionApplication>(`/api/admission/applications/${vars.id}/status`, {
      method: "PATCH",
      body: JSON.stringify(vars.data),
    }),
  });
}

export function useCreateOpportunity() {
  return useMutation({
    mutationFn: async (vars: { data: Record<string, unknown> }) =>
      apiFetchJson<Opportunity>(`/api/opportunities`, {
        method: "POST",
        body: JSON.stringify(vars.data),
      }),
  });
}

export function useUpdateOpportunity() {
  return useMutation({
    mutationFn: async (vars: { id: number; data: Record<string, unknown> }) =>
      apiFetchJson<Opportunity>(`/api/opportunities/${vars.id}`, {
        method: "PATCH",
        body: JSON.stringify(vars.data),
      }),
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
    }) =>
      apiFetchJson<Opportunity>(`/api/opportunities/${vars.id}/apply`, {
        method: "POST",
        body: JSON.stringify(vars.data),
      }),
  });
}

export function useRecommendPrograms() {
  return useMutation({
    mutationFn: async (vars: RecommendProgramsInput) =>
      apiFetchJson<RecommendResult>(`/api/admission/recommend`, {
        method: "POST",
        body: JSON.stringify(vars),
      }),
  });
}

/**
 * BUG FIX: useLoginUser and useRegisterUser were defined but login.tsx /
 * register.tsx use direct fetch() calls instead of these mutations.
 * The mutations were exported (keeping the build consistent) but the
 * isLoading / isPending state they carry was referenced in the UI
 * (loginMutation.isPending) while always being false.
 *
 * These hooks are kept for potential future use and for API-client consumers.
 * The login / register pages should migrate to using these hooks to benefit
 * from the automatic loading state, or remove the isPending reference.
 */
export function useLoginUser() {
  return useMutation({
    mutationFn: async (vars: { email: string; password: string }) =>
      apiFetchJson<{ user: User }>(`/api/auth/login`, {
        method: "POST",
        body: JSON.stringify(vars),
      }),
  });
}

export function useRegisterUser() {
  return useMutation({
    mutationFn: async (vars: { data: Record<string, unknown> }) =>
      apiFetchJson<{ email: string; needsVerification: boolean }>(`/api/auth/register`, {
        method: "POST",
        body: JSON.stringify(vars.data),
      }),
  });
}

export function useUpdateFinalistProfile() {
  return useMutation({
    mutationFn: async (vars: Partial<FinalistProfile>) =>
      apiFetchJson<FinalistProfile>(`/api/career/my-profile`, {
        method: "PUT",
        body: JSON.stringify(vars),
      }),
  });
}
