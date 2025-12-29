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
              <button @click="removeTable(tIndex)" class="btn-danger-icon" title="Remove Table">×</button>
            </div>
          </div>
          <div v-if="table.validationError" class="error-message">{{ table.validationError }}</div>

          <div class="columns-list">
            <div 
              v-for="(col, cIndex) in table.columns" 
              :key="cIndex" 
              class="column-row"
              :class="{ 'z-elevate': activeDropdown === `${tIndex}-${cIndex}` }"
            >
              <input 
                v-model="col.name" 
                placeholder="Column Name" 
                class="col-name-input"
              />
              <div class="custom-select-wrapper">
                <div 
                  class="custom-select" 
                  @click.stop="toggleDropdown(tIndex, cIndex)"
                  :class="{ 'active': activeDropdown === `${tIndex}-${cIndex}` }"
                >
                  <span class="selected-value">{{ col.type }}</span>
                  <span class="dropdown-arrow">▼</span>
                </div>
                <div 
                  v-if="activeDropdown === `${tIndex}-${cIndex}`" 
                  class="dropdown-menu"
                >
                  <div class="dropdown-group">
                    <div class="group-label">Numeric</div>
                    <div 
                      v-for="type in numericTypes" 
                      :key="type"
                      class="dropdown-option"
                      @click.stop="selectType(tIndex, cIndex, type)"
                    >
                      {{ type }}
                    </div>
                  </div>
                  <div class="dropdown-group">
                    <div class="group-label">String/Text</div>
                    <div 
                      v-for="type in stringTypes" 
                      :key="type"
                      class="dropdown-option"
                      @click.stop="selectType(tIndex, cIndex, type)"
                    >
                      {{ type }}
                    </div>
                  </div>
                  <div class="dropdown-group">
                    <div class="group-label">Date/Time</div>
                    <div 
                      v-for="type in dateTypes" 
                      :key="type"
                      class="dropdown-option"
                      @click.stop="selectType(tIndex, cIndex, type)"
                    >
                      {{ type }}
                    </div>
                  </div>
                  <div class="dropdown-group">
                    <div class="group-label">Others</div>
                    <div 
                      v-for="type in otherTypes" 
                      :key="type"
                      class="dropdown-option"
                      @click.stop="selectType(tIndex, cIndex, type)"
                    >
                      {{ type }}
                    </div>
                  </div>
                </div>
              </div>
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

    <div v-if="tables.length > 0" class="save-section">
      <button @click="saveAllTables" class="btn-save-all">Save</button>
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

// Data type options
const numericTypes = ['INT', 'BIGINT', 'SMALLINT', 'TINYINT', 'DECIMAL', 'FLOAT', 'DOUBLE'];
const stringTypes = ['VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'NVARCHAR'];
const dateTypes = ['DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'YEAR'];
const otherTypes = ['BOOLEAN'];

// Active dropdown tracking
const activeDropdown = ref(null);

// Close dropdown when clicking outside
const closeDropdown = () => {
  activeDropdown.value = null;
};

// Add click listener to close dropdown when clicking outside
if (typeof window !== 'undefined') {
  window.addEventListener('click', closeDropdown);
}

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

const toggleDropdown = (tableIndex, colIndex) => {
  const dropdownId = `${tableIndex}-${colIndex}`;
  activeDropdown.value = activeDropdown.value === dropdownId ? null : dropdownId;
};

const selectType = (tableIndex, colIndex, type) => {
  tables.value[tableIndex].columns[colIndex].type = type;
  activeDropdown.value = null;
  update();
};

const saveAllTables = () => {
  // Validate all tables before saving
  let hasErrors = false;
  
  tables.value.forEach((table, index) => {
    if (table.isEditing) {
      const error = validateTableName(table.name);
      if (error) {
        table.validationError = error;
        hasErrors = true;
      } else {
        table.validationError = null;
      }
    }
  });
  
  if (!hasErrors) {
    // Set all tables to view mode
    tables.value.forEach(table => {
      table.isEditing = false;
    });
    update();
  }
};

</script>

<style scoped>
.schema-builder {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  position: relative;
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
  overflow: visible;
}

.table-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  padding-bottom: 2rem;
  transition: all 0.2s;
  overflow: visible;
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
  margin-bottom: 1rem;
}

.column-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  position: relative;
  overflow: visible;
}

.col-name-input {
  flex: 1;
  min-width: 0;
  padding: 0.35rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* Custom Dropdown Styles */
.custom-select-wrapper {
  position: relative;
  width: 100px;
  flex-shrink: 0;
}

.column-row.z-elevate {
  z-index: 100;
}

.custom-select {
  width: 100%;
  padding: 0.35rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.75rem;
  background: white;
  color: #64748b;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
  transition: all 0.2s;
}

.custom-select:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.custom-select.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.selected-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  font-size: 0.6rem;
  margin-left: 0.25rem;
  transition: transform 0.2s;
}

.custom-select.active .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  min-width: 130px;
  background: white !important;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
  animation: dropdownSlide 0.2s ease-out;
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-group {
  padding: 0.25rem 0;
}

.dropdown-group:not(:last-child) {
  border-bottom: 1px solid #f1f5f9;
}

.group-label {
  padding: 0.4rem 0.75rem;
  font-size: 0.65rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f8fafc;
}

.dropdown-option {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.dropdown-option:hover {
  background: #eff6ff;
  color: #1e40af;
  font-weight: 500;
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

.save-section {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.btn-save-all {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}

.btn-save-all:hover {
  background: #1d4ed8;
  box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
  transform: translateY(-1px);
}

.btn-save-all:active {
  transform: translateY(0);
}

</style>
