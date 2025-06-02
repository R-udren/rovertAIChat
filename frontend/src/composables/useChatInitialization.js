// Composable for handling chat initialization logic
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'
import { useToastStore } from '@/stores/toast'
import { useUserSettingsStore } from '@/stores/userSettings'
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useChatInitialization() {
  const authStore = useAuthStore()
  const chatStore = useChatStore()
  const modelsStore = useModelsStore()
  const toastStore = useToastStore()
  const userSettingsStore = useUserSettingsStore()
  const route = useRoute()
  const router = useRouter()

  // Loading states
  const isInitializing = ref(true)
  const isLoadingSettings = ref(true)
  const isLoadingModels = ref(true)
  const isLoadingChats = ref(true)

  // Load user settings
  const loadUserSettings = async () => {
    try {
      await userSettingsStore.fetchSettings()
    } catch (error) {
      console.error('Error loading user settings:', error)
    } finally {
      isLoadingSettings.value = false
    }
  }

  // Load models
  const loadModels = async () => {
    try {
      await modelsStore.fetchModels()
    } catch (error) {
      console.error('Error loading models:', error)
    } finally {
      isLoadingModels.value = false
    }
  }

  // Load chats
  const loadChats = async () => {
    try {
      await chatStore.fetchChats()
    } catch (error) {
      console.error('Error loading chats:', error)
    } finally {
      isLoadingChats.value = false
    }
  }

  // Handle initial chat selection based on route
  const handleInitialChatSelection = async () => {
    // Wait for chats to be loaded before proceeding
    if (isLoadingChats.value) {
      await new Promise((resolve) => {
        const unwatch = watch(
          () => isLoadingChats.value,
          (loading) => {
            if (!loading) {
              unwatch()
              resolve()
            }
          },
        )
      })
    }

    if (route.params.id) {
      const chatId = route.params.id
      const conversation = chatStore.conversations.find((c) => c.id === chatId)

      if (conversation) {
        await chatStore.selectConversation(conversation)
      } else {
        // Chat ID not found, redirect to chat home
        router.push('/chat')
      }
    } else if (chatStore.conversations.length > 0) {
      // Load most recent chat
      await chatStore.selectConversation(chatStore.conversations[0])
      router.push(`/chat/${chatStore.conversations[0].id}`)
    }
  }

  // Initialize chat data asynchronously
  const initializeChat = async () => {
    if (!authStore.isAuthenticated) {
      toastStore.error('Please log in to use the chat feature')
      router.push('/login')
      return
    }

    try {
      // Start all initialization tasks in parallel
      const [settingsPromise, modelsPromise, chatsPromise] = [
        loadUserSettings(),
        loadModels(),
        loadChats(),
      ]

      // Wait for all to complete
      await Promise.all([settingsPromise, modelsPromise, chatsPromise])

      // Handle route-specific chat loading
      await handleInitialChatSelection()
    } catch (error) {
      console.error('Error during chat initialization:', error)
      toastStore.error('Failed to initialize chat. Please refresh the page.')
    } finally {
      isInitializing.value = false
    }
  }

  return {
    isInitializing,
    isLoadingSettings,
    isLoadingModels,
    isLoadingChats,
    initializeChat,
  }
}
