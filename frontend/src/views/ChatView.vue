<script setup>
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useToastStore } from '@/stores/toast'

const chatStore = useChatStore()
const toastStore = useToastStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const selectedModel = ref(chatStore.currentConversation?.model)

const messageInput = ref('')
const chatContainer = ref(null)
const showSidebar = ref(
  localStorage.getItem('sidebarVisible') !== null
    ? localStorage.getItem('sidebarVisible') === 'true'
    : window.innerWidth >= 1024,
)
const isSubmitting = computed(() => chatStore.sending || chatStore.streaming)
const isMobileSidebarOpen = ref(false)
const expandedInput = ref(false)
const textareaRef = ref(null)

// Auto-resize textarea
const adjustTextareaHeight = () => {
  if (!textareaRef.value) return

  textareaRef.value.style.height = 'auto'
  textareaRef.value.style.height = `${Math.min(textareaRef.value.scrollHeight, 150)}px`
  expandedInput.value = textareaRef.value.scrollHeight > 50
}

// Reset textarea height
const resetTextareaHeight = () => {
  if (!textareaRef.value) return
  textareaRef.value.style.height = 'auto'
  expandedInput.value = false
}

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
  if (!chatContainer.value) return

  // Wait for DOM update
  await nextTick()

  // Smooth scroll to bottom
  chatContainer.value.scrollTo({
    top: chatContainer.value.scrollHeight,
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
  resetTextareaHeight()

  const model = localStorage.getItem('preferredModel') || selectedModel.value

  await chatStore.sendMessage(message, model)

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
  if (conversation.id === chatStore.currentConversation?.id) return

  await chatStore.selectConversation(conversation)
  router.push(`/chat/${conversation.id}`)
  scrollToBottom()

  // Close mobile sidebar if open
  if (isMobileSidebarOpen.value) {
    isMobileSidebarOpen.value = false
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

// Load chats and set initial chat
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    toastStore.error('Please log in to use the chat feature')
    router.push('/login')
    return
  }

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

const handleModelChange = (model) => {
  console.log('Model changed to:', model)
  selectedModel.value = model
  if (chatStore.currentConversation) {
    chatStore.currentConversation.model = model
  }
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-64px)] bg-zinc-900">
    <!-- Mobile Header -->
    <div class="flex items-center justify-between px-4 py-2 bg-zinc-800/20 md:hidden">
      <button
        @click="toggleMobileSidebar"
        class="p-2 text-gray-400 transition-colors rounded-lg hover:text-white hover:bg-zinc-700"
        aria-label="Toggle sidebar"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-6 h-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
      <h1 class="text-lg font-medium text-white truncate">
        {{ chatStore.currentConversation?.title || 'New Chat' }}
      </h1>

      <div class="flex items-center space-x-2">
        <!-- Add the model selector here -->
        <ModelSelector
          v-model:modelId="selectedModel"
          :chatId="chatStore.currentConversation?.id"
          @model-changed="handleModelChange"
        />
        <button
          @click="startNewChat"
          class="p-2 text-gray-400 transition-colors rounded-lg hover:text-white hover:bg-zinc-700"
          aria-label="New chat"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
        </button>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <div
        :class="[
          'bg-zinc-800 border-r border-zinc-700 flex flex-col',
          'transition-all duration-300 ease-in-out',
          showSidebar ? 'w-72' : 'w-0',
          isMobileSidebarOpen
            ? 'fixed inset-0 z-50 w-full md:relative md:w-72'
            : 'hidden md:flex md:flex-col',
        ]"
      >
        <div class="flex items-center justify-between p-4">
          <h2 class="text-xl font-bold text-white">Conversations</h2>
          <div class="flex">
            <button
              @click="startNewChat"
              class="p-2 text-gray-400 transition-colors rounded-lg hover:text-white hover:bg-zinc-700"
              aria-label="New chat"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
            <button
              @click="toggleMobileSidebar"
              class="p-2 ml-2 text-gray-400 transition-colors rounded-lg md:hidden hover:text-white hover:bg-zinc-700"
              aria-label="Close sidebar"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <div class="flex-1 px-2 py-3 overflow-y-auto">
          <div v-if="chatStore.loading" class="flex justify-center p-4">
            <div
              class="w-6 h-6 border-2 border-t-2 rounded-full border-zinc-600 border-t-zinc-400 animate-spin"
            ></div>
          </div>
          <div
            v-else-if="chatStore.conversations.length === 0"
            class="p-4 text-center text-gray-400"
          >
            No conversations yet. Start a new chat!
          </div>
          <ul v-else class="space-y-1">
            <li v-for="chat in chatStore.conversations" :key="chat.id" class="flex items-center">
              <div
                @click="selectChat(chat)"
                :class="[
                  'flex items-center flex-grow w-full px-3 py-2 rounded-lg cursor-pointer',
                  'hover:bg-zinc-700 transition-colors text-left',
                  chat.id === chatStore.currentConversation?.id
                    ? 'bg-zinc-700 text-white'
                    : 'text-gray-300',
                ]"
              >
                <div class="w-full overflow-hidden">
                  <div class="truncate">{{ chat.title || 'New Chat' }}</div>
                  <div class="text-xs text-gray-400">
                    {{ new Date(chat.updated_at).toLocaleDateString() }}
                  </div>
                </div>
              </div>
              <button
                @click="deleteChat(chat.id)"
                class="p-1 ml-1 text-gray-400 transition-colors rounded hover:text-white hover:bg-red-500"
                aria-label="Delete chat"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </li>
          </ul>
        </div>
      </div>

      <!-- Chat Area -->
      <div class="flex flex-col flex-1 overflow-hidden">
        <!-- Desktop Header -->
        <div class="items-center justify-between hidden px-4 py-2 md:flex bg-zinc-800">
          <div class="flex items-center">
            <button
              @click="toggleSidebar"
              class="p-2 mr-4 text-gray-400 transition-colors rounded-lg hover:text-white hover:bg-zinc-700"
              aria-label="Toggle sidebar"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <h1 class="text-lg font-medium text-white truncate">
              {{ chatStore.currentConversation?.title || 'New Chat' }}
            </h1>
          </div>
          <div class="flex items-center space-x-2">
            <!-- Add the model selector here -->
            <ModelSelector
              v-model:modelId="selectedModel"
              :chatId="chatStore.currentConversation?.id"
              @model-changed="handleModelChange"
            />
            <button
              @click="startNewChat"
              class="p-2 text-gray-400 transition-colors rounded-lg hover:text-white hover:bg-zinc-700"
              aria-label="New chat"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div ref="chatContainer" class="flex-1 p-4 overflow-y-auto">
          <div
            v-if="!chatStore.currentConversation && !chatStore.loading"
            class="flex flex-col items-center justify-center h-full"
          >
            <div class="max-w-md p-6 text-center">
              <h2 class="mb-2 text-2xl font-bold text-white">Welcome to rovertChat</h2>
              <p class="mb-6 text-gray-300">
                Start a new conversation or select an existing one from the sidebar.
              </p>
              <button
                @click="startNewChat"
                class="px-4 py-2 font-medium text-white transition-colors rounded-lg bg-zinc-700 hover:bg-zinc-600"
              >
                Start a new chat
              </button>
            </div>
          </div>

          <div v-else-if="chatStore.loading" class="flex justify-center p-4">
            <div
              class="w-8 h-8 border-2 border-t-2 rounded-full border-zinc-600 border-t-zinc-400 animate-spin"
            ></div>
          </div>

          <div
            v-else-if="chatStore.messages.length === 0"
            class="flex justify-center p-4 text-gray-400"
          >
            No messages yet. Start the conversation!
          </div>

          <div v-else class="space-y-6">
            <ChatMessage
              v-for="(message, index) in chatStore.messages"
              :key="`${message.id || index}-${message.created_at}`"
              :message="message"
              :is-streaming="message.isStreaming"
            />

            <div v-if="chatStore.streaming" class="flex items-center ml-2 space-x-2 text-gray-400">
              <span>AI is thinking</span>
              <span class="animate-ellipsis">...</span>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-4 border-t border-zinc-700 bg-zinc-800">
          <div
            class="flex items-start p-2 transition-all rounded-lg bg-zinc-700 focus-within:ring-2 focus-within:ring-zinc-500"
            :class="{ 'items-center': !expandedInput }"
          >
            <textarea
              ref="textareaRef"
              v-model="messageInput"
              @input="adjustTextareaHeight"
              @keydown.enter.prevent="sendMessage"
              placeholder="Type your message here..."
              class="flex-1 min-h-[40px] mr-2 bg-transparent resize-none text-white focus:outline-none"
              :disabled="isSubmitting"
            ></textarea>
            <button
              @click="sendMessage"
              class="p-2 text-white transition-colors rounded-lg hover:bg-zinc-600"
              :disabled="!messageInput.trim() || isSubmitting"
              :class="{ 'opacity-50 cursor-not-allowed': !messageInput.trim() || isSubmitting }"
            >
              <svg
                v-if="!isSubmitting"
                xmlns="http://www.w3.org/2000/svg"
                class="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
              <svg
                v-else
                class="w-6 h-6 animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
