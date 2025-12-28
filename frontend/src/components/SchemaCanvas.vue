<template>
  <div class="schema-canvas">
    <div class="header">
      <h3><span class="icon">📊</span> Schema Diagram</h3>
    </div>
    
    <div class="canvas-container">
      <!-- Mermaid diagram will be rendered here -->
      <div v-if="error" class="error-msg">{{ error }}</div>
      <div v-else class="mermaid" v-html="mermaidHtml"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
import mermaid from 'mermaid';

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

const mermaidHtml = ref('');
const error = ref(null);

mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
});

const generateMermaidSyntax = () => {
  if (!props.tables.length) return '';

  let syntax = 'classDiagram\n  direction LR\n';

  // Add Tables (Classes)
  props.tables.forEach(table => {
    // Sanitize table name for Mermaid ID, but use raw name in backticks for display/keyword safety
    const tableId = table.name.replace(/\s+/g, '_');
    if (!tableId) return;
    
    try {
      syntax += `  class \`${table.name}\` {\n`;
      table.columns.forEach(col => {
        if (col.name && col.type) {
           // Format: Name Type (No colon in classDiagram members for types in standard mermaid)
           // Actually classDiagram uses "type name" or "name type" depending on version
           // Let's use name : type format which is usually safe in newer versions
           syntax += `    ${col.name}: ${col.type}\n`;
        }
      });
      syntax += `  }\n`;
    } catch (e) {
      console.warn("Skipping invalid table definition", e);
    }
  });

  // Add Relationships
  props.relationships.forEach(rel => {
    if (rel.from_table && rel.to_table && rel.from_column && rel.to_column) {
      // Use backticks for table names to handle spaces or reserved keywords
      const fromName = `\`${rel.from_table}\``;
      const toName = `\`${rel.to_table}\``;
      // Use standard relationship notation
      syntax += `  ${fromName} --> ${toName} : "${rel.from_column} -> ${rel.to_column}"\n`;
    }
  });

  return syntax;
};

const renderDiagram = async () => {
  const code = generateMermaidSyntax();
  if (!code) {
    mermaidHtml.value = '';
    return;
  }
  
  try {
    error.value = null;
    // mermaid.render returns an object { svg } in newer versions
    // We use a unique ID each time to prevent caching issues
    const { svg } = await mermaid.render(`mermaid-${Date.now()}`, code);
    mermaidHtml.value = svg;
  } catch (e) {
    console.error('Mermaid render error:', e);
    // Don't show error immediately as user might be typing
    // error.value = 'Failed to render diagram'; 
  }
};

watch([() => props.tables, () => props.relationships], () => {
  renderDiagram();
}, { deep: true });

onMounted(() => {
  renderDiagram();
});
</script>

<style scoped>
.schema-canvas {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  overflow: hidden;
}

.header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
}

.canvas-container {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  min-height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow-x: auto;
}

.error-msg {
  color: #ef4444;
  font-size: 0.9rem;
}
</style>
