import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Box, 
  Paper, 
  CircularProgress, 
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Card,
  CardContent
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { writingAPI } from '../services/api';

const Writing = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { prompt, studyActivityId, groupId } = location.state || {};
  
  const [text, setText] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    // Redirect if no prompt is available
    if (!prompt) {
      navigate('/study');
    }
  }, [prompt, navigate]);

  useEffect(() => {
    // Update word count when text changes
    const words = text.trim() ? text.trim().split(/\s+/) : [];
    setWordCount(words.length);
  }, [text]);

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setError(null);

      // Validate word count
      if (wordCount < 50) {
        setError('Your response is too short. Please write at least 50 words.');
        setSubmitting(false);
        return;
      }

      if (wordCount > 200) {
        setError('Your response is too long. Please write no more than 200 words.');
        setSubmitting(false);
        return;
      }

      // Submit the writing for evaluation
      const response = await writingAPI.submitWriting({
        prompt,
        text,
        study_activity_id: studyActivityId,
        group_id: groupId
      });

      setFeedback(response.data);
      if (response.data.session_id) {
        setSessionId(response.data.session_id);
      }
      setSubmitting(false);
    } catch (err) {
      console.error('Error submitting writing:', err);
      setError(err.response?.data?.message || 'Failed to submit writing. Please try again.');
      setSubmitting(false);
    }
  };

  const handleTryAgain = () => {
    setFeedback(null);
    setText('');
    setError(null);
  };

  const handleFinish = () => {
    navigate('/study');
  };

  if (!prompt) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">No writing prompt selected. Please go back and select a prompt.</Alert>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => navigate('/study')} 
          sx={{ mt: 2 }}
        >
          Back to Study
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      {!feedback ? (
        <>
          <Typography variant="h4" gutterBottom>
            Writing Practice
          </Typography>
          
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Prompt:
            </Typography>
            <Typography variant="body1" paragraph>
              {prompt}
            </Typography>
          </Paper>

          <TextField
            label="Your response (50-200 words)"
            multiline
            rows={10}
            value={text}
            onChange={handleTextChange}
            fullWidth
            variant="outlined"
            disabled={submitting}
            error={wordCount > 200}
            helperText={`Word count: ${wordCount}/200 ${wordCount < 50 ? '(minimum 50 words)' : wordCount > 200 ? '(maximum 200 words)' : ''}`}
            sx={{ mb: 3 }}
          />

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleSubmit}
              disabled={submitting || wordCount < 50 || wordCount > 200}
              sx={{ minWidth: 200 }}
            >
              {submitting ? <CircularProgress size={24} /> : 'Submit'}
            </Button>
          </Box>
        </>
      ) : (
        <>
          <Typography variant="h4" gutterBottom>
            Writing Feedback
          </Typography>

          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Prompt:
            </Typography>
            <Typography variant="body1" paragraph>
              {prompt}
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Your Response:
            </Typography>
            <Typography variant="body1" paragraph>
              {text}
            </Typography>
          </Paper>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" sx={{ mr: 2 }}>
                  Score:
                </Typography>
                <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                  {feedback.score}%
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Strengths:
              </Typography>
              <List>
                {feedback.feedback?.strengths?.map((strength, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" />
                    </ListItemIcon>
                    <ListItemText primary={strength} />
                  </ListItem>
                ))}
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Areas for Improvement:
              </Typography>
              <List>
                {feedback.feedback?.areas_for_improvement?.map((area, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <ErrorIcon color="error" />
                    </ListItemIcon>
                    <ListItemText primary={area} />
                  </ListItem>
                ))}
              </List>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Detailed Analysis:
              </Typography>
              <Typography variant="body1" paragraph>
                {feedback.feedback?.detailed_analysis}
              </Typography>
            </CardContent>
          </Card>

          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="outlined"
              color="primary"
              size="large"
              onClick={handleTryAgain}
              sx={{ minWidth: 150 }}
            >
              Try Again
            </Button>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleFinish}
              sx={{ minWidth: 150 }}
            >
              Finish
            </Button>
          </Box>
        </>
      )}
    </Container>
  );
};

export default Writing;
