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

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default {
  generate(question, tables, relationships, database_type = "MySQL", projectId = null) {
    return apiClient.post('/generate', {
      question,
      tables,
      relationships,
      database_type,
      project_id: projectId
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
  },
  suggestIndexes(sql, tables, database_type = "MySQL") {
    return apiClient.post('/suggest-indexes', {
      sql,
      tables,
      database_type
    });
  },
  getQueryHistory(projectId = null) {
    const params = projectId ? { project_id: projectId } : {};
    return apiClient.get('/history', { params });
  },
  deleteQueryHistory(id) {
    return apiClient.delete(`/history/${id}`);
  }
};
