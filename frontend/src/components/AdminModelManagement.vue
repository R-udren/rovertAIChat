<template>
  <div class="space-y-6">
    <!-- Header with Actions -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-white">Model Management</h2>
        <p class="text-zinc-400 mt-1">Manage Ollama models and their availability</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="showPullModal = true"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
          <span>Pull Model</span>
        </button>
        <button
          @click="refreshModels"
          :disabled="adminStore.loading"
          class="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
        >
          <svg
            v-if="!adminStore.loading"
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            ></path>
          </svg>
          <div
            v-else
            class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
          ></div>
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Ollama Status -->
    <div class="bg-zinc-800 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span class="text-white font-medium">Ollama Status</span>
          </div>
          <span class="text-zinc-400">Connected</span>
        </div>
        <button
          @click="checkOllamaVersion"
          class="text-blue-400 hover:text-blue-300 transition-colors text-sm"
        >
          Check Version
        </button>
      </div>
      <div v-if="ollamaVersion" class="mt-2 text-sm text-zinc-400">
        Version: {{ ollamaVersion.version || 'Unknown' }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="adminStore.loading && !models.length" class="flex justify-center py-12">
      <div class="text-center">
        <div
          class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"
        ></div>
        <p class="text-zinc-400">Loading models...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="adminStore.error" class="bg-red-900/20 border border-red-500 rounded-lg p-4">
      <div class="flex items-center space-x-3">
        <svg
          class="w-5 h-5 text-red-400 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
        <div>
          <h3 class="text-red-400 font-medium">Error loading models</h3>
          <p class="text-red-300 text-sm">{{ adminStore.error }}</p>
        </div>
      </div>
    </div>

    <!-- Models Grid -->
    <div v-else-if="models.length" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="model in models"
        :key="model.name"
        class="bg-zinc-800 rounded-lg p-6 hover:bg-zinc-750 transition-colors"
      >
        <!-- Model Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-white mb-1">{{ model.name }}</h3>
            <p class="text-sm text-zinc-400">
              {{ model.digest ? model.digest.substring(0, 12) + '...' : 'No digest' }}
            </p>
          </div>
          <div class="ml-4 flex space-x-2">
            <button
              @click="deleteModel(model)"
              class="text-red-400 hover:text-red-300 transition-colors p-1"
              title="Delete Model"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                ></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Model Details -->
        <div class="space-y-3">
          <div class="flex justify-between text-sm">
            <span class="text-zinc-400">Size:</span>
            <span class="text-white">{{ formatSize(model.size) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-zinc-400">Modified:</span>
            <span class="text-white">{{ formatDate(model.modified_at) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-zinc-400">Family:</span>
            <span class="text-white">{{ model.details?.family || 'Unknown' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-zinc-400">Format:</span>
            <span class="text-white">{{ model.details?.format || 'Unknown' }}</span>
          </div>
        </div>

        <!-- Model Parameters (if available) -->
        <div v-if="model.details?.parameter_size" class="mt-4 pt-4 border-t border-zinc-700">
          <div class="flex justify-between text-sm">
            <span class="text-zinc-400">Parameters:</span>
            <span class="text-white">{{ model.details.parameter_size }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <svg
        class="mx-auto h-12 w-12 text-zinc-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
        ></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-zinc-300">No models found</h3>
      <p class="mt-1 text-sm text-zinc-400">No Ollama models are currently installed.</p>
      <button
        @click="showPullModal = true"
        class="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Pull Your First Model
      </button>
    </div>

    <!-- Pull Model Modal -->
    <div
      v-if="showPullModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-zinc-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-white">Pull New Model</h3>
          <button @click="showPullModal = false" class="text-zinc-400 hover:text-zinc-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>

        <form @submit.prevent="pullModel">
          <div class="mb-4">
            <label for="modelName" class="block text-sm font-medium text-zinc-300 mb-2">
              Model Name
            </label>
            <input
              id="modelName"
              v-model="newModelName"
              type="text"
              placeholder="e.g., llama2, codellama, mistral"
              class="w-full px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-lg text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p class="mt-1 text-xs text-zinc-400">
              Enter the model name as it appears in the Ollama registry
            </p>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showPullModal = false"
              class="px-4 py-2 text-zinc-400 hover:text-zinc-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!newModelName.trim() || pullingModel"
              class="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
            >
              <div
                v-if="pullingModel"
                class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
              ></div>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              <span>{{ pullingModel ? 'Pulling...' : 'Pull Model' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'
import { computed, onMounted, ref } from 'vue'

const adminStore = useAdminStore()
const toastStore = useToastStore()

const showPullModal = ref(false)
const newModelName = ref('')
const pullingModel = ref(false)
const ollamaVersion = ref(null)

const models = computed(() => adminStore.models)

// Utility functions
const formatSize = (bytes) => {
  if (!bytes) return 'Unknown'
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Model management functions
const refreshModels = async () => {
  try {
    await adminStore.fetchOllamaModels()
    toastStore.success('Models refreshed successfully')
  } catch (error) {
    toastStore.error('Failed to refresh models: ' + error.message)
  }
}

const pullModel = async () => {
  if (!newModelName.value.trim()) return

  pullingModel.value = true
  try {
    await adminStore.pullOllamaModel(newModelName.value.trim())
    toastStore.success(`Model "${newModelName.value}" pulled successfully`)
    newModelName.value = ''
    showPullModal.value = false
  } catch (error) {
    toastStore.error('Failed to pull model: ' + error.message)
  } finally {
    pullingModel.value = false
  }
}

const deleteModel = async (model) => {
  if (
    confirm(`Are you sure you want to delete model "${model.name}"? This action cannot be undone.`)
  ) {
    try {
      await adminStore.deleteOllamaModel(model.name)
      toastStore.success(`Model "${model.name}" deleted successfully`)
    } catch (error) {
      toastStore.error('Failed to delete model: ' + error.message)
    }
  }
}

const checkOllamaVersion = async () => {
  try {
    ollamaVersion.value = await adminStore.getOllamaVersion()
    toastStore.success('Ollama version fetched successfully')
  } catch (error) {
    toastStore.error('Failed to fetch Ollama version: ' + error.message)
  }
}

// Load models on component mount
onMounted(async () => {
  await refreshModels()
  await checkOllamaVersion()
})
</script>
