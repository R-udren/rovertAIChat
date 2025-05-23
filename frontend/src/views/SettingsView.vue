<script setup>
import { useUserSettingsStore } from '@/stores/userSettings'
import { userSettingsSchema, validateForm } from '@/utils/validation'
import { onMounted, ref } from 'vue'

const userSettingsStore = useUserSettingsStore()

const updateStatus = ref('')
const isSubmitting = ref(false)
const formValid = ref(false)

const formData = ref({
  default_model_id: '',
  preferences: {
    theme: 'dark',
    fontSize: 'medium',
    chatBubbleStyle: 'rounded',
    messageSound: true,
    notifications: true,
    streamingEnabled: true,
  },
})

// Add watchers for real-time validation

onMounted(async () => {
  // Get user settings
  await userSettingsStore.fetchSettings()

  // Initialize form with current values
  if (userSettingsStore.settings) {
    formData.value.default_model_id = userSettingsStore.settings.default_model_id || ''
    formData.value.preferences = userSettingsStore.settings.preferences || {
      theme: 'dark',
      fontSize: 'medium',
      chatBubbleStyle: 'rounded',
      messageSound: true,
      notifications: true,
      streamingEnabled: true,
    }
  }

  // Validate form after initialization
  validateFormData()
})

// Validate the entire form
const validateFormData = () => {
  const result = validateForm(userSettingsSchema, formData.value)
  formValid.value = result.valid
  return result
}

const saveSettings = async () => {
  // Validate form before submitting
  const validation = validateFormData()

  if (!validation.valid) {
    // Show the first error message
    const firstErrorField = Object.keys(validation.errors)[0]
    updateStatus.value = `Error: ${validation.errors[firstErrorField]}`
    return
  }

  isSubmitting.value = true
  updateStatus.value = ''

  try {
    await userSettingsStore.updateSettings({
      default_model_id: formData.value.default_model_id || null,
      preferences: formData.value.preferences || null,
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
                Theme (Coming soon)
              </label>
              <select
                id="theme"
                v-model="formData.preferences.theme"
                class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="system">System</option>
              </select>
              <p class="mt-1 text-xs text-gray-500">This feature will be available soon</p>
            </div>

            <div>
              <label for="fontSize" class="block mb-1 text-sm font-medium text-gray-300">
                Font Size (Coming soon)
              </label>
              <select
                id="fontSize"
                v-model="formData.preferences.fontSize"
                class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
              <p class="mt-1 text-xs text-gray-500">This feature will be available soon</p>
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
                disabled
                id="messageSound"
                v-model="formData.preferences.messageSound"
                type="checkbox"
                class="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-zinc-600 bg-zinc-900"
              />
              <label for="messageSound" class="block ml-2 text-sm text-gray-300">
                Play sound on message
              </label>
              <span class="ml-2 text-xs text-gray-500">(Not implemented yet)</span>
            </div>

            <div class="flex items-center">
              <input
                disabled
                id="notifications"
                v-model="formData.preferences.notifications"
                type="checkbox"
                class="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-zinc-600 bg-zinc-900"
              />
              <label for="notifications" class="block ml-2 text-sm text-gray-300">
                Enable browser notifications
              </label>
              <span class="ml-2 text-xs text-gray-500">(Not implemented yet)</span>
            </div>

            <div class="flex items-center">
              <input
                disabled
                id="streamingEnabled"
                v-model="formData.preferences.streamingEnabled"
                type="checkbox"
                class="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-zinc-600 bg-zinc-900"
              />
              <label for="streamingEnabled" class="block ml-2 text-sm text-gray-300">
                Enable streaming responses
              </label>
              <span class="ml-2 text-xs text-gray-500">(Not implemented yet)</span>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isSubmitting || !formValid"
          >
            {{ isSubmitting ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
