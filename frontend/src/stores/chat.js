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
        content: msg.content,
        role: msg.role,
        timestamp: msg.created_at,
        model_id: msg.model_id,
        tokens_used: msg.tokens_used,
        images: msg.images, // Include images for multimodal messages
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

  // Send message with optional images
  async function sendMessage(message, model, images = []) {
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
      const userMessage = {
        id: Date.now().toString(),
        content: message,
        role: 'user',
        timestamp: new Date().toISOString(),
        images: images.length > 0 ? images : undefined,
      }

      messages.value.push(userMessage)
      sending.value = true

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
            images: msg.images, // Include images in the request
          })),
        model: model,
        stream: false,
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
        id: response.id, // This ID comes from the database now
        content: response.message.content,
        role: 'assistant',
        timestamp: new Date().toISOString(),
      }
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

  // Stream chat response with optional images
  async function streamChatResponse(message, model, images = []) {
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

    // Close any existing connection
    closeEventSource()

    error.value = null
    try {
      const userMessage = {
        id: Date.now().toString(),
        content: message,
        role: 'user',
        timestamp: new Date().toISOString(),
        images: images.length > 0 ? images : undefined,
      }

      messages.value.push(userMessage)
      streaming.value = true

      // Create a placeholder for the streaming response
      const assistantMessage = {
        id: null, // Will be updated from the stream
        content: '',
        role: 'assistant',
        isStreaming: true,
        timestamp: new Date().toISOString(),
      }

      messages.value.push(assistantMessage)

      // Create the API URL for the EventSource
      const queryParams = encodeURIComponent(
        JSON.stringify({
          chatId: currentConversation.value.id,
          messages: messages.value
            .filter((msg) => !msg.isStreaming) // Don't include the placeholder
            .map((msg) => ({
              role: msg.role,
              content: msg.content,
              images: msg.images, // Include images in streaming request
            })),
          model: model,
        }),
      )

      const streamUrl = `${api.baseUrl}/ollama/chat/stream?payload=${queryParams}`

      eventSource = new EventSource(streamUrl)

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Update the message ID if it's the first chunk
          if (data.id && !assistantMessage.id) {
            assistantMessage.id = data.id
          }

          // Append content if any
          if (data.content) {
            assistantMessage.content += data.content
          }

          // Handle stream completion
          if (data.done) {
            assistantMessage.isStreaming = false
            streaming.value = false
            closeEventSource()
          }
        } catch (err) {
          console.error('Error parsing event data:', err)
        }
      }

      eventSource.onerror = (err) => {
        console.error('EventSource error:', err)

        // Remove the streaming placeholder message
        if (assistantMessage.isStreaming) {
          const messageIndex = messages.value.findIndex((m) => m === assistantMessage)
          if (messageIndex !== -1) {
            messages.value.splice(messageIndex, 1)
          }
        }

        // Add system error message
        addSystemErrorMessage('Connection lost during streaming. Please try again.')

        assistantMessage.isStreaming = false
        streaming.value = false
        closeEventSource()
        error.value = 'Connection error during streaming'
        toastStore.error('Connection error occurred')
      }
    } catch (err) {
      // Remove the streaming placeholder message if it was added
      if (assistantMessage && assistantMessage.isStreaming) {
        const messageIndex = messages.value.findIndex((m) => m === assistantMessage)
        if (messageIndex !== -1) {
          messages.value.splice(messageIndex, 1)
        }
      }

      // Add system error message
      let errorMessage = 'Failed to connect to streaming API'
      if (err.response?.data?.details) {
        errorMessage = `Ollama Error: ${err.response.data.details}`
      } else if (err.response?.data?.error) {
        errorMessage = `Error: ${err.response.data.error}`
      } else if (err.message) {
        errorMessage = `Connection Error: ${err.message}`
      }

      addSystemErrorMessage(errorMessage)

      error.value = 'Failed to initiate streaming'
      toastStore.error('Failed to connect to streaming API')
      console.error('Error setting up streaming:', err)
      streaming.value = false
    }
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
    sendMessage,
    streamChatResponse,
    selectConversation,
    resetChat,
    closeEventSource,
    addSystemErrorMessage,
    addSystemMessage,
  }
})
