<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  messageInput: String,
  isSubmitting: Boolean,
  canUploadImages: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:messageInput', 'send-message', 'images-changed'])

const textareaRef = ref(null)
const fileInputRef = ref(null)
const expandedInput = ref(false)
const uploadedImages = ref([])
const isProcessingImages = ref(false)
const uploadFeedback = ref('')

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

// Handle input change
const handleInput = () => {
  emit('update:messageInput', textareaRef.value.value)
  adjustTextareaHeight()
}

// Handle image file selection
const handleImageUpload = (event) => {
  const files = Array.from(event.target.files)
  processImageFiles(files)
  // Reset file input
  event.target.value = ''
}

// Process image files and convert to base64
const processImageFiles = async (files) => {
  const imageFiles = files.filter((file) => file.type.startsWith('image/'))

  if (imageFiles.length === 0) {
    showUploadFeedback('No valid image files selected.', 'error')
    return
  }

  isProcessingImages.value = true
  showUploadFeedback(`Processing ${imageFiles.length} image(s)...`, 'info')

  let successCount = 0

  for (const file of imageFiles) {
    // Limit file size to 10MB
    if (file.size > 10 * 1024 * 1024) {
      showUploadFeedback(`Image ${file.name} is too large. Maximum size is 10MB.`, 'error')
      continue
    }

    try {
      const base64 = await convertToBase64(file)
      uploadedImages.value.push({
        id: Date.now() + Math.random(),
        name: file.name,
        base64: base64,
        url: URL.createObjectURL(file),
        size: file.size,
      })
      successCount++
    } catch (error) {
      console.error('Error converting image to base64:', error)
      showUploadFeedback(`Failed to process image ${file.name}`, 'error')
    }
  }

  isProcessingImages.value = false

  if (successCount > 0) {
    showUploadFeedback(`Successfully uploaded ${successCount} image(s)`, 'success')
    emit(
      'images-changed',
      uploadedImages.value.map((img) => img.base64),
    )
  }
}

// Show upload feedback
const showUploadFeedback = (message, type = 'info') => {
  uploadFeedback.value = { message, type }
  setTimeout(() => {
    uploadFeedback.value = ''
  }, 3000)
}

// Convert file to base64
const convertToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      // Remove the data:image/...;base64, prefix
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// Handle paste events for images
const handlePaste = async (event) => {
  if (!props.canUploadImages) return

  const items = Array.from(event.clipboardData?.items || [])
  const imageItems = items.filter((item) => item.type.startsWith('image/'))

  if (imageItems.length > 0) {
    event.preventDefault()
    const files = imageItems.map((item) => item.getAsFile()).filter(Boolean)
    await processImageFiles(files)
  }
}

// Remove uploaded image
const removeImage = (imageId) => {
  const imageIndex = uploadedImages.value.findIndex((img) => img.id === imageId)
  if (imageIndex !== -1) {
    // Revoke object URL to prevent memory leaks
    URL.revokeObjectURL(uploadedImages.value[imageIndex].url)
    uploadedImages.value.splice(imageIndex, 1)
    emit(
      'images-changed',
      uploadedImages.value.map((img) => img.base64),
    )
  }
}

// Clear all images
const clearImages = () => {
  uploadedImages.value.forEach((img) => URL.revokeObjectURL(img.url))
  uploadedImages.value = []
  emit('images-changed', [])
}

// Handle send message
const handleSendMessage = () => {
  emit('send-message')
  clearImages() // Clear images after sending
  resetTextareaHeight()
}

// Trigger file input
const triggerImageUpload = () => {
  fileInputRef.value?.click()
}

// Handle Enter key
const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSendMessage()
  }
}

// Enhanced upload button states
const uploadButtonClasses = computed(() => {
  const base = 'p-2 mr-2 transition-all duration-200 rounded-lg'
  const states = {
    default: 'text-gray-400 hover:text-white hover:bg-zinc-600',
    processing: 'text-blue-400 bg-blue-600/20 animate-pulse',
    hasImages: 'text-green-400 bg-green-600/20 hover:bg-green-600/30',
    disabled: 'text-gray-600 cursor-not-allowed opacity-50',
  }

  if (props.isSubmitting) return `${base} ${states.disabled}`
  if (isProcessingImages.value) return `${base} ${states.processing}`
  if (uploadedImages.value.length > 0) return `${base} ${states.hasImages}`
  return `${base} ${states.default}`
})

// Add images programmatically (for chat area drag-and-drop)
const addImages = async (base64Images) => {
  for (const base64 of base64Images) {
    const imageId = `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const imageUrl = `data:image/png;base64,${base64}`

    uploadedImages.value.push({
      id: imageId,
      base64,
      url: imageUrl,
      type: 'image/png',
    })
  }

  emit(
    'images-changed',
    uploadedImages.value.map((img) => img.base64),
  )
}

defineExpose({
  resetTextareaHeight,
  clearImages,
  addImages,
})
</script>

<template>
  <div class="relative p-4 border-t border-zinc-700 bg-zinc-800">
    <!-- Upload feedback -->
    <div v-if="uploadFeedback" class="mb-3">
      <div
        :class="[
          'px-3 py-2 rounded-lg text-sm flex items-center gap-2',
          uploadFeedback.type === 'success'
            ? 'bg-green-600/20 text-green-400 border border-green-600/30'
            : uploadFeedback.type === 'error'
              ? 'bg-red-600/20 text-red-400 border border-red-600/30'
              : 'bg-blue-600/20 text-blue-400 border border-blue-600/30',
        ]"
      >
        <svg
          v-if="uploadFeedback.type === 'success'"
          class="w-4 h-4"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clip-rule="evenodd"
          />
        </svg>
        <svg
          v-else-if="uploadFeedback.type === 'error'"
          class="w-4 h-4"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
        <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        {{ uploadFeedback.message }}
      </div>
    </div>

    <!-- Image preview area -->
    <div v-if="uploadedImages.length > 0" class="mb-3">
      <div class="flex flex-wrap gap-2 p-2 rounded-lg bg-zinc-700/50">
        <div v-for="image in uploadedImages" :key="image.id" class="relative group">
          <img
            :src="image.url"
            :alt="image.name"
            class="object-cover w-16 h-16 border rounded border-zinc-600"
          />
          <button
            @click="removeImage(image.id)"
            class="absolute flex items-center justify-center w-5 h-5 text-xs text-white transition-opacity bg-red-500 rounded-full opacity-0 -top-1 -right-1 hover:bg-red-600 group-hover:opacity-100"
            title="Remove image"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <div
      class="flex items-center justify-center px-2 transition-all rounded-lg bg-zinc-700 focus-within:ring-2 focus-within:ring-zinc-500"
    >
      <!-- Image upload button -->
      <button
        v-if="canUploadImages"
        @click="triggerImageUpload"
        :class="uploadButtonClasses"
        class="size-10"
        :disabled="isSubmitting"
        :title="
          isProcessingImages
            ? 'Processing images...'
            : uploadedImages.length > 0
              ? `${uploadedImages.length} image(s) uploaded`
              : 'Upload image or paste with Ctrl+V'
        "
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="size-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </button>

      <textarea
        ref="textareaRef"
        :value="messageInput"
        @input="handleInput"
        @keydown="handleKeyDown"
        @paste="handlePaste"
        placeholder="Type your message here..."
        class="flex-1 min-h-[40px] mr-2 bg-transparent resize-none text-white focus:outline-none mt-2"
        :disabled="isSubmitting"
      ></textarea>

      <button
        @click="handleSendMessage"
        class="p-2 text-white transition-colors rounded-lg hover:bg-zinc-600"
        :disabled="!messageInput.trim() || isSubmitting"
        :class="{ 'opacity-20 cursor-not-allowed': !messageInput.trim() || isSubmitting }"
      >
        <svg
          v-if="!isSubmitting"
          xmlns="http://www.w3.org/2000/svg"
          class="size-6"
          viewBox="0 0 16 16"
        >
          <!-- Icon from Fluent UI System Icons by Microsoft Corporation - https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE -->

          <path
            fill="currentColor"
            d="M1.177 1.119a.5.5 0 0 1 .547-.066l13 6.5a.5.5 0 0 1 0 .894l-13 6.5a.5.5 0 0 1-.702-.594L2.977 8L1.022 1.647a.5.5 0 0 1 .155-.528M3.869 8.5l-1.547 5.03L13.382 8L2.322 2.47L3.869 7.5H9.5a.5.5 0 0 1 0 1z"
          />
        </svg>
        <svg
          v-else
          class="size-6 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      </button>
    </div>

    <!-- Hidden file input -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      multiple
      @change="handleImageUpload"
      class="hidden"
    />
  </div>
</template>
