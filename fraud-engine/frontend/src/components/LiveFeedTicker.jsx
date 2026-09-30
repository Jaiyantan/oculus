/**
 * LiveFeedTicker — Real-time scrolling feed of recent transactions.
 * Makes the system feel alive during the demo.
 */
import React from 'react';
import RiskScoreBadge from './RiskScoreBadge';

function formatTime(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function LiveFeedTicker({ flags }) {
  const recentFlags = (flags || []).slice(0, 5);

  if (recentFlags.length === 0) {
    return (
      <div className="live-ticker">
        <div className="live-ticker-label">
          <div className="status-dot" />
          LIVE
        </div>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          Waiting for transactions...
        </span>
      </div>
    );
  }

  return (
    <div className="live-ticker">
      <div className="live-ticker-label">
        <div className="status-dot" />
        LIVE
      </div>
      <div className="live-ticker-items">
        {recentFlags.map((flag) => (
          <div className="ticker-item" key={flag.id}>
            <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
              {formatTime(flag.created_at)}
            </span>
            <span className="font-mono" style={{ fontSize: '12px' }}>
              {flag.transaction?.user_id || '—'}
            </span>
            <span className="font-mono" style={{ fontSize: '12px', color: 'var(--text-primary)' }}>
              ${flag.transaction?.amount?.toFixed(2) || '0.00'}
            </span>
            <RiskScoreBadge score={flag.risk_score} tier={flag.risk_tier} />
          </div>
        ))}
      </div>
    </div>
  );
}
