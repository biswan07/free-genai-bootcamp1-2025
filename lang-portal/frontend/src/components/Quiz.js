import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  CircularProgress,
  Button,
  Paper,
  Alert,
  Container,
  Radio,
  RadioGroup,
  FormControlLabel,
  LinearProgress,
  Card,
  CardContent,
  Divider,
  Stack
} from '@mui/material';
import { quizAPI } from '../services/api';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';

const Quiz = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [answerSubmitted, setAnswerSubmitted] = useState(false);
  const [answerResult, setAnswerResult] = useState(null);
  const [quizComplete, setQuizComplete] = useState(false);
  const [summary, setSummary] = useState(null);
  
  useEffect(() => {
    const fetchQuizSession = async () => {
      try {
        setLoading(true);
        const response = await quizAPI.getSummary(sessionId);
        
        if (response.data.questions && response.data.questions.length > 0) {
          setQuestions(response.data.questions);
          
          // Check if all questions have been answered
          const answeredQuestions = response.data.questions.filter(q => 'user_answer' in q);
          if (answeredQuestions.length === response.data.questions.length) {
            setQuizComplete(true);
            setSummary(response.data);
          } else {
            // Find the first unanswered question
            const nextUnansweredIndex = response.data.questions.findIndex(q => !('user_answer' in q));
            setCurrentQuestionIndex(nextUnansweredIndex >= 0 ? nextUnansweredIndex : 0);
          }
        } else {
          setError('No questions found for this quiz session');
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching quiz session:', err);
        setError('Failed to load quiz. Please try again later.');
        setLoading(false);
      }
    };

    fetchQuizSession();
  }, [sessionId]);

  const handleAnswerChange = (event) => {
    setSelectedAnswer(event.target.value);
  };

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer) return;
    
    try {
      setLoading(true);
      
      const response = await quizAPI.submitAnswer({
        session_id: sessionId,
        question_index: currentQuestionIndex,
        selected_answer: selectedAnswer
      });
      
      setAnswerSubmitted(true);
      setAnswerResult({
        isCorrect: response.data.is_correct,
        correctAnswer: response.data.correct_answer,
        explanation: response.data.explanation
      });
      
      setLoading(false);
    } catch (err) {
      console.error('Error submitting answer:', err);
      setError('Failed to submit answer. Please try again.');
      setLoading(false);
    }
  };

  const handleNextQuestion = async () => {
    setSelectedAnswer('');
    setAnswerSubmitted(false);
    setAnswerResult(null);
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      try {
        setLoading(true);
        const summaryResponse = await quizAPI.getSummary(sessionId);
        setQuizComplete(true);
        setSummary(summaryResponse.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching quiz summary:', err);
        setError('Failed to load quiz summary. Please try again later.');
        setLoading(false);
      }
    }
  };

  const handleFinishQuiz = () => {
    navigate('/dashboard');
  };

  if (loading && !answerSubmitted) {
    return (
      <Container>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="50vh">
          <CircularProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>Loading quiz...</Typography>
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

  if (quizComplete && summary) {
    return (
      <Container>
        <Paper sx={{ p: 3, my: 3 }}>
          <Typography variant="h4" gutterBottom>Quiz Complete!</Typography>
          
          <Box sx={{ my: 3 }}>
            <Typography variant="h6" gutterBottom>Your Results:</Typography>
            <Typography variant="body1">
              You answered {summary.correct_answers} out of {summary.total_questions} questions correctly.
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Accuracy: {summary.accuracy}%
            </Typography>
            
            <LinearProgress 
              variant="determinate" 
              value={summary.accuracy} 
              color={summary.accuracy >= 70 ? "success" : summary.accuracy >= 40 ? "warning" : "error"}
              sx={{ height: 10, borderRadius: 5, mb: 4 }}
            />
          </Box>
          
          <Typography variant="h6" gutterBottom>Question Summary:</Typography>
          
          {summary.questions.map((question, index) => (
            <Card key={index} sx={{ mb: 2, border: question.is_correct ? '1px solid #4caf50' : '1px solid #f44336' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  {question.is_correct ? (
                    <CheckCircleOutlineIcon color="success" sx={{ mr: 1 }} />
                  ) : (
                    <CancelOutlinedIcon color="error" sx={{ mr: 1 }} />
                  )}
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Question {index + 1}: {question.question}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Your answer: {question.user_answer}
                      {!question.is_correct && (
                        <Typography component="span" color="error">
                          {" "}(Incorrect)
                        </Typography>
                      )}
                    </Typography>
                    
                    {!question.is_correct && (
                      <Typography variant="body2" color="success.main" sx={{ mt: 0.5 }}>
                        Correct answer: {question.correct_answer}
                      </Typography>
                    )}
                    
                    <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                      {question.explanation}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
          
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleFinishQuiz}
              size="large"
            >
              Return to Dashboard
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = Math.round(((currentQuestionIndex + 1) / questions.length) * 100);

  return (
    <Container>
      <Paper sx={{ p: 3, my: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>Multiple Choice Quiz</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" sx={{ mr: 1 }}>
              Question {currentQuestionIndex + 1} of {questions.length}
            </Typography>
            <Typography variant="body2" sx={{ ml: 'auto' }}>
              {progress}%
            </Typography>
          </Box>
          <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
        </Box>

        <Box sx={{ my: 4 }}>
          <Typography variant="h6" gutterBottom>
            {currentQuestion?.question}
          </Typography>
          
          <RadioGroup
            aria-label="quiz-options"
            name="quiz-options"
            value={selectedAnswer}
            onChange={handleAnswerChange}
            sx={{ my: 2 }}
            disabled={answerSubmitted}
          >
            {currentQuestion?.options.map((option, index) => (
              <FormControlLabel
                key={index}
                value={option}
                control={<Radio />}
                label={option}
                disabled={answerSubmitted}
                sx={{
                  py: 1,
                  px: 2,
                  my: 0.5,
                  borderRadius: 1,
                  border: '1px solid #e0e0e0',
                  ...(answerSubmitted && option === answerResult?.correctAnswer && {
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderColor: '#4caf50',
                  }),
                  ...(answerSubmitted && option === selectedAnswer && !answerResult?.isCorrect && {
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    borderColor: '#f44336',
                  }),
                }}
              />
            ))}
          </RadioGroup>
          
          {answerSubmitted && (
            <Box sx={{ mt: 3, p: 2, backgroundColor: answerResult?.isCorrect ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)', borderRadius: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center">
                {answerResult?.isCorrect ? (
                  <CheckCircleOutlineIcon color="success" />
                ) : (
                  <CancelOutlinedIcon color="error" />
                )}
                <Typography variant="subtitle1" fontWeight="bold">
                  {answerResult?.isCorrect ? 'Correct!' : 'Incorrect!'}
                </Typography>
              </Stack>
              
              {!answerResult?.isCorrect && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  The correct answer is: <strong>{answerResult?.correctAnswer}</strong>
                </Typography>
              )}
              
              <Typography variant="body2" sx={{ mt: 1 }}>
                {answerResult?.explanation}
              </Typography>
            </Box>
          )}
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          {!answerSubmitted ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmitAnswer}
              disabled={!selectedAnswer || loading}
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : 'Submit Answer'}
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              onClick={handleNextQuestion}
              fullWidth
            >
              {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'See Results'}
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default Quiz;
