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
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import UserMenu from './components/UserMenu.vue';
import authService from './services/authService';

const route = useRoute();
const router = useRouter();

// Use reactive state from authService
const authState = authService.state;

const isAuthenticated = computed(() => {
  return authState.isAuthenticated && route.path !== '/login' && route.path !== '/register';
});

// --- Inactivity Timeout Logic ---
const TIMEOUT_DURATION = 30 * 60 * 1000; // 30 minutes in milliseconds
let logoutTimer = null;

const resetTimer = () => {
  if (logoutTimer) clearTimeout(logoutTimer);
  
  // Only set timer if user is authenticated
  if (authState.isAuthenticated) {
    logoutTimer = setTimeout(() => {
      handleAutoLogout();
    }, TIMEOUT_DURATION);
  }
};

const handleAutoLogout = () => {
  console.log('User inactive for 30 minutes. Logging out...');
  authService.logout();
  router.push('/login');
  alert('You have been logged out due to inactivity.');
};

const activityEvents = ['mousemove', 'mousedown', 'keydown', 'scroll', 'click', 'touchstart'];

const setupActivityListeners = () => {
  activityEvents.forEach(event => {
    window.addEventListener(event, resetTimer);
  });
};

const cleanupActivityListeners = () => {
  activityEvents.forEach(event => {
    window.removeEventListener(event, resetTimer);
  });
};
// ---------------------------------

// Load user on mount and setup activity tracking
onMounted(() => {
  if (authService.getToken()) {
    authService.getCurrentUser();
  }
  
  setupActivityListeners();
  resetTimer();
});

onUnmounted(() => {
  cleanupActivityListeners();
  if (logoutTimer) clearTimeout(logoutTimer);
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
