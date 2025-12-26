<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>📂 Load Project</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="loading" class="list-loading">
          <span class="spinner dark"></span> Loading projects...
        </div>
        <div v-else-if="projects.length === 0" class="empty-state">
          No saved projects found.
        </div>
        <div v-else class="project-list">
          <div 
            v-for="project in projects" 
            :key="project.id" 
            class="project-item"
            @click="emit('load', project.id)"
          >
            <div class="project-info">
              <span class="project-name">{{ project.name }}</span>
              <span class="project-date">{{ formatDate(project.created_at) }}</span>
            </div>
            <button @click.stop="emit('delete', project.id)" class="delete-btn" title="Delete project">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  show: Boolean,
  projects: Array,
  loading: Boolean
});

const emit = defineEmits(['close', 'load', 'delete']);

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 500px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  animation: modal-in 0.3s ease-out;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

@keyframes modal-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: 0;
  overflow-y: auto;
}

.list-loading, .empty-state {
  padding: 40px;
  text-align: center;
  color: #64748b;
}

.project-list {
  display: flex;
  flex-direction: column;
}

.project-item {
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: background 0.2s;
}

.project-item:hover {
  background: #f8fafc;
}

.project-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-name {
  font-weight: 600;
  color: #1e293b;
}

.project-date {
  font-size: 0.75rem;
  color: #94a3b8;
}

.delete-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  opacity: 0;
  transition: all 0.2s;
}

.project-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #fee2e2;
}

.spinner.dark {
  border-color: rgba(30, 41, 59, 0.1);
  border-top-color: #1e293b;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
