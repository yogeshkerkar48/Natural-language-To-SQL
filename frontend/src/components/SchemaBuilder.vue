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
              <button @click="saveTable(tIndex)" class="btn-save" title="Save Table">✓</button>
              <button @click="removeTable(tIndex)" class="btn-danger-icon" title="Remove Table">×</button>
            </div>
          </div>
          <div v-if="table.validationError" class="error-message">{{ table.validationError }}</div>
          <div v-if="table.generalError" class="error-message general-table-error">{{ table.generalError }}</div>

          <div class="columns-list">
            <template v-for="(col, cIndex) in table.columns" :key="cIndex">
              <div 
                class="column-row"
                :class="{ 
                  'z-elevate': activeDropdown === `${tIndex}-${cIndex}`,
                  'has-error': col.validationError
                }"
              >
                <div class="column-input-wrapper">
                  <input 
                    v-model="col.name" 
                    placeholder="Column Name" 
                    class="col-name-input"
                    :class="{ 'input-error': col.validationError }"
                    @input="col.validationError = null"
                  />
                  <div v-if="col.validationError" class="row-error-tooltip">{{ col.validationError }}</div>
                </div>
                
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

                <div class="constraints-toggles">
                  <button 
                    type="button" 
                    class="toggle-btn" 
                    :class="{ active: col.primaryKey }" 
                    @click="col.primaryKey = !col.primaryKey"
                    title="Primary Key"
                  >PK</button>
                  <button 
                    type="button" 
                    class="toggle-btn" 
                    :class="{ active: col.notNull }" 
                    @click="col.notNull = !col.notNull"
                    title="Not Null"
                  >NN</button>
                  <button 
                    type="button" 
                    class="toggle-btn" 
                    :class="{ active: col.unique }" 
                    @click="col.unique = !col.unique"
                    title="Unique"
                  >UQ</button>
                  <button 
                    type="button" 
                    class="toggle-btn" 
                    :class="{ active: col.hasDefault }" 
                    @click="col.hasDefault = !col.hasDefault"
                    title="Default Value"
                  >DEF</button>
                  <button 
                    type="button" 
                    class="toggle-btn" 
                    :class="{ active: col.hasCheck }" 
                    @click="col.hasCheck = !col.hasCheck"
                    title="Check Constraint"
                  >CHK</button>
                  <button 
                    type="button" 
                    class="toggle-btn" 
                    :class="{ active: col.isForeignKey }" 
                    @click="col.isForeignKey = !col.isForeignKey"
                    title="Foreign Key"
                  >FK</button>
                </div>

                <button @click="removeColumn(tIndex, cIndex)" class="btn-danger-icon-sm" title="Remove Column">×</button>
              </div>
              
              <!-- Constraint Details Inputs -->
              <div v-if="col.hasDefault || col.hasCheck || col.isForeignKey" class="constraint-details">
                <div v-if="col.hasDefault" class="detail-input-group">
                  <label>Default:</label>
                  <input v-model="col.defaultValue" placeholder="Value" class="detail-input" />
                </div>
                <div v-if="col.hasCheck" class="detail-input-group">
                  <label>Check:</label>
                  <input v-model="col.checkCondition" :placeholder="`e.g. ${col.name || 'column'} > 0`" class="detail-input" />
                </div>
                <div v-if="col.isForeignKey" class="detail-input-group fk-group">
                  <label>FK:</label>
                  <div class="fk-inputs">
                    <input v-model="col.fkTable" placeholder="Table Name" class="detail-input sm" list="table-suggestions" />
                    <span>.</span>
                    <input v-model="col.fkColumn" placeholder="Column Name" class="detail-input sm" :list="`col-suggestions-${tIndex}-${cIndex}`" />
                    <span class="fk-info-hint">Manual typing allowed for new tables</span>
                    
                    <datalist :id="`col-suggestions-${tIndex}-${cIndex}`">
                      <option v-for="cName in getColumnsForTable(col.fkTable)" :key="cName" :value="cName"></option>
                    </datalist>
                  </div>
                </div>
              </div>
            </template>
            
            <datalist id="table-suggestions">
              <option v-for="name in availableTables" :key="name" :value="name"></option>
            </datalist>
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
            <div v-for="(col, cIndex) in table.columns" :key="cIndex" class="column-view-group">
              <div class="column-view-row">
                <span class="col-name">
                  {{ col.name }}
                  <span v-if="col.primaryKey" class="constraint-icon" title="Primary Key">🔑</span>
                  <span v-if="col.notNull" class="mini-badge nn" title="Not Null">NN</span>
                  <span v-if="col.unique" class="mini-badge uq" title="Unique">UQ</span>
                  <span v-if="col.hasDefault" class="mini-badge def" title="Default">DEF</span>
                  <span v-if="col.hasCheck" class="mini-badge chk" title="Check">CHK</span>
                  <span v-if="col.isForeignKey" class="mini-badge fk" title="Foreign Key">FK</span>
                </span>
                <div class="col-info">
                  <span class="col-type-badge">{{ col.type }}</span>
                </div>
              </div>
              <div v-if="col.hasDefault || col.hasCheck || col.isForeignKey" class="column-view-details">
                <span v-if="col.hasDefault" class="detail-view">Default: {{ col.defaultValue }}</span>
                <span v-if="col.hasCheck" class="detail-view">Check: {{ col.checkCondition }}</span>
                <span v-if="col.isForeignKey" class="detail-view">FK: {{ col.fkTable }}.{{ col.fkColumn }}</span>
              </div>
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
import { ref, watch, computed } from 'vue';

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

const availableTables = computed(() => {
  return tables.value.map(t => t.name).filter(n => n && n.trim() !== '');
});

const getColumnsForTable = (tableName) => {
  const table = tables.value.find(t => t.name === tableName);
  return table ? table.columns.map(c => c.name) : [];
};

const TYPE_GROUPS = {
  numeric: ['INT', 'BIGINT', 'SMALLINT', 'TINYINT', 'DECIMAL', 'FLOAT', 'DOUBLE', 'NUMERIC', 'REAL'],
  string: ['VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'NVARCHAR', 'MEDIUMTEXT', 'TINYTEXT'],
  dateTime: ['DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'YEAR'],
  binary: ['BLOB', 'BINARY', 'VARBINARY']
};

const areTypesCompatible = (type1, type2) => {
  if (!type1 || !type2) return false;
  
  const t1 = type1.toUpperCase().split('(')[0].trim();
  const t2 = type2.toUpperCase().split('(')[0].trim();
  
  if (t1 === t2) return true;
  
  for (const group in TYPE_GROUPS) {
    if (TYPE_GROUPS[group].includes(t1) && TYPE_GROUPS[group].includes(t2)) {
      return true;
    }
  }
  
  return false;
};

const isNumeric = (val) => {
  if (val === undefined || val === null || val.toString().trim() === '') return false;
  return !isNaN(parseFloat(val)) && isFinite(val);
};

const isDefaultCompatible = (value, type) => {
  if (!value) return false;
  const valStr = value.toString().trim();
  const valUpper = valStr.toUpperCase();
  
  // Rule 1: No operators/conditions allowed in Default values (to prevent entering conditions by mistake)
  const operatorRegex = /[><=!]|AND\b|OR\b/i;
  if (operatorRegex.test(valStr)) return false;

  if (valUpper === 'NA') return true;
  
  const baseType = type.toUpperCase().split('(')[0].trim();
  const isNumericType = TYPE_GROUPS.numeric.includes(baseType);
  const isStringType = TYPE_GROUPS.string.includes(baseType);
  
  if (isNumericType) {
    // Rule 2: Pure numeric for numeric types
    return isNumeric(valStr);
  } else if (isStringType) {
    // Rule 3: Single datatype only - Pure characters for string types (no digits)
    const hasDigits = /\d/.test(valStr);
    if (hasDigits) return false;
    return true;
  }
  return true;
};

const initializeColumn = (col) => {
  return {
    name: col.name || '',
    type: col.type || 'VARCHAR',
    primaryKey: col.primaryKey || false,
    notNull: col.notNull || false,
    unique: col.unique || false,
    hasDefault: col.hasDefault || false,
    defaultValue: col.defaultValue || '',
    hasCheck: col.hasCheck || false,
    checkCondition: col.checkCondition || '',
    isForeignKey: col.isForeignKey || false,
    fkTable: col.fkTable || '',
    fkColumn: col.fkColumn || '',
    validationError: col.validationError || null
  };
};

watch(() => props.modelValue, (newVal) => {
  if (!newVal) return;
  
  tables.value = newVal.map(t => ({
    ...t,
    columns: (t.columns || []).map(initializeColumn),
    isEditing: t.isEditing !== undefined ? t.isEditing : false,
    validationError: t.validationError || null
  }));
}, { deep: true, immediate: true });

const update = () => {
  emit('update:modelValue', tables.value);
};

const validateName = (name, type = 'Table') => {
  const regex = /^[a-zA-Z][a-zA-Z0-9_]*$/;
  if (!name || name.trim() === '') {
    return `${type} name is required`;
  }
  if (!regex.test(name)) {
    return `Invalid ${type.toLowerCase()} name. Must start with a letter (a-z, A-Z). Letters, numbers, and underscores (_) allowed elsewhere. No spaces.`;
  }
  return null;
};

const validateTableName = (name) => {
  return validateName(name, 'Table');
};

const validateColumns = (table) => {
  const columnNames = new Set();
  let hasError = false;
  let pkCount = 0;
  
  // Clear previous errors
  table.generalError = null;
  
  table.columns.forEach(col => {
    col.validationError = null;
    
    // Name validation
    const nameError = validateName(col.name, 'Column');
    if (nameError) {
      col.validationError = nameError;
      hasError = true;
    } else if (columnNames.has(col.name.toLowerCase().trim())) {
      col.validationError = `Duplicate column: ${col.name}`;
      hasError = true;
    } else if (!col.type) {
      col.validationError = 'Data type is required';
      hasError = true;
    }
    
    // PK validation count
    if (col.primaryKey) pkCount++;

    // Default value validation
    if (col.hasDefault) {
      if (col.defaultValue === undefined || col.defaultValue === null || col.defaultValue.toString().trim() === '') {
        col.validationError = 'Default value is required';
        hasError = true;
      } else if (!isDefaultCompatible(col.defaultValue, col.type)) {
        col.validationError = `Invalid default for ${col.type} (use "NA" or ${TYPE_GROUPS.numeric.includes(col.type.toUpperCase().split('(')[0].trim()) ? 'number' : 'valid value'})`;
        hasError = true;
      }
    }

    // Check condition validation
    if (col.hasCheck) {
      if (!col.checkCondition || col.checkCondition.trim() === '') {
        col.validationError = 'Check condition is required';
        hasError = true;
      } else {
        const cond = col.checkCondition.toLowerCase();
        const colName = col.name.toLowerCase().trim();
        if (!cond.includes(colName)) {
          col.validationError = `Condition must refer to column "${colName}"`;
          hasError = true;
        }
      }
    }

    // Mutual exclusivity: PK and FK
    if (col.primaryKey && col.isForeignKey) {
      col.validationError = 'Column cannot be both Primary Key and Foreign Key';
      hasError = true;
    }

    // Foreign Key validation
    if (col.isForeignKey) {
      if (!col.fkTable || !col.fkColumn) {
        col.validationError = 'FK target table & column required';
        hasError = true;
      } else {
        // Validate type compatibility if target table/column exists
        const targetTable = tables.value.find(t => t.name === col.fkTable);
        if (targetTable) {
          const targetCol = targetTable.columns.find(c => c.name === col.fkColumn);
          if (targetCol) {
            if (targetTable.name === table.name && targetCol.name === col.name) {
              col.validationError = 'Column cannot reference itself as Foreign Key';
              hasError = true;
            } else if (!areTypesCompatible(col.type, targetCol.type)) {
              col.validationError = `Type mismatch: Target "${targetCol.name}" is ${targetCol.type}`;
              hasError = true;
            } else if (!targetCol.primaryKey && !targetCol.unique) {
              col.validationError = `Target "${targetCol.name}" must be Primary Key or Unique`;
              hasError = true;
            }
          }
        }
      }
    }
    
    if (col.name) {
      columnNames.add(col.name.toLowerCase().trim());
    }
  });

  // Table-level PK check
  if (pkCount > 1) {
    table.generalError = 'two primary keys not allowed in single table';
    hasError = true;
  }
  
  return !hasError;
};

const saveTable = (index) => {
  const table = tables.value[index];
  const nameError = validateTableName(table.name);
  const columnsValid = validateColumns(table);
  
  if (nameError || !columnsValid) {
    table.validationError = nameError;
    if (!columnsValid && !nameError && !table.generalError) {
      table.generalError = 'Please fix column errors below';
    }
    return;
  }
  
  table.validationError = null;
  table.generalError = null;
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
    columns: [{ 
      name: 'id', 
      type: 'INT',
      primaryKey: true,
      notNull: true,
      unique: false,
      hasDefault: false,
      defaultValue: '',
      hasCheck: false,
      checkCondition: '',
      isForeignKey: false,
      fkTable: '',
      fkColumn: ''
    }],
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
  tables.value[tableIndex].columns.push({ 
    name: '', 
    type: 'VARCHAR',
    primaryKey: false,
    notNull: false,
    unique: false,
    hasDefault: false,
    defaultValue: '',
    hasCheck: false,
    checkCondition: '',
    isForeignKey: false,
    fkTable: '',
    fkColumn: ''
  });
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
      const nameError = validateTableName(table.name);
      const colsValid = validateColumns(table);
      
      if (nameError || !colsValid) {
        table.validationError = nameError;
        if (!colsValid && !nameError && !table.generalError) {
          table.generalError = 'Please fix column errors below';
        }
        hasErrors = true;
      } else {
        table.validationError = null;
        table.generalError = null;
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
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  overflow: visible;
}

.table-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem;
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
  padding-bottom: 0.5rem;
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
  min-width: 0;
}

.table-name-input:focus {
  outline: none;
  border-bottom: 2px solid #3b82f6;
}

.input-error {
  border-color: #ef4444 !important;
  background-color: #fef2f2 !important;
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
  border-bottom: 1px solid #3b82f6;
}

.table-name-display {
  font-weight: 700;
  font-size: 1.2rem;
  color: #1e293b;
  margin: 0;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: visible;
  padding: 4px 0;
}

.column-input-wrapper {
  position: relative;
  flex: 1;
  min-width: 120px;
  max-width: 200px;
}

.row-error-tooltip {
  position: absolute;
  top: -24px;
  left: 0;
  background: #ef4444;
  color: white;
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 20;
  pointer-events: none;
}

.row-error-tooltip::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 10px;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #ef4444;
}

.col-name-input {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.85rem;
}

.input-error {
  border-color: #ef4444 !important;
  background-color: #fef2f2 !important;
}

.general-table-error {
  margin-top: 4px;
  font-weight: 600;
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

/* New Constraints Styles */
.constraints-toggles {
  display: flex;
  gap: 1px;
  background: #f1f5f9;
  padding: 2px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.toggle-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: #e2e8f0;
  color: #64748b;
}

.toggle-btn.active {
  background: #3b82f6;
  color: white;
}

.constraint-details {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 6px 6px;
  padding: 6px 10px;
  margin-top: -6px;
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.detail-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-input-group label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  min-width: 50px;
}

.detail-input {
  flex: 1;
  padding: 2px 6px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.75rem;
}

.detail-input.sm {
  max-width: 100px;
}

.fk-group span {
  font-weight: bold;
  color: #94a3b8;
}

.fk-inputs {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.fk-info-hint {
  font-size: 0.65rem;
  color: #94a3b8;
  font-style: italic;
  margin-left: 8px;
}

/* View Mode Details */
.column-view-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 4px;
}

.col-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mini-badge {
  font-size: 0.6rem;
  font-weight: 800;
  padding: 1px 3px;
  border-radius: 3px;
  text-transform: uppercase;
}

.mini-badge.nn { background: #fee2e2; color: #ef4444; }
.mini-badge.uq { background: #fef3c7; color: #d97706; }
.mini-badge.def { background: #dcfce7; color: #16a34a; }
.mini-badge.chk { background: #e0f2fe; color: #0369a1; }
.mini-badge.fk { background: #f3e8ff; color: #7e22ce; }

.constraint-icon {
  margin-left: 4px;
  font-size: 0.9rem;
}

.column-view-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-left: 10px;
  margin-top: 2px;
}

.detail-view {
  font-size: 0.7rem;
  color: #64748b;
  font-style: italic;
  background: #f1f5f9;
  padding: 0 4px;
  border-radius: 2px;
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
