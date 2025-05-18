<script setup>
import { useUserSettingsStore } from '@/stores/userSettings'
import { userSettingsSchema, validateField, validateForm } from '@/utils/validation'
import { onMounted, ref, watch } from 'vue'

const userSettingsStore = useUserSettingsStore()

const updateStatus = ref('')
const isSubmitting = ref(false)
const formValid = ref(false)

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

const formErrors = ref({
  display_name: '',
  avatar_url: '',
  default_model_id: '',
})

// Image preview state
const imageLoadStatus = ref({
  loaded: false,
  error: false,
  loading: false,
})

// Add watchers for real-time validation
watch(
  () => formData.value.display_name,
  (newValue) => {
    const result = validateField(userSettingsSchema, 'display_name', newValue)
    formErrors.value.display_name = result.valid ? '' : result.message
    validateFormData()
  },
)

watch(
  () => formData.value.avatar_url,
  (newValue) => {
    const result = validateField(userSettingsSchema, 'avatar_url', newValue)
    formErrors.value.avatar_url = result.valid ? '' : result.message

    if (newValue) {
      imageLoadStatus.value.loading = true
      imageLoadStatus.value.loaded = false
      imageLoadStatus.value.error = false
    } else {
      imageLoadStatus.value.loading = false
      imageLoadStatus.value.loaded = false
      imageLoadStatus.value.error = false
    }

    validateFormData()
  },
)

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
      display_name: formData.value.display_name || null,
      avatar_url: formData.value.avatar_url || null,
      default_model_id: formData.value.default_model_id || null,
      preferences: formData.value.preferences || null,
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
                :class="[
                  'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500',
                  formErrors.display_name
                    ? 'border-red-500 bg-red-500/10'
                    : formData.display_name
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-zinc-700 bg-zinc-900',
                ]"
                maxlength="100"
              />
              <p
                v-if="formErrors.display_name"
                class="mt-1 text-xs text-red-400 transition-opacity"
              >
                {{ formErrors.display_name }}
              </p>
              <p v-else class="mt-1 text-xs text-gray-500">
                This is how your name will appear in chats (optional)
              </p>
            </div>

            <div>
              <label for="avatar_url" class="block mb-1 text-sm font-medium text-gray-300">
                Avatar URL
              </label>
              <div class="flex space-x-4">
                <div class="flex-1">
                  <input
                    id="avatar_url"
                    v-model="formData.avatar_url"
                    type="text"
                    :class="[
                      'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500',
                      formErrors.avatar_url
                        ? 'border-red-500 bg-red-500/10'
                        : formData.avatar_url && imageLoadStatus.loaded
                          ? 'border-green-500 bg-green-500/10'
                          : 'border-zinc-700 bg-zinc-900',
                    ]"
                    maxlength="255"
                  />
                </div>

                <!-- Avatar preview -->
                <div
                  v-if="formData.avatar_url"
                  class="relative w-12 h-12 overflow-hidden rounded-full"
                >
                  <div
                    v-if="
                      imageLoadStatus.loading && !imageLoadStatus.loaded && !imageLoadStatus.error
                    "
                    class="absolute inset-0 flex items-center justify-center bg-zinc-800"
                  >
                    <div
                      class="w-6 h-6 border-t-2 border-solid rounded-full border-primary-500 animate-spin"
                    ></div>
                  </div>
                  <div
                    v-if="imageLoadStatus.error"
                    class="absolute inset-0 flex items-center justify-center text-red-500 bg-red-500/10"
                  >
                    <span class="text-lg">❌</span>
                  </div>
                  <img
                    v-show="!imageLoadStatus.error"
                    :src="formData.avatar_url"
                    @load="imageLoadStatus = { loaded: true, error: false, loading: false }"
                    @error="imageLoadStatus = { loaded: false, error: true, loading: false }"
                    class="object-cover w-full h-full"
                  />
                </div>
                <div
                  v-else
                  class="flex items-center justify-center w-12 h-12 rounded-full bg-primary-600"
                >
                  <span class="text-xl font-medium text-white">
                    {{ formData.display_name ? formData.display_name[0].toUpperCase() : 'U' }}
                  </span>
                </div>
              </div>
              <p v-if="formErrors.avatar_url" class="mt-1 text-xs text-red-400 transition-opacity">
                {{ formErrors.avatar_url }}
              </p>
              <p v-else-if="imageLoadStatus.error" class="mt-1 text-xs text-red-400">
                Unable to load image from URL
              </p>
              <p v-else class="mt-1 text-xs text-gray-500">URL to your profile image (optional)</p>
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
