<template>
  <div class="flex items-center justify-center min-h-[calc(100vh-64px)]">
    <div class="text-center">
      <h1 class="mb-2 text-6xl font-bold text-indigo-500">404</h1>
      <h2 class="mb-4 text-2xl font-medium text-white">Page Not Found</h2>
      <p class="mb-6 text-gray-400">The page you're looking for doesn't exist or has been moved.</p>
      <router-link
        to="/"
        class="px-6 py-2 font-medium text-white transition-colors duration-200 bg-indigo-600 rounded-md hover:bg-indigo-700"
      >
        Return Home
      </router-link>
    </div>
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div
        class="absolute rounded-full -top-40 -right-40 w-80 h-80 bg-purple-500/10 blur-3xl animate-pulse-subtle"
      ></div>
      <div
        class="absolute rounded-full -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 blur-3xl animate-pulse-subtle"
        style="animation-delay: 1s"
      ></div>
      <div
        class="absolute w-64 h-64 rounded-full top-1/8 left-1/3 bg-pink-500/5 blur-3xl animate-pulse-subtle"
        style="animation-delay: 2s"
      ></div>
    </div>
  </div>
</template>
