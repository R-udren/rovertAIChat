// Auth store to handle user authentication
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // Register new user
  async function register(credentials) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed')
      }

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
      const formData = new URLSearchParams()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed')
      }

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
    try {
      if (token.value) {
        await fetch('http://localhost:8000/api/auth/logout', {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token.value}`,
          },
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      refreshToken.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  // Refresh token
  async function refreshAccessToken() {
    if (!refreshToken.value) return false

    try {
      const response = await fetch('http://localhost:8000/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken.value }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      token.value = data.access_token
      refreshToken.value = data.refresh_token
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      return true
    } catch (err) {
      console.error('Token refresh error:', err)
      logout()
      return false
    }
  }

  // Fetch user profile
  async function fetchUserProfile() {
    if (!token.value) return null

    loading.value = true
    try {
      const response = await fetch('http://localhost:8000/api/users/me', {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })

      if (response.status === 401) {
        const refreshed = await refreshAccessToken()
        if (!refreshed) {
          throw new Error('Authentication failed')
        }
        return await fetchUserProfile()
      }

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch user profile')
      }

      user.value = data
      return data
    } catch (err) {
      console.error('Profile fetch error:', err)
      if (err.message === 'Authentication failed') {
        logout()
      }
      return null
    } finally {
      loading.value = false
    }
  }

  // Initialize - check if token exists and fetch user data
  async function initialize() {
    if (token.value) {
      await fetchUserProfile()
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
