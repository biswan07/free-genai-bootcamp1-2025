import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5001/api',
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
  getAll: () => api.get('/study_sessions'),
  getById: (id) => api.get(`/study_sessions/${id}`),
  create: (data) => api.post('/study_sessions', data),
  recordWordReview: ({ word_id, study_session_id, correct }) => 
    api.post(`/study_sessions/${study_session_id}/words/${word_id}/review`, { is_correct: correct }),
};

export const quizAPI = {
  generate: (data) => api.post('/quiz/generate', data),
  submitAnswer: (data) => api.post('/quiz/answer', data),
  getSummary: (sessionId) => api.get(`/quiz/summary/${sessionId}`),
};

export const writingAPI = {
  getPrompts: (count = 10, level = 'intermediate') => 
    api.get(`/writing/prompts?count=${count}&level=${level}`),
  submitWriting: (data) => api.post('/writing/submit', data),
  getSummary: (sessionId) => api.get(`/writing/summary/${sessionId}`),
};

const apiExports = {
  dashboardAPI,
  studyActivitiesAPI,
  wordsAPI,
  groupsAPI,
  studySessionsAPI,
  quizAPI,
  writingAPI,
};

export default apiExports;
