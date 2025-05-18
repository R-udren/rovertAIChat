<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ToastContainer from './components/ToastContainer.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const router = useRouter()

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
