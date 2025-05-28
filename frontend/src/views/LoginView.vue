<script setup>
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { loginSchema, validateField, validateForm } from '@/utils/validation'

const authStore = useAuthStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()

const form = ref({
  username: '',
  password: '',
})

const formErrors = ref({
  username: '',
  password: '',
})

const formValid = ref(false)
const isSubmitting = ref(false)
const showPassword = ref(false)
const rememberUsername = ref(localStorage.getItem('remember_username_preference') === 'true')

// Add watchers for real-time validation
watch(
  () => form.value.username,
  (newValue) => {
    const result = validateField(loginSchema, 'username', newValue, form.value)
    formErrors.value.username = result.valid ? '' : result.message
    validateFormData()
  },
)

watch(
  () => form.value.password,
  (newValue) => {
    const result = validateField(loginSchema, 'password', newValue, form.value)
    formErrors.value.password = result.valid ? '' : result.message
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
  const result = validateForm(loginSchema, form.value)
  formValid.value = result.valid
  return result
}

onMounted(() => {
  // Check if user was redirected after registration
  if (route.query.registered === 'success') {
    toastStore.success('Registration successful! Please login to continue.')
  }

  // Set username from query parameters if provided
  if (route.query.username) {
    form.value.username = route.query.username
    // If user wants to remember username
    if (rememberUsername.value) {
      localStorage.setItem('remembered_username', form.value.username)
    }
    validateField(loginSchema, 'username', form.value.username, form.value)
  }
  // If no username in query params and user preference is to remember, try to load from localStorage
  else if (rememberUsername.value && localStorage.getItem('remembered_username')) {
    form.value.username = localStorage.getItem('remembered_username')
    validateField(loginSchema, 'username', form.value.username, form.value)
  }
})

const formError = ref('')

const handleLogin = async () => {
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
    await authStore.login(form.value)

    // Save username to localStorage if user wants to remember
    if (rememberUsername.value) {
      localStorage.setItem('remembered_username', form.value.username)
    }

    toastStore.success('Login successful! Welcome back.')

    // Redirect to the intended page or home
    const redirectPath = route.query.redirect || '/chat'
    router.push(redirectPath)
  } catch (error) {
    formError.value = authStore.error || 'Login failed. Please check your credentials.'

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
  <div class="container max-w-md px-4 py-8 mx-auto">
    <div class="p-6 rounded-lg shadow-lg bg-zinc-800">
      <h1 class="mb-6 text-2xl font-bold text-center text-white">Login</h1>

      <form @submit.prevent="handleLogin" class="space-y-4">
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
            :aria-describedby="formErrors.username ? 'username-error' : ''"
            required
          />
          <p
            v-if="formErrors.username"
            id="username-error"
            class="mt-1 text-xs text-red-400"
            aria-live="polite"
          >
            {{ formErrors.username }}
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
              autocomplete="current-password"
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
          <p v-if="formErrors.password" class="mt-1 text-xs text-red-400">
            {{ formErrors.password }}
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
            <span v-if="!isSubmitting">Login</span>
            <div v-else class="flex items-center justify-center">
              <div
                class="w-5 h-5 mr-2 border-t-2 border-white border-solid rounded-full animate-spin"
                aria-hidden="true"
              ></div>
              <span>Logging in...</span>
            </div>
          </button>
        </div>

        <div class="text-sm text-center text-gray-400">
          <span id="register-prompt">Don't have an account?</span>
          <router-link
            :to="{
              path: '/register',
              query: form.username ? { username: form.username } : undefined,
            }"
            class="text-primary-400 hover:text-primary-300 focus:outline-none focus:underline focus:text-primary-300"
            aria-labelledby="register-prompt"
          >
            Register
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
