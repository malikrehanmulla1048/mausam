import React from 'react';
import { 
  Building, CheckCircle2, AlertTriangle, ShieldCheck, 
  TrendingUp, Percent, FileDown, PieChart, Activity 
} from 'lucide-react';

interface BanksEyeXRayProps {
  businessId: string;
}

export const BanksEyeXRay: React.FC<BanksEyeXRayProps> = () => {
  const readinessScore = 78;
  const grade = 'A-';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Underwriter Score Summary */}
      <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          {/* Circular Score Gauge */}
          <div style={{ position: 'relative', width: '92px', height: '92px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="3.2"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="url(#scoreGrad)"
                strokeDasharray={`${readinessScore}, 100`}
                strokeWidth="3.2"
                strokeLinecap="round"
              />
              <defs>
                <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#10B981" />
                  <stop offset="100%" stopColor="#06B6D4" />
                </linearGradient>
              </defs>
            </svg>
            <div style={{ position: 'absolute', textAlign: 'center' }}>
              <span style={{ fontSize: '1.35rem', fontWeight: 800, color: 'white' }}>{readinessScore}</span>
              <span style={{ fontSize: '0.65rem', display: 'block', color: 'var(--text-muted)' }}>/ 100</span>
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 800 }}>Bank Underwriting Readiness Score</h3>
              <span className="pill pill-emerald" style={{ fontSize: '0.8rem' }}>Grade {grade} (Bankable)</span>
            </div>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Algorithmically simulated against SBI, HDFC, and SIDBI MSME lending matrices.
            </p>
          </div>
        </div>

        <button
          onClick={() => alert('Exporting Bank Underwriting Dossier as cryptographically verified PDF/JSON package...')}
          className="btn-primary"
          style={{ fontSize: '0.85rem' }}
        >
          <FileDown size={16} /> Export Lender Credit Memo
        </button>
      </div>

      {/* Financial Underwriting Ratios Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '1rem' }}>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>DSCR (Debt Service Coverage)</span>
            <Activity size={16} color="var(--emerald-success)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.4rem', color: 'var(--emerald-success)' }}>
            1.48x
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Bank Benchmark: ≥ 1.25x (Pass)
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>Current Ratio</span>
            <TrendingUp size={16} color="var(--indigo-light)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.4rem', color: 'var(--indigo-light)' }}>
            1.38x
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Bank Benchmark: ≥ 1.33x (Adequate)
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>Revenue Concentration</span>
            <PieChart size={16} color="var(--amber-warning)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.4rem', color: 'var(--amber-warning)' }}>
            48.2%
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--rose-danger)', marginTop: '0.25rem' }}>
            Top 3 Buyers = 48% (High concentration)
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>Working Capital Cycle</span>
            <Percent size={16} color="var(--rose-danger)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.4rem', color: 'var(--rose-danger)' }}>
            72 Days
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Textile Sector Median: 48 Days
          </div>
        </div>
      </div>

      {/* Underwriting Checklist: Red Flags & Pre-emptive Mitigations */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
        {/* Red Flags Observed */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <AlertTriangle size={18} color="var(--rose-danger)" />
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Bank Underwriter Friction Points</h4>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div style={{ background: 'rgba(239, 68, 68, 0.06)', borderLeft: '3px solid var(--rose-danger)', padding: '0.75rem', borderRadius: '6px' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--rose-danger)' }}>Overdue Debtor Concentration</div>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                ₹5.20 Lakhs outstanding from Balaji Retail is over 45 days past terms, exceeding standard 90-day provisioning threshold.
              </p>
            </div>

            <div style={{ background: 'rgba(245, 158, 11, 0.06)', borderLeft: '3px solid var(--amber-warning)', padding: '0.75rem', borderRadius: '6px' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--amber-warning)' }}>GST vs Bank Turnover Disparity (4.2%)</div>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Reported GSTR-1 turnover (₹1.84 Cr) exceeds net bank credit collections (₹1.76 Cr) by 4.2% due to delayed receivables.
              </p>
            </div>

            <div style={{ background: 'rgba(99, 102, 241, 0.06)', borderLeft: '3px solid var(--indigo-primary)', padding: '0.75rem', borderRadius: '6px' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--indigo-light)' }}>Working Capital Utilization at 88%</div>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Existing Cash Credit (CC) limit of ₹25 Lakhs is drawn to ₹22 Lakhs, offering limited headroom for sudden supply shocks.
              </p>
            </div>
          </div>
        </div>

        {/* Pre-emptive Mitigations */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <ShieldCheck size={18} color="var(--emerald-success)" />
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Pre-Emptive Bankability Mitigations</h4>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.06)', borderLeft: '3px solid var(--emerald-success)', padding: '0.75rem', borderRadius: '6px' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--emerald-success)' }}>Enroll Invoices on TReDS Platform</div>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Discounting Reliance Retail receivables (₹18.5L) on RXIL/M1xchange converts credit to Day 3 liquidity at 8.2% p.a., lowering overall WC lag.
              </p>
            </div>

            <div style={{ background: 'rgba(16, 185, 129, 0.06)', borderLeft: '3px solid var(--emerald-success)', padding: '0.75rem', borderRadius: '6px' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--emerald-success)' }}>Covenants Compliance Assurance</div>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Current DSCR (1.48x) comfortably qualifies for CGTMSE collateral-free credit enhancement up to ₹50 Lakhs with 85% credit guarantee.
              </p>
            </div>

            <div style={{ background: 'rgba(16, 185, 129, 0.06)', borderLeft: '3px solid var(--emerald-success)', padding: '0.75rem', borderRadius: '6px' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--emerald-success)' }}>Health Passport Attachment</div>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Include MAUSAM verified cryptographic badge with bank loan application to fast-track credit committee approval from 21 days to 48 hours.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
