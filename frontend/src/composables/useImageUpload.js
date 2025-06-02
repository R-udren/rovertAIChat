// Composable for handling image upload and drag-drop functionality
import { useModelsStore } from '@/stores/models'
import { useToastStore } from '@/stores/toast'
import { computed, ref } from 'vue'

export function useImageUpload() {
  const toastStore = useToastStore()
  const modelsStore = useModelsStore()

  const currentImages = ref([])
  const isDragOverChat = ref(false)
  const isProcessingImages = ref(false)

  const canUploadImages = computed(() => {
    const selectedModel = localStorage.getItem('preferredModel')
    if (!selectedModel) return false
    return modelsStore.hasVisionCapability(selectedModel)
  })

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

  // Process image files for drag-and-drop
  const processImageFiles = async (files) => {
    if (!canUploadImages.value) {
      toastStore.error('Selected model does not support image uploads')
      return
    }

    if (files.length === 0) return

    isProcessingImages.value = true

    try {
      const imageFiles = files.filter((file) => file.type.startsWith('image/'))

      if (imageFiles.length === 0) {
        toastStore.error('Please select image files only')
        return
      }

      if (imageFiles.length > 5) {
        toastStore.error('Maximum 5 images allowed per message')
        return
      }

      const totalSize = imageFiles.reduce((sum, file) => sum + file.size, 0)
      const maxSize = 10 * 1024 * 1024 // 10MB total

      if (totalSize > maxSize) {
        toastStore.error('Total image size cannot exceed 10MB')
        return
      }

      const base64Images = await Promise.all(
        imageFiles.map(async (file) => {
          try {
            return await convertToBase64(file)
          } catch (error) {
            console.error('Error converting file to base64:', error)
            throw new Error(`Failed to process ${file.name}`)
          }
        }),
      )

      currentImages.value = [...currentImages.value, ...base64Images]
      toastStore.success(`${imageFiles.length} image(s) uploaded successfully`)

      return base64Images
    } catch (error) {
      console.error('Error processing images:', error)
      toastStore.error(error.message || 'Failed to process images')
    } finally {
      isProcessingImages.value = false
    }
  }

  // Handle drag and drop events for entire chat area
  const handleChatDragOver = (event) => {
    if (!canUploadImages.value) return
    event.preventDefault()
    event.dataTransfer.dropEffect = 'copy'
    isDragOverChat.value = true
  }

  const handleChatDragLeave = (event) => {
    if (!canUploadImages.value) return
    // Only hide overlay if leaving the main container
    if (!event.currentTarget.contains(event.relatedTarget)) {
      isDragOverChat.value = false
    }
  }

  const handleChatDrop = async (event) => {
    if (!canUploadImages.value) return
    event.preventDefault()
    isDragOverChat.value = false

    const files = Array.from(event.dataTransfer.files)
    if (files.length > 0) {
      return await processImageFiles(files)
    }
  }

  const clearImages = () => {
    currentImages.value = []
  }

  const clearImagesIfModelDoesntSupport = (model) => {
    if (!modelsStore.hasVisionCapability(model) && currentImages.value.length > 0) {
      clearImages()
      toastStore.info('Images cleared - selected model does not support vision')
    }
  }

  return {
    currentImages,
    isDragOverChat,
    isProcessingImages,
    canUploadImages,
    processImageFiles,
    handleChatDragOver,
    handleChatDragLeave,
    handleChatDrop,
    clearImages,
    clearImagesIfModelDoesntSupport,
  }
}
