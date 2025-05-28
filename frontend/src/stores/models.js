import { api } from '@/services/api'
import { useToastStore } from '@/stores/toast'
import { defineStore } from 'pinia'
import { computed, readonly, ref } from 'vue'

export const useModelsStore = defineStore('models', () => {
  const models = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastFetch = ref(null)

  // Cache duration: 5 minutes
  const CACHE_DURATION = 5 * 60 * 1000

  const fetchModels = async (forceRefresh = false) => {
    // Check if we have cached data and it's still fresh
    if (!forceRefresh && models.value.length > 0 && lastFetch.value) {
      const timeSinceLastFetch = Date.now() - lastFetch.value
      if (timeSinceLastFetch < CACHE_DURATION) {
        return models.value
      }
    }

    // Prevent multiple simultaneous requests
    if (loading.value) {
      // Wait for the current request to complete
      return new Promise((resolve) => {
        const checkLoading = () => {
          if (!loading.value) {
            resolve(models.value)
          } else {
            setTimeout(checkLoading, 50)
          }
        }
        checkLoading()
      })
    }
    try {
      loading.value = true
      error.value = null

      const response = await api.get('/ollama/tags')
      models.value = response.models || []
      lastFetch.value = Date.now()

      return models.value
    } catch (err) {
      error.value = err.message || 'Failed to fetch models'
      models.value = [] // Clear models on error
      console.error('Error fetching models:', err)

      // Only show toast for non-refresh requests
      if (!forceRefresh) {
        const toastStore = useToastStore()
        toastStore.error('Failed to load available models')
      }

      return []
    } finally {
      loading.value = false
    }
  }

  const refreshModels = () => {
    return fetchModels(true)
  }
  const getModelByName = (name) => {
    return models.value.find((model) => model.name === name)
  }

  // Computed properties for Ollama status
  const isOllamaAvailable = computed(() => {
    return !error.value && models.value.length > 0
  })

  const ollamaStatus = computed(() => {
    if (loading.value) return 'loading'
    if (error.value) return 'offline'
    if (models.value.length === 0) return 'no-models'
    return 'online'
  })

  const statusMessage = computed(() => {
    switch (ollamaStatus.value) {
      case 'loading':
        return 'Connecting to Ollama...'
      case 'offline':
        return 'Ollama is not available'
      case 'no-models':
        return 'No models found in Ollama'
      case 'online':
        return `${models.value.length} model${models.value.length === 1 ? '' : 's'} available`
      default:
        return 'Unknown status'
    }
  })

  return {
    models: readonly(models),
    loading: readonly(loading),
    error: readonly(error),
    isOllamaAvailable: readonly(isOllamaAvailable),
    ollamaStatus: readonly(ollamaStatus),
    statusMessage: readonly(statusMessage),
    fetchModels,
    refreshModels,
    getModelByName,
  }
})
