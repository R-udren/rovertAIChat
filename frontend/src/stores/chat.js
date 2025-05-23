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

  // Get all user chats
  async function fetchChats() {
    try {
      loading.value = true
      error.value = null

      const response = await api.get('/chats')

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

      const response = await api.get(`/chats/${chatId}`)

      currentConversation.value = response.chat
      messages.value = response.messages.map((msg) => ({
        id: msg.id,
        content: msg.content,
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

      const response = await api.post('/chats')

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
      const response = await api.patch(`/chats/${chatId}`, updates)

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
      await api.delete(`/chats/${chatId}`)

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

  async function sendMessage(message, model) {
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
      }

      messages.value.push(userMessage)
      sending.value = true

      // Send request to Ollama API with the chatId
      const response = await api.post('ollama/chat', {
        chatId: currentConversation.value.id,
        messages: messages.value.map((msg) => ({
          role: msg.role,
          content: msg.content,
        })),
        model: model,
        stream: false,
      })
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

  // Stream chat response
  async function streamChatResponse(message, model) {
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
        assistantMessage.isStreaming = false
        streaming.value = false
        closeEventSource()
        error.value = 'Connection error during streaming'
        toastStore.error('Connection error occurred')
      }
    } catch (err) {
      error.value = 'Failed to initiate streaming'
      toastStore.error('Failed to connect to streaming API')
      console.error('Error setting up streaming:', err)
      streaming.value = false
    }
  }

  // Stream chat response
  async function streamChatResponse(message, model) {
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

      // Prepare payload for streaming endpoint
      const payload = {
        chatId: currentConversation.value.id,
        messages: messages.value
          .filter((msg) => !msg.isStreaming) // Don't include the placeholder
          .map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        model: model,
        stream: true,
      }

      // Create event source for streaming
      const queryParams = new URLSearchParams({
        payload: JSON.stringify(payload),
      }).toString()

      eventSource = new EventSource(`${api.baseUrl}/ollama/chat/stream?${queryParams}`)

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
        assistantMessage.isStreaming = false
        streaming.value = false
        closeEventSource()
        error.value = 'Connection error during streaming'
        toastStore.error('Connection error occurred')
      }
    } catch (err) {
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
    sendMessage,
    streamChatResponse,
    selectConversation,
    resetChat,
    closeEventSource,
  }
})
