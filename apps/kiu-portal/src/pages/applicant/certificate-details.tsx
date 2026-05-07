import { useLocation } from 'wouter';

const CertificateDetails = () => {
  const [location, setLocation] = useLocation();
  const params = new URLSearchParams(location.split('?')[1] || '');
  const qualification = params.get('qualification') || 'alevel';
  const selectedProgram = params.get('program') || '';

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="grid grid-cols-3 gap-8">
        <div className="col-span-2">
          <h1 className="text-3xl font-bold text-green-700 mb-8">Certificate Details</h1>
          <div className="bg-white rounded-2xl shadow p-8">
            <p className="mb-6">Programme: <span className="font-semibold">{selectedProgram}</span></p>

            <h2 className="text-xl font-semibold mb-6">Upload Your Academic Documents</h2>
            <div className="space-y-6">
              {['o_level', 'a_level', 'diploma', 'hec', 'national_cert'].includes(qualification) && (
                <div>
                  <label className="block font-medium mb-2">O-Level / UCE Certificate</label>
                  <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" />
                </div>
              )}
              
              {qualification === 'a_level' && (
                <div>
                  <label className="block font-medium mb-2">A-Level / UACE Certificate</label>
                  <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" />
                </div>
              )}
              
              {qualification === 'diploma' && (
                <div>
                  <label className="block font-medium mb-2">Diploma Certificate & Transcript</label>
                  <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" multiple />
                </div>
              )}
              
              {qualification === 'national_cert' && (
                <div>
                  <label className="block font-medium mb-2">National Certificate</label>
                  <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" />
                </div>
              )}
              
              {qualification === 'bachelors' && (
                <div>
                  <label className="block font-medium mb-2">Bachelors Degree Certificate & Transcript</label>
                  <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" multiple />
                </div>
              )}
              
              {qualification === 'masters' && (
                <div>
                  <label className="block font-medium mb-2">Masters Degree Certificate & Transcript</label>
                  <input type="file" className="w-full p-4 border border-gray-300 rounded-xl" multiple />
                </div>
              )}
            </div>

            <div className="mt-10 flex justify-between">
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
        
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
            <h3 className="font-semibold text-blue-800 mb-3">Requirements</h3>
            <ul className="text-sm text-blue-700 space-y-2">
              <li>• All documents must be clear scanned copies</li>
              <li>• Accepted formats: PDF, JPG, PNG</li>
              <li>• Maximum file size: 5MB per file</li>
              <li>• Certificates must show all details clearly</li>
            </ul>
          </div>
          
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
            <h3 className="font-semibold text-gray-800 mb-3">Tips</h3>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>• Scan in colour for best results</li>
              <li>• Ensure all four corners are visible</li>
              <li>• Avoid glare or shadows on documents</li>
            </ul>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-xl p-5">
            <h3 className="font-semibold text-green-800 mb-3">Contact: Need Help?</h3>
            <p className="text-sm text-green-700">
              Contact Admissions Office<br/>
              <strong>+256-760-502660</strong><br/>
              admissions@kiu.ac.ug
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CertificateDetails;