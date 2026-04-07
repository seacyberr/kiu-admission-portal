# KIU Portal — Changes & Deployment Guide

## What Was Built

### Core Feature: A-Level Program Recommendation Tool (Proposal Requirement)
The proposal's primary requirement was:
> *"Allow input of Advanced Level subject combinations, grades, General Paper
>  and subsidiary subjects (pass/fail) to receive personalized program
>  recommendations, complete with entry requirements, fees, duration and
>  career prospects."*

The **backend engine already existed** at `POST /api/admission/recommend` with
full NCHE compliance logic (GP check, principal subject validation, point
thresholds for medical/law programs). What was missing was the **frontend UI**.

### Admin Analytics Dashboard (Proposal Requirement)
> *"Administrators will manage program data, opportunities and generate reports
>  for decision making and institutional planning."*

The backend analytics endpoint `GET /api/admission/analytics` already returned
dropout risk, monthly trends, NCHE compliance stats, top programs by demand,
and demographics. The frontend just showed basic counts. This is now fixed.

---

## Files to Deploy

| Output File | Destination in Project | What it does |
|---|---|---|
| `recommend.tsx` | `apps/kiu-portal/src/pages/applicant/recommend.tsx` | **NEW** — A-Level subject input + program recommendation results page |
| `new-applicant.tsx` | `apps/kiu-portal/src/pages/applicant/new-applicant.tsx` | **UPDATED** — adds "Get Recommendations" CTA for eligible A-Level students |
| `admin-dashboard.tsx` | `apps/kiu-portal/src/pages/admin/dashboard.tsx` | **UPDATED** — enhanced with charts, dropout risk, NCHE compliance, demographics |
| `App.tsx` | `apps/kiu-portal/src/App.tsx` | **UPDATED** — adds `/recommend` route (RoleGuard: applicant) |
| `index.ts` | `lib/api-client-react/src/index.ts` | **UPDATED** — adds `useRecommendPrograms` and `useGetAnalytics` hooks |

---

## New Features Detail

### 1. `/recommend` — Program Recommendation Tool

**Route:** `/recommend` (authenticated applicants only)

**Flow:**
1. Student adds their A-Level principal subjects with grades (A–F)
2. Student adds subsidiary subjects (General Paper, Sub ICT, Sub Math)
3. Optional campus filter (Kampala / Western / All)
4. Click **"Get Program Recommendations"**
5. Results show: match percentage ring, matched subjects highlighted, NCHE compliance badge, fees (local + international), entry requirements, description, "Apply for This Program" CTA

**NCHE Compliance panel** (sidebar) shows:
- Total principal points
- GP status and grade
- Any NCHE errors or warnings in real time

**Entry point:** The `new-applicant.tsx` now shows a prominent
"Use Program Recommendation Tool" card for A-Level students with 3+ principal
passes, before offering direct application links.

### 2. Enhanced Admin Dashboard

**New sections:**
- **Application status breakdown** — horizontal bars for each status (pending / under_review / accepted / rejected / waitlisted) with counts and percentages
- **Monthly application trends** — Recharts bar chart showing applications per month for the current year
- **Top programs by demand** — ranked list of programs with relative demand bars
- **NCHE compliance** — 4-cell grid: With GP / Without GP / Sufficient Points / Insufficient Points
- **Demographics** — Local vs International, Gender breakdown, Session of study distribution
- **Dropout risk table** — collapsible table of at-risk applications with risk level badge, points, and risk factors
- **Report summary card** — acceptance rate, at-risk count, NCHE compliance %, local:international ratio

### 3. Updated API Client Hooks

Two new exports in `lib/api-client-react/src/index.ts`:

```typescript
// POST /api/admission/recommend
useRecommendPrograms(): UseMutationResult<RecommendResult, Error, {...}>

// GET /api/admission/analytics (admin only)
useGetAnalytics(): UseQueryResult<Analytics, Error>
```

New types also exported: `RecommendedProgram`, `NcheCompliance`,
`RecommendResult`, `Analytics`, `DropoutRiskApp`, `MonthlyTrend`, `TopProgram`.

---

## No Backend Changes Needed

All backend endpoints were already implemented:
- `POST /api/admission/recommend` ✅
- `GET /api/admission/analytics` ✅
- `POST /api/auth/forgot-password` ✅
- `POST /api/auth/reset-password` ✅

---

## Quick Verification

After deploying, verify:

1. Log in as an **applicant** → click **"My Application"** → choose **"A-Level (UACE)"** → answer "Yes" to both questions → see the **"Get Personalised Program Recommendations"** card → click it → add subjects → get recommendations.

2. Log in as **admin** → see the enhanced dashboard with charts and analytics. Click "Refresh analytics" to re-fetch.

3. Check `/api/admission/recommend` returns 200 with `recommendations[]` and `ncheCompliance` object.

4. Check `/api/admission/analytics` returns 200 with `dropoutRisk`, `programDemand`, `ncheCompliance`, `demographics` objects.
