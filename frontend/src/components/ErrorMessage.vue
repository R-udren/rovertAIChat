<script setup>
defineProps({
  message: {
    type: String,
    required: true,
  },
  dismissible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['dismiss'])

const handleDismiss = () => {
  emit('dismiss')
}
</script>

<template>
  <div
    class="relative px-4 py-3 text-red-100 bg-red-500 border border-red-500 rounded-md bg-opacity-20"
  >
    <div v-if="dismissible" class="absolute top-2 right-2">
      <button
        @click="handleDismiss"
        class="text-red-200 transition-colors duration-200 hover:text-white"
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
    <p>{{ message }}</p>
  </div>
</template>
