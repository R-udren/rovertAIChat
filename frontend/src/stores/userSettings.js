// User settings store
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export const useUserSettingsStore = defineStore('userSettings', () => {
  const settings = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const authStore = useAuthStore()

  // Fetch user settings
  async function fetchSettings() {
    if (!authStore.isAuthenticated) return null

    loading.value = true
    error.value = null

    try {
      const response = await fetch('http://localhost:8000/api/user-settings/me', {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      })

      if (response.status === 401) {
        const refreshed = await authStore.refreshAccessToken()
        if (!refreshed) {
          throw new Error('Authentication failed')
        }
        return await fetchSettings()
      }

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch user settings')
      }

      settings.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('Settings fetch error:', err)
      if (err.message === 'Authentication failed') {
        authStore.logout()
      }
      return null
    } finally {
      loading.value = false
    }
  }

  // Update user settings
  async function updateSettings(updatedSettings) {
    if (!authStore.isAuthenticated) return null

    loading.value = true
    error.value = null

    try {
      const response = await fetch('http://localhost:8000/api/user-settings/me', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedSettings),
      })

      if (response.status === 401) {
        const refreshed = await authStore.refreshAccessToken()
        if (!refreshed) {
          throw new Error('Authentication failed')
        }
        return await updateSettings(updatedSettings)
      }

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update user settings')
      }

      settings.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('Settings update error:', err)
      if (err.message === 'Authentication failed') {
        authStore.logout()
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reset settings
  function resetSettings() {
    settings.value = null
    error.value = null
  }

  return {
    settings,
    loading,
    error,
    fetchSettings,
    updateSettings,
    resetSettings,
  }
})
