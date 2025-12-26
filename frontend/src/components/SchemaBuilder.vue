<template>
  <div class="schema-builder">
    <div class="header">
      <h3><span class="icon">📋</span> Define Tables</h3>
      <button @click="addTable" class="btn-primary-sm">+ Add Table</button>
    </div>

    <div v-if="tables.length === 0" class="empty-state">
      <p>No tables defined. Click "Add Table" to start building your schema.</p>
    </div>

    <div class="tables-list">
      <div v-for="(table, tIndex) in tables" :key="tIndex" class="table-card">
        <!-- Edit Mode -->
        <template v-if="table.isEditing">
          <div class="table-header">
            <input 
              v-model="table.name" 
              placeholder="Table Name (e.g. students)" 
              class="table-name-input"
              :class="{ 'input-error': table.validationError }"
            />
            <div class="header-actions">
              <button @click="saveTable(tIndex)" class="btn-save" title="Save Table">💾</button>
              <button @click="removeTable(tIndex)" class="btn-danger-icon" title="Remove Table">×</button>
            </div>
          </div>
          <div v-if="table.validationError" class="error-message">{{ table.validationError }}</div>

          <div class="columns-list">
            <div v-for="(col, cIndex) in table.columns" :key="cIndex" class="column-row">
              <input 
                v-model="col.name" 
                placeholder="Column Name" 
                class="col-name-input"
              />
              <select v-model="col.type" class="col-type-select">
                <optgroup label="Numeric">
                  <option value="INT">INT</option>
                  <option value="BIGINT">BIGINT</option>
                  <option value="SMALLINT">SMALLINT</option>
                  <option value="TINYINT">TINYINT</option>
                  <option value="DECIMAL">DECIMAL</option>
                  <option value="FLOAT">FLOAT</option>
                  <option value="DOUBLE">DOUBLE</option>
                </optgroup>
                <optgroup label="String/Text">
                  <option value="VARCHAR">VARCHAR</option>
                  <option value="CHAR">CHAR</option>
                  <option value="TEXT">TEXT</option>
                  <option value="LONGTEXT">LONGTEXT</option>
                  <option value="NVARCHAR">NVARCHAR</option>
                </optgroup>
                <optgroup label="Date/Time">
                  <option value="DATE">DATE</option>
                  <option value="DATETIME">DATETIME</option>
                  <option value="TIMESTAMP">TIMESTAMP</option>
                  <option value="TIME">TIME</option>
                  <option value="YEAR">YEAR</option>
                </optgroup>
                <optgroup label="Others">
                  <option value="BOOLEAN">BOOLEAN</option>
                </optgroup>
              </select>
              <button @click="removeColumn(tIndex, cIndex)" class="btn-danger-icon-sm" title="Remove Column">×</button>
            </div>
            <button @click="addColumn(tIndex)" class="btn-secondary-sm">+ Add Column</button>
          </div>
        </template>

        <!-- View Mode -->
        <template v-else>
          <div class="table-header-view">
            <h4 class="table-name-display">{{ table.name }}</h4>
            <div class="header-actions">
              <button @click="editTable(tIndex)" class="btn-edit" title="Edit Table">✏️</button>
              <button @click="removeTable(tIndex)" class="btn-danger-icon" title="Remove Table">×</button>
            </div>
          </div>

          <div class="columns-view">
            <div v-for="(col, cIndex) in table.columns" :key="cIndex" class="column-view-row">
              <span class="col-name">{{ col.name }}</span>
              <span class="col-type-badge">{{ col.type }}</span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

// Local copy of tables to mutate
const tables = ref(props.modelValue || []);

watch(() => props.modelValue, (newVal) => {
  tables.value = newVal.map(t => ({
    ...t,
    isEditing: t.isEditing !== undefined ? t.isEditing : true,
    validationError: t.validationError || null
  }));
}, { deep: true });

const update = () => {
  emit('update:modelValue', tables.value);
};

const validateTableName = (name) => {
  const regex = /^[a-zA-Z][a-zA-Z_]*[a-zA-Z]$|^[a-zA-Z]$/;
  if (!name || name.trim() === '') {
    return 'Table name is required';
  }
  if (!regex.test(name)) {
    return 'Invalid table name. Must start and end with a letter (a-z, A-Z). Underscores (_) allowed between letters.';
  }
  return null;
};

const saveTable = (index) => {
  const table = tables.value[index];
  const error = validateTableName(table.name);
  
  if (error) {
    table.validationError = error;
    return;
  }
  
  table.validationError = null;
  table.isEditing = false;
  update();
};

const editTable = (index) => {
  tables.value[index].isEditing = true;
  tables.value[index].validationError = null;
  update();
};

const addTable = () => {
  tables.value.push({
    name: '',
    columns: [{ name: 'id', type: 'INT' }],
    isEditing: true,
    validationError: null
  });
  update();
};

const removeTable = (index) => {
  tables.value.splice(index, 1);
  update();
};

const addColumn = (tableIndex) => {
  tables.value[tableIndex].columns.push({ name: '', type: 'VARCHAR' });
  update();
};

const removeColumn = (tableIndex, colIndex) => {
  tables.value[tableIndex].columns.splice(colIndex, 1);
  update();
};
</script>

<style scoped>
.schema-builder {
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px dashed #e5e7eb;
  color: #6b7280;
}

.tables-list {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.table-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s;
}

.table-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
}

/* Edit Mode */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.table-name-input {
  font-weight: 600;
  font-size: 1.1rem;
  border: none;
  background: transparent;
  flex: 1;
  color: #1e293b;
  padding: 0.25rem;
}

.table-name-input:focus {
  outline: none;
  border-bottom: 2px solid #3b82f6;
}

.input-error {
  border-bottom: 2px solid #ef4444 !important;
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: #fee2e2;
  border-radius: 4px;
}

/* View Mode */
.table-header-view {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #3b82f6;
}

.table-name-display {
  font-weight: 700;
  font-size: 1.2rem;
  color: #1e293b;
  margin: 0;
}

.columns-view {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.column-view-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.col-name {
  font-weight: 500;
  color: #334155;
}

.col-type-badge {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Edit Mode Columns */
.columns-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.column-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.col-name-input {
  flex: 1;
  padding: 0.35rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.9rem;
}

.col-type-select {
  width: 100px;
  padding: 0.35rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.85rem;
  background: white;
  color: #64748b;
}

/* Buttons */
.btn-primary-sm {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
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

.btn-secondary-sm {
  background: transparent;
  color: #3b82f6;
  border: 1px dashed #3b82f6;
  padding: 0.4rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  margin-top: 0.5rem;
  width: 100%;
}

.btn-secondary-sm:hover {
  background: #eff6ff;
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
  font-size: 1.2rem;
  line-height: 1;
}

.btn-danger-icon:hover {
  background: #fecaca;
}

.btn-danger-icon-sm {
  background: transparent;
  color: #94a3b8;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 4px;
}

.btn-danger-icon-sm:hover {
  color: #ef4444;
}
</style>
