import React, { useState } from 'react';
import { 
  Users, AlertTriangle, CheckCircle, Clock, 
  Send, ExternalLink, Filter, TrendingDown, DollarSign, MessageCircle 
} from 'lucide-react';

interface Customer {
  id: string;
  name: string;
  location: string;
  grade: 'A+' | 'A' | 'B' | 'C' | 'D';
  promisedDays: number;
  actualDays: number;
  totalReceivable: number;
  overdueAmount: number;
  workingCapitalDrag: number;
  delayTrend: 'improving' | 'stable' | 'deteriorating';
  lastPaymentDate: string;
}

const mockCustomers: Customer[] = [
  {
    id: 'cust_01',
    name: 'Balaji Retail Fabrics',
    location: 'Ahmedabad, Gujarat',
    grade: 'D',
    promisedDays: 30,
    actualDays: 78,
    totalReceivable: 680000,
    overdueAmount: 520000,
    workingCapitalDrag: 345000,
    delayTrend: 'deteriorating',
    lastPaymentDate: '48 days ago',
  },
  {
    id: 'cust_02',
    name: 'Mehta & Sons Wholesalers',
    location: 'Surat, Gujarat',
    grade: 'C',
    promisedDays: 45,
    actualDays: 72,
    totalReceivable: 940000,
    overdueAmount: 410000,
    workingCapitalDrag: 280000,
    delayTrend: 'deteriorating',
    lastPaymentDate: '32 days ago',
  },
  {
    id: 'cust_03',
    name: 'Kothari Exports Corp',
    location: 'Mumbai, Maharashtra',
    grade: 'B',
    promisedDays: 60,
    actualDays: 66,
    totalReceivable: 1250000,
    overdueAmount: 180000,
    workingCapitalDrag: 95000,
    delayTrend: 'stable',
    lastPaymentDate: '14 days ago',
  },
  {
    id: 'cust_04',
    name: 'Navkar Design Studios',
    location: 'Jaipur, Rajasthan',
    grade: 'A',
    promisedDays: 30,
    actualDays: 32,
    totalReceivable: 420000,
    overdueAmount: 0,
    workingCapitalDrag: 12000,
    delayTrend: 'improving',
    lastPaymentDate: '5 days ago',
  },
  {
    id: 'cust_05',
    name: 'Reliance Retail Supply Vendor',
    location: 'Navi Mumbai, Maharashtra',
    grade: 'A+',
    promisedDays: 45,
    actualDays: 44,
    totalReceivable: 1850000,
    overdueAmount: 0,
    workingCapitalDrag: 0,
    delayTrend: 'improving',
    lastPaymentDate: '3 days ago',
  },
];

interface DebtorDNAProps {
  businessId: string;
  language: string;
}

export const DebtorDNA: React.FC<DebtorDNAProps> = ({ language }) => {
  const [selectedGrade, setSelectedGrade] = useState<string>('ALL');
  const [activeModalCust, setActiveModalCust] = useState<Customer | null>(null);
  const [reminderTone, setReminderTone] = useState<'gentle' | 'firm' | 'legal'>('firm');

  const filteredCustomers = mockCustomers.filter((c) => {
    if (selectedGrade === 'ALL') return true;
    return c.grade === selectedGrade;
  });

  const totalDrag = mockCustomers.reduce((acc, c) => acc + c.workingCapitalDrag, 0);
  const totalReceivables = mockCustomers.reduce((acc, c) => acc + c.totalReceivable, 0);

  const formatINR = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  const getGradePill = (grade: string) => {
    switch (grade) {
      case 'A+':
      case 'A':
        return <span className="pill pill-emerald">{grade} Prime</span>;
      case 'B':
        return <span className="pill pill-indigo">{grade} Moderate</span>;
      case 'C':
        return <span className="pill pill-amber">{grade} Delayed</span>;
      case 'D':
        return <span className="pill pill-rose">{grade} Chronic Lag</span>;
      default:
        return null;
    }
  };

  // Multilingual reminder template
  const getWhatsAppTemplate = (cust: Customer, tone: 'gentle' | 'firm' | 'legal') => {
    const overdue = formatINR(cust.overdueAmount);
    if (language === 'hi') {
      if (tone === 'gentle') {
        return `नमस्ते ${cust.name}, रमेश टेक्सटाइल्स से स्मरण पत्र। इनवॉइस बकाया ${overdue} देय हो चुका है। कृपया जल्द भुगतान की पुष्टि करें। धन्यवाद।`;
      } else if (tone === 'firm') {
        return `प्रिय ${cust.name}, रमेश टेक्सटाइल्स से आवश्यक सूचना। आपका बकाया ${overdue} अब ${cust.actualDays - cust.promisedDays} दिनों से लंबित है। कृपया आज ही RTGS/NEFT द्वारा भुगतान सुनिश्चित करें।`;
      } else {
        return `कानूनी नोटिस चेतावनी: ${cust.name}, MSMED Act Section 15/16 के तहत बकाया ${overdue} 45 दिनों की वैधानिक सीमा पार कर चुका है। 3 कार्य दिवसों में भुगतान न करने पर बैंक ब्याज दावा और MSME समाधान पोर्टल पर शिकायत दर्ज की जाएगी।`;
      }
    } else if (language === 'gu') {
      return `નમસ્તે ${cust.name}, રમેશ ટેક્સટાઈલ્સ તરફથી નમ્ર વિનંતી। આપનું ${overdue} નું પેમેન્ટ ${cust.actualDays - cust.promisedDays} દિવસથી બાકી છે। મહેરબાની કરીને તાત્કાલિક ચૂકવણી કરશોજી।`;
    }

    // Default English
    if (tone === 'gentle') {
      return `Dear ${cust.name}, gentle courtesy reminder from Ramesh Textiles regarding outstanding invoices totaling ${overdue}. Kindly let us know once scheduled. Thank you!`;
    } else if (tone === 'firm') {
      return `URGENT: ${cust.name}, payment of ${overdue} is overdue by ${cust.actualDays - cust.promisedDays} days past agreed credit terms. Please process payment today to avoid supply disruption.`;
    } else {
      return `FORMAL NOTICE: ${cust.name}, invoice amount of ${overdue} remains unpaid beyond stipulated credit period. Under MSMED Act Sections 15 & 16, interest at 3x RBI bank rate becomes applicable. Please clear dues within 3 days.`;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Drag Banner */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderLeft: '4px solid var(--amber-warning)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '46px',
            height: '46px',
            borderRadius: '12px',
            background: 'var(--amber-glow)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <TrendingDown size={24} color="var(--amber-warning)" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Total Working Capital Drag from Chronic Late Payers</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Cash locked due to payment delays exceeding agreed contractual credit periods
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Locked Liquidity</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--amber-warning)' }}>
            {formatINR(totalDrag)}
          </div>
        </div>
      </div>

      {/* Customer Filters */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} color="var(--text-secondary)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Filter by Reliability Grade:</span>
          {['ALL', 'A+', 'A', 'B', 'C', 'D'].map((g) => (
            <button
              key={g}
              onClick={() => setSelectedGrade(g)}
              className={selectedGrade === g ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '0.3rem 0.75rem', fontSize: '0.78rem' }}
            >
              {g}
            </button>
          ))}
        </div>

        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Showing {filteredCustomers.length} of {mockCustomers.length} active debtors
        </span>
      </div>

      {/* Customer Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.25rem' }}>
        {filteredCustomers.map((cust) => {
          const delayDays = Math.max(0, cust.actualDays - cust.promisedDays);
          const barPct = Math.min(100, (cust.promisedDays / cust.actualDays) * 100);

          return (
            <div key={cust.id} className="glass-panel" style={{ padding: '1.25rem', position: 'relative' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>{cust.name}</h4>
                  <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>{cust.location}</p>
                </div>
                {getGradePill(cust.grade)}
              </div>

              {/* Payment Timeline Drag Bar */}
              <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Contracted: {cust.promisedDays}d</span>
                  <span style={{ color: delayDays > 0 ? 'var(--rose-danger)' : 'var(--emerald-success)', fontWeight: 600 }}>
                    Actual: {cust.actualDays}d (+{delayDays}d lag)
                  </span>
                </div>
                {/* Visual Progress Track */}
                <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                  <div style={{ width: `${barPct}%`, background: 'var(--indigo-primary)' }} title="Promised period" />
                  <div style={{ width: `${100 - barPct}%`, background: delayDays > 15 ? 'var(--rose-danger)' : 'var(--amber-warning)' }} title="Overdue delay" />
                </div>
              </div>

              {/* Financial Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', fontSize: '0.8rem' }}>
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>Total Receivables</div>
                  <div style={{ fontWeight: 700, marginTop: '0.15rem' }}>{formatINR(cust.totalReceivable)}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>Overdue Balance</div>
                  <div style={{ fontWeight: 700, color: cust.overdueAmount > 0 ? 'var(--rose-danger)' : 'var(--emerald-success)', marginTop: '0.15rem' }}>
                    {formatINR(cust.overdueAmount)}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={() => setActiveModalCust(cust)}
                  className="btn-primary"
                  style={{ flex: 1, fontSize: '0.76rem', padding: '0.45rem', justifyContent: 'center' }}
                >
                  <MessageCircle size={14} /> Send WhatsApp Nudge
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* WhatsApp Modal */}
      {activeModalCust && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1.5rem',
        }}>
          <div className="glass-panel" style={{ width: '100%', maxWidth: '520px', padding: '1.75rem', background: 'var(--bg-surface)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <MessageCircle size={20} color="#25D366" />
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>WhatsApp Payment Reminder</h3>
              </div>
              <button onClick={() => setActiveModalCust(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}>×</button>
            </div>

            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Drafted for <strong>{activeModalCust.name}</strong> • Overdue: {formatINR(activeModalCust.overdueAmount)}
            </p>

            {/* Tone Selector */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              {(['gentle', 'firm', 'legal'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setReminderTone(t)}
                  className={reminderTone === t ? 'btn-primary' : 'btn-secondary'}
                  style={{ textTransform: 'capitalize', fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
                >
                  {t} Tone
                </button>
              ))}
            </div>

            {/* Template Preview */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-medium)',
              borderRadius: '8px',
              padding: '1rem',
              fontSize: '0.85rem',
              lineHeight: 1.6,
              color: 'var(--text-primary)',
              marginBottom: '1.25rem',
            }}>
              {getWhatsAppTemplate(activeModalCust, reminderTone)}
            </div>

            {/* CTA */}
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button onClick={() => setActiveModalCust(null)} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
                Cancel
              </button>
              <a
                href={`https://wa.me/?text=${encodeURIComponent(getWhatsAppTemplate(activeModalCust, reminderTone))}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-success"
                style={{ fontSize: '0.8rem', textDecoration: 'none' }}
              >
                <Send size={14} /> Open in WhatsApp
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
