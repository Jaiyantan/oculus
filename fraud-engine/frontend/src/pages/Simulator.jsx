/**
 * Simulator Page — Transaction Simulator (Demo Panel)
 * 
 * Three scenario buttons with pre-filled payloads:
 * A: Velocity Attack (rapid transactions)
 * B: Amount Anomaly ($9,500 for a $48 baseline user)
 * C: Impossible Travel (NYC to London in 3 minutes + amount anomaly)
 */
import React, { useState } from 'react';
import { submitTransaction } from '../api/client';
import RiskScoreBadge from '../components/RiskScoreBadge';
import RuleBreakdownPanel from '../components/RuleBreakdownPanel';
import GlassCard from '../components/GlassCard';

const DEMO_SCENARIOS = [
  {
    id: 'velocity',
    icon: '⚡',
    title: 'Velocity Attack',
    subtitle: 'Rapid card-testing pattern — 6 transactions in 30 seconds',
    className: 'velocity',
    description: 'Fires 6 rapid transactions for Alice. Triggers the velocity_rule.',
    expectedScore: '0.48 – 0.60',
    expectedTier: 'flag_for_review',
    transactions: Array.from({ length: 6 }, (_, i) => ({
      user_id: 'user_demo_alice',
      amount: 5.00 + Math.random() * 10,
      currency: 'USD',
      merchant_id: `merch_test_${i}`,
      merchant_category: 'retail',
      latitude: 40.7128 + (Math.random() - 0.5) * 0.01,
      longitude: -74.0060 + (Math.random() - 0.5) * 0.01,
      device_fingerprint: 'fp_alice_velocity',
      ip_address: '203.0.113.42',
    })),
  },
  {
    id: 'amount',
    icon: '💰',
    title: 'Amount Anomaly',
    subtitle: '$9,500 charge for a user whose baseline is $48',
    className: 'amount',
    description: 'Single high-value transaction for Alice. Triggers amount_rule with Z-score ~4.2.',
    expectedScore: '0.65 – 0.80',
    expectedTier: 'flag_for_review',
    transactions: [{
      user_id: 'user_demo_alice',
      amount: 9500.00,
      currency: 'USD',
      merchant_id: 'merch_luxury_store',
      merchant_category: 'luxury_retail',
      latitude: 40.7580,
      longitude: -73.9855,
      device_fingerprint: 'fp_alice_1',
      ip_address: '192.168.1.100',
    }],
  },
  {
    id: 'travel',
    icon: '🌍',
    title: 'Impossible Travel',
    subtitle: 'NYC → London in 3 minutes + $8,000 charge',
    className: 'travel',
    description: 'Transaction in London for Alice who was just in NYC. Triggers geo_rule AND amount_rule.',
    expectedScore: '0.87 – 0.95',
    expectedTier: 'auto_block',
    transactions: [{
      user_id: 'user_demo_alice',
      amount: 8000.00,
      currency: 'GBP',
      merchant_id: 'merch_london_electronics',
      merchant_category: 'electronics',
      latitude: 51.5074,
      longitude: -0.1278,
      device_fingerprint: 'fp_unknown_device',
      ip_address: '185.220.101.33',
    }],
  },
];

export default function Simulator() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState(null);

  const fireScenario = async (scenario) => {
    setLoading(scenario.id);
    setError(null);
    setResults([]);

    try {
      const newResults = [];
      for (const tx of scenario.transactions) {
        const result = await submitTransaction(tx);
        newResults.push(result);
        // Small delay between rapid transactions for velocity scenario
        if (scenario.transactions.length > 1) {
          await new Promise(r => setTimeout(r, 200));
        }
      }
      setResults(newResults);
    } catch (err) {
      console.error('Scenario failed:', err);
      setError(err.response?.data?.detail || err.message || 'Transaction submission failed');
    } finally {
      setLoading(null);
    }
  };

  // Get the last (most impactful) result for display
  const lastResult = results.length > 0 ? results[results.length - 1] : null;

  function getScoreColorClass(score) {
    if (score >= 0.85) return 'red';
    if (score >= 0.45) return 'amber';
    return 'green';
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Simulated Attack Vectors</h1>
        <p className="page-description">
          <span style={{ color: 'var(--risk-amber)', fontWeight: '600' }}>⚠️ SYNTHETIC DATA MODE:</span> Fire pre-configured demo scenarios to see the Oculus rule engine in action.
          Results appear here instantly, and flagged transactions show up in the Review Console.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        {DEMO_SCENARIOS.map((scenario) => {
          let variant = 'speed';
          if (scenario.id === 'amount') variant = 'context';
          if (scenario.id === 'travel') variant = 'connections';

          return (
            <div key={scenario.id} onClick={() => !loading && fireScenario(scenario)} style={{ cursor: 'pointer', height: '400px', opacity: loading === scenario.id ? 0.7 : 1 }}>
              <GlassCard
                variant={variant}
                title={scenario.title}
                caption={scenario.description}
                metric={scenario.expectedScore.split(' – ')[0]}
              >
                <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '13px', textAlign: 'center', marginBottom: 'auto' }}>
                  {scenario.subtitle}
                </div>
                {loading === scenario.id && (
                  <div style={{ textAlign: 'center', marginTop: '16px', color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>
                    <span className="spinner" style={{ borderColor: 'white', borderTopColor: 'transparent' }} /> Processing...
                  </div>
                )}
              </GlassCard>
            </div>
          );
        })}
      </div>

      {/* Error */}
      {error && (
        <div className="result-panel" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
          <div style={{ color: 'var(--risk-red)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>❌</span>
            <span style={{ fontWeight: '600' }}>Error:</span>
            <span>{error}</span>
          </div>
          <p style={{ marginTop: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
            Make sure the backend is running at <code className="font-mono">http://localhost:8000</code>
          </p>
        </div>
      )}

      {/* Results */}
      {lastResult && (
        <div className="result-panel">
          <div className="result-header">
            <div>
              <div className={`result-score-large ${getScoreColorClass(lastResult.risk_score)}`}>
                {Math.round(lastResult.risk_score * 100)}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Risk Score
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span className={`tier-tag ${lastResult.risk_tier}`}>
                {lastResult.risk_tier.replace(/_/g, ' ')}
              </span>
              {lastResult.risk_tier === 'auto_block' && (
                <p style={{ fontSize: '12px', color: 'var(--risk-red)', marginTop: '8px' }}>
                  🚨 SNS notification fired
                </p>
              )}
              {lastResult.flag_id && (
                <p className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Flag: {lastResult.flag_id.slice(0, 8)}...
                </p>
              )}
            </div>
          </div>

          {results.length > 1 && (
            <div className="mb-16">
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                {results.length} transactions processed. Showing last result:
              </p>
              <div className="flex gap-8" style={{ flexWrap: 'wrap' }}>
                {results.map((r, i) => (
                  <RiskScoreBadge key={i} score={r.risk_score} tier={r.risk_tier} />
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-primary)' }}>
              Rule Breakdown
            </h3>
            <RuleBreakdownPanel ruleResults={lastResult.rule_results} />
          </div>

          <div className="mt-16" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <p className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Transaction ID: {lastResult.transaction_id}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
