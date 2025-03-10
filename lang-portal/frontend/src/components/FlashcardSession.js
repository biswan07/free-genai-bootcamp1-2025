import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Button, 
  Paper, 
  Alert,
  LinearProgress,
  Container
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import Flashcard from './Flashcard';
import { wordsAPI, studySessionsAPI } from '../services/api';

const FlashcardSession = () => {
  const { groupId, activityId, wordCount } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [words, setWords] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [results, setResults] = useState({ correct: 0, incorrect: 0 });
  const [sessionComplete, setSessionComplete] = useState(false);

  // Fetch words and create a new study session
  useEffect(() => {
    const fetchWordsAndCreateSession = async () => {
      try {
        // Fetch all words from the database
        const wordsResponse = await wordsAPI.getAll();
        
        // Check if we have words in the response
        if (!wordsResponse.data.words || wordsResponse.data.words.length === 0) {
          setError('No words available in the database');
          setLoading(false);
          return;
        }
        
        // Shuffle the words array
        const shuffledWords = [...wordsResponse.data.words].sort(() => Math.random() - 0.5);
        
        // If wordCount is specified, limit the number of words
        const selectedWords = wordCount 
          ? shuffledWords.slice(0, parseInt(wordCount)) 
          : shuffledWords;
          
        setWords(selectedWords);
        
        // Create a new study session
        // If groupId is not provided, use 1 as default or create a special session type
        const sessionResponse = await studySessionsAPI.create({
          group_id: parseInt(groupId || 1),
          study_activity_id: parseInt(activityId)
        });
        
        setSessionId(sessionResponse.data.id);
        setLoading(false);
      } catch (err) {
        console.error('Error setting up flashcard session:', err);
        setError('Failed to load flashcards. Please try again later.');
        setLoading(false);
      }
    };

    fetchWordsAndCreateSession();
  }, [groupId, activityId, wordCount]);

  const handleCorrect = async (wordId) => {
    try {
      await studySessionsAPI.recordWordReview({
        word_id: wordId,
        study_session_id: sessionId,
        correct: true
      });
      
      setResults(prev => ({ ...prev, correct: prev.correct + 1 }));
      moveToNextCard();
    } catch (err) {
      console.error('Error recording correct response:', err);
      setError('Failed to record your response. Please try again.');
    }
  };

  const handleIncorrect = async (wordId) => {
    try {
      await studySessionsAPI.recordWordReview({
        word_id: wordId,
        study_session_id: sessionId,
        correct: false
      });
      
      setResults(prev => ({ ...prev, incorrect: prev.incorrect + 1 }));
      moveToNextCard();
    } catch (err) {
      console.error('Error recording incorrect response:', err);
      setError('Failed to record your response. Please try again.');
    }
  };

  const moveToNextCard = () => {
    if (currentIndex < words.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setSessionComplete(true);
    }
  };

  const handleFinishSession = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="50vh">
          <CircularProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>Loading flashcards...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        <Button variant="contained" onClick={() => navigate('/study')}>
          Back to Study Activities
        </Button>
      </Container>
    );
  }

  if (sessionComplete) {
    const totalCards = results.correct + results.incorrect;
    const successRate = totalCards > 0 ? Math.round((results.correct / totalCards) * 100) : 0;
    
    return (
      <Container>
        <Paper sx={{ p: 3, my: 3 }}>
          <Typography variant="h4" gutterBottom>Session Complete!</Typography>
          
          <Box sx={{ my: 3 }}>
            <Typography variant="h6" gutterBottom>Your Results:</Typography>
            <Typography>Cards reviewed: {totalCards}</Typography>
            <Typography>Correct answers: {results.correct}</Typography>
            <Typography>Success rate: {successRate}%</Typography>
          </Box>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleFinishSession}
            sx={{ mt: 2 }}
          >
            Return to Dashboard
          </Button>
        </Paper>
      </Container>
    );
  }

  const progress = Math.round(((currentIndex + 1) / words.length) * 100);

  return (
    <Container>
      <Paper sx={{ p: 3, my: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>Flashcard Session</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" sx={{ mr: 1 }}>
              Progress: {currentIndex + 1} of {words.length}
            </Typography>
            <Typography variant="body2" sx={{ ml: 'auto' }}>
              {progress}%
            </Typography>
          </Box>
          <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
        </Box>

        {words.length > 0 && currentIndex < words.length && (
          <Flashcard 
            word={words[currentIndex]} 
            onCorrect={handleCorrect} 
            onIncorrect={handleIncorrect} 
            onNext={moveToNextCard}
          />
        )}
      </Paper>
    </Container>
  );
};

export default FlashcardSession;
