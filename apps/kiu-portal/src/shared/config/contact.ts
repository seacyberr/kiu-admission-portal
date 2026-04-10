/**
 * KIU University Contact Information
 * 
 * Source: Official KIU Publications
 * - Local Main Campus Brochure August 2025
 * - International Main Campus Brochure January 2025
 * 
 * Last Verified: April 2026
 */

export const KIU_CONTACT = {
  // University Name
  fullName: "Kampala International University",
  shortName: "KIU",
  tagline: "The Leading Private University in Uganda",
  
  // Main Contact Details
  email: "admissions@kiu.ac.ug",
  phone: "+256 414 100808",
  website: "https://www.kiu.ac.ug",
  
  // Addresses
  mainCampus: {
    name: "Main Campus",
    address: "Kansanga, Kampala",
    city: "Kampala",
    country: "Uganda",
    location: "Kansanga, Kampala, Uganda"
  },
  westernCampus: {
    name: "Western Campus",
    address: "Ishaka, Bushenyi District",
    city: "Bushenyi",
    country: "Uganda",
    location: "Ishaka, Bushenyi District, Uganda"
  },
  
  // Postal Address
  poBox: "Kampala",
  postalAddress: "P.O. BOX, Kampala - Uganda",
  
  // Contact Person
  directorOfAdmissions: "THE DIRECTOR OF ADMISSIONS",
} as const;

// Helper function to format contact info for display
export const formatContact = (type: 'short' | 'full' | 'inline' = 'short'): string => {
  switch (type) {
    case 'short':
      return `${KIU_CONTACT.phone}`;
    case 'full':
      return `${KIU_CONTACT.fullName}\n${KIU_CONTACT.mainCampus.location}\nTel: ${KIU_CONTACT.phone}\nEmail: ${KIU_CONTACT.email}\nWebsite: ${KIU_CONTACT.website}`;
    case 'inline':
      return `${KIU_CONTACT.mainCampus.location} | ${KIU_CONTACT.phone} | ${KIU_CONTACT.email}`;
    default:
      return KIU_CONTACT.phone;
  }
};

// Export individual values for convenience
export const {
  email: KIU_EMAIL,
  phone: KIU_PHONE,
  website: KIU_WEBSITE,
  mainCampus: KIU_MAIN_CAMPUS,
  westernCampus: KIU_WESTERN_CAMPUS
} = KIU_CONTACT;
