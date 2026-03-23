import { Link } from 'wouter';
import { useGetFinalistProfile, useGetCurrentUser } from '@workspace/api-client-react';
import { Card, Button, Badge } from '@/components/ui/shared';
import { UserCircle, Briefcase, MapPin, Map, Award, Clock } from 'lucide-react';

export default function FinalistDashboard() {
  const { data: user } = useGetCurrentUser();
  const { data: profile, isLoading, error } = useGetFinalistProfile({ query: { retry: false } });

  if (isLoading) {
    return <div className="p-8 flex justify-center"><Clock className="animate-spin text-primary w-8 h-8" /></div>;
  }

  const needsProfile = !profile || error;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-primary">Finalist Career Portal</h1>
        <p className="text-muted-foreground mt-2">Welcome, {user?.firstName}. Prepare for your next big step.</p>
      </div>

      {needsProfile ? (
        <Card className="p-12 text-center border-dashed border-2 border-accent bg-accent/5">
          <div className="w-20 h-20 bg-accent/20 text-accent rounded-full flex items-center justify-center mx-auto mb-6">
            <UserCircle className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-bold mb-4 text-accent-foreground">Complete Your Profile</h2>
          <p className="text-muted-foreground max-w-md mx-auto mb-8">
            To get personalized career paths and apply for opportunities, we need to know your academic background.
          </p>
          <Link href="/career/profile">
            <Button variant="accent" size="lg" className="px-8 shadow-xl">Setup Profile Now</Button>
          </Link>
        </Card>
      ) : (
        <div className="grid md:grid-cols-3 gap-8">
          {/* Profile Summary */}
          <div className="md:col-span-1 space-y-6">
            <Card className="p-6 border-primary/20 shadow-md">
              <div className="text-center mb-6">
                <div className="w-24 h-24 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-white shadow-sm">
                  <span className="text-3xl font-display font-bold">{user?.firstName?.[0]}{user?.lastName?.[0]}</span>
                </div>
                <h2 className="text-xl font-bold">{user?.firstName} {user?.lastName}</h2>
                <p className="text-sm text-muted-foreground">{profile.studentNumber}</p>
              </div>
              <div className="space-y-4 pt-4 border-t border-border text-sm">
                <div>
                  <p className="text-muted-foreground font-semibold">Program</p>
                  <p className="font-medium text-foreground">{profile.program?.name || 'N/A'}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-muted-foreground font-semibold">GPA</p>
                    <p className="font-bold text-primary text-lg">{profile.gpa || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground font-semibold">Grad Year</p>
                    <p className="font-bold text-foreground text-lg">{profile.graduationYear}</p>
                  </div>
                </div>
                <div>
                  <p className="text-muted-foreground font-semibold mb-2">Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills?.map(skill => (
                      <Badge key={skill} variant="outline">{skill}</Badge>
                    ))}
                  </div>
                </div>
              </div>
              <Link href="/career/profile">
                <Button variant="outline" className="w-full mt-6">Edit Profile</Button>
              </Link>
            </Card>
          </div>

          {/* Actions */}
          <div className="md:col-span-2 space-y-6">
            <Link href="/career/paths">
              <Card className="p-8 bg-gradient-to-r from-primary to-primary/90 text-primary-foreground hover:shadow-xl hover:-translate-y-1 transition-all cursor-pointer border-none relative overflow-hidden group">
                <div className="absolute right-0 top-0 w-64 h-64 bg-white/5 rounded-full blur-3xl group-hover:bg-white/10 transition-colors"></div>
                <div className="flex items-center gap-6 relative z-10">
                  <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center shrink-0">
                    <Map className="w-8 h-8" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Explore Career Paths</h3>
                    <p className="text-primary-foreground/80">Discover tailored career recommendations based on your degree.</p>
                  </div>
                </div>
              </Card>
            </Link>

            <Link href="/career/opportunities">
              <Card className="p-8 bg-card border-accent/40 shadow-lg shadow-accent/5 hover:shadow-xl hover:border-accent hover:-translate-y-1 transition-all cursor-pointer">
                <div className="flex items-center gap-6">
                  <div className="w-16 h-16 bg-accent/20 text-accent-foreground rounded-2xl flex items-center justify-center shrink-0">
                    <Briefcase className="w-8 h-8" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold mb-2 text-foreground">Jobs & Internships</h3>
                    <p className="text-muted-foreground">Apply directly for premium graduate roles and internships.</p>
                  </div>
                </div>
              </Card>
            </Link>

            <Link href="/career/applications">
              <Card className="p-8 bg-card hover:bg-secondary/30 transition-colors cursor-pointer">
                <div className="flex items-center gap-6">
                  <div className="w-16 h-16 bg-secondary text-primary rounded-2xl flex items-center justify-center shrink-0">
                    <Award className="w-8 h-8" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-1">My Applications</h3>
                    <p className="text-muted-foreground">Track the status of your submitted job applications.</p>
                  </div>
                </div>
              </Card>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
