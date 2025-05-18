import { api } from '@/services/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const isAuthenticated = ref(localStorage.getItem('user') !== null)

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
      // The server will set the cookies in the response
      const data = await api.postForm('auth/login', credentials)
      isAuthenticated.value = true
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
    // If already logged out, prevent duplicate calls
    if (!isAuthenticated.value) return

    // Clear local state
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('user')

    try {
      // The server will clear the cookies
      await api.post('auth/logout')
    } catch (err) {
      console.error('Logout error:', err)
    }
  }

  // Refresh token
  async function refreshAccessToken() {
    try {
      // The server will use the refresh cookie automatically
      await api.post('auth/refresh')
      return true
    } catch (err) {
      console.error('Token refresh error:', err)
      // Clear auth state on refresh failure
      await logout()
      return false
    }
  }

  // Fetch user profile
  async function fetchUserProfile() {
    loading.value = true
    try {
      const data = await api.get('users/me')
      if (data) {
        user.value = data
        isAuthenticated.value = true
        localStorage.setItem('user', JSON.stringify(data))
        return data
      }
      return null
    } catch (err) {
      console.error('Profile fetch error:', err)

      // Only handle specific error statuses
      if (err.status === 401 || err.status === 403) {
        isAuthenticated.value = false
        user.value = null
      }
      return null
    } finally {
      loading.value = false
    }
  }

  // Initialize - check if user is authenticated
  async function initialize() {
    try {
      await fetchUserProfile()
    } catch (err) {
      console.error('Initialization error:', err)
      isAuthenticated.value = false
      user.value = null
    }
  }

  return {
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
