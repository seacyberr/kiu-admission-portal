import { useState } from 'react';
import { useLocation } from 'wouter';

const RecommendationTool = () => {
  const [location, setLocation] = useLocation();
  const params = new URLSearchParams(location.split('?')[1] || '');
  const qualification = params.get('qualification') || 'alevel';

  const [formData, setFormData] = useState({
    ucePasses: '',
    uacePrincipalPasses: '0',
    uacePoints: '',
    subjects: [],
  });

  const [message, setMessage] = useState('');
  const [recommendations, setRecommendations] = useState<string[]>([]);

  const updateForm = (field: string, value: any) => setFormData(prev => ({ ...prev, [field]: value }));

  const checkEligibility = () => {
    let msg = '';
    let recs: string[] = [];

    switch (qualification) {
      case 'olevel':
        if (parseInt(formData.ucePasses) >= 5) {
          msg = "You meet NCHE requirements. You can apply for HEC and Diploma programmes.";
          recs = ["Higher Education Certificate (HEC)", "Diploma in Agribusiness Management", "Diploma in Social Work"];
        } else {
          msg = "You do not meet the NCHE minimum of 5 passes at UCE. Please improve your results or consider bridging options.";
        }
        break;

      case 'alevel':
        if (parseInt(formData.uacePrincipalPasses) >= 2) {
          msg = "You meet NCHE requirements for direct Degree entry.";
          recs = ["Bachelor of Business Administration", "Bachelor of Computer Science", "Bachelor of Nursing"];
        } else {
          msg = "You need at least 2 Principal Passes for Degree entry. You can still apply for Diploma or HEC.";
          recs = ["Diploma programmes", "Higher Education Certificate"];
        }
        break;

      case 'hec':
        msg = "You meet NCHE requirements. HEC holders can apply for Degree programmes.";
        recs = ["Bachelor of Business Administration", "Bachelor of Education"];
        break;

      case 'diploma':
        msg = "You meet NCHE requirements. Diploma holders can apply for Degree programmes with advanced standing.";
        recs = ["Bachelor of Business Administration (Year 2/3 entry)"];
        break;

      case 'degree':
        msg = "You meet NCHE requirements for Master's programmes.";
        recs = ["Master of Business Administration", "Master of Public Health"];
        break;

      case 'masters':
        msg = "You meet NCHE requirements for PhD programmes.";
        recs = ["PhD Programmes"];
        break;
    }

    setMessage(msg);
    setRecommendations(recs);
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-green-700 mb-2">Programme Recommendations</h1>
      <p className="text-gray-600 mb-8">Based on your highest qualification: <span className="font-semibold capitalize">{qualification}</span></p>

      <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 mb-10">
        <h3 className="font-semibold mb-3">NCHE Uganda Admission Rules</h3>
        <ul className="text-sm space-y-1 text-gray-700">
          <li>• O-Level: Minimum 5 passes → HEC or Diploma only</li>
          <li>• A-Level: Minimum 2 Principal Passes (same sitting) → Degree entry</li>
          <li>• HEC/Diploma: Credit or better → Degree with credit</li>
          <li>• Degree: 2nd Class Lower → Master's</li>
        </ul>
      </div>

      <div className="bg-white rounded-2xl shadow p-8">
        <h2 className="text-2xl font-semibold mb-6">Enter Your Details</h2>

        {qualification === 'olevel' && (
          <div className="mb-8">
            <label className="block font-medium mb-2">UCE Passes * (Minimum 5 required by NCHE)</label>
            <input 
              type="number" 
              value={formData.ucePasses} 
              onChange={(e) => updateForm('ucePasses', e.target.value)} 
              className="w-full p-4 border border-gray-300 rounded-xl" 
              placeholder="e.g. 7" 
            />
          </div>
        )}

        {qualification === 'alevel' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block font-medium mb-2">UACE Principal Passes *</label>
              <select 
                value={formData.uacePrincipalPasses} 
                onChange={(e) => updateForm('uacePrincipalPasses', e.target.value)} 
                className="w-full p-4 border border-gray-300 rounded-xl"
              >
                <option value="0">0</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3+</option>
              </select>
            </div>
            <div>
              <label className="block font-medium mb-2">UACE Points (optional)</label>
              <input 
                type="number" 
                value={formData.uacePoints} 
                onChange={(e) => updateForm('uacePoints', e.target.value)} 
                className="w-full p-4 border border-gray-300 rounded-xl" 
                placeholder="e.g. 15" 
              />
            </div>
          </div>
        )}

        <button 
          onClick={checkEligibility} 
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-medium text-lg"
        >
          Check Eligibility and Get Recommendations
        </button>

        {message && (
          <div className={`mt-10 p-6 rounded-2xl ${message.includes("do not meet") ? "bg-red-50 border border-red-200" : "bg-green-50 border border-green-200"}`}>
            <p className="text-lg font-medium">{message}</p>

            {recommendations.length > 0 && (
              <div className="mt-6 space-y-4">
                {recommendations.map((rec, i) => (
                  <div key={i} className="bg-white p-5 rounded-xl border border-gray-200 flex justify-between items-center">
                    <span>{rec}</span>
                    <button 
                      onClick={() => setLocation(`/apply/start?qualification=${qualification}&program=${encodeURIComponent(rec)}`)}
                      className="bg-green-700 text-white px-6 py-2 rounded-xl text-sm hover:bg-green-800"
                    >
                      Apply Now
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationTool;