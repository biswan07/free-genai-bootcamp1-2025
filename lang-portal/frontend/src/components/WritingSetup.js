import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Container, Typography, Button, Box, Card, CardContent, CircularProgress, Alert } from '@mui/material';
import { writingAPI } from '../services/api';

const WritingSetup = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const studyActivityId = queryParams.get('activityId');
  const groupId = queryParams.get('groupId');

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await writingAPI.getPrompts();
      setPrompts(response.data.prompts);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching writing prompts:', err);
      setError('Failed to load writing prompts. Please try again later.');
      setLoading(false);
    }
  };

  const handlePromptSelect = (prompt) => {
    setSelectedPrompt(prompt);
  };

  const handleStartWriting = () => {
    if (selectedPrompt) {
      navigate(`/study/${studyActivityId}/writing`, { 
        state: { 
          prompt: selectedPrompt,
          studyActivityId,
          groupId
        } 
      });
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading writing prompts...
        </Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={fetchPrompts} 
          sx={{ mt: 2 }}
        >
          Try Again
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Writing Practice
      </Typography>
      <Typography variant="body1" paragraph>
        Choose a writing prompt below. You'll need to write a response of 50-200 words, and you'll receive AI-powered feedback on your writing.
      </Typography>

      <Box sx={{ mt: 3, mb: 3 }}>
        {prompts.map((prompt, index) => (
          <Card 
            key={index} 
            sx={{ 
              mb: 2, 
              cursor: 'pointer',
              border: selectedPrompt === prompt ? '2px solid #1976d2' : 'none',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 3
              }
            }}
            onClick={() => handlePromptSelect(prompt)}
          >
            <CardContent>
              <Typography variant="h6">{prompt}</Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button 
          variant="contained" 
          color="primary" 
          size="large"
          disabled={!selectedPrompt}
          onClick={handleStartWriting}
        >
          Start Writing
        </Button>
      </Box>
    </Container>
  );
};

export default WritingSetup;
