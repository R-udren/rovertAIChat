<script setup>
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: 'Confirm Action',
  },
  message: {
    type: String,
    default: 'Are you sure you want to proceed?',
  },
  confirmText: {
    type: String,
    default: 'Confirm',
  },
  cancelText: {
    type: String,
    default: 'Cancel',
  },
  loadingText: {
    type: String,
    default: 'Processing...',
  },
  type: {
    type: String,
    default: 'warning', // 'warning', 'danger', 'info', 'success'
    validator: (value) => ['warning', 'danger', 'info', 'success'].includes(value),
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['confirm', 'cancel', 'close'])

const showContent = ref(false)

// Icon components
const WarningIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 19.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
  `,
}

const DangerIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  `,
}

const InfoIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `,
}

const SuccessIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `,
}

const iconComponent = computed(() => {
  switch (props.type) {
    case 'warning':
      return WarningIcon
    case 'danger':
      return DangerIcon
    case 'info':
      return InfoIcon
    case 'success':
      return SuccessIcon
    default:
      return WarningIcon
  }
})

const iconColorClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'bg-yellow-100/10 border border-yellow-500/20'
    case 'danger':
      return 'bg-red-100/10 border border-red-500/20'
    case 'info':
      return 'bg-blue-100/10 border border-blue-500/20'
    case 'success':
      return 'bg-green-100/10 border border-green-500/20'
    default:
      return 'bg-yellow-100/10 border border-yellow-500/20'
  }
})

const iconTextClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'text-yellow-400'
    case 'danger':
      return 'text-red-400'
    case 'info':
      return 'text-blue-400'
    case 'success':
      return 'text-green-400'
    default:
      return 'text-yellow-400'
  }
})

const confirmButtonClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
    case 'danger':
      return 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
    case 'info':
      return 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
    case 'success':
      return 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
    default:
      return 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
  }
})

const handleBackdropClick = () => {
  if (!props.loading) {
    handleCancel()
  }
}

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
  emit('close')
}

// Handle modal animation
watch(
  () => props.isOpen,
  async (newValue) => {
    if (newValue) {
      await nextTick()
      setTimeout(() => {
        showContent.value = true
      }, 10)
    } else {
      showContent.value = false
    }
  },
)

// Handle escape key
const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen && !props.loading) {
    handleCancel()
  }
}

// Add event listener when component mounts
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeydown)
}

// Clean up event listener when component unmounts
onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', handleKeydown)
  }
})
</script>

<template>
  <teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" @click="handleBackdropClick">
      <!-- Backdrop -->
      <div
        class="fixed inset-0 transition-opacity duration-300 bg-zinc-900/60 backdrop-blur-sm"
        :class="{ 'opacity-100': showContent, 'opacity-0': !showContent }"
      ></div>

      <!-- Modal Content -->
      <div class="flex items-center justify-center min-h-full p-4">
        <div
          class="relative w-full max-w-md overflow-hidden transition-all duration-300 transform border shadow-2xl rounded-xl bg-zinc-800 border-zinc-700"
          :class="{
            'scale-100 opacity-100': showContent,
            'scale-95 opacity-0': !showContent,
          }"
          @click.stop
        >
          <!-- Icon Section -->
          <div class="px-6 pt-6 pb-4">
            <div
              class="flex items-center justify-center w-16 h-16 mx-auto rounded-full"
              :class="iconColorClass"
            >
              <component :is="iconComponent" class="w-8 h-8" :class="iconTextClass" />
            </div>
          </div>

          <!-- Content -->
          <div class="px-6 pb-6">
            <div class="text-center">
              <h3 class="mb-2 text-lg font-semibold text-white" v-html="title"></h3>
              <p class="mb-6 text-sm text-zinc-400" v-html="message"></p>
            </div>

            <!-- Actions -->
            <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-center">
              <button
                @click="handleCancel"
                :disabled="loading"
                class="w-full sm:w-auto px-4 py-2.5 text-sm font-medium text-zinc-300 bg-zinc-700 border border-zinc-600 rounded-lg hover:bg-zinc-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {{ cancelText }}
              </button>
              <button
                @click="handleConfirm"
                :disabled="loading"
                class="w-full sm:w-auto px-4 py-2.5 text-sm font-medium text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center min-h-[2.75rem]"
                :class="confirmButtonClass"
              >
                <div
                  v-if="loading"
                  class="w-4 h-4 mr-2 border-2 border-white rounded-full border-t-transparent animate-spin"
                ></div>
                {{ loading ? loadingText : confirmText }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
/* Custom animations for smooth modal transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
