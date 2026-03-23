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

  // Handle global 401s to force logout — but NOT on public pages
  const publicPaths = ['/', '/login', '/register'];
  const isPublicPage = publicPaths.includes(window.location.pathname);
  if (response.status === 401 && !isPublicPage && localStorage.getItem('kiu_token')) {
    localStorage.removeItem('kiu_token');
    localStorage.removeItem('kiu_user');
    window.location.href = '/login';
  }

  return response;
};

export {};
