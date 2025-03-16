import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper } from '@mui/material';

function StudySessionShow() {
  const { id } = useParams();

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h5" gutterBottom>
          Study Session Details
        </Typography>
        <Typography>
          Session ID: {id}
        </Typography>
      </Paper>
    </Box>
  );
}

export default StudySessionShow;
