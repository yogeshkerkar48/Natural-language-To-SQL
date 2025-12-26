import axios from 'axios';

// Use relative URL for API calls - works with nginx proxy and ngrok
// When using nginx (port 8081), /api requests are proxied to backend (port 8000)
// For direct backend access, set VITE_API_URL environment variable
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  generate(question, tables, relationships, database_type = "MySQL") {
    return apiClient.post('/generate', {
      question,
      tables,
      relationships,
      database_type
    });
  },
  saveProject(name, state) {
    return apiClient.post('/projects', { name, state });
  },
  listProjects() {
    return apiClient.get('/projects');
  },
  getProject(id) {
    return apiClient.get(`/projects/${id}`);
  },
  deleteProject(id) {
    return apiClient.delete(`/projects/${id}`);
  }
};
