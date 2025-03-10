import React, { useState } from 'react';
import { Card, CardContent, Typography, Box, Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const FlipCard = styled(Card)(({ theme, flipped }) => ({
  perspective: '1000px',
  backgroundColor: 'transparent',
  width: '100%',
  height: '250px',
  cursor: 'pointer',
  '& .card-inner': {
    position: 'relative',
    width: '100%',
    height: '100%',
    transition: 'transform 0.6s',
    transformStyle: 'preserve-3d',
    transform: flipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
  },
  '& .card-front, & .card-back': {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backfaceVisibility: 'hidden',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing(2),
  },
  '& .card-front': {
    backgroundColor: theme.palette.primary.light,
    color: theme.palette.primary.contrastText,
  },
  '& .card-back': {
    backgroundColor: theme.palette.secondary.light,
    color: theme.palette.secondary.contrastText,
    transform: 'rotateY(180deg)',
  },
}));

const Flashcard = ({ word, onCorrect, onIncorrect, onNext }) => {
  const [flipped, setFlipped] = useState(false);
  const [answered, setAnswered] = useState(false);

  const handleFlip = () => {
    if (!answered) {
      setFlipped(!flipped);
    }
  };

  const handleResponse = (correct) => {
    setAnswered(true);
    if (correct) {
      onCorrect(word.id);
    } else {
      onIncorrect(word.id);
    }
  };

  const handleNext = () => {
    setFlipped(false);
    setAnswered(false);
    onNext();
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 500, mx: 'auto', my: 2 }}>
      <FlipCard flipped={flipped} onClick={handleFlip}>
        <Box className="card-inner">
          <CardContent className="card-front">
            <Typography variant="h4" component="div" align="center">
              {word.french}
            </Typography>
          </CardContent>
          <CardContent className="card-back">
            <Typography variant="h4" component="div" align="center">
              {word.english}
            </Typography>
          </CardContent>
        </Box>
      </FlipCard>
      
      {flipped && !answered && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
          <Button 
            variant="contained" 
            color="error" 
            onClick={() => handleResponse(false)}
            sx={{ width: '48%' }}
          >
            I didn't know
          </Button>
          <Button 
            variant="contained" 
            color="success" 
            onClick={() => handleResponse(true)}
            sx={{ width: '48%' }}
          >
            I knew it
          </Button>
        </Box>
      )}
      
      {answered && (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            Response recorded.
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleNext}
            fullWidth
          >
            Next Card
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default Flashcard;
