<script setup>
import { useUserSettingsStore } from '@/stores/userSettings'
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  isLast: {
    type: Boolean,
    default: false,
  },
})

const userSettingsStore = useUserSettingsStore()

// Chat bubble style based on user preferences
const chatBubbleStyle = computed(() => {
  const style = userSettingsStore.settings?.preferences?.chatBubbleStyle || 'rounded'
  return (
    {
      rounded: {
        user: 'rounded-2xl rounded-br-none',
        ai: 'rounded-2xl rounded-bl-none',
      },
      square: {
        user: 'rounded-md',
        ai: 'rounded-md',
      },
      modern: {
        user: 'rounded-lg rounded-tr-none',
        ai: 'rounded-lg rounded-tl-none',
      },
    }[style] || { user: 'rounded-2xl rounded-br-none', ai: 'rounded-2xl rounded-bl-none' }
  )
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const isUserMessage = computed(() => props.message.role === 'user')

const messageClasses = computed(() => [
  'flex max-w-[85%] transition-all',
  isUserMessage.value ? 'justify-end ml-auto' : 'justify-start',
  props.isLast ? 'animate-slide-up' : '',
])

const bubbleClasses = computed(() => [
  'p-4 relative shadow-md',
  isUserMessage.value
    ? `bg-gradient-to-br from-primary-600 to-primary-700 text-white ${chatBubbleStyle.value.user}`
    : `glass-effect text-gray-100 ${chatBubbleStyle.value.ai}`,
  props.isLast ? (isUserMessage.value ? 'animate-slide-in-left' : 'animate-slide-in-right') : '',
])
</script>

<template>
  <div :class="messageClasses">
    <div :class="bubbleClasses">
      <div class="whitespace-pre-wrap message-content">{{ message.content }}</div>
      <div class="flex items-center justify-between gap-2 mt-2 text-xs opacity-70">
        <div class="font-medium">
          {{ isUserMessage ? 'You' : 'AI' }}
        </div>
        <div>{{ formatDate(message.timestamp) }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-content {
  line-height: 1.6;
  word-break: break-word;
}
</style>
