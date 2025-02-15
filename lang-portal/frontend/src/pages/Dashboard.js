import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { dashboardAPI } from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastSession, setLastSession] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sessionResponse, statsResponse] = await Promise.all([
          dashboardAPI.getLastStudySession(),
          dashboardAPI.getQuickStats(),
        ]);

        setLastSession(sessionResponse.data);
        setStats(statsResponse.data);
        setLoading(false);
      } catch (err) {
        setError('Error loading dashboard data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" p={4}>
          <Typography>Loading...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Last Study Session
              </Typography>
              {lastSession?.has_sessions ? (
                <>
                  <Typography>
                    Activity: {lastSession.activity?.name}
                  </Typography>
                  <Typography>
                    Group: {lastSession.group?.name}
                  </Typography>
                  <Typography>
                    Words: {lastSession.stats?.total_words} • 
                    Correct: {lastSession.stats?.correct_words} • 
                    Accuracy: {Math.round((lastSession.stats?.correct_words / lastSession.stats?.total_words) * 100)}%
                  </Typography>
                </>
              ) : (
                <Typography>No study sessions yet</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Study Progress
              </Typography>
              {stats ? (
                <Typography>
                  Words studied: {stats.words_studied} / {stats.total_words}
                </Typography>
              ) : (
                <Typography>No progress data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Stats
              </Typography>
              {stats ? (
                <>
                  <Typography>{stats.total_words} Total Words</Typography>
                  <Typography>{stats.total_groups} Groups</Typography>
                  <Typography>{stats.study_sessions} Study Sessions</Typography>
                  <Typography>{stats.study_streak} Day Streak</Typography>
                </>
              ) : (
                <Typography>No statistics available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box mt={4}>
        <Button
          component={Link}
          to="/study-activities"
          variant="contained"
          color="primary"
          fullWidth
        >
          START STUDYING
        </Button>
      </Box>
    </Container>
  );
};

export default Dashboard;
