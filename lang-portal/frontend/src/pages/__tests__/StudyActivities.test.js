import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import StudyActivities from '../StudyActivities';
import { studyActivitiesAPI } from '../../services/api';

// Mock the API module
jest.mock('../../services/api', () => ({
  studyActivitiesAPI: {
    getAll: jest.fn(),
  },
}));

describe('StudyActivities', () => {
  beforeEach(() => {
    // Reset mock implementations before each test
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    studyActivitiesAPI.getAll.mockResolvedValue({ data: [] });

    render(
      <BrowserRouter>
        <StudyActivities />
      </BrowserRouter>
    );

    expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
  });

  it('renders error state when API fails', async () => {
    studyActivitiesAPI.getAll.mockRejectedValue(new Error('API Error'));

    render(
      <BrowserRouter>
        <StudyActivities />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading study activities/i)).toBeInTheDocument();
    });
  });

  it('renders study activities successfully', async () => {
    const mockActivities = [
      {
        id: 1,
        name: 'Flashcards',
        description: 'Practice with flashcards',
        thumbnail_url: '/images/flashcards.png',
      },
      {
        id: 2,
        name: 'Multiple Choice',
        description: 'Test your knowledge',
        thumbnail_url: '/images/multiple-choice.png',
      },
    ];

    studyActivitiesAPI.getAll.mockResolvedValue({ data: mockActivities });

    render(
      <BrowserRouter>
        <StudyActivities />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Flashcards')).toBeInTheDocument();
      expect(screen.getByText('Multiple Choice')).toBeInTheDocument();
      expect(screen.getByText('Practice with flashcards')).toBeInTheDocument();
      expect(screen.getByText('Test your knowledge')).toBeInTheDocument();
    });
  });

  it('renders no activities message when list is empty', async () => {
    studyActivitiesAPI.getAll.mockResolvedValue({ data: [] });

    render(
      <BrowserRouter>
        <StudyActivities />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No study activities available.')).toBeInTheDocument();
    });
  });
});
