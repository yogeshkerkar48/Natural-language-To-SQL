<template>
  <div v-if="history.length > 0" class="query-history">
    <div class="history-label">
      <span class="icon">🕒</span> Recent Questions:
    </div>
    <div class="history-list">
      <div 
        v-for="item in history" 
        :key="item.id" 
        class="history-item-wrapper"
      >
        <button 
          @click="$emit('select', item.question)"
          class="history-pill"
          :title="item.question"
        >
          {{ truncate(item.question) }}
        </button>
        <button 
          @click="deleteItem(item.id)" 
          class="delete-btn"
          title="Remove from history"
        >×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, defineExpose } from 'vue';
import api from '../services/api';

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  }
});

const history = ref([]);

const fetchHistory = async () => {
  try {
    const response = await api.getQueryHistory(props.projectId);
    history.value = response.data;
  } catch (error) {
    console.error('Failed to fetch history:', error);
  }
};

const deleteItem = async (id) => {
  if (!confirm('Remove this question from history?')) return;
  try {
    await api.deleteQueryHistory(id);
    // Remove from local list immediately
    history.value = history.value.filter(item => item.id !== id);
  } catch (error) {
    console.error('Failed to delete history item:', error);
  }
};

const truncate = (text) => {
  return text.length > 40 ? text.substring(0, 37) + '...' : text;
};

watch(() => props.projectId, () => {
  fetchHistory();
});

onMounted(fetchHistory);

defineExpose({
  refresh: fetchHistory
});

defineEmits(['select']);
</script>

<style scoped>
.query-history {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 4px;
}

.history-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 80px;
  overflow-y: auto;
  padding: 4px;
}

.history-item-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.history-pill {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 4px 24px 4px 12px; /* Extra padding right for delete button */
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.history-pill:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
  color: #1e293b;
  transform: translateY(-1px);
}

.history-pill:active {
  transform: translateY(0);
}

.delete-btn {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  opacity: 0;
  transition: all 0.2s;
}

.history-item-wrapper:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* Custom Scrollbar for history list */
.history-list::-webkit-scrollbar {
  width: 4px;
}

.history-list::-webkit-scrollbar-track {
  background: transparent;
}

.history-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
</style>
