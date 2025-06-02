// Composable for handling sidebar state
import { ref } from 'vue'

export function useSidebar() {
  const showSidebar = ref(
    localStorage.getItem('sidebarVisible') !== null
      ? localStorage.getItem('sidebarVisible') === 'true'
      : window.innerWidth >= 1024,
  )
  const isMobileSidebarOpen = ref(false)

  // Toggle sidebar
  const toggleSidebar = () => {
    showSidebar.value = !showSidebar.value
    localStorage.setItem('sidebarVisible', showSidebar.value.toString())
  }

  // Toggle mobile sidebar
  const toggleMobileSidebar = () => {
    isMobileSidebarOpen.value = !isMobileSidebarOpen.value
  }

  const closeMobileSidebar = () => {
    if (isMobileSidebarOpen.value) {
      isMobileSidebarOpen.value = false
    }
  }

  const closeMobileSidebarWithDelay = () => {
    if (isMobileSidebarOpen.value) {
      setTimeout(() => {
        isMobileSidebarOpen.value = false
      }, 150)
    }
  }

  return {
    showSidebar,
    isMobileSidebarOpen,
    toggleSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
    closeMobileSidebarWithDelay,
  }
}
