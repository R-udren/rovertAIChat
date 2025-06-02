<script setup>
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { useUserSettingsStore } from '@/stores/userSettings'
import { profileSchema, validateField, validateForm } from '@/utils/validation'

const authStore = useAuthStore()
const userSettingsStore = useUserSettingsStore()
const toastStore = useToastStore()

const isEditing = ref(false)
const isSubmitting = ref(false)

const formData = ref({
  username: '',
  email: '',
  display_name: '',
  avatar_url: '',
})

const formErrors = ref({
  username: '',
  email: '',
  display_name: '',
  avatar_url: '',
})

// Track image load status to properly handle preview validation
const imageLoadStatus = ref({
  loaded: false,
  error: false,
})

// Add watchers for real-time validation
watch(
  () => formData.value.username,
  (newValue) => {
    const result = validateField(profileSchema, 'username', newValue, formData.value)
    formErrors.value.username = result.valid ? '' : result.message
  },
)

watch(
  () => formData.value.email,
  (newValue) => {
    const result = validateField(profileSchema, 'email', newValue, formData.value)
    formErrors.value.email = result.valid ? '' : result.message
  },
)

watch(
  () => formData.value.display_name,
  (newValue) => {
    const result = validateField(profileSchema, 'display_name', newValue, formData.value)
    formErrors.value.display_name = result.valid ? '' : result.message
  },
)

watch(
  () => formData.value.avatar_url,
  (newValue) => {
    if (newValue) {
      // Reset image status when URL changes
      imageLoadStatus.value = { loaded: false, error: false }

      // Only validate if not empty
      const result = validateField(profileSchema, 'avatar_url', newValue, formData.value)
      formErrors.value.avatar_url = result.valid ? '' : result.message
    } else {
      formErrors.value.avatar_url = ''
      imageLoadStatus.value = { loaded: false, error: false }
    }
  },
)

const validateProfileForm = () => {
  const result = validateForm(profileSchema, formData.value)
  if (!result.valid) {
    formErrors.value = result.errors
    return false
  }
  return true
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
    formData.value.display_name = userSettingsStore.settings?.display_name || ''
    formData.value.avatar_url = userSettingsStore.settings?.avatar_url || ''
  }
})

const startEditing = () => {
  isEditing.value = true
  formData.value.username = authStore.user?.username || ''
  formData.value.email = authStore.user?.email || ''
  formData.value.display_name = userSettingsStore.settings?.display_name || ''
  formData.value.avatar_url = userSettingsStore.settings?.avatar_url || ''

  // Reset image load status for the avatar preview
  if (formData.value.avatar_url) {
    imageLoadStatus.value = { loaded: false, error: false }
  }
}

const cancelEditing = () => {
  isEditing.value = false
}

const saveProfile = async () => {
  // Validate form before submission
  if (!validateProfileForm()) {
    toastStore.error('Please fix the form errors')
    return
  }

  isSubmitting.value = true

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
    if (
      formData.value.avatar_url !== userSettingsStore.settings?.avatar_url ||
      formData.value.display_name !== userSettingsStore.settings?.display_name
    ) {
      const settingsData = {
        avatar_url: formData.value.avatar_url,
        display_name: formData.value.display_name,
        // Preserve existing settings
        default_model_id: userSettingsStore.settings?.default_model_id,
        preferences: userSettingsStore.settings?.preferences,
      }

      await userSettingsStore.updateSettings(settingsData)
    }

    toastStore.success('Profile updated successfully')
    isEditing.value = false
  } catch (error) {
    toastStore.error('Failed to update profile: ' + error.message)
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
          class="px-4 py-2 font-medium text-white transition-colors duration-200 bg-indigo-600 rounded-md hover:bg-indigo-700"
        >
          Edit Profile
        </button>
      </div>

      <div v-if="authStore.loading" class="py-8 text-center">
        <div
          class="w-12 h-12 mx-auto border-t-2 border-indigo-500 border-solid rounded-full animate-spin"
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
              class="flex items-center justify-center w-24 h-24 overflow-hidden rounded-full bg-zinc-700"
            >
              <img
                :src="userSettingsStore.settings.avatar_url"
                :alt="`${authStore.user.username}'s avatar`"
                class="object-cover w-full h-full"
              />
            </div>
            <div
              v-else
              class="flex items-center justify-center w-24 h-24 text-3xl text-white rounded-full bg-zinc-700"
            >
              {{ authStore.user.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h2 class="max-w-md overflow-hidden text-3xl font-semibold text-white">
                {{ userSettingsStore.settings?.display_name || authStore.user.username }}
              </h2>
              <p class="text-gray-400">@{{ authStore.user.username }}</p>
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
              class="w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2"
              :class="[
                formErrors.username
                  ? 'border-red-500 bg-red-500/10 focus:ring-red-500'
                  : formData.username
                    ? 'border-green-500/50 bg-green-500/5 focus:ring-green-500'
                    : 'border-zinc-700 bg-zinc-900 focus:ring-indigo-500',
              ]"
              required
              minlength="4"
              maxlength="64"
            />
            <transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="-translate-y-1 opacity-0"
              enter-to-class="translate-y-0 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="translate-y-0 opacity-100"
              leave-to-class="-translate-y-1 opacity-0"
            >
              <p v-if="formErrors.username" class="flex items-center mt-1 text-sm text-red-400">
                <span class="mr-1">&#9888;</span> {{ formErrors.username }}
              </p>
            </transition>
          </div>

          <div>
            <label for="email" class="block mb-1 text-sm font-medium text-gray-300"> Email </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              class="w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2"
              :class="[
                formErrors.email
                  ? 'border-red-500 bg-red-500/10 focus:ring-red-500'
                  : formData.email
                    ? 'border-green-500/50 bg-green-500/5 focus:ring-green-500'
                    : 'border-zinc-700 bg-zinc-900 focus:ring-indigo-500',
              ]"
              required
            />
            <transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="-translate-y-1 opacity-0"
              enter-to-class="translate-y-0 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="translate-y-0 opacity-100"
              leave-to-class="-translate-y-1 opacity-0"
            >
              <p v-if="formErrors.email" class="flex items-center mt-1 text-sm text-red-400">
                <span class="mr-1">&#9888;</span> {{ formErrors.email }}
              </p>
            </transition>
          </div>

          <div>
            <label for="display_name" class="block mb-1 text-sm font-medium text-gray-300">
              Display Name <span class="text-gray-500">(optional)</span>
            </label>
            <input
              id="display_name"
              v-model="formData.display_name"
              type="text"
              class="w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2"
              :class="[
                formErrors.display_name
                  ? 'border-red-500 bg-red-500/10 focus:ring-red-500'
                  : formData.display_name
                    ? 'border-green-500/50 bg-green-500/5 focus:ring-green-500'
                    : 'border-zinc-700 bg-zinc-900 focus:ring-indigo-500',
              ]"
              maxlength="100"
            />
            <transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="-translate-y-1 opacity-0"
              enter-to-class="translate-y-0 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="translate-y-0 opacity-100"
              leave-to-class="-translate-y-1 opacity-0"
            >
              <p v-if="formErrors.display_name" class="flex items-center mt-1 text-sm text-red-400">
                <span class="mr-1">&#9888;</span> {{ formErrors.display_name }}
              </p>
            </transition>
            <p class="mt-1 text-xs text-gray-500">This is how your name will appear in chats</p>
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
              class="w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2"
              :class="[
                formErrors.avatar_url
                  ? 'border-red-500 bg-red-500/10 focus:ring-red-500'
                  : formData.avatar_url
                    ? 'border-green-500/50 bg-green-500/5 focus:ring-green-500/50'
                    : 'border-zinc-700 bg-zinc-900 focus:ring-indigo-500',
              ]"
            />
            <transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="-translate-y-1 opacity-0"
              enter-to-class="translate-y-0 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="translate-y-0 opacity-100"
              leave-to-class="-translate-y-1 opacity-0"
            >
              <p v-if="formErrors.avatar_url" class="flex items-center mt-1 text-sm text-red-400">
                <span class="mr-1">&#9888;</span> {{ formErrors.avatar_url }}
              </p>
            </transition>
            <div
              v-if="formData.avatar_url && !formErrors.avatar_url"
              class="flex items-start mt-3 space-x-2"
            >
              <span class="mt-1 text-sm text-gray-400">Preview:</span>
              <div class="relative">
                <img
                  :src="formData.avatar_url"
                  alt="Avatar preview"
                  class="object-cover w-16 h-16 rounded-full bg-zinc-700"
                  @load="imageLoadStatus = { loaded: true, error: false }"
                  @error="imageLoadStatus = { loaded: false, error: true }"
                  :class="{ 'border border-red-500': imageLoadStatus.error }"
                />
                <div
                  v-if="imageLoadStatus.loaded && !imageLoadStatus.error"
                  class="absolute flex items-center justify-center w-5 h-5 text-xs text-white bg-green-500 rounded-full -bottom-1 -right-1"
                >
                  ✓
                </div>
                <div
                  v-if="imageLoadStatus.error"
                  class="absolute flex items-center justify-center w-5 h-5 text-xs text-white bg-red-500 rounded-full -bottom-1 -right-1"
                >
                  !
                </div>
              </div>
              <div v-if="imageLoadStatus.error" class="mt-1 ml-1 text-sm text-red-400">
                Image could not be loaded
              </div>
            </div>
          </div>

          <div class="flex pt-2 space-x-4">
            <button
              type="submit"
              class="px-4 py-2 font-medium text-white transition-colors duration-200 bg-indigo-600 rounded-md hover:bg-indigo-700"
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
