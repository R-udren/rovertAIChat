<template>
  <div class="flex items-center justify-center min-h-[calc(100vh-64px)]">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-primary-500 mb-2">404</h1>
      <h2 class="text-2xl font-medium text-white mb-4">Page Not Found</h2>
      <p class="text-gray-400 mb-6">The page you're looking for doesn't exist or has been moved.</p>
      <router-link
        to="/"
        class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-6 rounded-md transition-colors duration-200"
      >
        Return Home
      </router-link>
    </div>
  </div>
</template>
