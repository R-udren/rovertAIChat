<script setup>
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()
const isMobileMenuOpen = ref(false)
const lastScrollPosition = ref(0)
const showHeader = ref(true)
const showLogoutModal = ref(false)

const handleLogout = async () => {
  showLogoutModal.value = true
}

const confirmLogout = async () => {
  showLogoutModal.value = false
  isMobileMenuOpen.value = false
  await authStore.logout()
  router.push('/login')
  toastStore.info('Logged out successfully')
}

const cancelLogout = () => {
  showLogoutModal.value = false
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
const navLinks = computed(() => {
  const links = [
    { name: 'Home', path: '/', requiresAuth: false },
    { name: 'Chat', path: '/chat', requiresAuth: true },
    { name: 'Profile', path: '/profile', requiresAuth: true },
    { name: 'Settings', path: '/settings', requiresAuth: true },
  ]

  // Add admin panel link for admin users
  if (authStore.isAuthenticated && authStore.user?.role === 'admin') {
    links.splice(-1, 0, {
      name: 'Admin Panel',
      path: '/admin',
      requiresAuth: true,
      requiresAdmin: true,
    })
  }

  return links
})

const handleNavigation = (path) => {
  router.push(path)
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
    class="fixed top-0 left-0 right-0 z-50 transition-transform duration-300 backdrop-blur-lg bg-zinc-900"
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
            v-if="
              (!link.requiresAuth || authStore.isAuthenticated) &&
              (!link.requiresAdmin || authStore.user?.role === 'admin')
            "
            :to="link.path"
            class="relative px-1 py-1 text-gray-300 transition-all duration-200 hover:text-white group"
            active-class="text-indigo-400"
          >
            {{ link.name }}
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-indigo-500 transition-all duration-300 group-hover:w-full"
            ></span>
            <span
              class="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-500 opacity-0 transition-opacity duration-300"
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
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-indigo-500 transition-all duration-300 group-hover:w-full"
            ></span>
          </button>
        </template>

        <template v-else>
          <router-link
            to="/login"
            class="relative px-1 py-1 text-gray-300 transition-all duration-200 hover:text-white group"
            active-class="text-indigo-400"
          >
            Login
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-indigo-500 transition-all duration-300 group-hover:w-full"
            ></span>
            <span
              class="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-500 opacity-0 transition-opacity duration-300"
              :class="{ 'opacity-100': $route.path === '/login' }"
            ></span>
          </router-link>
          <router-link
            to="/register"
            class="px-4 py-2 text-white transition-all duration-200 rounded-lg shadow-md bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 active:scale-95"
          >
            Register
          </router-link>
        </template>

        <!-- GitHub Link -->
        <a
          href="https://github.com/R-udren/rovertAIChat"
          target="_blank"
          rel="noopener noreferrer"
          class="p-2 text-gray-300 transition-all duration-200 rounded-lg hover:text-white hover:bg-zinc-800/50 group"
          aria-label="View on GitHub"
        >
          <svg
            class="w-5 h-5 transition-transform group-hover:scale-110"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
            />
          </svg>
        </a>
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
      class="fixed inset-0 md:hidden animate-fade-in"
      @click="closeMobileMenu"
    >
      <!-- Mobile Navigation Menu -->
      <div
        class="fixed right-0 overflow-y-auto transition-transform duration-300 rounded-lg rounded-b-lg shadow-lg top-12 md:hidden bg-zinc-900/80 backdrop-blur-xl"
        :class="isMobileMenuOpen ? 'translate-y-0 animate-slide-up' : 'translate-y-full'"
      >
        <nav class="flex flex-col px-6 py-8 space-y-6">
          <template v-for="link in navLinks" :key="link.path">
            <button
              v-if="
                (!link.requiresAuth || authStore.isAuthenticated) &&
                (!link.requiresAdmin || authStore.user?.role === 'admin')
              "
              @click="handleNavigation(link.path)"
              class="flex items-center justify-between py-3 text-lg font-medium text-left transition-colors duration-200"
              :class="
                $route.path === link.path
                  ? 'text-indigo-400 hover:text-indigo-600'
                  : 'text-gray-300 hover:text-white'
              "
            >
              {{ link.name }}
              <svg
                v-if="$route.path === link.path"
                xmlns="http://www.w3.org/2000/svg"
                class="w-6 h-6 text-indigo-500"
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
              class="flex items-center justify-between pt-3 text-lg font-medium text-left text-gray-400 transition-colors duration-200 group hover:text-white"
            >
              Logout
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="size-6">
                <path
                  fill="currentColor"
                  class="text-gray-400 transition-colors duration-200 group-hover:text-gray-300"
                  d="M3 2.75C3 1.784 3.784 1 4.75 1h6.5c.966 0 1.75.784 1.75 1.75v3.457A5.5 5.5 0 0 0 7.257 15H4.75A1.75 1.75 0 0 1 3 13.25zM6 9a1 1 0 1 0 0-2a1 1 0 0 0 0 2m5.5 7a4.5 4.5 0 1 0 0-9a4.5 4.5 0 0 0 0 9m.354-2.146a.5.5 0 0 1-.708-.708L12.293 12H9.5a.5.5 0 0 1 0-1h2.793l-1.147-1.146a.5.5 0 0 1 .708-.708l2 2a.5.5 0 0 1 .146.351v.006a.5.5 0 0 1-.144.348l-.003.003z"
                />
              </svg>
            </button>
          </template>

          <template v-else>
            <button
              @click="handleNavigation('/login')"
              class="flex items-center justify-between py-3 text-lg font-medium text-left transition-colors duration-200"
              :class="$route.path === '/login' ? 'text-indigo-400' : 'text-gray-300'"
            >
              Login
              <svg
                v-if="$route.path === '/login'"
                xmlns="http://www.w3.org/2000/svg"
                class="w-5 h-5 text-indigo-500"
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
              class="w-full py-3 text-lg font-medium text-center text-white transition-all duration-200 rounded-lg shadow-md bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800"
            >
              Register
            </button>
          </template>

          <!-- GitHub Link in Mobile -->
          <div class="my-2 border-t border-zinc-700"></div>
          <a
            href="https://github.com/R-udren/rovertAIChat"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center justify-between py-3 text-lg font-medium text-left text-gray-400 transition-colors duration-200 hover:text-white"
            @click="closeMobileMenu"
          >
            GitHub
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path
                d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
              />
            </svg>
          </a>
        </nav>

        <div class="p-6 text-sm text-center text-gray-500 border-t border-zinc-800">
          <p>© {{ new Date().getFullYear() }} rovertAIChat</p>
          <p class="mt-1">
            <a
              href="https://github.com/R-udren/rovertAIChat"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-400 hover:text-gray-300"
            >
              Open Source on GitHub
            </a>
          </p>
        </div>
      </div>
    </div>
  </header>
  <!-- Spacer to compensate for fixed header -->
  <div class="h-16"></div>

  <!-- Logout Confirmation Modal -->
  <ConfirmationModal
    :isOpen="showLogoutModal"
    type="warning"
    title="Confirm Logout"
    message="Are you sure you want to log out? You will need to sign in again to access your account."
    confirmText="Logout"
    cancelText="Stay Logged In"
    @confirm="confirmLogout"
    @cancel="cancelLogout"
    @close="cancelLogout"
  />
</template>
