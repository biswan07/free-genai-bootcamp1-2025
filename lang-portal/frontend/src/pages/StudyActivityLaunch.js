import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper, Button } from '@mui/material';

function StudyActivityLaunch() {
  const { id } = useParams();

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h5" gutterBottom>
          Launch Study Activity
        </Typography>
        <Typography paragraph>
          Preparing to launch activity {id}...
        </Typography>
        <Button variant="contained" color="primary">
          Start Activity
        </Button>
      </Paper>
    </Box>
  );
}

export default StudyActivityLaunch;
