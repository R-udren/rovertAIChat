<script setup>
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  user: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'updated'])

const adminStore = useAdminStore()
const toastStore = useToastStore()

const loading = ref(false)
const errors = reactive({})

const editForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true,
})

const isCreating = computed(() => !props.user)

const resetForm = () => {
  Object.assign(errors, {})
  if (props.user) {
    // Editing existing user - populate with current values
    editForm.username = props.user.username || ''
    editForm.email = props.user.email || ''
    editForm.role = props.user.role || 'user'
    editForm.is_active = props.user.is_active !== false
    editForm.password = '' // Don't show password for existing users
  } else {
    // Creating new user - use empty defaults
    editForm.username = ''
    editForm.email = ''
    editForm.password = ''
    editForm.role = 'user'
    editForm.is_active = true
  }
}

const validateForm = () => {
  Object.assign(errors, {})

  if (!editForm.username.trim()) {
    errors.username = 'Username is required'
  } else if (editForm.username.length < 3) {
    errors.username = 'Username must be at least 3 characters'
  }

  if (!editForm.email.trim()) {
    errors.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editForm.email)) {
    errors.email = 'Please enter a valid email address'
  }

  // Password validation only for new users
  if (isCreating.value) {
    if (!editForm.password.trim()) {
      errors.password = 'Password is required'
    } else if (editForm.password.length < 6) {
      errors.password = 'Password must be at least 6 characters'
    }
  }

  return Object.keys(errors).length === 0
}

const submitForm = async () => {
  if (!validateForm()) return

  loading.value = true
  try {
    if (isCreating.value) {
      // Creating new user
      await adminStore.createUser({
        username: editForm.username,
        email: editForm.email,
        password: editForm.password,
        role: editForm.role,
        is_active: editForm.is_active,
      })
      toastStore.addToast('User created successfully', 'success')
    } else {
      // Updating existing user
      await adminStore.updateUser(props.user.id, {
        username: editForm.username,
        email: editForm.email,
        role: editForm.role,
        is_active: editForm.is_active,
      })
      toastStore.addToast('User updated successfully', 'success')
    }

    emit('updated')
    closeModal()
  } catch (error) {
    toastStore.addToast(error.message || 'Failed to save user', 'error')
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  emit('close')
}

// Improved reactive form reset when modal opens or user changes
watch(
  () => [props.isOpen, props.user],
  ([isOpen, user]) => {
    if (isOpen) {
      resetForm()
    }
  },
  { immediate: true },
)
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-zinc-900/80">
    <div class="w-full max-w-md p-6 mx-4 border rounded-lg bg-zinc-800 border-zinc-700">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">
          {{ isCreating ? 'Create User' : 'Edit User' }}
        </h3>
        <button @click="closeModal" class="transition-colors text-zinc-400 hover:text-white">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>
      <form @submit.prevent="submitForm" class="space-y-4">
        <div>
          <label for="username" class="block mb-1 text-sm font-medium text-zinc-300">
            Username
          </label>
          <input
            id="username"
            v-model="editForm.username"
            type="text"
            required
            :placeholder="isCreating ? 'Enter username' : props.user?.username"
            class="w-full px-3 py-2 text-white border rounded-md bg-zinc-700 border-zinc-600 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :class="{ 'border-red-500': errors.username }"
          />
          <p v-if="errors.username" class="mt-1 text-sm text-red-400">{{ errors.username }}</p>
        </div>

        <div>
          <label for="email" class="block mb-1 text-sm font-medium text-zinc-300">Email</label>
          <input
            id="email"
            v-model="editForm.email"
            type="email"
            required
            :placeholder="isCreating ? 'Enter email address' : props.user?.email"
            class="w-full px-3 py-2 text-white border rounded-md bg-zinc-700 border-zinc-600 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :class="{ 'border-red-500': errors.email }"
          />
          <p v-if="errors.email" class="mt-1 text-sm text-red-400">{{ errors.email }}</p>
        </div>

        <!-- Password field for new users -->
        <div v-if="isCreating">
          <label for="password" class="block mb-1 text-sm font-medium text-zinc-300">
            Password
          </label>
          <input
            id="password"
            v-model="editForm.password"
            type="password"
            required
            placeholder="Enter password (min 6 characters)"
            class="w-full px-3 py-2 text-white border rounded-md bg-zinc-700 border-zinc-600 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :class="{ 'border-red-500': errors.password }"
          />
          <p v-if="errors.password" class="mt-1 text-sm text-red-400">{{ errors.password }}</p>
        </div>

        <div>
          <label for="role" class="block mb-1 text-sm font-medium text-zinc-300">Role</label>
          <div class="relative">
            <select
              id="role"
              v-model="editForm.role"
              class="w-full px-3 py-2 text-white border rounded-md appearance-none cursor-pointer bg-zinc-700 border-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.role }"
            >
              <option value="user" class="text-white bg-zinc-700">User</option>
              <option value="admin" class="text-white bg-zinc-700">Admin</option>
            </select>
            <!-- Custom dropdown arrow -->
            <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
              <svg
                class="w-4 h-4 text-zinc-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                ></path>
              </svg>
            </div>
          </div>
          <p v-if="!isCreating" class="mt-1 text-xs text-zinc-400">
            Current role: {{ user?.role || 'N/A' }}
          </p>
        </div>

        <div class="flex items-center space-x-3">
          <div class="relative">
            <input
              id="is_active"
              v-model="editForm.is_active"
              type="checkbox"
              class="w-4 h-4 text-blue-600 rounded cursor-pointer bg-zinc-700 border-zinc-600 focus:ring-blue-500 focus:ring-2"
            />
          </div>
          <label for="is_active" class="text-sm cursor-pointer text-zinc-300">Active User</label>
          <span v-if="!isCreating" class="text-xs text-zinc-400">
            (Currently: {{ user?.is_active ? 'Active' : 'Inactive' }})
          </span>
        </div>

        <div class="flex justify-end pt-4 space-x-3">
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 text-sm font-medium transition-colors border rounded-lg text-zinc-300 bg-zinc-700 border-zinc-600 hover:bg-zinc-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="flex items-center px-4 py-2 space-x-2 text-sm font-medium text-white transition-colors bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div
              v-if="loading"
              class="w-4 h-4 border-2 border-white rounded-full border-t-transparent animate-spin"
            ></div>
            <span>
              {{
                loading
                  ? isCreating
                    ? 'Creating...'
                    : 'Updating...'
                  : isCreating
                    ? 'Create User'
                    : 'Update User'
              }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
