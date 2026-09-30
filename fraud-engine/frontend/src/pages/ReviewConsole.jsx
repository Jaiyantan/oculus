/**
 * ReviewConsole Page — Main reviewer dashboard.
 * 
 * Polls for new fraud flags every 2 seconds.
 * Click any flag to see full rule breakdown and take review actions.
 */
import React, { useState } from 'react';
import { useFraudFlags } from '../hooks/useFraudFlags';
import { getFraudFlagDetail } from '../api/client';
import RiskScoreBadge from '../components/RiskScoreBadge';
import RuleBreakdownPanel from '../components/RuleBreakdownPanel';
import ReviewActionButtons from '../components/ReviewActionButtons';
import GlassCard from '../components/GlassCard';
import LiveFeedTicker from '../components/LiveFeedTicker';

function formatTime(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
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

export default function ReviewConsole() {
  const [filter, setFilter] = useState('');
  const { flags, total, loading, error, refetch } = useFraudFlags(filter || null);
  const [selectedFlag, setSelectedFlag] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const handleFlagClick = async (flag) => {
    setDetailLoading(true);
    try {
      const detail = await getFraudFlagDetail(flag.id);
      setSelectedFlag(detail);
    } catch (err) {
      console.error('Failed to load detail:', err);
      setSelectedFlag(flag);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => setSelectedFlag(null);

  const handleActionComplete = () => {
    refetch();
    setSelectedFlag(null);
  };

  // Stats
  const pendingCount = flags.filter(f => f.review_status === 'pending_review').length;
  const autoBlockCount = flags.filter(f => f.risk_tier === 'auto_block').length;
  const highRiskCount = flags.filter(f => f.risk_score >= 0.85).length;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Review Console</h1>
        <p className="page-description">
          Flagged transactions auto-refresh every 2 seconds. Click any flag to investigate.
        </p>
      </div>

      {/* Live Feed */}
      <LiveFeedTicker flags={flags} />

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Flags</div>
          <div className="stat-value blue">{total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Review</div>
          <div className="stat-value amber">{pendingCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Auto-Blocked</div>
          <div className="stat-value red">{autoBlockCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">High Risk (≥85)</div>
          <div className="stat-value red">{highRiskCount}</div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-12 mb-16">
        <label className="form-label" style={{ marginBottom: 0 }}>Filter:</label>
        <select
          className="form-select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ width: '200px' }}
        >
          <option value="">All Flags</option>
          <option value="pending_review">Pending Review</option>
          <option value="confirmed_fraud">Confirmed Fraud</option>
          <option value="cleared">Cleared</option>
          <option value="escalated">Escalated</option>
        </select>
        <button className="btn btn-ghost btn-sm" onClick={refetch}>
          🔄 Refresh
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)', marginBottom: '16px' }}>
          <p style={{ color: 'var(--risk-red)' }}>
            ⚠️ Connection error: {error}. Retrying every 2 seconds...
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && flags.length === 0 && (
        <div className="empty-state">
          <div className="spinner" style={{ width: '32px', height: '32px' }} />
          <p className="empty-state-text mt-16">Loading fraud flags...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && flags.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">🛡️</div>
          <p className="empty-state-text">
            No flagged transactions. Fire a scenario from the Simulator to see flags appear here in real-time.
          </p>
        </div>
      )}

      {/* Flags Table */}
      {flags.length > 0 && (
        <div className="card data-table-wrapper" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table" id="fraud-flags-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>User</th>
                <th>Amount</th>
                <th>Risk Score</th>
                <th>Risk Tier</th>
                <th>Status</th>
                <th>Top Rule</th>
              </tr>
            </thead>
            <tbody>
              {flags.map((flag) => {
                const topRule = (flag.rule_results || [])
                  .filter(r => r.triggered)
                  .sort((a, b) => b.risk_contribution - a.risk_contribution)[0];

                return (
                  <tr key={flag.id} onClick={() => handleFlagClick(flag)} id={`flag-${flag.id}`}>
                    <td className="mono">{formatTime(flag.created_at)}</td>
                    <td className="mono">{flag.transaction?.user_id || '—'}</td>
                    <td className="mono">${flag.transaction?.amount?.toFixed(2) || '0.00'}</td>
                    <td>
                      <RiskScoreBadge score={flag.risk_score} tier={flag.risk_tier} />
                    </td>
                    <td>
                      <span className={`tier-tag ${flag.risk_tier}`}>
                        {flag.risk_tier.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>
                      <span className={`tier-tag ${flag.review_status}`}>
                        {getStatusLabel(flag.review_status)}
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '12px' }}>
                      {topRule ? topRule.rule_name : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail Panel (Slide-in) */}
      {selectedFlag && (
        <div className="detail-overlay" onClick={closeDetail}>
          <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
            <button className="detail-close" onClick={closeDetail}>✕</button>

            {detailLoading ? (
              <div className="empty-state">
                <div className="spinner" />
                <p className="mt-8" style={{ color: 'var(--text-muted)' }}>Loading details...</p>
              </div>
            ) : (
              <>
                {/* Header */}
                <div className="detail-section">
                  <div className="flex items-center justify-between mb-16">
                    <div>
                      <div className={`result-score-large ${selectedFlag.risk_score >= 0.85 ? 'red' : selectedFlag.risk_score >= 0.45 ? 'amber' : 'green'}`}>
                        {Math.round(selectedFlag.risk_score * 100)}
                      </div>
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Risk Score</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span className={`tier-tag ${selectedFlag.risk_tier}`}>
                        {selectedFlag.risk_tier.replace(/_/g, ' ')}
                      </span>
                      <br />
                      <span className={`tier-tag ${selectedFlag.review_status}`} style={{ marginTop: '6px', display: 'inline-flex' }}>
                        {getStatusLabel(selectedFlag.review_status)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Transaction Details */}
                <div className="detail-section">
                  <h3 className="detail-section-title">Transaction Details</h3>
                  {selectedFlag.transaction && (
                    <>
                      <div className="detail-field">
                        <span className="detail-label">User ID</span>
                        <span className="detail-value font-mono">{selectedFlag.transaction.user_id}</span>
                      </div>
                      <div className="detail-field">
                        <span className="detail-label">Amount</span>
                        <span className="detail-value font-mono">
                          ${selectedFlag.transaction.amount?.toFixed(2)} {selectedFlag.transaction.currency}
                        </span>
                      </div>
                      <div className="detail-field">
                        <span className="detail-label">Merchant</span>
                        <span className="detail-value">{selectedFlag.transaction.merchant_id || '—'}</span>
                      </div>
                      <div className="detail-field">
                        <span className="detail-label">Category</span>
                        <span className="detail-value">{selectedFlag.transaction.merchant_category || '—'}</span>
                      </div>
                      <div className="detail-field">
                        <span className="detail-label">Location</span>
                        <span className="detail-value font-mono">
                          {selectedFlag.transaction.latitude != null
                            ? `${selectedFlag.transaction.latitude?.toFixed(4)}, ${selectedFlag.transaction.longitude?.toFixed(4)}`
                            : '—'}
                        </span>
                      </div>
                      <div className="detail-field">
                        <span className="detail-label">Device</span>
                        <span className="detail-value font-mono">{selectedFlag.transaction.device_fingerprint || '—'}</span>
                      </div>
                      <div className="detail-field">
                        <span className="detail-label">IP Address</span>
                        <span className="detail-value font-mono">{selectedFlag.transaction.ip_address || '—'}</span>
                      </div>
                      <div className="detail-field">
                        <span className="detail-label">Time</span>
                        <span className="detail-value">{formatTime(selectedFlag.transaction.created_at)}</span>
                      </div>
                    </>
                  )}
                </div>

                {/* Rule Breakdown */}
                <div className="detail-section">
                  <h3 className="detail-section-title">Rule Breakdown</h3>
                  <RuleBreakdownPanel ruleResults={selectedFlag.rule_results} />
                </div>

                {/* Review Actions */}
                <div className="detail-section">
                  <h3 className="detail-section-title">Review Actions</h3>
                  <ReviewActionButtons
                    flagId={selectedFlag.id}
                    currentStatus={selectedFlag.review_status}
                    onActionComplete={handleActionComplete}
                  />
                </div>

                {/* Audit History */}
                {selectedFlag.review_actions && selectedFlag.review_actions.length > 0 && (
                  <div className="detail-section">
                    <h3 className="detail-section-title">Audit History</h3>
                    {selectedFlag.review_actions.map((action, idx) => (
                      <div key={idx} style={{ 
                        padding: '10px 12px', 
                        background: 'var(--bg-tertiary)', 
                        borderRadius: 'var(--radius-sm)', 
                        marginBottom: '8px',
                        fontSize: '13px' 
                      }}>
                        <div className="flex items-center gap-8">
                          <span className={`tier-tag ${action.from_status}`} style={{ fontSize: '10px' }}>
                            {action.from_status}
                          </span>
                          <span style={{ color: 'var(--text-muted)' }}>→</span>
                          <span className={`tier-tag ${action.to_status}`} style={{ fontSize: '10px' }}>
                            {action.to_status}
                          </span>
                          <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '11px' }}>
                            {action.reviewer_id}
                          </span>
                        </div>
                        {action.notes && (
                          <p style={{ marginTop: '6px', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                            "{action.notes}"
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* IDs */}
                <div className="detail-section">
                  <h3 className="detail-section-title">Identifiers</h3>
                  <div className="detail-field">
                    <span className="detail-label">Flag ID</span>
                    <span className="detail-value font-mono" style={{ fontSize: '11px' }}>{selectedFlag.id}</span>
                  </div>
                  <div className="detail-field">
                    <span className="detail-label">Transaction ID</span>
                    <span className="detail-value font-mono" style={{ fontSize: '11px' }}>{selectedFlag.transaction_id}</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
