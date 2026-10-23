import React, { useState } from 'react';
import { 
  Bell, AlertTriangle, AlertCircle, Sparkles, Check, 
  Send, MessageSquare, Volume2, Globe, Clock, ShieldCheck 
} from 'lucide-react';

interface AlertItem {
  id: string;
  type: 'CRITICAL' | 'WARNING' | 'OPPORTUNITY';
  title: string;
  description: string;
  amount?: number;
  recipientName?: string;
  dueDate?: string;
  isRead: boolean;
  timeAgo: string;
}

const mockAlerts: AlertItem[] = [
  {
    id: 'alt_01',
    type: 'CRITICAL',
    title: 'Cash D-Day Approaching: 47 Days Remaining',
    description: 'At current collection rates, bank liquidity will become negative on 12-Apr-2025 by -₹3.40 Lakhs. Activate Rescue Plan levers immediately.',
    amount: 340000,
    dueDate: '12-Apr-2025',
    isRead: false,
    timeAgo: '10 mins ago',
  },
  {
    id: 'alt_02',
    type: 'CRITICAL',
    title: 'Disallowed ITC: Vendor GSTIN Retrospectively Cancelled',
    description: 'Rajdhani Yarn Mills GSTIN was cancelled by authorities. Table 4(B)(2) reversal required to avoid 18% p.a. interest penalty.',
    amount: 242000,
    isRead: false,
    timeAgo: '1 hour ago',
  },
  {
    id: 'alt_03',
    type: 'WARNING',
    title: 'Severe Payment Overdue: Balaji Retail Fabrics',
    description: 'Invoices exceeding agreed 30-day credit limit by +48 days. Total outstanding ₹5,20,000. Send automated legal caution notice.',
    amount: 520000,
    recipientName: 'Balaji Retail Fabrics',
    isRead: false,
    timeAgo: '3 hours ago',
  },
  {
    id: 'alt_04',
    type: 'OPPORTUNITY',
    title: 'TReDS Discounting Opportunity: Reliance Retail',
    description: 'Approved invoices worth ₹18,50,000 are eligible for instant auction discounting on RXIL at 8.2% p.a. to unlock Day-3 cash.',
    amount: 1850000,
    recipientName: 'Reliance Retail Supply Vendor',
    isRead: true,
    timeAgo: '1 day ago',
  },
];

interface AlertsCentreProps {
  businessId: string;
  language: string;
}

export const AlertsCentre: React.FC<AlertsCentreProps> = ({ language }) => {
  const [alerts, setAlerts] = useState<AlertItem[]>(mockAlerts);
  const [filterType, setFilterType] = useState<string>('ALL');

  const formatINR = (val?: number) => {
    if (!val) return '';
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const handleMarkRead = (id: string) => {
    setAlerts(alerts.map((a) => (a.id === id ? { ...a, isRead: true } : a)));
  };

  const filtered = alerts.filter((a) => {
    if (filterType === 'ALL') return true;
    return a.type === filterType;
  });

  const unreadCount = alerts.filter((a) => !a.isRead).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Alert Center Header */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'var(--rose-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Bell size={22} color="var(--rose-danger)" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Proactive Alert & Action Centre</h3>
              {unreadCount > 0 && (
                <span className="pill pill-rose" style={{ fontSize: '0.7rem' }}>
                  {unreadCount} Unread Actions
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Real-time early warnings, statutory deadlines, and receivables action triggers
            </p>
          </div>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {['ALL', 'CRITICAL', 'WARNING', 'OPPORTUNITY'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={filterType === t ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Feed */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filtered.map((item) => (
          <div
            key={item.id}
            className="glass-panel"
            style={{
              padding: '1.25rem',
              borderLeft: `4px solid ${
                item.type === 'CRITICAL'
                  ? 'var(--rose-danger)'
                  : item.type === 'WARNING'
                  ? 'var(--amber-warning)'
                  : 'var(--emerald-success)'
              }`,
              opacity: item.isRead ? 0.75 : 1,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ marginTop: '2px' }}>
                  {item.type === 'CRITICAL' && <AlertCircle size={20} color="var(--rose-danger)" />}
                  {item.type === 'WARNING' && <AlertTriangle size={20} color="var(--amber-warning)" />}
                  {item.type === 'OPPORTUNITY' && <Sparkles size={20} color="var(--emerald-success)" />}
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span
                      className={`pill ${
                        item.type === 'CRITICAL'
                          ? 'pill-rose'
                          : item.type === 'WARNING'
                          ? 'pill-amber'
                          : 'pill-emerald'
                      }`}
                      style={{ fontSize: '0.65rem' }}
                    >
                      {item.type}
                    </span>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={12} /> {item.timeAgo}
                    </span>
                  </div>

                  <h4 style={{ fontSize: '0.98rem', fontWeight: 700, marginTop: '0.35rem' }}>{item.title}</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem', lineHeight: 1.5 }}>
                    {item.description}
                  </p>

                  {item.amount && (
                    <div style={{ display: 'inline-block', marginTop: '0.5rem', background: 'rgba(255, 255, 255, 0.04)', padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.76rem', fontWeight: 600 }}>
                      Financial Exposure: <span style={{ color: item.type === 'OPPORTUNITY' ? 'var(--emerald-success)' : 'var(--rose-danger)' }}>{formatINR(item.amount)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action buttons */}
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', whiteSpace: 'nowrap', marginLeft: '1rem' }}>
                {!item.isRead && (
                  <button
                    onClick={() => handleMarkRead(item.id)}
                    className="btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
                    title="Mark alert as reviewed"
                  >
                    <Check size={14} /> Mark Read
                  </button>
                )}

                {item.recipientName && (
                  <a
                    href={`https://wa.me/?text=${encodeURIComponent(`Reminder from Ramesh Textiles regarding overdue account for ${item.recipientName}. Total: ${formatINR(item.amount)}`)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-success"
                    style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem', textDecoration: 'none' }}
                  >
                    <Send size={13} /> WhatsApp
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
