import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthPage from './pages/Auth.jsx';
import ProtectedRoute from './components/ProtectedRoute';
import Feed from './pages/Feed.jsx';
import CreateSessionPage from './pages/CreateSessionPage.jsx'; // Import CreateSessionPage
import JournalPage from './pages/JournalPage.jsx'; // Import JournalPage
import { Toaster } from 'react-hot-toast';
import Navigation from './components/Navigation'; // Import Navigation component

// A component to handle the root URL path, redirecting based on auth state.
const Home = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/feed" /> : <Navigate to="/auth/login" />;
};

const AppContent = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Router>
      {isAuthenticated && <Navigation />}
      <div className={isAuthenticated ? "pt-16 pb-16" : ""}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth/login" element={<AuthPage />} />
          <Route
            path="/feed"
            element={
              <ProtectedRoute>
                <Feed />
              </ProtectedRoute>
            }
          />
          <Route
            path="/create-session"
            element={
              <ProtectedRoute>
                <CreateSessionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/journal"
            element={
              <ProtectedRoute>
                <JournalPage />
              </ProtectedRoute>
            }
          />
          {/* Redirect any other path to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
};

function App() {
  return (
    <AuthProvider>
      <Toaster position="top-center" reverseOrder={false} />
      <AppContent />
    </AuthProvider>
  );
}

export default App;