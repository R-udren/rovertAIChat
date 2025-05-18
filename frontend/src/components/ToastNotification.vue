<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'info', 'warning'].includes(value),
  },
  duration: {
    type: Number,
    default: 3000,
  },
  position: {
    type: String,
    default: 'top-right',
    validator: (value) =>
      [
        'top-right',
        'top-left',
        'bottom-right',
        'bottom-left',
        'top-center',
        'bottom-center',
      ].includes(value),
  },
})

const emit = defineEmits(['close'])

const isVisible = ref(false)
const progress = ref(100)
let timer = null
let progressTimer = null

const typeConfig = {
  success: {
    bg: 'from-green-500/80 to-green-600/80',
    border: 'border-green-400/30',
    icon: 'M5 13l4 4L19 7',
  },
  error: {
    bg: 'from-red-500/80 to-red-600/80',
    border: 'border-red-400/30',
    icon: 'M6 18L18 6M6 6l12 12',
  },
  info: {
    bg: 'from-primary-500/80 to-primary-600/80',
    border: 'border-primary-400/30',
    icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  warning: {
    bg: 'from-yellow-500/80 to-yellow-600/80',
    border: 'border-yellow-400/30',
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  },
}

const positionClasses = {
  'top-right': 'top-4 right-4',
  'top-left': 'top-4 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'top-center': 'top-4 left-1/2 -translate-x-1/2',
  'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
}

const toastClasses = computed(() => [
  'fixed z-50 p-4 rounded-lg shadow-xl max-w-md transition-all transform glass-effect backdrop-blur-md',
  `bg-gradient-to-br ${typeConfig[props.type].bg}`,
  `border ${typeConfig[props.type].border}`,
  positionClasses[props.position],
])

const updateProgress = () => {
  // Calculate actual step to complete exactly at the end of duration
  const updateFrequency = 10 // ms between updates
  const totalSteps = props.duration / updateFrequency
  const step = 100 / totalSteps

  progressTimer = setInterval(() => {
    progress.value = Math.max(0, progress.value - step)
    if (progress.value <= 0) {
      clearInterval(progressTimer)
    }
  }, updateFrequency)
}

const closeToast = () => {
  isVisible.value = false
  clearTimeout(timer)
  clearInterval(progressTimer)
  setTimeout(() => {
    emit('close')
  }, 300)
}

onMounted(() => {
  isVisible.value = true

  if (props.duration > 0) {
    updateProgress()
    // Set timer to close the toast at the same time the progress bar completes
    // We add a tiny bit of extra time to ensure the progress bar has completed
    timer = setTimeout(() => {
      closeToast()
    }, props.duration + 50)
  }
})

onBeforeUnmount(() => {
  clearTimeout(timer)
  clearInterval(progressTimer)
})
</script>

<template>
  <Transition name="toast">
    <div v-if="isVisible" :class="toastClasses">
      <div class="flex items-center gap-3">
        <!-- Icon based on type -->
        <div class="flex-shrink-0 text-white">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              :d="typeConfig[type].icon"
            />
          </svg>
        </div>

        <!-- Message -->
        <div class="flex-1 font-medium text-white">{{ message }}</div>

        <!-- Close button -->
        <button
          @click="closeToast"
          class="p-1 ml-auto text-white transition-colors rounded-full opacity-70 hover:opacity-100 hover:bg-black/10"
          aria-label="Close notification"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-5 h-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>

      <!-- Progress bar -->
      <div v-if="duration > 0" class="h-1 mt-3 overflow-hidden rounded-full bg-white/20">
        <div class="h-full rounded-full bg-white/80" :style="{ width: `${progress}%` }"></div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition:
    opacity 0.3s,
    transform 0.3s;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
