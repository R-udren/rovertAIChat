<script setup>
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  active: {
    type: Boolean,
    default: false,
  },
})

const adminStore = useAdminStore()
const toastStore = useToastStore()

const showPullModal = ref(false)
const showDeleteModal = ref(false)
const modelToDelete = ref(null)
const newModelName = ref('')
const pullingModel = ref(false)
const ollamaVersion = ref(null)

const models = computed(() => adminStore.models)

// Watch for active prop changes
watch(
  () => props.active,
  async (newActive) => {
    if (newActive) {
      await refreshModels()
      await checkOllamaVersion()
    }
  },
  { immediate: true },
)

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
  modelToDelete.value = model
  showDeleteModal.value = true
}

const confirmDeleteModel = async () => {
  if (!modelToDelete.value) return

  try {
    await adminStore.deleteOllamaModel(modelToDelete.value.name)
    toastStore.success(`Model "${modelToDelete.value.name}" deleted successfully`)
  } catch (error) {
    toastStore.error('Failed to delete model: ' + error.message)
  } finally {
    cancelDeleteModel()
  }
}

const cancelDeleteModel = () => {
  showDeleteModal.value = false
  modelToDelete.value = null
}

const checkOllamaVersion = async () => {
  try {
    ollamaVersion.value = await adminStore.getOllamaVersion()
  } catch (error) {
    toastStore.error('Failed to fetch Ollama version: ' + error.message)
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header with Actions -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-white">Model Management</h2>
        <p class="mt-1 text-zinc-400">Manage Ollama models and their availability</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="showPullModal = true"
          class="flex items-center px-4 py-2 space-x-2 text-white transition-colors bg-green-600 rounded-lg hover:bg-green-700"
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
          class="flex items-center px-4 py-2 space-x-2 text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
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
            class="w-4 h-4 border-2 border-white rounded-full border-t-transparent animate-spin"
          ></div>
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Ollama Status -->
    <div class="p-4 rounded-lg bg-zinc-800">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="flex items-center space-x-2">
            <div
              :class="[
                'w-3 h-3 rounded-full',
                adminStore.ollamaError ? 'bg-red-400' : 'bg-green-400 animate-pulse',
              ]"
            ></div>
            <span class="font-medium text-white">Ollama Status</span>
          </div>
          <span class="text-zinc-400">
            {{ adminStore.ollamaError ? 'Disconnected' : 'Connected' }}
          </span>
        </div>
        <button
          @click="checkOllamaVersion"
          :disabled="!!adminStore.ollamaError"
          class="text-sm transition-colors disabled:text-zinc-500 disabled:cursor-not-allowed"
          :class="adminStore.ollamaError ? 'text-zinc-500' : 'text-blue-400 hover:text-blue-300'"
        >
          Check Version
        </button>
      </div>
      <div v-if="ollamaVersion" class="mt-2 text-sm text-zinc-400">
        Version: {{ ollamaVersion.version || 'Unknown' }}
      </div>
      <div v-else-if="adminStore.ollamaError" class="mt-2 text-sm text-red-400">
        Ollama service is unavailable
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="adminStore.loading && !models.length" class="flex justify-center py-12">
      <div class="text-center">
        <div
          class="w-8 h-8 mx-auto mb-4 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"
        ></div>
        <p class="text-zinc-400">Loading models...</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="adminStore.ollamaError"
      class="p-4 border border-red-500 rounded-lg bg-red-900/20"
    >
      <div class="flex items-center space-x-3">
        <svg
          class="flex-shrink-0 w-5 h-5 text-red-400"
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
          <h3 class="font-medium text-red-400">Error loading models</h3>
          <p class="text-sm text-red-300">{{ adminStore.ollamaError }}</p>
        </div>
      </div>
    </div>

    <!-- Models Grid -->
    <div v-else-if="models.length" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="model in models"
        :key="model.name"
        class="p-6 transition-colors rounded-lg bg-zinc-800 hover:bg-zinc-750"
      >
        <!-- Model Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="mb-1 text-lg font-semibold text-white">{{ model.name }}</h3>
            <p class="text-sm text-zinc-400">
              {{ model.digest ? model.digest.substring(0, 12) + '...' : 'No digest' }}
            </p>
          </div>
          <div class="flex ml-4 space-x-2">
            <button
              @click="deleteModel(model)"
              class="p-1 text-red-400 transition-colors hover:text-red-300"
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
          <!-- Capabilities (if available) -->
          <div v-if="model.capabilities && model.capabilities.length > 0" class="text-sm">
            <span class="text-zinc-400">Capabilities:</span>
            <div class="flex flex-wrap gap-1 mt-1">
              <span
                v-for="capability in model.capabilities"
                :key="capability"
                class="px-2 py-1 text-xs text-gray-200 border border-purple-700 rounded-full bg-purple-600/10"
              >
                {{ capability }}
              </span>
            </div>
          </div>
        </div>

        <!-- Model Parameters (if available) -->
        <div v-if="model.details?.parameter_size" class="pt-4 mt-4 border-t border-zinc-700">
          <div class="flex justify-between text-sm">
            <span class="text-zinc-400">Parameters:</span>
            <span class="text-white">{{ model.details.parameter_size }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="py-12 text-center">
      <svg
        class="w-12 h-12 mx-auto text-zinc-400"
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
        class="px-4 py-2 mt-4 text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700"
      >
        Pull Your First Model
      </button>
    </div>
    <!-- Pull Model Modal -->
    <div
      v-if="showPullModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur"
    >
      <div class="w-full max-w-md p-6 mx-4 rounded-lg bg-zinc-800">
        <div class="flex items-center justify-between mb-4">
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
            <label for="modelName" class="block mb-2 text-sm font-medium text-zinc-300">
              Model Name
            </label>
            <input
              id="modelName"
              v-model="newModelName"
              type="text"
              placeholder="e.g., llama2, codellama, mistral"
              class="w-full px-3 py-2 text-white border rounded-lg bg-zinc-700 border-zinc-600 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p class="mt-1 text-xs text-zinc-400">
              Enter the model name as it appears in the
              <a
                href="https://ollama.com/search"
                target="_blank"
                rel="noopener noreferrer"
                class="text-blue-400 hover:underline"
              >
                Ollama registry
              </a>
            </p>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showPullModal = false"
              class="px-4 py-2 transition-colors text-zinc-400 hover:text-zinc-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!newModelName.trim() || pullingModel"
              class="flex items-center px-4 py-2 space-x-2 text-white transition-colors bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <div
                v-if="pullingModel"
                class="w-4 h-4 border-2 border-white rounded-full border-t-transparent animate-spin"
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

    <!-- Delete Confirmation Modal -->
    <ConfirmationModal
      :is-open="showDeleteModal"
      type="danger"
      :title="`Delete Model: ${modelToDelete?.name}`"
      :message="`Are you sure you want to delete the model '${modelToDelete?.name}'? This action cannot be undone and will permanently remove the model from your system.`"
      confirm-text="Delete Model"
      cancel-text="Cancel"
      @confirm="confirmDeleteModel"
      @cancel="cancelDeleteModel"
    />
  </div>
</template>
