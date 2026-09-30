/**
 * AuditLog Page — Append-only log of all reviewer actions.
 * 
 * Timeline view of every review decision, with transition details and notes.
 * This data is both the compliance audit trail and the future ML training dataset.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { getReviewActions } from '../api/client';
import AuditLogEntry from '../components/AuditLogEntry';

export default function AuditLog() {
  const [actions, setActions] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchActions = useCallback(async () => {
    try {
      const data = await getReviewActions(100, 0);
      setActions(data.actions);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch audit log:', err);
      setError(err.message || 'Failed to fetch audit log');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActions();
    const interval = setInterval(fetchActions, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [fetchActions]);

  return (
    <div>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">Audit Log</h1>
            <p className="page-description">
              Append-only record of every reviewer action. Never updated, never deleted.
              DPDP compliant by architecture.
            </p>
          </div>
          <div className="flex items-center gap-12">
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              {total} total actions
            </span>
            <button className="btn btn-ghost btn-sm" onClick={fetchActions}>
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Actions</div>
          <div className="stat-value blue">{total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Confirmed Fraud</div>
          <div className="stat-value red">
            {actions.filter(a => a.to_status === 'confirmed_fraud').length}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Cleared</div>
          <div className="stat-value green">
            {actions.filter(a => a.to_status === 'cleared').length}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Escalated</div>
          <div className="stat-value" style={{ color: 'var(--accent-purple)' }}>
            {actions.filter(a => a.to_status === 'escalated').length}
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)', marginBottom: '16px' }}>
          <p style={{ color: 'var(--risk-red)' }}>
            ⚠️ Error: {error}. Make sure the backend is running.
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="empty-state">
          <div className="spinner" style={{ width: '32px', height: '32px' }} />
          <p className="empty-state-text mt-16">Loading audit log...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && actions.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <p className="empty-state-text">
            No review actions yet. Review a flagged transaction from the console to see actions appear here.
          </p>
        </div>
      )}

      {/* Timeline */}
      {actions.length > 0 && (
        <div className="audit-timeline">
          {actions.map((action) => (
            <AuditLogEntry key={action.id} action={action} />
          ))}
        </div>
      )}
    </div>
  );
}
