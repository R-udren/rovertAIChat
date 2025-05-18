<script setup>
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const authStore = useAuthStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()

const form = ref({
  username: '',
  password: '',
})

const formError = ref('')
const isSubmitting = ref(false)

onMounted(() => {
  // Check if user was redirected after registration
  if (route.query.registered === 'success') {
    toastStore.success('Registration successful! Please login to continue.')
  }
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    formError.value = 'Please enter both username and password'
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
            class="w-full px-3 py-2 text-white border rounded-md border-zinc-700 bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            autocomplete="username"
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
            autocomplete="current-password"
            required
          />
        </div>
        <div>
          <button
            type="submit"
            class="w-full px-4 py-2 font-medium text-white transition-colors duration-200 rounded-md bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-zinc-800"
            :disabled="isSubmitting"
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
