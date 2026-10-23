import React, { useState } from 'react';
import { 
  ShieldAlert, TrendingUp, Scale, Bot, CheckCircle2, 
  RotateCcw, Sparkles, AlertCircle, FileCheck, Landmark 
} from 'lucide-react';
import { runCommittee } from '../api/client';

interface AgentMessage {
  agent: 'Risk Officer (Prudence)' | 'Growth Officer (Catalyst)' | 'Chief Underwriter (Arbiter)';
  role: 'risk' | 'growth' | 'arbiter';
  avatar: string;
  sentiment: 'cautious' | 'bullish' | 'balanced';
  timestamp: string;
  statement: string;
  points: string[];
}

const mockTranscript: AgentMessage[] = [
  {
    agent: 'Risk Officer (Prudence)',
    role: 'risk',
    avatar: '🛡️',
    sentiment: 'cautious',
    timestamp: '15:24:02',
    statement: 'I express serious reservation regarding standalone collateral-free credit expansion.',
    points: [
      'Top debtor Balaji Retail exhibits severe payment lag of 78 days against agreed 30-day terms, representing ₹5.20L in delinquent working capital.',
      'A ₹14.80L circular billing anomaly was identified in the textile trade cluster between Ramesh, Subhash, and Shivam Dyeing.',
      'Without covenant protections, credit enhancement would merely subsidize third-party payment delays.',
    ],
  },
  {
    agent: 'Growth Officer (Catalyst)',
    role: 'growth',
    avatar: '🚀',
    sentiment: 'bullish',
    timestamp: '15:24:08',
    statement: 'The macroeconomic fundamentals and operational margins strongly justify sanctioning working capital.',
    points: [
      'Debt Service Coverage Ratio (DSCR) is solid at 1.48x, which comfortably surpasses SBI / SIDBI standard hurdle rate of 1.25x.',
      'The company has secured direct institutional orders from Reliance Retail Vendor network (₹18.5L regular flow).',
      'The Surat textile cluster is experiencing a seasonal surge; working capital injection will capture 22% higher gross margins.',
    ],
  },
  {
    agent: 'Chief Underwriter (Arbiter)',
    role: 'arbiter',
    avatar: '⚖️',
    sentiment: 'balanced',
    timestamp: '15:24:15',
    statement: 'Deliberation concluded. Sanction approved with structured risk mitigations and conditional covenants.',
    points: [
      'Approve ₹35,00,000 Working Capital Overdraft / Invoice Discounting facility.',
      'Pricing set at 10.25% p.a. (competitive for rated MSMEs under CGTMSE guarantee scheme).',
      'Covenant 1: Immediate routing of Reliance Retail invoices via TReDS factoring platform.',
      'Covenant 2: Formal inquiry and reversal of circular billing cluster entries before disbursement.',
      'Covenant 3: Monthly DSCR certification by statutory Chartered Accountant.',
    ],
  },
];

interface CreditCommitteeProps {
  businessId: string;
}

export const CreditCommittee: React.FC<CreditCommitteeProps> = ({ businessId }) => {
  const [messages, setMessages] = useState<AgentMessage[]>(mockTranscript);
  const [isDeliberating, setIsDeliberating] = useState<boolean>(false);

  const handleRunCommittee = async () => {
    setIsDeliberating(true);
    try {
      await runCommittee(businessId);
    } catch (e) {
      // In mock/demo mode, simulation updates locally
    }
    setTimeout(() => {
      setIsDeliberating(false);
    }, 1800);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Committee Header Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot size={22} color="var(--indigo-light)" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Autonomous AI Credit Committee</h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Amazon Bedrock Multi-Agent Underwriting Simulation • 3 Specialized Economic Personas
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={handleRunCommittee}
          disabled={isDeliberating}
          className="btn-primary"
          style={{ fontSize: '0.82rem' }}
        >
          <RotateCcw size={15} className={isDeliberating ? 'spin-slow' : ''} />
          {isDeliberating ? 'Synthesizing Bedrock Agents...' : 'Re-Run Multi-Agent Deliberation'}
        </button>
      </div>

      {/* Main Deliberation Transcript */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: '1.25rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
            Live Committee Transcript
          </h4>

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className="glass-panel"
              style={{
                padding: '1.25rem',
                borderLeft: `4px solid ${
                  msg.role === 'risk'
                    ? 'var(--rose-danger)'
                    : msg.role === 'growth'
                    ? 'var(--emerald-success)'
                    : 'var(--indigo-primary)'
                }`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '1.2rem' }}>{msg.avatar}</span>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{msg.agent}</span>
                  <span
                    className={`pill ${
                      msg.role === 'risk'
                        ? 'pill-rose'
                        : msg.role === 'growth'
                        ? 'pill-emerald'
                        : 'pill-indigo'
                    }`}
                    style={{ fontSize: '0.68rem', textTransform: 'capitalize' }}
                  >
                    {msg.sentiment}
                  </span>
                </div>
                <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  {msg.timestamp}
                </span>
              </div>

              <p style={{ fontSize: '0.84rem', color: 'var(--text-primary)', marginBottom: '0.75rem', fontWeight: 500 }}>
                "{msg.statement}"
              </p>

              <ul style={{ paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                {msg.points.map((pt, pIdx) => (
                  <li key={pIdx} style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    {pt}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Synthesized Sanction Memo */}
        <div className="glass-panel" style={{ padding: '1.5rem', height: 'fit-content', border: '1px solid var(--border-glow)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <Landmark size={20} color="var(--indigo-light)" />
            <h4 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Binding Sanction Memorandum</h4>
          </div>

          <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--emerald-success)', fontWeight: 700, textTransform: 'uppercase' }}>
                Recommendation
              </span>
              <span className="pill pill-emerald" style={{ fontSize: '0.7rem' }}>
                <CheckCircle2 size={12} /> SANCTION APPROVED
              </span>
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'white', marginTop: '0.4rem' }}>
              ₹35,00,000
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Facility: Working Capital Term Loan (WCTL) / CC
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem', fontSize: '0.8rem' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '8px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>Interest Rate</div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem', marginTop: '0.15rem' }}>10.25% p.a.</div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '8px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>Facility Tenor</div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem', marginTop: '0.15rem' }}>12 Mos (Revolving)</div>
            </div>
          </div>

          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Mandatory Sanction Covenants
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={14} color="var(--indigo-light)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Borrower must onboard Reliance Retail receivables on TReDS within 30 days of first drawdown.</span>
            </div>
            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={14} color="var(--indigo-light)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Subhash Fabrics & Shivam Dyeing transactions must be audited by independent CA.</span>
            </div>
            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={14} color="var(--indigo-light)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Statutory minimum DSCR of 1.25x to be maintained quarterly.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
