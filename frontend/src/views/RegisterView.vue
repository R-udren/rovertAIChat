<script setup>
import { useFormValidation } from '@/composables/useFormValidation'
import { useSavedUsername } from '@/composables/useSavedUsername'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { registerSchema } from '@/utils/validation'

const authStore = useAuthStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()

// Form handling
const { form, errors, isSubmitting, validate, clearErrors } = useFormValidation(registerSchema)
const { rememberUsername, savedUsername, saveUsername } = useSavedUsername()

// UI state
const showPassword = ref(false)
const formError = ref('')

// Initialize form
form.value = {
  username: route.query.username || savedUsername.value || '',
  email: '',
  password: '',
  confirmPassword: '',
}

const handleRegister = async () => {
  clearErrors()

  if (!validate()) {
    const firstError = Object.values(errors.value)[0]
    formError.value = firstError
    return
  }

  formError.value = ''
  isSubmitting.value = true

  try {
    await authStore.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
    })

    // Save username if user wants to remember
    saveUsername(form.value.username)

    toastStore.success('Registration successful!')

    // Redirect to intended page
    const redirectPath = route.query.redirect || '/chat'
    router.push(redirectPath)
  } catch (error) {
    formError.value = authStore.error || 'Registration failed. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div
    class="min-h-[calc(100vh-64px)] bg-zinc-900 relative overflow-hidden flex items-center"
    role="main"
  >
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div
        class="absolute rounded-full -top-40 -right-40 w-80 h-80 bg-purple-500/10 blur-3xl animate-pulse-subtle"
      ></div>
      <div
        class="absolute rounded-full -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 blur-3xl animate-pulse-subtle"
        style="animation-delay: 1s"
      ></div>
      <div
        class="absolute w-64 h-64 rounded-full top-1/3 left-1/3 bg-pink-500/5 blur-3xl animate-pulse-subtle"
        style="animation-delay: 2s"
      ></div>
    </div>

    <div class="container relative max-w-lg px-4 py-8 mx-auto">
      <div
        class="p-8 border shadow-2xl glass-effect rounded-2xl border-zinc-700/50 backdrop-blur-xl bg-zinc-800/60 animate-fade-in"
      >
        <!-- Header -->
        <div class="mb-8 text-center">
          <div class="mb-4">
            <div
              class="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-2"
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
                  d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                />
              </svg>
            </div>
          </div>
          <h1 class="mb-2 text-3xl font-bold text-white">
            Join <span class="text-gradient-2">rovertChat</span>
          </h1>
          <p class="text-gray-400">Create your account and start your AI journey</p>
        </div>

        <form
          @submit.prevent="handleRegister"
          class="space-y-6"
          aria-labelledby="register-heading"
          novalidate
        >
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

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label for="username" class="block mb-2 text-sm font-semibold text-gray-200">
                Username
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <svg
                    class="w-5 h-5 text-gray-400"
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
                    errors.username
                      ? 'border-red-500/50 bg-red-500/10 focus:ring-red-500/50'
                      : form.username
                        ? 'border-green-500/50 bg-green-500/10 focus:ring-green-500/50'
                        : 'border-zinc-700/50 focus:ring-purple-500/50 hover:border-zinc-600/50',
                  ]"
                  placeholder="Choose a username"
                  autocomplete="username"
                  :aria-invalid="!!errors.username"
                  :aria-describedby="errors.username ? 'username-error' : 'username-hint'"
                  required
                />
              </div>
              <p
                v-if="errors.username"
                id="username-error"
                class="mt-2 text-sm text-red-400 animate-slide-up"
                aria-live="polite"
              >
                {{ errors.username }}
              </p>
              <p v-else id="username-hint" class="mt-2 text-xs text-gray-500">
                4-64 characters long
              </p>
            </div>

            <div>
              <label for="email" class="block mb-2 text-sm font-semibold text-gray-200">
                Email
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <svg
                    class="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
                    />
                  </svg>
                </div>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  :class="[
                    'w-full pl-10 pr-4 py-3 text-white border rounded-xl focus:outline-none focus:ring-2 transition-all duration-200 autofill:bg-zinc-800 bg-zinc-900/50 backdrop-blur-sm',
                    errors.email
                      ? 'border-red-500/50 bg-red-500/10 focus:ring-red-500/50'
                      : form.email
                        ? 'border-green-500/50 bg-green-500/10 focus:ring-green-500/50'
                        : 'border-zinc-700/50 focus:ring-purple-500/50 hover:border-zinc-600/50',
                  ]"
                  placeholder="Enter your email"
                  autocomplete="email"
                  :aria-invalid="!!errors.email"
                  :aria-describedby="errors.email ? 'email-error' : ''"
                  required
                />
              </div>
              <p
                v-if="errors.email"
                id="email-error"
                class="mt-2 text-sm text-red-400 animate-slide-up"
                aria-live="polite"
              >
                {{ errors.email }}
              </p>
            </div>
          </div>

          <div>
            <label for="password" class="block mb-2 text-sm font-semibold text-gray-200">
              Password
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg
                  class="w-5 h-5 text-gray-400"
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
                  errors.password
                    ? 'border-red-500/50 bg-red-500/10 focus:ring-red-500/50'
                    : form.password
                      ? 'border-green-500/50 bg-green-500/10 focus:ring-green-500/50'
                      : 'border-zinc-700/50 focus:ring-purple-500/50 hover:border-zinc-600/50',
                ]"
                placeholder="Create a password"
                autocomplete="new-password"
                :aria-invalid="!!errors.password"
                :aria-describedby="errors.password ? 'password-error' : 'password-hint'"
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
            <p
              v-if="errors.password"
              id="password-error"
              class="mt-2 text-sm text-red-400 animate-slide-up"
              aria-live="polite"
            >
              {{ errors.password }}
            </p>
            <p v-else id="password-hint" class="mt-2 text-xs text-gray-500">
              At least 8 characters long
            </p>
          </div>

          <div>
            <label for="confirmPassword" class="block mb-2 text-sm font-semibold text-gray-200">
              Confirm Password
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg
                  class="w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                :class="[
                  'w-full pl-10 pr-12 py-3 text-white border rounded-xl focus:outline-none focus:ring-2 transition-all duration-200 autofill:bg-zinc-800 bg-zinc-900/50 backdrop-blur-sm',
                  errors.confirmPassword
                    ? 'border-red-500/50 bg-red-500/10 focus:ring-red-500/50'
                    : form.confirmPassword
                      ? 'border-green-500/50 bg-green-500/10 focus:ring-green-500/50'
                      : 'border-zinc-700/50 focus:ring-purple-500/50 hover:border-zinc-600/50',
                ]"
                placeholder="Confirm your password"
                autocomplete="new-password"
                :aria-invalid="!!errors.confirmPassword"
                :aria-describedby="errors.confirmPassword ? 'confirmPassword-error' : ''"
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
            <p
              v-if="errors.confirmPassword"
              id="confirmPassword-error"
              class="mt-2 text-sm text-red-400 animate-slide-up"
              aria-live="polite"
            >
              {{ errors.confirmPassword }}
            </p>
          </div>

          <div
            class="flex items-center justify-between p-4 transition-all duration-200 border rounded-xl bg-zinc-700/20 hover:bg-zinc-700/30 border-zinc-700/30"
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
                Remember username for next time
              </label>
            </div>
            <span id="remember-username-hint" class="sr-only">
              When checked, your username will be remembered for your next visit
            </span>
          </div>

          <div>
            <button
              type="submit"
              class="w-full px-6 py-3 font-semibold text-white transition-all duration-300 shadow-xl rounded-xl bg-gradient-2 hover:-translate-y-1 hover:shadow-2xl hover:shadow-pink-500/25 focus:outline-none focus:ring-2 focus:ring-pink-500/50 focus:ring-offset-2 focus:ring-offset-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none group"
              :disabled="isSubmitting"
              aria-busy="isSubmitting"
              aria-live="polite"
            >
              <span v-if="!isSubmitting" class="flex items-center justify-center">
                Create Account
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
                <span>Creating Account...</span>
              </div>
            </button>
          </div>

          <div class="text-center">
            <p class="text-gray-400">
              Already have an account?
              <router-link
                :to="{
                  path: '/login',
                  query: form.username ? { username: form.username } : undefined,
                }"
                class="ml-1 font-semibold transition-all duration-200 text-gradient hover:text-gradient-2 focus:outline-none focus:underline"
                aria-labelledby="login-prompt"
              >
                Sign in here
              </router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
