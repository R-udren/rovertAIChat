// Composable for handling chat operations
import { useChatStore } from '@/stores/chat'
import { computed, nextTick, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useChatOperations() {
  const chatStore = useChatStore()
  const route = useRoute()
  const router = useRouter()

  const messageInput = ref('')
  const chatContainerRef = ref(null)
  const chatInputRef = ref(null)
  const selectedModel = ref(chatStore.currentConversation?.model)

  const isSubmitting = computed(() => chatStore.sending || chatStore.streaming)

  // Scroll to bottom of chat
  const scrollToBottom = async () => {
    if (!chatContainerRef.value?.scrollContainer) return

    // Wait for DOM update
    await nextTick()

    // Smooth scroll to bottom
    chatContainerRef.value.scrollContainer.scrollTo({
      top: chatContainerRef.value.scrollContainer.scrollHeight,
      behavior: 'smooth',
    })
  }

  // Send message
  const sendMessage = async (images = []) => {
    if (!messageInput.value.trim() || isSubmitting.value) {
      console.warn('Message input is empty or already submitting')
      return
    }

    const message = messageInput.value
    const model = localStorage.getItem('preferredModel') || selectedModel.value

    messageInput.value = ''

    // Reset textarea height through the ChatInput component
    if (chatInputRef.value) {
      chatInputRef.value.resetTextareaHeight()
    }

    await chatStore.sendMessage(message, model, images)

    // If a new conversation was created, navigate to it
    if (chatStore.currentConversation && route.path === '/chat') {
      router.push(`/chat/${chatStore.currentConversation.id}`)
    }

    scrollToBottom()
  }

  // Start new chat
  const startNewChat = async () => {
    await chatStore.startNewConversation()
    router.push(`/chat/${chatStore.currentConversation.id}`)
    scrollToBottom()
  }

  // Select conversation
  const selectChat = async (conversation) => {
    if (conversation.id === chatStore.currentConversation?.id) {
      return
    }

    await chatStore.selectConversation(conversation)
    router.push(`/chat/${conversation.id}`)
    scrollToBottom()
  }

  // Update chat title
  const updateChatTitle = async (chatId, newTitle) => {
    if (!chatId || !newTitle.trim()) return
    await chatStore.updateChat(chatId, { title: newTitle.trim() })
  }

  // Handle model change
  const handleModelChange = (model) => {
    console.log('Model changed to:', model)
    selectedModel.value = model
    if (chatStore.currentConversation) {
      chatStore.currentConversation.model = model
    }
  }

  return {
    messageInput,
    chatContainerRef,
    chatInputRef,
    selectedModel,
    isSubmitting,
    scrollToBottom,
    sendMessage,
    startNewChat,
    selectChat,
    updateChatTitle,
    handleModelChange,
  }
}
