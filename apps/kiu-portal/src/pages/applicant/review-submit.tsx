import { useLocation } from 'wouter';
import { useToast } from "@/hooks/use-toast";

const ReviewSubmit = () => {
  const [location, setLocation] = useLocation();
  const { toast } = useToast();
  const params = new URLSearchParams(location.split('?')[1] || '');
  const qualification = params.get('qualification') || 'alevel';
  const selectedProgram = params.get('program') || '';

  const handleSubmit = () => {
    toast({
      title: "Application Submitted",
      description: "Your application has been successfully submitted. You will receive a confirmation email shortly.",
    });
    
    setTimeout(() => {
      setLocation('/dashboard');
    }, 2000);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-green-700 mb-8">Review & Submit</h1>
      
      <div className="bg-white rounded-2xl shadow p-8 mb-8">
        <h2 className="text-xl font-semibold mb-6">Application Summary</h2>
        
        <div className="space-y-4 mb-8">
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Programme Applied For:</span>
            <span className="font-semibold">{selectedProgram}</span>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Qualification Type:</span>
            <span className="font-semibold capitalize">{qualification}</span>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Documents Uploaded:</span>
            <span className="font-semibold text-green-700">3 Documents</span>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Application Fee:</span>
            <span className="font-semibold">UGX 50,000</span>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-8">
          <p className="text-yellow-800">
            By clicking Submit Application, you confirm that all information provided is accurate and complete. 
            You understand that providing false information may result in immediate disqualification.
          </p>
        </div>
      </div>

      <div className="flex justify-between">
        <button onClick={() => window.history.back()} className="px-8 py-4 border border-gray-300 rounded-xl">
          Back
        </button>
        <button 
          onClick={handleSubmit}
          className="bg-green-700 text-white px-10 py-4 rounded-xl font-semibold text-lg"
        >
          Submit Application
        </button>
      </div>
    </div>
  );
};

export default ReviewSubmit;