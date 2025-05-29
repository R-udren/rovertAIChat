<template>
  <div class="min-h-screen pt-20 bg-zinc-900">
    <div class="container px-4 py-8 mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="mb-2 text-3xl font-bold text-white">Admin Panel</h1>
        <p class="text-zinc-400">Manage users and Ollama models</p>
      </div>

      <!-- Access Denied for Non-Admins -->
      <div v-if="!adminStore.isAdmin()" class="p-6 border border-red-500 rounded-lg bg-red-900/20">
        <div class="flex items-center space-x-3">
          <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 19.5c-.77.833.192 2.5 1.732 2.5z"
            ></path>
          </svg>
          <div>
            <h3 class="font-semibold text-red-400">Access Denied</h3>
            <p class="text-red-300">You need administrator privileges to access this panel.</p>
          </div>
        </div>
      </div>

      <!-- Admin Panel Content -->
      <div v-else>
        <!-- Tab Navigation -->
        <div class="mb-8 border-b border-zinc-700">
          <nav class="flex -mb-px space-x-8">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="{
                'border-blue-500 text-blue-400': activeTab === tab.id,
                'border-transparent text-zinc-400 hover:text-zinc-300 hover:border-zinc-300':
                  activeTab !== tab.id,
              }"
              class="px-1 py-4 text-sm font-medium transition-colors border-b-2 whitespace-nowrap"
            >
              <div class="flex items-center space-x-2">
                <component :is="tab.icon" class="w-5 h-5" />
                <span>{{ tab.name }}</span>
              </div>
            </button>
          </nav>
        </div>
        <!-- Tab Content -->
        <div class="space-y-6">
          <!-- User Management Tab -->
          <div v-show="activeTab === 'users'">
            <AdminUserManagement :active="activeTab === 'users'" />
          </div>

          <!-- Model Management Tab -->
          <div v-show="activeTab === 'models'">
            <AdminModelManagement :active="activeTab === 'models'" />
          </div>

          <!-- System Info Tab -->
          <div v-show="activeTab === 'system'">
            <AdminSystemInfo :active="activeTab === 'system'" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AdminModelManagement from '@/components/AdminModelManagement.vue'
import AdminSystemInfo from '@/components/AdminSystemInfo.vue'
import AdminUserManagement from '@/components/AdminUserManagement.vue'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { onMounted, ref } from 'vue'

// Icons (inline SVG components)
const UsersIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
    </svg>
  `,
}

const CpuIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
    </svg>
  `,
}

const CogIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
    </svg>
  `,
}

const adminStore = useAdminStore()
const authStore = useAuthStore()
const toastStore = useToastStore()

const activeTab = ref('users')

const tabs = [
  { id: 'users', name: 'User Management', icon: UsersIcon },
  { id: 'models', name: 'Model Management', icon: CpuIcon },
  { id: 'system', name: 'System Info', icon: CogIcon },
]

onMounted(() => {
  // Check if user is admin and redirect if not
  if (!adminStore.isAdmin()) {
    toastStore.error('Admin access required')
  }
})
</script>
