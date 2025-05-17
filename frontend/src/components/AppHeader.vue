<template>
  <header class="bg-zinc-900 shadow-md">
    <div class="container mx-auto px-4 py-3 flex items-center justify-between">
      <h1 class="text-xl font-medium text-white">My Application</h1>
      <nav class="flex space-x-6">
        <router-link
          to="/"
          class="text text-gray-300 hover:text-white transition-colors duration-200"
          active-class="text-white border-b border-indigo-500 pb-1"
        >
          Home
        </router-link>
        <router-link
          to="/about"
          class="text text-gray-300 hover:text-white transition-colors duration-200"
          active-class="text-white border-b border-indigo-500 pb-1"
        >
          About
        </router-link>
      </nav>
    </div>
  </header>
</template>
