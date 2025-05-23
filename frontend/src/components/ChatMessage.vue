<script setup>
import { useUserSettingsStore } from '@/stores/userSettings'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
  isLast: {
    type: Boolean,
    default: false,
  },
})

const userSettingsStore = useUserSettingsStore()
const isExpanded = ref(false)
const isRendered = ref(false)
const contentRef = ref(null)

// Render markdown and sanitize HTML
const renderedContent = computed(() => {
  if (!props.message.content) return ''

  try {
    const html = marked.parse(props.message.content.toString(), {
      breaks: true,
    })
    return DOMPurify.sanitize(html)
  } catch (error) {
    console.error('Error rendering markdown:', error)
    return props.message.content
  }
})

// Determine if the message should be truncated
const isTruncatable = computed(() => {
  if (!contentRef.value || isExpanded.value) return false
  return contentRef.value.scrollHeight > 300
})

// Watch for content changes (for streaming)
watch(
  () => props.message.content,
  () => {
    isRendered.value = true
  },
  { immediate: true },
)

// Toggle expanded state
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

// Format timestamp
const formatTime = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div
    :class="[
      'flex items-start gap-4 px-4 py-6 transition-opacity duration-300',
      message.role === 'assistant' ? 'bg-zinc-800/50 rounded-lg' : '',
      isStreaming ? 'animate-pulse' : '',
    ]"
  >
    <!-- Avatar -->
    <div
      :class="[
        'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white',
        message.role === 'assistant' ? 'bg-indigo-600' : 'bg-zinc-700',
      ]"
    >
      <!-- User avatar -->
      <template v-if="message.role === 'user'">
        <span class="text-lg font-medium">{{ userSettingsStore.displayInitial }}</span>
      </template>

      <!-- Assistant avatar -->
      <template v-else>
        <svg
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          ></path>
        </svg>
      </template>
    </div>

    <!-- Message content -->
    <div class="flex-1 min-w-0">
      <!-- Header -->
      <div class="flex items-center justify-between mb-2">
        <div class="font-medium text-gray-200">
          {{ message.role === 'assistant' ? 'AI Assistant' : userSettingsStore.displayName }}
        </div>
        <div class="text-xs text-gray-400">
          {{ formatTime(message.created_at) }}
        </div>
      </div>

      <!-- Content -->
      <div
        ref="contentRef"
        class="prose transition-all duration-300 prose-invert max-w-none"
        :class="[isTruncatable && !isExpanded ? 'max-h-[300px] overflow-hidden' : '']"
        v-html="renderedContent"
      ></div>

      <!-- Expand/collapse button -->
      <button
        v-if="isTruncatable"
        @click="toggleExpand"
        class="mt-2 text-sm text-indigo-400 hover:text-indigo-300"
      >
        {{ isExpanded ? 'Show less' : 'Read more' }}
      </button>

      <!-- Streaming indicator -->
      <div v-if="isStreaming" class="h-4 mt-1">
        <span class="inline-block w-2 h-2 bg-indigo-400 rounded-full animate-pulse"></span>
        <span
          class="inline-block w-2 h-2 ml-1 bg-indigo-400 rounded-full animate-pulse"
          style="animation-delay: 0.2s"
        ></span>
        <span
          class="inline-block w-2 h-2 ml-1 bg-indigo-400 rounded-full animate-pulse"
          style="animation-delay: 0.4s"
        ></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-content {
  line-height: 1.6;
  word-break: break-word;
}
</style>
