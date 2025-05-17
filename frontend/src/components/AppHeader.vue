<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="bg-zinc-900 shadow-md">
    <div class="container mx-auto px-4 py-3 flex items-center justify-between">
      <h1 class="text-xl font-medium text-white">rovertAIChat</h1>
      <nav class="flex space-x-6">
        <router-link
          to="/"
          class="text text-gray-300 hover:text-white transition-colors duration-200"
          active-class="text-white border-b border-primary-500 pb-1"
        >
          Home
        </router-link>

        <template v-if="authStore.isAuthenticated">
          <router-link
            to="/chat"
            class="text text-gray-300 hover:text-white transition-colors duration-200"
            active-class="text-white border-b border-primary-500 pb-1"
          >
            Chat
          </router-link>
          <router-link
            to="/profile"
            class="text text-gray-300 hover:text-white transition-colors duration-200"
            active-class="text-white border-b border-primary-500 pb-1"
          >
            Profile
          </router-link>
          <router-link
            to="/settings"
            class="text text-gray-300 hover:text-white transition-colors duration-200"
            active-class="text-white border-b border-primary-500 pb-1"
          >
            Settings
          </router-link>
          <button
            @click="handleLogout"
            class="text text-gray-300 hover:text-white transition-colors duration-200"
          >
            Logout
          </button>
        </template>

        <template v-else>
          <router-link
            to="/login"
            class="text text-gray-300 hover:text-white transition-colors duration-200"
            active-class="text-white border-b border-primary-500 pb-1"
          >
            Login
          </router-link>
          <router-link
            to="/register"
            class="text text-gray-300 hover:text-white transition-colors duration-200"
            active-class="text-white border-b border-primary-500 pb-1"
          >
            Register
          </router-link>
        </template>
      </nav>
    </div>
  </header>
</template>
