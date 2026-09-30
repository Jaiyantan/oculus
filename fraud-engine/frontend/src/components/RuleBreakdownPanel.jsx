/**
 * RuleBreakdownPanel — Expandable per-rule contribution detail.
 * Shows each rule's name, trigger status, contribution, and human-readable reason.
 */
import React from 'react';

export default function RuleBreakdownPanel({ ruleResults }) {
  if (!ruleResults || ruleResults.length === 0) {
    return (
      <div className="empty-state">
        <p className="empty-state-text">No rule results available</p>
      </div>
    );
  }

  return (
    <div className="rule-breakdown">
      {ruleResults.map((rule, idx) => (
        <div className="rule-item" key={idx}>
          <div className={`rule-indicator ${rule.triggered ? 'triggered' : 'safe'}`} />
          <div className="rule-details">
            <div className="rule-name">{rule.rule_name}</div>
            <div className="rule-reason">{rule.reason}</div>
          </div>
          <div className={`rule-contribution ${rule.risk_contribution > 0 ? 'positive' : 'zero'}`}>
            {rule.risk_contribution > 0 ? `+${(rule.risk_contribution * 100).toFixed(1)}%` : '0%'}
          </div>
        </div>
      ))}
    </div>
  );
}
