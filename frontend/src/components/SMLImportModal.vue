<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Import Schema (SML)</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Tab Navigation -->
        <div class="tabs">
          <button 
            :class="['tab', { active: activeTab === 'paste' }]"
            @click="activeTab = 'paste'"
          >
            Paste YAML
          </button>
          <button 
            :class="['tab', { active: activeTab === 'upload' }]"
            @click="activeTab = 'upload'"
          >
            Upload File
          </button>
        </div>

        <!-- Paste Tab -->
        <div v-if="activeTab === 'paste'" class="tab-content">
          <!-- Quick Templates -->
          <div class="template-buttons">
            <button @click="loadTemplate('basic')" class="template-btn">📝 Basic Example</button>
            <button @click="loadTemplate('withFK')" class="template-btn">🔗 With Foreign Key</button>
            <button @click="loadTemplate('advanced')" class="template-btn">⚡ Advanced</button>
            <button @click="showHelp = !showHelp" class="template-btn help-btn">❓ Help</button>
          </div>

          <!-- Help Section -->
          <div v-if="showHelp" class="help-section">
            <h4>📖 Quick Reference</h4>
            <div class="help-content">
              <div class="help-item">
                <strong>Basic Structure:</strong>
                <code>dialect: MySQL | PostgreSQL | SQLite</code>
              </div>
              <div class="help-item">
                <strong>Column with length:</strong>
                <code>type: VARCHAR<br>precision: 50</code>
                <small>❌ NOT: type: VARCHAR(50)</small>
              </div>
              <div class="help-item">
                <strong>Decimal types:</strong>
                <code>type: DECIMAL<br>precision: 10<br>scale: 2</code>
              </div>
              <div class="help-item">
                <strong>Constraints:</strong>
                <code>primary_key: true<br>not_null: true<br>unique: true</code>
              </div>
              <div class="help-item">
                <strong>Default value:</strong>
                <code>has_default: true<br>default_value: 0</code>
              </div>
              <div class="help-item">
                <strong>Check constraint:</strong>
                <code>has_check: true<br>check_condition: "age > 18"</code>
              </div>
              <div class="help-item">
                <strong>Foreign key:</strong>
                <code>foreign_key:<br>&nbsp;&nbsp;table: users<br>&nbsp;&nbsp;column: id</code>
              </div>
            </div>
          </div>

          <textarea
            v-model="smlContent"
            class="sml-input"
            :class="{ 'with-help': showHelp }"
            placeholder="Paste your SML YAML content here or click a template button above..."
            rows="15"
            @input="validateSML"
          ></textarea>
        </div>

        <!-- Upload Tab -->
        <div v-if="activeTab === 'upload'" class="tab-content">
          <div class="upload-area" @drop.prevent="handleDrop" @dragover.prevent>
            <input
              ref="fileInput"
              type="file"
              accept=".yaml,.yml,.sml"
              @change="handleFileSelect"
              style="display: none"
            />
            <div class="upload-prompt">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="17 8 12 3 7 8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="3" x2="12" y2="15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <p>Drag and drop your .yaml or .yml file here</p>
              <p class="or-text">or</p>
              <button class="browse-btn" @click="$refs.fileInput.click()">
                Browse Files
              </button>
            </div>
            <p v-if="fileName" class="file-name">Selected: {{ fileName }}</p>
          </div>
        </div>

        <!-- Validation Feedback -->
        <div v-if="validationError" class="error-message">
          <strong>Error:</strong> {{ validationError }}
        </div>
        <div v-if="validationSuccess" class="success-message">
          <strong>✓</strong> {{ validationSuccess }}
        </div>

        <!-- Preview Section -->
        <div v-if="parsedSchema" class="preview-section">
          <h3>Schema Preview</h3>
          <div class="preview-content">
            <p><strong>Dialect:</strong> {{ parsedSchema.dialect }}</p>
            <p><strong>Tables:</strong> {{ parsedSchema.tables.length }}</p>
            <p><strong>Relationships:</strong> {{ parsedSchema.relationships.length }}</p>
            <div class="table-list">
              <div v-for="table in parsedSchema.tables" :key="table.name" class="table-item">
                <strong>{{ table.name }}</strong> ({{ table.columns.length }} columns)
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal">Cancel</button>
        <button 
          class="btn btn-primary" 
          @click="importSchema"
          :disabled="!smlContent || validationError || isImporting"
        >
          {{ isImporting ? 'Importing...' : 'Import Schema' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'SMLImportModal',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      activeTab: 'paste',
      smlContent: '',
      fileName: '',
      validationError: null,
      validationSuccess: null,
      parsedSchema: null,
      isImporting: false,
      validationTimeout: null,
      showHelp: false
    };
  },
  methods: {
    loadTemplate(type) {
      const templates = {
        basic: `dialect: MySQL
tables:
  - name: users
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: username
        type: VARCHAR
        precision: 50
        not_null: true
        unique: true
      - name: email
        type: VARCHAR
        precision: 100
        not_null: true
      - name: created_at
        type: TIMESTAMP
        has_default: true
        default_value: CURRENT_TIMESTAMP`,
        
        withFK: `dialect: MySQL
tables:
  - name: departments
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: name
        type: VARCHAR
        precision: 100
        not_null: true
        unique: true

  - name: employees
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: name
        type: VARCHAR
        precision: 100
        not_null: true
      - name: department_id
        type: INT
        not_null: true
        foreign_key:
          table: departments
          column: id
      - name: salary
        type: DECIMAL
        precision: 10
        scale: 2
        has_check: true
        check_condition: "salary > 0"`,
        
        advanced: `dialect: MySQL
tables:
  - name: customers
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: email
        type: VARCHAR
        precision: 255
        not_null: true
        unique: true
      - name: name
        type: VARCHAR
        precision: 100
        not_null: true

  - name: products
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: name
        type: VARCHAR
        precision: 200
        not_null: true
      - name: price
        type: DECIMAL
        precision: 10
        scale: 2
        not_null: true
        has_check: true
        check_condition: "price >= 0"
      - name: stock
        type: INT
        not_null: true
        has_default: true
        default_value: "0"

  - name: orders
    columns:
      - name: id
        type: INT
        primary_key: true
        not_null: true
      - name: customer_id
        type: INT
        not_null: true
        foreign_key:
          table: customers
          column: id
      - name: total_amount
        type: DECIMAL
        precision: 10
        scale: 2
        not_null: true`
      };
      
      this.smlContent = templates[type] || '';
      this.validateSML();
    },
    closeModal() {
      this.$emit('close');
      this.resetModal();
    },
    resetModal() {
      this.smlContent = '';
      this.fileName = '';
      this.validationError = null;
      this.validationSuccess = null;
      this.parsedSchema = null;
      this.activeTab = 'paste';
    },
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.fileName = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.smlContent = e.target.result;
          this.validateSML();
        };
        reader.readAsText(file);
      }
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0];
      if (file && (file.name.endsWith('.yaml') || file.name.endsWith('.yml') || file.name.endsWith('.sml'))) {
        this.fileName = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.smlContent = e.target.result;
          this.validateSML();
        };
        reader.readAsText(file);
      } else {
        this.validationError = 'Please upload a .yaml, .yml, or .sml file';
      }
    },
    validateSML() {
      // Clear previous timeout
      if (this.validationTimeout) {
        clearTimeout(this.validationTimeout);
      }

      // Debounce validation
      this.validationTimeout = setTimeout(async () => {
        if (!this.smlContent.trim()) {
          this.validationError = null;
          this.validationSuccess = null;
          this.parsedSchema = null;
          return;
        }

        try {
          const response = await api.importSML(this.smlContent);
          this.parsedSchema = response.data;
          this.validationSuccess = response.data.message;
          this.validationError = null;
        } catch (error) {
          this.validationError = error.response?.data?.detail || 'Invalid SML format';
          this.validationSuccess = null;
          this.parsedSchema = null;
        }
      }, 500);
    },
    async importSchema() {
      if (!this.parsedSchema) {
        return;
      }

      this.isImporting = true;
      try {
        // Emit the parsed schema to parent component
        this.$emit('import', {
          tables: this.parsedSchema.tables,
          relationships: this.parsedSchema.relationships,
          dialect: this.parsedSchema.dialect
        });
        this.closeModal();
      } catch (error) {
        this.validationError = 'Failed to import schema';
      } finally {
        this.isImporting = false;
      }
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.tab {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  transition: all 0.2s;
}

.tab.active {
  color: #4CAF50;
  border-bottom-color: #4CAF50;
}

.tab:hover {
  color: #333;
}

.tab-content {
  margin-top: 20px;
}

.sml-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 300px;
}

.sml-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.sml-input.with-help {
  min-height: 200px;
}

.template-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.template-btn {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  color: #333;
}

.template-btn:hover {
  background: #e8e8e8;
  border-color: #4CAF50;
}

.template-btn.help-btn {
  margin-left: auto;
  background: #e3f2fd;
  border-color: #2196F3;
  color: #1976D2;
}

.template-btn.help-btn:hover {
  background: #bbdefb;
}

.help-section {
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.help-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1rem;
}

.help-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.help-item {
  background: white;
  padding: 10px;
  border-radius: 4px;
  border-left: 3px solid #4CAF50;
}

.help-item strong {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-size: 0.85rem;
}

.help-item code {
  display: block;
  background: #f5f5f5;
  padding: 6px 8px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: #d32f2f;
  line-height: 1.4;
  white-space: pre-wrap;
}

.help-item small {
  display: block;
  margin-top: 4px;
  color: #f44336;
  font-size: 0.75rem;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #4CAF50;
  background: #f9f9f9;
}

.upload-prompt svg {
  color: #999;
  margin-bottom: 15px;
}

.upload-prompt p {
  margin: 10px 0;
  color: #666;
}

.or-text {
  color: #999;
  font-size: 0.9rem;
}

.browse-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.browse-btn:hover {
  background: #45a049;
}

.file-name {
  margin-top: 15px;
  color: #4CAF50;
  font-weight: 500;
}

.error-message {
  margin-top: 15px;
  padding: 12px;
  background: #ffebee;
  border-left: 4px solid #f44336;
  border-radius: 4px;
  color: #c62828;
}

.success-message {
  margin-top: 15px;
  padding: 12px;
  background: #e8f5e9;
  border-left: 4px solid #4CAF50;
  border-radius: 4px;
  color: #2e7d32;
}

.preview-section {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.preview-section h3 {
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  color: #333;
}

.preview-content p {
  margin: 8px 0;
  color: #555;
}

.table-list {
  margin-top: 15px;
  max-height: 150px;
  overflow-y: auto;
}

.table-item {
  padding: 8px;
  background: white;
  margin-bottom: 5px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
