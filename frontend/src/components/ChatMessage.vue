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
const copySuccess = ref({}) // To track copy success state for each code block
const imageModalOpen = ref(false)
const selectedImageUrl = ref('')

// ...existing code...

// Open image in modal
const openImageModal = (imageUrl) => {
  selectedImageUrl.value = imageUrl
  imageModalOpen.value = true
}

// Close image modal
const closeImageModal = () => {
  imageModalOpen.value = false
  selectedImageUrl.value = ''
}

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

// Check if message has images
const hasImages = computed(() => {
  return props.message.images && props.message.images.length > 0
})

// Convert base64 to data URL for display
const getImageDataUrl = (base64) => {
  // Check if it already has the data URL prefix
  if (base64.startsWith('data:')) {
    return base64
  }
  // Assume PNG if no prefix (most common format for uploads)
  return `data:image/png;base64,${base64}`
}

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
  ADD_ATTR: ['class', 'style', 'data-lang', 'target', 'rel', 'data-toggle'],
  ADD_TAGS: ['span', 'div', 'think', 'button', 'details', 'summary'],
})

// Render markdown and sanitize HTML
const renderedContent = computed(() => {
  if (!props.message.content && !props.message.isLoading) return ''

  // If message is loading, return the typing animation placeholder
  if (props.message.isLoading) {
    return '<div class="typing-animation"><span></span><span></span><span></span></div>'
  }

  try {
    // Process <think> tags before passing to marked
    let content = props.message.content.toString()

    // Replace <think> tags with HTML5 details/summary for native collapsible behavior
    content = content.replace(/<think>([\s\S]*?)<\/think>/g, (_match, thinkContent) => {
      // Use HTML5 details/summary for native collapsible functionality with improved accessibility
      return `
<details class="thinking-block">
  <summary class="thinking-summary" role="button" aria-expanded="false" tabindex="0">
    <span class="thinking-icon" aria-hidden="true"></span>
    <span class="thinking-label">Thinking process</span>
  </summary>
  <div class="thinking-content">
    ${thinkContent}
  </div>
</details>
      `
    })

    const html = marked.parse(content)
    return DOMPurify.sanitize(html)
  } catch (error) {
    console.error('Error rendering markdown:', error)
    return props.message.content
  }
})

// Function to copy code to clipboard
const copyCodeToClipboard = (code, id) => {
  // Check if Clipboard API is available
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(code).then(
      () => {
        // Set success state for this specific code block
        copySuccess.value[id] = true

        // Reset success state after 2 seconds
        setTimeout(() => {
          copySuccess.value[id] = false
        }, 2000)
      },
      (err) => {
        console.error('Could not copy text: ', err)
        fallbackCopyTextToClipboard(code, id)
      },
    )
  } else {
    // Fallback for browsers that don't support clipboard API
    fallbackCopyTextToClipboard(code, id)
  }
}

// Fallback method using a temporary textarea element
const fallbackCopyTextToClipboard = (text, id) => {
  const textArea = document.createElement('textarea')
  textArea.value = text
  textArea.style.position = 'fixed'
  textArea.style.left = '0'
  textArea.style.top = '0'
  textArea.style.opacity = '0'
  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()

  try {
    const successful = document.execCommand('copy')
    if (successful) {
      copySuccess.value[id] = true
      setTimeout(() => {
        copySuccess.value[id] = false
      }, 2000)
    } else {
      console.error('Failed to copy using fallback method')
    }
  } catch (err) {
    console.error('Fallback copy method failed:', err)
  }

  document.body.removeChild(textArea)
}

// Determine if the message should be truncated
const isTruncatable = computed(() => {
  if (!contentRef.value || isExpanded.value) return false
  return contentRef.value.scrollHeight > 500
})

// No need for custom event listeners or watchers with HTML5 details/summary

// Watch for content changes (for streaming)
watch(
  () => props.message.content,
  () => {
    isRendered.value = true
    // Apply syntax highlighting to code blocks on content update
    nextTick(() => {
      if (contentRef.value) {
        // Highlight all code blocks
        const codeBlocks = contentRef.value.querySelectorAll('pre code')
        codeBlocks.forEach((block, index) => {
          hljs.highlightElement(block)

          // Generate a unique ID for this code block
          const blockId = `code-block-${props.message.id}-${index}`

          // Get the parent pre element
          const preElement = block.parentElement

          // Only add the copy button if it doesn't already exist
          if (!preElement.querySelector('.copy-code-button')) {
            // Create the copy button container
            const buttonContainer = document.createElement('div')
            buttonContainer.className = 'copy-code-button-container'

            // Create the copy button
            const copyButton = document.createElement('button')
            copyButton.className = 'copy-code-button'
            copyButton.setAttribute('aria-label', 'Copy code')
            copyButton.innerHTML = `
              <svg xmlns="http://www.w3.org/2000/svg" class="copy-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <svg xmlns="http://www.w3.org/2000/svg" class="check-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            `
            buttonContainer.appendChild(copyButton)

            // Add button container to pre element
            preElement.style.position = 'relative'
            preElement.appendChild(buttonContainer)

            // Add click event listener
            copyButton.addEventListener('click', () => {
              copyCodeToClipboard(block.textContent, blockId)

              // Show success state
              copyButton.classList.add('copied')

              // Remove success state after animation completes
              setTimeout(() => {
                copyButton.classList.remove('copied')
              }, 2000)
            })
          }
        })

        // Set up details element enhancements
        const detailsElements = contentRef.value.querySelectorAll('.thinking-block')
        detailsElements.forEach((details) => {
          const summary = details.querySelector('summary')

          // Update aria-expanded attribute on toggle
          details.addEventListener('toggle', (e) => {
            if (summary) {
              summary.setAttribute('aria-expanded', e.target.open ? 'true' : 'false')
            }

            if (e.target.open) {
              // Re-highlight code blocks when details are opened
              const thinkingCodeBlocks = e.target.querySelectorAll('pre code')
              thinkingCodeBlocks.forEach((block) => {
                hljs.highlightElement(block)
              })
            }
          })

          // Add keyboard support for Enter and Space
          if (summary) {
            summary.addEventListener('keydown', (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                details.open = !details.open

                // Trigger the toggle event manually
                details.dispatchEvent(new Event('toggle'))
              }
            })
          }
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

// Check if this is a system message
const isSystemMessage = computed(() => {
  return props.message.role === 'system'
})

// Check if this is an error message
const isErrorMessage = computed(() => {
  return props.message.isError === true
})
</script>

<template>
  <!-- System/Error Messages -->
  <div
    v-if="isSystemMessage"
    :class="[
      'flex items-center justify-center px-4 py-3 mx-4 mb-4 rounded-lg transition-opacity duration-300',
      isErrorMessage
        ? 'bg-red-900/20 border border-red-500/30 text-red-300'
        : 'bg-blue-900/20 border border-blue-500/30 text-blue-300',
      isStreaming ? 'animate-pulse opacity-80' : 'opacity-100',
    ]"
  >
    <div class="flex items-center gap-2 text-sm">
      <!-- Error icon -->
      <svg
        v-if="isErrorMessage"
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5 text-red-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
        />
      </svg>
      <!-- Info icon -->
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5 text-blue-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>{{ message.content }}</span>
      <span v-if="message.timestamp" class="ml-2 text-xs opacity-60">
        {{ formatTime(message.timestamp) }}
      </span>
    </div>
  </div>

  <!-- Regular User/Assistant Messages -->
  <div
    v-else
    :class="[
      'flex items-start gap-4 px-4 py-6 transition-opacity duration-300',
      message.role === 'assistant' ? 'bg-zinc-800/50 rounded-lg' : '',
      isStreaming || message.isLoading ? 'opacity-80' : 'opacity-100',
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
          {{ formatTime(message.created_at || message.timestamp) }}
        </div>
      </div>

      <!-- Content -->
      <div
        ref="contentRef"
        class="prose transition-all duration-300 message-content prose-invert max-w-none"
        :class="[isTruncatable && !isExpanded ? 'max-h-[500px] overflow-hidden gradient-mask' : '']"
        v-html="renderedContent"
      ></div>

      <!-- Images -->
      <div v-if="hasImages" class="mt-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="(image, index) in message.images" :key="index" class="relative group">
            <div class="relative overflow-hidden rounded-lg">
              <img
                :src="getImageDataUrl(image)"
                :alt="`Message image ${index + 1}`"
                class="w-full h-auto max-w-sm transition-all duration-200 border rounded-lg shadow-lg cursor-pointer border-zinc-600 hover:border-zinc-400"
                @click="openImageModal(getImageDataUrl(image))"
              />
              <div
                class="absolute inset-0 flex items-center justify-center transition-all duration-200 rounded-lg opacity-0 pointer-events-none bg-black/50 group-hover:opacity-100"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-8 h-8 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Expand/collapse button -->
      <button
        v-if="isTruncatable"
        @click="toggleExpand"
        class="px-2 py-1 mt-2 text-sm text-indigo-400 transition-colors rounded hover:text-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50"
      >
        {{ isExpanded ? 'Show less' : 'Read more' }}
      </button>

      <!-- Streaming indicator -->
      <div v-if="isStreaming && !message.isLoading" class="h-4 mt-1">
        <span class="inline-block w-2 h-2 bg-indigo-400 rounded-full animate-pulse"></span>
        <span style="animation-delay: 0.2s"></span>
        <span style="animation-delay: 0.4s"></span>
      </div>
    </div>
  </div>

  <!-- Image Modal -->
  <div
    v-if="imageModalOpen"
    class="fixed inset-0 z-50 flex items-center justify-center h-full p-4 bg-black/75"
    @click="closeImageModal"
  >
    <div class="relative max-w-4xl max-h-full">
      <img
        :src="selectedImageUrl"
        alt="Full size image"
        class="max-w-full max-h-full rounded-lg shadow-2xl"
        @click.stop
      />
      <button
        @click="closeImageModal"
        class="absolute flex items-center justify-center w-10 h-10 text-white transition-all duration-200 rounded-full bg-black/50 top-4 right-4 hover:bg-black/75"
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
  position: relative; /* For copy button positioning */
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

/* Copy code button styles */
.copy-code-button-container {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 10;
}

.copy-code-button {
  background-color: rgba(30, 30, 30, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 0.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  cursor: pointer;
  opacity: 0.6;
  transition:
    opacity 0.2s,
    background-color 0.2s;
  color: #a1a1aa;
}

.copy-code-button:hover {
  opacity: 1;
  background-color: rgba(50, 50, 50, 0.7);
  color: #f1f1f1;
}

.copy-code-button svg {
  width: 16px;
  height: 16px;
}

.copy-code-button .check-icon {
  display: none;
}

.copy-code-button.copied .copy-icon {
  display: none;
}

.copy-code-button.copied .check-icon {
  display: block;
  color: #10b981;
}

.copy-code-button.copied {
  background-color: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.3);
}

/* Typing animation styles */
.typing-animation {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.5rem 0;
  height: 2rem;
}

.typing-animation span {
  display: inline-block;
  width: 0.5rem;
  height: 0.5rem;
  background-color: #818cf8;
  border-radius: 50%;
  opacity: 0.6;
  animation: typing 1.4s ease-in-out infinite;
}

.typing-animation span:nth-child(1) {
  animation-delay: 0s;
}

.typing-animation span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-animation span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-0.5rem);
    opacity: 1;
  }
}

/* Remaining styles */
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

.message-content h1 {
  font-size: 2rem;
}

.message-content h2 {
  font-size: 1.75rem;
}

.message-content h3 {
  font-size: 1.5rem;
}

.message-content h4 {
  font-size: 1.25rem;
}

.message-content h5 {
  font-size: 1.125rem;
}

.message-content h6 {
  font-size: 1rem;
}

.message-content ul,
.message-content ol {
  padding-left: 1.5rem;
  margin: 1rem 0;
  list-style-position: outside;
  list-style-type: disc;
}

.message-content li {
  margin: 0.5rem 0;
  line-height: 1.5;
  list-style-type: disc;
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

/* Styling for thinking blocks using HTML5 details/summary */
.message-content .thinking-block {
  border: 1px solid rgba(107, 114, 128, 0.3);
  border-radius: 0.375rem;
  margin: 1.25rem 0;
  background-color: rgba(30, 30, 30, 0.3);
  color: #a1a1aa;
  overflow: hidden;
}

.message-content .thinking-summary {
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  user-select: none;
  transition: background-color 0.15s ease;
}

.message-content .thinking-summary:hover {
  background-color: rgba(55, 55, 55, 0.3);
}

.message-content .thinking-summary::-webkit-details-marker {
  display: none;
}

.message-content .thinking-icon {
  position: relative;
  width: 0.6rem;
  height: 0.6rem;
}

.message-content .thinking-icon:before {
  content: '';
  position: absolute;
  border-right: 2px solid #a1a1aa;
  border-bottom: 2px solid #a1a1aa;
  width: 0.4rem;
  height: 0.4rem;
  transform: rotate(-45deg);
  transition: transform 0.2s ease;
}

.message-content details[open] .thinking-icon:before {
  transform: rotate(45deg);
}

.message-content .thinking-label {
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.01em;
}

.message-content .thinking-content {
  padding: 0.75rem 1rem 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
  border-top: 1px solid rgba(107, 114, 128, 0.2);
}

/* Additional styling for links and code inside thinking blocks */
.message-content .thinking-content a {
  color: #94a3b8;
  text-decoration: underline;
  text-underline-offset: 0.15rem;
}

.message-content .thinking-content code {
  color: #cbd5e1;
  background-color: rgba(30, 30, 30, 0.5);
}

/* Improved styling for lists in thinking content */
.message-content .thinking-content ul,
.message-content .thinking-content ol {
  margin: 0.5rem 0;
}

.message-content .thinking-content li {
  margin: 0.25rem 0;
}
</style>
