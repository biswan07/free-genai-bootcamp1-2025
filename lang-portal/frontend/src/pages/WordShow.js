import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper } from '@mui/material';

function WordShow() {
  const { id } = useParams();

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h5" gutterBottom>
          Word Details
        </Typography>
        <Typography>
          Word ID: {id}
        </Typography>
      </Paper>
    </Box>
  );
}

export default WordShow;
