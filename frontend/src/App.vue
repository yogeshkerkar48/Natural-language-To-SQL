<template>
  <div class="app-container">
    <header>
      <h1>NL2SQL Generator</h1>
      <p>Convert Natural Language to MySQL Queries</p>
    </header>

    <main>
      <QueryInput @sql-generated="onSqlGenerated" @sql-loading="onSqlLoading" />
      <ResultDisplay :result="sqlResult" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import QueryInput from './components/QueryInput.vue';
import ResultDisplay from './components/ResultDisplay.vue';

const sqlResult = ref(null);

const onSqlGenerated = (result) => {
  sqlResult.value = result;
};

const onSqlLoading = () => {
  sqlResult.value = null;
};
</script>

<style scoped>
.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: 'Inter', sans-serif;
  color: #333;
}

header {
  text-align: center;
  margin-bottom: 40px;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
