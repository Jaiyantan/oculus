import React, { useEffect, useState } from 'react';
import { getFraudFlags } from '../api/client';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import GlassCard from '../components/GlassCard';
import LedText from '../components/LedText';

export default function Dashboard() {
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const data = await getFraudFlags();
      setFlags(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Safeguard in case API returns undefined/null
  const safeFlags = Array.isArray(flags) ? flags : [];

  // Compute stats
  const pendingCount = safeFlags.filter(f => f.review_status === 'pending_review').length;
  const confirmedCount = safeFlags.filter(f => f.review_status === 'confirmed_fraud').length;
  const clearedCount = safeFlags.filter(f => f.review_status === 'cleared').length;

  const pieData = [
    { name: 'Pending', value: pendingCount },
    { name: 'Confirmed Fraud', value: confirmedCount },
    { name: 'Cleared', value: clearedCount }
  ];

  const COLORS = ['#f59e0b', '#ef4444', '#10b981'];

  // Mock timeline data based on flags (in reality, grouped by date/hour)
  const barData = [
    { 
      name: 'Rules', 
      amount_rule: safeFlags.filter(f => f.rule_results?.some(r => r.rule_name === 'amount_rule' && r.triggered)).length, 
      velocity_rule: safeFlags.filter(f => f.rule_results?.some(r => r.rule_name === 'velocity_rule' && r.triggered)).length, 
      geo_rule: safeFlags.filter(f => f.rule_results?.some(r => r.rule_name === 'geo_rule' && r.triggered)).length 
    }
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Analytics Dashboard</h1>
        <p className="page-description">Real-time fraud insights and system performance.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '24px', marginBottom: '32px' }}>
        <GlassCard 
          variant="speed" 
          title="Pending Reviews" 
          metric={pendingCount.toString()} 
          caption="Requires manual intervention" 
        />
        <GlassCard 
          variant="context" 
          title="Confirmed Fraud" 
          metric={confirmedCount.toString()} 
          caption="Blocked transactions" 
        />
        <GlassCard 
          variant="connections" 
          title="False Positives" 
          metric={clearedCount.toString()} 
          caption="Legitimate transactions cleared" 
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div className="card">
          <h3 className="card-title">Flag Status Distribution</h3>
          <div style={{ height: '300px', marginTop: '16px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)', borderRadius: '8px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Top Rules Triggered</h3>
          <div style={{ height: '300px', marginTop: '16px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="name" stroke="var(--text-muted)" />
                <YAxis stroke="var(--text-muted)" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="amount_rule" fill="var(--accent-purple)" name="Amount Rule" />
                <Bar dataKey="velocity_rule" fill="var(--risk-amber)" name="Velocity Rule" />
                <Bar dataKey="geo_rule" fill="var(--risk-red)" name="Geo Rule" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
