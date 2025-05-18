<script setup>
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { loginSchema, validateField, validateForm } from '@/utils/validation'
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

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
})

const formError = ref('')

const handleLogin = async () => {
  // Validate the form using Zod
  const validation = validateFormData()

  if (!validation.valid) {
    // Show the first error message
    const firstErrorField = Object.keys(validation.errors)[0]
    formError.value = validation.errors[firstErrorField]
    return
  }

  formError.value = ''
  isSubmitting.value = true

  try {
    await authStore.login(form.value)

    toastStore.success('Login successful! Welcome back.')

    // Redirect to the intended page or home
    const redirectPath = route.query.redirect || '/chat'
    router.push(redirectPath)
  } catch (error) {
    formError.value = authStore.error || 'Login failed. Please check your credentials.'
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
              'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500',
              formErrors.username
                ? 'border-red-500 bg-red-500/10'
                : form.username
                  ? 'border-green-500 bg-green-500/10'
                  : 'border-zinc-700 bg-zinc-900',
            ]"
            autocomplete="username"
            required
          />
          <p v-if="formErrors.username" class="mt-1 text-xs text-red-400">
            {{ formErrors.username }}
          </p>
        </div>

        <div>
          <label for="password" class="block mb-1 text-sm font-medium text-gray-300">
            Password
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            :class="[
              'w-full px-3 py-2 text-white border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500',
              formErrors.password
                ? 'border-red-500 bg-red-500/10'
                : form.password
                  ? 'border-green-500 bg-green-500/10'
                  : 'border-zinc-700 bg-zinc-900',
            ]"
            autocomplete="current-password"
            required
          />
          <p v-if="formErrors.password" class="mt-1 text-xs text-red-400">
            {{ formErrors.password }}
          </p>
        </div>
        <div>
          <button
            type="submit"
            class="w-full px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isSubmitting || !formValid"
          >
            <span v-if="!isSubmitting">Login</span>
            <div v-else class="flex items-center justify-center">
              <div
                class="w-5 h-5 mr-2 border-t-2 border-white border-solid rounded-full animate-spin"
              ></div>
              <span>Logging in...</span>
            </div>
          </button>
        </div>

        <div class="text-sm text-center text-gray-400">
          Don't have an account?
          <router-link to="/register" class="text-primary-400 hover:text-primary-300">
            Register
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
