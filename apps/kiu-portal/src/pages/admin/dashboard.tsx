/**
 * admin/dashboard.tsx — Enhanced Admin Dashboard with Analytics
 *
 * Proposal requirement:
 * "Administrators will manage program data, opportunities and generate reports
 *  for decision making and institutional planning."
 *
 * Features added over original:
 * - Application status breakdown with visual bars
 * - Monthly application trend chart (Recharts)
 * - Top programs by demand
 * - NCHE compliance statistics
 * - Dropout risk summary table
 * - Demographics (gender, local/international, session)
 */

import { useState } from "react";
import { Link } from "wouter";
import {
  useListAdmissionApplications,
  useListOpportunities,
  useGetAnalytics,
} from "@workspace/api-client-react";
import { Card, Badge } from "@/components/ui/shared";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  Users,
  FileText,
  Briefcase,
  AlertTriangle,
  TrendingUp,
  ChevronRight,
  CheckCircle,
  GraduationCap,
  BarChart2,
  RefreshCw,
} from "lucide-react";

// ── Colour helpers ─────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  pending: "#f59e0b",
  under_review: "#3b82f6",
  accepted: "#10b981",
  rejected: "#ef4444",
  waitlisted: "#8b5cf6",
};

const BAR_COLORS = [
  "#16a34a", "#2563eb", "#d97706", "#7c3aed", "#db2777",
  "#0891b2", "#ea580c", "#65a30d", "#0d9488", "#9333ea",
];

// ── Stat Card ─────────────────────────────────────────────────────────────────

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  color = "primary",
  href,
}: {
  icon: React.ElementType;
  label: string;
  value: number | string;
  sub?: string;
  color?: "primary" | "amber" | "green" | "red" | "purple";
  href?: string;
}) {
  const colorMap = {
    primary: "bg-primary text-primary-foreground",
    amber: "bg-amber-50 border-amber-200 text-amber-700",
    green: "bg-green-50 border-green-200 text-green-700",
    red: "bg-red-50 border-red-200 text-red-700",
    purple: "bg-purple-50 border-purple-200 text-purple-700",
  };
  const iconMap = {
    primary: "bg-white/20",
    amber: "bg-amber-100",
    green: "bg-green-100",
    red: "bg-red-100",
    purple: "bg-purple-100",
  };

  const inner = (
    <Card
      className={`p-6 flex items-center gap-4 border ${colorMap[color]} ${href ? "hover:shadow-md transition-shadow cursor-pointer" : ""}`}
    >
      <div className={`w-12 h-12 rounded-full ${iconMap[color]} flex items-center justify-center shrink-0`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <p className={`font-semibold text-sm opacity-80`}>{label}</p>
        <p className="text-3xl font-bold">{value}</p>
        {sub && <p className="text-xs opacity-70 mt-0.5">{sub}</p>}
      </div>
    </Card>
  );

  return href ? <Link href={href}>{inner}</Link> : inner;
}

// ── StatusBar ─────────────────────────────────────────────────────────────────

function StatusBar({ status, count, total }: { status: string; count: number; total: number }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  const color = STATUS_COLORS[status] ?? "#94a3b8";
  return (
    <div className="flex items-center gap-3">
      <span
        className="text-xs font-semibold capitalize w-24 shrink-0"
        style={{ color }}
      >
        {status.replace("_", " ")}
      </span>
      <div className="flex-1 bg-secondary rounded-full h-2">
        <div
          className="h-2 rounded-full transition-all"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-xs font-bold w-8 text-right">{count}</span>
      <span className="text-xs text-muted-foreground w-8">({pct}%)</span>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const { data: admissions } = useListAdmissionApplications();
  const { data: opportunities } = useListOpportunities();
  const {
    data: analytics,
    isLoading: analyticsLoading,
    refetch,
    isRefetching,
  } = useGetAnalytics();

  const [showRiskTable, setShowRiskTable] = useState(false);

  const pendingCount =
    admissions?.applications.filter((a: any) => a.status === "pending").length ?? 0;
  const activeJobs =
    opportunities?.opportunities.filter((o: any) => o.isActive).length ?? 0;

  const total = analytics?.summary.totalApplications ?? 0;
  const byStatus = analytics?.summary.byStatus ?? {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-10">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-primary">
            Admin Overview
          </h1>
          <p className="text-muted-foreground mt-1">
            Admissions, opportunities and institutional analytics
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary transition-colors"
        >
          <RefreshCw
            className={`w-4 h-4 ${isRefetching ? "animate-spin" : ""}`}
          />
          Refresh analytics
        </button>
      </div>

      {/* ── KPI cards ────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={FileText}
          label="Total Applications"
          value={total || admissions?.total || 0}
          color="primary"
          href="/admin/admissions"
        />
        <StatCard
          icon={AlertTriangle}
          label="Pending Review"
          value={byStatus["pending"] ?? pendingCount}
          sub="Awaiting action"
          color="amber"
          href="/admin/admissions"
        />
        <StatCard
          icon={CheckCircle}
          label="Accepted"
          value={byStatus["accepted"] ?? 0}
          color="green"
        />
        <StatCard
          icon={Briefcase}
          label="Active Opportunities"
          value={activeJobs}
          color="purple"
          href="/admin/opportunities"
        />
      </div>

      {/* ── Main analytics grid ───────────────────────────────────────────── */}
      <div className="grid lg:grid-cols-2 gap-8">

        {/* Application status breakdown */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-5 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-primary" />
            Applications by Status
          </h2>
          {analyticsLoading ? (
            <div className="h-40 flex items-center justify-center text-muted-foreground text-sm">
              Loading…
            </div>
          ) : (
            <div className="space-y-3">
              {["pending", "under_review", "accepted", "rejected", "waitlisted"].map(
                (s) => (
                  <StatusBar
                    key={s}
                    status={s}
                    count={byStatus[s] ?? 0}
                    total={total}
                  />
                )
              )}
              {total === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No applications yet.
                </p>
              )}
            </div>
          )}
        </Card>

        {/* Monthly trends chart */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-5 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Monthly Application Trends ({new Date().getFullYear()})
          </h2>
          {analyticsLoading ? (
            <div className="h-40 flex items-center justify-center text-muted-foreground text-sm">
              Loading…
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart
                data={analytics?.programDemand.monthlyTrends ?? []}
                margin={{ top: 4, right: 8, bottom: 0, left: -24 }}
              >
                <XAxis
                  dataKey="monthName"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(v: string) => v.slice(0, 3)}
                />
                <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
                <Tooltip
                  formatter={(v: number) => [v, "Applications"]}
                  labelStyle={{ fontSize: 12 }}
                  contentStyle={{ fontSize: 12 }}
                />
                <Bar dataKey="applications" radius={[4, 4, 0, 0]}>
                  {(analytics?.programDemand.monthlyTrends ?? []).map(
                    (_, i) => (
                      <Cell
                        key={i}
                        fill={
                          BAR_COLORS[i % BAR_COLORS.length]
                        }
                      />
                    )
                  )}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        {/* Top programs by demand */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-5 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-primary" />
            Top Programs by Demand
          </h2>
          {analyticsLoading ? (
            <div className="h-40 flex items-center justify-center text-muted-foreground text-sm">
              Loading…
            </div>
          ) : analytics?.programDemand.topPrograms.length ? (
            <div className="space-y-3">
              {analytics.programDemand.topPrograms.map((p, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-xs font-bold text-muted-foreground w-5">
                    {i + 1}.
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{p.name}</p>
                    <p className="text-xs text-muted-foreground">{p.faculty}</p>
                  </div>
                  <div className="shrink-0">
                    <div className="w-16 bg-secondary rounded-full h-1.5">
                      <div
                        className="h-1.5 rounded-full bg-primary"
                        style={{
                          width: `${Math.min(
                            100,
                            (p.applications /
                              (analytics.programDemand.topPrograms[0]
                                ?.applications || 1)) *
                              100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span className="text-xs font-bold w-6 text-right">
                    {p.applications}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-4">
              No application data yet.
            </p>
          )}
        </Card>

        {/* NCHE Compliance + Demographics */}
        <div className="space-y-6">
          {/* NCHE compliance */}
          <Card className="p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-primary" />
              NCHE Compliance
            </h2>
            {analyticsLoading ? (
              <div className="h-20 flex items-center justify-center text-muted-foreground text-sm">
                Loading…
              </div>
            ) : analytics ? (
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="p-3 rounded-xl bg-green-50">
                  <p className="text-xs text-green-600 font-semibold mb-1">
                    With General Paper
                  </p>
                  <p className="text-2xl font-bold text-green-700">
                    {analytics.ncheCompliance.withGeneralPaper}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-amber-50">
                  <p className="text-xs text-amber-600 font-semibold mb-1">
                    Without General Paper
                  </p>
                  <p className="text-2xl font-bold text-amber-700">
                    {analytics.ncheCompliance.withoutGeneralPaper}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-green-50">
                  <p className="text-xs text-green-600 font-semibold mb-1">
                    Sufficient Points
                  </p>
                  <p className="text-2xl font-bold text-green-700">
                    {analytics.ncheCompliance.sufficientPoints}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-red-50">
                  <p className="text-xs text-red-600 font-semibold mb-1">
                    Insufficient Points
                  </p>
                  <p className="text-2xl font-bold text-red-700">
                    {analytics.ncheCompliance.insufficientPoints}
                  </p>
                </div>
              </div>
            ) : null}
          </Card>

          {/* Demographics */}
          <Card className="p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" />
              Demographics
            </h2>
            {analyticsLoading ? (
              <div className="h-20 flex items-center justify-center text-muted-foreground text-sm">
                Loading…
              </div>
            ) : analytics ? (
              <div className="space-y-4 text-sm">
                {/* Local vs International */}
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                    Nationality
                  </p>
                  <div className="flex gap-3">
                    <div className="flex-1 p-2 rounded-lg bg-blue-50 text-center">
                      <p className="font-bold text-blue-700">
                        {analytics.demographics.feeDistribution.local}
                      </p>
                      <p className="text-xs text-blue-600">Local/EA</p>
                    </div>
                    <div className="flex-1 p-2 rounded-lg bg-purple-50 text-center">
                      <p className="font-bold text-purple-700">
                        {analytics.demographics.feeDistribution.international}
                      </p>
                      <p className="text-xs text-purple-600">International</p>
                    </div>
                  </div>
                </div>

                {/* Gender */}
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                    Gender
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {Object.entries(
                      analytics.demographics.genderDistribution
                    ).map(([g, count]) => (
                      <div
                        key={g}
                        className="px-3 py-1.5 rounded-lg bg-secondary text-sm"
                      >
                        <span className="capitalize font-semibold">{g}</span>:{" "}
                        <span className="font-bold">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Session */}
                {Object.keys(analytics.demographics.sessionDistribution).length >
                  0 && (
                  <div>
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                      Session of Study
                    </p>
                    <div className="flex gap-2 flex-wrap">
                      {Object.entries(
                        analytics.demographics.sessionDistribution
                      ).map(([s, count]) => (
                        <div
                          key={s}
                          className="px-3 py-1.5 rounded-lg bg-secondary text-sm"
                        >
                          <span className="capitalize font-semibold">{s}</span>:{" "}
                          <span className="font-bold">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </Card>
        </div>
      </div>

      {/* ── Dropout Risk Section ──────────────────────────────────────────── */}
      {analytics && analytics.dropoutRisk.totalAtRisk > 0 && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-lg font-bold flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Dropout Risk Alerts
              </h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Students whose profile may not meet program requirements
              </p>
            </div>
            <div className="flex gap-3">
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">
                  {analytics.dropoutRisk.highRisk}
                </p>
                <p className="text-xs text-muted-foreground">High Risk</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-amber-500">
                  {analytics.dropoutRisk.mediumRisk}
                </p>
                <p className="text-xs text-muted-foreground">Medium Risk</p>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setShowRiskTable((v) => !v)}
            className="text-sm font-semibold text-primary hover:underline mb-4"
          >
            {showRiskTable ? "Hide details ▲" : "View at-risk applications ▼"}
          </button>

          {showRiskTable && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-xs text-muted-foreground uppercase tracking-wider">
                    <th className="py-2 text-left">Application</th>
                    <th className="py-2 text-left">Student</th>
                    <th className="py-2 text-left">Program</th>
                    <th className="py-2 text-left">Points</th>
                    <th className="py-2 text-left">Risk</th>
                    <th className="py-2 text-left">Status</th>
                    <th className="py-2 text-left">Factors</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {analytics.dropoutRisk.applications.map((a) => (
                    <tr key={a.applicationId} className="hover:bg-secondary/30">
                      <td className="py-2 font-mono text-xs">
                        {a.applicationNumber}
                      </td>
                      <td className="py-2">{a.studentName}</td>
                      <td className="py-2">
                        <span className="font-semibold">{a.programCode}</span>
                        <span className="text-muted-foreground ml-1 text-xs">
                          {a.program.length > 25
                            ? a.program.slice(0, 22) + "…"
                            : a.program}
                        </span>
                      </td>
                      <td className="py-2">
                        {a.totalPoints}
                        {a.minRequired ? (
                          <span className="text-muted-foreground">
                            /{a.minRequired}
                          </span>
                        ) : null}
                      </td>
                      <td className="py-2">
                        <Badge
                          variant={
                            a.riskLevel === "high" ? "danger" : "warning"
                          }
                          className="text-xs"
                        >
                          {a.riskLevel}
                        </Badge>
                      </td>
                      <td className="py-2">
                        <Badge variant="outline" className="text-xs capitalize">
                          {a.status.replace("_", " ")}
                        </Badge>
                      </td>
                      <td className="py-2 text-xs text-muted-foreground max-w-[200px]">
                        {a.riskFactors.join("; ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* ── Quick Actions ─────────────────────────────────────────────────── */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              href="/admin/admissions"
              className="flex items-center justify-between p-4 rounded-xl border border-border hover:border-primary hover:bg-primary/5 transition-all group"
            >
              <div>
                <div className="font-semibold text-primary">
                  Review Admissions
                </div>
                <p className="text-sm text-muted-foreground">
                  {pendingCount > 0
                    ? `${pendingCount} applications pending review`
                    : "No pending applications"}
                </p>
              </div>
              <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary" />
            </Link>
            <Link
              href="/admin/opportunities"
              className="flex items-center justify-between p-4 rounded-xl border border-border hover:border-accent hover:bg-accent/5 transition-all group"
            >
              <div>
                <div className="font-semibold text-accent-foreground">
                  Manage Jobs & Internships
                </div>
                <p className="text-sm text-muted-foreground">
                  {activeJobs} active opportunities posted
                </p>
              </div>
              <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-accent-foreground" />
            </Link>
          </div>
        </Card>

        {analytics && (
          <Card className="p-6">
            <h2 className="text-lg font-bold mb-4">Report Summary</h2>
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex justify-between">
                <span>Total applications</span>
                <span className="font-bold text-foreground">{total}</span>
              </div>
              <div className="flex justify-between">
                <span>Acceptance rate</span>
                <span className="font-bold text-foreground">
                  {total > 0
                    ? `${Math.round(((byStatus["accepted"] ?? 0) / total) * 100)}%`
                    : "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>At-risk students</span>
                <span
                  className={`font-bold ${
                    analytics.dropoutRisk.totalAtRisk > 0
                      ? "text-amber-600"
                      : "text-foreground"
                  }`}
                >
                  {analytics.dropoutRisk.totalAtRisk}
                </span>
              </div>
              <div className="flex justify-between">
                <span>NCHE compliant (points)</span>
                <span className="font-bold text-foreground">
                  {total > 0
                    ? `${Math.round(
                        (analytics.ncheCompliance.sufficientPoints / total) * 100
                      )}%`
                    : "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Local vs International</span>
                <span className="font-bold text-foreground">
                  {analytics.demographics.feeDistribution.local} :{" "}
                  {analytics.demographics.feeDistribution.international}
                </span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              Generated:{" "}
              {analytics.generatedAt
                ? new Date(analytics.generatedAt).toLocaleString()
                : "—"}
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
