import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ApplicationData } from "./index";

interface ReviewSubmitProps {
  data: ApplicationData;
  onBack: () => void;
  onSubmit: () => void;
  onEdit?: (step: number) => void;
}

const ReviewSubmit = ({ data, onBack, onSubmit, onEdit }: ReviewSubmitProps) => {
  const handleSubmit = () => {
    toast.success("Application submitted successfully!");
    onSubmit();
  };

  const getProgramName = () => {
    return data.program?.firstChoice || "Not selected";
  };

  const getQualificationType = () => {
    return data.education?.qualificationType || "Not specified";
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-green-700 mb-6">Review & Submit</h1>
      
      <Card className="p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Application Summary</h2>
        
        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Programme Applied For:</span>
            <span className="font-semibold">{getProgramName()}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Qualification Type:</span>
            <span className="font-semibold capitalize">{getQualificationType()}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Documents Uploaded:</span>
            <span className="font-semibold text-green-700">
              {data.documents?.files ? Object.keys(data.documents.files).length : 0} Documents
            </span>
          </div>
        </div>
      </Card>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <p className="text-yellow-800 text-sm">
          By clicking Submit Application, you confirm that all information provided is accurate and complete. 
          You understand that providing false information may result in immediate disqualification.
        </p>
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={onBack}>
          Back
        </Button>
        <Button 
          onClick={handleSubmit}
          className="bg-green-700 hover:bg-green-800"
        >
          Submit Application
        </Button>
      </div>
    </div>
  );
};

export default ReviewSubmit;
