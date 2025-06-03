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

// Computed properties for enhanced display
const userInitials = computed(() => {
  if (userSettingsStore.settings?.display_name) {
    return userSettingsStore.settings.display_name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }
  return authStore.user?.username?.charAt(0).toUpperCase() || '?'
})

const displayName = computed(() => {
  return userSettingsStore.settings?.display_name || authStore.user?.username || 'User'
})

const memberSince = computed(() => {
  if (!authStore.user?.created_at) return 'Unknown'
  const date = new Date(authStore.user.created_at)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
})

const lastSeenFormatted = computed(() => {
  if (!authStore.user?.last_login) return 'Never'
  const date = new Date(authStore.user.last_login)
  const now = new Date()
  const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))

  if (diffInHours < 1) return 'Just now'
  if (diffInHours < 24) return `${diffInHours} hours ago`
  if (diffInHours < 168) return `${Math.floor(diffInHours / 24)} days ago`
  return date.toLocaleDateString()
})

const accountAge = computed(() => {
  if (!authStore.user?.created_at) return '0 days'
  const created = new Date(authStore.user.created_at)
  const now = new Date()
  const diffInDays = Math.floor((now - created) / (1000 * 60 * 60 * 24))

  if (diffInDays < 7) return `${diffInDays} days`
  if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks`
  if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months`
  return `${Math.floor(diffInDays / 365)} years`
})

const roleColor = computed(() => {
  const role = authStore.user?.role
  switch (role) {
    case 'admin':
      return 'from-red-500 to-pink-500'
    case 'moderator':
      return 'from-purple-500 to-indigo-500'
    case 'premium':
      return 'from-yellow-500 to-orange-500'
    default:
      return 'from-blue-500 to-cyan-500'
  }
})

const roleIcon = computed(() => {
  const role = authStore.user?.role
  switch (role) {
    case 'admin':
      return '👑'
    default:
      return '👤'
  }
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
  <div
    class="min-h-[calc(100vh-64px)] bg-gradient-to-br from-zinc-900 via-purple-900/20 to-zinc-900"
  >
    <div class="container relative z-10 max-w-6xl px-4 py-8 mx-auto">
      <!-- Loading State -->
      <div v-if="authStore.loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="flex flex-col items-center justify-center">
          <div class="relative flex">
            <div class="w-20 h-20 border-4 rounded-full border-purple-500/30 animate-spin"></div>
            <div
              class="absolute top-0 left-0 w-20 h-20 border-4 border-purple-500 rounded-full border-t-transparent animate-spin"
              style="animation-direction: reverse; animation-duration: 1.5s"
            ></div>
          </div>
          <p class="mt-4 text-lg text-gray-300 animate-pulse">Loading your profile...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="!authStore.user" class="flex items-center justify-center min-h-[60vh]">
        <div
          class="p-8 text-center border bg-red-500/10 border-red-500/30 rounded-2xl backdrop-blur-sm"
        >
          <div class="mb-4 text-6xl">😕</div>
          <h2 class="mb-2 text-2xl font-bold text-red-400">Oops!</h2>
          <p class="text-gray-300">Unable to load your profile data</p>
        </div>
      </div>

      <!-- Main Profile Content -->
      <template v-else>
        <!-- Header with Edit Button -->
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center space-x-4">
            <div class="w-2 h-12 rounded-full bg-gradient-to-b from-purple-500 to-blue-500"></div>
            <h1
              class="text-4xl font-bold text-transparent bg-gradient-to-r from-white via-purple-200 to-gray-300 bg-clip-text"
            >
              Your Profile
            </h1>
          </div>
          <button
            v-if="!isEditing"
            @click="startEditing"
            class="relative px-6 py-3 font-semibold text-white transition-all duration-300 group bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl hover:shadow-2xl hover:shadow-purple-500/25 hover:scale-105 active:scale-95"
          >
            <span
              class="absolute inset-0 transition-opacity duration-300 opacity-0 bg-gradient-to-r from-purple-700 to-blue-700 rounded-xl blur group-hover:opacity-100"
            ></span>
            <span class="relative flex items-center space-x-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                ></path>
              </svg>
              <span>Edit Profile</span>
            </span>
          </button>
        </div>

        <!-- View Mode -->
        <div v-if="!isEditing" class="space-y-8">
          <!-- Hero Profile Card -->
          <div
            class="relative p-8 overflow-hidden border shadow-2xl bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border-slate-700/50 rounded-3xl"
          >
            <!-- Decorative elements -->
            <div
              class="absolute top-0 right-0 w-32 h-32 rounded-full bg-gradient-to-bl from-purple-500/20 to-transparent blur-2xl"
            ></div>
            <div
              class="absolute bottom-0 left-0 w-24 h-24 rounded-full bg-gradient-to-tr from-blue-500/20 to-transparent blur-xl"
            ></div>

            <div
              class="relative flex flex-col items-start space-y-6 lg:flex-row lg:items-center lg:space-y-0 lg:space-x-8"
            >
              <!-- Avatar Section -->
              <div class="relative group">
                <div class="relative">
                  <!-- Avatar Ring -->
                  <div
                    class="absolute transition-opacity duration-500 rounded-full -inset-4 bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500 blur-lg opacity-60 group-hover:opacity-80"
                  ></div>
                  <div
                    class="absolute rounded-full -inset-2 bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500 opacity-80"
                  ></div>

                  <!-- Avatar Image/Initials -->
                  <div
                    class="relative w-32 h-32 overflow-hidden border-4 rounded-full bg-slate-700 border-slate-800"
                  >
                    <img
                      v-if="userSettingsStore.settings?.avatar_url"
                      :src="userSettingsStore.settings.avatar_url"
                      :alt="`${displayName}'s avatar`"
                      class="object-cover w-full h-full transition-transform duration-300 group-hover:scale-110"
                    />
                    <div
                      v-else
                      class="flex items-center justify-center w-full h-full text-4xl font-bold text-white bg-gradient-to-br from-slate-600 to-slate-700"
                    >
                      {{ userInitials }}
                    </div>
                  </div>

                  <!-- Status Indicator -->
                  <div
                    class="absolute w-6 h-6 bg-green-500 border-4 rounded-full bottom-2 right-2 border-slate-800"
                  ></div>
                </div>
              </div>

              <!-- User Info -->
              <div class="flex-1 space-y-4">
                <div>
                  <h2
                    class="mb-2 text-4xl font-bold text-transparent bg-gradient-to-r from-white via-purple-200 to-gray-300 bg-clip-text"
                  >
                    {{ displayName }}
                  </h2>
                  <div class="flex items-center space-x-3">
                    <p class="text-xl text-gray-400">@{{ authStore.user.username }}</p>
                    <div
                      :class="`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-gradient-to-r ${roleColor} text-white shadow-lg`"
                    >
                      <span class="mr-1">{{ roleIcon }}</span>
                      {{
                        authStore.user.role.charAt(0).toUpperCase() + authStore.user.role.slice(1)
                      }}
                    </div>
                  </div>
                </div>

                <!-- Quick Stats -->
                <div class="grid grid-cols-2 gap-4 lg:grid-cols-3">
                  <div
                    class="p-4 border bg-slate-800/50 backdrop-blur-sm rounded-xl border-slate-700/30"
                  >
                    <div class="text-2xl font-bold text-purple-400">{{ accountAge }}</div>
                    <div class="text-sm text-gray-500">Member for</div>
                  </div>
                  <div
                    class="p-4 border bg-slate-800/50 backdrop-blur-sm rounded-xl border-slate-700/30"
                  >
                    <div class="text-2xl font-bold text-blue-400">{{ lastSeenFormatted }}</div>
                    <div class="text-sm text-gray-500">Last seen</div>
                  </div>
                  <div
                    class="col-span-2 p-4 border bg-slate-800/50 backdrop-blur-sm rounded-xl border-slate-700/30 lg:col-span-1"
                  >
                    <div class="flex items-center space-x-2">
                      <div
                        :class="`w-3 h-3 rounded-full ${authStore.user.is_active ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`"
                      ></div>
                      <span
                        class="text-2xl font-bold"
                        :class="authStore.user.is_active ? 'text-green-400' : 'text-red-400'"
                      >
                        {{ authStore.user.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </div>
                    <div class="text-sm text-gray-500">Status</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Detailed Information Cards -->
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <!-- Account Details -->
            <div
              class="p-6 transition-all duration-300 border shadow-xl bg-slate-800/60 backdrop-blur-xl border-slate-700/50 rounded-2xl hover:shadow-2xl hover:border-purple-500/30"
            >
              <div class="flex items-center mb-6 space-x-3">
                <div
                  class="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500"
                >
                  <svg
                    class="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    ></path>
                  </svg>
                </div>
                <h3 class="text-xl font-semibold text-white">Account Details</h3>
              </div>

              <div class="space-y-4">
                <div class="group">
                  <label class="block mb-1 text-sm font-medium text-gray-400">Username</label>
                  <div
                    class="p-3 transition-colors border rounded-lg bg-slate-700/30 border-slate-600/50 group-hover:border-purple-500/30"
                  >
                    <p class="font-medium text-white">{{ authStore.user.username }}</p>
                  </div>
                </div>

                <div class="group">
                  <label class="block mb-1 text-sm font-medium text-gray-400">Email Address</label>
                  <div
                    class="p-3 transition-colors border rounded-lg bg-slate-700/30 border-slate-600/50 group-hover:border-purple-500/30"
                  >
                    <p class="font-medium text-white">{{ authStore.user.email }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Account Statistics -->
            <div
              class="p-6 transition-all duration-300 border shadow-xl bg-slate-800/60 backdrop-blur-xl border-slate-700/50 rounded-2xl hover:shadow-2xl hover:border-blue-500/30"
            >
              <div class="flex items-center mb-6 space-x-3">
                <div
                  class="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500"
                >
                  <svg
                    class="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    ></path>
                  </svg>
                </div>
                <h3 class="text-xl font-semibold text-white">Account Statistics</h3>
              </div>

              <div class="space-y-4">
                <div class="group">
                  <label class="block mb-1 text-sm font-medium text-gray-400">Member Since</label>
                  <div
                    class="p-3 transition-colors border rounded-lg bg-slate-700/30 border-slate-600/50 group-hover:border-blue-500/30"
                  >
                    <p class="font-medium text-white">{{ memberSince }}</p>
                  </div>
                </div>

                <div class="group">
                  <label class="block mb-1 text-sm font-medium text-gray-400">Last Login</label>
                  <div
                    class="p-3 transition-colors border rounded-lg bg-slate-700/30 border-slate-600/50 group-hover:border-blue-500/30"
                  >
                    <p class="font-medium text-white">
                      {{
                        authStore.user.last_login
                          ? new Date(authStore.user.last_login).toLocaleString()
                          : 'Never'
                      }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Edit Mode -->
        <div v-else class="space-y-8">
          <!-- Edit Form Container -->
          <div
            class="relative overflow-hidden border shadow-2xl bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border-slate-700/50 rounded-3xl"
          >
            <!-- Decorative background -->
            <div
              class="absolute top-0 right-0 w-40 h-40 rounded-full bg-gradient-to-bl from-purple-500/10 to-transparent blur-3xl"
            ></div>
            <div
              class="absolute bottom-0 left-0 w-32 h-32 rounded-full bg-gradient-to-tr from-blue-500/10 to-transparent blur-2xl"
            ></div>

            <div class="relative p-8">
              <!-- Form Header -->
              <div class="flex items-center mb-8 space-x-4">
                <div
                  class="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl"
                >
                  <svg
                    class="text-white w-7 h-7"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    ></path>
                  </svg>
                </div>
                <div>
                  <h2 class="text-3xl font-bold text-white">Edit Profile</h2>
                  <p class="text-gray-400">Update your profile information</p>
                </div>
              </div>

              <!-- Edit Form -->
              <form @submit.prevent="saveProfile" class="grid grid-cols-1 gap-8 lg:grid-cols-2">
                <!-- Left Column -->
                <div class="space-y-6">
                  <!-- Username Field -->
                  <div class="group">
                    <label for="username" class="block mb-3 text-sm font-semibold text-gray-300">
                      <span class="flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                          ></path>
                        </svg>
                        <span>Username</span>
                      </span>
                    </label>
                    <div class="relative">
                      <input
                        id="username"
                        v-model="formData.username"
                        type="text"
                        class="w-full px-4 py-4 text-white placeholder-gray-500 transition-all duration-300 border-2 bg-slate-700/50 rounded-xl focus:outline-none focus:ring-4"
                        :class="[
                          formErrors.username
                            ? 'border-red-500/70 bg-red-500/10 focus:ring-red-500/20 focus:border-red-400'
                            : formData.username
                              ? 'border-green-500/70 bg-green-500/10 focus:ring-green-500/20 focus:border-green-400'
                              : 'border-slate-600/50 focus:ring-purple-500/20 focus:border-purple-400',
                        ]"
                        required
                        minlength="4"
                        maxlength="64"
                        placeholder="Enter your username"
                      />
                      <div
                        v-if="formData.username && !formErrors.username"
                        class="absolute transform -translate-y-1/2 right-3 top-1/2"
                      >
                        <div
                          class="flex items-center justify-center w-6 h-6 bg-green-500 rounded-full"
                        >
                          <svg
                            class="w-4 h-4 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M5 13l4 4L19 7"
                            ></path>
                          </svg>
                        </div>
                      </div>
                    </div>
                    <transition
                      enter-active-class="transition duration-300 ease-out"
                      enter-from-class="transform -translate-y-2 opacity-0"
                      enter-to-class="transform translate-y-0 opacity-100"
                      leave-active-class="transition duration-200 ease-in"
                      leave-from-class="transform translate-y-0 opacity-100"
                      leave-to-class="transform -translate-y-2 opacity-0"
                    >
                      <div
                        v-if="formErrors.username"
                        class="p-3 mt-3 border rounded-lg bg-red-500/10 border-red-500/30"
                      >
                        <p class="flex items-center text-sm text-red-400">
                          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fill-rule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                              clip-rule="evenodd"
                            ></path>
                          </svg>
                          {{ formErrors.username }}
                        </p>
                      </div>
                    </transition>
                  </div>

                  <!-- Email Field -->
                  <div class="group">
                    <label for="email" class="block mb-3 text-sm font-semibold text-gray-300">
                      <span class="flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                          ></path>
                        </svg>
                        <span>Email Address</span>
                      </span>
                    </label>
                    <div class="relative">
                      <input
                        id="email"
                        v-model="formData.email"
                        type="email"
                        class="w-full px-4 py-4 text-white placeholder-gray-500 transition-all duration-300 border-2 bg-slate-700/50 rounded-xl focus:outline-none focus:ring-4"
                        :class="[
                          formErrors.email
                            ? 'border-red-500/70 bg-red-500/10 focus:ring-red-500/20 focus:border-red-400'
                            : formData.email
                              ? 'border-green-500/70 bg-green-500/10 focus:ring-green-500/20 focus:border-green-400'
                              : 'border-slate-600/50 focus:ring-purple-500/20 focus:border-purple-400',
                        ]"
                        required
                        placeholder="Enter your email address"
                      />
                      <div
                        v-if="formData.email && !formErrors.email"
                        class="absolute transform -translate-y-1/2 right-3 top-1/2"
                      >
                        <div
                          class="flex items-center justify-center w-6 h-6 bg-green-500 rounded-full"
                        >
                          <svg
                            class="w-4 h-4 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M5 13l4 4L19 7"
                            ></path>
                          </svg>
                        </div>
                      </div>
                    </div>
                    <transition
                      enter-active-class="transition duration-300 ease-out"
                      enter-from-class="transform -translate-y-2 opacity-0"
                      enter-to-class="transform translate-y-0 opacity-100"
                      leave-active-class="transition duration-200 ease-in"
                      leave-from-class="transform translate-y-0 opacity-100"
                      leave-to-class="transform -translate-y-2 opacity-0"
                    >
                      <div
                        v-if="formErrors.email"
                        class="p-3 mt-3 border rounded-lg bg-red-500/10 border-red-500/30"
                      >
                        <p class="flex items-center text-sm text-red-400">
                          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fill-rule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                              clip-rule="evenodd"
                            ></path>
                          </svg>
                          {{ formErrors.email }}
                        </p>
                      </div>
                    </transition>
                  </div>
                </div>

                <!-- Right Column -->
                <div class="space-y-6">
                  <!-- Display Name Field -->
                  <div class="group">
                    <label
                      for="display_name"
                      class="block mb-3 text-sm font-semibold text-gray-300"
                    >
                      <span class="flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                          ></path>
                        </svg>
                        <span>Display Name</span>
                        <span class="text-xs text-gray-500">(optional)</span>
                      </span>
                    </label>
                    <div class="relative">
                      <input
                        id="display_name"
                        v-model="formData.display_name"
                        type="text"
                        class="w-full px-4 py-4 text-white placeholder-gray-500 transition-all duration-300 border-2 bg-slate-700/50 rounded-xl focus:outline-none focus:ring-4"
                        :class="[
                          formErrors.display_name
                            ? 'border-red-500/70 bg-red-500/10 focus:ring-red-500/20 focus:border-red-400'
                            : formData.display_name
                              ? 'border-green-500/70 bg-green-500/10 focus:ring-green-500/20 focus:border-green-400'
                              : 'border-slate-600/50 focus:ring-purple-500/20 focus:border-purple-400',
                        ]"
                        maxlength="100"
                        placeholder="How should we call you?"
                      />
                      <div
                        v-if="formData.display_name && !formErrors.display_name"
                        class="absolute transform -translate-y-1/2 right-3 top-1/2"
                      >
                        <div
                          class="flex items-center justify-center w-6 h-6 bg-green-500 rounded-full"
                        >
                          <svg
                            class="w-4 h-4 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M5 13l4 4L19 7"
                            ></path>
                          </svg>
                        </div>
                      </div>
                    </div>
                    <transition
                      enter-active-class="transition duration-300 ease-out"
                      enter-from-class="transform -translate-y-2 opacity-0"
                      enter-to-class="transform translate-y-0 opacity-100"
                      leave-active-class="transition duration-200 ease-in"
                      leave-from-class="transform translate-y-0 opacity-100"
                      leave-to-class="transform -translate-y-2 opacity-0"
                    >
                      <div
                        v-if="formErrors.display_name"
                        class="p-3 mt-3 border rounded-lg bg-red-500/10 border-red-500/30"
                      >
                        <p class="flex items-center text-sm text-red-400">
                          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fill-rule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                              clip-rule="evenodd"
                            ></path>
                          </svg>
                          {{ formErrors.display_name }}
                        </p>
                      </div>
                    </transition>
                  </div>

                  <!-- Avatar URL Field -->
                  <div class="group">
                    <label for="avatar_url" class="block mb-3 text-sm font-semibold text-gray-300">
                      <span class="flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                          ></path>
                        </svg>
                        <span>Profile Picture URL</span>
                        <span class="text-xs text-gray-500">(optional)</span>
                      </span>
                    </label>
                    <div class="relative">
                      <input
                        id="avatar_url"
                        v-model="formData.avatar_url"
                        type="url"
                        class="w-full px-4 py-4 text-white placeholder-gray-500 transition-all duration-300 border-2 bg-slate-700/50 rounded-xl focus:outline-none focus:ring-4"
                        :class="[
                          formErrors.avatar_url
                            ? 'border-red-500/70 bg-red-500/10 focus:ring-red-500/20 focus:border-red-400'
                            : formData.avatar_url
                              ? 'border-green-500/70 bg-green-500/10 focus:ring-green-500/20 focus:border-green-400'
                              : 'border-slate-600/50 focus:ring-purple-500/20 focus:border-purple-400',
                        ]"
                        placeholder="https://example.com/your-avatar.jpg"
                      />
                      <div
                        v-if="
                          formData.avatar_url && !formErrors.avatar_url && imageLoadStatus.loaded
                        "
                        class="absolute transform -translate-y-1/2 right-3 top-1/2"
                      >
                        <div
                          class="flex items-center justify-center w-6 h-6 bg-green-500 rounded-full"
                        >
                          <svg
                            class="w-4 h-4 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M5 13l4 4L19 7"
                            ></path>
                          </svg>
                        </div>
                      </div>
                    </div>
                    <transition
                      enter-active-class="transition duration-300 ease-out"
                      enter-from-class="transform -translate-y-2 opacity-0"
                      enter-to-class="transform translate-y-0 opacity-100"
                      leave-active-class="transition duration-200 ease-in"
                      leave-from-class="transform translate-y-0 opacity-100"
                      leave-to-class="transform -translate-y-2 opacity-0"
                    >
                      <div
                        v-if="formErrors.avatar_url"
                        class="p-3 mt-3 border rounded-lg bg-red-500/10 border-red-500/30"
                      >
                        <p class="flex items-center text-sm text-red-400">
                          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fill-rule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                              clip-rule="evenodd"
                            ></path>
                          </svg>
                          {{ formErrors.avatar_url }}
                        </p>
                      </div>
                    </transition>

                    <!-- Avatar Preview -->
                    <div
                      v-if="formData.avatar_url && !formErrors.avatar_url"
                      class="p-4 mt-4 border bg-slate-700/30 rounded-xl border-slate-600/50"
                    >
                      <div class="flex items-center space-x-4">
                        <span class="text-sm font-medium text-gray-400">Preview:</span>
                        <div class="relative group">
                          <div
                            class="absolute transition-opacity rounded-full -inset-1 bg-gradient-to-r from-purple-500 to-blue-500 blur opacity-60 group-hover:opacity-100"
                          ></div>
                          <div
                            class="relative w-16 h-16 overflow-hidden border-2 rounded-full bg-slate-600 border-slate-700"
                          >
                            <img
                              :src="formData.avatar_url"
                              alt="Avatar preview"
                              class="object-cover w-full h-full transition-transform duration-300 group-hover:scale-110"
                              @load="imageLoadStatus = { loaded: true, error: false }"
                              @error="imageLoadStatus = { loaded: false, error: true }"
                            />
                            <div
                              v-if="imageLoadStatus.loaded && !imageLoadStatus.error"
                              class="absolute flex items-center justify-center w-5 h-5 bg-green-500 border-2 rounded-full -bottom-1 -right-1 border-slate-800"
                            >
                              <svg
                                class="w-3 h-3 text-white"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                  stroke-width="2"
                                  d="M5 13l4 4L19 7"
                                ></path>
                              </svg>
                            </div>
                            <div
                              v-if="imageLoadStatus.error"
                              class="absolute flex items-center justify-center w-5 h-5 bg-red-500 border-2 rounded-full -bottom-1 -right-1 border-slate-800"
                            >
                              <svg
                                class="w-3 h-3 text-white"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                              >
                                <path
                                  fill-rule="evenodd"
                                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                                  clip-rule="evenodd"
                                ></path>
                              </svg>
                            </div>
                          </div>
                        </div>
                        <div v-if="imageLoadStatus.error" class="text-sm text-red-400">
                          <p class="flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path
                                fill-rule="evenodd"
                                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                                clip-rule="evenodd"
                              ></path>
                            </svg>
                            Unable to load image
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Form Actions -->
                <div class="pt-6 border-t lg:col-span-2 border-slate-700/50">
                  <div
                    class="flex flex-col items-center space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4"
                  >
                    <button
                      type="submit"
                      class="relative flex-1 px-8 py-4 font-bold text-white transition-all duration-300 group sm:flex-none bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl hover:shadow-2xl hover:shadow-purple-500/25 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                      :disabled="isSubmitting"
                    >
                      <span
                        class="absolute inset-0 transition-opacity duration-300 opacity-0 bg-gradient-to-r from-purple-700 to-blue-700 rounded-xl blur group-hover:opacity-100"
                      ></span>
                      <span class="relative flex items-center justify-center space-x-2">
                        <svg
                          v-if="!isSubmitting"
                          class="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M5 13l4 4L19 7"
                          ></path>
                        </svg>
                        <div
                          v-else
                          class="w-5 h-5 border-2 rounded-full border-white/30 border-t-white animate-spin"
                        ></div>
                        <span>{{ isSubmitting ? 'Saving Changes...' : 'Save Changes' }}</span>
                      </span>
                    </button>

                    <button
                      type="button"
                      @click="cancelEditing"
                      class="flex-1 px-8 py-4 font-semibold text-white transition-all duration-300 border sm:flex-none bg-slate-700/50 rounded-xl border-slate-600/50 hover:bg-slate-600/50 hover:border-slate-500/50 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                      :disabled="isSubmitting"
                    >
                      <span class="flex items-center justify-center space-x-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M6 18L18 6M6 6l12 12"
                          ></path>
                        </svg>
                        <span>Cancel</span>
                      </span>
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
