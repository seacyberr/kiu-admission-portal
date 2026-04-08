import { useLocation } from 'wouter';

const CertificateDetails = () => {
  const [location, setLocation] = useLocation();
  const params = new URLSearchParams(location.split('?')[1] || '');
  const qualification = params.get('qualification') || 'alevel';
  const selectedProgram = params.get('program') || '';

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-green-700 mb-8">Certificate Details</h1>
      <div className="bg-white rounded-2xl shadow p-8">
        <p className="mb-6">Programme: <span className="font-semibold">{selectedProgram}</span></p>

        <h2 className="text-xl font-semibold mb-6">Upload Your Academic Documents</h2>
        <div className="space-y-8">
          <div>
            <label className="block font-medium mb-2">O-Level / UCE Certificate</label>
            <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" />
          </div>
          <div>
            <label className="block font-medium mb-2">A-Level / UACE Certificate (if applicable)</label>
            <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" />
          </div>
          <div>
            <label className="block font-medium mb-2">Diploma / Degree Transcript</label>
            <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" />
          </div>
        </div>

        <div className="mt-12 flex justify-between">
          <button onClick={() => window.history.back()} className="px-8 py-4 border border-gray-300 rounded-xl">Back</button>
          <button 
            onClick={() => setLocation(`/apply/personal-info?qualification=${qualification}&program=${encodeURIComponent(selectedProgram)}`)}
            className="bg-green-700 text-white px-10 py-4 rounded-xl"
          >
            Next: Personal Information
          </button>
        </div>
      </div>
    </div>
  );
};

export default CertificateDetails;