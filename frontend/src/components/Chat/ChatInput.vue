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
  <div class="relative p-4 border-t border-zinc-800 bg-zinc-900">
    <div
      class="flex items-center justify-center px-2 transition-all rounded-lg bg-zinc-800 focus-within:ring-2 focus-within:ring-zinc-500"
    >
      <textarea
        ref="textareaRef"
        :value="messageInput"
        @input="handleInput"
        @keydown="handleKeyDown"
        placeholder="Type your message here..."
        class="flex-1 min-h-[40px] bg-transparent resize-none text-white focus:outline-none p-2"
        :disabled="isSubmitting"
      ></textarea>

      <button
        @click="handleSendMessage"
        class="p-2 text-white transition-colors rounded-lg hover:bg-zinc-600"
        :disabled="!messageInput.trim() || isSubmitting"
        :class="{ 'opacity-20 cursor-not-allowed': !messageInput.trim() || isSubmitting }"
      >
        <svg
          v-if="!isSubmitting"
          xmlns="http://www.w3.org/2000/svg"
          class="size-6"
          viewBox="0 0 16 16"
        >
          <path
            fill="currentColor"
            d="M1.177 1.119a.5.5 0 0 1 .547-.066l13 6.5a.5.5 0 0 1 0 .894l-13 6.5a.5.5 0 0 1-.702-.594L2.977 8L1.022 1.647a.5.5 0 0 1 .155-.528M3.869 8.5l-1.547 5.03L13.382 8L2.322 2.47L3.869 7.5H9.5a.5.5 0 0 1 0 1z"
          />
        </svg>
        <svg
          v-else
          class="size-6 animate-spin"
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
