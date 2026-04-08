import { useLocation } from 'wouter';

const PersonalInfo = () => {
  const [location, setLocation] = useLocation();
  const params = new URLSearchParams(location.split('?')[1] || '');
  const qualification = params.get('qualification') || 'alevel';
  const selectedProgram = params.get('program') || '';

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-green-700 mb-8">Personal Information</h1>
      <div className="bg-white rounded-2xl shadow p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block font-medium mb-2">Full Name</label>
            <input type="text" className="w-full p-4 border border-gray-300 rounded-xl" />
          </div>
          <div>
            <label className="block font-medium mb-2">Email Address</label>
            <input type="email" className="w-full p-4 border border-gray-300 rounded-xl" />
          </div>
          <div>
            <label className="block font-medium mb-2">Phone Number</label>
            <input type="tel" className="w-full p-4 border border-gray-300 rounded-xl" />
          </div>
          <div>
            <label className="block font-medium mb-2">Date of Birth</label>
            <input type="date" className="w-full p-4 border border-gray-300 rounded-xl" />
          </div>
        </div>

        <div className="mt-12 flex justify-between">
          <button onClick={() => window.history.back()} className="px-8 py-4 border border-gray-300 rounded-xl">Back</button>
          <button 
            onClick={() => setLocation(`/apply/review?qualification=${qualification}&program=${encodeURIComponent(selectedProgram)}`)}
            className="bg-green-700 text-white px-10 py-4 rounded-xl"
          >
            Next: Review & Submit
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonalInfo;