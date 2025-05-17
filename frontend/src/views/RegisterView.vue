<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const formError = ref('')
const isSubmitting = ref(false)

const handleRegister = async () => {
  // Basic form validation
  if (!form.value.username || !form.value.email || !form.value.password) {
    formError.value = 'Please fill in all required fields'
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    formError.value = 'Passwords do not match'
    return
  }

  if (form.value.password.length < 8) {
    formError.value = 'Password must be at least 8 characters long'
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

    toastStore.success('Registration successful! Please login to continue.')

    // Redirect to login page with success message
    router.push({
      path: '/login',
      query: { registered: 'success' },
    })
  } catch (error) {
    formError.value = authStore.error || 'Registration failed. Please try again.'
    toastStore.error('Registration failed. Please check your input and try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-md">
    <div class="bg-zinc-800 rounded-lg shadow-lg p-6">
      <h1 class="text-2xl font-bold text-white mb-6 text-center">Register</h1>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div
          v-if="formError"
          class="bg-red-500 bg-opacity-20 border border-red-500 text-red-100 px-4 py-2 rounded-md"
        >
          {{ formError }}
        </div>

        <div>
          <label for="username" class="block text-sm font-medium text-gray-300 mb-1">
            Username
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="username"
            required
            minlength="4"
            maxlength="64"
          />
          <p class="text-xs text-gray-500 mt-1">4-64 characters long</p>
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-300 mb-1"> Email </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="email"
            required
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-300 mb-1">
            Password
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="new-password"
            required
            minlength="8"
          />
          <p class="text-xs text-gray-500 mt-1">At least 8 characters long</p>
        </div>

        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-300 mb-1">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            class="w-full px-3 py-2 border border-zinc-700 bg-zinc-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="new-password"
            required
          />
        </div>
        <div>
          <button
            type="submit"
            class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-zinc-800"
            :disabled="isSubmitting"
          >
            <span v-if="!isSubmitting">Register</span>
            <div v-else class="flex items-center justify-center">
              <div
                class="w-5 h-5 border-t-2 border-white border-solid rounded-full animate-spin mr-2"
              ></div>
              <span>Registering...</span>
            </div>
          </button>
        </div>

        <div class="text-center text-gray-400 text-sm">
          Already have an account?
          <router-link to="/login" class="text-primary-400 hover:text-primary-300">
            Login
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
