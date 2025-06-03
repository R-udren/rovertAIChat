<template>
  <div
    class="message-actions absolute right-2 bottom-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity"
    v-if="!props.isSystemMessage && !props.isEditing"
  >
    <!-- Edit button -->
    <button
      v-if="props.canEdit"
      @click.stop="onEdit"
      class="p-1.5 bg-zinc-800 hover:bg-zinc-700 rounded text-gray-400 hover:text-white transition-colors"
      title="Edit message"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
        />
      </svg>
    </button>

    <!-- Delete button -->
    <button
      v-if="props.canDelete"
      @click.stop="onDelete"
      class="p-1.5 bg-zinc-800 hover:bg-red-900/60 rounded text-gray-400 hover:text-red-300 transition-colors"
      title="Delete message"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
          clip-rule="evenodd"
        />
      </svg>
    </button>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  isSystemMessage: {
    type: Boolean,
    default: false,
  },
  isEditing: {
    type: Boolean,
    default: false,
  },
  canEdit: {
    type: Boolean,
    default: false,
  },
  canDelete: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['edit', 'delete'])

const onEdit = () => emit('edit', props.message)
const onDelete = () => emit('delete', props.message)
</script>

<style scoped>
.message-actions {
  z-index: 100;
}
</style>
