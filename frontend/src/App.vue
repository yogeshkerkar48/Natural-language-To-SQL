<template>
  <div id="app">
    <!-- Show header only when authenticated -->
    <header v-if="isAuthenticated" class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <h1>NL2SQL Generator</h1>
          <p>Convert Natural Language to SQL Queries</p>
        </div>
        <UserMenu :user="authState.user" />
      </div>
    </header>

    <!-- Router view for different pages -->
    <router-view />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import UserMenu from './components/UserMenu.vue';
import authService from './services/authService';

const route = useRoute();

// Use reactive state from authService
const authState = authService.state;

const isAuthenticated = computed(() => {
  return authState.isAuthenticated && route.path !== '/login' && route.path !== '/register';
});

// Load user on mount if authenticated (to verify token)
onMounted(() => {
  if (authService.getToken()) {
    authService.getCurrentUser();
  }
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  background: #f8f9fa;
}

.app-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 20px 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section h1 {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 4px;
}

.logo-section p {
  font-size: 0.85rem;
  color: #666;
}
</style>
