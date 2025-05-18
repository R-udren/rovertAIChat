// User settings store
import { api } from '@/services/api'
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
      const data = await api.get('user-settings/me')
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
      const data = await api.put('user-settings/me', updatedSettings)
      settings.value = data
      return data
    } catch (err) {
      error.value = err.message
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
