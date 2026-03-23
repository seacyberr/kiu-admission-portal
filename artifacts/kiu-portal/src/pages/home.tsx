import { Link } from 'wouter';
import { Button } from '@/components/ui/shared';
import { motion } from 'framer-motion';
import { ArrowRight, GraduationCap, Briefcase, BookOpen, ChevronRight, Award, LineChart } from 'lucide-react';

export default function Home() {
  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="relative w-full h-[85vh] min-h-[600px] flex items-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src={`${import.meta.env.BASE_URL}images/hero-bg.png`} 
            alt="KIU Campus" 
            className="w-full h-full object-cover scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-primary/95 via-primary/80 to-transparent"></div>
          <div className="absolute inset-0 bg-black/20"></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="max-w-3xl space-y-8"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/20 backdrop-blur-md border border-accent/30 text-accent font-semibold text-sm">
              <Award className="w-4 h-4" />
              <span>Excellence in Higher Education</span>
            </div>
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold text-white leading-[1.1]">
              Shape Your Future at <span className="text-accent">KIU</span>
            </h1>
            <p className="text-lg md:text-xl text-white/80 max-w-2xl leading-relaxed">
              Welcome to the unified portal for Kampala International University. Whether you're applying as a new student or seeking career opportunities as a graduating finalist, your journey starts here.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Link href="/register">
                <Button variant="accent" size="lg" className="w-full sm:w-auto gap-2 text-base shadow-xl shadow-accent/20">
                  <GraduationCap className="w-5 h-5" />
                  Apply for Admission
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg" className="w-full sm:w-auto gap-2 text-white border-white/30 hover:bg-white/10 hover:text-white backdrop-blur-sm text-base">
                  <Briefcase className="w-5 h-5" />
                  Finalist Career Portal
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
        
        {/* Decorative Wave */}
        <div className="absolute bottom-0 inset-x-0 h-16 bg-gradient-to-t from-background to-transparent z-20"></div>
      </section>

      {/* Features Split */}
      <section className="py-24 bg-background relative z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">One Portal, Two Pathways</h2>
            <p className="text-muted-foreground text-lg">We support our students from the day they apply until the day they launch their careers.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 lg:gap-12">
            {/* Admissions Card */}
            <motion.div 
              whileHover={{ y: -8 }}
              className="bg-card rounded-3xl p-8 border border-border shadow-xl shadow-primary/5 relative overflow-hidden group"
            >
              <div className="absolute top-0 right-0 -mr-8 -mt-8 w-40 h-40 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-colors"></div>
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 text-primary">
                <BookOpen className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold mb-3">New Admissions</h3>
              <p className="text-muted-foreground mb-8">
                Seamlessly apply for Undergraduate and Diploma programs. Track your application status, submit your UNEB grades, and manage your admission process.
              </p>
              <ul className="space-y-3 mb-8">
                {['O-Level (UCE) & A-Level (UACE) Integration', 'Real-time Application Tracking', 'Secure Document Uploads'].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm font-medium">
                    <div className="w-5 h-5 rounded-full bg-accent/20 text-accent flex items-center justify-center shrink-0">
                      <ChevronRight className="w-3 h-3" />
                    </div>
                    {item}
                  </li>
                ))}
              </ul>
              <Link href="/register">
                <Button variant="outline" className="w-full group/btn">
                  Start Application <ArrowRight className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </motion.div>

            {/* Careers Card */}
            <motion.div 
              whileHover={{ y: -8 }}
              className="bg-primary rounded-3xl p-8 border border-primary-light shadow-xl shadow-primary/20 relative overflow-hidden group text-white"
            >
              <div className="absolute top-0 right-0 -mr-8 -mt-8 w-40 h-40 bg-accent/20 rounded-full blur-3xl group-hover:bg-accent/30 transition-colors"></div>
              <div className="w-16 h-16 rounded-2xl bg-accent flex items-center justify-center mb-6 text-primary">
                <LineChart className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold mb-3 text-white">Finalist Careers</h3>
              <p className="text-primary-foreground/80 mb-8">
                Exclusive to final-year degree and diploma students. Get personalized career path recommendations and apply directly for premium internships and graduate jobs.
              </p>
              <ul className="space-y-3 mb-8">
                {['AI-driven Career Path Matching', 'Exclusive Job & Internship Board', 'Direct Employer Applications'].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm font-medium text-white">
                    <div className="w-5 h-5 rounded-full bg-accent text-primary flex items-center justify-center shrink-0">
                      <ChevronRight className="w-3 h-3" />
                    </div>
                    {item}
                  </li>
                ))}
              </ul>
              <Link href="/login">
                <Button variant="accent" className="w-full group/btn text-primary">
                  Access Career Portal <ArrowRight className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
}
