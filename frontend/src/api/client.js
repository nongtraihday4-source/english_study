/**
 * Axios instance — sends cookies (HttpOnly JWT) automatically.
 * Base URL reads from VITE_API_BASE env or defaults to /api/v1 (proxied by Vite).
 */
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  withCredentials: true,        // send HttpOnly cookies
  headers: { 'Content-Type': 'application/json' },
})

// Response interceptor: auto-refresh token on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('token/refresh') &&
      !originalRequest.url.includes('auth/login')
    ) {
      originalRequest._retry = true
      try {
        await api.post('/auth/auth/token/refresh/')
        return api(originalRequest)
      } catch {
        // Refresh failed — force logout
        window.dispatchEvent(new CustomEvent('es:force-logout'))
      }
    }
    return Promise.reject(error)
  },
)

export default api
