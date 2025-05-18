<script setup>
import { useUserSettingsStore } from '@/stores/userSettings'
import { onMounted, ref } from 'vue'

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
    // console.error(error)
    updateStatus.value = 'Failed to update settings: ' + (userSettingsStore.error || error.message)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container max-w-2xl px-4 py-8 mx-auto">
    <div class="p-6 rounded-lg shadow-lg bg-zinc-800">
      <h1 class="mb-6 text-2xl font-bold text-white">Settings</h1>

      <div
        v-if="updateStatus"
        class="p-3 mb-4 rounded-md"
        :class="
          updateStatus.includes('success')
            ? 'bg-green-500 bg-opacity-20 text-green-100'
            : 'bg-red-500 bg-opacity-20 text-red-100'
        "
      >
        {{ updateStatus }}
      </div>

      <div v-if="userSettingsStore.loading" class="py-8 text-center">
        <div
          class="w-12 h-12 mx-auto border-t-2 border-solid rounded-full border-primary-500 animate-spin"
        ></div>
        <p class="mt-2 text-gray-400">Loading settings...</p>
      </div>

      <form v-else @submit.prevent="saveSettings" class="space-y-6">
        <div>
          <h2 class="mb-4 text-xl font-medium text-white">Profile Settings</h2>

          <div class="space-y-4">
            <div>
              <label for="display_name" class="block mb-1 text-sm font-medium text-gray-300">
                Display Name
              </label>
              <input
                id="display_name"
                v-model="formData.display_name"
                type="text"
                class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                maxlength="100"
              />
              <p class="mt-1 text-xs text-gray-500">
                This is how your name will appear in chats (optional)
              </p>
            </div>

            <div>
              <label for="avatar_url" class="block mb-1 text-sm font-medium text-gray-300">
                Avatar URL
              </label>
              <input
                id="avatar_url"
                v-model="formData.avatar_url"
                type="text"
                class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                maxlength="255"
              />
              <p class="mt-1 text-xs text-gray-500">URL to your profile image (optional)</p>
            </div>
          </div>
        </div>

        <div>
          <h2 class="mb-4 text-xl font-medium text-white">AI Model Settings</h2>

          <div>
            <label for="default_model" class="block mb-1 text-sm font-medium text-gray-300">
              Default AI Model
            </label>
            <select
              id="default_model"
              v-model="formData.default_model_id"
              class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select a default model</option>
              <option value="MMMe6f1ae10-9b0e-4639-b4d9-daa82d125d4e">GPT-3.5</option>
              <option value="5429a4ed-8112-4abb-bbed-777fb83a2476">GPT-4</option>
              <option value="94b4848b-6176-41c6-8314-83a5297da424">Claude</option>
            </select>
            <p class="mt-1 text-xs text-gray-500">
              This model will be used by default for new conversations
            </p>
          </div>
        </div>

        <div>
          <h2 class="mb-4 text-xl font-medium text-white">App Preferences</h2>

          <div class="space-y-4">
            <div>
              <label for="theme" class="block mb-1 text-sm font-medium text-gray-300">
                Theme
              </label>
              <select
                id="theme"
                v-model="formData.preferences.theme"
                class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="system">System</option>
              </select>
            </div>

            <div>
              <label for="fontSize" class="block mb-1 text-sm font-medium text-gray-300">
                Font Size
              </label>
              <select
                id="fontSize"
                v-model="formData.preferences.fontSize"
                class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </div>

            <div>
              <label for="chatBubbleStyle" class="block mb-1 text-sm font-medium text-gray-300">
                Chat Bubble Style
              </label>
              <select
                id="chatBubbleStyle"
                v-model="formData.preferences.chatBubbleStyle"
                class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
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
                class="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-zinc-600 bg-zinc-900"
              />
              <label for="messageSound" class="block ml-2 text-sm text-gray-300">
                Play sound on message
              </label>
            </div>

            <div class="flex items-center">
              <input
                id="notifications"
                v-model="formData.preferences.notifications"
                type="checkbox"
                class="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-zinc-600 bg-zinc-900"
              />
              <label for="notifications" class="block ml-2 text-sm text-gray-300">
                Enable browser notifications
              </label>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
