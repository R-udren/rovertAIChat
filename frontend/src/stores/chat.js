// Chat store
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)

  const authStore = useAuthStore()

  // Placeholder function for sending messages
  // In a real app, this would connect to a chat API endpoint
  async function sendMessage(text) {
    if (!authStore.isAuthenticated || !currentConversation.value) return null

    loading.value = true
    error.value = null

    try {
      // Add user message to the list
      const userMessage = {
        id: Date.now().toString(),
        content: text,
        role: 'user',
        timestamp: new Date().toISOString(),
      }

      messages.value.push(userMessage)

      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Simulate AI response
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        content: `This is a simulated AI response to: "${text}"`,
        role: 'assistant',
        timestamp: new Date().toISOString(),
      }

      messages.value.push(aiMessage)

      return aiMessage
    } catch (err) {
      error.value = err.message
      console.error('Message send error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Start a new conversation
  function startNewConversation() {
    const newConversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      timestamp: new Date().toISOString(),
    }

    conversations.value.unshift(newConversation)
    currentConversation.value = newConversation
    messages.value = []

    return newConversation
  }

  // Select an existing conversation
  function selectConversation(conversationId) {
    const conversation = conversations.value.find((c) => c.id === conversationId)
    if (conversation) {
      currentConversation.value = conversation
      // In a real app, you would fetch messages for this conversation from the API
      messages.value = [] // Placeholder - would load actual messages
    }
  }

  // Reset chat state
  function resetChat() {
    conversations.value = []
    currentConversation.value = null
    messages.value = []
    error.value = null
  }

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    error,
    sendMessage,
    startNewConversation,
    selectConversation,
    resetChat,
  }
})
