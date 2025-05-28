<script setup>
defineProps({
  currentConversation: Object,
  selectedModel: String,
  isMobile: Boolean,
})

defineEmits([
  'toggle-sidebar',
  'toggle-mobile-sidebar',
  'start-new-chat',
  'model-changed',
  'update-chat-title',
])
</script>

<template>
  <!-- Mobile Header -->
  <div v-if="isMobile" class="flex items-center justify-between px-4 py-2 bg-zinc-800/20 md:hidden">
    <button
      @click="$emit('toggle-mobile-sidebar')"
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
    <div class="min-w-0 text-lg font-medium text-white truncate">
      <EditableTitle
        :title="currentConversation?.title"
        @update-title="(newTitle) => $emit('update-chat-title', currentConversation?.id, newTitle)"
      />
    </div>

    <div class="flex items-center space-x-2">
      <ModelSelector :model-id="selectedModel" @model-changed="$emit('model-changed', $event)" />
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
    </div>
  </div>

  <!-- Desktop Header -->
  <div v-else class="items-center justify-between hidden px-4 py-2 md:flex bg-zinc-800">
    <div class="flex items-center">
      <button
        @click="$emit('toggle-sidebar')"
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
      <div class="min-w-0 text-lg font-medium text-white truncate">
        <EditableTitle
          :title="currentConversation?.title"
          @update-title="
            (newTitle) => $emit('update-chat-title', currentConversation?.id, newTitle)
          "
        />
      </div>
    </div>
    <div class="flex items-center space-x-2">
      <ModelSelector :model-id="selectedModel" @model-changed="$emit('model-changed', $event)" />
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
    </div>
  </div>
</template>
