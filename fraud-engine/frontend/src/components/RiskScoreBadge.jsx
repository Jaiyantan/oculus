/**
 * RiskScoreBadge — Color-coded score display.
 * Green below 45, amber 45-85, red above 85.
 */
import React from 'react';

function getScoreColor(score) {
  if (score >= 0.85) return 'red';
  if (score >= 0.45) return 'amber';
  return 'green';
}

function getTierClass(tier) {
  const map = {
    clean: 'clean',
    log_only: 'log-only',
    flag_for_review: 'flag-for-review',
    auto_block: 'auto-block',
  };
  return map[tier] || 'clean';
}

export default function RiskScoreBadge({ score, tier }) {
  const color = getScoreColor(score);
  const tierClass = getTierClass(tier);
  const percentage = Math.round(score * 100);

  return (
    <div className={`risk-score-badge ${tierClass}`}>
      <span>{percentage}</span>
      <div className="risk-score-bar">
        <div
          className={`risk-score-bar-fill ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
