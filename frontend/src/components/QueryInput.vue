<template>
  <div class="query-input-container">
    <!-- Project Actions -->
    <div class="project-actions">
      <div v-if="currentProjectName" class="current-project">
        <span class="folder-icon">📂</span>
        <span class="project-name">{{ currentProjectName }}</span>
        <button @click="unloadProject" class="unload-btn" title="Unload Project">×</button>
      </div>
      <button @click="showLoadModal = true" class="btn secondary-project small">📂 Load Project</button>
      <button 
        @click="handleSaveProjectCurrent" 
        :disabled="!currentProjectName || tables.length === 0 || savingProject" 
        class="btn secondary-project small"
      >
        <span v-if="savingProjectCurrent" class="spinner-small"></span>
        💾 Save
      </button>
      <button @click="showSaveModal = true" :disabled="tables.length === 0" class="btn secondary-project small">💾 Save As...</button>
    </div>

    <!-- Visual Schema Builder -->
    <SchemaBuilder 
      :key="`builder-${componentKey}`" 
      v-model="tables" 
      @schema-imported="handleSchemaImported"
    />

    <!-- Interactive Schema Diagram with Drag & Drop -->
    <InteractiveSchemaCanvas :key="`canvas-${componentKey}`" :tables="tables" :relationships="relationships" @update:relationships="relationships = $event" />

    <!-- Question Input -->
    <div class="card query-card">
      <div class="card-header">
        <div class="icon-wrapper question-icon">❓</div>
        <div>
          <h3>Ask Your Question</h3>
          <p class="hint">Natural language query about your schema</p>
        </div>
        
        <!-- Database Type Selector -->
        <div class="db-selector">
          <label for="db-type">Dialect:</label>
          <select id="db-type" v-model="databaseType" class="db-select">
            <option value="MySQL">MySQL</option>
            <option value="PostgreSQL">PostgreSQL</option>
            <option value="SQLite">SQLite</option>
            <option value="SQL Server">SQL Server</option>
            <option value="Oracle">Oracle</option>
          </select>
        </div>
      </div>
      <textarea 
        v-model="question" 
        placeholder="e.g., How many students are enrolled in each class?" 
        rows="3"
        class="question-input"
      ></textarea>
      
      <!-- Query History -->
      <QueryHistory ref="historyRef" :project-id="currentProjectId" @select="question = $event" />
      <button @click="generateSQL" :disabled="generating || !question || tables.length === 0" class="btn accent">
        <span v-if="generating" class="spinner"></span>
        {{ generating ? 'Generating SQL...' : '🚀 Generate SQL' }}
      </button>
      <p v-if="generating" class="loading-hint">⏳ This may take 5-10 seconds...</p>
    </div>

    <!-- Modals -->
    <SaveProjectModal 
      :show="showSaveModal" 
      :saving="savingProject"
      @close="showSaveModal = false" 
      @save="handleSaveProject" 
    />

    <LoadProjectModal 
      :show="showLoadModal" 
      :projects="savedProjects"
      :loading="loadingProjects"
      @close="showLoadModal = false" 
      @load="handleLoadProject"
      @delete="handleDeleteProject"
    />
    <ConfirmationModal
      :show="showConfirmModal"
      :title="confirmTitle"
      :message="confirmMessage"
      @close="showConfirmModal = false"
      @confirm="handleConfirm"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import api from '../services/api';
import SchemaBuilder from './SchemaBuilder.vue';
import InteractiveSchemaCanvas from './InteractiveSchemaCanvas.vue';
import SaveProjectModal from './SaveProjectModal.vue';
import LoadProjectModal from './LoadProjectModal.vue';
import ConfirmationModal from './ConfirmationModal.vue';
import QueryHistory from './QueryHistory.vue';

const historyRef = ref(null);

const props = defineProps({
  currentSuggestions: {
    type: Object,
    default: null
  }
});

// Structured state (arrays/objects instead of strings)
const tables = ref([]);
const relationships = ref([]);
const question = ref('');
const databaseType = ref('MySQL');
const generating = ref(false);
const result = ref(null);
const loading = ref(false);
const error = ref(null);
const projects = ref([]);

const emit = defineEmits(['sql-generated', 'sql-loading']);

// Persistence state
const showSaveModal = ref(false);
const showLoadModal = ref(false);
const savingProject = ref(false);
const savingProjectCurrent = ref(false);
const loadingProjects = ref(false);
const savedProjects = ref([]);
const lastGeneratedSql = ref('');
const currentProjectName = ref('');
const currentProjectId = ref(null);
const componentKey = ref(0); // Key to force re-render of components

// Modal State
const showConfirmModal = ref(false);
const confirmTitle = ref('');
const confirmMessage = ref('');
const confirmAction = ref(null);

// Listen for generated SQL to save it in state
watch(() => lastGeneratedSql.value, (newVal) => {
  // We'll keep track of the last generated SQL to save it in the project state
});

const generateSQL = async () => {
  emit('sql-loading');
  generating.value = true;
  
  try {
    const response = await api.generate(
      question.value, 
      tables.value, 
      relationships.value,
      databaseType.value,
      currentProjectId.value
    );
    lastGeneratedSql.value = response.data.sql;
    emit('sql-generated', { 
      ...response.data, 
      tables: JSON.parse(JSON.stringify(tables.value)), 
      databaseType: databaseType.value 
    });
    
    // Refresh history after successful generation
    if (historyRef.value) {
      historyRef.value.refresh();
    }
  } catch (error) {
    console.error(error);
    alert('Generation failed: ' + (error.response?.data?.detail || error.message));
  } finally {
    generating.value = false;
  }
};

const fetchProjects = async () => {
  loadingProjects.value = true;
  try {
    const response = await api.listProjects();
    savedProjects.value = response.data;
  } catch (error) {
    console.error('Failed to fetch projects:', error);
  } finally {
    loadingProjects.value = false;
  }
};

watch(showLoadModal, (newVal) => {
  if (newVal) fetchProjects();
});

const handleSaveProject = async (name) => {
  savingProject.value = true;
  await performSave(name);
  savingProject.value = false;
  showSaveModal.value = false;
};

const handleSaveProjectCurrent = async () => {
  if (!currentProjectName.value) return;
  savingProjectCurrent.value = true;
  await performSave(currentProjectName.value);
  savingProjectCurrent.value = false;
};

const performSave = async (name) => {
  const state = {
    tables: tables.value,
    relationships: relationships.value,
    question: question.value,
    databaseType: databaseType.value,
    sql: lastGeneratedSql.value,
    suggestions: props.currentSuggestions
  };

  try {
    const response = await api.saveProject(name, state);
    currentProjectName.value = name;
    if (response.data && response.data.id) {
       currentProjectId.value = response.data.id;
    }
    // No alert for silent auto-save if desired, but here we keep it for confirmation
    // maybe a toast would be better but let's stick to alert for consistency
    // alert('Project saved successfully!');
  } catch (error) {
    console.error('Failed to save project:', error);
    alert('Save failed: ' + (error.response?.data?.detail || error.message));
  }
};

const handleLoadProject = async (id) => {
  try {
    const response = await api.getProject(id);
    const { state, name, id: projectId } = response.data;
    currentProjectName.value = name;
    currentProjectId.value = projectId;
    
    // Restore state
    tables.value = state.tables || [];
    relationships.value = state.relationships || [];
    question.value = state.question || '';
    databaseType.value = state.databaseType || 'MySQL';
    
    // Force refresh of child components
    componentKey.value++;
    
    if (state.sql) {
      emit('sql-generated', { 
        sql: state.sql, 
        is_valid: true,
        tables: JSON.parse(JSON.stringify(tables.value)),
        databaseType: databaseType.value,
        suggestions: state.suggestions || null
      });
      lastGeneratedSql.value = state.sql;
    }

    showLoadModal.value = false;
  } catch (error) {
    console.error('Failed to load project:', error);
    alert('Load failed: ' + (error.response?.data?.detail || error.message));
  }
};

const unloadProject = () => {
  confirmTitle.value = 'Unload Project';
  confirmMessage.value = 'Are you sure you want to unload the current project? Any unsaved changes will be lost.';
  confirmAction.value = async () => {
    currentProjectName.value = '';
    currentProjectId.value = null;
    tables.value = [];
    relationships.value = [];
    question.value = '';
    lastGeneratedSql.value = '';
    
    await nextTick();
    componentKey.value++; // Force refresh
    emit('sql-generated', null);
  };
  showConfirmModal.value = true;
};

const handleDeleteProject = (id) => {
  confirmTitle.value = 'Delete Project';
  confirmMessage.value = 'Are you sure you want to permanently delete this project? This action cannot be undone.';
  confirmAction.value = async () => {
    try {
      await api.deleteProject(id);
      await fetchProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      alert('Delete failed: ' + (error.response?.data?.detail || error.message));
    }
  };
  showConfirmModal.value = true;
};

const handleConfirm = async () => {
  if (confirmAction.value) {
    await confirmAction.value();
  }
  showConfirmModal.value = false;
};

const handleSchemaImported = async () => {
  console.log('QueryInput: Schema imported, resetting project state...');
  
  // Reset project state to treat as new project
  currentProjectId.value = null;
  currentProjectName.value = '';
  relationships.value = [];
  question.value = '';
  lastGeneratedSql.value = '';
  
  // Reset History
  if (historyRef.value && historyRef.value.clearSelection) {
      historyRef.value.clearSelection();
  }
  
  await nextTick();
  componentKey.value++; // Force re-render of canvas and builder
  
  console.log('QueryInput: State reset complete');
};
</script>

<style scoped>
.query-input-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1000px; /* Increased width for canvas */
  margin: 0 auto;
}

.project-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.current-project {
  margin-right: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.folder-icon {
  font-size: 1.2rem;
}

.project-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.95rem;
  letter-spacing: -0.01em;
}

.unload-btn {
  background: #fee2e2;
  color: #ef4444;
  border: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  margin-left: 4px;
  transition: all 0.2s;
}

.unload-btn:hover {
  background: #fecaca;
  transform: scale(1.1);
}

.btn.secondary-project {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  width: auto;
  margin-top: 0;
  padding: 10px 18px;
  font-size: 0.9rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.btn.secondary-project:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1e293b;
}

.card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  padding: 28px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
              0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: all 0.3s ease;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.question-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hint {
  margin: 4px 0 0 0;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

.question-input {
  width: 100%;
  padding: 14px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-family: 'Inter', system-ui, sans-serif; /* changed from monospace for question */
  font-size: 1rem;
  resize: vertical;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.question-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.db-selector {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.db-selector label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}

.db-select {
  border: none;
  background: transparent;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
  outline: none;
}

.btn {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s ease;
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.accent { 
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.accent:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5);
  transform: translateY(-2px);
}

.accent:active:not(:disabled) {
  transform: translateY(0);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner-small {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(0,0,0,0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 4px;
}

.loading-hint {
  color: #64748b;
  font-size: 0.875rem;
  margin-top: 12px;
  text-align: center;
  font-weight: 500;
}
</style>
