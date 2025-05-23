<script setup>
import { useUserSettingsStore } from '@/stores/userSettings'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
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

// User display name and initial for avatar
const displayName = computed(() => {
  return userSettingsStore.settings?.display_name || 'User'
})

const displayInitial = computed(() => {
  const name = displayName.value
  return name ? name.charAt(0).toUpperCase() : 'U'
})

// Check if user has an avatar image
const hasAvatar = computed(() => {
  return !!userSettingsStore.settings?.avatar_url
})

// Get user avatar URL
const avatarUrl = computed(() => {
  return userSettingsStore.settings?.avatar_url || ''
})

// Configure marked with code highlighting
marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('Highlight.js error:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
  renderer: (function () {
    const renderer = new marked.Renderer()
    // Make links open in new tab by default
    const linkRenderer = renderer.link
    renderer.link = (href, title, text) => {
      const html = linkRenderer.call(renderer, href, title, text)
      return html.replace(/^<a /, '<a target="_blank" rel="noopener noreferrer" ')
    }
    return renderer
  })(),
})

// Setup DOMPurify to allow certain attributes for styling
DOMPurify.setConfig({
  ADD_ATTR: ['class', 'style', 'data-lang', 'target', 'rel'],
  ADD_TAGS: ['span', 'div'],
})

// Render markdown and sanitize HTML
const renderedContent = computed(() => {
  if (!props.message.content) return ''

  try {
    const html = marked.parse(props.message.content.toString())
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
    // Apply syntax highlighting to code blocks on content update
    nextTick(() => {
      if (contentRef.value) {
        const codeBlocks = contentRef.value.querySelectorAll('pre code')
        codeBlocks.forEach((block) => {
          hljs.highlightElement(block)
        })
      }
    })
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
      isStreaming ? 'animate-pulse opacity-80' : 'opacity-100',
    ]"
  >
    <!-- Avatar -->
    <div
      :class="[
        'flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-white overflow-hidden',
        message.role === 'assistant' ? 'bg-indigo-600' : 'bg-zinc-700',
        'shadow-md border border-gray-700',
      ]"
      aria-hidden="true"
    >
      <!-- User avatar -->
      <template v-if="message.role === 'user'">
        <img
          v-if="hasAvatar"
          :src="avatarUrl"
          :alt="displayName"
          class="object-cover w-full h-full"
        />
        <span v-else class="text-lg font-medium">{{ displayInitial }}</span>
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
          {{ message.role === 'assistant' ? 'AI Assistant' : displayName }}
        </div>
        <div class="text-xs text-gray-400">
          {{ formatTime(message.created_at) }}
        </div>
      </div>

      <!-- Content -->
      <div
        ref="contentRef"
        class="prose transition-all duration-300 message-content prose-invert max-w-none"
        :class="[isTruncatable && !isExpanded ? 'max-h-[300px] overflow-hidden gradient-mask' : '']"
        v-html="renderedContent"
      ></div>

      <!-- Expand/collapse button -->
      <button
        v-if="isTruncatable"
        @click="toggleExpand"
        class="px-2 py-1 mt-2 text-sm text-indigo-400 transition-colors rounded hover:text-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50"
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

<style>
/* Target syntax highlighting for code blocks */
.hljs {
  background: #282c34 !important;
  border-radius: 0.375rem;
  padding: 1rem !important;
  margin: 1rem 0;
  overflow-x: auto;
}

/* Override default prose styling for our chat messages */
.message-content {
  line-height: 1.6;
  word-break: break-word;
}

.message-content pre {
  background: #282c34;
  border-radius: 0.375rem;
  margin: 1rem 0;
  padding: 0;
}

.message-content code {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.message-content :not(pre) > code {
  background-color: rgba(40, 44, 52, 0.5);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  white-space: nowrap;
}

.message-content p {
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
}

.message-content h1,
.message-content h2,
.message-content h3,
.message-content h4,
.message-content h5,
.message-content h6 {
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  line-height: 1.25;
}

.message-content ul,
.message-content ol {
  padding-left: 1.5rem;
  margin: 1rem 0;
}

.message-content li {
  margin: 0.5rem 0;
}

.message-content blockquote {
  border-left: 4px solid #6366f1;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #d1d5db;
  font-style: italic;
}

.message-content table {
  border-collapse: collapse;
  margin: 1rem 0;
  width: 100%;
}

.message-content th,
.message-content td {
  padding: 0.5rem;
  border: 1px solid #4b5563;
}

.message-content th {
  background-color: #374151;
  font-weight: 600;
}

.message-content a {
  color: #818cf8;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.message-content a:hover {
  color: #6366f1;
}

.gradient-mask {
  mask-image: linear-gradient(to bottom, black 75%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 75%, transparent 100%);
}
</style>
