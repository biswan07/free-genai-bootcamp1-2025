import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
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
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  ListItemText
} from '@mui/material';
import { wordsAPI, groupsAPI, quizAPI } from '../services/api';

const QuizSetup = () => {
  const { activityId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalWords, setTotalWords] = useState(0);
  const [questionCount, setQuestionCount] = useState(10);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');
  const [useAllWords, setUseAllWords] = useState(true);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get groupId from URL query parameters
        const searchParams = new URLSearchParams(location.search);
        const groupIdFromUrl = searchParams.get('groupId');
        
        // Fetch all words to get the total count
        const wordsResponse = await wordsAPI.getAll();
        if (!wordsResponse.data.words || wordsResponse.data.words.length === 0) {
          setError('No words available in the database');
          setLoading(false);
          return;
        }
        
        const total = wordsResponse.data.total || wordsResponse.data.words.length;
        setTotalWords(total);
        
        // Fetch groups
        const groupsResponse = await groupsAPI.getAll();
        setGroups(groupsResponse.data.groups || []);
        
        // Set selected group from URL query parameter
        if (groupIdFromUrl) {
          setSelectedGroup(groupIdFromUrl);
          setUseAllWords(false);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, [location.search]);

  const handleQuestionCountChange = (event, newValue) => {
    setQuestionCount(newValue);
  };

  const handleInputChange = (event) => {
    const value = event.target.value === '' ? 0 : Number(event.target.value);
    setQuestionCount(Math.min(Math.max(1, value), 20)); // Max 20 questions
  };

  const handleGroupChange = (event) => {
    setSelectedGroup(event.target.value);
    setUseAllWords(false);
  };

  const toggleUseAllWords = () => {
    setUseAllWords(!useAllWords);
    if (!useAllWords) {
      setSelectedGroup('');
    }
  };

  const handleStartQuiz = async () => {
    try {
      setLoading(true);
      
      const quizData = {
        question_count: questionCount,
        study_activity_id: parseInt(activityId || 1)
      };
      
      if (!useAllWords && selectedGroup) {
        quizData.group_id = parseInt(selectedGroup);
      }
      
      console.log('Generating quiz with data:', quizData);
      
      const response = await quizAPI.generate(quizData);
      console.log('Quiz generation response:', response);
      
      if (response.data && response.data.session_id) {
        navigate(`/study/${activityId}/quiz/${response.data.session_id}`);
      } else {
        setError('Failed to generate quiz: Invalid response from server');
        setLoading(false);
      }
    } catch (err) {
      console.error('Error starting quiz:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Unknown error';
      setError(`Failed to start quiz: ${errorMessage}`);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="50vh">
          <CircularProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>Loading...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        <Button variant="outlined" onClick={() => navigate('/study')}>
          Back to Study Activities
        </Button>
      </Container>
    );
  }

  return (
    <Container>
      <Paper sx={{ p: 3, my: 3 }}>
        <Typography variant="h4" gutterBottom>Multiple Choice Quiz Setup</Typography>
        
        <Box sx={{ my: 4 }}>
          <Typography variant="h6" gutterBottom>
            There are {totalWords} words available in the database.
          </Typography>
          
          <Box sx={{ my: 3 }}>
            <Typography variant="body1" gutterBottom>
              Word Selection:
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Checkbox
                checked={useAllWords}
                onChange={toggleUseAllWords}
                name="useAllWords"
              />
              <Typography>Use all available words</Typography>
            </Box>
            
            {!useAllWords && (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="group-select-label">Select a Group</InputLabel>
                <Select
                  labelId="group-select-label"
                  id="group-select"
                  value={selectedGroup}
                  label="Select a Group"
                  onChange={handleGroupChange}
                  disabled={useAllWords}
                >
                  {groups.map((group) => (
                    <MenuItem key={group.id} value={group.id}>
                      <ListItemText primary={group.name} secondary={`${group.word_count} words`} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          </Box>
          
          <Box sx={{ my: 3 }}>
            <Typography variant="body1" gutterBottom>
              How many questions would you like in your quiz?
            </Typography>
            
            <Stack spacing={2} direction="row" sx={{ mb: 1 }} alignItems="center">
              <Typography>1</Typography>
              <Slider
                value={questionCount}
                onChange={handleQuestionCountChange}
                aria-labelledby="question-count-slider"
                valueLabelDisplay="auto"
                step={1}
                min={1}
                max={20}
                sx={{ mx: 2 }}
              />
              <Typography>20</Typography>
            </Stack>
            
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', my: 2 }}>
              <TextField
                value={questionCount}
                onChange={handleInputChange}
                inputProps={{
                  step: 1,
                  min: 1,
                  max: 20,
                  type: 'number',
                  'aria-labelledby': 'question-count-slider',
                }}
                sx={{ width: '100px' }}
              />
              <Typography variant="body1" sx={{ ml: 2 }}>questions</Typography>
            </Box>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button variant="outlined" onClick={() => navigate('/study')}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleStartQuiz}
            disabled={!useAllWords && !selectedGroup}
          >
            Start Quiz
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default QuizSetup;
