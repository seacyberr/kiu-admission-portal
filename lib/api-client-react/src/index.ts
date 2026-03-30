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

// -----------------------------------------------------------------------------
// Internals
// -----------------------------------------------------------------------------

type QueryParams = Record<string, string | number | boolean | undefined | null>;

function getBaseUrl(): string {
  const env = (import.meta as any)?.env ?? {};
  return String(env.BASE_URL ?? "").replace(/\/$/, "");
}

const BASE_URL = getBaseUrl();

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("kiu_token");
}

function toQueryString(params?: QueryParams): string {
  if (!params) return "";
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null);
  if (entries.length === 0) return "";
  return entries
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join("&");
}

async function apiFetchJson<T>(path: string, init?: RequestInit & { token?: string | null }): Promise<T> {
  const token = init?.token ?? getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers ? (init.headers as Record<string, string>) : {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
  });

  // Try to return structured errors, but keep it resilient.
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

  return (await res.json()) as T;
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
  const url = params?.level ? `/api/admission/programs?level=${encodeURIComponent(params.level)}` : `/api/admission/programs`;
  return useQuery<{ programs: Program[] }, Error>({
    queryKey: ["programs", params?.level ?? null],
    queryFn: () => apiFetchJson<{ programs: Program[] }>(url, { method: "GET" }),
  });
}

export function useGetCurrentUser(options?: { query?: QueryOverrides<User> }) {
  const token = getToken();
  return useQuery<User, Error>({
    queryKey: ["me", token ? true : false],
    enabled: mergeQueryOverrides(options?.query).enabled ?? !!token,
    queryFn: () => apiFetchJson<User>(`/api/auth/me`, { method: "GET" }),
    ...mergeQueryOverrides(options?.query),
  });
}

export function useGetMyAdmissionApplication(options?: { query?: QueryOverrides<AdmissionApplication | null> }) {
  const token = getToken();
  return useQuery<AdmissionApplication | null, Error>({
    queryKey: ["my-admission-application"],
    enabled: mergeQueryOverrides(options?.query).enabled ?? !!token,
    queryFn: async () => {
      const json = await apiFetchJson<{ application: AdmissionApplication | null }>(
        `/api/admission/applications/mine`,
        { method: "GET" },
      );
      return json.application;
    },
    ...mergeQueryOverrides(options?.query),
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
  return useQuery<Resp, Error>({
    queryKey: ["admin-admission-applications", queryParams],
    queryFn: () =>
      apiFetchJson<Resp>(`/api/admission/applications?${toQueryString(queryParams)}`, { method: "GET" }),
    ...(options?.query ?? {}),
  });
}

export function useListOpportunities(options?: { type?: string; field?: string; page?: number; limit?: number; query?: QueryOverrides<{
  opportunities: Opportunity[];
  total: number;
  page: number;
  limit: number;
}> } | undefined) {
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

export function useListCareerPaths(options?: { program?: string; query?: QueryOverrides<{
  careerPaths: CareerPath[];
  total: number;
}>; faculty?: string }) {
  const queryParams: QueryParams = {
    program: options?.program,
    faculty: options?.faculty,
  };

  type Resp = {
    careerPaths: CareerPath[];
    total: number;
  };
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

export function useGetFinalistProfile(options?: { query?: any }) {
  const token = getToken();
  return useQuery<FinalistProfile, Error>({
    queryKey: ["my-finalist-profile"],
    enabled: (options?.query as any)?.enabled ?? !!token,
    queryFn: () => apiFetchJson<FinalistProfile>(`/api/career/my-profile`, { method: "GET" }),
    ...(options?.query ?? {}),
  });
}

// -----------------------------------------------------------------------------
// Mutations
// -----------------------------------------------------------------------------

type MutVars<T> = T;

export function useUpdateAdmissionStatus() {
  return useMutation({
    mutationFn: async (vars: { id: number; data: { status: AdmissionApplicationStatus; adminNotes?: string | undefined } }) => {
      return apiFetchJson<AdmissionApplication>(`/api/admission/applications/${vars.id}/status`, {
        method: "PATCH",
        body: JSON.stringify(vars.data),
      });
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
        headers: getToken() ? { Authorization: `Bearer ${getToken()}` } : undefined,
      });
      if (!res.ok) throw new Error(`Delete failed (${res.status})`);
      return true;
    },
  });
}

export function useApplyForOpportunity() {
  return useMutation({
    mutationFn: async (vars: { id: number; data: { coverLetter: string; cvUrl?: string; additionalInfo?: string } }) => {
      return apiFetchJson<Opportunity>(`/api/opportunities/${vars.id}/apply`, {
        method: "POST",
        body: JSON.stringify(vars.data),
      });
    },
  });
}

// Login/register mutations are not used by the current UI (login/register pages do direct fetch),
// but exporting them keeps the build consistent.
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

