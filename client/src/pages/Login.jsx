import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Brain, Eye, EyeOff, GraduationCap,
  AlertCircle, Loader2, Sparkles, User, Lock, IdCard, UserCheck, CheckCircle2
} from 'lucide-react';
import api from '../api/api';
import './Login.css';

const FEATURES = [
  'Upload Semester Syllabus (PDF)',
  'AI Generates Questions Automatically',
  'Adaptive Difficulty per Student',
  'Confidence-Based Answer Tracking',
  'Topic-wise Performance Reports',
  'Faculty Can Monitor All Students',
];

const STATS = [
  { value: '8',   label: 'Semesters'      },
  { value: 'AI',  label: 'Auto Questions' },
  { value: '100%', label: 'PDF-Based'     },
];

const Login = () => {
  const navigate    = useNavigate();
  const [params]    = useSearchParams();
  const defaultRole = params.get('role') === 'student' ? 'student' : 'faculty';

  const [mode,        setMode]        = useState('login');
  const [role,        setRole]        = useState(defaultRole);
  const [identifier,  setIdentifier]  = useState('');
  const [password,    setPassword]    = useState('');
  const [name,        setName]        = useState('');        // register: full name
  const [studentName, setStudentName] = useState('');        // student login: display name
  const [showPass,    setShowPass]    = useState(false);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState('');

  useEffect(() => {
    const token     = localStorage.getItem('auth_token');
    const savedRole = localStorage.getItem('auth_role');
    if (token && savedRole) {
      navigate(savedRole === 'faculty' ? '/faculty' : '/student', { replace: true });
    }
  }, [navigate]);

  const reset = () => { setIdentifier(''); setPassword(''); setName(''); setStudentName(''); setError(''); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!identifier.trim() || !password.trim()) { setError('Please fill in all fields.'); return; }
    if (mode === 'login' && role === 'student' && !studentName.trim()) { setError('Please enter your full name.'); return; }
    if (mode === 'register' && !name.trim()) { setError('Full name is required.'); return; }
    setLoading(true);
    setError('');

    const endpoint = mode === 'login' ? '/auth/login' : '/auth/register';
    const body = mode === 'login'
      ? { identifier: identifier.trim(), password: password.trim(), role,
          ...(role === 'student' ? { student_name: studentName.trim() } : {}) }
      : { identifier: identifier.trim(), password: password.trim(), role, name: name.trim() };

    try {
      const { data } = await api.post(endpoint, body);

      // For student login, use the entered display name if backend name is just identifier
      const displayName = (role === 'student' && studentName.trim()) ? studentName.trim() : data.name;

      localStorage.setItem('auth_token',      data.token);
      localStorage.setItem('auth_role',        data.role);
      localStorage.setItem('auth_name',        displayName);
      localStorage.setItem('auth_identifier',  data.identifier);
      window.dispatchEvent(new Event('storage'));
      navigate(data.role === 'faculty' ? '/faculty' : '/student', { replace: true });
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || 'Network error — could not connect to backend server.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="lp-root">
      {/* ── Left: Branding ── */}
      <div className="lp-left">
        <div className="lp-brand">
          <div className="lp-brand-icon"><Brain size={20} color="#fff" /></div>
          <span className="lp-brand-name">STUDENT PERFORMANCE SYSTEM</span>
        </div>

        <h1 className="lp-heading">
          AI-Based Student<br />Assessment Platform
        </h1>
        <p className="lp-desc">
          Faculty uploads the semester syllabus. The system automatically generates
          questions, evaluates student answers in real time, and produces
          detailed performance reports for every student.
        </p>

        <div className="lp-feature-grid">
          {FEATURES.map(f => (
            <div key={f} className="lp-feature-pill">
              <CheckCircle2 size={13} className="lp-pill-icon" />
              <span>{f}</span>
            </div>
          ))}
        </div>

        <div className="lp-stats">
          {STATS.map(s => (
            <div key={s.label} className="lp-stat">
              <span className="lp-stat-val">{s.value}</span>
              <span className="lp-stat-lbl">{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Right: Auth Card ── */}
      <div className="lp-right">
        <div className="lp-card">
          {/* Mode tabs: Login / Register */}
          <div className="lp-mode-tabs">
            <button
              id="tab-login"
              type="button"
              className={`lp-mode-tab ${mode === 'login' ? 'active' : ''}`}
              onClick={() => { setMode('login'); reset(); }}
            >
              Login
            </button>
            <button
              id="tab-register"
              type="button"
              className={`lp-mode-tab ${mode === 'register' ? 'active' : ''}`}
              onClick={() => { setMode('register'); reset(); }}
            >
              Register
            </button>
          </div>

          <h2 className="lp-card-title">
            {mode === 'login' ? 'Welcome back' : 'Create account'}
          </h2>
          <p className="lp-card-sub">
            {mode === 'login'
              ? 'Sign in to access your dashboard.'
              : 'Create an account to get started.'}
          </p>

          <form onSubmit={handleSubmit} className="lp-form" noValidate>
            {/* Register-only: Name */}
            {mode === 'register' && (
              <div className="lp-field">
                <label htmlFor="lp-name">Full Name</label>
                <div className="lp-input-wrap">
                  <User className="lp-input-icon" size={16} />
                  <input
                    id="lp-name"
                    type="text"
                    placeholder="e.g. Priya Sharma"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    autoFocus
                  />
                </div>
              </div>
            )}

            {/* Student login: Full Name (for dashboard display) */}
            {mode === 'login' && role === 'student' && (
              <div className="lp-field">
                <label htmlFor="lp-student-name">Full Name</label>
                <div className="lp-input-wrap">
                  <User className="lp-input-icon" size={16} />
                  <input
                    id="lp-student-name"
                    type="text"
                    placeholder="e.g. Priya Sharma"
                    value={studentName}
                    onChange={e => setStudentName(e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Identifier — Enrollment No for student, Mentor ID for faculty */}
            <div className="lp-field">
              <label htmlFor="lp-id">
                {role === 'faculty' ? 'Faculty / Mentor ID' : 'Enrollment Number'}
              </label>
              <div className="lp-input-wrap">
                <IdCard className="lp-input-icon" size={16} />
                <input
                  id="lp-id"
                  type="text"
                  placeholder={role === 'faculty' ? 'e.g. MTR001' : 'e.g. STU001'}
                  value={identifier}
                  onChange={e => setIdentifier(e.target.value)}
                  autoFocus={mode === 'login'}
                />
              </div>
            </div>

            {/* Password */}
            <div className="lp-field">
              <label htmlFor="lp-pass">Password</label>
              <div className="lp-input-wrap">
                <Lock className="lp-input-icon" size={16} />
                <input
                  id="lp-pass"
                  type={showPass ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="lp-eye-toggle"
                  onClick={() => setShowPass(v => !v)}
                  title={showPass ? "Hide password" : "Show password"}
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Role selection */}
            <div className="lp-field">
              <label>Role</label>
              <div className="lp-role-pills">
                <button
                  id="role-student"
                  type="button"
                  className={`lp-role-pill ${role === 'student' ? 'active' : ''}`}
                  onClick={() => setRole('student')}
                >
                  <GraduationCap size={15} /> Student
                </button>
                <button
                  id="role-faculty"
                  type="button"
                  className={`lp-role-pill ${role === 'faculty' ? 'active' : ''}`}
                  onClick={() => setRole('faculty')}
                >
                  <UserCheck size={15} /> Faculty
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="lp-error">
                <AlertCircle size={14} />
                <span>{error}</span>
              </div>
            )}

            {/* Submit */}
            <button id="btn-submit" type="submit" className="lp-submit" disabled={loading}>
              {loading
                ? <><Loader2 size={16} className="spin" /> Please wait…</>
                : mode === 'login' ? 'Login to dashboard' : 'Create account'}
            </button>
          </form>

          {/* Switch mode */}
          <p className="lp-switch">
            {mode === 'login' ? "New here? " : "Already have an account? "}
            <button
              id="btn-switch-mode"
              type="button"
              onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); reset(); }}
            >
              {mode === 'login' ? 'Create an account' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
