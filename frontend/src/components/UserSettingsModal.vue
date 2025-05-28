<script>
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'
import { reactive, ref, watch } from 'vue'

export default {
  name: 'UserSettingsModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false,
    },
    user: {
      type: Object,
      default: null,
    },
  },
  emits: ['close'],
  setup(props, { emit }) {
    const adminStore = useAdminStore()
    const toastStore = useToastStore()

    const loading = ref(false)
    const saving = ref(false)
    const settings = ref(null)

    const editableSettings = reactive({
      theme: 'light',
      language: 'en',
      default_model: '',
      messages_per_page: 20,
      auto_save_conversations: true,
      sound_notifications: true,
      data_collection_consent: false,
      email_notifications: true,
      api_timeout: 30,
      max_tokens: 2048,
    })

    const loadUserSettings = async () => {
      if (!props.user?.id) return

      loading.value = true
      try {
        const userSettings = await adminStore.getUserSettings(props.user.id)
        settings.value = userSettings

        // Update editable settings with loaded data
        if (userSettings) {
          Object.keys(editableSettings).forEach((key) => {
            if (userSettings[key] !== undefined) {
              editableSettings[key] = userSettings[key]
            }
          })
        }
      } catch (error) {
        toastStore.addToast('Failed to load user settings', 'error')
      } finally {
        loading.value = false
      }
    }

    const saveSettings = async () => {
      if (!props.user?.id) return

      saving.value = true
      try {
        await adminStore.updateUserSettings(props.user.id, editableSettings)
        toastStore.addToast('Settings updated successfully', 'success')
        settings.value = { ...settings.value, ...editableSettings }
      } catch (error) {
        toastStore.addToast('Failed to save settings', 'error')
      } finally {
        saving.value = false
      }
    }

    const resetSettings = () => {
      if (settings.value) {
        Object.keys(editableSettings).forEach((key) => {
          if (settings.value[key] !== undefined) {
            editableSettings[key] = settings.value[key]
          }
        })
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    }

    const closeModal = () => {
      emit('close')
    }

    watch(
      () => props.isOpen,
      (newValue) => {
        if (newValue && props.user) {
          loadUserSettings()
        }
      },
    )

    watch(
      () => props.user,
      () => {
        if (props.isOpen && props.user) {
          loadUserSettings()
        }
      },
    )

    return {
      loading,
      saving,
      settings,
      editableSettings,
      saveSettings,
      resetSettings,
      formatDate,
      closeModal,
    }
  },
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
  >
    <div class="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">User Settings - {{ user?.username }}</h3>
        <button @click="closeModal" class="text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <div v-if="loading" class="flex justify-center py-8">
        <div class="w-8 h-8 border-b-2 border-blue-600 rounded-full animate-spin"></div>
      </div>

      <div v-else-if="settings" class="space-y-6">
        <!-- Theme Settings -->
        <div class="pb-4 border-b">
          <h4 class="mb-3 font-medium text-gray-900 text-md">Theme Preferences</h4>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700">Theme</label>
              <select
                v-model="editableSettings.theme"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="auto">Auto</option>
              </select>
            </div>
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700">Language</label>
              <select
                v-model="editableSettings.language"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Chat Settings -->
        <div class="pb-4 border-b">
          <h4 class="mb-3 font-medium text-gray-900 text-md">Chat Preferences</h4>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700">Default Model</label>
              <input
                v-model="editableSettings.default_model"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., llama2, mistral"
              />
            </div>
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700">Messages per Page</label>
              <input
                v-model.number="editableSettings.messages_per_page"
                type="number"
                min="10"
                max="100"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div class="mt-4 space-y-3">
            <div class="flex items-center">
              <input
                id="auto_save"
                v-model="editableSettings.auto_save_conversations"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label for="auto_save" class="block ml-2 text-sm text-gray-700">
                Auto-save conversations
              </label>
            </div>
            <div class="flex items-center">
              <input
                id="sound_notifications"
                v-model="editableSettings.sound_notifications"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label for="sound_notifications" class="block ml-2 text-sm text-gray-700">
                Sound notifications
              </label>
            </div>
          </div>
        </div>

        <!-- Privacy Settings -->
        <div class="pb-4 border-b">
          <h4 class="mb-3 font-medium text-gray-900 text-md">Privacy & Security</h4>
          <div class="space-y-3">
            <div class="flex items-center">
              <input
                id="data_collection"
                v-model="editableSettings.data_collection_consent"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label for="data_collection" class="block ml-2 text-sm text-gray-700">
                Allow data collection for improving service
              </label>
            </div>
            <div class="flex items-center">
              <input
                id="email_notifications"
                v-model="editableSettings.email_notifications"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label for="email_notifications" class="block ml-2 text-sm text-gray-700">
                Email notifications
              </label>
            </div>
          </div>
        </div>

        <!-- API Settings -->
        <div class="pb-4 border-b">
          <h4 class="mb-3 font-medium text-gray-900 text-md">API Configuration</h4>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700"
                >API Timeout (seconds)</label
              >
              <input
                v-model.number="editableSettings.api_timeout"
                type="number"
                min="5"
                max="300"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700">Max Tokens</label>
              <input
                v-model.number="editableSettings.max_tokens"
                type="number"
                min="100"
                max="4096"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <!-- Account Information -->
        <div>
          <h4 class="mb-3 font-medium text-gray-900 text-md">Account Information</h4>
          <div class="p-4 space-y-2 rounded-md bg-gray-50">
            <div class="flex justify-between">
              <span class="text-sm font-medium text-gray-700">User ID:</span>
              <span class="text-sm text-gray-600">{{ user?.id }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm font-medium text-gray-700">Role:</span>
              <span class="text-sm text-gray-600 capitalize">{{ user?.role }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm font-medium text-gray-700">Status:</span>
              <span class="text-sm" :class="user?.is_active ? 'text-green-600' : 'text-red-600'">
                {{ user?.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm font-medium text-gray-700">Created:</span>
              <span class="text-sm text-gray-600">{{ formatDate(user?.created_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm font-medium text-gray-700">Last Updated:</span>
              <span class="text-sm text-gray-600">{{ formatDate(settings?.updated_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end pt-4 space-x-3 border-t">
          <button
            type="button"
            @click="resetSettings"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Reset
          </button>
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Close
          </button>
          <button
            @click="saveSettings"
            :disabled="saving"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>

      <div v-else class="py-8 text-center text-gray-500">No settings found for this user.</div>
    </div>
  </div>
</template>
