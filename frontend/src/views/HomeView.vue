<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const goToChat = () => {
  if (authStore.isAuthenticated) {
    router.push('/chat')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-64px)] bg-zinc-900">
    <div class="container mx-auto px-4 py-16">
      <div class="text-center max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6">
          Welcome to <span class="text-primary-500">rovertAIChat</span>
        </h1>
        <p class="text-xl text-gray-300 mb-8">
          Your intelligent AI assistant for conversations and answers.
        </p>

        <div class="mb-12">
          <button
            @click="goToChat"
            class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-8 rounded-md transition-colors duration-200 shadow-lg"
          >
            {{ authStore.isAuthenticated ? 'Go to Chat' : 'Get Started' }}
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
          <div class="bg-zinc-800 p-6 rounded-lg shadow-md">
            <div
              class="w-12 h-12 mx-auto mb-4 bg-primary-600 rounded-full flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
            </div>
            <h3 class="text-xl font-medium text-white mb-2">Smart Conversations</h3>
            <p class="text-gray-400">
              Have natural, flowing conversations with our advanced AI assistant.
            </p>
          </div>

          <div class="bg-zinc-800 p-6 rounded-lg shadow-md">
            <div
              class="w-12 h-12 mx-auto mb-4 bg-primary-600 rounded-full flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 class="text-xl font-medium text-white mb-2">Get Answers Fast</h3>
            <p class="text-gray-400">
              Receive accurate, helpful responses to your questions instantly.
            </p>
          </div>

          <div class="bg-zinc-800 p-6 rounded-lg shadow-md">
            <div
              class="w-12 h-12 mx-auto mb-4 bg-primary-600 rounded-full flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <h3 class="text-xl font-medium text-white mb-2">Personalized Settings</h3>
            <p class="text-gray-400">Customize your chat experience to match your preferences.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
