import { api } from '@/services/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const isAuthenticated = computed(() => !!token.value)

  // Flag to prevent multiple simultaneous refresh attempts
  const isRefreshing = ref(false)

  // Flag to prevent initialization loops
  const initializationAttempted = ref(false)

  // Register new user
  async function register(credentials) {
    loading.value = true
    error.value = null
    try {
      const data = await api.post('auth/register', credentials)
      await login({
        username: credentials.username,
        password: credentials.password,
      })
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Login user
  async function login(credentials) {
    loading.value = true
    error.value = null
    try {
      const data = await api.postForm('auth/login', credentials)
      token.value = data.access_token
      refreshToken.value = data.refresh_token
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchUserProfile()
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Logout user
  async function logout() {
    // If already logging out or no token exists, prevent duplicate calls
    if (!token.value) return

    // Clear tokens first to prevent other operations from using them
    const tempToken = token.value
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    try {
      // Only attempt API logout if we had a token
      if (tempToken) {
        await api.delete('auth/logout').catch((err) => {
          // Silently handle logout API errors
          console.error('Logout API error:', err)
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
    }
  }

  // Refresh token
  async function refreshAccessToken() {
    // Don't attempt refresh if no refresh token or already refreshing
    if (!refreshToken.value || isRefreshing.value) return false

    isRefreshing.value = true

    try {
      const data = await api.post('auth/refresh', { refresh_token: refreshToken.value })

      // Only update tokens if we got valid data back
      if (data && data.access_token) {
        token.value = data.access_token

        // Only update refresh token if a new one was provided
        if (data.refresh_token) {
          refreshToken.value = data.refresh_token
          localStorage.setItem('refresh_token', data.refresh_token)
        }

        localStorage.setItem('access_token', data.access_token)
        return true
      }
      return false
    } catch (err) {
      console.error('Token refresh error:', err)
      // Clear auth state on refresh failure
      await logout()
      return false
    } finally {
      isRefreshing.value = false
    }
  }

  // Fetch user profile
  async function fetchUserProfile() {
    if (!token.value) return null

    loading.value = true
    try {
      const data = await api.get('users/me')
      user.value = data
      return data
    } catch (err) {
      console.error('Profile fetch error:', err)

      // Only attempt token refresh on specific errors
      const status = err.response?.status

      if (status === 401 || status === 403) {
        // Only try to refresh once, then logout if that fails
        const refreshed = await refreshAccessToken()
        if (!refreshed) {
          await logout()
        }
      }
      return null
    } finally {
      loading.value = false
    }
  }

  // Initialize - check if token exists and fetch user data
  // Has protection against initialization loops
  async function initialize() {
    // Prevent multiple initialization attempts
    if (initializationAttempted.value) return
    initializationAttempted.value = true

    if (token.value) {
      try {
        // Set a timeout for initialization to prevent hanging
        const profilePromise = fetchUserProfile()
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Profile fetch timeout')), 5000)
        })

        await Promise.race([profilePromise, timeoutPromise])
      } catch (err) {
        console.error('Initialization error:', err)
        await logout()
      }
    }
  }

  return {
    token,
    refreshToken,
    user,
    loading,
    error,
    isAuthenticated,
    register,
    login,
    logout,
    refreshAccessToken,
    fetchUserProfile,
    initialize,
  }
})
