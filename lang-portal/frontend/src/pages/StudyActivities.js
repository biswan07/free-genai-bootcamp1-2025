import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Box,
  Alert,
} from '@mui/material';
import { studyActivitiesAPI } from '../services/api';

const StudyActivities = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const response = await studyActivitiesAPI.getAll();
        setActivities(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error loading study activities');
        setLoading(false);
      }
    };

    fetchActivities();
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

  if (activities.length === 0) {
    return (
      <Container>
        <Alert severity="info">No study activities available.</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Grid container spacing={3}>
        {activities.map((activity) => (
          <Grid item xs={12} sm={6} md={4} key={activity.id}>
            <Card>
              {activity.thumbnail_url && (
                <CardMedia
                  component="img"
                  height="140"
                  image={activity.thumbnail_url}
                  alt={activity.name}
                />
              )}
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {activity.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {activity.description}
                </Typography>
                <Box display="flex" justifyContent="space-between" mt={2}>
                  <Button
                    component={Link}
                    to={`/study-activities/${activity.id}/launch`}
                    variant="contained"
                    color="primary"
                  >
                    LAUNCH
                  </Button>
                  <Button
                    component={Link}
                    to={`/study-activities/${activity.id}/details`}
                    variant="outlined"
                    color="primary"
                  >
                    VIEW DETAILS
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default StudyActivities;
