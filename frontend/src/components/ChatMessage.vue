<script setup>
import { useUserSettingsStore } from '@/stores/userSettings'
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
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
</script>

<template>
  <div class="flex" :class="isUserMessage ? 'justify-end' : 'justify-start'">
    <div
      class="max-w-[80%] p-3 relative"
      :class="[
        isUserMessage
          ? `bg-primary-600 text-white ${chatBubbleStyle.user}`
          : `bg-zinc-700 text-gray-100 ${chatBubbleStyle.ai}`,
      ]"
    >
      <div class="whitespace-pre-wrap">{{ message.content }}</div>
      <div class="mt-1 text-xs text-right opacity-70">{{ formatDate(message.timestamp) }}</div>
    </div>
  </div>
</template>
