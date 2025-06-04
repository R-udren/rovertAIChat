<script setup>
const props = defineProps({
  content: {
    type: String,
    required: true,
  },
  error: {
    type: String,
    default: null,
  },
  saving: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['save', 'cancel'])
const localContent = ref(props.content)
const textareaRef = ref(null)

// Auto-focus and auto-resize the textarea
onMounted(async () => {
  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.focus()
    autoResizeTextarea()
  }
})

watch(
  () => props.content,
  (newContent) => {
    localContent.value = newContent
  },
)

const autoResizeTextarea = () => {
  if (!textareaRef.value) return

  // Reset height first
  textareaRef.value.style.height = 'auto'

  // Set new height based on scroll height
  textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`
}

watch(localContent, () => {
  autoResizeTextarea()
})

const save = () => {
  emit('save', localContent.value)
}

const cancel = () => {
  emit('cancel')
}
</script>

<template>
  <div class="relative bg-zinc-800/50 rounded-md border border-zinc-700/50 p-3">
    <textarea
      v-model="localContent"
      class="w-full bg-transparent text-white border-0 focus:outline-none focus:ring-0 resize-none"
      :class="{ 'border-red-500': error }"
      rows="4"
      placeholder="Edit your message..."
      @keydown.ctrl.enter="save"
      @keydown.esc="cancel"
      ref="textareaRef"
    ></textarea>

    <div v-if="error" class="text-red-400 text-sm mt-1">
      {{ error }}
    </div>

    <div class="flex justify-end gap-2 mt-2">
      <button
        @click="cancel"
        class="px-3 py-1 text-sm text-gray-300 bg-zinc-700/50 hover:bg-zinc-700 rounded transition-colors"
      >
        Cancel
      </button>
      <button
        @click="save"
        class="px-3 py-1 text-sm text-white bg-indigo-600/80 hover:bg-indigo-600 rounded transition-colors"
        :disabled="saving"
      >
        <span v-if="saving" class="flex items-center gap-1">
          <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24">
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
          Saving...
        </span>
        <span v-else>Save</span>
      </button>
    </div>

    <div class="text-xs text-gray-500 mt-2">Press Ctrl+Enter to save, Esc to cancel</div>
  </div>
</template>

<style scoped>
textarea {
  min-height: 80px;
}
</style>
