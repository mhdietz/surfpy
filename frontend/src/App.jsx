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

// Placeholder for the main feed page
const Feed = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Welcome to the Feed!</h2>
      {user && <p>You are logged in as user ID: {user.id}</p>}
      <button onClick={handleLogout} style={{ padding: '10px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px' }}>
        Logout
      </button>
    </div>
  );
};

// A component to handle the root URL path
const Home = () => {
  const { isAuthenticated } = useAuth();
  // If logged in, go to the feed. Otherwise, go to the login page.
  return isAuthenticated ? <Navigate to="/feed" /> : <Navigate to="/auth/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
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
          {/* Redirect any other path to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
