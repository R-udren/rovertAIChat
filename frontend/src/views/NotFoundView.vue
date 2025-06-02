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
  </div>
</template>
