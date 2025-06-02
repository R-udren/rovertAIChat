<template>
  <div
    v-if="isDragOverChat && canUploadImages"
    class="absolute inset-0 z-50 flex items-center justify-center border-2 border-blue-400 border-dashed rounded-lg pointer-events-none bg-blue-600/20 backdrop-blur-sm"
  >
    <div class="text-center">
      <svg
        class="w-16 h-16 mx-auto mb-4 text-blue-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>
      <p class="mb-2 text-lg font-medium text-blue-400">Drop images here</p>
      <p class="text-sm text-blue-300">Upload images to enhance your conversation</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isDragOverChat: Boolean,
  canUploadImages: Boolean,
})
</script>
