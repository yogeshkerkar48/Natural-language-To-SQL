<template>
  <div class="relationship-builder">
    <div class="header">
      <h3><span class="icon">🔗</span> Define Relationships</h3>
      <button @click="addRelationship" class="btn-primary-sm">+ Add Relationship</button>
    </div>

    <div v-if="relationships.length === 0" class="empty-state">
      <p>No relationships defined.</p>
      <p class="sub-text">Define relationships to help the AI understand how tables connect.</p>
    </div>

    <div v-else class="relationships-list">
      <div v-for="(rel, index) in relationships" :key="index" class="rel-card">
        <!-- Edit Mode -->
        <template v-if="rel.isEditing">
          <div class="rel-row">
            <!-- FROM -->
            <div class="rel-group">
              <span class="label">From</span>
              <select v-model="rel.from_table" class="table-select">
                <option value="" disabled>Select Table</option>
                <option v-for="t in tables" :key="t.name" :value="t.name">{{ t.name }}</option>
              </select>
              <select v-model="rel.from_column" class="col-select" :disabled="!rel.from_table">
                <option value="" disabled>Column</option>
                <option v-for="col in getColumns(rel.from_table)" :key="col.name" :value="col.name">
                  {{ col.name }}
                </option>
              </select>
            </div>

            <div class="arrow">→</div>

            <!-- TO -->
            <div class="rel-group">
              <span class="label">To</span>
              <select v-model="rel.to_table" class="table-select">
                <option value="" disabled>Select Table</option>
                <option v-for="t in tables" :key="t.name" :value="t.name">{{ t.name }}</option>
              </select>
              <select v-model="rel.to_column" class="col-select" :disabled="!rel.to_table">
                <option value="" disabled>Column</option>
                <option v-for="col in getColumns(rel.to_table)" :key="col.name" :value="col.name">
                  {{ col.name }}
                </option>
              </select>
            </div>

            <div class="action-buttons">
              <button @click="saveRelationship(index)" class="btn-save" title="Save Relationship">💾</button>
              <button @click="removeRelationship(index)" class="btn-danger-icon" title="Remove Relationship">×</button>
            </div>
          </div>
          <div v-if="rel.validationError" class="error-message">{{ rel.validationError }}</div>
        </template>

        <!-- View Mode -->
        <template v-else>
          <div class="rel-row-view">
            <div class="rel-display">
              <span class="rel-text">
                <strong>{{ rel.from_table }}</strong>.{{ rel.from_column }}
                <span class="arrow-view">→</span>
                <strong>{{ rel.to_table }}</strong>.{{ rel.to_column }}
              </span>
            </div>
            <div class="action-buttons">
              <button @click="editRelationship(index)" class="btn-edit" title="Edit Relationship">✏️</button>
              <button @click="removeRelationship(index)" class="btn-danger-icon" title="Remove Relationship">×</button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array,
    required: true
  },
  tables: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const relationships = ref(props.modelValue || []);

watch(() => props.modelValue, (newVal) => {
  relationships.value = newVal.map(r => ({
    ...r,
    isEditing: r.isEditing !== undefined ? r.isEditing : true,
    validationError: r.validationError || null
  }));
}, { deep: true });

const update = () => {
  emit('update:modelValue', relationships.value);
};

const validateRelationship = (rel) => {
  if (!rel.from_table || !rel.from_column || !rel.to_table || !rel.to_column) {
    return 'All fields are required';
  }
  return null;
};

const saveRelationship = (index) => {
  const rel = relationships.value[index];
  const error = validateRelationship(rel);
  
  if (error) {
    rel.validationError = error;
    return;
  }
  
  rel.validationError = null;
  rel.isEditing = false;
  update();
};

const editRelationship = (index) => {
  relationships.value[index].isEditing = true;
  relationships.value[index].validationError = null;
  update();
};

const addRelationship = () => {
  relationships.value.push({
    from_table: '',
    from_column: '',
    to_table: '',
    to_column: '',
    isEditing: true,
    validationError: null
  });
  update();
};

const removeRelationship = (index) => {
  relationships.value.splice(index, 1);
  update();
};

const getColumns = (tableName) => {
  const table = props.tables.find(t => t.name === tableName);
  return table ? table.columns : [];
};
</script>

<style scoped>
.relationship-builder {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  gap: 0.5rem;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px dashed #e5e7eb;
  color: #6b7280;
}

.sub-text {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.relationships-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rel-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
}

/* Edit Mode */
.rel-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.rel-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.label {
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 700;
  color: #94a3b8;
  margin-right: 0.25rem;
}

.table-select, .col-select {
  padding: 0.35rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 0.9rem;
  min-width: 120px;
}

.col-select {
  min-width: 100px;
  color: #475569;
}

.arrow {
  color: #64748b;
  font-weight: bold;
  font-size: 1.2rem;
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fee2e2;
  border-radius: 4px;
}

/* View Mode */
.rel-row-view {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.rel-display {
  flex: 1;
  background: white;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.rel-text {
  font-size: 0.95rem;
  color: #334155;
}

.rel-text strong {
  color: #1e293b;
  font-weight: 600;
}

.arrow-view {
  color: #3b82f6;
  font-weight: bold;
  margin: 0 0.5rem;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-left: auto;
}

.btn-primary-sm {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary-sm:hover {
  background: #1d4ed8;
}

.btn-save {
  background: #10b981;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.btn-save:hover {
  background: #059669;
}

.btn-edit {
  background: #f59e0b;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.btn-edit:hover {
  background: #d97706;
}

.btn-danger-icon {
  background: #fee2e2;
  color: #ef4444;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.btn-danger-icon:hover {
  background: #fecaca;
}
</style>
