<template>
  <div class="space-y-6">
    <!-- Header with Actions -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-white">User Management</h2>
        <p class="text-zinc-400 mt-1">Manage system users and their permissions</p>
      </div>
      <button
        @click="refreshUsers"
        :disabled="adminStore.loading"
        class="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
      >
        <svg
          v-if="!adminStore.loading"
          class="w-4 h-4"
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
          class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
        ></div>
        <span>Refresh</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="adminStore.loading && !users.length" class="flex justify-center py-12">
      <div class="text-center">
        <div
          class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"
        ></div>
        <p class="text-zinc-400">Loading users...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="adminStore.error" class="bg-red-900/20 border border-red-500 rounded-lg p-4">
      <div class="flex items-center space-x-3">
        <svg
          class="w-5 h-5 text-red-400 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
        <div>
          <h3 class="text-red-400 font-medium">Error loading users</h3>
          <p class="text-red-300 text-sm">{{ adminStore.error }}</p>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div v-else-if="users.length" class="bg-zinc-800 rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-zinc-700">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider"
              >
                User
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider"
              >
                Role
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider"
              >
                Created
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider"
              >
                Last Login
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium text-zinc-300 uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-700">
            <tr v-for="user in users" :key="user.id" class="hover:bg-zinc-750 transition-colors">
              <!-- User Info -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div
                      class="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center"
                    >
                      <span class="text-sm font-medium text-white">{{
                        getUserInitials(user)
                      }}</span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-white">{{ user.username }}</div>
                    <div class="text-sm text-zinc-400">{{ user.email }}</div>
                  </div>
                </div>
              </td>

              <!-- Role -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="{
                    'bg-red-100 text-red-800': user.role === 'admin',
                    'bg-blue-100 text-blue-800': user.role === 'user',
                    'bg-gray-100 text-gray-800': user.role === 'guest',
                  }"
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                >
                  {{ user.role.charAt(0).toUpperCase() + user.role.slice(1) }}
                </span>
              </td>

              <!-- Status -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="{
                    'bg-green-100 text-green-800': user.is_active,
                    'bg-red-100 text-red-800': !user.is_active,
                  }"
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                >
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>

              <!-- Created -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-zinc-400">
                {{ formatDate(user.created_at) }}
              </td>

              <!-- Last Login -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-zinc-400">
                {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
              </td>

              <!-- Actions -->
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <!-- Edit User Button -->
                  <button
                    @click="editUser(user)"
                    class="text-blue-400 hover:text-blue-300 transition-colors"
                    title="Edit User"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      ></path>
                    </svg>
                  </button>

                  <!-- Activate/Deactivate Button -->
                  <button
                    v-if="user.id !== authStore.user?.id"
                    @click="user.is_active ? deactivateUser(user) : activateUser(user)"
                    :class="{
                      'text-red-400 hover:text-red-300': user.is_active,
                      'text-green-400 hover:text-green-300': !user.is_active,
                    }"
                    class="transition-colors"
                    :title="user.is_active ? 'Deactivate User' : 'Activate User'"
                  >
                    <svg
                      v-if="user.is_active"
                      class="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"
                      ></path>
                    </svg>
                    <svg
                      v-else
                      class="w-4 h-4"
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
                  </button>

                  <!-- View Settings Button -->
                  <button
                    @click="viewUserSettings(user)"
                    class="text-zinc-400 hover:text-zinc-300 transition-colors"
                    title="View Settings"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                      ></path>
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      ></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <svg
        class="mx-auto h-12 w-12 text-zinc-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
        ></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-zinc-300">No users found</h3>
      <p class="mt-1 text-sm text-zinc-400">No users have been registered yet.</p>
    </div>

    <!-- Edit User Modal -->
    <EditUserModal
      v-if="editingUser"
      :user="editingUser"
      @close="editingUser = null"
      @updated="handleUserUpdated"
    />

    <!-- User Settings Modal -->
    <UserSettingsModal
      v-if="viewingUserSettings"
      :user="viewingUserSettings"
      @close="viewingUserSettings = null"
    />
  </div>
</template>

<script setup>
import EditUserModal from '@/components/EditUserModal.vue'
import UserSettingsModal from '@/components/UserSettingsModal.vue'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { computed, onMounted, ref } from 'vue'

const adminStore = useAdminStore()
const authStore = useAuthStore()
const toastStore = useToastStore()

const editingUser = ref(null)
const viewingUserSettings = ref(null)

const users = computed(() => adminStore.users)

// Utility functions
const getUserInitials = (user) => {
  return (user.username.charAt(0) + (user.username.charAt(1) || '')).toUpperCase()
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// User management functions
const refreshUsers = async () => {
  try {
    await adminStore.fetchUsers()
    toastStore.success('Users refreshed successfully')
  } catch (error) {
    toastStore.error('Failed to refresh users: ' + error.message)
  }
}

const editUser = (user) => {
  editingUser.value = { ...user }
}

const deactivateUser = async (user) => {
  if (user.id === authStore.user?.id) {
    toastStore.error('You cannot deactivate your own account')
    return
  }

  if (confirm(`Are you sure you want to deactivate ${user.username}?`)) {
    try {
      await adminStore.deactivateUser(user.id)
      toastStore.success(`User ${user.username} deactivated successfully`)
    } catch (error) {
      toastStore.error('Failed to deactivate user: ' + error.message)
    }
  }
}

const activateUser = async (user) => {
  try {
    await adminStore.activateUser(user.id)
    toastStore.success(`User ${user.username} activated successfully`)
  } catch (error) {
    toastStore.error('Failed to activate user: ' + error.message)
  }
}

const viewUserSettings = (user) => {
  viewingUserSettings.value = user
}

const handleUserUpdated = (updatedUser) => {
  editingUser.value = null
  toastStore.success(`User ${updatedUser.username} updated successfully`)
}

// Load users on component mount
onMounted(() => {
  refreshUsers()
})
</script>
