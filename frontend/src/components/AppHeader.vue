<script setup>
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()

const handleLogout = async () => {
  toastStore.info('Logging out...')
  // await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="shadow-md bg-zinc-900">
    <div class="container flex items-center justify-between px-4 py-3 mx-auto">
      <h1 class="text-xl font-medium text-white">rovertAIChat</h1>
      <nav class="flex space-x-6">
        <router-link
          to="/"
          class="text-gray-300 transition-colors duration-200 text hover:text-white"
          active-class="pb-1 text-white border-b border-primary-500"
        >
          Home
        </router-link>

        <template v-if="authStore.isAuthenticated">
          <router-link
            to="/chat"
            class="text-gray-300 transition-colors duration-200 text hover:text-white"
            active-class="pb-1 text-white border-b border-primary-500"
          >
            Chat
          </router-link>
          <router-link
            to="/profile"
            class="text-gray-300 transition-colors duration-200 text hover:text-white"
            active-class="pb-1 text-white border-b border-primary-500"
          >
            Profile
          </router-link>
          <router-link
            to="/settings"
            class="text-gray-300 transition-colors duration-200 text hover:text-white"
            active-class="pb-1 text-white border-b border-primary-500"
          >
            Settings
          </router-link>
          <button
            @click="handleLogout"
            class="pb-1 text-gray-300 transition-colors duration-200 hover:text-white"
          >
            Logout
          </button>
        </template>

        <template v-else>
          <router-link
            to="/login"
            class="text-gray-300 transition-colors duration-200 text hover:text-white"
            active-class="pb-1 text-white border-b border-primary-500"
          >
            Login
          </router-link>
          <router-link
            to="/register"
            class="text-gray-300 transition-colors duration-200 text hover:text-white"
            active-class="pb-1 text-white border-b border-primary-500"
          >
            Register
          </router-link>
        </template>
      </nav>
    </div>
  </header>
</template>
