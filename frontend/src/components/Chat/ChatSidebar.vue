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
    class="fixed inset-0 z-40 transition-opacity duration-300 bg-black bg-opacity-50 backdrop-blur-sm"
    @click="$emit('toggle-mobile-sidebar')"
  ></div>

  <!-- Sidebar container -->
  <div
    :class="[
      'flex flex-col h-full',
      'transition-all duration-300 ease-in-out',
      // Desktop mode
      { 'bg-zinc-800 border-r border-zinc-700 w-72 flex-shrink-0': !isMobile && showSidebar },
      { 'w-0 overflow-hidden': !isMobile && !showSidebar },
      // Mobile mode
      { 'fixed inset-y-0 left-0 z-50 w-80 max-w-[80vw]': isMobile },
      { 'bg-zinc-800/90 backdrop-blur-md shadow-xl': isMobile },
      { 'transform -translate-x-full': isMobile && !isMobileSidebarOpen },
      { 'transform translate-x-0': isMobile && isMobileSidebarOpen },
    ]"
  >
    <!-- Header with title and action buttons -->
    <div
      :class="[
        'flex items-center justify-between p-2 border-b',
        isMobile ? 'border-zinc-700/30' : 'border-zinc-700',
        isMobile ? 'bg-zinc-800/80 backdrop-blur-md' : '',
      ]"
    >
      <h2 class="text-xl font-bold text-white">Conversations</h2>
      <div class="flex items-center">
        <button
          @click="$emit('start-new-chat')"
          class="p-2 text-gray-400 transition-all rounded-lg hover:text-white hover:bg-zinc-700/70 active:scale-95"
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
          v-if="isMobile"
          @click="$emit('toggle-mobile-sidebar')"
          class="p-2 ml-2 text-gray-400 transition-all rounded-lg hover:text-white hover:bg-zinc-700/70 active:scale-95"
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

    <!-- Conversations list container -->
    <div
      :class="[
        'flex-1 py-3 overflow-y-auto',
        isMobile ? 'px-3' : 'px-2',
        isMobile ? 'bg-gradient-to-b from-zinc-800/80 to-zinc-800/60' : '',
      ]"
    >
      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center p-4">
        <div
          class="w-6 h-6 border-2 border-t-2 rounded-full border-zinc-600 border-t-indigo-400 animate-spin"
        ></div>
      </div>

      <!-- Empty state -->
      <div v-else-if="conversations.length === 0" class="p-4 text-center text-gray-400">
        No conversations yet. Start a new chat!
      </div>

      <!-- Conversations list -->
      <ul v-else class="space-y-2">
        <li
          v-for="chat in conversations"
          :key="chat.id"
          class="flex items-center justify-between transition-transform hover:translate-x-1"
        >
          <!-- Chat item (Explicitly clickable) -->
          <div
            :class="[
              'flex items-center flex-grow max-w-[calc(100%-32px)] px-3 py-2 rounded-lg cursor-pointer',
              'transition-all duration-200 text-left',
              'hover:bg-zinc-700/80 hover:shadow-md',
              isMobile ? 'backdrop-blur-sm' : '',
              chat.id === currentConversation?.id
                ? isMobile
                  ? 'bg-indigo-600/20 border border-indigo-500/30 text-white shadow-md'
                  : 'bg-zinc-700 text-white'
                : 'text-gray-300',
            ]"
            @click="selectChat(chat)"
          >
            <div class="w-full mr-2 overflow-hidden truncate max-w-[180px]">
              <!-- Regular title (not editable) -->
              <div class="font-medium truncate pointer-events-none">
                {{ chat.title }}
              </div>
              <!-- Date -->
              <div class="text-xs text-gray-400 pointer-events-none">
                {{ new Date(chat.updated_at).toLocaleDateString() }}
              </div>
            </div>
          </div>

          <!-- Delete button -->
          <button
            @click.stop="$emit('delete-chat', chat.id)"
            class="p-1 ml-1 text-gray-400 transition-all rounded-full hover:text-white hover:bg-red-500/80 hover:shadow-md active:scale-95"
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
    <!-- Clear all chats button -->
    <div v-if="conversations.length > 0" class="mb-4 text-center">
      <button
        @click="$emit('delete-chats')"
        class="px-4 py-2 text-sm text-red-500 transition-colors border border-red-500 rounded-md hover:bg-red-500 hover:text-white"
      >
        Clear All Chats
      </button>
    </div>
  </div>
</template>
