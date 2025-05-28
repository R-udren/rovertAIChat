<script setup>
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'
import { useToastStore } from '@/stores/toast'
import { useUserSettingsStore } from '@/stores/userSettings'

const chatStore = useChatStore()
const toastStore = useToastStore()
const authStore = useAuthStore()
const userSettingsStore = useUserSettingsStore()
const modelsStore = useModelsStore()
const route = useRoute()
const router = useRouter()
const selectedModel = ref(chatStore.currentConversation?.model)

const messageInput = ref('')
const chatContainerRef = ref(null)
const chatInputRef = ref(null)
const showSidebar = ref(
  localStorage.getItem('sidebarVisible') !== null
    ? localStorage.getItem('sidebarVisible') === 'true'
    : window.innerWidth >= 1024,
)
const isSubmitting = computed(() => chatStore.sending || chatStore.streaming)
const isMobileSidebarOpen = ref(false)

// Toggle sidebar
const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
  localStorage.setItem('sidebarVisible', showSidebar.value.toString())
}

// Toggle mobile sidebar
const toggleMobileSidebar = () => {
  isMobileSidebarOpen.value = !isMobileSidebarOpen.value
}

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
const sendMessage = async () => {
  if (!messageInput.value.trim() || isSubmitting.value) {
    console.warn('Message input is empty or already submitting')
    return
  }

  const message = messageInput.value
  messageInput.value = ''

  // Reset textarea height through the ChatInput component
  if (chatInputRef.value) {
    chatInputRef.value.resetTextareaHeight()
  }

  const model = localStorage.getItem('preferredModel') || selectedModel.value

  // Check if streaming is enabled in user settings
  const useStreaming = userSettingsStore.settings?.preferences?.streamingEnabled ?? false

  if (useStreaming) {
    await chatStore.streamChatResponse(message, model)
  } else {
    await chatStore.sendMessage(message, model)
  }

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

  // Close mobile sidebar if open
  if (isMobileSidebarOpen.value) {
    isMobileSidebarOpen.value = false
  }
}

// Select conversation
const selectChat = async (conversation) => {
  if (conversation.id === chatStore.currentConversation?.id) {
    // If selecting the current conversation, just close the sidebar on mobile
    if (isMobileSidebarOpen.value) {
      isMobileSidebarOpen.value = false
    }
    return
  }

  await chatStore.selectConversation(conversation)
  router.push(`/chat/${conversation.id}`)
  scrollToBottom()

  // Close mobile sidebar with a slight delay to ensure navigation completes first
  if (isMobileSidebarOpen.value) {
    setTimeout(() => {
      isMobileSidebarOpen.value = false
    }, 150)
  }
}

// Delete chat
const deleteChat = async (chatId) => {
  if (confirm('Are you sure you want to delete this conversation?')) {
    const success = await chatStore.deleteChat(chatId)

    if (success && chatId === chatStore.currentConversation?.id) {
      router.push('/chat')
    }
  }
}

// Update chat title
const updateChatTitle = async (chatId, newTitle) => {
  if (!chatId || !newTitle.trim()) return

  await chatStore.updateChat(chatId, { title: newTitle.trim() })
}

// Load chats and set initial chat
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    toastStore.error('Please log in to use the chat feature')
    router.push('/login')
    return
  }

  // Load user settings
  await userSettingsStore.fetchSettings()

  // Initialize models store and check Ollama status
  await modelsStore.fetchModels()

  // Load user chats
  await chatStore.fetchChats()

  // If route has chat ID, load that chat
  if (route.params.id) {
    const chatId = route.params.id
    const conversation = chatStore.conversations.find((c) => c.id === chatId)

    if (conversation) {
      await chatStore.selectConversation(conversation)
    } else {
      // Chat ID not found, redirect to chat home
      router.push('/chat')
    }
  } else if (chatStore.conversations.length > 0) {
    // Load most recent chat
    await chatStore.selectConversation(chatStore.conversations[0])
    router.push(`/chat/${chatStore.conversations[0].id}`)
  }

  // Initial scroll to bottom
  scrollToBottom()
})

// Clean up when component unmounts
onUnmounted(() => {
  chatStore.closeEventSource()
})

// Watch for message changes to scroll to bottom
watch(
  () => chatStore.messages,
  () => {
    scrollToBottom()
  },
  { deep: true },
)

// Watch for route changes to load appropriate chat
watch(
  () => route.params.id,
  async (newId) => {
    if (newId && newId !== chatStore.currentConversation?.id) {
      const conversation = chatStore.conversations.find((c) => c.id === newId)

      if (conversation) {
        await chatStore.selectConversation(conversation)
      } else {
        router.push('/chat')
      }
    }
  },
)

// Watch for Ollama status changes to show system messages
watch(
  () => modelsStore.ollamaStatus,
  (newStatus, oldStatus) => {
    // Only show messages after initial load and when status actually changes
    if (oldStatus && oldStatus !== newStatus && chatStore.currentConversation) {
      if (newStatus === 'offline' || newStatus === 'no-models') {
        chatStore.addSystemErrorMessage(
          'Ollama is currently unavailable. Please check your connection and try again.',
        )
      } else if (newStatus === 'online' && (oldStatus === 'offline' || oldStatus === 'no-models')) {
        chatStore.addSystemMessage('Ollama is now available.', 'info')
      }
    }
  },
)

const handleModelChange = (model) => {
  console.log('Model changed to:', model)
  selectedModel.value = model
  if (chatStore.currentConversation) {
    chatStore.currentConversation.model = model
  }
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-64px)] w-full bg-zinc-900">
    <!-- Mobile Header -->
    <ChatHeader
      :current-conversation="chatStore.currentConversation"
      :selected-model="selectedModel"
      :is-mobile="true"
      @toggle-mobile-sidebar="toggleMobileSidebar"
      @start-new-chat="startNewChat"
      @model-changed="handleModelChange"
      @update-chat-title="updateChatTitle"
    />

    <div class="flex flex-1 w-full overflow-hidden">
      <!-- Sidebar - Always render for proper mobile support -->
      <ChatSidebar
        :show-sidebar="showSidebar"
        :is-mobile-sidebar-open="isMobileSidebarOpen"
        :conversations="chatStore.conversations"
        :current-conversation="chatStore.currentConversation"
        :loading="chatStore.loading"
        @toggle-mobile-sidebar="toggleMobileSidebar"
        @start-new-chat="startNewChat"
        @select-chat="selectChat"
        @delete-chat="deleteChat"
        @update-chat-title="updateChatTitle"
      />

      <!-- Chat Area -->
      <div class="flex flex-col flex-1 w-full overflow-hidden">
        <!-- Desktop Header -->
        <ChatHeader
          :current-conversation="chatStore.currentConversation"
          :selected-model="selectedModel"
          :is-mobile="false"
          @toggle-sidebar="toggleSidebar"
          @start-new-chat="startNewChat"
          @model-changed="handleModelChange"
          @update-chat-title="updateChatTitle"
        />

        <!-- Ollama Status Indicator -->
        <div
          v-if="!modelsStore.isOllamaAvailable || modelsStore.ollamaStatus === 'loading'"
          class="px-4 py-2 border-b bg-zinc-800/50 border-zinc-700/50"
        >
          <OllamaStatusIndicator :compact="true" />
        </div>

        <!-- Messages -->
        <ChatContainer
          ref="chatContainerRef"
          :current-conversation="chatStore.currentConversation"
          :messages="chatStore.messages"
          :loading="chatStore.loading"
          :streaming="chatStore.streaming"
          @start-new-chat="startNewChat"
        />

        <!-- Input Area -->
        <ChatInput
          ref="chatInputRef"
          v-model:message-input="messageInput"
          :is-submitting="isSubmitting"
          @send-message="sendMessage"
        />
      </div>
    </div>
  </div>
</template>
