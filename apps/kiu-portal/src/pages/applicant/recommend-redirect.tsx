/**
 * Legacy recommendation page - redirects to new NCHE-based system
 * 
 * This page redirects to the new NCHE Uganda compliant recommendation system
 * which provides official standards-based assessments with direct applications.
 */

import { useEffect } from "react";
import { useLocation } from "wouter";

export default function RecommendRedirect() {
  const [, setLocation] = useLocation();
  
  useEffect(() => {
    // Redirect to the new NCHE-based recommendation system
    setLocation("/nche-recommend");
  }, [setLocation]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirecting to NCHE Assessment System...</p>
      </div>
    </div>
  );
}
