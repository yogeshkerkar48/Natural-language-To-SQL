<template>
  <div class="result-display" v-if="result">
    <div class="card result-card">
      <div class="header">
        <h3>Generated SQL</h3>
        <div class="validation-badge" :class="result.is_valid ? 'valid' : 'invalid'">
          {{ result.is_valid ? '✓ Valid SQL' : '✗ Invalid SQL' }}
        </div>
        <div v-if="result.from_cache" class="cache-badge" :title="'Matched with: ' + result.original_question">
          🚀 Instant Result ({{ (result.cache_similarity * 100).toFixed(0) }}% match)
        </div>
      </div>

      <pre class="code-block"><code>{{ result.sql }}</code></pre>
      
      <p v-if="!result.is_valid" class="error-msg">⚠️ {{ result.message }}</p>

      <div class="actions" v-if="result.is_valid">
        <button @click="copySQL" class="btn secondary">
          {{ copied ? '✓ Copied!' : '📋 Copy SQL' }}
        </button>
        <button @click="getSuggestions" :disabled="loadingSuggestions" class="btn optimization">
          <span v-if="loadingSuggestions" class="spinner small"></span>
          {{ loadingSuggestions ? 'Analyzing...' : '⚡ Suggest Index Optimization' }}
        </button>
      </div>

      <!-- Index Suggestions Section -->
      <div v-if="suggestions" class="suggestions-container">
        <div class="suggestions-header">
          <span class="icon">🔍</span>
          <h4>Index Suggestions</h4>
        </div>
        <p class="summary">{{ suggestions.summary }}</p>
        
        <div v-if="suggestions.suggestions.length > 0" class="suggestions-list">
          <div v-for="(sug, idx) in suggestions.suggestions" :key="idx" class="suggestion-item">
            <div class="sug-header">
              <span class="sug-type">{{ sug.index_type }}</span>
              <span class="sug-table">{{ sug.table }}</span>
            </div>
            <div class="sug-columns">
              <span v-for="col in sug.columns" :key="col" class="col-pill">{{ col }}</span>
            </div>
            <p class="sug-rationale">{{ sug.rationale }}</p>
            <div class="sug-sql-wrapper">
              <pre class="sug-sql"><code>{{ sug.sql }}</code></pre>
              <button @click="copyIndexSQL(sug.sql, idx)" class="btn-copy-sm">
                {{ indexCopied === idx ? '✓' : '📋' }}
              </button>
            </div>
          </div>
        </div>
        <div v-else-if="!loadingSuggestions" class="no-suggestions">
          No indexing optimizations recommended for this query.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';

const props = defineProps({
  result: {
    type: Object, // { sql, is_valid, message, tables, databaseType, suggestions }
    default: null
  }
});

const emit = defineEmits(['suggestions-fetched']);

const copied = ref(false);
const loadingSuggestions = ref(false);
const suggestions = ref(null);
const indexCopied = ref(null);

import { watch } from 'vue';
watch(() => props.result, (newVal) => {
  if (newVal && newVal.suggestions) {
    suggestions.value = newVal.suggestions;
  } else {
    suggestions.value = null;
  }
}, { immediate: true });

const copySQL = () => {
  if (props.result && props.result.sql) {
    navigator.clipboard.writeText(props.result.sql);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  }
};

const copyIndexSQL = (sql, idx) => {
  navigator.clipboard.writeText(sql);
  indexCopied.value = idx;
  setTimeout(() => {
    indexCopied.value = null;
  }, 2000);
};

const getSuggestions = async () => {
  if (!props.result || !props.result.tables) return;
  
  loadingSuggestions.value = true;
  suggestions.value = null;
  
  try {
    const response = await api.suggestIndexes(
      props.result.sql,
      props.result.tables,
      props.result.databaseType
    );
    suggestions.value = response.data;
    emit('suggestions-fetched', response.data);
  } catch (error) {
    console.error('Failed to get index suggestions:', error);
    alert('Index suggestion failed');
  } finally {
    loadingSuggestions.value = false;
  }
};
</script>

<style scoped>
.result-display {
  margin-top: 24px;
}

.card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.1rem;
}

.code-block {
  background: #1e293b;
  color: #e2e8f0;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
  margin: 12px 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

.validation-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
}

.valid { 
  background: #d1fae5; 
  color: #065f46; 
}

.invalid { 
  background: #fee2e2; 
  color: #991b1b; 
}

.cache-badge {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  color: #1d4ed8;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid #bfdbfe;
  cursor: help;
  display: flex;
  align-items: center;
  gap: 4px;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-msg { 
  color: #dc2626; 
  margin-top: 10px;
  padding: 12px;
  background: #fef2f2;
  border-radius: 6px;
  border-left: 4px solid #dc2626;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  background: white;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn.secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn.optimization {
  background: #eff6ff;
  color: #2563eb;
  border-color: #bfdbfe;
}

.btn.optimization:hover:not(:disabled) {
  background: #dbeafe;
  border-color: #93c5fd;
}

/* Suggestions UI */
.suggestions-container {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.suggestions-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.suggestions-header h4 {
  margin: 0;
  color: #334155;
  font-size: 1rem;
}

.summary {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 16px;
  font-style: italic;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.sug-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.sug-type {
  background: #334155;
  color: white;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 700;
}

.sug-table {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.9rem;
}

.sug-columns {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.col-pill {
  background: #e2e8f0;
  color: #475569;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  font-family: 'Fira Code', monospace;
}

.sug-rationale {
  font-size: 0.85rem;
  color: #475569;
  line-height: 1.5;
  margin: 0 0 10px 0;
}

.sug-sql-wrapper {
  position: relative;
  background: #1e293b;
  border-radius: 6px;
  overflow: hidden;
}

.sug-sql {
  margin: 0;
  padding: 12px;
  color: #10b981;
  font-size: 0.85rem;
  font-family: 'Fira Code', monospace;
  overflow-x: auto;
}

.btn-copy-sm {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #94a3b8;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
  transition: all 0.2s;
}

.btn-copy-sm:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.no-suggestions {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 0.9rem;
  background: #f8fafc;
  border-radius: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0,0,0,0.1);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
