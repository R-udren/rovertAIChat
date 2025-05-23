<script setup>
defineProps({
  showSidebar: Boolean,
  isMobileSidebarOpen: Boolean,
  conversations: Array,
  currentConversation: Object,
  loading: Boolean,
})

defineEmits(['toggle-mobile-sidebar', 'start-new-chat', 'select-chat', 'delete-chat'])
</script>

<template>
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
          @click="$emit('start-new-chat')"
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
          @click="$emit('toggle-mobile-sidebar')"
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
      <div v-if="loading" class="flex justify-center p-4">
        <div
          class="w-6 h-6 border-2 border-t-2 rounded-full border-zinc-600 border-t-zinc-400 animate-spin"
        ></div>
      </div>
      <div v-else-if="conversations.length === 0" class="p-4 text-center text-gray-400">
        No conversations yet. Start a new chat!
      </div>
      <ul v-else class="space-y-1">
        <li v-for="chat in conversations" :key="chat.id" class="flex items-center">
          <div
            @click="$emit('select-chat', chat)"
            :class="[
              'flex items-center flex-grow w-full px-3 py-2 rounded-lg cursor-pointer',
              'hover:bg-zinc-700 transition-colors text-left',
              chat.id === currentConversation?.id ? 'bg-zinc-700 text-white' : 'text-gray-300',
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
            @click="$emit('delete-chat', chat.id)"
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
</template>
