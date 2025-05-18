<script setup>
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  await authStore.initialize()
})
</script>

<template>
  <div class="min-h-screen bg-zinc-900">
    <AppHeader />
    <RouterView />
    <ToastContainer />
  </div>
</template>
