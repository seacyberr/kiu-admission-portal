/**
 * Intercepts the global window.fetch to automatically append the 
 * Bearer token for all requests made by the generated Orval hooks.
 */
const originalFetch = window.fetch;

window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const token = localStorage.getItem('kiu_token');
  
  if (token) {
    const headers = new Headers(init?.headers);
    if (!headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    
    init = {
      ...init,
      headers
    };
  }

  const response = await originalFetch(input, init);

  // Handle global 401s — force logout on protected pages only
  const publicPaths = ['/', '/login', '/register', '/verify-otp'];
  const isPublicPage = publicPaths.some(p => window.location.pathname === p || window.location.pathname.startsWith(p + '/'));
  if (response.status === 401 && !isPublicPage && localStorage.getItem('kiu_token')) {
    localStorage.removeItem('kiu_token');
    localStorage.removeItem('kiu_user');
    window.location.href = '/login';
  }

  return response;
};

export {};
