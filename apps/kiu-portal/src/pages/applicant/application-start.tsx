import { useLocation } from 'wouter';

const ApplicationStart = () => {
  const [location, setLocation] = useLocation();
  const params = new URLSearchParams(location.split('?')[1] || '');
  const qualification = params.get('qualification') || 'alevel';
  const selectedProgram = params.get('program') || '';

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold text-green-700 mb-8">Application Started</h1>
      <div className="bg-white rounded-2xl shadow p-8">
        <p className="mb-6">Programme: <span className="font-semibold">{selectedProgram}</span></p>
        <p className="mb-8">Qualification: <span className="capitalize">{qualification}</span></p>

        <div className="mt-10 flex justify-between">
          <button onClick={() => window.history.back()} className="px-8 py-4 border border-gray-300 rounded-xl">Back</button>
          <button 
            onClick={() => setLocation(`/apply/certificate-details?qualification=${qualification}&program=${encodeURIComponent(selectedProgram)}`)}
            className="bg-green-700 text-white px-10 py-4 rounded-xl"
          >
            Continue to Certificate Details →
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApplicationStart;