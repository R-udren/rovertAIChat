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
const dropdownRef = ref(null)

// Initialize component
onMounted(async () => {
  await initializeModel()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Initialize model selection
const initializeModel = async () => {
  await modelsStore.fetchModels()

  const storedModel = localStorage.getItem('preferredModel')
  const targetModel = props.modelId || storedModel

  if (targetModel && modelsStore.models.some((m) => m.name === targetModel)) {
    selectedModel.value = targetModel
  } else if (modelsStore.models.length > 0) {
    selectedModel.value = modelsStore.models[0].name
    saveModelPreference(selectedModel.value)
  }
}

// Reactive model details
const selectedModelDetails = computed(() => {
  if (!selectedModel.value || modelsStore.models.length === 0) return null
  return modelsStore.models.find((model) => model.name === selectedModel.value)
})

// Display text with better UX messages
const displayText = computed(() => {
  if (modelsStore.loading) return 'Loading models...'
  if (modelsStore.error) return 'Connection failed'
  if (modelsStore.models.length === 0) return 'No models found'
  return selectedModelDetails.value?.display_name || selectedModel.value || 'Choose a model'
})

// Get capability icon and label
const getCapabilityInfo = (capability) => {
  const capabilityMap = {
    tools: {
      icon: 'M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z',
      label: 'Function Calling',
      color: 'text-emerald-500',
    },
    thinking: {
      icon: 'M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z',
      label: 'Chain of Thought',
      color: 'text-purple-500',
    },
    vision: {
      icon: 'M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
      label: 'Vision',
      color: 'text-blue-500',
    },
    multimodal: {
      icon: 'M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z',
      label: 'Multimodal',
      color: 'text-indigo-500',
    },
  }

  return (
    capabilityMap[capability] || {
      icon: 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z',
      label: capability.charAt(0).toUpperCase() + capability.slice(1),
      color: 'text-gray-500',
    }
  )
}

// Filter out 'completion' capability and get relevant capabilities for display
const getDisplayCapabilities = (capabilities) => {
  if (!capabilities || !Array.isArray(capabilities)) return []
  return capabilities.filter((cap) => cap !== 'completion')
}

// Status for styling
const status = computed(() => {
  if (modelsStore.loading) return 'loading'
  if (modelsStore.error) return 'error'
  if (modelsStore.models.length === 0) return 'empty'
  return 'ready'
})

// Model selection handler
const selectModel = (model) => {
  selectedModel.value = model.name
  isDropdownOpen.value = false
  saveModelPreference(model.name)
}

// Utility functions
const saveModelPreference = (modelName) => {
  localStorage.setItem('preferredModel', modelName)
}

const toggleDropdown = () => {
  if (status.value === 'ready') {
    isDropdownOpen.value = !isDropdownOpen.value
  }
}

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false
  }
}

const handleRefresh = async () => {
  await modelsStore.refreshModels()
  if (!selectedModel.value && modelsStore.models.length > 0) {
    selectedModel.value = modelsStore.models[0].name
    saveModelPreference(selectedModel.value)
  }
}

// Watchers
watch(
  () => props.modelId,
  (newModelId) => {
    if (newModelId && newModelId !== selectedModel.value) {
      selectedModel.value = newModelId
    }
  },
  { immediate: true },
)

watch(selectedModel, (newModel) => {
  if (newModel) {
    emit('update:modelId', newModel)
    emit('modelChanged', newModel)
  }
})

watch(
  () => modelsStore.models,
  (models) => {
    if (models.length === 0) {
      selectedModel.value = ''
    } else if (!selectedModel.value) {
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
  <div ref="dropdownRef" class="relative model-selector">
    <!-- Main Button -->
    <button
      @click="toggleDropdown"
      class="group flex items-center gap-3 p-2 text-sm font-medium rounded-lg transition-all duration-200 ease-in-out min-w-0 w-full md:w-auto"
      :class="{
        'bg-zinc-700 hover:bg-zinc-600 text-white shadow-lg hover:shadow-xl':
          status === 'ready' && selectedModel,
        'bg-zinc-700 hover:bg-zinc-600 text-white': status === 'ready' && !selectedModel,
        'bg-zinc-600 text-zinc-400 cursor-not-allowed': status === 'loading',
        'bg-red-900/50 hover:bg-red-800/50 text-red-200 border border-red-500/50':
          status === 'error',
        'bg-yellow-900/50 hover:bg-yellow-800/50 text-yellow-200 border border-yellow-500/50':
          status === 'empty',
      }"
      :disabled="status === 'loading'"
    >
      <!-- Status Icons -->
      <div class="flex-shrink-0">
        <!-- Loading Spinner -->
        <div
          v-if="status === 'loading'"
          class="w-4 h-4 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin"
        />
        <!-- Error Icon -->
        <svg
          v-else-if="status === 'error'"
          class="w-4 h-4 text-red-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
          />
        </svg>
        <!-- Warning Icon -->
        <svg
          v-else-if="status === 'empty'"
          class="w-4 h-4 text-yellow-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z"
          />
        </svg>
      </div>

      <!-- Model Name -->
      <div class="flex-1 min-w-0">
        <span class="block truncate text-left">
          {{ displayText }}
        </span>
        <span
          v-if="selectedModelDetails?.details?.parameter_size && status === 'ready'"
          class="block text-xs opacity-75 text-left"
        >
          {{ selectedModelDetails.details.parameter_size }}
        </span>
      </div>

      <!-- Dropdown Arrow -->
      <svg
        class="w-4 h-4 transition-transform duration-200 flex-shrink-0"
        :class="{ 'rotate-180': isDropdownOpen, 'opacity-50': status !== 'ready' }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="isDropdownOpen"
        class="absolute right-0 z-50 w-96 mt-2 bg-white dark:bg-zinc-900 rounded-xl shadow-2xl border border-zinc-200 dark:border-zinc-700 overflow-hidden"
      >
        <!-- Content -->
        <div class="max-h-[50vh] overflow-y-auto">
          <!-- Loading State -->
          <div v-if="status === 'loading'" class="flex flex-col items-center justify-center py-8">
            <div
              class="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-3"
            ></div>
            <p class="text-sm text-zinc-600 dark:text-zinc-400">Loading available models...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="status === 'error'" class="p-6 text-center">
            <div
              class="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-6 h-6 text-red-600 dark:text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-zinc-900 dark:text-white mb-2">
              Connection Failed
            </h4>
            <p class="text-xs text-zinc-500 dark:text-zinc-400 mb-4">{{ modelsStore.error }}</p>
            <button
              @click="handleRefresh"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              :disabled="modelsStore.loading"
            >
              <svg
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
              {{ modelsStore.loading ? 'Retrying...' : 'Retry Connection' }}
            </button>
          </div>

          <!-- Empty State -->
          <div v-else-if="status === 'empty'" class="p-6 text-center">
            <div
              class="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-6 h-6 text-yellow-600 dark:text-yellow-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z"
                />
              </svg>
            </div>
            <h4 class="text-sm font-medium text-zinc-900 dark:text-white mb-2">No Models Found</h4>
            <p class="text-xs text-zinc-500 dark:text-zinc-400 mb-4">
              No AI models are currently available
            </p>
            <button
              @click="handleRefresh"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              :disabled="modelsStore.loading"
            >
              <svg
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
              {{ modelsStore.loading ? 'Refreshing...' : 'Refresh Models' }}
            </button>
          </div>

          <!-- Models List -->
          <div v-else class="py-1">
            <button
              v-for="model in modelsStore.models"
              :key="model.id || model.name"
              @click="selectModel(model)"
              class="w-full px-4 py-4 text-left hover:bg-zinc-50 dark:hover:bg-zinc-700/50 transition-colors group flex items-start gap-3 border-l-3 border-transparent"
              :class="{
                'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500': model.name === selectedModel,
              }"
            >
              <!-- Model Icon -->
              <div class="flex-shrink-0 mt-0.5">
                <div
                  class="size-8 rounded-xl flex items-center justify-center shadow-sm"
                  :class="
                    model.name === selectedModel
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
                      : 'bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-700 dark:to-zinc-600 text-zinc-600 dark:text-zinc-300'
                  "
                >
                  <svg
                    class="size-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              </div>

              <!-- Model Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span
                    class="font-semibold text-zinc-900 dark:text-white truncate text-sm"
                    :class="{ 'text-blue-700 dark:text-blue-300': model.name === selectedModel }"
                  >
                    {{ model.display_name || model.name }}
                  </span>
                  <span
                    v-if="model.name === selectedModel"
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300"
                  >
                    Active
                  </span>
                </div>

                <!-- Model Size -->
                <div v-if="model.details?.parameter_size" class="flex items-center gap-2 mb-2">
                  <span
                    class="text-xs font-medium px-2 py-1 rounded-md bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300"
                  >
                    {{ model.details.parameter_size }}
                  </span>
                  <span
                    v-if="model.details?.quantization_level"
                    class="text-xs text-zinc-500 dark:text-zinc-400"
                  >
                    {{ model.details.quantization_level }}
                  </span>
                </div>

                <!-- Capabilities -->
                <div
                  v-if="getDisplayCapabilities(model.capabilities).length > 0"
                  class="flex flex-wrap gap-1.5"
                >
                  <div
                    v-for="capability in getDisplayCapabilities(model.capabilities)"
                    :key="capability"
                    class="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-600 shadow-sm"
                    :title="getCapabilityInfo(capability).label"
                  >
                    <svg
                      class="w-3 h-3"
                      :class="getCapabilityInfo(capability).color"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        :d="getCapabilityInfo(capability).icon"
                      />
                    </svg>
                    <span class="text-zinc-700 dark:text-zinc-300">
                      {{ getCapabilityInfo(capability).label }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Selected Checkmark -->
              <div v-if="model.name === selectedModel" class="flex-shrink-0 mt-2">
                <div class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fill-rule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Footer -->
        <div
          v-if="status === 'ready'"
          class="bg-gradient-to-r from-zinc-50 to-blue-50 dark:from-zinc-800 dark:to-blue-900/20 border-t border-zinc-200 dark:border-zinc-700"
        >
          <button
            @click="handleRefresh"
            class="w-full inline-flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-white dark:hover:bg-zinc-700 rounded-lg transition-colors"
            :disabled="modelsStore.loading"
          >
            <svg
              class="w-3 h-3"
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
            {{ modelsStore.loading ? 'Refreshing...' : 'Refresh models' }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
