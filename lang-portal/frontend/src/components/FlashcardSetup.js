import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  CircularProgress,
  Button,
  Paper,
  Alert,
  TextField,
  Container,
  Slider,
  Stack
} from '@mui/material';
import { wordsAPI } from '../services/api';

const FlashcardSetup = () => {
  const { activityId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalWords, setTotalWords] = useState(0);
  const [wordCount, setWordCount] = useState(10);
  const [maxWords, setMaxWords] = useState(10);

  useEffect(() => {
    const fetchTotalWords = async () => {
      try {
        setLoading(true);
        const response = await wordsAPI.getAll();
        
        if (!response.data.words || response.data.words.length === 0) {
          setError('No words available in the database');
          setLoading(false);
          return;
        }
        
        const total = response.data.total || response.data.words.length;
        setTotalWords(total);
        setMaxWords(total);
        setWordCount(Math.min(10, total));
        setLoading(false);
      } catch (err) {
        console.error('Error fetching words:', err);
        setError('Failed to load words. Please try again later.');
        setLoading(false);
      }
    };

    fetchTotalWords();
  }, []);

  const handleWordCountChange = (event, newValue) => {
    setWordCount(newValue);
  };

  const handleInputChange = (event) => {
    const value = event.target.value === '' ? 0 : Number(event.target.value);
    setWordCount(Math.min(Math.max(1, value), maxWords));
  };

  const handleStartFlashcards = () => {
    navigate(`/study/${activityId}/flashcards/practice/${wordCount}`);
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="50vh">
          <CircularProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>Loading words...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        <Button variant="contained" onClick={() => navigate('/words')}>
          Back to Words
        </Button>
      </Container>
    );
  }

  return (
    <Container>
      <Paper sx={{ p: 3, my: 3 }}>
        <Typography variant="h4" gutterBottom>Flashcard Setup</Typography>
        
        <Box sx={{ my: 4 }}>
          <Typography variant="h6" gutterBottom>
            There are {totalWords} words available in the database.
          </Typography>
          <Typography variant="body1" gutterBottom>
            How many words would you like to practice?
          </Typography>
          
          <Stack spacing={2} direction="row" sx={{ mb: 1 }} alignItems="center">
            <Typography>1</Typography>
            <Slider
              value={wordCount}
              onChange={handleWordCountChange}
              aria-labelledby="word-count-slider"
              valueLabelDisplay="auto"
              step={1}
              min={1}
              max={maxWords}
              sx={{ mx: 2 }}
            />
            <Typography>{maxWords}</Typography>
          </Stack>
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', my: 2 }}>
            <TextField
              value={wordCount}
              onChange={handleInputChange}
              inputProps={{
                step: 1,
                min: 1,
                max: maxWords,
                type: 'number',
                'aria-labelledby': 'word-count-slider',
              }}
              sx={{ width: '100px' }}
            />
            <Typography variant="body1" sx={{ ml: 2 }}>words</Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button variant="outlined" onClick={() => navigate('/words')}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleStartFlashcards}
            disabled={wordCount < 1}
          >
            Start Flashcards
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default FlashcardSetup;
