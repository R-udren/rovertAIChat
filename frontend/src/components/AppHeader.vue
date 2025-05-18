<script setup>
import { useToastStore } from '@/stores/toast'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()
const isMobileMenuOpen = ref(false)
const lastScrollPosition = ref(0)
const showHeader = ref(true)

const handleLogout = async () => {
  isMobileMenuOpen.value = false
  await authStore.logout()
  router.push('/login')
  toastStore.info('Logged out successfully')
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value

  // Prevent scrolling when menu is open
  document.body.style.overflow = isMobileMenuOpen.value ? 'hidden' : ''
}

const closeMobileMenu = () => {
  if (isMobileMenuOpen.value) {
    isMobileMenuOpen.value = false
    document.body.style.overflow = ''
  }
}

// Navigation links with active state management
const navLinks = computed(() => [
  { name: 'Home', path: '/', requiresAuth: false },
  { name: 'Chat', path: '/chat', requiresAuth: true },
  { name: 'Profile', path: '/profile', requiresAuth: true },
  { name: 'Settings', path: '/settings', requiresAuth: true },
])

const handleNavigation = (path) => {
  router.push(path)
  closeMobileMenu()
}

// Handle scroll behavior - hide header on scroll down, show on scroll up
const handleScroll = () => {
  const currentScrollPosition = window.scrollY

  if (currentScrollPosition < 10) {
    showHeader.value = true
    return
  }

  if (currentScrollPosition > lastScrollPosition.value) {
    showHeader.value = false // Scrolling down
  } else {
    showHeader.value = true // Scrolling up
  }

  lastScrollPosition.value = currentScrollPosition
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)

  // Handle escape key for closing menu
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isMobileMenuOpen.value) {
      closeMobileMenu()
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.body.style.overflow = ''
})
</script>

<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 transition-transform duration-300 backdrop-blur-lg"
    :class="[
      'glass-effect border-b border-zinc-800/50 shadow-lg',
      showHeader ? 'translate-y-0' : '-translate-y-full',
    ]"
  >
    <div class="container flex items-center justify-between h-16 px-4 py-3 mx-auto">
      <router-link to="/" class="text-3xl font-bold text-gradient" @click="closeMobileMenu">
        rovertAIChat
      </router-link>

      <!-- Desktop Navigation -->
      <nav class="items-center hidden space-x-6 md:flex">
        <template v-for="link in navLinks" :key="link.path">
          <router-link
            v-if="!link.requiresAuth || authStore.isAuthenticated"
            :to="link.path"
            class="relative px-1 py-1 text-gray-300 transition-all duration-200 hover:text-white group"
            active-class="text-primary-400"
          >
            {{ link.name }}
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-primary-500 transition-all duration-300 group-hover:w-full"
            ></span>
            <span
              class="absolute bottom-0 left-0 w-full h-0.5 bg-primary-500 opacity-0 transition-opacity duration-300"
              :class="{ 'opacity-100': $route.path === link.path }"
            ></span>
          </router-link>
        </template>

        <template v-if="authStore.isAuthenticated">
          <button
            @click="handleLogout"
            class="relative px-1 py-1 text-gray-300 transition-all duration-200 hover:text-white group"
          >
            Logout
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-primary-500 transition-all duration-300 group-hover:w-full"
            ></span>
          </button>
        </template>

        <template v-else>
          <router-link
            to="/login"
            class="relative px-1 py-1 text-gray-300 transition-all duration-200 hover:text-white group"
            active-class="text-primary-400"
          >
            Login
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-primary-500 transition-all duration-300 group-hover:w-full"
            ></span>
            <span
              class="absolute bottom-0 left-0 w-full h-0.5 bg-primary-500 opacity-0 transition-opacity duration-300"
              :class="{ 'opacity-100': $route.path === '/login' }"
            ></span>
          </router-link>
          <router-link
            to="/register"
            class="px-4 py-2 text-white transition-all duration-200 rounded-lg shadow-md bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 active:scale-95"
          >
            Register
          </router-link>
        </template>
      </nav>

      <!-- Mobile Menu Button -->
      <button
        @click="toggleMobileMenu"
        class="flex items-center justify-center w-10 h-10 text-gray-300 transition-colors md:hidden hover:text-white focus:outline-none"
        aria-label="Toggle menu"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-6 h-6"
          :class="{ hidden: isMobileMenuOpen, block: !isMobileMenuOpen }"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-6 h-6"
          :class="{ block: isMobileMenuOpen, hidden: !isMobileMenuOpen }"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- Mobile Navigation Overlay -->
    <div
      v-if="isMobileMenuOpen"
      class="fixed inset-0 z-40 bg-black/80 md:hidden animate-fade-in"
      @click="closeMobileMenu"
    ></div>

    <!-- Mobile Navigation Menu -->
    <div
      class="fixed bottom-0 left-0 right-0 z-40 overflow-y-auto transition-transform duration-300 transform top-16 md:hidden glass-effect backdrop-blur-xl"
      :class="isMobileMenuOpen ? 'translate-y-0 animate-slide-up' : 'translate-y-full'"
    >
      <nav class="flex flex-col px-6 py-8 space-y-6">
        <template v-for="link in navLinks" :key="link.path">
          <button
            v-if="!link.requiresAuth || authStore.isAuthenticated"
            @click="handleNavigation(link.path)"
            class="flex items-center justify-between py-3 text-lg font-medium text-left transition-colors duration-200"
            :class="$route.path === link.path ? 'text-primary-400' : 'text-gray-300'"
          >
            {{ link.name }}
            <svg
              v-if="$route.path === link.path"
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-primary-500"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </template>

        <div class="my-2 border-t border-zinc-700"></div>

        <template v-if="authStore.isAuthenticated">
          <button
            @click="handleLogout"
            class="flex items-center justify-between py-3 text-lg font-medium text-left text-gray-300"
          >
            Logout
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-gray-500"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V4a1 1 0 00-1-1H3zm11.293 9.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L10 10.414V14a1 1 0 102 0v-3.586l1.293 1.293z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </template>

        <template v-else>
          <button
            @click="handleNavigation('/login')"
            class="flex items-center justify-between py-3 text-lg font-medium text-left transition-colors duration-200"
            :class="$route.path === '/login' ? 'text-primary-400' : 'text-gray-300'"
          >
            Login
            <svg
              v-if="$route.path === '/login'"
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-primary-500"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clip-rule="evenodd"
              />
            </svg>
          </button>

          <button
            @click="handleNavigation('/register')"
            class="w-full py-3 text-lg font-medium text-center text-white transition-all duration-200 rounded-lg shadow-md bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800"
          >
            Register
          </button>
        </template>
      </nav>

      <div class="p-6 text-sm text-center text-gray-500 border-t border-zinc-800">
        <p>© {{ new Date().getFullYear() }} rovertAIChat</p>
        <p class="mt-1">All rights reserved</p>
      </div>
    </div>
  </header>

  <!-- Spacer to compensate for fixed header -->
  <div class="h-16"></div>
</template>

<style scoped>
.glass-effect {
  background-color: rgba(24, 24, 27, 0.7);
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
