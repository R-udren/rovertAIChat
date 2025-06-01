import { createRouter, createWebHistory } from 'vue-router'

// Import the auth store (without using useAuthStore to avoid circular dependency)
// We'll use it inside beforeEach guard

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/chat/:id',
      name: 'chat-detail',
      component: () => import('../views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
    },
  ],
})

// Fast auth check cache to avoid store reactivity overhead
let cachedAuthState = {
  isAuthenticated: localStorage.getItem('user') ? true : false,
  user: null,
  lastCheck: 0,
}

// Update cache from localStorage
const updateAuthCache = () => {
  const now = Date.now()
  // Only update cache every 200ms to avoid excessive checks
  if (now - cachedAuthState.lastCheck < 200) return

  try {
    const userData = localStorage.getItem('user')
    cachedAuthState.isAuthenticated = !!userData
    cachedAuthState.user = userData ? JSON.parse(userData) : null
    cachedAuthState.lastCheck = now
  } catch (err) {
    cachedAuthState.isAuthenticated = false
    cachedAuthState.user = null
    cachedAuthState.lastCheck = now
  }
}

// Navigation guards - optimized for speed
router.beforeEach((to, _from, next) => {
  // Fast auth check using cached state
  updateAuthCache()

  // Check for protected routes
  if (to.meta.requiresAuth && !cachedAuthState.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Check for admin-only routes
  if (
    to.meta.requiresAdmin &&
    (!cachedAuthState.isAuthenticated || cachedAuthState.user?.role !== 'admin')
  ) {
    return next({ name: 'home' })
  }

  // Check for guest-only routes (like login, register)
  if (to.meta.requiresGuest && cachedAuthState.isAuthenticated) {
    return next({ name: 'home' })
  }

  // Otherwise proceed normally - no blocking operations
  next()
})

// Listen for auth state changes to update cache
window.addEventListener('storage', (e) => {
  if (e.key === 'user') {
    updateAuthCache()
  }
})

export default router
