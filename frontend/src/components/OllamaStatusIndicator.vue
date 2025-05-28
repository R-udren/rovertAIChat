<template>
  <div
    :class="[
      'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all duration-300',
      statusClass,
    ]"
  >
    <!-- Status icon -->
    <div class="flex-shrink-0">
      <!-- Loading -->
      <div
        v-if="modelsStore.ollamaStatus === 'loading'"
        class="w-4 h-4 border-2 border-t-2 border-gray-500 rounded-full border-t-blue-400 animate-spin"
      ></div>

      <!-- Online -->
      <svg
        v-else-if="modelsStore.ollamaStatus === 'online'"
        xmlns="http://www.w3.org/2000/svg"
        class="w-4 h-4 text-green-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>

      <!-- Offline/Error -->
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        class="w-4 h-4 text-red-400"
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
    </div>

    <!-- Status text -->
    <span class="font-medium">{{ modelsStore.statusMessage }}</span>

    <!-- Retry button for offline state -->
    <button
      v-if="modelsStore.ollamaStatus === 'offline' && showRetry"
      @click="handleRetry"
      class="px-2 py-1 ml-2 text-xs text-white transition-colors bg-red-600 rounded hover:bg-red-500"
      :disabled="modelsStore.loading"
    >
      {{ modelsStore.loading ? 'Retrying...' : 'Retry' }}
    </button>
  </div>
</template>

<script setup>
import { useModelsStore } from '@/stores/models'

const props = defineProps({
  showRetry: {
    type: Boolean,
    default: true,
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

const modelsStore = useModelsStore()

const statusClass = computed(() => {
  const baseClass = props.compact ? 'text-xs' : 'text-sm'

  switch (modelsStore.ollamaStatus) {
    case 'loading':
      return `${baseClass} bg-blue-900/20 border border-blue-500/30 text-blue-300`
    case 'online':
      return `${baseClass} bg-green-900/20 border border-green-500/30 text-green-300`
    case 'offline':
    case 'no-models':
      return `${baseClass} bg-red-900/20 border border-red-500/30 text-red-300`
    default:
      return `${baseClass} bg-gray-900/20 border border-gray-500/30 text-gray-300`
  }
})

const handleRetry = async () => {
  await modelsStore.refreshModels()
}
</script>
