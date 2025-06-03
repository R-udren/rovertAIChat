// Composable for handling message actions (edit, delete)
import { useChatStore } from '@/stores/chat'
import { useToastStore } from '@/stores/toast'
import { computed, ref } from 'vue'

export function useMessageActions() {
  const chatStore = useChatStore()
  const toastStore = useToastStore() // for notifications

  // Message editing state
  const isEditing = ref(false)
  const messageBeingEdited = ref(null)
  const editedContent = ref('')
  const editError = ref(null)
  const isSavingEdit = ref(false) // add saving state
  // Bulk selection state
  const isDeletingMultiple = ref(false)
  const selectedMessages = ref([])
  const showBulkDeleteModal = ref(false)

  // Computed properties
  const hasSelectedMessages = computed(() => selectedMessages.value.length > 0)
  const selectedCount = computed(() => selectedMessages.value.length)

  // Message editing functions
  const startEditing = (message) => {
    // Can only edit user messages
    if (message.role !== 'user') {
      console.warn('[MessageActions] cannot edit non-user message')
      return
    }

    messageBeingEdited.value = message
    editedContent.value = message.content
    isEditing.value = true
    editError.value = null
  }

  const cancelEditing = () => {
    isEditing.value = false
    messageBeingEdited.value = null
    editedContent.value = ''
    editError.value = null
  }

  // Modify saveEdit to accept newContent
  const saveEdit = async (newContent) => {
    // If content passed from editor, update editedContent
    if (newContent !== undefined) {
      editedContent.value = newContent.trim()
    }

    if (!editedContent.value) {
      editError.value = 'Message cannot be empty'
      return
    }

    try {
      isSavingEdit.value = true
      // Update in the store/backend
      await chatStore.updateMessage(
        messageBeingEdited.value.chat_id,
        messageBeingEdited.value.id,
        editedContent.value,
      )

      // Reset editing state
      cancelEditing()
    } catch (error) {
      console.error('[MessageActions] Error updating message:', error)
      editError.value = 'Failed to update message'
      toastStore.error('Failed to update message')
    } finally {
      isSavingEdit.value = false
    }
  }
  // Message deletion functions
  const deleteMessage = async (message) => {
    console.log('[MessageActions] deleteMessage', message)

    await chatStore.deleteMessage(message.chat_id, message.id)
    console.log('[MessageActions] message deleted successfully')
  }

  // Bulk selection functions
  const toggleMessageSelection = (message) => {
    const index = selectedMessages.value.findIndex((m) => m.id === message.id)

    if (index === -1) {
      selectedMessages.value.push(message)
    } else {
      selectedMessages.value.splice(index, 1)
    }
  }

  const isMessageSelected = (message) => {
    return selectedMessages.value.some((m) => m.id === message.id)
  }

  const clearSelectedMessages = () => {
    selectedMessages.value = []
  }

  const confirmBulkDelete = () => {
    if (selectedMessages.value.length === 0) return
    showBulkDeleteModal.value = true
  }

  const bulkDeleteMessages = async () => {
    if (selectedMessages.value.length === 0) return

    try {
      const chatId = selectedMessages.value[0].chat_id
      const messageIds = selectedMessages.value.map((message) => message.id)

      await chatStore.bulkDeleteMessages(chatId, messageIds)

      // Reset state
      clearSelectedMessages()
      showBulkDeleteModal.value = false
    } catch (error) {
      console.error('Error bulk deleting messages:', error)
    }
  }

  return {
    // Editing state
    isEditing,
    messageBeingEdited,
    editedContent,
    editError,
    isSavingEdit, // add saving state to return

    // Bulk selection state
    selectedMessages,
    showBulkDeleteModal,
    hasSelectedMessages,
    selectedCount,

    // Editing functions
    startEditing,
    cancelEditing,
    saveEdit,

    // Deletion functions
    deleteMessage,

    // Bulk selection functions
    toggleMessageSelection,
    isMessageSelected,
    clearSelectedMessages,
    confirmBulkDelete,
    bulkDeleteMessages,
  }
}
