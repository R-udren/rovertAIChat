<script setup>
import AdminModelManagement from '@/components/Admin/AdminModelManagement.vue'
import AdminSystemInfo from '@/components/Admin/AdminSystemInfo.vue'
import AdminUserManagement from '@/components/Admin/AdminUserManagement.vue'
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'

const adminStore = useAdminStore()
const toastStore = useToastStore()

const activeTab = ref('users')

const tabs = [
  { id: 'users', name: 'User Management' },
  { id: 'models', name: 'Model Management' },
  { id: 'system', name: 'System Info' },
]

onMounted(() => {
  // Check if user is admin and redirect if not
  if (!adminStore.isAdmin()) {
    toastStore.error('Admin access required')
  }
})
</script>

<template>
  <div class="min-h-screen pt-8 bg-zinc-900">
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
              <div class="flex items-center space-x-2 group">
                <span class="transition-colors">{{ tab.name }}</span>
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
