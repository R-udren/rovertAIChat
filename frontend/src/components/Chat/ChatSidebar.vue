<script setup>
const props = defineProps({
  showSidebar: Boolean,
  isMobileSidebarOpen: Boolean,
  conversations: Array,
  currentConversation: Object,
  loading: Boolean,
})

const emit = defineEmits([
  'toggle-mobile-sidebar',
  'start-new-chat',
  'select-chat',
  'delete-chat',
  'delete-chats',
  'update-chat-title',
])

// Track if we're on mobile or desktop
const isMobile = ref(false)

// Update on mount and when window is resized
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

// Check screen size
function checkScreenSize() {
  isMobile.value = window.innerWidth < 768
}

// Handle chat selection with touch support for mobile
function selectChat(chat) {
  emit('select-chat', chat)
}
</script>

<template>
  <!-- Mobile backdrop overlay when sidebar is open -->
  <div
    v-if="isMobile && isMobileSidebarOpen"
    class="fixed inset-0 z-40 transition-opacity duration-300 bg-black/40 backdrop-blur-sm"
    @click="$emit('toggle-mobile-sidebar')"
  ></div>

  <!-- Sidebar container -->
  <div
    :class="[
      'flex flex-col h-full',
      'transition-all duration-300 ease-in-out',
      // Desktop mode
      {
        'bg-zinc-900/80 border-r border-zinc-700/50 w-72 flex-shrink-0 backdrop-blur-md':
          !isMobile && showSidebar,
      },
      { 'w-0 overflow-hidden': !isMobile && !showSidebar },
      // Mobile mode
      { 'fixed inset-y-0 left-0 z-50 w-80 max-w-[80vw]': isMobile },
      { 'bg-zinc-900/95 backdrop-blur-md shadow-2xl': isMobile },
      { 'transform -translate-x-full': isMobile && !isMobileSidebarOpen },
      { 'transform translate-x-0': isMobile && isMobileSidebarOpen },
    ]"
  >
    <!-- Header with title and action buttons -->
    <div
      :class="[
        'flex items-center justify-between border-zinc-800/50',
        isMobile ? ' bg-zinc-900/20 py-3 backdrop-blur-md border-y' : 'bg-zinc-800/20 border-b p-2',
      ]"
    >
      <h2 class="ml-2 text-xl font-bold text-white">Conversations</h2>
      <div class="flex items-center space-x-2">
        <button
          @click="$emit('start-new-chat')"
          class="p-2 text-gray-400 transition-all duration-200 rounded-lg hover:text-white hover:bg-zinc-700/70 hover:scale-105 active:scale-95"
          aria-label="New chat"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="size-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <button
          v-if="isMobile"
          @click="$emit('toggle-mobile-sidebar')"
          class="p-2 text-gray-400 transition-all duration-200 rounded-lg hover:text-white hover:bg-zinc-700/70 hover:scale-105 active:scale-95"
          aria-label="Close sidebar"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="size-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Conversations list container -->
    <div
      :class="[
        'flex-1 py-3 overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-600 scrollbar-track-transparent',
        isMobile ? 'px-3' : 'px-2',
        isMobile ? 'bg-gradient-to-b from-zinc-800/80 to-zinc-900/50' : '',
      ]"
    >
      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center p-6">
        <div class="flex items-center space-x-2">
          <div
            class="w-3 h-3 bg-indigo-400 rounded-full animate-bounce"
            style="animation-delay: 0ms"
          ></div>
          <div
            class="w-3 h-3 bg-purple-400 rounded-full animate-bounce"
            style="animation-delay: 150ms"
          ></div>
          <div
            class="w-3 h-3 bg-pink-400 rounded-full animate-bounce"
            style="animation-delay: 300ms"
          ></div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="conversations.length === 0" class="p-6 text-center">
        <div class="mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-12 h-12 mx-auto text-gray-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        </div>
        <p class="text-gray-400">No conversations yet</p>
        <p class="mt-2 text-sm text-gray-500">Start a new chat to begin!</p>
      </div>

      <!-- Conversations list -->
      <ul v-else class="space-y-2">
        <li
          v-for="chat in conversations"
          :key="chat.id"
          class="transition-all duration-200 group hover:transform hover:translate-x-1"
        >
          <div class="flex items-center justify-between">
            <!-- Chat item (Explicitly clickable) -->
            <div
              :class="[
                'flex items-center flex-grow max-w-[calc(100%-40px)] px-3 py-3 rounded-lg cursor-pointer',
                'transition-all duration-200 text-left',
                'hover:bg-zinc-700/80 hover:shadow-md hover:scale-[1.02]',
                'group-hover:shadow-lg',
                isMobile ? 'backdrop-blur-sm' : '',
                chat.id === currentConversation?.id
                  ? 'bg-gradient-to-r from-indigo-600/30 to-purple-600/20 border border-indigo-500/30 text-white shadow-lg shadow-indigo-500/10'
                  : 'text-gray-300 hover:text-white',
              ]"
              @click="selectChat(chat)"
            >
              <div class="w-full mr-2">
                <!-- Chat icon -->
                <div class="flex items-center mb-1">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="mr-2 text-gray-400 size-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  <!-- Regular title (not editable) -->
                  <div class="font-medium truncate pointer-events-none max-w-[180px]">
                    {{ chat.title }}
                  </div>
                </div>
                <!-- Date -->
                <div class="ml-6 text-xs text-gray-400 pointer-events-none">
                  {{ new Date(chat.updated_at).toLocaleDateString() }}
                </div>
              </div>
            </div>

            <!-- Delete button -->
            <button
              @click.stop="$emit('delete-chat', chat.id)"
              class="p-2 ml-2 text-gray-400 transition-all duration-200 rounded-full opacity-0 hover:text-white hover:bg-red-500/80 hover:shadow-md hover:scale-110 active:scale-95 group-hover:opacity-100"
              aria-label="Delete chat"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Footer section -->
    <div class="p-3 border-t border-zinc-700/50 bg-zinc-900/50">
      <!-- Clear all chats button -->
      <div v-if="conversations.length > 0" class="mb-4">
        <button
          @click="$emit('delete-chats')"
          class="w-full px-4 py-2 text-sm text-red-400 transition-all duration-200 border rounded-lg border-red-500/30 hover:bg-red-500/10 hover:border-red-500 hover:text-red-300 hover:shadow-md active:scale-95"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="inline w-4 h-4 mr-2"
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
          Clear All Chats
        </button>
      </div>

      <!-- GitHub link in sidebar footer -->
      <div class="text-center">
        <a
          href="https://github.com/R-udren/rovertAIChat"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 text-xs text-gray-500 transition-all duration-200 hover:text-gray-300 group"
        >
          <svg
            class="transition-transform size-4 group-hover:scale-110"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.30.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
            />
          </svg>
          rovertAIChat
        </a>
      </div>
    </div>
  </div>
</template>
