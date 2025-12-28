<template>
  <div class="main-page">
    <div class="content-container">
      <QueryInput @sql-generated="onSqlGenerated" @sql-loading="onSqlLoading" />
      <ResultDisplay :result="sqlResult" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import QueryInput from './QueryInput.vue';
import ResultDisplay from './ResultDisplay.vue';

const sqlResult = ref(null);

const onSqlGenerated = (result) => {
  sqlResult.value = result;
};

const onSqlLoading = () => {
  sqlResult.value = null;
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
