import { useListCareerPaths, useGetFinalistProfile } from '@workspace/api-client-react';
import { Card, Badge } from '@/components/ui/shared';
import { ArrowLeft, Award, Clock, Map, TrendingUp, Target, DollarSign } from 'lucide-react';
import { Link } from 'wouter';

export default function CareerPaths() {
  const { data: profile } = useGetFinalistProfile({ query: { retry: false } });
  
  // Pass program to get personalized paths
  const { data, isLoading } = useListCareerPaths({ program: profile?.program?.name });

  if (isLoading) {
    return <div className="p-12 flex justify-center"><Clock className="animate-spin text-primary w-8 h-8" /></div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-10">
        <Link href="/career" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
        </Link>
        <h1 className="text-3xl font-display font-bold text-primary flex items-center gap-3">
          <Map className="w-8 h-8 text-accent" /> Recommended Career Paths
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Based on your {profile?.program?.name || 'studies'}, here are potential directions for your career.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {data?.careerPaths?.map((path) => (
          <Card key={path.id} className="p-8 hover:shadow-xl transition-shadow flex flex-col h-full">
            <div className="flex-1">
              <Badge variant="default" className="mb-4">{path.industryField}</Badge>
              <h2 className="text-2xl font-bold mb-3">{path.title}</h2>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                {path.description}
              </p>
              
              <div className="space-y-4 mb-8">
                <div>
                  <h4 className="font-semibold text-sm flex items-center gap-2 mb-2 text-foreground">
                    <Target className="w-4 h-4 text-primary" /> Potential Roles
                  </h4>
                  <ul className="list-disc list-inside text-sm text-muted-foreground ml-6 space-y-1">
                    {path.potentialRoles.map((role, i) => <li key={i}>{role}</li>)}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold text-sm flex items-center gap-2 mb-2 text-foreground">
                    <Award className="w-4 h-4 text-accent" /> Key Skills Needed
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {path.skills.map((skill, i) => (
                      <Badge key={i} variant="outline" className="bg-secondary/50 text-xs">{skill}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-auto pt-6 border-t border-border grid grid-cols-2 gap-4 bg-background/50 -mx-8 -mb-8 p-6 rounded-b-2xl">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
                  <DollarSign className="w-3 h-3" /> Avg Salary
                </p>
                <p className="font-bold text-primary">{path.averageSalaryRange || 'Varies'}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" /> Outlook
                </p>
                <p className="font-bold text-success">{path.growthOutlook || 'Positive'}</p>
              </div>
            </div>
          </Card>
        ))}

        {!data?.careerPaths?.length && (
          <div className="col-span-2 text-center py-12 bg-secondary/20 rounded-2xl border-2 border-dashed">
            <p className="text-muted-foreground">No specific career paths mapped for your program yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
