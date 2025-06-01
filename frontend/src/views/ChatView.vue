<script setup>
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'
import { useToastStore } from '@/stores/toast'
import { useUserSettingsStore } from '@/stores/userSettings'

// Lazy load chat components for faster initial route transition
const ChatHeader = defineAsyncComponent(() => import('@/components/Chat/ChatHeader.vue'))
const ChatSidebar = defineAsyncComponent(() => import('@/components/Chat/ChatSidebar.vue'))
const ChatContainer = defineAsyncComponent(() => import('@/components/Chat/ChatContainer.vue'))
const ChatInput = defineAsyncComponent(() => import('@/components/Chat/ChatInput.vue'))
const OllamaStatusIndicator = defineAsyncComponent(
  () => import('@/components/Chat/OllamaStatusIndicator.vue'),
)
const ConfirmationModal = defineAsyncComponent(
  () => import('@/components/UI/ConfirmationModal.vue'),
)

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

// Loading states for lazy loading
const isInitializing = ref(true)
const isLoadingSettings = ref(true)
const isLoadingModels = ref(true)
const isLoadingChats = ref(true)

// Image support
const currentImages = ref([])
const canUploadImages = computed(() => {
  if (!selectedModel.value) return false
  return modelsStore.hasVisionCapability(selectedModel.value)
})

// Drag and drop state for entire chat area
const isDragOverChat = ref(false)
const isProcessingImages = ref(false)

// Delete modal state
const showDeleteModal = ref(false)
const deleteModalType = ref('single') // 'single' or 'multiple'
const chatToDelete = ref(null)

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
  const images = [...currentImages.value] // Copy current images
  messageInput.value = ''
  currentImages.value = [] // Clear images after sending

  // Reset textarea height through the ChatInput component
  if (chatInputRef.value) {
    chatInputRef.value.resetTextareaHeight()
  }

  const model = localStorage.getItem('preferredModel') || selectedModel.value

  // Check if streaming is enabled in user settings
  const useStreaming = userSettingsStore.settings?.preferences?.streamingEnabled ?? false

  if (useStreaming) {
    await chatStore.streamChatResponse(message, model, images)
  } else {
    await chatStore.sendMessage(message, model, images)
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
  chatToDelete.value = chatId
  deleteModalType.value = 'single'
  showDeleteModal.value = true
}

const deleteChats = async () => {
  deleteModalType.value = 'multiple'
  showDeleteModal.value = true
}

// Modal confirmation handlers
const confirmDeleteModel = async () => {
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

  // Start initialization tasks in parallel for faster loading
  initializeChat()
})

// Initialize chat data asynchronously without blocking route
const initializeChat = async () => {
  try {
    // Start all initialization tasks in parallel
    const [settingsPromise, modelsPromise, chatsPromise] = [
      loadUserSettings(),
      loadModels(),
      loadChats(),
    ]

    // Wait for all to complete
    await Promise.all([settingsPromise, modelsPromise, chatsPromise])

    // Handle route-specific chat loading
    await handleInitialChatSelection()
  } catch (error) {
    console.error('Error during chat initialization:', error)
    toastStore.error('Failed to initialize chat. Please refresh the page.')
  } finally {
    isInitializing.value = false
    // Initial scroll to bottom after everything is loaded
    scrollToBottom()
  }
}

// Load user settings
const loadUserSettings = async () => {
  try {
    await userSettingsStore.fetchSettings()
  } catch (error) {
    console.error('Error loading user settings:', error)
  } finally {
    isLoadingSettings.value = false
  }
}

// Load models
const loadModels = async () => {
  try {
    await modelsStore.fetchModels()
  } catch (error) {
    console.error('Error loading models:', error)
  } finally {
    isLoadingModels.value = false
  }
}

// Load chats
const loadChats = async () => {
  try {
    await chatStore.fetchChats()
  } catch (error) {
    console.error('Error loading chats:', error)
  } finally {
    isLoadingChats.value = false
  }
}

// Handle initial chat selection based on route
const handleInitialChatSelection = async () => {
  // Wait for chats to be loaded before proceeding
  if (isLoadingChats.value) {
    await new Promise((resolve) => {
      const unwatch = watch(
        () => isLoadingChats.value,
        (loading) => {
          if (!loading) {
            unwatch()
            resolve()
          }
        },
      )
    })
  }

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
}

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

// Handle images changed from ChatInput
const handleImagesChanged = (images) => {
  currentImages.value = images
}

// Convert file to base64
const convertToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      // Remove the data:image/...;base64, prefix
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// Process image files for drag-and-drop
const processImageFiles = async (files) => {
  if (!canUploadImages.value) {
    toastStore.error('Selected model does not support image uploads')
    return
  }

  if (files.length === 0) return

  isProcessingImages.value = true

  try {
    const imageFiles = files.filter((file) => file.type.startsWith('image/'))

    if (imageFiles.length === 0) {
      toastStore.error('Please select image files only')
      return
    }

    if (imageFiles.length > 5) {
      toastStore.error('Maximum 5 images allowed per message')
      return
    }

    const totalSize = imageFiles.reduce((sum, file) => sum + file.size, 0)
    const maxSize = 10 * 1024 * 1024 // 10MB total

    if (totalSize > maxSize) {
      toastStore.error('Total image size cannot exceed 10MB')
      return
    }

    const base64Images = await Promise.all(
      imageFiles.map(async (file) => {
        try {
          return await convertToBase64(file)
        } catch (error) {
          console.error('Error converting file to base64:', error)
          throw new Error(`Failed to process ${file.name}`)
        }
      }),
    )

    currentImages.value = [...currentImages.value, ...base64Images]

    // Update ChatInput component
    if (chatInputRef.value) {
      chatInputRef.value.addImages(base64Images)
    }

    toastStore.success(`${imageFiles.length} image(s) uploaded successfully`)
  } catch (error) {
    console.error('Error processing images:', error)
    toastStore.error(error.message || 'Failed to process images')
  } finally {
    isProcessingImages.value = false
  }
}

// Handle drag and drop events for entire chat area
const handleChatDragOver = (event) => {
  if (!canUploadImages.value) return
  event.preventDefault()
  event.dataTransfer.dropEffect = 'copy'
  isDragOverChat.value = true
}

const handleChatDragLeave = (event) => {
  if (!canUploadImages.value) return
  // Only hide overlay if leaving the main container
  if (!event.currentTarget.contains(event.relatedTarget)) {
    isDragOverChat.value = false
  }
}

const handleChatDrop = async (event) => {
  if (!canUploadImages.value) return
  event.preventDefault()
  isDragOverChat.value = false

  const files = Array.from(event.dataTransfer.files)
  if (files.length > 0) {
    await processImageFiles(files)
  }
}

// Clear images when switching from vision to non-vision model
const handleModelChange = (model) => {
  console.log('Model changed to:', model)
  selectedModel.value = model
  if (chatStore.currentConversation) {
    chatStore.currentConversation.model = model
  }

  // Clear images if new model doesn't support vision
  if (!modelsStore.hasVisionCapability(model) && currentImages.value.length > 0) {
    currentImages.value = []
    if (chatInputRef.value) {
      chatInputRef.value.clearImages()
    }
    toastStore.info('Images cleared - selected model does not support vision')
  }
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-64px)] w-full bg-zinc-900">
    <!-- Loading Screen -->
    <div v-if="isInitializing" class="flex flex-col items-center justify-center flex-1 space-y-6">
      <div class="relative">
        <div class="w-16 h-16 border-4 rounded-full border-purple-500/20"></div>
        <div
          class="absolute top-0 left-0 w-16 h-16 border-4 border-transparent rounded-full border-t-purple-500 animate-spin"
        ></div>
      </div>
      <div class="space-y-2 text-center">
        <h2 class="text-xl font-semibold text-white">Initializing Chat</h2>
        <div class="space-y-1 text-sm text-gray-400">
          <p v-if="isLoadingSettings" class="flex items-center justify-center">
            <span class="w-2 h-2 mr-2 bg-purple-500 rounded-full animate-pulse"></span>
            Loading settings...
          </p>
          <p v-if="isLoadingModels" class="flex items-center justify-center">
            <span class="w-2 h-2 mr-2 bg-blue-500 rounded-full animate-pulse"></span>
            Loading models...
          </p>
          <p v-if="isLoadingChats" class="flex items-center justify-center">
            <span class="w-2 h-2 mr-2 bg-green-500 rounded-full animate-pulse"></span>
            Loading conversations...
          </p>
        </div>
      </div>
    </div>

    <!-- Main Chat Interface - Only show when not initializing -->
    <template v-else>
      <!-- Mobile Header -->
      <Suspense>
        <template #default>
          <ChatHeader
            :current-conversation="chatStore.currentConversation"
            :selected-model="selectedModel"
            :is-mobile="true"
            @toggle-mobile-sidebar="toggleMobileSidebar"
            @start-new-chat="startNewChat"
            @model-changed="handleModelChange"
            @update-chat-title="updateChatTitle"
          />
        </template>
        <template #fallback>
          <div class="h-16 bg-zinc-800/50 animate-pulse"></div>
        </template>
      </Suspense>

      <div class="flex flex-1 w-full overflow-hidden">
        <!-- Sidebar - Always render for proper mobile support -->
        <Suspense>
          <template #default>
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
              @delete-chats="deleteChats"
              @update-chat-title="updateChatTitle"
            />
          </template>
          <template #fallback>
            <div class="w-80 bg-zinc-800/50 animate-pulse"></div>
          </template>
        </Suspense>

        <!-- Chat Area -->
        <div
          class="relative flex flex-col flex-1 w-full overflow-hidden"
          @dragover="handleChatDragOver"
          @dragleave="handleChatDragLeave"
          @drop="handleChatDrop"
        >
          <!-- Drag overlay for entire chat area -->
          <div
            v-if="isDragOverChat && canUploadImages"
            class="absolute inset-0 z-50 flex items-center justify-center border-2 border-blue-400 border-dashed rounded-lg pointer-events-none bg-blue-600/20 backdrop-blur-sm"
          >
            <div class="text-center">
              <svg
                class="w-16 h-16 mx-auto mb-4 text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p class="mb-2 text-lg font-medium text-blue-400">Drop images here</p>
              <p class="text-sm text-blue-300">Upload images to enhance your conversation</p>
            </div>
          </div>
          <!-- Desktop Header -->
          <Suspense>
            <template #default>
              <ChatHeader
                :current-conversation="chatStore.currentConversation"
                :selected-model="selectedModel"
                :is-mobile="false"
                @toggle-sidebar="toggleSidebar"
                @start-new-chat="startNewChat"
                @model-changed="handleModelChange"
                @update-chat-title="updateChatTitle"
              />
            </template>
            <template #fallback>
              <div class="h-16 bg-zinc-800/50 animate-pulse"></div>
            </template>
          </Suspense>

          <!-- Ollama Status Indicator -->
          <div
            v-if="!modelsStore.isOllamaAvailable || modelsStore.ollamaStatus === 'loading'"
            class="px-4 py-2 border-b bg-zinc-800/50 border-zinc-700/50"
          >
            <Suspense>
              <template #default>
                <OllamaStatusIndicator :compact="true" />
              </template>
              <template #fallback>
                <div class="h-8 rounded bg-zinc-700/50 animate-pulse"></div>
              </template>
            </Suspense>
          </div>

          <!-- Messages -->
          <Suspense>
            <template #default>
              <ChatContainer
                ref="chatContainerRef"
                :current-conversation="chatStore.currentConversation"
                :messages="chatStore.messages"
                :loading="chatStore.loading"
                :streaming="chatStore.streaming"
                @start-new-chat="startNewChat"
              />
            </template>
            <template #fallback>
              <div class="flex-1 bg-zinc-900/50 animate-pulse"></div>
            </template>
          </Suspense>

          <!-- Input Area -->
          <Suspense>
            <template #default>
              <ChatInput
                ref="chatInputRef"
                v-model:message-input="messageInput"
                :is-submitting="isSubmitting"
                :can-upload-images="canUploadImages"
                @send-message="sendMessage"
                @images-changed="handleImagesChanged"
              />
            </template>
            <template #fallback>
              <div class="h-20 bg-zinc-800/50 animate-pulse"></div>
            </template>
          </Suspense>
        </div>
      </div>
    </template>

    <!-- Delete Confirmation Modal -->
    <Suspense>
      <template #default>
        <ConfirmationModal
          :is-open="showDeleteModal"
          type="warning"
          :title="deleteModalType === 'single' ? 'Delete Chat' : 'Delete All Chats'"
          :message="
            deleteModalType === 'single'
              ? 'Are you sure you want to delete this chat? This action cannot be undone.'
              : `Are you sure you want to delete all ${chatStore.conversations.length} chat${chatStore.conversations.length > 1 ? 's' : ''}? This action cannot be undone.`
          "
          :confirm-text="deleteModalType === 'single' ? 'Delete Chat' : 'Delete All Chats'"
          cancel-text="Cancel"
          @confirm="confirmDeleteModel"
          @cancel="showDeleteModal = false"
          @close="showDeleteModal = false"
        />
      </template>
      <template #fallback>
        <!-- Modal fallback is usually not needed since it loads fast -->
      </template>
    </Suspense>
  </div>
</template>
