<template>
  <div class="relationship-builder">
    <div class="header">
      <h3><span class="icon">🔗</span> Define Relationships</h3>
      <div class="header-hint">
        <span class="hint-text">💡 Drag a column from one table and drop it on another table's column to create a relationship</span>
      </div>
    </div>

    <div v-if="relationships.length === 0 && !isDragging" class="empty-state">
      <p>No relationships defined.</p>
      <p class="sub-text">Drag a column from one table to another to create a relationship.</p>
    </div>

    <!-- Drag and Drop Tables Display -->
    <div v-if="tables.length > 0" class="drag-drop-area">
      <div class="tables-grid">
        <div 
          v-for="(table, tIndex) in tables" 
          :key="tIndex" 
          class="draggable-table"
          :class="{ 'highlight': dragOverTable === table.name }"
        >
          <div class="table-title">{{ table.name }}</div>
          <div class="columns-list-drag">
            <div 
              v-for="(col, cIndex) in table.columns" 
              :key="cIndex"
              class="draggable-column"
              :class="{ 
                'dragging': dragSource && dragSource.table === table.name && dragSource.column === col.name,
                'drop-target': dragOverColumn && dragOverColumn.table === table.name && dragOverColumn.column === col.name
              }"
              draggable="true"
              @dragstart="handleDragStart($event, table.name, col.name)"
              @dragend="handleDragEnd"
              @dragover.prevent="handleDragOver($event, table.name, col.name)"
              @dragleave="handleDragLeave"
              @drop="handleDrop($event, table.name, col.name)"
            >
              <span class="drag-handle" style="pointer-events: none;">⋮⋮</span>
              <span class="col-name" style="pointer-events: none;">{{ col.name }}</span>
              <span class="col-type" style="pointer-events: none;">{{ col.type }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Existing Relationships List -->
    <div v-if="relationships.length > 0" class="relationships-list">
      <div class="relationships-header">
        <h4>Defined Relationships</h4>
      </div>
      <div v-for="(rel, index) in relationships" :key="index" class="rel-card">
        <div class="rel-row-view">
          <div class="rel-display">
            <span class="rel-text">
              <strong>{{ rel.from_table }}</strong>.{{ rel.from_column }}
              <span class="arrow-view">→</span>
              <strong>{{ rel.to_table }}</strong>.{{ rel.to_column }}
            </span>
          </div>
          <div class="action-buttons">
            <button @click="removeRelationship(index)" class="btn-danger-icon" title="Remove Relationship">×</button>
          </div>
        </div>
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
  },
  tables: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const relationships = ref(props.modelValue || []);

// Drag and drop state
const dragSource = ref(null);
const dragOverTable = ref(null);
const dragOverColumn = ref(null);
const isDragging = ref(false);

// Type compatibility groups
const TYPE_GROUPS = {
  numeric: ['INT', 'TINYINT', 'SMALLINT', 'BIGINT', 'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL', 'BIT'],
  string: ['VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT', 'TINYTEXT', 'JSON', 'ENUM', 'SET'],
  dateTime: ['DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'YEAR'],
  binary: ['BINARY', 'VARBINARY', 'BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'TINYBLOB']
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

watch(() => props.modelValue, (newVal) => {
  relationships.value = newVal || [];
}, { deep: true });

const update = () => {
  emit('update:modelValue', relationships.value);
};

const handleDragStart = (event, tableName, columnName) => {
  console.log('Drag started:', tableName, columnName);
  isDragging.value = true;
  dragSource.value = {
    table: tableName,
    column: columnName
  };
  
  // Set drag effect
  event.dataTransfer.effectAllowed = 'link';
  event.dataTransfer.setData('text/plain', `${tableName}.${columnName}`);
  
  // Add visual feedback
  if (event.target) {
    event.target.style.opacity = '0.5';
  }
};

const handleDragEnd = (event) => {
  isDragging.value = false;
  dragSource.value = null;
  dragOverTable.value = null;
  dragOverColumn.value = null;
  event.target.style.opacity = '1';
};

const handleDragOver = (event, tableName, columnName) => {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'link';
  
  dragOverTable.value = tableName;
  dragOverColumn.value = {
    table: tableName,
    column: columnName
  };
};

const handleDragLeave = () => {
  dragOverColumn.value = null;
};

const handleDrop = (event, tableName, columnName) => {
  event.preventDefault();
  
  if (!dragSource.value) return;
  
  // Don't create relationship if dropping on the same column
  if (dragSource.value.table === tableName && dragSource.value.column === columnName) {
    return;
  }
  
  // Find column types
  const sourceTable = props.tables.find(t => t.name === dragSource.value.table);
  const sourceColumn = sourceTable?.columns.find(c => c.name === dragSource.value.column);
  const targetTable = props.tables.find(t => t.name === tableName);
  const targetColumn = targetTable?.columns.find(c => c.name === columnName);
  
  // Check if types are compatible
  if (!areTypesCompatible(sourceColumn?.type, targetColumn?.type)) {
    alert(`Cannot relate columns with incompatible types: ${sourceColumn?.type} and ${targetColumn?.type}.\nPlease use compatible types (e.g., both numeric or both string).`);
    return;
  }
  
  // Check if relationship already exists
  const exists = relationships.value.some(rel => 
    (rel.from_table === dragSource.value.table && 
     rel.from_column === dragSource.value.column &&
     rel.to_table === tableName &&
     rel.to_column === columnName) ||
    (rel.from_table === tableName && 
     rel.from_column === columnName &&
     rel.to_table === dragSource.value.table &&
     rel.to_column === dragSource.value.column)
  );
  
  if (!exists) {
    // Create new relationship
    relationships.value.push({
      from_table: dragSource.value.table,
      from_column: dragSource.value.column,
      to_table: tableName,
      to_column: columnName
    });
    update();
  }
  
  // Reset drag state
  dragSource.value = null;
  dragOverTable.value = null;
  dragOverColumn.value = null;
};

const removeRelationship = (index) => {
  relationships.value.splice(index, 1);
  update();
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
  flex-wrap: wrap;
  gap: 1rem;
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

.header-hint {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.hint-text {
  font-size: 0.85rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
}

.empty-state {
  text-align: center;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px dashed #e5e7eb;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.sub-text {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

/* Drag and Drop Area */
.drag-drop-area {
  margin-bottom: 2rem;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.draggable-table {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
  transition: all 0.3s;
}

.draggable-table.highlight {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.table-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: #1e293b;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3b82f6;
}

.columns-list-drag {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.draggable-column {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s;
  -webkit-user-drag: element;
}

.draggable-column:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  transform: translateX(4px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.draggable-column:active {
  cursor: grabbing;
}

.draggable-column.dragging {
  opacity: 0.5;
  border-color: #3b82f6;
  background: #dbeafe;
}

.draggable-column.drop-target {
  border-color: #10b981;
  background: #d1fae5;
  border-width: 2px;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
  animation: pulse 0.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

.drag-handle {
  color: #94a3b8;
  font-size: 0.9rem;
  cursor: grab;
}

.draggable-column:active .drag-handle {
  cursor: grabbing;
}

.col-name {
  flex: 1;
  font-weight: 500;
  color: #334155;
  font-size: 0.9rem;
}

.col-type {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
}

/* Relationships List */
.relationships-list {
  margin-top: 2rem;
}

.relationships-header {
  margin-bottom: 1rem;
}

.relationships-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.rel-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
}

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
  transition: all 0.2s;
}

.btn-danger-icon:hover {
  background: #fecaca;
  transform: scale(1.1);
}
</style>

