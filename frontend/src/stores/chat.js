// Chat store
import { api } from '@/services/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import { useToastStore } from './toast'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([]) // Stores messages for the currentConversation
  const loading = ref(false) // For initial message loading
  const sending = ref(false) // For sending a new message
  const streaming = ref(false) // For streaming response
  const error = ref(null)
  const toastStore = useToastStore()
  const authStore = useAuthStore()

  // EventSource for streaming responses
  let eventSource = null

  // Helper function to add system error message
  function addSystemErrorMessage(errorMessage) {
    addSystemMessage(errorMessage, 'error')
  }

  // Helper function to add system message (info or error)
  function addSystemMessage(content, type = 'info') {
    const systemMessage = {
      id: `system-${type}-${Date.now()}`,
      content: content,
      role: 'system',
      isError: type === 'error',
      timestamp: new Date().toISOString(),
    }
    messages.value.push(systemMessage)
  }

  // Get all user chats
  async function fetchChats() {
    try {
      loading.value = true
      error.value = null

      const response = await api.get('/chats/my')

      conversations.value = response.chats || []

      return response.chats
    } catch (err) {
      error.value = 'Failed to load chats'
      toastStore.error('Failed to load chat history')
      console.error('Error fetching chats:', err)
    } finally {
      loading.value = false
    }
  }

  // Get a specific chat
  async function loadChat(chatId) {
    try {
      loading.value = true
      error.value = null

      const response = await api.get(`/chats/chat/${chatId}`)

      currentConversation.value = response.chat
      messages.value = response.messages.map((msg) => ({
        id: msg.id,
        chat_id: response.chat.id, // ensure chat_id is present
        content: msg.content,
        thinking: msg.thinking,
        role: msg.role,
        timestamp: msg.created_at,
        model_id: msg.model_id,
        tokens_used: msg.tokens_used,
      }))

      return response
    } catch (err) {
      error.value = 'Failed to load chat'
      toastStore.error('Failed to load chat messages')
      console.error('Error loading chat:', err)
    } finally {
      loading.value = false
    }
  }

  // Create a new chat
  async function startNewConversation() {
    try {
      loading.value = true
      error.value = null

      const response = await api.post('/chats/my')

      currentConversation.value = response
      messages.value = []

      // Add to conversations list
      conversations.value.unshift(response)

      return response
    } catch (err) {
      error.value = 'Failed to create new chat'
      toastStore.error('Failed to create new chat')
      console.error('Error creating chat:', err)
    } finally {
      loading.value = false
    }
  }

  // Update chat (title, archived status)
  async function updateChat(chatId, updates) {
    try {
      const response = await api.patch(`/chats/chat/${chatId}`, updates)

      // Update in conversations list
      const index = conversations.value.findIndex((c) => c.id === chatId)
      if (index !== -1) {
        conversations.value[index] = { ...conversations.value[index], ...updates }
      }

      // Update current conversation if it's the one being edited
      if (currentConversation.value?.id === chatId) {
        currentConversation.value = { ...currentConversation.value, ...updates }
      }

      return response
    } catch (err) {
      toastStore.error('Failed to update chat')
      console.error('Error updating chat:', err)
    }
  }

  // Delete chat
  async function deleteChat(chatId) {
    try {
      await api.delete(`/chats/chat/${chatId}`)

      // Remove from conversations list
      conversations.value = conversations.value.filter((c) => c.id !== chatId)

      // Reset current conversation if it was the one deleted
      if (currentConversation.value?.id === chatId) {
        currentConversation.value = null
        messages.value = []
      }

      toastStore.success('Chat deleted successfully')
      return true
    } catch (err) {
      toastStore.error('Failed to delete chat')
      console.error('Error deleting chat:', err)
      return false
    }
  }

  async function deleteChats() {
    try {
      await api.delete('/chats/my')
      conversations.value = []
      currentConversation.value = null
      messages.value = []
      toastStore.success('All chats deleted successfully')
      return true
    } catch (err) {
      toastStore.error('Failed to delete all chats')
      console.error('Error deleting all chats:', err)
      return false
    }
  }

  // Send message
  async function sendMessage(message, model, think = true) {
    if (!message) {
      toastStore.error('Message cannot be empty')
      return
    }

    if (!model) {
      toastStore.error('Model is required')
      return
    }

    if (!authStore.isAuthenticated) {
      toastStore.error('You must be logged in to send messages')
      return
    }

    // Auto-create conversation if none exists
    if (!currentConversation.value) {
      try {
        await startNewConversation()
        if (!currentConversation.value) {
          toastStore.error('Failed to create new conversation')
          return
        }
      } catch (err) {
        toastStore.error('Failed to create new conversation')
        console.error('Error creating conversation:', err)
        return
      }
    }

    error.value = null
    try {
      sending.value = true

      const messageInDb = await api.post(`/chats/${currentConversation.value.id}/messages`, {
        content: message,
        role: 'user',
      })
      messages.value.push(messageInDb)

      // Add a temporary loading message
      const loadingMessageId = `loading-${Date.now()}`
      const loadingMessage = {
        id: loadingMessageId,
        content: '',
        role: 'assistant',
        isLoading: true,
        timestamp: new Date().toISOString(),
      }
      messages.value.push(loadingMessage)

      // Send request to Ollama API with the chatId
      const response = await api.post('ollama/chat', {
        chatId: currentConversation.value.id,
        messages: messages.value
          .filter((msg) => !msg.isLoading) // Don't include the loading placeholder
          .map((msg) => ({
            role: msg.role,
            content: msg.content,
            thinking: msg.thinking,
          })),
        model: model,
        stream: false,
        think: undefined, // TODO: Implement later
      })

      // Replace the loading message with the actual response
      const loadingIndex = messages.value.findIndex((m) => m.id === loadingMessageId)
      if (loadingIndex !== -1) {
        messages.value.splice(loadingIndex, 1)
      }

      // Update chat title if it was auto-generated from the first message
      if (response.chat && response.chat.title && currentConversation.value) {
        currentConversation.value.title = response.chat.title

        // Update the title in the conversations list as well
        const conversationIndex = conversations.value.findIndex(
          (c) => c.id === currentConversation.value.id,
        )
        if (conversationIndex !== -1) {
          conversations.value[conversationIndex].title = response.chat.title
        }
      }

      // Create the assistant message using the ID returned from the backend
      const assistantMessage = {
        id: response.id,
        chat_id: currentConversation.value.id, // add chat_id for assistant message
        model: response.model,
        content: response.message.content,
        thinking: response.message.thinking, // (for thinking models) the model's thinking process
        role: 'assistant',
        timestamp: new Date().toISOString(),
      }
      console.log('Assistant message:', assistantMessage)
      messages.value.push(assistantMessage)
    } catch (err) {
      error.value = 'Failed to send message'

      // Remove the loading message
      const loadingIndex = messages.value.findIndex((m) => m.isLoading)
      if (loadingIndex !== -1) {
        messages.value.splice(loadingIndex, 1)
      }

      // Add system error message to chat
      let errorMessage = 'Failed to get response from Ollama'

      // Try to extract more specific error message
      if (err.response?.data?.details) {
        errorMessage = `Ollama Error: ${err.response.data.details}`
      } else if (err.response?.data?.error) {
        errorMessage = `Error: ${err.response.data.error}`
      } else if (err.message) {
        errorMessage = `Connection Error: ${err.message}`
      }

      addSystemErrorMessage(errorMessage)

      toastStore.error('Failed to send message')
      console.error('Error sending message:', err)
    } finally {
      sending.value = false
    }
  }

  // Delete message
  async function deleteMessage(chatId, messageId) {
    try {
      await api.delete(`/chats/${chatId}/messages/${messageId}`)

      // Remove from messages array
      messages.value = messages.value.filter((msg) => msg.id !== messageId)

      toastStore.success('Message deleted successfully')
      return true
    } catch (err) {
      toastStore.error('Failed to delete message')
      console.error('Error deleting message:', err)
      return false
    }
  }

  // Bulk delete messages
  async function bulkDeleteMessages(chatId, messageIds) {
    try {
      await api.delete(`/chats/${chatId}/messages/bulk`, {
        message_ids: messageIds,
      })

      // Remove from messages array
      messages.value = messages.value.filter((msg) => !messageIds.includes(msg.id))

      const count = messageIds.length
      toastStore.success(`${count} message${count !== 1 ? 's' : ''} deleted successfully`)
      return true
    } catch (err) {
      toastStore.error('Failed to delete messages')
      console.error('Error deleting messages:', err)
      return false
    }
  }

  // Update message
  async function updateMessage(chatId, messageId, content, images = null, metadata = null) {
    try {
      const updateData = { content }
      if (images !== null) updateData.images = images
      if (metadata !== null) updateData.extended_metadata = metadata

      const response = await api.patch(`/chats/${chatId}/messages/${messageId}`, updateData)

      // Update in messages array without replacing object
      const msg = messages.value.find((m) => m.id === messageId)
      if (msg) {
        msg.content = content
        msg.isEdited = true
        if (images !== null) msg.images = images
        if (metadata !== null) msg.extended_metadata = metadata
      }

      toastStore.success('Message updated successfully')
      return response
    } catch (err) {
      toastStore.error('Failed to update message')
      console.error('Error updating message:', err)
      throw err
    }
  }

  // Close event source
  function closeEventSource() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    streaming.value = false

    // Mark any streaming messages as complete
    messages.value.forEach((msg) => {
      if (msg.isStreaming) {
        msg.isStreaming = false
      }
    })
  }

  // Select a conversation
  async function selectConversation(conversation) {
    closeEventSource()
    currentConversation.value = conversation

    if (conversation) {
      await loadChat(conversation.id)
    } else {
      messages.value = []
    }
  }

  // Reset chat state
  function resetChat() {
    closeEventSource()
    currentConversation.value = null
    messages.value = []
    error.value = null
  }

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    sending,
    streaming,
    error,
    fetchChats,
    loadChat,
    startNewConversation,
    updateChat,
    deleteChat,
    deleteChats,
    deleteMessage,
    bulkDeleteMessages,
    updateMessage,
    sendMessage,
    selectConversation,
    resetChat,
    closeEventSource,
    addSystemErrorMessage,
    addSystemMessage,
  }
})
