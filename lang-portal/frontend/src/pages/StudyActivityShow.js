import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper } from '@mui/material';

function StudyActivityShow() {
  const { id } = useParams();

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h5" gutterBottom>
          Study Activity Details
        </Typography>
        <Typography>
          Activity ID: {id}
        </Typography>
      </Paper>
    </Box>
  );
}

export default StudyActivityShow;
