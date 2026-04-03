/**
 * new-applicant.tsx — Applicant Onboarding & Program Guidance
 *
 * Routes applicants to the correct application form based on their
 * highest education level.  For A-Level students who have 3 principal
 * passes, it now offers the Program Recommendation Tool BEFORE they
 * fill in the full application form, matching the proposal requirement:
 *
 *  "input their A-Level subject combinations… to receive personalized
 *   program recommendations, complete with entry requirements, fees,
 *   duration and career prospects."
 */

import { useMemo, useState } from 'react';
import { useLocation } from 'wouter';
import { Button, Card, Badge } from '@/components/ui/shared';
import {
  ArrowLeft,
  ArrowRight,
  GraduationCap,
  School,
  FileText,
  Sparkles,
  Award,
  BookOpen,
} from 'lucide-react';

type HighestEducation = 'o_level' | 'a_level' | 'diploma' | 'hec' | 'masters' | 'phd';
type YesNo = 'yes' | 'no';

function toDegreeApply(qualification: 'a_level' | 'diploma' | 'hec') {
  return `/apply/degree?qualification=${encodeURIComponent(qualification)}`;
}

export default function NewApplicant() {
  const [, setLocation] = useLocation();

  const [highest, setHighest] = useState<HighestEducation | null>(null);
  const [hasALevelCertificate, setHasALevelCertificate] = useState<YesNo | null>(null);
  const [hasThreePrincipalPasses, setHasThreePrincipalPasses] = useState<YesNo | null>(null);

  const reset = () => {
    setHighest(null);
    setHasALevelCertificate(null);
    setHasThreePrincipalPasses(null);
  };

  const heading = useMemo(() => {
    if (!highest) return 'New Applicant Guidance';
    switch (highest) {
      case 'o_level':    return 'O-Level Path (UCE)';
      case 'a_level':    return 'A-Level Path (UACE)';
      case 'diploma':    return 'Diploma Holder → Degree';
      case 'hec':        return 'HEC Holder → Degree';
      default:           return 'New Applicant Guidance';
    }
  }, [highest]);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <button
          onClick={() => (highest ? reset() : setLocation('/dashboard'))}
          className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {highest ? 'Back to choices' : 'Back to Dashboard'}
        </button>
        <h1 className="text-3xl font-display font-bold text-primary">{heading}</h1>
        <p className="text-muted-foreground mt-2">
          Choose your highest education first. You will then be guided to the correct KIU application.
        </p>
      </div>

      <div className="space-y-6">

        {/* ── Step 1: Choose highest education ────────────────────────────── */}
        {!highest && (
          <Card className="p-8">
            <div className="flex items-center gap-3 mb-6">
              <Sparkles className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-bold">Select Your Highest Education</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                {
                  key: 'o_level' as HighestEducation,
                  icon: School,
                  label: 'O-Level (UCE)',
                  sub: 'Apply for HEC or Diploma',
                },
                {
                  key: 'a_level' as HighestEducation,
                  icon: GraduationCap,
                  label: 'A-Level (UACE)',
                  sub: 'Answer 2 quick questions',
                },
                {
                  key: 'diploma' as HighestEducation,
                  icon: FileText,
                  label: 'DIPLOMA',
                  sub: 'Apply for Degree',
                },
                {
                  key: 'hec' as HighestEducation,
                  icon: FileText,
                  label: 'HEC',
                  sub: 'Apply for Degree',
                },
                {
                  key: 'masters' as HighestEducation,
                  icon: Award,
                  label: "Master's Degree",
                  sub: "Bachelor's degree holder",
                },
                {
                  key: 'phd' as HighestEducation,
                  icon: BookOpen,
                  label: 'PhD',
                  sub: "Master's degree holder",
                },
              ].map(({ key, icon: Icon, label, sub }) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setHighest(key)}
                  className="text-left p-5 rounded-2xl border-2 border-border hover:border-primary/40 hover:bg-primary/5 transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-6 h-6 text-primary shrink-0" />
                    <div>
                      <div className="font-bold">{label}</div>
                      <div className="text-xs text-muted-foreground mt-1">{sub}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </Card>
        )}

        {/* ── O-Level ─────────────────────────────────────────────────────── */}
        {highest === 'o_level' && (
          <Card className="p-8">
            <div className="flex items-center justify-between gap-3 mb-6">
              <div className="space-y-1">
                <h2 className="text-lg font-bold">For O-Level applicants</h2>
                <p className="text-muted-foreground text-sm">
                  You should apply to Diploma or Higher Education Certificate (HEC).
                </p>
              </div>
              <Badge className="bg-primary/10 text-primary border-primary/20">
                No degree at O-Level
              </Badge>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Card className="p-5 border-border bg-secondary/20">
                <div className="flex items-start gap-3">
                  <GraduationCap className="w-6 h-6 text-primary mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-bold">Apply for Diploma</h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      Foundation for degree (specific course later).
                    </p>
                    <Button
                      className="mt-4 w-full"
                      onClick={() => setLocation('/apply/diploma')}
                      variant="accent"
                    >
                      Continue to Diploma
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
              </Card>

              <Card className="p-5 border-border bg-secondary/20">
                <div className="flex items-start gap-3">
                  <GraduationCap className="w-6 h-6 text-primary mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-bold">Apply for HEC</h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      Compensates for missing/weak A-Level.
                    </p>
                    <Button
                      className="mt-4 w-full"
                      onClick={() => setLocation('/apply/hec')}
                      variant="accent"
                    >
                      Continue to HEC
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </Card>
        )}

        {/* ── A-Level ─────────────────────────────────────────────────────── */}
        {highest === 'a_level' && (
          <Card className="p-8">
            <h2 className="text-lg font-bold mb-2">For A-Level applicants</h2>
            <p className="text-muted-foreground text-sm mb-6">
              KIU uses your A-Level results and principal pass count to decide the correct
              application platform.
            </p>

            {/* Q1: Do you have A-Level results? */}
            {!hasALevelCertificate && (
              <div className="space-y-4">
                <h3 className="font-bold">Do you have A-Level results/certificate?</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Button variant="accent" onClick={() => setHasALevelCertificate('yes')}>
                    Yes
                  </Button>
                  <Button variant="outline" onClick={() => setHasALevelCertificate('no')}>
                    No
                  </Button>
                </div>
              </div>
            )}

            {hasALevelCertificate === 'no' && (
              <div className="space-y-4">
                <div className="bg-blue-50 p-4 rounded-xl text-sm">
                  <p className="font-semibold text-blue-800">No A-Level certificate</p>
                  <p className="text-blue-700 mt-1">You should apply to Diploma or HEC.</p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Button className="w-full" variant="accent" onClick={() => setLocation('/apply/diploma')}>
                    Apply Diploma <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                  <Button className="w-full" variant="accent" onClick={() => setLocation('/apply/hec')}>
                    Apply HEC <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </div>
            )}

            {/* Q2: Do you have at least 3 principal passes? */}
            {hasALevelCertificate === 'yes' && !hasThreePrincipalPasses && (
              <div className="space-y-4">
                <h3 className="font-bold">Do you have at least 3 principal passes?</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Button variant="accent" onClick={() => setHasThreePrincipalPasses('yes')}>
                    Yes (eligible for Degree)
                  </Button>
                  <Button variant="outline" onClick={() => setHasThreePrincipalPasses('no')}>
                    No (apply Diploma/HEC)
                  </Button>
                </div>
              </div>
            )}

            {hasThreePrincipalPasses === 'no' && (
              <div className="space-y-4">
                <div className="bg-blue-50 p-4 rounded-xl text-sm">
                  <p className="font-semibold text-blue-800">Less than 3 principal passes</p>
                  <p className="text-blue-700 mt-1">You should apply to Diploma or HEC.</p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Button className="w-full" variant="accent" onClick={() => setLocation('/apply/diploma')}>
                    Apply Diploma <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                  <Button className="w-full" variant="accent" onClick={() => setLocation('/apply/hec')}>
                    Apply HEC <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </div>
            )}

            {/* ── Eligible for Degree: offer Recommendation Tool first ────── */}
            {hasThreePrincipalPasses === 'yes' && (
              <div className="space-y-5">
                <div className="bg-green-50 p-4 rounded-xl text-sm">
                  <p className="font-semibold text-green-800">✓ Eligible for Degree</p>
                  <p className="text-green-700 mt-1">
                    You can apply for a Degree with A-Level (UACE). We recommend using the
                    Program Recommendation Tool first to find the best match for your subjects.
                  </p>
                </div>

                {/* ── PRIMARY CTA: Recommendation Tool ── */}
                <div className="p-5 rounded-2xl border-2 border-accent/40 bg-accent/5">
                  <div className="flex items-start gap-3 mb-4">
                    <div className="w-10 h-10 rounded-xl bg-accent/20 flex items-center justify-center shrink-0">
                      <Sparkles className="w-5 h-5 text-accent-foreground" />
                    </div>
                    <div>
                      <h3 className="font-bold text-base">
                        🎯 Get Personalised Program Recommendations
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Enter your A-Level subjects and grades. Our NCHE-compliant engine will
                        show you the programs that best match your combination — with fees,
                        entry requirements and career prospects.
                      </p>
                    </div>
                  </div>
                  <Button
                    className="w-full gap-2"
                    variant="accent"
                    onClick={() => setLocation('/recommend')}
                  >
                    <Sparkles className="w-4 h-4" />
                    Use Program Recommendation Tool
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>

                {/* ── Secondary: Apply directly ── */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-3 text-muted-foreground">
                      or apply directly
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <Button
                    className="w-full"
                    variant="accent"
                    onClick={() => setLocation(toDegreeApply('a_level'))}
                  >
                    Apply for Degree
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setLocation('/apply/diploma')}
                  >
                    Diploma Option
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setLocation('/apply/hec')}
                  >
                    HEC Option
                  </Button>
                </div>
              </div>
            )}
          </Card>
        )}

        {/* ── Diploma → Degree ─────────────────────────────────────────────── */}
        {highest === 'diploma' && (
          <Card className="p-8">
            <div className="bg-secondary/30 rounded-xl p-5 mb-6">
              <h2 className="text-lg font-bold">Diploma holder → Degree application</h2>
              <p className="text-muted-foreground text-sm mt-1">
                Your Diploma certificate qualifies you to apply for Degree programs.
              </p>
            </div>
            <Button className="w-full" variant="accent" onClick={() => setLocation(toDegreeApply('diploma'))}>
              Continue to Degree Application
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Card>
        )}

        {/* ── HEC → Degree ─────────────────────────────────────────────────── */}
        {highest === 'hec' && (
          <Card className="p-8">
            <div className="bg-secondary/30 rounded-xl p-5 mb-6">
              <h2 className="text-lg font-bold">HEC holder → Degree application</h2>
              <p className="text-muted-foreground text-sm mt-1">
                Your Higher Education Certificate (HEC) qualifies you to apply for Degree programs.
              </p>
            </div>
            <Button className="w-full" variant="accent" onClick={() => setLocation(toDegreeApply('hec'))}>
              Continue to Degree Application
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Card>
        )}

        {/* ── Masters ──────────────────────────────────────────────────────── */}
        {highest === 'masters' && (
          <Card className="p-8">
            <div className="bg-secondary/30 rounded-xl p-5 mb-6">
              <h2 className="text-lg font-bold">Master's Program Application</h2>
              <p className="text-muted-foreground text-sm mt-1">
                Apply for Master's degree programs at KIU. You will need to provide your
                Bachelor's degree information including university, degree title, graduation
                year, and GPA.
              </p>
            </div>
            <Button className="w-full" variant="accent" onClick={() => setLocation('/apply/masters')}>
              Continue to Master's Application
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Card>
        )}

        {/* ── PhD ──────────────────────────────────────────────────────────── */}
        {highest === 'phd' && (
          <Card className="p-8">
            <div className="bg-secondary/30 rounded-xl p-5 mb-6">
              <h2 className="text-lg font-bold">PhD Program Application</h2>
              <p className="text-muted-foreground text-sm mt-1">
                Apply for Doctoral (PhD) programs at KIU. You will need to provide your
                Master's degree information and a research proposal.
              </p>
            </div>
            <Button className="w-full" variant="accent" onClick={() => setLocation('/apply/phd')}>
              Continue to PhD Application
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
}
