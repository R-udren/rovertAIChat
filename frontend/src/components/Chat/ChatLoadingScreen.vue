<template>
  <div class="flex flex-col items-center justify-center flex-1 space-y-6">
    <div class="relative">
      <div class="w-16 h-16 border-4 rounded-full border-purple-500/20"></div>
      <div
        class="absolute top-0 left-0 w-16 h-16 border-4 border-transparent rounded-full border-t-purple-500 animate-spin"
      ></div>
    </div>
    <div class="space-y-2 text-center">
      <h2 class="text-xl font-semibold text-white">Initializing Chat</h2>
      <div class="space-y-1 text-sm text-gray-400">
        <p v-if="isLoadingSettings" class="flex items-center justify-center">
          <span class="w-2 h-2 mr-2 bg-purple-500 rounded-full animate-pulse"></span>
          Loading settings...
        </p>
        <p v-if="isLoadingModels" class="flex items-center justify-center">
          <span class="w-2 h-2 mr-2 bg-blue-500 rounded-full animate-pulse"></span>
          Loading models...
        </p>
        <p v-if="isLoadingChats" class="flex items-center justify-center">
          <span class="w-2 h-2 mr-2 bg-green-500 rounded-full animate-pulse"></span>
          Loading conversations...
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isLoadingSettings: Boolean,
  isLoadingModels: Boolean,
  isLoadingChats: Boolean,
})
</script>
