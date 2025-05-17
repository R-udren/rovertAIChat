<script setup>
import { ref, onMounted } from 'vue'
import { useUserSettingsStore } from '@/stores/userSettings'

const userSettingsStore = useUserSettingsStore()

const updateStatus = ref('')
const isSubmitting = ref(false)

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

onMounted(async () => {
  // Get user settings
  await userSettingsStore.fetchSettings()

  // Initialize form with current values
  if (userSettingsStore.settings) {
    formData.value.display_name = userSettingsStore.settings.display_name || ''
    formData.value.avatar_url = userSettingsStore.settings.avatar_url || ''
    formData.value.default_model_id = userSettingsStore.settings.default_model_id || ''
    formData.value.preferences = userSettingsStore.settings.preferences || {
      theme: 'dark',
      fontSize: 'medium',
      chatBubbleStyle: 'rounded',
      messageSound: true,
      notifications: true,
    }
  }
})

const saveSettings = async () => {
  isSubmitting.value = true
  updateStatus.value = ''

  try {
    await userSettingsStore.updateSettings({
      display_name: formData.value.display_name,
      avatar_url: formData.value.avatar_url,
      default_model_id: formData.value.default_model_id,
      preferences: formData.value.preferences,
    })

    updateStatus.value = 'Settings updated successfully'
  } catch (error) {
    updateStatus.value = 'Failed to update settings: ' + (userSettingsStore.error || error.message)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <div class="bg-zinc-800 rounded-lg shadow-lg p-6">
      <h1 class="text-2xl font-bold text-white mb-6">Settings</h1>

      <div
        v-if="updateStatus"
        class="mb-4 p-3 rounded-md"
        :class="
          updateStatus.includes('success')
            ? 'bg-green-500 bg-opacity-20 text-green-100'
            : 'bg-red-500 bg-opacity-20 text-red-100'
        "
      >
        {{ updateStatus }}
      </div>

      <div v-if="userSettingsStore.loading" class="text-center py-8">
        <div
          class="w-12 h-12 border-t-2 border-primary-500 border-solid rounded-full animate-spin mx-auto"
        ></div>
        <p class="text-gray-400 mt-2">Loading settings...</p>
      </div>

      <form v-else @submit.prevent="saveSettings" class="space-y-6">
        <div>
          <h2 class="text-xl font-medium text-white mb-4">Profile Settings</h2>

          <div class="space-y-4">
            <div>
              <label for="display_name" class="block text-sm font-medium text-gray-300 mb-1">
                Display Name
              </label>
              <input
                id="display_name"
                v-model="formData.display_name"
                type="text"
                class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                maxlength="100"
              />
              <p class="text-xs text-gray-500 mt-1">
                This is how your name will appear in chats (optional)
              </p>
            </div>

            <div>
              <label for="avatar_url" class="block text-sm font-medium text-gray-300 mb-1">
                Avatar URL
              </label>
              <input
                id="avatar_url"
                v-model="formData.avatar_url"
                type="text"
                class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                maxlength="255"
              />
              <p class="text-xs text-gray-500 mt-1">URL to your profile image (optional)</p>
            </div>
          </div>
        </div>

        <div>
          <h2 class="text-xl font-medium text-white mb-4">AI Model Settings</h2>

          <div>
            <label for="default_model" class="block text-sm font-medium text-gray-300 mb-1">
              Default AI Model
            </label>
            <select
              id="default_model"
              v-model="formData.default_model_id"
              class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select a default model</option>
              <option value="model-1">GPT-3.5</option>
              <option value="model-2">GPT-4</option>
              <option value="model-3">Claude</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">
              This model will be used by default for new conversations
            </p>
          </div>
        </div>

        <div>
          <h2 class="text-xl font-medium text-white mb-4">App Preferences</h2>

          <div class="space-y-4">
            <div>
              <label for="theme" class="block text-sm font-medium text-gray-300 mb-1">
                Theme
              </label>
              <select
                id="theme"
                v-model="formData.preferences.theme"
                class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="system">System</option>
              </select>
            </div>

            <div>
              <label for="fontSize" class="block text-sm font-medium text-gray-300 mb-1">
                Font Size
              </label>
              <select
                id="fontSize"
                v-model="formData.preferences.fontSize"
                class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </div>

            <div>
              <label for="chatBubbleStyle" class="block text-sm font-medium text-gray-300 mb-1">
                Chat Bubble Style
              </label>
              <select
                id="chatBubbleStyle"
                v-model="formData.preferences.chatBubbleStyle"
                class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="rounded">Rounded</option>
                <option value="square">Square</option>
                <option value="modern">Modern</option>
              </select>
            </div>

            <div class="flex items-center">
              <input
                id="messageSound"
                v-model="formData.preferences.messageSound"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-zinc-600 rounded bg-zinc-900"
              />
              <label for="messageSound" class="ml-2 block text-sm text-gray-300">
                Play sound on message
              </label>
            </div>

            <div class="flex items-center">
              <input
                id="notifications"
                v-model="formData.preferences.notifications"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-zinc-600 rounded bg-zinc-900"
              />
              <label for="notifications" class="ml-2 block text-sm text-gray-300">
                Enable browser notifications
              </label>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
