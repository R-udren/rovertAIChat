<script setup>
import ChatMessage from '@/components/ChatMessage.vue'
import { ref } from 'vue'

defineProps({
  currentConversation: Object,
  messages: Array,
  loading: Boolean,
  streaming: Boolean,
})

defineEmits(['start-new-chat'])

const scrollContainer = ref(null)

// Expose the scroll container to parent
defineExpose({
  scrollContainer,
})
</script>

<template>
  <div ref="scrollContainer" class="flex-1 p-4 overflow-y-auto">
    <div
      v-if="!currentConversation && !loading"
      class="flex flex-col items-center justify-center h-full"
    >
      <div class="max-w-md p-6 text-center">
        <h2 class="mb-2 text-2xl font-bold text-white">Welcome to rovertChat</h2>
        <p class="mb-6 text-gray-300">
          Start a new conversation or select an existing one from the sidebar.
        </p>
        <button
          @click="$emit('start-new-chat')"
          class="px-4 py-2 font-medium text-white transition-colors rounded-lg bg-zinc-700 hover:bg-zinc-600"
        >
          Start a new chat
        </button>
      </div>
    </div>

    <div v-else-if="loading" class="flex justify-center p-4">
      <div
        class="w-8 h-8 border-2 border-t-2 rounded-full border-zinc-600 border-t-zinc-400 animate-spin"
      ></div>
    </div>

    <div v-else-if="messages.length === 0" class="flex justify-center p-4 text-gray-400">
      No messages yet. Start the conversation!
    </div>

    <div v-else class="space-y-6">
      <ChatMessage
        v-for="(message, index) in messages"
        :key="`${message.id || index}-${message.created_at || Date.now()}`"
        :message="message"
        :is-streaming="message.isStreaming"
        :is-last="index === messages.length - 1"
      />

      <div
        v-if="
          streaming &&
          !messages[messages.length - 1]?.isStreaming &&
          !messages[messages.length - 1]?.isLoading
        "
        class="flex items-center ml-2 space-x-2 text-gray-400"
      >
        <span>AI is thinking</span>
        <span class="animate-ellipsis">...</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-ellipsis {
  display: inline-block;
  animation: ellipsis 1.5s infinite;
}

@keyframes ellipsis {
  0% {
    content: '.';
  }
  33% {
    content: '..';
  }
  66% {
    content: '...';
  }
}
</style>
