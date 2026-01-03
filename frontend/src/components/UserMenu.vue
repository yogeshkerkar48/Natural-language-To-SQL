<template>
  <div class="user-menu">
    <div class="user-info" @click="toggleMenu">
      <div class="user-avatar">{{ userInitial }}</div>
      <span class="username">{{ username }}</span>
      <svg class="dropdown-icon" :class="{ open: isOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M2 4L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </div>

    <transition name="dropdown">
      <div v-if="isOpen" class="dropdown-menu">
        <div class="menu-item user-details">
          <div class="detail-label">Email</div>
          <div class="detail-value">{{ email }}</div>
        </div>
        <div class="menu-divider"></div>
        <button class="menu-item password-btn" @click="showPasswordModal = true">
          <span class="icon">🔐</span>
          Change Password
        </button>
        <div class="menu-divider"></div>
        <button class="menu-item logout-btn" @click="handleLogout">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 14H3C2.44772 14 2 13.5523 2 13V3C2 2.44772 2.44772 2 3 2H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M11 11L14 8M14 8L11 5M14 8H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Logout
        </button>
      </div>
    </transition>

    <ChangePasswordModal 
      :is-open="showPasswordModal" 
      @close="showPasswordModal = false"
      @success="onPasswordSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, toRefs } from 'vue';
import { useRouter } from 'vue-router';
import authService from '../services/authService';
import ChangePasswordModal from './ChangePasswordModal.vue';

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
});

const router = useRouter();
const isOpen = ref(false);
const showPasswordModal = ref(false);
const localUser = ref(null);

const displayUser = computed(() => props.user || localUser.value);
const username = computed(() => displayUser.value?.username || displayUser.value?.email?.split('@')[0] || 'User');
const email = computed(() => displayUser.value?.email || '');
const userInitial = computed(() => (username.value ? username.value.charAt(0).toUpperCase() : 'U'));

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const closeMenu = () => {
  isOpen.value = false;
};

const handleLogout = () => {
  authService.logout();
  router.push('/login');
};

const onPasswordSuccess = () => {
  isOpen.value = false; // Close menu
};

// Load user from localStorage if not provided via prop
onMounted(() => {
  if (!props.user) {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      localUser.value = JSON.parse(storedUser);
    }
  }
  
  // Close menu when clicking outside
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const handleClickOutside = (event) => {
  const menu = event.target.closest('.user-menu');
  if (!menu) {
    closeMenu();
  }
};
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: #f3f4f6; /* Visible light gray background */
  border-radius: 20px; /* Pill shape */
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
}

.user-info:hover {
  background: #e5e7eb;
  transform: translateY(-1px);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.username {
  font-weight: 500;
  color: #333;
  font-size: 0.95rem;
}

.dropdown-icon {
  transition: transform 0.3s ease;
  color: #666;
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  min-width: 220px;
  overflow: hidden;
  z-index: 1000;
}

.menu-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.menu-item:hover:not(.user-details) {
  background: #f5f5f5;
}

.user-details {
  cursor: default;
  background: #fafafa;
}

.detail-label {
  font-size: 0.75rem;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 0.9rem;
  color: #333;
  word-break: break-all;
}

.menu-divider {
  height: 1px;
  background: #e0e0e0;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  border: none;
  background: none;
  color: #c33;
  font-weight: 500;
  font-size: 0.9rem;
}

.logout-btn:hover {
  background: #fee !important;
}

.password-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  border: none;
  background: none;
  color: #3b82f6;
  font-weight: 500;
  font-size: 0.9rem;
}

.password-btn:hover {
  background: #eff6ff !important;
}

.password-btn .icon {
  font-size: 1.1rem;
}

.logout-btn svg {
  stroke: currentColor;
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
