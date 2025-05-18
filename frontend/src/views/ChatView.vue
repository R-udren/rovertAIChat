<script setup>
import ChatMessage from '@/components/ChatMessage.vue'
import { useChatStore } from '@/stores/chat'
import { useToastStore } from '@/stores/toast'
import { useUserSettingsStore } from '@/stores/userSettings'

const chatStore = useChatStore()
const userSettingsStore = useUserSettingsStore()
const toastStore = useToastStore()

const messageInput = ref('')
const chatContainer = ref(null)
const showSidebar = ref(
  localStorage.getItem('sidebarVisible') !== null
    ? localStorage.getItem('sidebarVisible') === 'true'
    : window.innerWidth >= 1024,
)
const isSubmitting = ref(false)
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

// Watch for changes to message input
watch(messageInput, () => {
  nextTick(adjustTextareaHeight)
})

// Computed properties for conditional classes
const sidebarClasses = computed(() => ({
  'translate-x-0 shadow-2xl': isMobileSidebarOpen.value,
  '-translate-x-full': !isMobileSidebarOpen.value,
  'lg:translate-x-0 lg:w-80': showSidebar.value,
  'lg:-translate-x-full lg:w-0 lg:min-w-0': !showSidebar.value,
}))

onMounted(async () => {
  // Get user settings (for theme, preferences)
  await userSettingsStore.fetchSettings()

  // Start a new conversation if none exists
  if (!chatStore.currentConversation) {
    chatStore.startNewConversation()
  }

  // Load saved sidebar state from localStorage
  const savedSidebarState = localStorage.getItem('sidebarVisible')
  if (savedSidebarState !== null) {
    showSidebar.value = savedSidebarState === 'true'
  }

  // Setup resize listener for sidebar
  window.addEventListener('resize', () => {
    if (window.innerWidth >= 1024) {
      // Only set isMobileSidebarOpen to false, don't change desktop sidebar state
      isMobileSidebarOpen.value = false
    } else {
      // On mobile, ensure sidebar is always hidden initially
      isMobileSidebarOpen.value = false
    }
  })

  // Listen for escape key to close mobile sidebar
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isMobileSidebarOpen.value) {
      isMobileSidebarOpen.value = false
    }
  })
})

const sendMessage = async () => {
  if (!messageInput.value.trim() || isSubmitting.value) return

  isSubmitting.value = true

  try {
    await chatStore.sendMessage(messageInput.value.trim())
    messageInput.value = ''
    resetTextareaHeight()

    // Scroll to bottom of chat
    await nextTick()
    scrollToBottom()
  } catch (error) {
    toastStore.error('Failed to send message. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const startNewChat = () => {
  chatStore.startNewConversation()
  toastStore.info('New conversation started')
  // Close sidebar on mobile after selecting
  closeMobileSidebar()
}

const selectConversation = (conversationId) => {
  chatStore.selectConversation(conversationId)
  // Close sidebar on mobile after selecting
  closeMobileSidebar()
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const toggleSidebar = () => {
  if (window.innerWidth < 1024) {
    // Mobile: toggle the mobile sidebar overlay
    isMobileSidebarOpen.value = !isMobileSidebarOpen.value
  } else {
    // Desktop: toggle the persistent sidebar
    showSidebar.value = !showSidebar.value
    // Store user preference in localStorage
    localStorage.setItem('sidebarVisible', showSidebar.value.toString())
  }
}

const closeMobileSidebar = () => {
  if (window.innerWidth < 1024) {
    isMobileSidebarOpen.value = false
  }
}

const handleKeyDown = (e) => {
  // Send message on Enter (without Shift)
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div class="relative h-[calc(100vh-64px)] flex flex-col lg:flex-row bg-zinc-900 overflow-hidden">
    <!-- Sidebar overlay -->
    <div
      v-if="isMobileSidebarOpen"
      class="fixed inset-0 z-20 transition-opacity duration-300 bg-black/50 lg:hidden animate-fade-in"
      @click="closeMobileSidebar"
    ></div>

    <!-- Sidebar with conversations -->
    <aside
      class="fixed lg:sticky top-[64px] left-0 h-[calc(100vh-64px)] w-80 z-30 transform bg-zinc-900 border-r border-zinc-800/50 transition-all duration-300 overflow-hidden"
      :class="sidebarClasses"
    >
      <div class="flex flex-col h-full">
        <div class="p-3 border-b border-zinc-800/70 glass-effect">
          <button
            @click="startNewChat"
            class="flex items-center justify-center w-full px-4 py-2.5 font-medium text-white transition-all duration-300 rounded-lg shadow-md bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 hover:shadow-lg active:scale-95"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 mr-2"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                clip-rule="evenodd"
              />
            </svg>
            New Chat
          </button>
        </div>

        <div class="flex-1 p-3 space-y-2 overflow-y-auto">
          <div
            v-if="chatStore.conversations.length === 0"
            class="py-8 text-center text-gray-500 animate-pulse-subtle"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-12 h-12 mx-auto mb-3 text-zinc-700"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
            <p>No conversations yet</p>
            <p class="mt-1 text-sm">Start a new chat to begin</p>
          </div>

          <div v-else class="space-y-2">
            <button
              v-for="conversation in chatStore.conversations"
              :key="conversation.id"
              @click="selectConversation(conversation.id)"
              class="flex items-center w-full p-3 text-left transition-all duration-200 rounded-lg group"
              :class="
                chatStore.currentConversation?.id === conversation.id
                  ? 'bg-primary-900/30 text-primary-400 border border-primary-700/30'
                  : 'text-gray-300 hover:bg-zinc-800/70 border border-transparent'
              "
            >
              <div class="flex-1 min-w-0">
                <div class="font-medium truncate">{{ conversation.title }}</div>
                <div class="mt-1 text-xs text-gray-500 truncate">
                  {{ new Date(conversation.timestamp).toLocaleDateString() }}
                </div>
              </div>

              <div class="transition-opacity opacity-0 group-hover:opacity-100">
                <button
                  class="p-1 text-gray-400 hover:text-white"
                  title="Delete conversation"
                  @click.stop="chatStore.selectConversation(conversation.id)"
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
              </div>
            </button>
          </div>
        </div>

        <div class="p-3 border-t border-zinc-800/70">
          <div class="text-xs text-center text-gray-500">
            <span class="text-primary-500">rovertAIChat</span> © {{ new Date().getFullYear() }}
          </div>
        </div>
      </div>
    </aside>

    <!-- Main chat area -->
    <main
      class="relative flex flex-col flex-1 w-full h-full transition-all duration-300 ease-in-out sidebar-transition"
    >
      <!-- Chat header -->
      <div
        class="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b border-zinc-800 glass-effect backdrop-blur-lg"
      >
        <div class="flex items-center">
          <!-- Toggle sidebar on desktop -->
          <button
            @click="toggleSidebar"
            class="mr-3 text-gray-400 transition-colors lg:block hover:text-white p-1.5 rounded-md hover:bg-zinc-800"
            :title="showSidebar ? 'Hide sidebar' : 'Show sidebar'"
            :class="{ 'bg-zinc-800/50': !showSidebar, 'text-primary-400': !showSidebar }"
          >
            <svg
              v-if="showSidebar"
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h7"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5"
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

          <h1 class="text-xl font-medium text-white truncate">
            {{ chatStore.currentConversation?.title || 'New Conversation' }}
          </h1>
        </div>

        <div>
          <button
            class="p-2 text-gray-400 transition-colors hover:text-white"
            title="Clear conversation"
            @click="startNewChat"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Messages container -->
      <div ref="chatContainer" class="flex-1 p-4 space-y-6 overflow-y-auto md:p-6 scroll-smooth">
        <div v-if="chatStore.messages.length === 0" class="flex items-center justify-center h-full">
          <div class="max-w-md p-6 text-center animate-fade-in">
            <div
              class="flex items-center justify-center w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary-600 to-blue-600"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="text-white h-14 w-14"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h3 class="mb-3 text-2xl font-medium text-gradient">Start a new conversation</h3>
            <p class="mb-4 leading-relaxed text-gray-400">
              Ask a question or start a discussion with the AI assistant. Your conversations will be
              saved in the sidebar.
            </p>
          </div>
        </div>

        <div v-else class="space-y-6">
          <ChatMessage
            v-for="(message, index) in chatStore.messages"
            :key="message.id"
            :message="message"
            :is-last="index === chatStore.messages.length - 1 && !chatStore.loading"
          />
        </div>

        <div v-if="chatStore.loading" class="flex justify-center my-6 animate-fade-in">
          <div class="flex items-center px-5 py-3 space-x-3 rounded-full glass-effect">
            <div class="flex space-x-1">
              <div
                class="w-2 h-2 rounded-full bg-primary-400 animate-bounce"
                style="animation-delay: 0s"
              ></div>
              <div
                class="w-2 h-2 rounded-full bg-primary-400 animate-bounce"
                style="animation-delay: 0.1s"
              ></div>
              <div
                class="w-2 h-2 rounded-full bg-primary-400 animate-bounce"
                style="animation-delay: 0.2s"
              ></div>
            </div>
            <span class="text-sm font-medium text-primary-300">AI is thinking...</span>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="p-4 transition-all duration-300 border-t md:p-6 border-zinc-800 glass-effect">
        <form @submit.prevent="sendMessage" class="flex items-end space-x-3">
          <div class="relative flex-1 overflow-hidden rounded-xl">
            <textarea
              ref="textareaRef"
              v-model="messageInput"
              placeholder="Type a message..."
              class="w-full px-4 py-3 text-white transition-all duration-200 border shadow-inner resize-none bg-zinc-800/80 border-zinc-700/50 rounded-xl focus:outline-none focus:border-primary-500/50"
              :rows="expandedInput ? 4 : 1"
              @keydown="handleKeyDown"
              @focus="adjustTextareaHeight"
              aria-label="Message input"
            ></textarea>
          </div>

          <button
            type="submit"
            class="flex-shrink-0 p-3 text-white transition-all duration-200 shadow-lg bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 rounded-xl hover:shadow-primary-600/20 active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
            :disabled="isSubmitting || !messageInput.trim()"
            aria-label="Send message"
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
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </form>

        <div class="mt-2 text-xs text-center text-gray-500">
          <span
            >Press
            <kbd class="px-2 py-1 mx-1 border rounded bg-zinc-800 border-zinc-700">Enter</kbd> to
            send,
            <kbd class="px-2 py-1 mx-1 border rounded bg-zinc-800 border-zinc-700"
              >Shift + Enter</kbd
            >
            for a new line</span
          >
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
textarea {
  min-height: 20px;
  max-height: 150px;
}

kbd {
  font-family: monospace;
}
</style>
