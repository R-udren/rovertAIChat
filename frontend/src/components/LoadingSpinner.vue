<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  text: {
    type: String,
    default: 'Loading...',
  },
})

const sizeClasses = {
  sm: 'w-6 h-6',
  md: 'w-10 h-10',
  lg: 'w-16 h-16',
}
</script>

<template>
  <div class="flex flex-col items-center justify-center">
    <div
      :class="[
        sizeClasses[size],
        'border-t-2 border-primary-500 border-solid rounded-full animate-spin',
      ]"
    ></div>
    <p v-if="text" class="text-gray-400 mt-2">{{ text }}</p>
  </div>
</template>
