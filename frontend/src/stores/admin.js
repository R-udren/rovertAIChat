// Admin store for user and model management
import { api } from '@/services/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export const useAdminStore = defineStore('admin', () => {
  const users = ref([])
  const models = ref([])
  const loading = ref(false)
  const usersError = ref(null)
  const ollamaError = ref(null)

  const authStore = useAuthStore()

  // Check if current user is admin
  const isAdmin = () => {
    return authStore.user?.role === 'admin'
  }

  // User Management Functions
  async function fetchUsers() {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    usersError.value = null

    try {
      const data = await api.get('users')
      users.value = data
      return data
    } catch (err) {
      usersError.value = err.message
      console.error('Error fetching users:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  async function createUser(userData) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    usersError.value = null

    try {
      const newUser = await api.post('auth/register', userData)

      // Add the new user to the local state
      users.value.unshift(newUser)

      return newUser
    } catch (err) {
      usersError.value = err.message
      console.error('Error creating user:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateUser(userId, userData) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    usersError.value = null

    try {
      const updatedUser = await api.put(`users/${userId}`, userData)

      // Update the user in the local state
      const index = users.value.findIndex((user) => user.id === userId)
      if (index !== -1) {
        users.value[index] = updatedUser
      }

      return updatedUser
    } catch (err) {
      usersError.value = err.message
      console.error('Error updating user:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deactivateUser(userId) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    usersError.value = null

    try {
      const updatedUser = await api.delete(`users/${userId}`)

      // Update the user in the local state
      const index = users.value.findIndex((user) => user.id === userId)
      if (index !== -1) {
        users.value[index] = updatedUser
      }

      return updatedUser
    } catch (err) {
      usersError.value = err.message
      console.error('Error deactivating user:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function activateUser(userId) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    usersError.value = null

    try {
      const updatedUser = await api.post(`users/${userId}/activate`)

      // Update the user in the local state
      const index = users.value.findIndex((user) => user.id === userId)
      if (index !== -1) {
        users.value[index] = updatedUser
      }

      return updatedUser
    } catch (err) {
      usersError.value = err.message
      console.error('Error activating user:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Ollama Model Management Functions
  async function fetchOllamaModels() {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    ollamaError.value = null

    try {
      const data = await api.get('ollama/tags')
      models.value = data.models || []
      return data
    } catch (err) {
      ollamaError.value = err.message
      console.error('Error fetching Ollama models:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function pullOllamaModel(modelName) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    ollamaError.value = null

    try {
      const response = await api.post('ollama/pull', { model: modelName })
      // Refresh the models list after pulling
      await fetchOllamaModels()
      return response
    } catch (err) {
      ollamaError.value = err.message
      console.error('Error pulling Ollama model:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteOllamaModel(modelName) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    loading.value = true
    ollamaError.value = null

    try {
      const response = await api.delete('ollama/delete', {
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model: modelName }),
      })
      // Refresh the models list after deletion
      await fetchOllamaModels()
      return response
    } catch (err) {
      ollamaError.value = err.message
      console.error('Error deleting Ollama model:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getOllamaVersion() {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    try {
      const version = await api.get('ollama/version')
      return version
    } catch (err) {
      console.error('Error fetching Ollama version:', err)
      throw err
    }
  }

  // User Settings Management
  async function getUserSettings(userId) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    try {
      const settings = await api.get(`user-settings/${userId}`)
      return settings
    } catch (err) {
      console.error('Error fetching user settings:', err)
      throw err
    }
  }

  async function updateUserSettings(userId, settings) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    try {
      const updatedSettings = await api.put(`user-settings/${userId}`, settings)
      return updatedSettings
    } catch (err) {
      console.error('Error updating user settings:', err)
      throw err
    }
  }

  async function deleteUserSettings(userId) {
    if (!isAdmin()) {
      throw new Error('Unauthorized: Admin access required')
    }

    try {
      await api.delete(`user-settings/${userId}`)
      return true
    } catch (err) {
      console.error('Error deleting user settings:', err)
      throw err
    }
  }

  // Reset store state
  function reset() {
    users.value = []
    models.value = []
    usersError.value = null
    ollamaError.value = null
    loading.value = false
  }
  return {
    users,
    models,
    loading,
    usersError,
    ollamaError,
    isAdmin,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser: deactivateUser,
    deactivateUser,
    activateUser,
    fetchOllamaModels,
    pullOllamaModel,
    deleteOllamaModel,
    getOllamaVersion,
    getUserSettings,
    updateUserSettings,
    deleteUserSettings,
    reset,
  }
})
