<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import ToastContainer from './components/ToastContainer.vue'

const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  await authStore.initialize()
})
</script>

<template>
  <div class="bg-zinc-900 min-h-screen">
    <AppHeader />
    <RouterView />
    <ToastContainer />
  </div>
</template>
