import React, { useState, useEffect } from 'react';
import { wordsAPI } from '../services/api';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  CircularProgress,
  Box,
} from '@mui/material';

const Words = () => {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWords = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await wordsAPI.getAll();
        setWords(response.data.words || []);
      } catch (err) {
        console.error('Error fetching words:', err);
        setError('Failed to fetch words. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchWords();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Words
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>English</TableCell>
              <TableCell>French</TableCell>
              <TableCell>Correct Count</TableCell>
              <TableCell>Wrong Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {words.map((word) => (
              <TableRow key={word.id}>
                <TableCell>{word.english}</TableCell>
                <TableCell>{word.french}</TableCell>
                <TableCell>{word.stats?.correct_count || 0}</TableCell>
                <TableCell>{word.stats?.wrong_count || 0}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default Words;
