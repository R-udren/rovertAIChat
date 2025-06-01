<script setup>
import { useToastStore } from '@/stores/toast'
import ToastNotification from './ToastNotification.vue'

const toastStore = useToastStore()
</script>

<template>
  <div>
    <ToastNotification
      v-for="toast in toastStore.toasts"
      :key="toast.id"
      :message="toast.message"
      :type="toast.type"
      :duration="toast.duration"
      :position="toast.position"
      @close="toastStore.removeToast(toast.id)"
    />
  </div>
</template>
