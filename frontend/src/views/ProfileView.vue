<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUserSettingsStore } from '@/stores/userSettings'

const authStore = useAuthStore()
const userSettingsStore = useUserSettingsStore()

const isEditing = ref(false)
const updateStatus = ref('')
const isSubmitting = ref(false)

const formData = ref({
  username: '',
  email: '',
})

onMounted(async () => {
  // Refresh user profile data
  await authStore.fetchUserProfile()

  // Get user settings
  await userSettingsStore.fetchSettings()

  // Initialize form with current values
  if (authStore.user) {
    formData.value.username = authStore.user.username
    formData.value.email = authStore.user.email
  }
})

const startEditing = () => {
  isEditing.value = true
  formData.value.username = authStore.user?.username || ''
  formData.value.email = authStore.user?.email || ''
  updateStatus.value = ''
}

const cancelEditing = () => {
  isEditing.value = false
  updateStatus.value = ''
}

const saveProfile = async () => {
  isSubmitting.value = true
  updateStatus.value = ''

  try {
    // In a real app, you would call an update profile API here
    // For now, just simulate a delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    updateStatus.value = 'Profile updated successfully'
    isEditing.value = false
  } catch (error) {
    updateStatus.value = 'Failed to update profile: ' + error.message
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <div class="bg-zinc-800 rounded-lg shadow-lg p-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-white">Profile</h1>
        <button
          v-if="!isEditing"
          @click="startEditing"
          class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
        >
          Edit Profile
        </button>
      </div>

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

      <div v-if="authStore.loading" class="text-center py-8">
        <div
          class="w-12 h-12 border-t-2 border-primary-500 border-solid rounded-full animate-spin mx-auto"
        ></div>
        <p class="text-gray-400 mt-2">Loading profile...</p>
      </div>

      <div v-else-if="!authStore.user" class="text-center py-8">
        <p class="text-gray-400">Unable to load profile data</p>
      </div>

      <template v-else>
        <!-- View mode -->
        <div v-if="!isEditing" class="space-y-6">
          <div class="flex items-center space-x-4">
            <div
              class="w-16 h-16 rounded-full bg-zinc-700 flex items-center justify-center text-xl text-white"
            >
              {{ authStore.user.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h2 class="text-xl font-medium text-white">{{ authStore.user.username }}</h2>
              <p class="text-gray-400">
                {{ userSettingsStore.settings?.display_name || 'No display name set' }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Username</h3>
              <p class="text-white">{{ authStore.user.username }}</p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Email</h3>
              <p class="text-white">{{ authStore.user.email }}</p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Role</h3>
              <p class="text-white capitalize">{{ authStore.user.role }}</p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Registered On</h3>
              <p class="text-white">
                {{ new Date(authStore.user.created_at).toLocaleDateString() }}
              </p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Last Login</h3>
              <p class="text-white">
                {{
                  authStore.user.last_login
                    ? new Date(authStore.user.last_login).toLocaleString()
                    : 'N/A'
                }}
              </p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Account Status</h3>
              <p class="text-white">
                <span
                  class="inline-block px-2 py-1 rounded-full text-xs"
                  :class="
                    authStore.user.is_active
                      ? 'bg-green-500 bg-opacity-30 text-green-200'
                      : 'bg-red-500 bg-opacity-30 text-red-200'
                  "
                >
                  {{ authStore.user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <!-- Edit mode -->
        <form v-else @submit.prevent="saveProfile" class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-300 mb-1">
              Username
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
              minlength="4"
              maxlength="64"
            />
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-300 mb-1"> Email </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div class="flex space-x-4 pt-2">
            <button
              type="submit"
              class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>

            <button
              type="button"
              @click="cancelEditing"
              class="bg-zinc-600 hover:bg-zinc-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
              :disabled="isSubmitting"
            >
              Cancel
            </button>
          </div>
        </form>
      </template>
    </div>
  </div>
</template>
