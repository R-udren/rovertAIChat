// Composable for handling delete operations and modals
import { useChatStore } from '@/stores/chat'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export function useChatDeletion() {
  const chatStore = useChatStore()
  const router = useRouter()

  const showDeleteModal = ref(false)
  const deleteModalType = ref('single') // 'single' or 'multiple'
  const chatToDelete = ref(null)

  // Delete chat
  const deleteChat = async (chatId) => {
    chatToDelete.value = chatId
    deleteModalType.value = 'single'
    showDeleteModal.value = true
  }

  const deleteChats = async () => {
    deleteModalType.value = 'multiple'
    showDeleteModal.value = true
  }

  // Modal confirmation handlers
  const confirmDeleteModal = async () => {
    try {
      let success = false

      if (deleteModalType.value === 'single' && chatToDelete.value) {
        success = await chatStore.deleteChat(chatToDelete.value)

        if (success && chatToDelete.value === chatStore.currentConversation?.id) {
          router.push('/chat')
        }
      } else if (deleteModalType.value === 'multiple') {
        success = await chatStore.deleteChats()

        // Always redirect to chat home when all chats are deleted
        if (success) {
          router.push('/chat')
        }
      }
    } catch (error) {
      console.error('Error during delete operation:', error)
    } finally {
      // Reset modal state
      showDeleteModal.value = false
      chatToDelete.value = null
      deleteModalType.value = 'single'
    }
  }

  const cancelDelete = () => {
    showDeleteModal.value = false
    chatToDelete.value = null
    deleteModalType.value = 'single'
  }

  return {
    showDeleteModal,
    deleteModalType,
    chatToDelete,
    deleteChat,
    deleteChats,
    confirmDeleteModal,
    cancelDelete,
  }
}
