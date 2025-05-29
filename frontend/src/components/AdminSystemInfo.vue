<script setup>
import { api } from '@/services/api'
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'
import { computed, ref, watch } from 'vue'

const props = defineProps({
  active: {
    type: Boolean,
    default: false,
  },
})

const adminStore = useAdminStore()
const toastStore = useToastStore()

const loading = ref(false)
const ollamaStatus = ref({ connected: false })

// Watch for active prop changes
watch(
  () => props.active,
  async (newActive) => {
    if (newActive) {
      await refreshAllData()
      await checkSystemHealth()
    }
  },
  { immediate: true },
)

// System configuration
const systemConfig = ref({
  environment: 'Development',
  apiVersion: 'v1.0.0',
  ollamaUrl: 'http://localhost:11434',
})

// Computed properties for system stats
const systemStats = computed(() => {
  const users = adminStore.users
  const models = adminStore.models

  return {
    totalUsers: users.length,
    activeUsers: users.filter((user) => user.is_active).length,
    adminUsers: users.filter((user) => user.role === 'admin').length,
    totalModels: models.length,
  }
})

const recentUsers = computed(() => {
  return adminStore.users
    .filter((user) => user.last_login)
    .sort((a, b) => new Date(b.last_login) - new Date(a.last_login))
    .slice(0, 5)
})

// Utility functions
const getUserInitials = (user) => {
  return (user.username.charAt(0) + (user.username.charAt(1) || '')).toUpperCase()
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 1) return 'Today'
  if (diffDays <= 7) return `${diffDays} days ago`

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  })
}

// Admin actions
const refreshAllData = async () => {
  loading.value = true
  try {
    await Promise.all([adminStore.fetchUsers(), adminStore.fetchOllamaModels()])
    // toastStore.success('All data refreshed successfully')
  } catch (error) {
    toastStore.error('Failed to refresh data: ' + error.message)
  } finally {
    loading.value = false
  }
}

const checkSystemHealth = async () => {
  try {
    // Check backend health
    await api.get('health')

    // Check database health separately
    try {
      const response = await api.get('health/db')
      console.log('Database health check:', response)
    } catch (error) {
      console.warn('Database health check failed:', error)
    }

    // Check Ollama status
    try {
      await adminStore.getOllamaVersion()
      ollamaStatus.value.connected = true
    } catch (error) {
      ollamaStatus.value.connected = false
    }

    // toastStore.success('System health check completed')
  } catch (error) {
    toastStore.error('System health check failed: ' + error.message)
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-white">System Information</h2>
      <p class="mt-1 text-zinc-400">System status and configuration overview</p>
    </div>

    <!-- System Stats Grid -->
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      <!-- Total Users -->
      <div class="p-6 rounded-lg bg-zinc-800">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg
              class="w-8 h-8 text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              ></path>
            </svg>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-white">{{ systemStats.totalUsers }}</h3>
            <p class="text-sm text-zinc-400">Total Users</p>
          </div>
        </div>
      </div>
      <!-- Active Users -->
      <div class="p-6 rounded-lg bg-zinc-800">
        <div class="flex items-center">
          <div class="relative flex-shrink-0">
            <svg
              class="w-8 h-8 text-green-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
            <!-- Ping animation for active status -->
            <span
              class="absolute top-0 right-0 block w-3 h-3 bg-green-400 rounded-full animate-ping"
            ></span>
            <span class="absolute top-0 right-0 block w-3 h-3 bg-green-400 rounded-full"></span>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-white">{{ systemStats.activeUsers }}</h3>
            <p class="text-sm text-zinc-400">Active Users</p>
          </div>
        </div>
      </div>

      <!-- Total Models -->
      <div class="p-6 rounded-lg bg-zinc-800">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg
              class="w-8 h-8 text-purple-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
              ></path>
            </svg>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-white">{{ systemStats.totalModels }}</h3>
            <p class="text-sm text-zinc-400">Installed Models</p>
          </div>
        </div>
      </div>

      <!-- Admin Users -->
      <div class="p-6 rounded-lg bg-zinc-800">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              ></path>
            </svg>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-white">{{ systemStats.adminUsers }}</h3>
            <p class="text-sm text-zinc-400">Admin Users</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Status -->
    <div class="p-6 rounded-lg bg-zinc-800">
      <h3 class="mb-4 text-lg font-semibold text-white">Service Status</h3>
      <div class="space-y-4">
        <!-- Backend API -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="relative">
              <div class="w-3 h-3 bg-green-400 rounded-full"></div>
              <div
                class="absolute top-0 left-0 w-3 h-3 bg-green-400 rounded-full animate-ping"
              ></div>
            </div>
            <span class="text-white">Backend API</span>
          </div>
          <span class="text-sm text-green-400">Online</span>
        </div>

        <!-- Database -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="relative">
              <div class="w-3 h-3 bg-green-400 rounded-full"></div>
              <div
                class="absolute top-0 left-0 w-3 h-3 bg-green-400 rounded-full animate-ping"
              ></div>
            </div>
            <span class="text-white">Database</span>
          </div>
          <span class="text-sm text-green-400">Connected</span>
        </div>

        <!-- Ollama Service -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="relative">
              <div
                :class="ollamaStatus.connected ? 'bg-green-400' : 'bg-red-400'"
                class="w-3 h-3 rounded-full"
              ></div>
              <div
                v-if="ollamaStatus.connected"
                :class="ollamaStatus.connected ? 'bg-green-400' : 'bg-red-400'"
                class="absolute top-0 left-0 w-3 h-3 rounded-full animate-ping"
              ></div>
            </div>
            <span class="text-white">Ollama Service</span>
          </div>
          <span :class="ollamaStatus.connected ? 'text-green-400' : 'text-red-400'" class="text-sm">
            {{ ollamaStatus.connected ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="p-6 rounded-lg bg-zinc-800">
      <h3 class="mb-4 text-lg font-semibold text-white">Recent User Activity</h3>
      <div class="space-y-3">
        <div
          v-for="user in recentUsers"
          :key="user.id"
          class="flex items-center justify-between py-2"
        >
          <div class="flex items-center space-x-3">
            <div
              class="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
            >
              <span class="text-xs font-medium text-white">{{ getUserInitials(user) }}</span>
            </div>
            <div>
              <p class="text-sm text-white">{{ user.username }}</p>
              <p class="text-xs text-zinc-400">{{ user.email }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-xs text-zinc-400">Last login</p>
            <p class="text-sm text-white">{{ formatDate(user.last_login) }}</p>
          </div>
        </div>
        <div v-if="!recentUsers.length" class="py-4 text-center text-zinc-400">
          No recent activity
        </div>
      </div>
    </div>

    <!-- System Configuration -->
    <div class="p-6 rounded-lg bg-zinc-800">
      <h3 class="mb-4 text-lg font-semibold text-white">Configuration</h3>
      <div class="space-y-3">
        <div class="flex justify-between">
          <span class="text-zinc-400">Environment</span>
          <span class="text-white">{{ systemConfig.environment }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-zinc-400">API Version</span>
          <span class="text-white">{{ systemConfig.apiVersion }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-zinc-400">Ollama URL</span>
          <span class="text-white">{{ systemConfig.ollamaUrl }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-zinc-400">Rate Limiting</span>
          <span class="text-green-400">Enabled</span>
        </div>
        <div class="flex justify-between">
          <span class="text-zinc-400">CORS</span>
          <span class="text-green-400">Configured</span>
        </div>
      </div>
    </div>

    <!-- Admin Actions -->
    <div class="p-6 rounded-lg bg-zinc-800">
      <h3 class="mb-4 text-lg font-semibold text-white">Admin Actions</h3>
      <div class="grid gap-4 md:grid-cols-2">
        <button
          @click="refreshAllData"
          :disabled="loading"
          class="flex items-center px-4 py-3 space-x-2 text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <svg
            v-if="!loading"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            ></path>
          </svg>
          <div
            v-else
            class="w-5 h-5 border-2 border-white rounded-full border-t-transparent animate-spin"
          ></div>
          <span>Refresh All Data</span>
        </button>

        <button
          @click="checkSystemHealth"
          class="flex items-center px-4 py-3 space-x-2 text-white transition-colors bg-green-600 rounded-lg hover:bg-green-700"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <span>Check System Health</span>
        </button>
      </div>
    </div>
  </div>
</template>
