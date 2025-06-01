<script setup>
import { useModelsStore } from '@/stores/models'

const props = defineProps({
  modelId: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['update:modelId', 'modelChanged'])

const modelsStore = useModelsStore()
const selectedModel = ref('')
const isDropdownOpen = ref(false)
const modelCapabilitiesCache = ref({})

onMounted(async () => {
  const storedModel = localStorage.getItem('preferredModel')
  selectedModel.value = props.modelId || storedModel || ''

  // Fetch models using the shared store
  await modelsStore.fetchModels()

  // If no model is selected yet and we have models, select the first one
  if (!selectedModel.value && modelsStore.models.length > 0) {
    selectedModel.value = modelsStore.models[0].name
    saveModelPreference(selectedModel.value)
  }

  // Fetch capabilities for all models to show vision badges
  for (const model of modelsStore.models) {
    await fetchModelCapabilities(model.name)
  }

  document.addEventListener('click', closeDropdown)
})

// Watch for prop changes
watch(
  () => props.modelId,
  (newModelId) => {
    if (newModelId && newModelId !== selectedModel.value) {
      selectedModel.value = newModelId
    }
  },
  { immediate: true },
)

// Watch for selectedModel changes and emit
watch(selectedModel, (newModel) => {
  if (newModel) {
    emit('update:modelId', newModel)
    emit('modelChanged', newModel)
  }
})

// Save model preference to localStorage
const saveModelPreference = (modelName) => {
  localStorage.setItem('preferredModel', modelName)
}

// Fetch capabilities for a model when needed
const fetchModelCapabilities = async (modelName) => {
  if (!modelName || modelCapabilitiesCache.value[modelName]) return

  const capabilities = await modelsStore.getModelCapabilities(modelName)
  if (capabilities) {
    modelCapabilitiesCache.value[modelName] = capabilities
  }
}

// Check if model has vision support
const modelHasVision = (modelName) => {
  return modelCapabilitiesCache.value[modelName]?.has_vision || false
}

// Handle model selection with capability loading
const selectModel = async (model) => {
  selectedModel.value = model.name
  isDropdownOpen.value = false
  saveModelPreference(model.name)

  // Fetch capabilities for the selected model
  await fetchModelCapabilities(model.name)

  // Emit events will be handled by the watch above
}

// Toggle dropdown
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

// Close dropdown when clicking outside
const closeDropdown = (event) => {
  if (!event.target.closest('.model-selector')) {
    isDropdownOpen.value = false
  }
}

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})

// Get currently selected model details
const selectedModelDetails = computed(() => {
  // If there's an error or no models available, don't show a selected model
  if (modelsStore.error || modelsStore.models.length === 0) {
    return {}
  }
  return modelsStore.models.find((model) => model.name === selectedModel.value) || {}
})

// Computed property to show the display text
const displayText = computed(() => {
  if (modelsStore.loading) {
    return 'Loading models...'
  }
  if (modelsStore.error) {
    return 'Ollama unavailable'
  }
  if (modelsStore.models.length === 0) {
    return 'No models available :('
  }
  return selectedModelDetails.value.display_name || selectedModel.value || 'Select model'
})

// Handle refresh
const handleRefresh = async () => {
  await modelsStore.refreshModels()

  // If no model is selected yet and we have models, select the first one
  if (!selectedModel.value && modelsStore.models.length > 0) {
    selectedModel.value = modelsStore.models[0].name
    saveModelPreference(selectedModel.value)
  }
}

// Watch for models store changes to clear selected model when offline
watch(
  () => modelsStore.error,
  (hasError) => {
    if (hasError) {
      // Clear selected model when there's an error
      selectedModel.value = ''
    }
  },
)

watch(
  () => modelsStore.models,
  (models) => {
    // If models become empty, clear the selected model
    if (models.length === 0) {
      selectedModel.value = ''
    }
    // If we have models but no selected model, select the first one
    else if (!selectedModel.value) {
      const storedModel = localStorage.getItem('preferredModel')
      const modelExists = models.find((m) => m.name === storedModel)

      if (modelExists) {
        selectedModel.value = storedModel
      } else {
        selectedModel.value = models[0].name
        saveModelPreference(selectedModel.value)
      }
    }
  },
)
</script>

<template>
  <div class="relative model-selector">
    <button
      @click.stop="toggleDropdown"
      class="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md bg-zinc-700 hover:bg-zinc-600 text-white"
      :disabled="modelsStore.loading"
    >
      <span
        v-if="modelsStore.loading"
        class="w-4 h-4 border-2 border-t-2 rounded-full border-zinc-500 border-t-zinc-200 animate-spin"
      ></span>
      <span v-else class="truncate max-w-[150px]">
        {{ displayText }}
      </span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-4 h-4 ml-1 transition-transform"
        :class="{ 'rotate-180': isDropdownOpen }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div
      v-if="isDropdownOpen"
      class="absolute right-0 z-10 w-64 mt-2 overflow-hidden border rounded-md shadow-lg bg-zinc-800 border-zinc-700"
    >
      <div class="py-1 overflow-y-auto max-h-60">
        <div v-if="modelsStore.loading" class="flex justify-center py-4">
          <div
            class="w-5 h-5 border-2 border-t-2 rounded-full border-zinc-600 border-t-zinc-300 animate-spin"
          ></div>
        </div>
        <div v-else-if="modelsStore.error" class="px-4 py-3">
          <div class="mb-2 text-sm text-red-400">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="inline w-4 h-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            Ollama unavailable
          </div>
          <div class="mb-3 text-xs text-gray-400">
            {{ modelsStore.error }}
          </div>
          <button
            @click="handleRefresh"
            class="flex items-center gap-2 px-3 py-1.5 text-xs rounded-md bg-zinc-700 hover:bg-zinc-600 text-white transition-colors w-full justify-center"
            :disabled="modelsStore.loading"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              :class="{ 'animate-spin': modelsStore.loading }"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Retry Connection
          </button>
        </div>
        <div v-else-if="modelsStore.models.length === 0" class="px-4 py-2 text-sm text-gray-400">
          No models available
        </div>
        <template v-else>
          <button
            v-for="model in modelsStore.models"
            :key="model.id || model.name"
            @click="selectModel(model)"
            class="flex items-start w-full px-4 py-2 text-left text-white transition-colors hover:bg-zinc-700"
            :class="{ 'bg-zinc-700': model.name === selectedModel }"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-medium">{{ model.display_name || model.name }}</span>
                <span
                  v-if="modelHasVision(model.name)"
                  class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30"
                  title="Supports image input"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-3 h-3 mr-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  Vision
                </span>
              </div>
              <div class="text-xs text-gray-400 truncate">
                {{ model.description || 'Model from Ollama' }}
              </div>
              <div v-if="model.details?.parameter_size" class="mt-1 text-xs text-gray-300">
                {{ model.details.parameter_size }}
              </div>
            </div>
            <svg
              v-if="model.name === selectedModel"
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-indigo-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
          <div class="flex flex-col items-center mt-4">
            <button
              @click="handleRefresh"
              class="flex items-center gap-2 px-3 py-1.5 text-xs rounded-md bg-zinc-700 hover:bg-zinc-600 text-white transition-colors w-full/50 justify-center"
              :disabled="modelsStore.loading"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4"
                :class="{ 'animate-spin': modelsStore.loading }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Fetch again
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
