import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Brain, LogIn, LogOut, User } from 'lucide-react';

const Navigation = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  const readAuth = () => {
    const token = localStorage.getItem('auth_token');
    const name  = localStorage.getItem('auth_name');
    const role  = localStorage.getItem('auth_role');
    const id    = localStorage.getItem('auth_identifier');
    if (token && name) setUser({ name, role, identifier: id });
    else               setUser(null);
  };

  useEffect(() => {
    readAuth();
    // Sync across tabs and after login redirect
    window.addEventListener('storage', readAuth);
    return () => window.removeEventListener('storage', readAuth);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_role');
    localStorage.removeItem('auth_name');
    localStorage.removeItem('auth_identifier');
    setUser(null);
    navigate('/', { replace: true });
  };

  return (
    <nav>
      <NavLink to="/" className="nav-brand">
        <Brain color="#6366f1" size={28} />
        <span
          style={{
            background: 'linear-gradient(to right, var(--primary), var(--secondary))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontSize: '1.1rem',
            whiteSpace: 'nowrap',
          }}
        >
          Student Academic Performance Monitoring
        </span>
      </NavLink>

      <div className="nav-links">
        {user ? (
          <>
            {/* Logged-in user chip */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.4rem 0.85rem',
                background: 'rgba(99,102,241,0.12)',
                border: '1px solid rgba(99,102,241,0.3)',
                borderRadius: '8px',
                color: 'var(--primary)',
                fontSize: '0.875rem',
                fontWeight: 500,
              }}
            >
              <User size={15} />
              <span>{user.identifier}</span>
              <span
                style={{
                  fontSize: '0.7rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  opacity: 0.7,
                  background: 'rgba(99,102,241,0.2)',
                  padding: '0.1rem 0.4rem',
                  borderRadius: '4px',
                }}
              >
                {user.role}
              </span>
            </div>

            {/* Logout */}
            <button
              id="btn-logout"
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.45rem 0.9rem',
                background: 'rgba(239,68,68,0.12)',
                border: '1px solid rgba(239,68,68,0.25)',
                borderRadius: '8px',
                color: '#f87171',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'background 0.2s',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.22)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.12)')}
            >
              <LogOut size={15} />
              Logout
            </button>
          </>
        ) : (
          <NavLink
            to="/"
            id="btn-nav-login"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.45rem 1rem',
              background: isActive
                ? 'rgba(99,102,241,0.25)'
                : 'linear-gradient(135deg,#6366f1,#7c3aed)',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '0.875rem',
              fontWeight: 600,
              textDecoration: 'none',
              boxShadow: '0 4px 12px rgba(99,102,241,0.3)',
              transition: 'opacity 0.2s',
            })}
          >
            <LogIn size={15} />
            Login
          </NavLink>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
