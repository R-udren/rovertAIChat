<script setup>
const props = defineProps({
  currentConversation: Object,
  messages: Array,
  loading: Boolean,
  streaming: Boolean,
  isEditing: Boolean,
  messageBeingEdited: Object,
  editError: String,
  isSavingEdit: Boolean,
})

const emit = defineEmits([
  'start-new-chat',
  'edit-message',
  'delete-message',
  'save-edit',
  'cancel-edit',
])

const scrollContainer = ref(null)
</script>

<template>
  <div ref="scrollContainer" class="flex-1 p-6 overflow-y-auto bg-zinc-900 relative">
    <div
      v-if="!currentConversation && !loading"
      class="flex flex-col items-center justify-center h-full relative z-10"
    >
      <div class="max-w-lg p-8 text-center">
        <div class="mb-6 flex justify-center">
          <div
            class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl animate-float"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="size-12" viewBox="0 0 48 48">
              <path
                fill="currentColor"
                d="M31.833 13.112a5.36 5.36 0 0 0-2.544-1.805l-2.603-.845a1.028 1.028 0 0 1 0-1.937l2.602-.845a5.36 5.36 0 0 0 3.323-3.33l.022-.064l.845-2.6a1.027 1.027 0 0 1 1.94 0l.845 2.6A5.36 5.36 0 0 0 39.66 7.68l2.602.845l.052.013a1.028 1.028 0 0 1 0 1.937l-2.602.845a5.36 5.36 0 0 0-3.397 3.394l-.846 2.6l-.025.064a1.027 1.027 0 0 1-1.538.433a1.03 1.03 0 0 1-.375-.497l-.846-2.6a5.4 5.4 0 0 0-.852-1.602m14.776 6.872l-1.378-.448a2.84 2.84 0 0 1-1.797-1.796l-.448-1.377a.544.544 0 0 0-1.027 0l-.448 1.377a2.84 2.84 0 0 1-1.77 1.796l-1.378.448a.545.545 0 0 0 0 1.025l1.378.448q.227.075.438.188l.003.015a2.84 2.84 0 0 1 1.357 1.61l.448 1.377a.545.545 0 0 0 1.01.039v-.01l.016-.039l.448-1.377a2.84 2.84 0 0 1 1.798-1.796l1.378-.448a.545.545 0 0 0 0-1.025zM29.93 5q.042-.039.081-.081A20 20 0 0 0 24 4C12.954 4 4 12.954 4 24c0 3.448.873 6.695 2.411 9.528L4.07 41.766c-.375 1.318.843 2.537 2.162 2.162l8.236-2.342A19.9 19.9 0 0 0 24 44c10.16 0 18.551-7.577 19.831-17.388A2.55 2.55 0 0 1 41 26.54a2.54 2.54 0 0 1-.89-1.35l-.44-1.37a.9.9 0 0 0-.2-.33a1 1 0 0 0-.2-.15l-.12-.06l-1.42-.46a2.55 2.55 0 0 1-1.7-2.4c0-.346.075-.687.22-1a3 3 0 0 1-3.47 0a3 3 0 0 1-1.12-1.51l-.84-2.59a3.2 3.2 0 0 0-.54-1A3 3 0 0 0 30 14a3.3 3.3 0 0 0-1.35-.79L26 12.35a3 3 0 0 1-1.44-4.58a3.1 3.1 0 0 1 1.51-1.12l2.57-.83A3.4 3.4 0 0 0 29.93 5"
              />
            </svg>
          </div>
        </div>

        <h2
          class="mb-4 text-4xl font-semibold bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent animate-gradient"
        >
          Welcome to <span class="text-gradient-3 font-bold">rovertChat</span>
        </h2>
        <p class="mb-8 text-lg text-gray-300 leading-relaxed">
          Start a new conversation or select an existing one from the sidebar.
          <br />
          <span class="text-sm text-gray-400">Your AI companion is ready to help!</span>
        </p>
        <button
          @click="$emit('start-new-chat')"
          class="group relative px-8 py-4 font-semibold text-white transition-all duration-300 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 transform hover:scale-105 hover:shadow-2xl shadow-lg"
        >
          <span class="relative z-10 flex items-center space-x-2">
            <svg
              class="w-5 h-5 transition-transform group-hover:rotate-12"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              ></path>
            </svg>
            <span>Start a new chat</span>
          </span>
          <div
            class="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"
          ></div>
        </button>
      </div>
    </div>

    <div v-else-if="loading" class="flex flex-col items-center justify-center p-8">
      <div class="relative">
        <div
          class="w-16 h-16 border-4 border-zinc-600 border-t-blue-500 rounded-full animate-spin"
        ></div>
        <div
          class="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-purple-500 rounded-full animate-spin animate-reverse"
        ></div>
      </div>
      <p class="mt-4 text-gray-400 animate-pulse">Loading conversation...</p>
    </div>

    <div
      v-else-if="messages.length === 0"
      class="flex flex-col items-center justify-center p-12 text-center"
    >
      <div
        class="w-16 h-16 bg-gradient-to-br from-zinc-700 to-zinc-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg"
      >
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          ></path>
        </svg>
      </div>
      <p class="text-gray-400 text-lg">No messages yet. Start the conversation!</p>
      <p class="text-gray-500 text-sm mt-2">Type a message below to begin chatting</p>
    </div>

    <div v-else class="space-y-6">
      <ChatMessage
        v-for="(message, index) in messages"
        :key="`${message.id || index}-${message.created_at || Date.now()}`"
        :message="message"
        :is-streaming="message.isStreaming"
        :is-last="index === messages.length - 1"
        :is-editing="props.isEditing && props.messageBeingEdited?.id === message.id"
        :edit-error="props.editError"
        :is-saving-edit="props.isSavingEdit"
        @edit="$emit('edit-message', $event)"
        @delete="$emit('delete-message', $event)"
        @save-edit="$emit('save-edit', $event)"
        @cancel-edit="$emit('cancel-edit')"
      />

      <div
        v-if="
          streaming &&
          !messages[messages.length - 1]?.isStreaming &&
          !messages[messages.length - 1]?.isLoading
        "
        class="flex items-center ml-2 space-x-3 text-gray-400 p-4 rounded-xl bg-zinc-800/50 backdrop-blur-sm"
      >
        <div class="flex space-x-1">
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
          <div
            class="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
            style="animation-delay: 0.1s"
          ></div>
          <div
            class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
            style="animation-delay: 0.2s"
          ></div>
        </div>
        <span class="text-sm font-medium">AI is thinking...</span>
      </div>
    </div>
  </div>
  <!-- Delete Message Confirmation Modal (moved to top-level ChatView) -->
  <!--
  <Suspense>
    <ConfirmationModal
      v-if="showMessageDeleteModal"
      :is-open="showMessageDeleteModal"
      type="warning"
      title="Delete Message"
      message="Are you sure you want to delete this message? This action cannot be undone."
      confirm-text="Delete Message"
      cancel-text="Cancel"
      @confirm="deleteMessage"
      @cancel="showMessageDeleteModal = false"
      @close="showMessageDeleteModal = false"
    />
  </Suspense>-->
</template>

<style scoped>
.animate-float {
  animation: float 3s ease-in-out infinite;
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradient 3s ease infinite;
}

.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}

.animate-reverse {
  animation-direction: reverse;
}

.bg-grid-pattern {
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(2deg);
  }
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes pulse-slow {
  0%,
  100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.1;
  }
}

@keyframes ellipsis {
  0% {
    content: '.';
  }
  33% {
    content: '..';
  }
  66% {
    content: '...';
  }
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(39, 39, 42, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.6), rgba(147, 51, 234, 0.6));
  border-radius: 4px;
  transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.8), rgba(147, 51, 234, 0.8));
}
</style>
