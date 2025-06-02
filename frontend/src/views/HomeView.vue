<script setup>
import { useAuthStore } from '@/stores/auth'

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
  <div class="min-h-[calc(100vh-64px)] bg-zinc-900 relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div
        class="absolute rounded-full -top-40 -right-40 w-80 h-80 bg-purple-500/20 blur-3xl animate-pulse-subtle"
      ></div>
      <div
        class="absolute rounded-full -bottom-40 -left-40 w-80 h-80 bg-blue-500/20 blur-3xl animate-pulse-subtle"
        style="animation-delay: 1s"
      ></div>
      <div
        class="absolute transform -translate-x-1/2 -translate-y-1/2 rounded-full top-1/2 left-1/2 w-96 h-96 bg-purple-400/10 blur-3xl animate-pulse-subtle"
        style="animation-delay: 2s"
      ></div>
    </div>

    <div class="container relative px-4 py-16 mx-auto">
      <!-- Hero Section -->
      <div class="max-w-4xl mx-auto text-center animate-fade-in">
        <div class="mb-6">
          <h1 class="mb-4 text-4xl font-bold text-white md:text-7xl lg:text-8xl xl:text-9xl">
            Welcome to <span class="text-gradient-3">rovertChat</span>
          </h1>
        </div>

        <p class="mb-4 text-xl text-gray-300 md:text-2xl">
          Your <span class="font-semibold text-gradient-2">self-hosted privacy-focused</span> AI
          platform ✨
        </p>

        <p class="max-w-2xl mx-auto mb-8 text-lg text-gray-400">
          Complete control over your AI interactions with seamless integration to Ollama and
          OpenAI-compatible APIs. No data leaves your infrastructure.
        </p>

        <!-- Feature badges -->
        <div class="flex flex-wrap justify-center gap-3 mb-8">
          <span class="px-3 py-1 text-sm font-medium text-white rounded-full bg-gradient"
            >🔒 Self-Hosted</span
          >
          <span class="px-3 py-1 text-sm font-medium text-white rounded-full bg-gradient-2"
            >⚡ Real-time</span
          >
          <span class="px-3 py-1 text-sm font-medium text-white rounded-full bg-gradient"
            >🎯 Multi-Model</span
          >
          <span class="px-3 py-1 text-sm font-medium text-white rounded-full bg-gradient-3"
            >👥 Multi-User</span
          >
        </div>

        <div class="mb-16">
          <button
            @click="goToChat"
            class="px-12 py-4 text-lg font-semibold text-white transition-all duration-300 rounded-lg shadow-2xl bg-gradient-2 hover:-translate-y-2 hover:shadow-purple-500/25 group"
          >
            <span class="flex items-center gap-2">
              {{ authStore.isAuthenticated ? 'Go to Chat' : 'Get Started' }}
              <svg
                class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                ></path>
              </svg>
            </span>
          </button>
        </div>

        <!-- Core Features Grid -->
        <div class="grid grid-cols-1 gap-8 mb-16 md:grid-cols-3">
          <div
            class="p-8 transition-all duration-300 shadow-lg rounded-xl bg-zinc-800/50 backdrop-blur-sm hover:-translate-y-2 hover:shadow-2xl hover:shadow-purple-500/10 animate-slide-in-left"
          >
            <div
              class="flex items-center justify-center w-16 h-16 mx-auto mb-6 rounded-full bg-gradient-3"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-8 h-8 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <h3 class="mb-4 text-2xl font-semibold text-white">Smart Conversations</h3>
            <p class="leading-relaxed text-gray-400">
              Have natural, flowing conversations with advanced AI models. Supports multiple LLM
              backends including Ollama and OpenAI-compatible APIs.
            </p>
          </div>

          <div
            class="p-8 transition-all duration-300 shadow-lg rounded-xl bg-zinc-800/50 backdrop-blur-sm hover:-translate-y-2 hover:shadow-2xl hover:shadow-blue-500/10 animate-slide-up"
            style="animation-delay: 0.2s"
          >
            <div
              class="flex items-center justify-center w-16 h-16 mx-auto mb-6 rounded-full bg-gradient"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-8 h-8 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
            <h3 class="mb-4 text-2xl font-semibold text-white">Privacy First</h3>
            <p class="leading-relaxed text-gray-400">
              Complete data control with self-hosted infrastructure. Your conversations never leave
              your servers, ensuring maximum privacy and security.
            </p>
          </div>

          <div
            class="p-8 transition-all duration-300 shadow-lg rounded-xl bg-zinc-800/50 backdrop-blur-sm hover:-translate-y-2 hover:shadow-2xl hover:shadow-pink-500/10 animate-slide-in-right"
            style="animation-delay: 0.4s"
          >
            <div
              class="flex items-center justify-center w-16 h-16 mx-auto mb-6 rounded-full bg-gradient-2"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-8 h-8 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
            </div>
            <h3 class="mb-4 text-2xl font-semibold text-white">Multi-User Support</h3>
            <p class="leading-relaxed text-gray-400">
              Role-based access control with guest, user, and admin roles. Persistent chat history
              and personalized settings for each user.
            </p>
          </div>
        </div>

        <!-- Technical Highlights -->
        <div class="max-w-4xl mx-auto mb-16">
          <h2 class="mb-8 text-3xl font-bold text-center text-white">
            Built with <span class="text-gradient">Modern Technology</span>
          </h2>
          <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div class="p-6 rounded-lg glass-effect">
              <h4 class="mb-3 text-lg font-semibold text-white">Backend Power</h4>
              <div class="flex flex-wrap justify-center gap-2">
                <span class="px-3 py-1 text-sm text-blue-200 rounded-full bg-blue-500/20"
                  >Python</span
                >
                <span class="px-3 py-1 text-sm text-green-200 rounded-full bg-green-500/20"
                  >FastAPI</span
                >
                <span class="px-3 py-1 text-sm text-purple-200 rounded-full bg-purple-500/20"
                  >Socket.IO</span
                >
                <span class="px-3 py-1 text-sm text-indigo-200 rounded-full bg-indigo-500/20"
                  >PostgreSQL</span
                >
              </div>
            </div>
            <div class="p-6 rounded-lg glass-effect">
              <h4 class="mb-3 text-lg font-semibold text-white">Frontend Excellence</h4>
              <div class="flex flex-wrap justify-center gap-2">
                <span class="px-3 py-1 text-sm rounded-full bg-emerald-500/20 text-emerald-200"
                  >Vue.js</span
                >
                <span class="px-3 py-1 text-sm rounded-full bg-cyan-500/20 text-cyan-200"
                  >TailwindCSS 4</span
                >
                <span class="px-3 py-1 text-sm text-orange-200 rounded-full bg-orange-500/20"
                  >Bun</span
                >
                <span class="px-3 py-1 text-sm text-yellow-200 rounded-full bg-yellow-500/20"
                  >Markdown</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Coming Soon Features -->
        <div class="max-w-4xl mx-auto mb-16">
          <h2 class="mb-8 text-3xl font-bold text-center text-white">
            <span class="text-gradient-2">Coming Soon</span> ✨
          </h2>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div class="p-4 text-center rounded-lg bg-zinc-800/30 backdrop-blur-sm">
              <div class="mb-2 text-2xl">🎤</div>
              <h4 class="mb-2 font-semibold text-white">Voice Chat</h4>
              <p class="text-sm text-gray-400">Real-time speech-to-text and text-to-speech</p>
            </div>
            <div class="p-4 text-center rounded-lg bg-zinc-800/30 backdrop-blur-sm">
              <div class="mb-2 text-2xl">🎨</div>
              <h4 class="mb-2 font-semibold text-white">Image Generation</h4>
              <p class="text-sm text-gray-400">Create images using text prompts</p>
            </div>
            <div class="p-4 text-center rounded-lg bg-zinc-800/30 backdrop-blur-sm">
              <div class="mb-2 text-2xl">📊</div>
              <h4 class="mb-2 font-semibold text-white">Mermaid Diagrams</h4>
              <p class="text-sm text-gray-400">Visualize diagrams directly in chat</p>
            </div>
            <div class="p-4 text-center rounded-lg bg-zinc-800/30 backdrop-blur-sm">
              <div class="mb-2 text-2xl">⚡</div>
              <h4 class="mb-2 font-semibold text-white">Function Calling</h4>
              <p class="text-sm text-gray-400">Execute external functions through chat</p>
            </div>
            <div class="p-4 text-center rounded-lg bg-zinc-800/30 backdrop-blur-sm">
              <div class="mb-2 text-2xl">✍️</div>
              <h4 class="mb-2 font-semibold text-white">Advanced Markdown</h4>
              <p class="text-sm text-gray-400">Real-time rendering and code highlighting</p>
            </div>
            <div class="p-4 text-center rounded-lg bg-zinc-800/30 backdrop-blur-sm">
              <div class="mb-2 text-2xl">🐳</div>
              <h4 class="mb-2 font-semibold text-white">Docker Deploy</h4>
              <p class="text-sm text-gray-400">Simple containerized deployment</p>
            </div>
          </div>
        </div>

        <!-- User Roles Section -->
        <div class="max-w-4xl mx-auto mb-16">
          <h2 class="mb-8 text-3xl font-bold text-center text-white">
            Choose Your <span class="text-gradient">Experience</span>
          </h2>
          <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
            <div
              class="p-6 text-center transition-all duration-300 rounded-xl bg-zinc-800/50 hover:bg-zinc-800/70"
            >
              <div
                class="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-gray-500/20"
              >
                <span class="text-2xl">👤</span>
              </div>
              <h3 class="mb-2 text-xl font-semibold text-white">Guest</h3>
              <p class="text-gray-400">Quick access for limited sessions</p>
            </div>
            <div
              class="p-6 text-center transition-all duration-300 border rounded-xl bg-zinc-800/50 hover:bg-zinc-800/70 border-blue-500/30"
            >
              <div
                class="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-blue-500/20"
              >
                <span class="text-2xl">👥</span>
              </div>
              <h3 class="mb-2 text-xl font-semibold text-white">User</h3>
              <p class="text-gray-400">Persistent history & personalized settings</p>
            </div>
            <div
              class="p-6 text-center transition-all duration-300 border rounded-xl bg-zinc-800/50 hover:bg-zinc-800/70 border-purple-500/30"
            >
              <div
                class="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-purple-500/20"
              >
                <span class="text-2xl">👑</span>
              </div>
              <h3 class="mb-2 text-xl font-semibold text-white">Admin</h3>
              <p class="text-gray-400">Full system control & user management</p>
            </div>
          </div>
        </div>
        <!-- Call to Action -->
        <div class="text-center">
          <div class="max-w-2xl p-8 mx-auto rounded-2xl glass-effect">
            <h2 class="mb-4 text-2xl font-bold text-white">
              Ready to take control of your AI conversations?
            </h2>
            <p class="mb-6 text-gray-400">
              Join the privacy-focused AI revolution with rovertChat. Your data, your rules, your
              infrastructure.
            </p>
            <div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <button
                @click="goToChat"
                class="px-8 py-3 font-semibold text-white transition-all duration-300 rounded-lg bg-gradient hover:scale-105 hover:shadow-lg hover:shadow-blue-500/25"
              >
                {{ authStore.isAuthenticated ? 'Continue Chatting' : 'Start Your Journey' }}
              </button>
              <a
                href="https://github.com/R-udren/rovertAIChat"
                target="_blank"
                rel="noopener noreferrer"
                class="flex items-center justify-center gap-2 px-6 py-3 text-gray-300 transition-all duration-300 border border-gray-600 rounded-lg hover:border-purple-500 hover:text-white hover:shadow-lg hover:shadow-purple-500/20"
              >
                <svg
                  class="transition-transform size-5 group-hover:scale-110"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
                  />
                </svg>
                Star on GitHub ⭐
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
