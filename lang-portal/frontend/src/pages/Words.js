import React, { useState, useEffect } from 'react';
import { wordsAPI, groupsAPI, studySessionsAPI } from '../services/api';
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
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import FlashcardIcon from '@mui/icons-material/School';
import { useNavigate } from 'react-router-dom';

const Words = () => {
  const navigate = useNavigate();
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [totalWords, setTotalWords] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedWords, setSelectedWords] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');
  const [createNewGroup, setCreateNewGroup] = useState(false);
  const [flashcardDialogOpen, setFlashcardDialogOpen] = useState(false);

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

  const fetchGroups = async () => {
    try {
      const response = await groupsAPI.getAll();
      setGroups(response.data.groups || []);
    } catch (err) {
      console.error('Error fetching groups:', err);
    }
  };

  useEffect(() => {
    fetchWords(1);
    fetchGroups();
  }, []);

  const handleRefresh = () => {
    fetchWords(1);
    fetchGroups();
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSelectWord = (wordId) => {
    setSelectedWords(prev => {
      if (prev.includes(wordId)) {
        return prev.filter(id => id !== wordId);
      } else {
        return [...prev, wordId];
      }
    });
  };

  const handleSelectAllWords = (event) => {
    if (event.target.checked) {
      setSelectedWords(displayedWords.map(word => word.id));
    } else {
      setSelectedWords([]);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewGroupName('');
    setSelectedGroup('');
    setCreateNewGroup(false);
  };

  const handleOpenFlashcardDialog = () => {
    setFlashcardDialogOpen(true);
  };

  const handleCloseFlashcardDialog = () => {
    setFlashcardDialogOpen(false);
    setSelectedGroup('');
  };

  const handleCreateGroup = async () => {
    try {
      if (createNewGroup && !newGroupName.trim()) {
        alert('Please enter a group name');
        return;
      }

      let groupId;
      
      if (createNewGroup) {
        // Create new group
        const response = await groupsAPI.create({ name: newGroupName });
        groupId = response.data.id;
        
        // Add selected words to the new group
        for (const wordId of selectedWords) {
          await wordsAPI.update(wordId, { group_ids: [groupId] });
        }
      } else {
        // Add selected words to existing group
        groupId = selectedGroup;
        
        // Get current words in the group
        const groupResponse = await groupsAPI.getById(groupId);
        const currentWordIds = groupResponse.data.words?.map(word => word.id) || [];
        
        // Add selected words to the group
        for (const wordId of selectedWords) {
          if (!currentWordIds.includes(wordId)) {
            await wordsAPI.update(wordId, { 
              group_ids: [...currentWordIds, wordId]
            });
          }
        }
      }
      
      handleCloseDialog();
      fetchGroups();
      alert('Words added to group successfully!');
    } catch (err) {
      console.error('Error creating/updating group:', err);
      alert('Failed to add words to group. Please try again.');
    }
  };

  const handleStartFlashcards = async () => {
    try {
      if (!selectedGroup) {
        alert('Please select a group');
        return;
      }
      
      // Navigate to flashcard session with selected group
      navigate(`/study/1/group/${selectedGroup}`);
      handleCloseFlashcardDialog();
    } catch (err) {
      console.error('Error starting flashcard session:', err);
      alert('Failed to start flashcard session. Please try again.');
    }
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
  const isAllSelected = displayedWords.length > 0 && selectedWords.length === displayedWords.length;

  return (
    <Container>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Words</Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<FlashcardIcon />}
            onClick={() => navigate('/study/1/flashcards')}
          >
            Practice All Words
          </Button>
          {selectedWords.length > 0 && (
            <>
              <Button
                variant="contained"
                color="secondary"
                startIcon={<FlashcardIcon />}
                onClick={handleOpenFlashcardDialog}
              >
                Practice Selected
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handleOpenDialog}
              >
                Add to Group
              </Button>
            </>
          )}
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
      </Stack>

      {selectedWords.length > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {selectedWords.length} word(s) selected
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selectedWords.length > 0 && selectedWords.length < displayedWords.length}
                  checked={isAllSelected}
                  onChange={handleSelectAllWords}
                />
              </TableCell>
              <TableCell>English</TableCell>
              <TableCell>French</TableCell>
              <TableCell>Correct Count</TableCell>
              <TableCell>Wrong Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {displayedWords.map((word) => (
              <TableRow 
                key={word.id}
                selected={selectedWords.includes(word.id)}
                onClick={() => handleSelectWord(word.id)}
                hover
                sx={{ cursor: 'pointer' }}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedWords.includes(word.id)}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleSelectWord(word.id);
                    }}
                  />
                </TableCell>
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

      {/* Add to Group Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Add Words to Group</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="group-select-label">Group</InputLabel>
              <Select
                labelId="group-select-label"
                value={createNewGroup ? "new" : selectedGroup}
                label="Group"
                onChange={(e) => {
                  if (e.target.value === "new") {
                    setCreateNewGroup(true);
                    setSelectedGroup('');
                  } else {
                    setCreateNewGroup(false);
                    setSelectedGroup(e.target.value);
                  }
                }}
              >
                <MenuItem value="new">Create New Group</MenuItem>
                {groups.map((group) => (
                  <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>
                ))}
              </Select>
            </FormControl>

            {createNewGroup && (
              <TextField
                fullWidth
                label="New Group Name"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                sx={{ mb: 2 }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleCreateGroup} variant="contained" color="primary">
            Add to Group
          </Button>
        </DialogActions>
      </Dialog>

      {/* Start Flashcard Dialog */}
      <Dialog open={flashcardDialogOpen} onClose={handleCloseFlashcardDialog}>
        <DialogTitle>Practice with Flashcards</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="flashcard-group-select-label">Select Group</InputLabel>
              <Select
                labelId="flashcard-group-select-label"
                value={selectedGroup}
                label="Select Group"
                onChange={(e) => setSelectedGroup(e.target.value)}
              >
                {groups.map((group) => (
                  <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseFlashcardDialog}>Cancel</Button>
          <Button 
            onClick={handleStartFlashcards} 
            variant="contained" 
            color="primary"
            disabled={!selectedGroup}
          >
            Start Flashcards
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Words;
