/**
 * Oculus — Fraud Rule Engine with Review Console
 * 
 * App shell with navigation and routing.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import Simulator from './pages/Simulator';
import ReviewConsole from './pages/ReviewConsole';
import AuditLog from './pages/AuditLog';
import Dashboard from './pages/Dashboard';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app-layout">
        {/* Clean SaaS Navbar matching OceanPulse aesthetic */}
        <nav className="nav" aria-label="Primary">
          <NavLink to="/simulator" className="brand">
            <span className="brand__name">Oculus</span>
          </NavLink>

          <ul className="nav__links">
            <li>
              <NavLink to="/simulator" className={({ isActive }) => isActive ? 'active' : ''}>
                Simulated Attacks
              </NavLink>
            </li>
            <li>
              <NavLink to="/console" className={({ isActive }) => isActive ? 'active' : ''}>
                Review Console
              </NavLink>
            </li>
            <li>
              <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>
                Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink to="/audit" className={({ isActive }) => isActive ? 'active' : ''}>
                Audit Log
              </NavLink>
            </li>
          </ul>

          <div className="status-indicator">
            <div className="status-dot" />
            <span className="status-text">Live</span>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/simulator" replace />} />
            <Route path="/simulator" element={<Simulator />} />
            <Route path="/console" element={<ReviewConsole />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/audit" element={<AuditLog />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
