import React, { useState } from 'react';
import { 
  ShieldAlert, CheckCircle2, AlertOctagon, FileSpreadsheet, 
  ArrowRightLeft, AlertTriangle, FileText, Check, X, Eye 
} from 'lucide-react';

interface Finding {
  id: string;
  type: 'circular_billing' | 'phantom_gst' | 'ghost_invoice' | 'tds_mismatch';
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  amount: number;
  description: string;
  parties: string[];
  suggestedAction: string;
  status: 'OPEN' | 'REVIEWED' | 'DISPUTED';
}

const mockFindings: Finding[] = [
  {
    id: 'find_01',
    type: 'circular_billing',
    title: 'Suspected Circular Invoicing Ring Detected',
    severity: 'CRITICAL',
    amount: 1480000,
    description: 'Algorithmic loop detected across 3 entities: Ramesh Textiles -> Subhash Fabrics -> Shivam Dyeing -> Ramesh Textiles with identical fabric lot numbers and near-zero margin within 14 days.',
    parties: ['Subhash Fabrics Pvt Ltd', 'Shivam Dyeing Works'],
    suggestedAction: 'Isolate ledger entries, request physical E-Way bill proofs, and notify compliance officer before filing GST return.',
    status: 'OPEN',
  },
  {
    id: 'find_02',
    type: 'phantom_gst',
    title: 'Ineligible ITC Claim on Cancelled GSTIN',
    severity: 'HIGH',
    amount: 242000,
    description: 'Input Tax Credit of ₹2,42,000 claimed in GSTR-3B for vendor Rajdhani Yarn Mills. Vendor GSTIN (24AAACR1234F1Z5) was retrospectively cancelled by GST authorities on 12-Jan-2025.',
    parties: ['Rajdhani Yarn Mills'],
    suggestedAction: 'Reverse ITC in Table 4(B)(2) of next GSTR-3B to avoid mandatory 18% p.a. interest penalty under Section 50(3).',
    status: 'OPEN',
  },
  {
    id: 'find_03',
    type: 'ghost_invoice',
    title: 'Unreconciled Invoices with Missing Bank Credits',
    severity: 'HIGH',
    amount: 580000,
    description: '3 sales invoices totaling ₹5,80,000 recorded in Tally as "Paid by Cheque" have no matching clearance credit in SBI or HDFC bank statements over 45 days.',
    parties: ['Surat Silk Traders'],
    suggestedAction: 'Verify cheque dishonour advice with bank manager or reclassify to Sundry Debtors.',
    status: 'OPEN',
  },
  {
    id: 'find_04',
    type: 'tds_mismatch',
    title: 'Form 26AS vs Book TDS Credit Variance',
    severity: 'MEDIUM',
    amount: 48500,
    description: 'Customer deducted 2% Section 194C TDS in books, but PAN-level credit is unreflected in Traces 26AS for Q3.',
    parties: ['Kothari Exports Corp'],
    suggestedAction: 'Send automated Form 16A request letter to debtor finance department.',
    status: 'REVIEWED',
  },
];

export const TruthCheck: React.FC = () => {
  const [findings, setFindings] = useState<Finding[]>(mockFindings);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  const formatINR = (val: number) => {
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const handleUpdateStatus = (id: string, newStatus: 'OPEN' | 'REVIEWED' | 'DISPUTED') => {
    setFindings(findings.map((f) => (f.id === id ? { ...f, status: newStatus } : f)));
    if (selectedFinding && selectedFinding.id === id) {
      setSelectedFinding({ ...selectedFinding, status: newStatus });
    }
  };

  const totalAtRisk = findings
    .filter((f) => f.status === 'OPEN')
    .reduce((acc, f) => acc + f.amount, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 3-Way Reconciliation Scorecard Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Truth Check: 3-Way Reconciliation Matrix</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Cross-validating GST Returns (GSTR-1, 2B, 3B), Bank Statements, and Tally ERP Books
            </p>
          </div>
          <div className="pill pill-rose" style={{ padding: '0.4rem 0.8rem' }}>
            <AlertOctagon size={16} /> Total Anomaly Exposure: {formatINR(totalAtRisk)}
          </div>
        </div>

        {/* 3-Way Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--cyan-accent)', fontSize: '0.85rem', fontWeight: 600 }}>
              <FileSpreadsheet size={16} /> GST Portal vs GSTR-2B
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, marginTop: '0.5rem' }}>94.2% Matched</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--rose-danger)', marginTop: '0.2rem' }}>
              ₹2.42L Disallowed ITC from cancelled vendor
            </div>
          </div>

          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--indigo-light)', fontSize: '0.85rem', fontWeight: 600 }}>
              <ArrowRightLeft size={16} /> Bank Txns vs Invoices
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, marginTop: '0.5rem' }}>91.8% Matched</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--amber-warning)', marginTop: '0.2rem' }}>
              3 Ghost cheques uncredited in bank ledger
            </div>
          </div>

          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--emerald-success)', fontSize: '0.85rem', fontWeight: 600 }}>
              <CheckCircle2 size={16} /> Tally ERP Ledger Sync
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, marginTop: '0.5rem' }}>100% Up to Date</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Synced with Surat branch tally server
            </div>
          </div>
        </div>
      </div>

      {/* Findings List & Detail Pane */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedFinding ? '1.2fr 1fr' : '1fr', gap: '1.25rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
            Detected Discrepancies & Compliance Risks ({findings.length})
          </h4>

          {findings.map((f) => (
            <div
              key={f.id}
              className="glass-card-interactive"
              onClick={() => setSelectedFinding(f)}
              style={{
                padding: '1.25rem',
                borderLeft: `4px solid ${f.severity === 'CRITICAL' ? 'var(--rose-danger)' : f.severity === 'HIGH' ? 'var(--amber-warning)' : 'var(--indigo-primary)'}`,
                background: selectedFinding?.id === f.id ? 'var(--bg-card-hover)' : undefined,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className={`pill ${f.severity === 'CRITICAL' ? 'pill-rose' : f.severity === 'HIGH' ? 'pill-amber' : 'pill-indigo'}`}>
                      {f.severity}
                    </span>
                    <span className="pill" style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-secondary)' }}>
                      {f.type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className={`pill ${f.status === 'REVIEWED' ? 'pill-emerald' : f.status === 'DISPUTED' ? 'pill-amber' : 'pill-rose'}`}>
                      {f.status}
                    </span>
                  </div>
                  <h4 style={{ fontSize: '1.02rem', fontWeight: 700, marginTop: '0.5rem' }}>{f.title}</h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.5 }}>
                    {f.description}
                  </p>
                </div>

                <div style={{ textAlign: 'right', whiteSpace: 'nowrap', marginLeft: '1rem' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>At Risk</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--rose-danger)' }}>
                    {formatINR(f.amount)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Selected Finding Detail Drawer */}
        {selectedFinding && (
          <div className="glass-panel" style={{ padding: '1.5rem', height: 'fit-content', border: '1px solid var(--border-glow)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Finding Investigation</h4>
              <button onClick={() => setSelectedFinding(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem' }}>×</button>
            </div>

            <div style={{ fontSize: '0.82rem', marginBottom: '1rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {selectedFinding.description}
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.85rem', borderRadius: '8px', marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Involved Entities</div>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', marginTop: '0.2rem' }}>
                {selectedFinding.parties.join(', ')}
              </div>
            </div>

            <div style={{ background: 'rgba(99, 102, 241, 0.08)', border: '1px solid var(--border-glow)', padding: '0.85rem', borderRadius: '8px', marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--indigo-light)', fontWeight: 600 }}>AI Recommended Remediation</div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', marginTop: '0.25rem', lineHeight: 1.5 }}>
                {selectedFinding.suggestedAction}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button
                onClick={() => handleUpdateStatus(selectedFinding.id, 'REVIEWED')}
                className="btn-success"
                style={{ fontSize: '0.78rem', padding: '0.45rem 0.85rem' }}
              >
                <Check size={14} /> Mark as Reviewed
              </button>
              <button
                onClick={() => handleUpdateStatus(selectedFinding.id, 'DISPUTED')}
                className="btn-secondary"
                style={{ fontSize: '0.78rem', padding: '0.45rem 0.85rem' }}
              >
                <AlertTriangle size={14} /> Flag Dispute
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
