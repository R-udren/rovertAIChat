<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Edit User</h3>
        <button @click="closeModal" class="text-gray-500 hover:text-gray-700">
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

      <form @submit.prevent="updateUser" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <input
            id="username"
            v-model="editForm.username"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.username }"
          />
          <p v-if="errors.username" class="text-red-500 text-sm mt-1">{{ errors.username }}</p>
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1"> Email </label>
          <input
            id="email"
            v-model="editForm.email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.email }"
          />
          <p v-if="errors.email" class="text-red-500 text-sm mt-1">{{ errors.email }}</p>
        </div>

        <div>
          <label for="role" class="block text-sm font-medium text-gray-700 mb-1"> Role </label>
          <select
            id="role"
            v-model="editForm.role"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div class="flex items-center">
          <input
            id="is_active"
            v-model="editForm.is_active"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="is_active" class="ml-2 block text-sm text-gray-700"> Active User </label>
        </div>

        <div class="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ loading ? 'Updating...' : 'Update User' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'
import { reactive, ref, watch } from 'vue'

export default {
  name: 'EditUserModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false,
    },
    user: {
      type: Object,
      default: null,
    },
  },
  emits: ['close', 'updated'],
  setup(props, { emit }) {
    const adminStore = useAdminStore()
    const toastStore = useToastStore()

    const loading = ref(false)
    const errors = reactive({})

    const editForm = reactive({
      username: '',
      email: '',
      role: 'user',
      is_active: true,
    })

    const resetForm = () => {
      Object.assign(errors, {})
      if (props.user) {
        editForm.username = props.user.username || ''
        editForm.email = props.user.email || ''
        editForm.role = props.user.role || 'user'
        editForm.is_active = props.user.is_active !== false
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

      return Object.keys(errors).length === 0
    }

    const updateUser = async () => {
      if (!validateForm()) return

      loading.value = true
      try {
        await adminStore.updateUser(props.user.id, {
          username: editForm.username,
          email: editForm.email,
          role: editForm.role,
          is_active: editForm.is_active,
        })

        toastStore.addToast('User updated successfully', 'success')
        emit('updated')
        closeModal()
      } catch (error) {
        toastStore.addToast(error.message || 'Failed to update user', 'error')
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      emit('close')
    }

    watch(
      () => props.isOpen,
      (newValue) => {
        if (newValue) {
          resetForm()
        }
      },
    )

    watch(
      () => props.user,
      () => {
        if (props.isOpen) {
          resetForm()
        }
      },
    )

    return {
      loading,
      errors,
      editForm,
      updateUser,
      closeModal,
    }
  },
}
</script>
