import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false // Important for CORS
});

// Add response interceptor to handle errors
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const dashboardAPI = {
  getLastStudySession: () => api.get('/dashboard/last_study_session'),
  getStudyProgress: () => api.get('/dashboard/study_progress'),
  getQuickStats: () => api.get('/dashboard/quick_stats'),
};

export const studyActivitiesAPI = {
  getAll: () => api.get('/study_activities'),
  getById: (id) => api.get(`/study_activities/${id}`),
  getStudySessions: (id) => api.get(`/study_activities/${id}/study_sessions`),
  create: (data) => api.post('/study_activities', data),
};

export const wordsAPI = {
  getAll: (page = 1) => api.get(`/words?page=${page}`),
  getById: (id) => api.get(`/words/${id}`),
  create: (data) => api.post('/words', data),
};

export const studySessionsAPI = {
  getById: (id) => api.get(`/study_sessions/${id}`),
};

const apiExports = {
  dashboardAPI,
  studyActivitiesAPI,
  wordsAPI,
  studySessionsAPI,
};

export default apiExports;
