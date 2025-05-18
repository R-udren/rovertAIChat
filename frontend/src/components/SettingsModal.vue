<script setup>
import { useToastStore } from '@/stores/toast'
import { useUserSettingsStore } from '@/stores/userSettings'
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['close', 'save'])

const userSettingsStore = useUserSettingsStore()
const toastStore = useToastStore()

const isSubmitting = ref(false)
const activeTab = ref('appearance')

const formData = ref({
  display_name: '',
  avatar_url: '',
  default_model_id: '',
  preferences: {
    theme: 'dark',
    fontSize: 'medium',
    chatBubbleStyle: 'rounded',
    messageSound: true,
    notifications: true,
  },
})

// Font size options
const fontSizes = [
  { value: 'small', label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large', label: 'Large' },
]

// Chat bubble style options
const bubbleStyles = [
  { value: 'rounded', label: 'Rounded' },
  { value: 'square', label: 'Square' },
  { value: 'modern', label: 'Modern' },
]

// Available themes
const themes = [
  { value: 'dark', label: 'Dark' },
  { value: 'light', label: 'Light' },
  { value: 'system', label: 'System' },
]

// Initialize form with current settings
const initializeForm = () => {
  if (userSettingsStore.settings) {
    formData.value.display_name = userSettingsStore.settings.display_name || ''
    formData.value.avatar_url = userSettingsStore.settings.avatar_url || ''
    formData.value.default_model_id = userSettingsStore.settings.default_model_id || ''
    formData.value.preferences = { ...userSettingsStore.settings.preferences } || {
      theme: 'dark',
      fontSize: 'medium',
      chatBubbleStyle: 'rounded',
      messageSound: true,
      notifications: true,
    }
  }
}

// Handle tab switching
const switchTab = (tab) => {
  activeTab.value = tab
}

// Close modal handler
const handleClose = () => {
  emit('close')
}

// Submit handler
const handleSubmit = async () => {
  isSubmitting.value = true

  try {
    await userSettingsStore.updateSettings({
      display_name: formData.value.display_name || null,
      avatar_url: formData.value.avatar_url || null,
      default_model_id: formData.value.default_model_id || null,
      preferences: formData.value.preferences || null,
    })

    toastStore.success('Settings updated successfully')
    emit('save')
  } catch (error) {
    toastStore.error('Failed to update settings')
  } finally {
    isSubmitting.value = false
  }
}

// Close modal when escape key is pressed
const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    handleClose()
  }
}

onMounted(() => {
  initializeForm()
  document.addEventListener('keydown', handleKeydown)
})

// Clean up event listener
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// Watch for open state changes to initialize form data
watch(
  () => props.isOpen,
  () => {
    if (props.isOpen) {
      initializeForm()
    }
  },
)

// Watch for changes in the store settings
watch(
  () => userSettingsStore.settings,
  () => {
    if (userSettingsStore.settings) {
      initializeForm()
    }
  },
  { deep: true },
)
</script>

<template>
  <Transition name="modal">
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black/70 backdrop-blur-sm" @click="handleClose"></div>

      <!-- Modal -->
      <div
        class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-zinc-900 rounded-xl shadow-2xl border border-zinc-800 glass-effect animate-slide-up"
      >
        <!-- Header -->
        <div
          class="sticky top-0 z-10 flex items-center justify-between p-4 border-b border-zinc-800 bg-zinc-900/90 backdrop-blur-md"
        >
          <h2 class="text-xl font-medium text-white">Settings</h2>
          <button
            @click="handleClose"
            class="p-2 text-gray-400 transition-colors rounded-full hover:text-white hover:bg-zinc-800"
            aria-label="Close modal"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="flex flex-col md:flex-row">
          <!-- Tabs sidebar -->
          <div
            class="w-full p-2 border-b md:w-48 md:border-b-0 md:border-r border-zinc-800 md:h-[500px]"
          >
            <div class="flex space-x-2 overflow-x-auto md:flex-col md:space-x-0 md:space-y-1">
              <button
                @click="switchTab('appearance')"
                :class="[
                  'px-4 py-3 rounded-lg text-left w-full whitespace-nowrap transition-colors',
                  activeTab === 'appearance'
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'hover:bg-zinc-800/70 text-gray-300',
                ]"
              >
                <span class="flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                    />
                  </svg>
                  Appearance
                </span>
              </button>
              <button
                @click="switchTab('account')"
                :class="[
                  'px-4 py-3 rounded-lg text-left w-full whitespace-nowrap transition-colors',
                  activeTab === 'account'
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'hover:bg-zinc-800/70 text-gray-300',
                ]"
              >
                <span class="flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                  Account
                </span>
              </button>
              <button
                @click="switchTab('notifications')"
                :class="[
                  'px-4 py-3 rounded-lg text-left w-full whitespace-nowrap transition-colors',
                  activeTab === 'notifications'
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'hover:bg-zinc-800/70 text-gray-300',
                ]"
              >
                <span class="flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                  </svg>
                  Notifications
                </span>
              </button>
            </div>
          </div>

          <!-- Tab content -->
          <div class="flex-1 p-4">
            <form @submit.prevent="handleSubmit">
              <!-- Appearance Tab -->
              <div v-show="activeTab === 'appearance'">
                <h3 class="text-lg font-medium text-white">Appearance Settings</h3>
                <p class="mt-1 text-sm text-gray-400">
                  Customize how rovertAIChat looks and feels.
                </p>

                <div class="mt-6 space-y-6">
                  <!-- Theme -->
                  <div>
                    <label class="block mb-2 text-sm font-medium text-gray-300">Theme</label>
                    <div class="grid grid-cols-3 gap-3">
                      <div
                        v-for="theme in themes"
                        :key="theme.value"
                        @click="formData.preferences.theme = theme.value"
                        :class="[
                          'flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-all',
                          formData.preferences.theme === theme.value
                            ? 'border-primary-500 bg-primary-900/30 text-primary-400'
                            : 'border-zinc-700 bg-zinc-800/50 text-gray-300 hover:bg-zinc-800',
                        ]"
                      >
                        {{ theme.label }}
                      </div>
                    </div>
                  </div>

                  <!-- Font Size -->
                  <div>
                    <label class="block mb-2 text-sm font-medium text-gray-300">Font Size</label>
                    <div class="grid grid-cols-3 gap-3">
                      <div
                        v-for="size in fontSizes"
                        :key="size.value"
                        @click="formData.preferences.fontSize = size.value"
                        :class="[
                          'flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-all',
                          formData.preferences.fontSize === size.value
                            ? 'border-primary-500 bg-primary-900/30 text-primary-400'
                            : 'border-zinc-700 bg-zinc-800/50 text-gray-300 hover:bg-zinc-800',
                        ]"
                      >
                        {{ size.label }}
                      </div>
                    </div>
                  </div>

                  <!-- Chat Bubble Style -->
                  <div>
                    <label class="block mb-2 text-sm font-medium text-gray-300"
                      >Chat Bubble Style</label
                    >
                    <div class="grid grid-cols-3 gap-3">
                      <div
                        v-for="style in bubbleStyles"
                        :key="style.value"
                        @click="formData.preferences.chatBubbleStyle = style.value"
                        :class="[
                          'flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-all',
                          formData.preferences.chatBubbleStyle === style.value
                            ? 'border-primary-500 bg-primary-900/30 text-primary-400'
                            : 'border-zinc-700 bg-zinc-800/50 text-gray-300 hover:bg-zinc-800',
                        ]"
                      >
                        {{ style.label }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Account Tab -->
              <div v-show="activeTab === 'account'">
                <h3 class="text-lg font-medium text-white">Account Information</h3>
                <p class="mt-1 text-sm text-gray-400">Update your profile and account settings.</p>

                <div class="mt-6 space-y-6">
                  <!-- Display Name -->
                  <div>
                    <label for="display_name" class="block mb-2 text-sm font-medium text-gray-300"
                      >Display Name</label
                    >
                    <input
                      id="display_name"
                      v-model="formData.display_name"
                      type="text"
                      class="w-full px-4 py-2 text-white border rounded-lg bg-zinc-800/80 border-zinc-700 focus:outline-none focus:border-primary-500"
                      placeholder="Your display name"
                    />
                  </div>

                  <!-- Avatar URL -->
                  <div>
                    <label for="avatar_url" class="block mb-2 text-sm font-medium text-gray-300"
                      >Avatar URL</label
                    >
                    <input
                      id="avatar_url"
                      v-model="formData.avatar_url"
                      type="url"
                      class="w-full px-4 py-2 text-white border rounded-lg bg-zinc-800/80 border-zinc-700 focus:outline-none focus:border-primary-500"
                      placeholder="https://example.com/avatar.jpg"
                    />
                    <p class="mt-1 text-xs text-gray-500">
                      Enter URL to an image for your profile picture
                    </p>

                    <!-- Avatar preview -->
                    <div v-if="formData.avatar_url" class="flex items-center mt-4 space-x-4">
                      <div class="text-sm text-gray-400">Preview:</div>
                      <img
                        :src="formData.avatar_url"
                        class="object-cover w-12 h-12 border-2 rounded-full border-zinc-700"
                        alt="Avatar preview"
                        @error="formData.avatar_url = ''"
                      />
                    </div>
                  </div>

                  <!-- Default Model -->
                  <div>
                    <label for="default_model" class="block mb-2 text-sm font-medium text-gray-300"
                      >Default AI Model</label
                    >
                    <input
                      id="default_model"
                      v-model="formData.default_model_id"
                      type="text"
                      class="w-full px-4 py-2 text-white border rounded-lg bg-zinc-800/80 border-zinc-700 focus:outline-none focus:border-primary-500"
                      placeholder="gpt-3.5-turbo"
                    />
                    <p class="mt-1 text-xs text-gray-500">
                      The default AI model to use for new conversations
                    </p>
                  </div>
                </div>
              </div>

              <!-- Notifications Tab -->
              <div v-show="activeTab === 'notifications'">
                <h3 class="text-lg font-medium text-white">Notification Settings</h3>
                <p class="mt-1 text-sm text-gray-400">
                  Control how and when you receive notifications.
                </p>

                <div class="mt-6 space-y-6">
                  <!-- Message Sounds -->
                  <div class="flex items-center justify-between">
                    <div>
                      <h4 class="text-sm font-medium text-gray-200">Message Sounds</h4>
                      <p class="text-xs text-gray-400">Play a sound when you receive a message</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        v-model="formData.preferences.messageSound"
                        class="sr-only peer"
                      />
                      <div
                        class="w-11 h-6 bg-zinc-700 rounded-full peer-checked:bg-primary-600 peer-focus:ring-2 peer-focus:ring-primary-500/30 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:border-zinc-600 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-5"
                      ></div>
                    </label>
                  </div>

                  <!-- Browser Notifications -->
                  <div class="flex items-center justify-between">
                    <div>
                      <h4 class="text-sm font-medium text-gray-200">Browser Notifications</h4>
                      <p class="text-xs text-gray-400">Show notifications in your browser</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        v-model="formData.preferences.notifications"
                        class="sr-only peer"
                      />
                      <div
                        class="w-11 h-6 bg-zinc-700 rounded-full peer-checked:bg-primary-600 peer-focus:ring-2 peer-focus:ring-primary-500/30 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:border-zinc-600 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-5"
                      ></div>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Footer buttons -->
              <div class="flex items-center justify-end gap-3 pt-6 mt-8 border-t border-zinc-800">
                <button
                  type="button"
                  @click="handleClose"
                  class="px-4 py-2 text-gray-300 transition-colors rounded-lg bg-zinc-800 hover:bg-zinc-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="px-4 py-2 text-white transition-all rounded-lg shadow-md bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 hover:shadow-lg active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
                  :disabled="isSubmitting"
                >
                  <span v-if="isSubmitting" class="flex items-center">
                    <svg
                      class="w-4 h-4 mr-2 animate-spin"
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
                    Saving...
                  </span>
                  <span v-else>Save Changes</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.modal-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
