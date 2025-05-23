<script setup>
import { api } from '@/services/api'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  modelId: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['update:modelId', 'modelChanged'])

const models = ref([])
const loading = ref(false)
const selectedModel = ref('')
const toastStore = useToastStore()
const isDropdownOpen = ref(false)

onMounted(() => {
  const storedModel = localStorage.getItem('preferredModel')
  selectedModel.value = props.modelId || storedModel || ''
  fetchModels()
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

// Fetch available models from the API
const fetchModels = async () => {
  try {
    loading.value = true
    const response = await api.get('/ollama/tags')
    models.value = response.models || []

    // If no model is selected yet, select the first one
    if (!selectedModel.value && models.value.length > 0) {
      selectedModel.value = models.value[0].name
      saveModelPreference(selectedModel.value)
    }
  } catch (error) {
    console.error('Error fetching models:', error)
    toastStore.error('Failed to load available models')
  } finally {
    loading.value = false
  }
}

// Save model preference to localStorage
const saveModelPreference = (modelName) => {
  localStorage.setItem('preferredModel', modelName)
}

// Handle model selection
const selectModel = async (model) => {
  selectedModel.value = model.name
  isDropdownOpen.value = false
  saveModelPreference(model.name)
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
  return models.value.find((model) => model.name === selectedModel.value) || {}
})
</script>

<template>
  <div class="relative model-selector">
    <button
      @click.stop="toggleDropdown"
      class="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md bg-zinc-700 hover:bg-zinc-600 text-white"
      :disabled="loading"
    >
      <span
        v-if="loading"
        class="w-4 h-4 border-2 border-t-2 rounded-full border-zinc-500 border-t-zinc-200 animate-spin"
      ></span>
      <span v-else class="truncate max-w-[150px]">
        {{ selectedModelDetails.display_name || selectedModel || 'Select model' }}
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
      class="absolute right-0 z-10 w-64 mt-2 overflow-hidden rounded-md shadow-lg bg-zinc-800"
    >
      <div class="py-1 overflow-y-auto max-h-60">
        <div v-if="loading" class="flex justify-center py-4">
          <div
            class="w-5 h-5 border-2 border-t-2 rounded-full border-zinc-600 border-t-zinc-300 animate-spin"
          ></div>
        </div>
        <div v-else-if="models.length === 0" class="px-4 py-2 text-sm text-gray-400">
          No models available
        </div>
        <template v-else>
          <button
            v-for="model in models"
            :key="model.id || model.name"
            @click="selectModel(model)"
            class="flex items-start w-full px-4 py-2 text-left text-white transition-colors hover:bg-zinc-700"
            :class="{ 'bg-zinc-700': model.name === selectedModel }"
          >
            <div class="flex-1 min-w-0">
              <div class="font-medium">{{ model.display_name || model.name }}</div>
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
        </template>
      </div>
    </div>
  </div>
</template>
