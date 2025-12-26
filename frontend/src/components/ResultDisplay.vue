<template>
  <div class="result-display" v-if="result">
    <div class="card result-card">
      <h3>Generated SQL</h3>
      
      <div class="validation-badge" :class="result.is_valid ? 'valid' : 'invalid'">
        {{ result.is_valid ? '✓ Valid SQL' : '✗ Invalid SQL' }}
      </div>

      <pre class="code-block"><code>{{ result.sql }}</code></pre>
      
      <p v-if="!result.is_valid" class="error-msg">⚠️ {{ result.message }}</p>

      <div class="actions" v-if="result.is_valid">
        <button @click="copySQL" class="btn secondary">
          {{ copied ? '✓ Copied!' : '📋 Copy SQL' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  result: {
    type: Object, // { sql, is_valid, message }
    default: null
  }
});

const copied = ref(false);

const copySQL = () => {
  if (props.result && props.result.sql) {
    navigator.clipboard.writeText(props.result.sql);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  }
};
</script>

<style scoped>
.result-display {
  margin-top: 20px;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.code-block {
  background: #1e293b;
  color: #e2e8f0;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
  margin: 15px 0;
}

.validation-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: bold;
  margin-bottom: 10px;
}

.valid { 
  background: #d1fae5; 
  color: #065f46; 
}

.invalid { 
  background: #fee2e2; 
  color: #991b1b; 
}

.error-msg { 
  color: #dc2626; 
  margin-top: 10px;
  padding: 10px;
  background: #fef2f2;
  border-radius: 4px;
  border-left: 4px solid #dc2626;
}

.actions {
  margin-top: 15px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  background: white;
  font-weight: 500;
  transition: all 0.2s;
}

.btn.secondary:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}
</style>
