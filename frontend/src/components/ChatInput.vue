<script setup>
import { ref } from 'vue'

const props = defineProps({
  messageInput: String,
  isSubmitting: Boolean,
})

const emit = defineEmits(['update:messageInput', 'send-message'])

const textareaRef = ref(null)
const expandedInput = ref(false)

// Auto-resize textarea
const adjustTextareaHeight = () => {
  if (!textareaRef.value) return

  textareaRef.value.style.height = 'auto'
  textareaRef.value.style.height = `${Math.min(textareaRef.value.scrollHeight, 150)}px`
  expandedInput.value = textareaRef.value.scrollHeight > 50
}

// Reset textarea height
const resetTextareaHeight = () => {
  if (!textareaRef.value) return
  textareaRef.value.style.height = 'auto'
  expandedInput.value = false
}

// Handle input change
const handleInput = () => {
  emit('update:messageInput', textareaRef.value.value)
  adjustTextareaHeight()
}

// Handle send message
const handleSendMessage = () => {
  emit('send-message')
  resetTextareaHeight()
}

// Handle Enter key
const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSendMessage()
  }
}

defineExpose({
  resetTextareaHeight,
})
</script>

<template>
  <div class="p-4 border-t border-zinc-700 bg-zinc-800">
    <div
      class="flex items-start p-2 transition-all rounded-lg bg-zinc-700 focus-within:ring-2 focus-within:ring-zinc-500"
      :class="{ 'items-center': !expandedInput }"
    >
      <textarea
        ref="textareaRef"
        :value="messageInput"
        @input="handleInput"
        @keydown="handleKeyDown"
        placeholder="Type your message here..."
        class="flex-1 min-h-[40px] mr-2 bg-transparent resize-none text-white focus:outline-none"
        :disabled="isSubmitting"
      ></textarea>
      <button
        @click="handleSendMessage"
        class="p-2 text-white transition-colors rounded-lg hover:bg-zinc-600"
        :disabled="!messageInput.trim() || isSubmitting"
        :class="{ 'opacity-50 cursor-not-allowed': !messageInput.trim() || isSubmitting }"
      >
        <svg
          v-if="!isSubmitting"
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
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
        <svg
          v-else
          class="w-6 h-6 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      </button>
    </div>
  </div>
</template>
