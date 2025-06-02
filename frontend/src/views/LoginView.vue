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
  <div class="min-h-[calc(100vh-64px)] bg-zinc-900 relative overflow-hidden flex items-center">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div
        class="absolute rounded-full -top-40 -right-40 w-80 h-80 bg-blue-500/10 blur-3xl animate-pulse-subtle"
      ></div>
      <div
        class="absolute rounded-full -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 blur-3xl animate-pulse-subtle"
        style="animation-delay: 1s"
      ></div>
    </div>

    <div class="container relative max-w-md px-4 py-8 mx-auto">
      <div
        class="p-8 border shadow-2xl glass-effect rounded-2xl border-zinc-700/50 backdrop-blur-xl bg-zinc-800/60 animate-fade-in"
      >
        <!-- Header -->
        <div class="mb-8 text-center">
          <div class="mb-4">
            <div
              class="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-3"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-8 h-8 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
          </div>
          <h1 class="mb-2 text-3xl font-bold text-white">
            Welcome to <span class="text-gradient">rovertChat</span>
          </h1>
          <p class="text-gray-400">Sign in to continue your AI conversations</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div
            v-if="formError"
            class="px-4 py-3 text-red-100 border bg-red-500/20 border-red-500/30 rounded-xl backdrop-blur-sm animate-slide-up"
            role="alert"
            aria-live="assertive"
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clip-rule="evenodd"
                />
              </svg>
              {{ formError }}
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label for="username" class="block mb-2 text-sm font-semibold text-gray-200">
                Username
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <svg
                    class="text-gray-400 z-1 size-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <input
                  id="username"
                  v-model="form.username"
                  type="text"
                  :class="[
                    'w-full pl-10 pr-4 py-3 text-white border rounded-xl focus:outline-none focus:ring-2 transition-all duration-200 autofill:bg-zinc-800 bg-zinc-900/50 backdrop-blur-sm',
                    formErrors.username
                      ? 'border-red-500/50 bg-red-500/10 focus:ring-red-500/50'
                      : form.username
                        ? 'border-green-500/50 bg-green-500/10 focus:ring-green-500/50'
                        : 'border-zinc-700/50 focus:ring-purple-500/50 hover:border-zinc-600/50',
                  ]"
                  placeholder="Enter your username"
                  autocomplete="username"
                  :aria-invalid="!!formErrors.username"
                  :aria-describedby="formErrors.username ? 'username-error' : ''"
                  required
                />
              </div>
              <p
                v-if="formErrors.username"
                id="username-error"
                class="mt-2 text-sm text-red-400 animate-slide-up"
                aria-live="polite"
              >
                {{ formErrors.username }}
              </p>
            </div>

            <div>
              <label for="password" class="block mb-2 text-sm font-semibold text-gray-200">
                Password
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <svg
                    class="text-gray-400 z-1 size-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  :class="[
                    'w-full pl-10 pr-12 py-3 text-white border rounded-xl focus:outline-none focus:ring-2 transition-all duration-200 autofill:bg-zinc-800 bg-zinc-900/50 backdrop-blur-sm',
                    formErrors.password
                      ? 'border-red-500/50 bg-red-500/10 focus:ring-red-500/50'
                      : form.password
                        ? 'border-green-500/50 bg-green-500/10 focus:ring-green-500/50'
                        : 'border-zinc-700/50 focus:ring-purple-500/50 hover:border-zinc-600/50',
                  ]"
                  placeholder="Enter your password"
                  autocomplete="current-password"
                  required
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 transition-colors duration-200 hover:text-white focus:outline-none"
                  @click="showPassword = !showPassword"
                  aria-label="Toggle password visibility"
                  tabindex="-1"
                >
                  <svg
                    v-if="!showPassword"
                    xmlns="http://www.w3.org/2000/svg"
                    class="size-5"
                    viewBox="0 0 24 24"
                  >
                    <g fill="none">
                      <path
                        d="M12 9.005a4 4 0 1 1 0 8a4 4 0 0 1 0-8zm0 1.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 0 0 0-5zM12 5.5c4.613 0 8.596 3.15 9.701 7.564a.75.75 0 1 1-1.455.365a8.503 8.503 0 0 0-16.493.004a.75.75 0 0 1-1.455-.363A10.003 10.003 0 0 1 12 5.5z"
                        fill="currentColor"
                      />
                    </g>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="size-5" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M2.22 2.22a.75.75 0 0 0-.073.976l.073.084l4.034 4.035a10 10 0 0 0-3.955 5.75a.75.75 0 0 0 1.455.364a8.5 8.5 0 0 1 3.58-5.034l1.81 1.81A4 4 0 0 0 14.8 15.86l5.919 5.92a.75.75 0 0 0 1.133-.977l-.073-.084l-6.113-6.114l.001-.002l-1.2-1.198l-2.87-2.87h.002l-2.88-2.877l.001-.002l-1.133-1.13L3.28 2.22a.75.75 0 0 0-1.06 0m7.984 9.045l3.535 3.536a2.5 2.5 0 0 1-3.535-3.535M12 5.5c-1 0-1.97.148-2.889.425l1.237 1.236a8.503 8.503 0 0 1 9.899 6.272a.75.75 0 0 0 1.455-.363A10 10 0 0 0 12 5.5m.195 3.51l3.801 3.8a4.003 4.003 0 0 0-3.801-3.8"
                    />
                  </svg>
                </button>
              </div>
              <p v-if="formErrors.password" class="mt-2 text-sm text-red-400 animate-slide-up">
                {{ formErrors.password }}
              </p>
            </div>
          </div>

          <div
            class="flex items-center justify-between p-3 transition-colors duration-200 rounded-lg bg-zinc-700/20 hover:bg-zinc-700/30"
          >
            <div class="flex items-center">
              <input
                id="rememberUsername"
                v-model="rememberUsername"
                type="checkbox"
                class="w-5 h-5 rounded-md cursor-pointer accent-purple-500 bg-zinc-900 border-zinc-600 focus:ring-2 focus:ring-purple-500/50 focus:ring-offset-1 focus:ring-offset-zinc-800"
                aria-describedby="remember-username-hint"
              />
              <label
                for="rememberUsername"
                class="ml-3 text-sm text-gray-300 cursor-pointer select-none"
              >
                Remember username
              </label>
            </div>
            <span id="remember-username-hint" class="sr-only">
              When checked, your username will be remembered for your next visit
            </span>
          </div>

          <div>
            <button
              type="submit"
              class="w-full px-6 py-3 font-semibold text-white transition-all duration-300 shadow-xl rounded-xl bg-gradient-3 hover:-translate-y-1 hover:shadow-2xl hover:shadow-purple-500/25 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:ring-offset-2 focus:ring-offset-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none group"
              :disabled="isSubmitting || !formValid"
              aria-busy="isSubmitting"
              aria-live="polite"
            >
              <span v-if="!isSubmitting" class="flex items-center justify-center">
                Sign In
                <svg
                  class="w-5 h-5 ml-2 transition-transform duration-300 group-hover:translate-x-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </span>
              <div v-else class="flex items-center justify-center">
                <div
                  class="w-5 h-5 mr-2 border-t-2 border-white border-solid rounded-full animate-spin"
                  aria-hidden="true"
                ></div>
                <span>Signing in...</span>
              </div>
            </button>
          </div>

          <div class="text-center">
            <p class="text-gray-400">
              Don't have an account?
              <router-link
                :to="{
                  path: '/register',
                  query: form.username ? { username: form.username } : undefined,
                }"
                class="ml-1 font-semibold transition-all duration-200 text-gradient hover:text-gradient-2 focus:outline-none focus:underline"
                aria-labelledby="register-prompt"
              >
                Create one now
              </router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
