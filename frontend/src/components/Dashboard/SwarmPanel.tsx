import { useEffect, useState } from 'react';
import { fetchSystemSoul } from '../../lib/api';
import { Activity, ShieldCheck, HeartPulse, Clock, FileText, Database } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export function SwarmPanel() {
  const [soulData, setSoulData] = useState<{ content: string; exists: boolean; last_pulse?: string; error?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const refreshSoul = async () => {
    setLoading(true);
    try {
      const soul = await fetchSystemSoul();
      setSoulData(soul);
      setLastRefreshed(new Date());
    } catch (e) {
      console.error("Failed to fetch soul", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshSoul();
    const interval = setInterval(refreshSoul, 10000); // 10 seconds refresh
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="rounded-xl overflow-hidden mb-4" style={{ background: 'var(--color-bg)', border: '1px solid var(--color-border)' }}>
      <div className="flex items-center justify-between p-4" style={{ borderBottom: '1px solid var(--color-border)', background: 'var(--color-bg-secondary)' }}>
        <div className="flex items-center gap-3">
          <ShieldCheck size={20} style={{ color: 'var(--color-accent)' }} />
          <h2 className="font-semibold text-mg" style={{ color: 'var(--color-text)' }}>Swarm Identity (SOUL)</h2>
        </div>
        <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
          <div className="flex items-center gap-1">
            <HeartPulse size={14} className={loading ? 'animate-pulse' : ''} style={{ color: '#22c55e' }} />
            <span>Live Sync</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock size={14} />
            <span>Last checked: {lastRefreshed.toLocaleTimeString()}</span>
          </div>
          <button 
            onClick={refreshSoul} 
            className="p-1 rounded bg-transparent opacity-80 hover:opacity-100 transition-opacity"
            title="Refresh Identity"
            disabled={loading}
          >
            <Activity size={16} />
          </button>
        </div>
      </div>
      
      <div className="p-4" style={{ maxHeight: '350px', overflowY: 'auto' }}>
        {!soulData?.exists ? (
          <div className="flex flex-col items-center justify-center py-8 opacity-60" style={{ color: 'var(--color-text-secondary)' }}>
            <Database size={32} className="mb-2" />
            <p>SOUL.md Identity file is currently missing or uninitialized.</p>
            <p className="text-xs mt-1">Run an agent in Auto or Plan mode to construct the persistent identity.</p>
          </div>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none" style={{ color: 'var(--color-text-secondary)' }}>
            <ReactMarkdown>{soulData.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
