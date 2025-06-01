<script setup>
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  active: {
    type: Boolean,
    default: false,
  },
})

const adminStore = useAdminStore()
const toastStore = useToastStore()

const editingUser = ref(null)
const viewingUserSettings = ref(null)
const showCreateUserModal = ref(false)

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

const viewUserSettings = (user) => {
  viewingUserSettings.value = user
}

const handleUserUpdated = () => {
  editingUser.value = null
  refreshUsers()
}

const handleUserCreated = () => {
  showCreateUserModal.value = false
  refreshUsers()
}

// Load users when component becomes active
watch(
  () => props.active,
  (isActive) => {
    if (isActive && users.value.length === 0) {
      refreshUsers()
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="space-y-6">
    <!-- Header with Actions -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-white">User Management</h2>
        <p class="mt-1 text-zinc-400">Manage system users and their permissions</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="showCreateUserModal = true"
          class="flex items-center px-4 py-2 space-x-2 text-white transition-colors bg-green-600 rounded-lg hover:bg-green-700"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            ></path>
          </svg>
          <span>Create User</span>
        </button>
        <button
          @click="refreshUsers"
          :disabled="adminStore.loading"
          class="flex items-center px-4 py-2 space-x-2 text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
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
            class="w-4 h-4 border-2 border-white rounded-full border-t-transparent animate-spin"
          ></div>
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="adminStore.loading && !users.length" class="flex justify-center py-12">
      <div class="text-center">
        <div
          class="w-8 h-8 mx-auto mb-4 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"
        ></div>
        <p class="text-zinc-400">Loading users...</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="adminStore.usersError"
      class="p-4 border border-red-500 rounded-lg bg-red-900/20"
    >
      <div class="flex items-center space-x-3">
        <svg
          class="flex-shrink-0 w-5 h-5 text-red-400"
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
          <h3 class="font-medium text-red-400">Error loading users</h3>
          <p class="text-sm text-red-300">{{ adminStore.usersError }}</p>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div v-else-if="users.length" class="overflow-hidden rounded-lg bg-zinc-800">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-zinc-700">
            <tr>
              <th
                class="px-6 py-3 text-xs font-medium tracking-wider text-left uppercase text-zinc-300"
              >
                User
              </th>
              <th
                class="px-6 py-3 text-xs font-medium tracking-wider text-left uppercase text-zinc-300"
              >
                Role
              </th>
              <th
                class="px-6 py-3 text-xs font-medium tracking-wider text-left uppercase text-zinc-300"
              >
                Status
              </th>
              <th
                class="px-6 py-3 text-xs font-medium tracking-wider text-left uppercase text-zinc-300"
              >
                Created
              </th>
              <th
                class="px-6 py-3 text-xs font-medium tracking-wider text-left uppercase text-zinc-300"
              >
                Last Login
              </th>
              <th
                class="px-6 py-3 text-xs font-medium tracking-wider text-right uppercase text-zinc-300"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-700">
            <tr v-for="user in users" :key="user.id" class="transition-colors hover:bg-zinc-750">
              <!-- User Info -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-10 h-10">
                    <div
                      class="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
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
                    'bg-yellow-400/10 text-yellow-400': user.role === 'admin',
                    'bg-blue-400/10 text-blue-400': user.role === 'user',
                    'bg-gray-100 text-gray-800': user.role === 'guest',
                  }"
                  class="inline-flex px-2 py-1 text-xs font-semibold border rounded-full"
                >
                  {{ user.role.charAt(0).toUpperCase() + user.role.slice(1) }}
                </span>
              </td>

              <!-- Status -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="{
                    'bg-green-400/10 text-green-400': user.is_active,
                    'bg-red-400/10 text-red-400': !user.is_active,
                  }"
                  class="inline-flex px-2 py-1 text-xs font-semibold border rounded-full"
                >
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>

              <!-- Created -->
              <td class="px-6 py-4 text-sm whitespace-nowrap text-zinc-400">
                {{ formatDate(user.created_at) }}
              </td>

              <!-- Last Login -->
              <td class="px-6 py-4 text-sm whitespace-nowrap text-zinc-400">
                {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
              </td>

              <!-- Actions -->
              <td class="px-6 py-4 text-sm font-medium text-right whitespace-nowrap">
                <div class="flex justify-end space-x-2">
                  <!-- Edit User Button -->
                  <button
                    @click="editUser(user)"
                    class="text-blue-400 transition-colors hover:text-blue-300"
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

                  <!-- View Settings Button -->
                  <button
                    @click="viewUserSettings(user)"
                    class="transition-colors text-zinc-400 hover:text-zinc-300"
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
    <div v-else class="py-12 text-center">
      <svg
        class="w-12 h-12 mx-auto text-zinc-400"
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
      :is-open="!!editingUser"
      @close="editingUser = null"
      @updated="handleUserUpdated"
    />

    <!-- Create User Modal -->
    <EditUserModal
      v-if="showCreateUserModal"
      :user="null"
      :is-open="showCreateUserModal"
      @close="showCreateUserModal = false"
      @updated="handleUserCreated"
    />

    <!-- User Settings Modal -->
    <UserSettingsModal
      v-if="viewingUserSettings"
      :user="viewingUserSettings"
      :is-open="!!viewingUserSettings"
      @close="viewingUserSettings = null"
    />
  </div>
</template>
