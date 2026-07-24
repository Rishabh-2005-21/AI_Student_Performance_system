import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import Login from './pages/Login';
import MentorDashboard from './pages/MentorDashboard';
import StudentDashboard from './pages/StudentDashboard';
import './App.css';
import './index.css';

/**
 * ProtectedRoute — redirects to / (login) if the user has no valid auth token.
 * Optionally restricts by role: only 'faculty' → /faculty, only 'student' → /student.
 */
const ProtectedRoute = ({ element, requiredRole }) => {
  const token = localStorage.getItem('auth_token');
  const role  = localStorage.getItem('auth_role');

  if (!token) return <Navigate to="/" replace />;

  if (requiredRole && role !== requiredRole) {
    return <Navigate to={role === 'faculty' ? '/faculty' : '/student'} replace />;
  }
  return element;
};

function App() {
  return (
    <Router>
      <Navigation />
      <Routes>
        {/* Login is the root / first page */}
        <Route path="/" element={<Login />} />

        {/* Protected dashboards */}
        <Route
          path="/faculty"
          element={<ProtectedRoute element={<MentorDashboard />} requiredRole="faculty" />}
        />
        <Route
          path="/dashboard"
          element={<ProtectedRoute element={<MentorDashboard />} requiredRole="faculty" />}
        />
        <Route
          path="/student"
          element={<ProtectedRoute element={<StudentDashboard />} requiredRole="student" />}
        />

        {/* Anything else → login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
