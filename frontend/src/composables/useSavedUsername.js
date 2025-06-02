// Simple composable for managing saved username functionality
import { ref, watch } from 'vue'

export function useSavedUsername() {
  const REMEMBER_KEY = 'remember_username'
  const USERNAME_KEY = 'saved_username'

  // Initialize from localStorage
  const rememberUsername = ref(localStorage.getItem(REMEMBER_KEY) === 'true')
  const savedUsername = ref(rememberUsername.value ? localStorage.getItem(USERNAME_KEY) || '' : '')

  // Watch for changes and update localStorage
  watch(rememberUsername, (newValue) => {
    localStorage.setItem(REMEMBER_KEY, newValue)
    if (!newValue) {
      // Clear saved username when turning off
      localStorage.removeItem(USERNAME_KEY)
      savedUsername.value = ''
    }
  })

  // Save username to localStorage
  const saveUsername = (username) => {
    if (rememberUsername.value && username) {
      localStorage.setItem(USERNAME_KEY, username)
      savedUsername.value = username
    }
  }

  // Clear saved username
  const clearUsername = () => {
    localStorage.removeItem(USERNAME_KEY)
    savedUsername.value = ''
  }

  return {
    rememberUsername,
    savedUsername,
    saveUsername,
    clearUsername,
  }
}
