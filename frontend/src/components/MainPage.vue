<template>
  <div class="main-page">
    <div class="content-container">
      <QueryInput 
        @sql-generated="onSqlGenerated" 
        @sql-loading="onSqlLoading" 
        :current-suggestions="currentSuggestions"
      />
      <ResultDisplay :result="sqlResult" @suggestions-fetched="onSuggestionsFetched" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import QueryInput from './QueryInput.vue';
import ResultDisplay from './ResultDisplay.vue';

const sqlResult = ref(null);
const currentSuggestions = ref(null);

const onSqlGenerated = (result) => {
  sqlResult.value = result;
  currentSuggestions.value = result?.suggestions || null;
};

const onSqlLoading = () => {
  sqlResult.value = null;
  currentSuggestions.value = null;
};

const onSuggestionsFetched = (suggestions) => {
  currentSuggestions.value = suggestions;
  if (sqlResult.value) {
    sqlResult.value.suggestions = suggestions;
  }
};
</script>

<style scoped>
.main-page {
  min-height: calc(100vh - 100px);
  padding: 40px 20px;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
