<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  title: String,
  defaultTitle: {
    type: String,
    default: 'New Chat',
  },
})

const emit = defineEmits(['update-title'])

const isEditing = ref(false)
const editTitle = ref('')
const inputRef = ref(null)

// Start editing
const startEdit = () => {
  editTitle.value = props.title || props.defaultTitle
  isEditing.value = true
  // Focus input after DOM update
  setTimeout(() => {
    if (inputRef.value) {
      inputRef.value.focus()
      inputRef.value.select()
    }
  }, 10)
}

// Save title
const saveTitle = () => {
  const newTitle = editTitle.value.trim()
  if (newTitle && newTitle !== props.title) {
    emit('update-title', newTitle)
  }
  isEditing.value = false
}

// Cancel editing
const cancelEdit = () => {
  isEditing.value = false
  editTitle.value = ''
}

// Handle key events
const handleKeyDown = (event) => {
  if (event.key === 'Enter') {
    event.preventDefault()
    saveTitle()
  } else if (event.key === 'Escape') {
    event.preventDefault()
    cancelEdit()
  }
}

// Watch for clicking outside
const handleBlur = () => {
  saveTitle()
}

// Reset editing state when title prop changes
watch(
  () => props.title,
  () => {
    isEditing.value = false
  },
)
</script>

<template>
  <div class="flex items-center min-w-0">
    <input
      v-if="isEditing"
      ref="inputRef"
      v-model="editTitle"
      @keydown="handleKeyDown"
      @blur="handleBlur"
      class="flex-1 px-2 py-1 text-white bg-zinc-600 border border-zinc-500 rounded focus:outline-none focus:border-zinc-400"
      maxlength="100"
    />
    <div
      v-else
      @click="startEdit"
      class="flex-1 cursor-pointer truncate hover:text-zinc-300 transition-colors"
      :title="title || defaultTitle"
    >
      {{ title || defaultTitle }}
    </div>
  </div>
</template>
