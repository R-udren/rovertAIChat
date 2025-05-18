<script setup>
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

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

    toastStore.success('Registration successful!')

    // Redirect to profile page with success message
    const redirectPath = route.query.redirect || '/chat'
    router.push(redirectPath)
  } catch (error) {
    formError.value = authStore.error || 'Registration failed. Please try again.'
    toastStore.error('Registration failed. Please check your input and try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container max-w-md px-4 py-8 mx-auto">
    <div class="p-6 rounded-lg shadow-lg bg-zinc-800">
      <h1 class="mb-6 text-2xl font-bold text-center text-white">Register</h1>

      <form @submit.prevent="handleRegister" class="space-y-4">
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
            class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="username"
            required
            minlength="4"
            maxlength="64"
          />
          <p class="mt-1 text-xs text-gray-500">4-64 characters long</p>
        </div>

        <div>
          <label for="email" class="block mb-1 text-sm font-medium text-gray-300"> Email </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="email"
            required
          />
        </div>

        <div>
          <label for="password" class="block mb-1 text-sm font-medium text-gray-300">
            Password
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="new-password"
            required
            minlength="8"
          />
          <p class="mt-1 text-xs text-gray-500">At least 8 characters long</p>
        </div>

        <div>
          <label for="confirmPassword" class="block mb-1 text-sm font-medium text-gray-300">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="new-password"
            required
          />
        </div>
        <div>
          <button
            type="submit"
            class="w-full px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-zinc-800"
            :disabled="isSubmitting"
          >
            <span v-if="!isSubmitting">Register</span>
            <div v-else class="flex items-center justify-center">
              <div
                class="w-5 h-5 mr-2 border-t-2 border-white border-solid rounded-full animate-spin"
              ></div>
              <span>Registering...</span>
            </div>
          </button>
        </div>

        <div class="text-sm text-center text-gray-400">
          Already have an account?
          <router-link to="/login" class="text-primary-400 hover:text-primary-300">
            Login
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
