/**
 * Asset Configuration - Optimized Image References
 * 
 * Instead of storing large image files in the repo, we use:
 * 1. Unsplash source URLs for high-quality stock photos
 * 2. Data URIs for small icons/placeholders
 * 3. References to external CDN for production assets
 * 
 * This keeps the repository size small while maintaining professional appearance.
 */

export const ASSETS = {
  // Hero & Campus Images (High-quality Unsplash)
  campus: {
    main: 'https://images.unsplash.com/photo-1562774053-701939374585?w=1920&q=80',
    library: 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1200&q=80',
    students: 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1200&q=80',
    graduation: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1200&q=80',
    lecture: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=1200&q=80',
  },
  
  // Program Category Images
  programs: {
    health: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80',
    business: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80',
    computing: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80',
    law: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80',
    education: 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80',
    engineering: 'https://images.unsplash.com/photo-1581092921461-eab62e97a782?w=800&q=80',
    agriculture: 'https://images.unsplash.com/photo-1500937386664-56b1ec8ff621?w=800&q=80',
  },
  
  // Student Life
  students: {
    studying: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600&q=80',
    group: 'https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=600&q=80',
    graduate: 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=600&q=80',
    diverse: 'https://images.unsplash.com/photo-1525921429624-479b6a26d84d?w=600&q=80',
  },
  
  // Icons (SVG data URIs for zero HTTP requests)
  icons: {
    logo: '/images/logo.png', // Keep existing logo
    placeholder: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjFmNWY5Ii8+PHN2ZyB4PSI1MCUiIHk9IjUwJSIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHRyYW5zZm9ybT0idHJhbnNsYXRlKC0xMiwgLTEyKSIgZmlsbD0iIzk0YTNiOCI+PHBhdGggZD0iTTIxIDE5VjVjMC0xLjEtLjktMi0yLTJINWMtMS4xIDAtMiAuOS0yIDJ2MTRjMCAxLjEuOSAyIDIgMmgxNGMxLjEgMCAyLS45IDItMnpNOC41IDEzLjVsMi41IDMuMDFMMTQuNSAxMmw1IDVWN2wtNS41IDUuNUw4LjUgMTMuNXoiLz48L3N2Zz4=',
    user: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMTJDMTEuMTc1IDEyIDEwLjQyOSA1IDkuNzUgNUM5LjA3MSA1IDguMzI2IDEyIDcuNSAxMkM2LjY3NCAxMiA2IDExLjMyNiA2IDEwLjVDNiA5LjY3NCA2LjY3NCA5IDcuNSA5QzguMzI2IDkgOS4wNzEgMTYgOS43NSAxNkMxMC40MjkgMTYgMTEuMTc1IDkgMTIgOUMxMi44MjUgOSAxMy41NzEgMTYgMTQuMjUgMTZDMTQuOTI5IDE2IDE1LjY3NCA5IDE2LjUgOUMxNy4zMjYgOSAxOCA5LjY3NCAxOCAxMC41QzE4IDExLjMyNiAxNy4zMjYgMTIgMTYuNSAxMkMxNS42NzQgMTIgMTQuOTI5IDUgMTQuMjUgNUMxMy41NzEgNSAxMi44MjUgMTIgMTIgMTJaIiBzdHJva2U9IiM2NDc0OEIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PGNpcmNsZSBjeD0iMTIiIGN5PSI4IiByPSI0IiBzdHJva2U9IiM2NDc0OEIiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg==',
  }
} as const;

// Helper to get optimized image URL with size
export const getImageUrl = (
  category: keyof typeof ASSETS.campus | keyof typeof ASSETS.programs | keyof typeof ASSETS.students,
  subcategory: string,
  width?: number,
  height?: number
): string => {
  const categoryMap: Record<string, Record<string, string>> = {
    campus: ASSETS.campus,
    programs: ASSETS.programs,
    students: ASSETS.students,
  };
  
  const url = categoryMap[category]?.[subcategory] || ASSETS.icons.placeholder;
  
  // Add size parameters for Unsplash images
  if (url.includes('unsplash.com') && width) {
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}w=${width}${height ? `&h=${height}&fit=crop` : ''}`;
  }
  
  return url;
};

// Export individual categories for convenience
export const { campus, programs, students, icons } = ASSETS;
