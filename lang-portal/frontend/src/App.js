import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SchoolIcon from '@mui/icons-material/School';
import TranslateIcon from '@mui/icons-material/Translate';

// Pages
import Dashboard from './pages/Dashboard';
import StudyActivities from './pages/StudyActivities';
import StudyActivityShow from './pages/StudyActivityShow';
import StudyActivityLaunch from './pages/StudyActivityLaunch';
import Words from './pages/Words';
import WordShow from './pages/WordShow';
import StudySessionShow from './pages/StudySessionShow';

const drawerWidth = 240;

function App() {
  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div">
              Language Learning Portal
            </Typography>
          </Toolbar>
        </AppBar>
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              <ListItem button component={Link} to="/">
                <ListItemIcon>
                  <DashboardIcon />
                </ListItemIcon>
                <ListItemText primary="Dashboard" />
              </ListItem>
              <ListItem button component={Link} to="/study-activities">
                <ListItemIcon>
                  <SchoolIcon />
                </ListItemIcon>
                <ListItemText primary="Study Activities" />
              </ListItem>
              <ListItem button component={Link} to="/words">
                <ListItemIcon>
                  <TranslateIcon />
                </ListItemIcon>
                <ListItemText primary="Words" />
              </ListItem>
            </List>
          </Box>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Container>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/study-activities" element={<StudyActivities />} />
              <Route path="/study-activities/:id" element={<StudyActivityShow />} />
              <Route path="/study-activities/:id/launch" element={<StudyActivityLaunch />} />
              <Route path="/words" element={<Words />} />
              <Route path="/words/:id" element={<WordShow />} />
              <Route path="/study-sessions/:id" element={<StudySessionShow />} />
            </Routes>
          </Container>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
