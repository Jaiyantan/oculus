/**
 * ReviewActionButtons — Shows only valid next actions for the current status.
 * 
 * State machine:
 *   pending_review -> confirmed_fraud | cleared | escalated
 *   confirmed_fraud -> pending_review (reopen)
 *   cleared -> pending_review (reopen)
 *   escalated -> confirmed_fraud | cleared
 */
import React, { useState } from 'react';
import { reviewFraudFlag } from '../api/client';

const VALID_TRANSITIONS = {
  pending_review: [
    { status: 'confirmed_fraud', label: '🚨 Confirm Fraud', className: 'btn-danger' },
    { status: 'cleared', label: '✅ Clear', className: 'btn-success' },
    { status: 'escalated', label: '⬆️ Escalate', className: 'btn-warning' },
  ],
  confirmed_fraud: [
    { status: 'pending_review', label: '🔄 Reopen', className: 'btn-outline' },
  ],
  cleared: [
    { status: 'pending_review', label: '🔄 Reopen', className: 'btn-outline' },
  ],
  escalated: [
    { status: 'confirmed_fraud', label: '🚨 Confirm Fraud', className: 'btn-danger' },
    { status: 'cleared', label: '✅ Clear', className: 'btn-success' },
  ],
};

export default function ReviewActionButtons({ flagId, currentStatus, onActionComplete }) {
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const [showNotes, setShowNotes] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);

  const actions = VALID_TRANSITIONS[currentStatus] || [];

  const handleAction = async (toStatus) => {
    setLoading(true);
    try {
      await reviewFraudFlag(flagId, {
        reviewer_id: 'demo_reviewer',
        to_status: toStatus,
        notes: notes || null,
      });
      setNotes('');
      setShowNotes(false);
      setSelectedAction(null);
      if (onActionComplete) onActionComplete();
    } catch (err) {
      console.error('Review action failed:', err);
      alert(`Action failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (actions.length === 0) {
    return <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No actions available</p>;
  }

  return (
    <div>
      <div className="review-actions">
        {actions.map((action) => (
          <button
            key={action.status}
            className={`btn btn-sm ${action.className}`}
            disabled={loading}
            onClick={() => {
              setSelectedAction(action.status);
              setShowNotes(true);
            }}
          >
            {loading && selectedAction === action.status ? (
              <span className="spinner" />
            ) : null}
            {action.label}
          </button>
        ))}
      </div>

      {showNotes && (
        <div className="mt-16" style={{ animation: 'slide-up 0.2s ease' }}>
          <textarea
            className="form-textarea"
            placeholder="Add notes (optional)..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
          />
          <div className="flex gap-8 mt-8">
            <button
              className="btn btn-primary btn-sm"
              disabled={loading}
              onClick={() => handleAction(selectedAction)}
            >
              {loading ? <span className="spinner" /> : 'Confirm Action'}
            </button>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => { setShowNotes(false); setSelectedAction(null); }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
