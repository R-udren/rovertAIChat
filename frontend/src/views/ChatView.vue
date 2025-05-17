<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import { useUserSettingsStore } from '@/stores/userSettings'
import { useToastStore } from '@/stores/toast'
import ChatMessage from '@/components/ChatMessage.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()
const userSettingsStore = useUserSettingsStore()
const toastStore = useToastStore()

const messageInput = ref('')
const chatContainer = ref(null)
const showSidebar = ref(window.innerWidth >= 768)
const isSubmitting = ref(false)

onMounted(async () => {
  // Get user settings (for theme, preferences)
  await userSettingsStore.fetchSettings()

  // Start a new conversation if none exists
  if (!chatStore.currentConversation) {
    chatStore.startNewConversation()
  }

  // Setup resize listener for sidebar
  window.addEventListener('resize', () => {
    showSidebar.value = window.innerWidth >= 768
  })
})

const sendMessage = async () => {
  if (!messageInput.value.trim() || isSubmitting.value) return

  isSubmitting.value = true

  try {
    await chatStore.sendMessage(messageInput.value.trim())
    messageInput.value = ''

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
  if (window.innerWidth < 768) {
    showSidebar.value = false
  }
}

const selectConversation = (conversationId) => {
  chatStore.selectConversation(conversationId)
  // Close sidebar on mobile after selecting
  if (window.innerWidth < 768) {
    showSidebar.value = false
  }
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
  showSidebar.value = !showSidebar.value
}
</script>

<template>
  <div class="flex h-[calc(100vh-64px)]">
    <!-- Sidebar with conversations -->
    <div
      v-show="showSidebar"
      class="bg-zinc-800 h-full w-full md:w-64 flex flex-col border-r border-zinc-700 fixed md:relative z-20 left-0 top-[64px] bottom-0"
    >
      <div class="p-4 border-b border-zinc-700">
        <button
          @click="startNewChat"
          class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 mr-2"
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

      <div class="flex-1 overflow-y-auto p-2">
        <div v-if="chatStore.conversations.length === 0" class="text-center py-8 text-gray-500">
          No conversations yet
        </div>

        <div v-else class="space-y-1">
          <button
            v-for="conversation in chatStore.conversations"
            :key="conversation.id"
            @click="selectConversation(conversation.id)"
            class="w-full text-left p-3 rounded-md transition-colors duration-150"
            :class="
              chatStore.currentConversation?.id === conversation.id
                ? 'bg-zinc-700 text-white'
                : 'text-gray-300 hover:bg-zinc-700 hover:text-white'
            "
          >
            <div class="truncate">{{ conversation.title }}</div>
            <div class="text-xs text-gray-500">
              {{ new Date(conversation.timestamp).toLocaleDateString() }}
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile sidebar toggle -->
    <button
      @click="toggleSidebar"
      class="md:hidden fixed bottom-6 left-6 z-30 bg-primary-600 rounded-full p-3 shadow-lg"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6 text-white"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 6h16M4 12h16m-7 6h7"
        />
      </svg>
    </button>

    <!-- Main chat area -->
    <div class="flex-1 flex flex-col bg-zinc-900 h-full overflow-hidden">
      <!-- Chat header -->
      <div class="p-4 border-b border-zinc-700 flex items-center">
        <h1 class="text-xl font-medium text-white">
          {{ chatStore.currentConversation?.title || 'New Conversation' }}
        </h1>
      </div>

      <!-- Messages container -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-if="chatStore.messages.length === 0" class="flex h-full items-center justify-center">
          <div class="text-center max-w-md p-6">
            <h3 class="text-xl font-medium text-white mb-2">Start a new conversation</h3>
            <p class="text-gray-400 mb-4">
              Ask a question or start a discussion with the AI assistant.
            </p>
          </div>
        </div>

        <div v-else class="space-y-4">
          <ChatMessage v-for="message in chatStore.messages" :key="message.id" :message="message" />
        </div>

        <div v-if="chatStore.loading" class="flex justify-center my-4">
          <LoadingSpinner size="md" text="AI is thinking..." />
        </div>
      </div>

      <!-- Input area -->
      <div class="p-4 border-t border-zinc-700">
        <form @submit.prevent="sendMessage" class="flex space-x-2">
          <textarea
            v-model="messageInput"
            placeholder="Type a message..."
            class="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none text-white"
            rows="1"
            @keydown.enter.prevent="sendMessage"
          ></textarea>

          <button
            type="submit"
            class="bg-primary-600 hover:bg-primary-700 text-white font-medium p-2 rounded-md transition-colors duration-200"
            :disabled="isSubmitting || !messageInput.trim()"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
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
      </div>
    </div>
  </div>
</template>
