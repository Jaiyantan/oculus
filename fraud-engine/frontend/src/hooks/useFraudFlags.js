/**
 * useFraudFlags — Custom hook for 2-second polling of fraud flags.
 * 
 * Powers the real-time feel of the review console without WebSocket infrastructure.
 */
import { useState, useEffect, useCallback } from 'react';
import { getFraudFlags } from '../api/client';

export function useFraudFlags(filterStatus = null) {
  const [flags, setFlags] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchFlags = useCallback(async () => {
    try {
      const data = await getFraudFlags(filterStatus);
      setFlags(data.flags);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch flags:', err);
      setError(err.message || 'Failed to fetch flags');
    } finally {
      setLoading(false);
    }
  }, [filterStatus]);

  useEffect(() => {
    fetchFlags();
    const interval = setInterval(fetchFlags, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [fetchFlags]);

  return { flags, total, loading, error, refetch: fetchFlags };
}
