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
  color: {
    type: String,
    default: 'primary',
  },
})

const sizeClasses = {
  sm: {
    spinner: 'w-5 h-5',
    text: 'text-xs',
  },
  md: {
    spinner: 'w-8 h-8',
    text: 'text-sm',
  },
  lg: {
    spinner: 'w-12 h-12',
    text: 'text-base',
  },
}

const colorClasses = {
  primary:
    'border-t-primary-500 border-r-primary-500/30 border-b-primary-500/10 border-l-primary-500/0',
  white: 'border-t-white border-r-white/30 border-b-white/10 border-l-white/0',
  blue: 'border-t-blue-500 border-r-blue-500/30 border-b-blue-500/10 border-l-blue-500/0',
}
</script>

<template>
  <div class="flex flex-col items-center justify-center space-y-3">
    <div
      :class="[
        sizeClasses[size].spinner,
        colorClasses[color],
        'border-2 rounded-full animate-spin transition-all',
      ]"
    ></div>
    <p
      v-if="text"
      :class="[sizeClasses[size].text, 'text-gray-300 font-medium animate-pulse-subtle']"
    >
      {{ text }}
    </p>
  </div>
</template>

<style scoped>
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 0.8s linear infinite;
}
</style>
