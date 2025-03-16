import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Button, 
  CircularProgress, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  Divider,
  Alert
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { quizAPI } from '../services/api';

const QuizSummary = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId } = location.state || {};
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (sessionId) {
      fetchSummary();
    } else {
      setError('No session ID provided');
      setLoading(false);
    }
  }, [sessionId]);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await quizAPI.getSummary(sessionId);
      setSummary(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching quiz summary:', err);
      setError('Failed to load quiz summary. Please try again later.');
      setLoading(false);
    }
  };

  const handleFinish = () => {
    navigate('/study');
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading quiz summary...
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
          onClick={handleFinish} 
          sx={{ mt: 2 }}
        >
          Back to Study
        </Button>
      </Container>
    );
  }

  if (!summary) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="warning">No summary data available.</Alert>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleFinish} 
          sx={{ mt: 2 }}
        >
          Back to Study
        </Button>
      </Container>
    );
  }

  const correctCount = summary.questions?.filter(q => q.is_correct).length || 0;
  const totalCount = summary.questions?.length || 0;
  const score = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Quiz Summary
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" sx={{ mr: 2 }}>
            Score:
          </Typography>
          <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
            {score}% ({correctCount}/{totalCount})
          </Typography>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="h6" gutterBottom>
          Question Review:
        </Typography>
        
        <List>
          {summary.questions?.map((question, index) => (
            <React.Fragment key={index}>
              <ListItem alignItems="flex-start">
                <ListItemIcon>
                  {question.is_correct ? 
                    <CheckCircleIcon color="success" /> : 
                    <CancelIcon color="error" />
                  }
                </ListItemIcon>
                <ListItemText
                  primary={`Question ${index + 1}: ${question.question}`}
                  secondary={
                    <>
                      <Typography component="span" variant="body2" color="text.primary">
                        Your answer: {question.selected_answer}
                      </Typography>
                      {!question.is_correct && (
                        <Typography component="span" variant="body2" color="success.main" sx={{ display: 'block' }}>
                          Correct answer: {question.correct_answer}
                        </Typography>
                      )}
                      {question.explanation && (
                        <Typography component="span" variant="body2" sx={{ display: 'block', mt: 1 }}>
                          {question.explanation}
                        </Typography>
                      )}
                    </>
                  }
                />
              </ListItem>
              {index < summary.questions.length - 1 && <Divider variant="inset" component="li" />}
            </React.Fragment>
          ))}
        </List>
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={handleFinish}
          sx={{ minWidth: 200 }}
        >
          Finish
        </Button>
      </Box>
    </Container>
  );
};

export default QuizSummary;
