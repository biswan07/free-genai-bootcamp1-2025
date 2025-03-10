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
  getByGroup: (groupId) => api.get(`/words?group_id=${groupId}`),
  create: (data) => api.post('/words', data),
  update: (id, data) => api.put(`/words/${id}`, data),
};

export const groupsAPI = {
  getAll: () => api.get('/groups'),
  getById: (id) => api.get(`/groups/${id}`),
  create: (data) => api.post('/groups', data),
};

export const studySessionsAPI = {
  getAll: () => api.get('/study-sessions'),
  getById: (id) => api.get(`/study-sessions/${id}`),
  create: (data) => api.post('/study-sessions', data),
  recordWordReview: (data) => api.post('/word-reviews', data),
};

export const quizAPI = {
  generate: (data) => api.post('/quiz/generate', data),
  submitAnswer: (data) => api.post('/quiz/answer', data),
  getSummary: (sessionId) => api.get(`/quiz/summary/${sessionId}`),
};

const apiExports = {
  dashboardAPI,
  studyActivitiesAPI,
  wordsAPI,
  groupsAPI,
  studySessionsAPI,
  quizAPI,
};

export default apiExports;
