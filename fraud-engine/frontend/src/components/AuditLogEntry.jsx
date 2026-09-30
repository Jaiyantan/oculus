/**
 * AuditLogEntry — Single row in the audit trail timeline.
 */
import React from 'react';

function formatTime(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function getStatusLabel(status) {
  const labels = {
    pending_review: 'Pending Review',
    confirmed_fraud: 'Confirmed Fraud',
    cleared: 'Cleared',
    escalated: 'Escalated',
    auto_blocked: 'Auto-Blocked',
    log_only: 'Log Only',
  };
  return labels[status] || status;
}

export default function AuditLogEntry({ action }) {
  return (
    <div className={`audit-entry ${action.to_status}`}>
      <div className="audit-meta">
        <span>🧑‍💼 {action.reviewer_id}</span>
        <span>•</span>
        <span>{formatTime(action.acted_at)}</span>
        <span>•</span>
        <span className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          {action.fraud_flag_id?.slice(0, 8)}...
        </span>
      </div>
      <div className="audit-transition">
        <span className={`tier-tag ${action.from_status}`}>{getStatusLabel(action.from_status)}</span>
        <span className="audit-arrow">→</span>
        <span className={`tier-tag ${action.to_status}`}>{getStatusLabel(action.to_status)}</span>
      </div>
      {action.notes && (
        <div className="audit-notes">"{action.notes}"</div>
      )}
    </div>
  );
}
