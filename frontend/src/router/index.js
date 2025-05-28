import HomeView from '@/views/HomeView.vue'
import { createRouter, createWebHistory } from 'vue-router'

// Import the auth store (without using useAuthStore to avoid circular dependency)
// We'll use it inside beforeEach guard
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
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

// Navigation guards
router.beforeEach((to, _from, next) => {
  // Get auth store and isAuthenticated state
  const authStore = useAuthStore()
  const { isAuthenticated, user } = storeToRefs(authStore)

  // Check for protected routes
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Check for admin-only routes
  if (to.meta.requiresAdmin && (!isAuthenticated.value || user.value?.role !== 'admin')) {
    return next({ name: 'home' })
  }

  // Check for guest-only routes (like login, register)
  if (to.meta.requiresGuest && isAuthenticated.value) {
    return next({ name: 'home' })
  }

  // Otherwise proceed normally
  next()
})

export default router
