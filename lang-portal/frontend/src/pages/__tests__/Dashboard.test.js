import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';
import { dashboardAPI } from '../../services/api';

// Mock the API module
jest.mock('../../services/api', () => ({
  dashboardAPI: {
    getLastStudySession: jest.fn(),
    getQuickStats: jest.fn(),
  },
}));

describe('Dashboard', () => {
  beforeEach(() => {
    // Reset mock implementations before each test
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    dashboardAPI.getLastStudySession.mockResolvedValue({ data: {} });
    dashboardAPI.getQuickStats.mockResolvedValue({ data: {} });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
  });

  it('renders error state when API fails', async () => {
    dashboardAPI.getLastStudySession.mockRejectedValue(new Error('API Error'));
    dashboardAPI.getQuickStats.mockRejectedValue(new Error('API Error'));

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading dashboard data/i)).toBeInTheDocument();
    });
  });

  it('renders dashboard data successfully', async () => {
    const mockLastSession = {
      has_sessions: true,
      stats: {
        total_words: 10,
        correct_words: 8,
      },
      activity: {
        name: 'Flashcards',
      },
      group: {
        name: 'Test Group',
      },
    };

    const mockQuickStats = {
      total_words: 100,
      total_groups: 5,
      study_sessions: 20,
      study_streak: 3,
      words_studied: 50,
    };

    dashboardAPI.getLastStudySession.mockResolvedValue({ data: mockLastSession });
    dashboardAPI.getQuickStats.mockResolvedValue({ data: mockQuickStats });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Flashcards/i)).toBeInTheDocument();
      expect(screen.getByText(/Test Group/i)).toBeInTheDocument();
      expect(screen.getByText(/100 Total Words/i)).toBeInTheDocument();
      expect(screen.getByText(/5 Groups/i)).toBeInTheDocument();
      expect(screen.getByText(/3 Day Streak/i)).toBeInTheDocument();
    });
  });
});
