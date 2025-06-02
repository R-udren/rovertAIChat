import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
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
  // Get auth store inside the guard when Pinia is available
  const authStore = useAuthStore()

  // Check for protected routes
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.warn('Access denied to protected route:', to.fullPath)
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Check for admin-only routes
  if (to.meta.requiresAdmin && (!authStore.isAuthenticated || authStore.user?.role !== 'admin')) {
    console.warn('Access denied to admin route:', to.fullPath)
    return next({ name: 'home' })
  }

  // Check for guest-only routes (like login, register)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    console.warn('Access denied to guest route:', to.fullPath)
    return next({ name: 'home' })
  }

  // Otherwise proceed normally
  next()
})
export default router
