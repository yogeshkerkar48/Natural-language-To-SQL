<template>
  <div class="interactive-schema">
    <div class="header">
      <h3><span class="icon">📊</span> Interactive Schema Diagram</h3>
      <div class="header-hint">
        <button @click="resetLayout" class="btn-reset">🔄 Reset Layout</button>
        <span class="hint-text">💡 Drag tables to reposition • Drag columns to create relationships</span>
      </div>
    </div>

    <div class="canvas-wrapper" ref="canvasWrapper">
      <svg 
        ref="svgCanvas" 
        class="schema-svg"
        :height="canvasHeight"
        @mousedown="handleCanvasMouseDown"
        @mousemove="handleCanvasMouseMove"
        @mouseup="handleCanvasMouseUp"
      >
        <!-- Relationship arrows -->
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="#3b82f6" />
          </marker>
        </defs>

        <!-- Draw relationship lines -->
        <g class="relationships-layer">
          <g 
            v-for="(rel, idx) in relationships" 
            :key="`rel-${idx}`"
            class="relationship-group"
          >
            <path
              :d="getRelationshipPath(rel)"
              stroke="#3b82f6"
              stroke-width="2"
              fill="none"
              marker-end="url(#arrowhead)"
              class="relationship-line"
            />
            <g :transform="`translate(${getRelationshipLabelPosition(rel).x}, ${getRelationshipLabelPosition(rel).y})`" class="label-group">
              <rect
                x="-50"
                y="-15"
                width="100"
                height="24"
                rx="12"
                class="label-bg"
              />
              <text
                class="relationship-label"
                text-anchor="middle"
                y="2"
              >
                {{ rel.from_column }} → {{ rel.to_column }}
              </text>
              <g 
                class="btn-remove-rel" 
                @click.stop="removeRelationship(idx)"
                transform="translate(55, -3)"
              >
                <circle r="8" fill="#ef4444" />
                <text 
                  y="3" 
                  text-anchor="middle" 
                  fill="white" 
                  font-size="10" 
                  font-weight="bold"
                >✕</text>
              </g>
            </g>
          </g>
        </g>

        <!-- Draw tables -->
        <g v-for="(table, tIdx) in tablesWithPositions" :key="`table-${tIdx}`">
          <g
            :transform="`translate(${table.x}, ${table.y})`"
            @mousedown.stop="handleTableMouseDown($event, tIdx)"
            class="table-group"
            :class="{ 'dragging': draggingTableIndex === tIdx }"
          >
            <!-- Table container -->
            <rect
              :width="tableWidth"
              :height="getTableHeight(table)"
              rx="8"
              class="table-rect"
            />
            
            <!-- Table header -->
            <rect
              :width="tableWidth"
              height="40"
              rx="8"
              class="table-header"
            />
            <text
              :x="tableWidth / 2"
              y="25"
              class="table-title"
              text-anchor="middle"
            >
              {{ table.name }}
            </text>

            <!-- Columns -->
            <g v-for="(col, cIdx) in table.columns" :key="`col-${cIdx}`">
              <g
                :transform="`translate(0, ${40 + cIdx * 35})`"
                @mousedown.stop="handleColumnMouseDown($event, tIdx, cIdx)"
                @mouseup.stop="handleColumnMouseUp($event, tIdx, cIdx)"
                @mouseenter="handleColumnMouseEnter(tIdx, cIdx)"
                @mouseleave="handleColumnMouseLeave"
                class="column-group"
                :class="{
                  'column-dragging': dragSourceColumn && dragSourceColumn.tableIdx === tIdx && dragSourceColumn.colIdx === cIdx,
                  'column-drop-target': dropTargetColumn && dropTargetColumn.tableIdx === tIdx && dropTargetColumn.colIdx === cIdx
                }"
              >
                <rect
                  :width="tableWidth"
                  height="35"
                  class="column-rect"
                />
                <text x="10" y="22" class="column-name">{{ col.name }}</text>
                <text :x="tableWidth - 10" y="22" class="column-type" text-anchor="end">{{ getFullType(col) }}</text>
                
                <!-- Drag handle -->
                <text :x="tableWidth / 2" y="22" class="drag-indicator" text-anchor="middle" opacity="0.3">⋮⋮</text>
              </g>
            </g>
          </g>
        </g>

        <!-- Temporary drag line -->
        <line
          v-if="isDraggingColumn && dragLineEnd"
          :x1="dragLineStart.x"
          :y1="dragLineStart.y"
          :x2="dragLineEnd.x"
          :y2="dragLineEnd.y"
          stroke="#10b981"
          stroke-width="2"
          stroke-dasharray="5,5"
          class="drag-line"
        />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  tables: {
    type: Array,
    required: true
  },
  relationships: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:relationships']);

// Canvas refs
const svgCanvas = ref(null);
const canvasWrapper = ref(null);

// Table dimensions
const tableWidth = 250;
const columnHeight = 35;
const headerHeight = 40;

// Dragging state
const draggingTableIndex = ref(null);
const dragOffset = ref({ x: 0, y: 0 });
const dragSourceColumn = ref(null);
const dropTargetColumn = ref(null);
const isDraggingColumn = ref(false);
const dragLineStart = ref(null);
const dragLineEnd = ref(null);

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
  
  // Check if both belong to the same group
  for (const group in TYPE_GROUPS) {
    if (TYPE_GROUPS[group].includes(t1) && TYPE_GROUPS[group].includes(t2)) {
      return true;
    }
  }
  
  return false;
};

// Table positions
const tablePositions = ref({});

// Initialize table positions
const initializePositions = (force = false) => {
  const positions = {};
  props.tables.forEach((table, idx) => {
    // If table already has a position and we're not forcing reset, keep it
    if (!force && tablePositions.value[table.name]) {
      positions[table.name] = tablePositions.value[table.name];
    } else {
      // Create a neat grid: 3 tables per row
      const col = idx % 3;
      const row = Math.floor(idx / 3);
      positions[table.name] = {
        x: 50 + col * 300,
        y: 50 + row * 250
      };
    }
  });
  tablePositions.value = positions;
};

const resetLayout = () => {
  if (confirm('Are you sure you want to reset the diagram layout? This will reposition all tables.')) {
    initializePositions(true);
  }
};

// Computed tables with positions
const tablesWithPositions = computed(() => {
  return props.tables.map(table => ({
    ...table,
    x: tablePositions.value[table.name]?.x || 0,
    y: tablePositions.value[table.name]?.y || 0
  }));
});

// Get table height
const getTableHeight = (table) => {
  return headerHeight + table.columns.length * columnHeight;
};

// Computed canvas height
const canvasHeight = computed(() => {
  if (props.tables.length === 0) return 200;
  
  let maxHeight = 300;
  tablesWithPositions.value.forEach(table => {
    const tableBottom = (table.y || 0) + getTableHeight(table) + 50;
    if (tableBottom > maxHeight) {
      maxHeight = tableBottom;
    }
  });
  return maxHeight;
});

// Table dragging handlers
const handleTableMouseDown = (event, tableIdx) => {
  draggingTableIndex.value = tableIdx;
  const rect = svgCanvas.value.getBoundingClientRect();
  const table = tablesWithPositions.value[tableIdx];
  
  // Calculate offset relative to the SVG canvas
  dragOffset.value = {
    x: (event.clientX - rect.left) - table.x,
    y: (event.clientY - rect.top) - table.y
  };
};

const handleCanvasMouseMove = (event) => {
  if (draggingTableIndex.value !== null) {
    const rect = svgCanvas.value.getBoundingClientRect();
    const table = tablesWithPositions.value[draggingTableIndex.value];
    
    // Calculate new position
    let newX = event.clientX - rect.left - dragOffset.value.x;
    let newY = event.clientY - rect.top - dragOffset.value.y;
    
    // Boundary checks
    const minX = 0;
    const minY = 0;
    const maxX = Math.max(1200, rect.width) - tableWidth;
    const maxY = canvasHeight.value - getTableHeight(table);
    
    tablePositions.value[table.name] = {
      x: Math.max(minX, Math.min(newX, maxX)),
      y: Math.max(minY, Math.min(newY, maxY))
    };
  }

  // Update drag line for column dragging
  if (isDraggingColumn.value && dragLineStart.value) {
    const rect = svgCanvas.value.getBoundingClientRect();
    dragLineEnd.value = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
  }
};

const handleCanvasMouseUp = () => {
  draggingTableIndex.value = null;
  if (isDraggingColumn.value) {
    isDraggingColumn.value = false;
    dragSourceColumn.value = null;
    dragLineStart.value = null;
    dragLineEnd.value = null;
  }
};

const handleCanvasMouseDown = (event) => {
  // Only handle if clicking on canvas background
  if (event.target === svgCanvas.value) {
    handleCanvasMouseUp();
  }
};

// Column dragging for relationships
const handleColumnMouseDown = (event, tableIdx, colIdx) => {
  event.stopPropagation();
  dragSourceColumn.value = { tableIdx, colIdx };
  isDraggingColumn.value = true;
  
  const table = tablesWithPositions.value[tableIdx];
  const rect = svgCanvas.value.getBoundingClientRect();
  
  dragLineStart.value = {
    x: table.x + tableWidth / 2,
    y: table.y + headerHeight + colIdx * columnHeight + columnHeight / 2
  };
};

const handleColumnMouseUp = (event, tableIdx, colIdx) => {
  event.stopPropagation();
  
  if (isDraggingColumn.value && dragSourceColumn.value) {
    const sourceTable = tablesWithPositions.value[dragSourceColumn.value.tableIdx];
    const sourceColumn = sourceTable.columns[dragSourceColumn.value.colIdx];
    const targetTable = tablesWithPositions.value[tableIdx];
    const targetColumn = targetTable.columns[colIdx];
    
    // Don't create relationship with same column
    if (dragSourceColumn.value.tableIdx === tableIdx && dragSourceColumn.value.colIdx === colIdx) {
      handleCanvasMouseUp();
      return;
    }
    
    // Check for Foreign Key context
    const sourceIsFK = sourceColumn.isForeignKey;
    const targetIsFK = targetColumn.isForeignKey;
    const sourceIsPKUQ = sourceColumn.primaryKey || sourceColumn.unique;
    const targetIsPKUQ = targetColumn.primaryKey || targetColumn.unique;

    let isValidLink = false;
    let errorDetail = "";

    if (sourceIsFK && targetIsPKUQ) {
      if (sourceColumn.fkTable === targetTable.name && sourceColumn.fkColumn === targetColumn.name) {
        isValidLink = true;
      } else {
        errorDetail = `Column "${sourceColumn.name}" is a Foreign Key to "${sourceColumn.fkTable}.${sourceColumn.fkColumn}", not "${targetTable.name}.${targetColumn.name}".`;
      }
    } else if (targetIsFK && sourceIsPKUQ) {
      if (targetColumn.fkTable === sourceTable.name && targetColumn.fkColumn === sourceColumn.name) {
        isValidLink = true;
      } else {
        errorDetail = `Column "${targetColumn.name}" is a Foreign Key to "${targetColumn.fkTable}.${targetColumn.fkColumn}", not "${sourceTable.name}.${sourceColumn.name}".`;
      }
    } else {
      if (!sourceIsFK && !targetIsFK) {
        errorDetail = "One of the columns must be defined as a Foreign Key in the Schema Builder.";
      } else {
        const fkCol = sourceIsFK ? sourceColumn : targetColumn;
        errorDetail = `The target column for "${fkCol.name}" must be a Primary Key or Unique Key.`;
      }
    }

    if (!isValidLink) {
      alert(`Invalid Relationship: ${errorDetail}\n\nPlease define the Foreign Key relationship correctly in the table settings first.`);
      handleCanvasMouseUp();
      return;
    }

    // Check if types are compatible (redundant but safe)
    if (!areTypesCompatible(sourceColumn.type, targetColumn.type)) {
      alert(`Type Mismatch: ${sourceColumn.name} (${sourceColumn.type}) and ${targetColumn.name} (${targetColumn.type}) are incompatible.`);
      handleCanvasMouseUp();
      return;
    }
    
    // Check if relationship already exists
    const exists = props.relationships.some(rel =>
      (rel.from_table === sourceTable.name && rel.from_column === sourceColumn.name &&
       rel.to_table === targetTable.name && rel.to_column === targetColumn.name) ||
      (rel.from_table === targetTable.name && rel.from_column === targetColumn.name &&
       rel.to_table === sourceTable.name && rel.to_column === sourceColumn.name)
    );
    
    if (!exists) {
      const newRelationships = [...props.relationships, {
        from_table: sourceIsFK ? sourceTable.name : targetTable.name,
        from_column: sourceIsFK ? sourceColumn.name : targetColumn.name,
        to_table: sourceIsFK ? targetTable.name : sourceTable.name,
        to_column: sourceIsFK ? targetColumn.name : sourceColumn.name
      }];
      emit('update:relationships', newRelationships);
    }
  }
  
  handleCanvasMouseUp();
};

const handleColumnMouseEnter = (tableIdx, colIdx) => {
  if (isDraggingColumn.value) {
    dropTargetColumn.value = { tableIdx, colIdx };
  }
};

const handleColumnMouseLeave = () => {
  dropTargetColumn.value = null;
};

const removeRelationship = (index) => {
  if (confirm('Are you sure you want to remove this relationship?')) {
    const newRelationships = [...props.relationships];
    newRelationships.splice(index, 1);
    emit('update:relationships', newRelationships);
  }
};

// Get relationship path
const getRelationshipPath = (rel) => {
  const fromTable = tablesWithPositions.value.find(t => t.name === rel.from_table);
  const toTable = tablesWithPositions.value.find(t => t.name === rel.to_table);
  
  if (!fromTable || !toTable) return '';
  
  const fromColIdx = fromTable.columns.findIndex(c => c.name === rel.from_column);
  const toColIdx = toTable.columns.findIndex(c => c.name === rel.to_column);
  
  const x1 = fromTable.x + tableWidth;
  const y1 = fromTable.y + headerHeight + fromColIdx * columnHeight + columnHeight / 2;
  const x2 = toTable.x;
  const y2 = toTable.y + headerHeight + toColIdx * columnHeight + columnHeight / 2;
  
  // Create curved path
  const midX = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
};

// Get relationship label position
const getRelationshipLabelPosition = (rel) => {
  const fromTable = tablesWithPositions.value.find(t => t.name === rel.from_table);
  const toTable = tablesWithPositions.value.find(t => t.name === rel.to_table);
  
  if (!fromTable || !toTable) return { x: 0, y: 0 };
  
  const fromColIdx = fromTable.columns.findIndex(c => c.name === rel.from_column);
  const toColIdx = toTable.columns.findIndex(c => c.name === rel.to_column);
  
  const x1 = fromTable.x + tableWidth;
  const y1 = fromTable.y + headerHeight + fromColIdx * columnHeight + columnHeight / 2;
  const x2 = toTable.x;
  const y2 = toTable.y + headerHeight + toColIdx * columnHeight + columnHeight / 2;
  
  return {
    x: (x1 + x2) / 2,
    y: (y1 + y2) / 2
  };
};

watch(() => props.tables, () => {
  initializePositions();
}, { deep: true, immediate: true });

onMounted(() => {
  initializePositions();
});
const getFullType = (col) => {
  if (!col.type) return '';
  // If type already has params (from SchemaBuilder update), don't append again
  if (col.type.includes('(')) return col.type;
  
  let full = col.type;
  if (col.precision && col.precision.toString().trim() !== '') {
    full += `(${col.precision}${col.scale && col.scale.toString().trim() !== '' ? `,${col.scale}` : ''})`;
  }
  return full;
};

</script>

<style scoped>
.interactive-schema {
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
  align-items: center;
  gap: 1rem;
}

.btn-reset {
  background: white;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-reset:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1e293b;
}

.hint-text {
  font-size: 0.85rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
}

.canvas-wrapper {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: auto;
  min-height: 200px;
}

.schema-svg {
  width: 100%;
  min-width: 1200px;
  cursor: default;
}

/* Table styles */
.table-group {
  cursor: move;
  transition: opacity 0.2s;
}

.table-group.dragging {
  opacity: 0.7;
}

.table-rect {
  fill: white;
  stroke: #e2e8f0;
  stroke-width: 2;
}

.table-header {
  fill: #3b82f6;
  stroke: none;
}

.table-title {
  fill: white;
  font-weight: 700;
  font-size: 14px;
  pointer-events: none;
}

/* Column styles */
.column-group {
  cursor: pointer;
  transition: all 0.2s;
}

.column-rect {
  fill: white;
  stroke: #e2e8f0;
  stroke-width: 1;
  transition: all 0.2s;
}

.column-group:hover .column-rect {
  fill: #f8fafc;
  stroke: #cbd5e1;
}

.column-group.column-dragging .column-rect {
  fill: #dbeafe;
  stroke: #3b82f6;
  stroke-width: 2;
}

.column-group.column-drop-target .column-rect {
  fill: #d1fae5;
  stroke: #10b981;
  stroke-width: 2;
  animation: pulse 0.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.column-name {
  fill: #334155;
  font-size: 12px;
  font-weight: 500;
  pointer-events: none;
}

.column-type {
  fill: #1e40af;
  font-size: 11px;
  font-weight: 600;
  pointer-events: none;
}

.drag-indicator {
  fill: #94a3b8;
  font-size: 10px;
  pointer-events: none;
}

/* Relationship styles */
.relationship-group {
  cursor: default;
}

.relationship-line {
  transition: all 0.2s;
  pointer-events: none;
}

.relationship-group:hover .relationship-line {
  stroke: #2563eb;
  stroke-width: 3;
}

.label-bg {
  fill: white;
  stroke: #3b82f6;
  stroke-width: 1;
}

.relationship-label {
  fill: #1e40af;
  font-size: 10px;
  font-weight: 600;
  pointer-events: none;
}

.btn-remove-rel {
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.relationship-group:hover .btn-remove-rel {
  opacity: 1;
}

.btn-remove-rel:hover circle {
  fill: #dc2626;
}

.drag-line {
  pointer-events: none;
}
</style>
