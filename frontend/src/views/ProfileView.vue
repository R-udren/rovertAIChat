<script setup>
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useUserSettingsStore } from '@/stores/userSettings'
import { onMounted, ref } from 'vue'

const authStore = useAuthStore()
const userSettingsStore = useUserSettingsStore()

const isEditing = ref(false)
const updateStatus = ref('')
const isSubmitting = ref(false)

const formData = ref({
  username: '',
  email: '',
  avatar_url: '',
})

const formErrors = ref({
  username: '',
  email: '',
  avatar_url: '',
})

const validateForm = () => {
  let isValid = true
  formErrors.value = {
    username: '',
    email: '',
    avatar_url: '',
  }

  // Validate username (4-100 characters as per API schema)
  if (!formData.value.username) {
    formErrors.value.username = 'Username is required'
    isValid = false
  } else if (formData.value.username.length < 4) {
    formErrors.value.username = 'Username must be at least 4 characters'
    isValid = false
  } else if (formData.value.username.length > 100) {
    formErrors.value.username = 'Username cannot exceed 100 characters'
    isValid = false
  }

  // Validate email format
  if (!formData.value.email) {
    formErrors.value.email = 'Email is required'
    isValid = false
  } else {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailPattern.test(formData.value.email)) {
      formErrors.value.email = 'Please enter a valid email address'
      isValid = false
    }
  }

  // Validate avatar URL if provided
  if (formData.value.avatar_url) {
    // Basic URL validation
    try {
      new URL(formData.value.avatar_url)
    } catch (e) {
      formErrors.value.avatar_url = 'Please enter a valid URL'
      isValid = false
    }

    // Check max length (255 characters from schema)
    if (formData.value.avatar_url.length > 255) {
      formErrors.value.avatar_url = 'URL cannot exceed 255 characters'
      isValid = false
    }
  }

  return isValid
}

onMounted(async () => {
  // Refresh user profile data
  await authStore.fetchUserProfile()

  // Get user settings
  await userSettingsStore.fetchSettings()

  // Initialize form with current values
  if (authStore.user) {
    formData.value.username = authStore.user.username
    formData.value.email = authStore.user.email
    formData.value.avatar_url = userSettingsStore.settings?.avatar_url || ''
  }
})

const startEditing = () => {
  isEditing.value = true
  formData.value.username = authStore.user?.username || ''
  formData.value.email = authStore.user?.email || ''
  formData.value.avatar_url = userSettingsStore.settings?.avatar_url || ''
  updateStatus.value = ''
}

const cancelEditing = () => {
  isEditing.value = false
  updateStatus.value = ''
}

const saveProfile = async () => {
  // Validate form before submission
  if (!validateForm()) {
    updateStatus.value = 'Please fix the form errors'
    return
  }

  isSubmitting.value = true
  updateStatus.value = ''

  try {
    // Get user data to update
    const userUpdateData = {
      username: formData.value.username,
      email: formData.value.email,
    }

    // Call the API to update the user profile
    const updatedUser = await api.put('users/me', userUpdateData)

    // Update the user in the auth store
    authStore.user = updatedUser

    // Update localStorage to keep data in sync
    localStorage.setItem('user', JSON.stringify(updatedUser))

    // Update user settings with the avatar URL
    if (formData.value.avatar_url !== userSettingsStore.settings?.avatar_url) {
      const settingsData = {
        avatar_url: formData.value.avatar_url,
        // Preserve existing settings
        display_name: userSettingsStore.settings?.display_name,
        default_model_id: userSettingsStore.settings?.default_model_id,
        preferences: userSettingsStore.settings?.preferences,
      }

      await userSettingsStore.updateSettings(settingsData)
    }

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
  <div class="container max-w-2xl px-4 py-8 mx-auto">
    <div class="p-6 rounded-lg shadow-lg bg-zinc-800">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-white">Profile</h1>
        <button
          v-if="!isEditing"
          @click="startEditing"
          class="px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700"
        >
          Edit Profile
        </button>
      </div>

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

      <div v-if="authStore.loading" class="py-8 text-center">
        <div
          class="w-12 h-12 mx-auto border-t-2 border-solid rounded-full border-primary-500 animate-spin"
        ></div>
        <p class="mt-2 text-gray-400">Loading profile...</p>
      </div>

      <div v-else-if="!authStore.user" class="py-8 text-center">
        <p class="text-gray-400">Unable to load profile data</p>
      </div>

      <template v-else>
        <!-- View mode -->
        <div v-if="!isEditing" class="space-y-6">
          <div class="flex items-center space-x-4">
            <div
              v-if="userSettingsStore.settings?.avatar_url"
              class="flex items-center justify-center w-16 h-16 overflow-hidden rounded-full bg-zinc-700"
            >
              <img
                :src="userSettingsStore.settings.avatar_url"
                :alt="`${authStore.user.username}'s avatar`"
                class="object-cover w-full h-full"
              />
            </div>
            <div
              v-else
              class="flex items-center justify-center w-16 h-16 text-xl text-white rounded-full bg-zinc-700"
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

          <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <h3 class="mb-2 text-sm font-medium text-gray-500 uppercase">Username</h3>
              <p class="text-white">{{ authStore.user.username }}</p>
            </div>

            <div>
              <h3 class="mb-2 text-sm font-medium text-gray-500 uppercase">Email</h3>
              <p class="text-white">{{ authStore.user.email }}</p>
            </div>

            <div>
              <h3 class="mb-2 text-sm font-medium text-gray-500 uppercase">Role</h3>
              <p class="text-white capitalize">{{ authStore.user.role }}</p>
            </div>

            <div>
              <h3 class="mb-2 text-sm font-medium text-gray-500 uppercase">Registered On</h3>
              <p class="text-white">
                {{ new Date(authStore.user.created_at).toLocaleDateString() }}
              </p>
            </div>

            <div>
              <h3 class="mb-2 text-sm font-medium text-gray-500 uppercase">Last Login</h3>
              <p class="text-white">
                {{
                  authStore.user.last_login
                    ? new Date(authStore.user.last_login).toLocaleString()
                    : 'N/A'
                }}
              </p>
            </div>

            <div>
              <h3 class="mb-2 text-sm font-medium text-gray-500 uppercase">Account Status</h3>
              <p class="text-white">
                <span
                  class="inline-block px-2 py-1 text-sm border-2 border-green-500 rounded-xl"
                  :class="
                    authStore.user.is_active
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
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
            <label for="username" class="block mb-1 text-sm font-medium text-gray-300">
              Username
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
              minlength="4"
              maxlength="64"
            />
            <p v-if="formErrors.username" class="mt-1 text-sm text-red-400">
              {{ formErrors.username }}
            </p>
          </div>

          <div>
            <label for="email" class="block mb-1 text-sm font-medium text-gray-300"> Email </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
            <p v-if="formErrors.email" class="mt-1 text-sm text-red-400">
              {{ formErrors.email }}
            </p>
          </div>

          <div>
            <label for="avatar_url" class="block mb-1 text-sm font-medium text-gray-300">
              Profile Picture URL <span class="text-gray-500">(optional)</span>
            </label>
            <input
              id="avatar_url"
              v-model="formData.avatar_url"
              type="url"
              placeholder="https://example.com/avatar.jpg"
              class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <p v-if="formErrors.avatar_url" class="mt-1 text-sm text-red-400">
              {{ formErrors.avatar_url }}
            </p>
            <p v-if="formData.avatar_url" class="flex items-start mt-2 space-x-2">
              <span class="text-sm text-gray-400">Preview:</span>
              <img
                :src="formData.avatar_url"
                alt="Avatar preview"
                class="object-cover w-10 h-10 rounded-full bg-zinc-700"
                @error="(e) => e.target.classList.add('border', 'border-red-500')"
              />
            </p>
          </div>

          <div class="flex pt-2 space-x-4">
            <button
              type="submit"
              class="px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>

            <button
              type="button"
              @click="cancelEditing"
              class="px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-zinc-600 hover:bg-zinc-700"
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
