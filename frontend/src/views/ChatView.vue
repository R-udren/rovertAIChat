<script setup>
import { onMounted } from 'vue'
// Store imports
import { useChatStore } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'

// Import composables
import { useChatDeletion } from '@/composables/useChatDeletion'
import { useChatInitialization } from '@/composables/useChatInitialization'
import { useChatOperations } from '@/composables/useChatOperations'
import { useMessageActions } from '@/composables/useMessageActions'
import { useSidebar } from '@/composables/useSidebar'

// Access stores
const chatStore = useChatStore()
const modelsStore = useModelsStore()

// Initialize chat initialization composable
const { isInitializing, isLoadingSettings, isLoadingModels, isLoadingChats, initializeChat } =
  useChatInitialization()

// Initialize chat operations composable
const {
  messageInput,
  chatContainerRef,
  chatInputRef,
  isSubmitting,
  selectedModel,
  scrollToBottom,
  sendMessage,
  startNewChat,
  selectChat,
  updateChatTitle,
  handleModelChange,
} = useChatOperations()

// Initialize chat deletion composable
const {
  showDeleteModal,
  deleteModalType,
  chatToDelete,
  deleteChat,
  deleteChats,
  confirmDeleteModal,
} = useChatDeletion()

// Initialize sidebar composable
const { showSidebar, isMobileSidebarOpen, toggleSidebar, toggleMobileSidebar } = useSidebar()

// Initialize message actions composable
const {
  isEditing,
  messageBeingEdited,
  editedContent,
  editError,
  isSavingEdit,
  startEditing,
  cancelEditing,
  saveEdit,
  deleteMessage,
} = useMessageActions()

// Initialize chat when component mounts
onMounted(() => {
  initializeChat()
})
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-64px)] w-full bg-zinc-900">
    <!-- Loading Screen -->
    <ChatLoadingScreen
      v-if="isInitializing"
      :is-loading-settings="isLoadingSettings"
      :is-loading-models="isLoadingModels"
      :is-loading-chats="isLoadingChats"
    />

    <!-- Main Chat Interface - Only show when not initializing -->
    <template v-else>
      <!-- Mobile Header -->
      <Suspense>
        <template #default>
          <ChatHeader
            :current-conversation="chatStore.currentConversation"
            :selected-model="selectedModel"
            :is-mobile="true"
            @toggle-mobile-sidebar="toggleMobileSidebar"
            @start-new-chat="startNewChat"
            @model-changed="handleModelChange"
            @update-chat-title="updateChatTitle"
          />
        </template>
        <template #fallback>
          <div class="h-16 bg-zinc-800/50 animate-pulse"></div>
        </template>
      </Suspense>

      <div class="flex flex-1 w-full overflow-hidden">
        <!-- Sidebar - Always render for proper mobile support -->
        <Suspense>
          <template #default>
            <ChatSidebar
              :show-sidebar="showSidebar"
              :is-mobile-sidebar-open="isMobileSidebarOpen"
              :conversations="chatStore.conversations"
              :current-conversation="chatStore.currentConversation"
              :loading="chatStore.loading"
              @toggle-mobile-sidebar="toggleMobileSidebar"
              @start-new-chat="startNewChat"
              @select-chat="selectChat"
              @delete-chat="deleteChat"
              @delete-chats="deleteChats"
              @update-chat-title="updateChatTitle"
            />
          </template>
          <template #fallback>
            <div class="w-80 bg-zinc-800/50 animate-pulse"></div>
          </template>
        </Suspense>

        <!-- Chat Area -->
        <div class="relative flex flex-col flex-1 w-full overflow-hidden">
          <!-- Desktop Header -->
          <Suspense>
            <template #default>
              <ChatHeader
                :current-conversation="chatStore.currentConversation"
                :selected-model="selectedModel"
                :is-mobile="false"
                @toggle-sidebar="toggleSidebar"
                @start-new-chat="startNewChat"
                @model-changed="handleModelChange"
                @update-chat-title="updateChatTitle"
              />
            </template>
            <template #fallback>
              <div class="h-16 bg-zinc-800/50 animate-pulse"></div>
            </template>
          </Suspense>

          <!-- Ollama Status Indicator -->
          <div
            v-if="!modelsStore.isOllamaAvailable || modelsStore.ollamaStatus === 'loading'"
            class="px-4 py-2 border-b bg-zinc-800/50 border-zinc-700/50"
          >
            <Suspense>
              <template #default>
                <OllamaStatusIndicator :compact="true" />
              </template>
              <template #fallback>
                <div class="h-8 rounded bg-zinc-700/50 animate-pulse"></div>
              </template>
            </Suspense>
          </div>

          <!-- Messages -->
          <Suspense>
            <template #default>
              <ChatContainer
                ref="chatContainerRef"
                :current-conversation="chatStore.currentConversation"
                :messages="chatStore.messages"
                :loading="chatStore.loading"
                :streaming="chatStore.streaming"
                :is-editing="isEditing"
                :message-being-edited="messageBeingEdited"
                :edit-error="editError"
                :is-saving-edit="isSavingEdit"
                @start-new-chat="startNewChat"
                @edit-message="startEditing"
                @delete-message="deleteMessage"
                @save-edit="saveEdit"
                @cancel-edit="cancelEditing"
              />
            </template>
            <template #fallback>
              <div class="flex-1 bg-zinc-900/50 animate-pulse"></div>
            </template>
          </Suspense>

          <!-- Input Area -->
          <Suspense>
            <template #default>
              <ChatInput
                ref="chatInputRef"
                v-model:message-input="messageInput"
                :is-submitting="isSubmitting"
                @send-message="sendMessage"
              />
            </template>
            <template #fallback>
              <div class="h-20 bg-zinc-800/50 animate-pulse"></div>
            </template>
          </Suspense>
        </div>
      </div>
    </template>

    <!-- Delete Confirmation Modal -->
    <Suspense>
      <ConfirmationModal
        :is-open="showDeleteModal"
        type="warning"
        :title="deleteModalType === 'single' ? 'Delete Chat' : 'Delete All Chats'"
        :message="
          deleteModalType === 'single'
            ? 'Are you sure you want to delete this chat? This action cannot be undone.'
            : `Are you sure you want to delete all ${chatStore.conversations.length} chat${chatStore.conversations.length > 1 ? 's' : ''}? This action cannot be undone.`
        "
        :confirm-text="deleteModalType === 'single' ? 'Delete Chat' : 'Delete All Chats'"
        cancel-text="Cancel"
        @confirm="confirmDeleteModal"
        @cancel="showDeleteModal = false"
        @close="showDeleteModal = false"
      />
    </Suspense>
  </div>
</template>
