import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Container, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Alert,
  CircularProgress
} from '@mui/material';
import { studyActivitiesAPI, groupsAPI } from '../services/api';

function StudyActivityLaunch() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activity, setActivity] = useState(null);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');

  useEffect(() => {
    const fetchActivityAndGroups = async () => {
      try {
        // Fetch activity details
        const activityResponse = await studyActivitiesAPI.getById(id);
        setActivity(activityResponse.data);
        
        // Fetch available word groups
        const groupsResponse = await groupsAPI.getAll();
        // Fix: Extract the groups array from the response data
        setGroups(groupsResponse.data.groups || []);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load activity data. Please try again later.');
        setLoading(false);
      }
    };

    fetchActivityAndGroups();
  }, [id]);

  const handleGroupChange = (event) => {
    setSelectedGroup(event.target.value);
  };

  const handleStartActivity = () => {
    if (!selectedGroup) {
      setError('Please select a word group to continue');
      return;
    }

    // Navigate based on activity type
    if (activity.name === 'Flashcards') {
      navigate(`/study/${id}/flashcards`);
    } else if (activity.name === 'Multiple Choice Quiz') {
      navigate(`/study/${id}/quiz-setup`);
    } else {
      // For other activities (to be implemented later)
      setError('This activity type is not yet implemented');
    }
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
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

  return (
    <Container>
      <Paper sx={{ p: 3, my: 3 }}>
        <Typography variant="h5" gutterBottom>
          {activity?.name}
        </Typography>
        
        <Typography paragraph>
          {activity?.description}
        </Typography>
        
        <Box sx={{ my: 3 }}>
          <FormControl fullWidth>
            <InputLabel id="group-select-label">Select Word Group</InputLabel>
            <Select
              labelId="group-select-label"
              id="group-select"
              value={selectedGroup}
              label="Select Word Group"
              onChange={handleGroupChange}
            >
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button 
            variant="outlined" 
            onClick={() => navigate('/study')}
          >
            Cancel
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleStartActivity}
            disabled={!selectedGroup}
          >
            Start Activity
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default StudyActivityLaunch;
