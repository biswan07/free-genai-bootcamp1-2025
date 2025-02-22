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
  Button,
  Stack,
  TablePagination,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

const Words = () => {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [totalWords, setTotalWords] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const fetchWords = async (pageNum = 1) => {
    try {
      setLoading(true);
      setError(null);
      const response = await wordsAPI.getAll(pageNum);
      if (pageNum === 1) {
        setWords(response.data.words || []);
      } else {
        setWords(prev => [...prev, ...(response.data.words || [])]);
      }
      setTotalWords(response.data.total || 0);
      
      // If there are more pages, fetch them
      if (pageNum < response.data.pages) {
        await fetchWords(pageNum + 1);
      }
    } catch (err) {
      console.error('Error fetching words:', err);
      setError('Failed to fetch words. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWords(1);
  }, []);

  const handleRefresh = () => {
    fetchWords(1);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading && words.length === 0) {
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

  const displayedWords = words.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Container>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Words</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={loading}
        >
          Refresh
        </Button>
      </Stack>
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
            {displayedWords.map((word) => (
              <TableRow key={word.id}>
                <TableCell>{word.english}</TableCell>
                <TableCell>{word.french}</TableCell>
                <TableCell>{word.stats?.correct_count || 0}</TableCell>
                <TableCell>{word.stats?.wrong_count || 0}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={totalWords}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Container>
  );
};

export default Words;
