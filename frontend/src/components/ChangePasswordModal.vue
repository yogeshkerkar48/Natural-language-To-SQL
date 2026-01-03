<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-content card shadow">
      <div class="modal-header">
        <h3><span class="icon">🔐</span> Change Password</h3>
        <button @click="close" class="close-btn">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-form">
        <div v-if="error" class="error-banner">
          {{ error }}
        </div>
        <div v-if="success" class="success-banner">
          {{ success }}
        </div>

        <div class="form-group">
          <label for="old-password">Current Password</label>
          <input
            id="old-password"
            v-model="oldPassword"
            type="password"
            placeholder="Enter current password"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="new-password">New Password</label>
          <input
            id="new-password"
            v-model="newPassword"
            type="password"
            placeholder="Min 6 characters"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="confirm-password">Confirm New Password</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            placeholder="Repeat new password"
            required
            :disabled="loading"
          />
        </div>

        <div class="modal-actions">
          <button type="button" @click="close" class="btn secondary" :disabled="loading">Cancel</button>
          <button type="submit" class="btn accent" :disabled="loading || !isValid">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Updating...' : 'Update Password' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import authService from '../services/authService';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close', 'success']);

const oldPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const error = ref('');
const success = ref('');

const isValid = computed(() => {
  return (
    oldPassword.value &&
    newPassword.value.length >= 6 &&
    newPassword.value === confirmPassword.value
  );
});

const close = () => {
  if (loading.value) return;
  // Reset form
  oldPassword.value = '';
  newPassword.value = '';
  confirmPassword.value = '';
  error.value = '';
  success.value = '';
  emit('close');
};

const handleSubmit = async () => {
  if (!isValid.value) return;
  
  loading.value = true;
  error.value = '';
  success.value = '';

  try {
    await authService.changePassword({
      old_password: oldPassword.value,
      new_password: newPassword.value
    });
    
    success.value = 'Password updated successfully! Closing...';
    emit('success');
    
    // Auto-close after success
    setTimeout(() => {
      close();
    }, 2000);
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update password. Please check your old password.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

.modal-content {
  width: 100%;
  max-width: 450px;
  background: white;
  padding: 32px;
  animation: slideUp 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #ef4444;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #475569;
  font-size: 0.9rem;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

.error-banner {
  background: #fef2f2;
  color: #ef4444;
  padding: 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  border: 1px solid #fee2e2;
}

.success-banner {
  background: #f0fdf4;
  color: #22c55e;
  padding: 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  border: 1px solid #dcfce7;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
