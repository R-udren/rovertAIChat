<script setup>
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { registerSchema, validateField, validateForm } from '@/utils/validation'
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const authStore = useAuthStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const formErrors = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const formValid = ref(false)
const formError = ref('')
const isSubmitting = ref(false)
const showPassword = ref(false)
const rememberUsername = ref(localStorage.getItem('remember_username_preference') === 'true')

// Add watchers for real-time validation
watch(
  () => form.value.username,
  (newValue) => {
    const result = validateField(registerSchema, 'username', newValue, form.value)
    formErrors.value.username = result.valid ? '' : result.message
    validateFormData()
  },
)

watch(
  () => form.value.email,
  (newValue) => {
    const result = validateField(registerSchema, 'email', newValue, form.value)
    formErrors.value.email = result.valid ? '' : result.message
    validateFormData()
  },
)

watch(
  () => form.value.password,
  (newValue) => {
    const result = validateField(registerSchema, 'password', newValue, form.value)
    formErrors.value.password = result.valid ? '' : result.message

    // Also validate confirmPassword when password changes
    if (form.value.confirmPassword) {
      const confirmResult = validateField(
        registerSchema,
        'confirmPassword',
        form.value.confirmPassword,
        form.value,
      )
      formErrors.value.confirmPassword = confirmResult.valid ? '' : confirmResult.message
    }

    validateFormData()
  },
)

watch(
  () => form.value.confirmPassword,
  (newValue) => {
    // For confirmPassword, validate with the full form data
    const result = validateField(registerSchema, 'confirmPassword', newValue, form.value)
    formErrors.value.confirmPassword = result.valid ? '' : result.message
    validateFormData()
  },
)

// Watch for remember username preference changes
watch(
  () => rememberUsername.value,
  (newValue) => {
    localStorage.setItem('remember_username_preference', newValue)

    // If turning off, clear the saved username
    if (!newValue) {
      localStorage.removeItem('remembered_username')
    } else if (form.value.username) {
      // If turning on and we have a username, save it
      localStorage.setItem('remembered_username', form.value.username)
    }
  },
)

// Validate the entire form
const validateFormData = () => {
  const result = validateForm(registerSchema, form.value)
  formValid.value = result.valid
  return result
}

// Check for username in query params on mount
onMounted(() => {
  // Set username from query parameters if provided
  if (route.query.username) {
    form.value.username = route.query.username
    // If user wants to remember username
    if (rememberUsername.value) {
      localStorage.setItem('remembered_username', form.value.username)
    }
    validateField(registerSchema, 'username', form.value.username, form.value)
  }
  // If no username in query params and user preference is to remember, try to load from localStorage
  else if (rememberUsername.value && localStorage.getItem('remembered_username')) {
    form.value.username = localStorage.getItem('remembered_username')
    validateField(registerSchema, 'username', form.value.username, form.value)
  }
})

const handleRegister = async () => {
  // Validate the form using Zod
  const validation = validateFormData()

  if (!validation.valid) {
    // Show the first error message
    const firstErrorField = Object.keys(validation.errors)[0]
    formError.value = validation.errors[firstErrorField]

    // Focus on the first field with an error
    setTimeout(() => {
      const errorElement = document.getElementById(firstErrorField)
      if (errorElement) errorElement.focus()
    }, 100)

    return
  }

  formError.value = ''
  isSubmitting.value = true

  try {
    // Submit registration data
    await authStore.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
    })

    // Save username to localStorage if user wants to remember
    if (rememberUsername.value) {
      localStorage.setItem('remembered_username', form.value.username)
    }

    toastStore.success('Registration successful!')

    // Announce success for screen readers
    const successAnnouncement = document.createElement('div')
    successAnnouncement.setAttribute('aria-live', 'assertive')
    successAnnouncement.setAttribute('class', 'sr-only')
    successAnnouncement.textContent = 'Registration successful! Redirecting you now.'
    document.body.appendChild(successAnnouncement)

    // Clean up after 3 seconds
    setTimeout(() => {
      document.body.removeChild(successAnnouncement)
    }, 3000)

    // Redirect to profile page with success message
    const redirectPath = route.query.redirect || '/chat'
    router.push(redirectPath)
  } catch (error) {
    formError.value = authStore.error || 'Registration failed. Please try again.'
    toastStore.error('Registration failed. Please check your input and try again.')

    // Focus on the error message for screen readers
    setTimeout(() => {
      const errorElement = document.querySelector('[role="alert"]')
      if (errorElement) errorElement.focus()
    }, 100)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container max-w-md px-4 py-8 mx-auto" role="main">
    <div class="p-6 rounded-lg shadow-lg bg-zinc-800">
      <h1 id="register-heading" class="mb-6 text-2xl font-bold text-center text-white">Register</h1>

      <form
        @submit.prevent="handleRegister"
        class="space-y-4"
        aria-labelledby="register-heading"
        novalidate
      >
        <div
          v-if="formError"
          class="px-4 py-2 text-red-100 bg-red-500 border border-red-500 rounded-md bg-opacity-20"
          role="alert"
          aria-live="assertive"
        >
          {{ formError }}
        </div>

        <div>
          <label for="username" class="block mb-1 text-sm font-medium text-gray-300">
            Username
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            :class="[
              'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2',
              formErrors.username
                ? 'border-red-500 bg-red-500/10'
                : form.username
                  ? 'border-green-500 bg-green-500/10 focus:ring-green-500'
                  : 'border-zinc-700 bg-zinc-900',
            ]"
            autocomplete="username"
            :aria-invalid="!!formErrors.username"
            :aria-describedby="formErrors.username ? 'username-error' : 'username-hint'"
            required
          />
          <p
            v-if="formErrors.username"
            id="username-error"
            class="mt-1 text-xs text-red-400 transition-opacity"
            aria-live="polite"
          >
            {{ formErrors.username }}
          </p>
          <p v-else id="username-hint" class="mt-1 text-xs text-gray-500">4-64 characters long</p>
        </div>

        <div>
          <label for="email" class="block mb-1 text-sm font-medium text-gray-300"> Email </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            :class="[
              'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2 ',
              formErrors.email
                ? 'border-red-500 bg-red-500/10'
                : form.email
                  ? 'border-green-500 bg-green-500/10 focus:ring-green-500'
                  : 'border-zinc-700 bg-zinc-900',
            ]"
            autocomplete="email"
            :aria-invalid="!!formErrors.email"
            :aria-describedby="formErrors.email ? 'email-error' : ''"
            required
          />
          <p
            v-if="formErrors.email"
            id="email-error"
            class="mt-1 text-xs text-red-400 transition-opacity"
            aria-live="polite"
          >
            {{ formErrors.email }}
          </p>
        </div>

        <div>
          <label for="password" class="block mb-1 text-sm font-medium text-gray-300">
            Password
          </label>
          <div class="relative">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              :class="[
                'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2 pr-10',
                formErrors.password
                  ? 'border-red-500 bg-red-500/10'
                  : form.password
                    ? 'border-green-500 bg-green-500/10 focus:ring-green-500'
                    : 'border-zinc-700 bg-zinc-900',
              ]"
              autocomplete="new-password"
              :aria-invalid="!!formErrors.password"
              :aria-describedby="formErrors.password ? 'password-error' : 'password-hint'"
              required
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-white focus:outline-none"
              @click="showPassword = !showPassword"
              aria-label="Toggle password visibility"
              tabindex="-1"
            >
              <span v-if="showPassword" aria-hidden="true">🙈</span>
              <span v-else aria-hidden="true">👁️</span>
            </button>
          </div>
          <p
            v-if="formErrors.password"
            id="password-error"
            class="mt-1 text-xs text-red-400 transition-opacity"
            aria-live="polite"
          >
            {{ formErrors.password }}
          </p>
          <p v-else id="password-hint" class="mt-1 text-xs text-gray-500">
            At least 8 characters long
          </p>
        </div>

        <div>
          <label for="confirmPassword" class="block mb-1 text-sm font-medium text-gray-300">
            Confirm Password
          </label>
          <div class="relative">
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              :class="[
                'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2 pr-10',
                formErrors.confirmPassword
                  ? 'border-red-500 bg-red-500/10'
                  : form.confirmPassword
                    ? 'border-green-500 bg-green-500/10 focus:ring-green-500'
                    : 'border-zinc-700 bg-zinc-900',
              ]"
              autocomplete="new-password"
              :aria-invalid="!!formErrors.confirmPassword"
              :aria-describedby="formErrors.confirmPassword ? 'confirmPassword-error' : ''"
              required
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-white focus:outline-none"
              @click="showPassword = !showPassword"
              aria-label="Toggle password visibility"
              tabindex="-1"
            >
              <span v-if="showPassword" aria-hidden="true">🙈</span>
              <span v-else aria-hidden="true">👁️</span>
            </button>
          </div>
          <p
            v-if="formErrors.confirmPassword"
            id="confirmPassword-error"
            class="mt-1 text-xs text-red-400 transition-opacity"
            aria-live="polite"
          >
            {{ formErrors.confirmPassword }}
          </p>
        </div>

        <div class="flex items-center">
          <input
            id="rememberUsername"
            v-model="rememberUsername"
            type="checkbox"
            class="w-4 h-4 rounded accent-primary-600 bg-zinc-900 border-zinc-700 focus:ring-primary-500"
            aria-describedby="remember-username-hint"
          />
          <label for="rememberUsername" class="ml-2 text-sm text-gray-300">
            Remember username
          </label>
          <span id="remember-username-hint" class="sr-only">
            When checked, your username will be remembered for your next visit
          </span>
        </div>

        <div>
          <button
            type="submit"
            class="w-full px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isSubmitting || !formValid"
            aria-busy="isSubmitting"
            aria-live="polite"
          >
            <span v-if="!isSubmitting">Register</span>
            <div v-else class="flex items-center justify-center">
              <div
                class="w-5 h-5 mr-2 border-t-2 border-white border-solid rounded-full animate-spin"
                aria-hidden="true"
              ></div>
              <span>Registering...</span>
            </div>
          </button>
        </div>

        <div class="text-sm text-center text-gray-400">
          <span id="login-prompt">Already have an account?</span>
          <router-link
            :to="{ path: '/login', query: form.username ? { username: form.username } : undefined }"
            class="text-primary-400 hover:text-primary-300 focus:outline-none focus:underline focus:text-primary-300"
            aria-labelledby="login-prompt"
          >
            Login
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
