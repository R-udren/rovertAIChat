// Toast notification store
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  let idCounter = 0

  const addToast = ({ message, type = 'info', duration = 3000, position = 'bottom-right' }) => {
    const id = idCounter++

    const toast = {
      id,
      message,
      type,
      duration,
      position,
    }

    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex((toast) => toast.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (message, options = {}) => {
    return addToast({
      message,
      type: 'success',
      ...options,
    })
  }

  const error = (message, options = {}) => {
    return addToast({
      message,
      type: 'error',
      ...options,
    })
  }

  const info = (message, options = {}) => {
    return addToast({
      message,
      type: 'info',
      ...options,
    })
  }

  const warning = (message, options = {}) => {
    return addToast({
      message,
      type: 'warning',
      ...options,
    })
  }

  const clearAll = () => {
    toasts.value = []
  }

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    info,
    warning,
    clearAll,
  }
})
