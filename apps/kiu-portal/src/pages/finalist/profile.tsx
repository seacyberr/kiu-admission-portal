import { useState } from 'react';
import { useGetCurrentUser, useGetFinalistProfile, useUpdateFinalistProfile } from '@workspace/api-client-react';
import { Card, Button, Input, Textarea, Label } from '@/components/ui/shared';
import { ArrowLeft, Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Link } from 'wouter';
import { toast } from 'sonner';

export default function FinalistProfileEdit() {
  const { data: user } = useGetCurrentUser();
  const { data: profile } = useGetFinalistProfile({ query: { retry: false } });
  const updateProfile = useUpdateFinalistProfile();

  const [formData, setFormData] = useState({
    studentNumber: profile?.studentNumber || '',
    programId: profile?.programId || '',
    gpa: profile?.gpa || '',
    graduationYear: profile?.graduationYear || new Date().getFullYear(),
    skills: profile?.skills?.join(', ') || '',
    cvUrl: profile?.cvUrl || '',
  });

  const [cvFile, setCvFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 5 * 1024 * 1024) {
        toast.error('CV file must be less than 5MB');
        return;
      }
      setCvFile(file);
    }
  };

  const handleUpload = async () => {
    if (!cvFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('cv', cvFile);

    try {
      const response = await fetch('/api/v1/finalist/profile/upload-cv', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setFormData(prev => ({ ...prev, cvUrl: data.cvUrl }));
        toast.success('CV uploaded successfully');
      } else {
        toast.error('Failed to upload CV');
      }
    } catch (err) {
      toast.error('Failed to upload CV');
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    updateProfile.mutate({
      studentNumber: formData.studentNumber,
      programId: formData.programId ? parseInt(formData.programId) : undefined,
      gpa: formData.gpa ? parseFloat(formData.gpa) : undefined,
      graduationYear: formData.graduationYear,
      skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean),
      cvUrl: formData.cvUrl,
    }, {
      onSuccess: () => {
        toast.success('Profile updated successfully');
      },
      onError: () => {
        toast.error('Failed to update profile');
      }
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-10">
        <Link href="/career" className="inline-flex items-center text-sm font-semibold text-muted-foreground hover:text-primary mb-4 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
        </Link>
        <h1 className="text-3xl font-display font-bold text-primary">Edit Your Profile</h1>
        <p className="text-muted-foreground mt-2">Update your academic information and upload your CV</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <Card className="p-8">
          <h2 className="text-xl font-bold mb-6">Academic Information</h2>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="studentNumber">Student Number</Label>
              <Input
                id="studentNumber"
                value={formData.studentNumber}
                onChange={(e) => setFormData({ ...formData, studentNumber: e.target.value })}
                placeholder="Enter your student number"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="programId">Program ID</Label>
              <Input
                id="programId"
                value={formData.programId}
                onChange={(e) => setFormData({ ...formData, programId: e.target.value })}
                placeholder="Program ID"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gpa">GPA</Label>
              <Input
                id="gpa"
                type="number"
                step="0.01"
                min="0"
                max="4.0"
                value={formData.gpa}
                onChange={(e) => setFormData({ ...formData, gpa: e.target.value })}
                placeholder="Current GPA"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="graduationYear">Graduation Year</Label>
              <Input
                id="graduationYear"
                type="number"
                min={new Date().getFullYear()}
                value={formData.graduationYear}
                onChange={(e) => setFormData({ ...formData, graduationYear: parseInt(e.target.value) })}
                placeholder="Expected graduation year"
              />
            </div>
          </div>

          <div className="space-y-2 mt-6">
            <Label htmlFor="skills">Skills (comma separated)</Label>
            <Textarea
              id="skills"
              value={formData.skills}
              onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
              placeholder="JavaScript, Python, Project Management, ..."
              rows={3}
            />
          </div>
        </Card>

        <Card className="p-8">
          <h2 className="text-xl font-bold mb-6">CV Upload</h2>

          <div className="border-2 border-dashed border-border rounded-xl p-8 text-center">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />

            {formData.cvUrl ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center gap-2 text-success">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">CV uploaded successfully</span>
                </div>
                <Button variant="outline" type="button" onClick={() => setFormData({ ...formData, cvUrl: '' })}>
                  Replace CV
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-muted-foreground">Upload your CV (PDF, DOC, DOCX, max 5MB)</p>
                <Input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="max-w-xs mx-auto"
                />
                {cvFile && (
                  <div className="space-y-2">
                    <p className="text-sm text-foreground font-medium">Selected: {cvFile.name}</p>
                    <Button
                      type="button"
                      onClick={handleUpload}
                      disabled={uploading}
                    >
                      {uploading ? (
                        <>
                          <AlertCircle className="w-4 h-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          Upload CV
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>

        <div className="flex justify-end gap-4">
          <Link href="/career">
            <Button variant="outline" type="button">Cancel</Button>
          </Link>
          <Button type="submit" disabled={updateProfile.isPending}>
            {updateProfile.isPending ? 'Saving...' : 'Save Profile'}
          </Button>
        </div>
      </form>
    </div>
  );
}