import { useState } from 'react';
import { useListOpportunities, useApplyForOpportunity } from '@workspace/api-client-react';
import { Card, Button, Badge, Input, Textarea, Label } from '@/components/ui/shared';
import { Link } from 'wouter';
import { ArrowLeft, Briefcase, MapPin, Clock, Building2 } from 'lucide-react';
import { format } from 'date-fns';
import { useToast } from '@/hooks/use-toast';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const applySchema = z.object({
  coverLetter: z.string().min(50, "Cover letter must be at least 50 characters"),
  cvUrl: z.string().url("Must be a valid URL").optional().or(z.literal('')),
});

type ApplyForm = z.infer<typeof applySchema>;

export default function Opportunities() {
  const [filterType, setFilterType] = useState<string>('');
  const { data, isLoading } = useListOpportunities(filterType ? { type: filterType as any } : {});
  const [selectedOp, setSelectedOp] = useState<number | null>(null);
  const { toast } = useToast();
  const applyMutation = useApplyForOpportunity();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<ApplyForm>({
    resolver: zodResolver(applySchema)
  });

  const onSubmit = (formData: ApplyForm) => {
    if (!selectedOp) return;
    
    applyMutation.mutate({ id: selectedOp, data: formData }, {
      onSuccess: () => {
        toast({ title: "Application Submitted!", description: "Best of luck!" });
        setSelectedOp(null);
        reset();
      },
      onError: (err: any) => {
        toast({ title: "Failed to apply", description: err.message, variant: "destructive" });
      }
    });
  };

  if (isLoading) return <div className="p-12 flex justify-center"><Clock className="animate-spin text-primary w-8 h-8" /></div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative">
      <div className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <Link href="/career" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
          </Link>
          <h1 className="text-3xl font-display font-bold text-primary">Job Board</h1>
          <p className="text-muted-foreground mt-2">Exclusive jobs and internships for KIU Finalists.</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant={filterType === '' ? 'primary' : 'outline'} onClick={() => setFilterType('')}>All</Button>
          <Button variant={filterType === 'job' ? 'primary' : 'outline'} onClick={() => setFilterType('job')}>Jobs</Button>
          <Button variant={filterType === 'internship' ? 'primary' : 'outline'} onClick={() => setFilterType('internship')}>Internships</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.opportunities?.map((op) => (
          <Card key={op.id} className="flex flex-col hover:border-primary/50 transition-colors">
            <div className="p-6 flex-1">
              <div className="flex justify-between items-start mb-4">
                <Badge variant={op.type === 'job' ? 'default' : 'warning'} className="capitalize">{op.type}</Badge>
                {op.isActive ? (
                  <span className="text-xs font-semibold text-success bg-success/10 px-2 py-1 rounded-md">Active</span>
                ) : (
                  <span className="text-xs font-semibold text-destructive bg-destructive/10 px-2 py-1 rounded-md">Closed</span>
                )}
              </div>
              <h3 className="text-xl font-bold mb-1 line-clamp-2">{op.title}</h3>
              <p className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Building2 className="w-4 h-4" /> {op.organization}
              </p>
              
              <div className="space-y-2 text-sm text-muted-foreground mb-6">
                {op.location && (
                  <p className="flex items-center gap-2"><MapPin className="w-4 h-4" /> {op.location}</p>
                )}
                <p className="flex items-center gap-2">
                  <Clock className="w-4 h-4" /> Deadline: {format(new Date(op.applicationDeadline), 'MMM d, yyyy')}
                </p>
              </div>
              
              <p className="text-sm line-clamp-3 text-foreground/80">{op.description}</p>
            </div>
            <div className="p-6 pt-0 mt-auto">
              <Button 
                variant="accent" 
                className="w-full" 
                disabled={!op.isActive}
                onClick={() => setSelectedOp(op.id)}
              >
                Apply Now
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Apply Modal */}
      {selectedOp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-8 relative animate-in zoom-in-95">
            <h2 className="text-2xl font-bold mb-6 text-primary">Submit Application</h2>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-2">
                <Label>Cover Letter</Label>
                <Textarea 
                  placeholder="Introduce yourself and explain why you're a great fit..."
                  className="h-48"
                  {...register("coverLetter")}
                />
                {errors.coverLetter && <p className="text-xs text-destructive">{errors.coverLetter.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>CV / Resume Link</Label>
                <Input placeholder="https://drive.google.com/..." {...register("cvUrl")} />
                {errors.cvUrl && <p className="text-xs text-destructive">{errors.cvUrl.message}</p>}
                <p className="text-xs text-muted-foreground">Provide a viewable link to your resume (Google Drive, Dropbox, etc.)</p>
              </div>
              
              <div className="flex justify-end gap-4 pt-4 border-t border-border">
                <Button type="button" variant="ghost" onClick={() => setSelectedOp(null)}>Cancel</Button>
                <Button type="submit" isLoading={applyMutation.isPending}>Send Application</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
