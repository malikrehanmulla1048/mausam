import React, { useState } from 'react';
import { 
  Users, AlertTriangle, CheckCircle, Clock, 
  Send, ExternalLink, Filter, TrendingDown, DollarSign, 
  MessageSquare, Smartphone, Check, Loader2, MessageCircle 
} from 'lucide-react';
import { sendCustomerSMS } from '../api/client';

interface Customer {
  id: string;
  name: string;
  location: string;
  phone: string;
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
    phone: '+91 98250 11001',
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
    phone: '+91 98250 11002',
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
    phone: '+91 98250 11003',
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
    phone: '+91 98250 11004',
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
    phone: '+91 98250 11005',
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

export const DebtorDNA: React.FC<DebtorDNAProps> = ({ businessId, language }) => {
  const [selectedGrade, setSelectedGrade] = useState<string>('ALL');
  const [activeModalCust, setActiveModalCust] = useState<Customer | null>(null);
  const [reminderTone, setReminderTone] = useState<'gentle' | 'firm' | 'legal'>('firm');
  const [recipientPhone, setRecipientPhone] = useState<string>('');
  const [smsStatus, setSmsStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [smsDispatchId, setSmsDispatchId] = useState<string>('');
  const [smsDeliveryChannel, setSmsDeliveryChannel] = useState<string>('');
  const [smsIsSimulated, setSmsIsSimulated] = useState<boolean>(true);
  const [smsDeliveryNote, setSmsDeliveryNote] = useState<string>('');
  const [smsErrorMsg, setSmsErrorMsg] = useState<string>('');

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

  // Multilingual SMS reminder template (concise for SMS delivery)
  const getSMSTemplate = (cust: Customer, tone: 'gentle' | 'firm' | 'legal') => {
    const overdue = formatINR(cust.overdueAmount);
    const delayDays = Math.max(0, cust.actualDays - cust.promisedDays);

    if (language === 'hi') {
      if (tone === 'gentle') {
        return `रमेश टेक्सटाइल्स: नमस्ते ${cust.name}, बकाया ${overdue} देय है। कृपया भुगतान की पुष्टि करें। धन्यवाद।`;
      } else if (tone === 'firm') {
        return `अति-आवश्यक रमेश टेक्सटाइल्स: ${cust.name}, ${overdue} का भुगतान ${delayDays} दिनों से लंबित है। कृपया आज ही RTGS/NEFT करें।`;
      } else {
        return `कानूनी नोटिस रमेश टेक्सटाइल्स: ${cust.name}, MSMED Act तहत बकाया ${overdue} 3 दिनों में न भरने पर 3x ब्याज व कानूनी कार्रवाई होगी।`;
      }
    } else if (language === 'gu') {
      return `રમેશ ટેક્સટાઈલ્સ: નમસ્તે ${cust.name}, આપનું ${overdue} નું પેમેન્ટ ${delayDays} દિવસથી બાકી છે. કૃપા કરીને તાત્કાલિક ચૂકવણી કરશોજી.`;
    }

    // Default English
    if (tone === 'gentle') {
      return `Ramesh Textiles: Gentle courtesy reminder for ${cust.name}. Overdue ${overdue} is pending. Kindly confirm payment schedule. Thank you.`;
    } else if (tone === 'firm') {
      return `URGENT Ramesh Textiles: ${cust.name}, payment of ${overdue} is overdue by ${delayDays} days. Please process payment today to avoid supply hold.`;
    } else {
      return `NOTICE Ramesh Textiles: ${cust.name}, dues ${overdue} unpaid past terms. Under MSMED Act, interest at 3x RBI rate applies. Clear within 3 days.`;
    }
  };

  const openCustomerModal = (cust: Customer) => {
    setActiveModalCust(cust);
    setRecipientPhone(cust.phone || '+91 98250 11001');
    setSmsStatus('idle');
    setSmsDispatchId('');
    setSmsDeliveryChannel('');
    setSmsIsSimulated(true);
    setSmsDeliveryNote('');
    setSmsErrorMsg('');
  };

  const handleSendSMS = async () => {
    if (!activeModalCust) return;
    setSmsStatus('sending');
    setSmsErrorMsg('');
    try {
      const res = await sendCustomerSMS(businessId, activeModalCust.id, {
        phone: recipientPhone,
        message: getSMSTemplate(activeModalCust, reminderTone),
        tone: reminderTone,
        language,
        amount_str: formatINR(activeModalCust.overdueAmount),
        days_overdue: Math.max(0, activeModalCust.actualDays - activeModalCust.promisedDays),
      });
      setSmsStatus('sent');
      setSmsDispatchId(res.dispatch_id || 'SMS-DISPATCHED');
      setSmsDeliveryChannel(res.delivery_channel || 'SIMULATED_GATEWAY');
      setSmsIsSimulated(Boolean(res.is_simulated ?? (res.delivery_channel === 'SIMULATED_GATEWAY')));
      setSmsDeliveryNote(res.delivery_note || '');
    } catch (err: any) {
      setSmsStatus('error');
      setSmsErrorMsg(err.message || 'Failed to dispatch SMS');
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
                  onClick={() => openCustomerModal(cust)}
                  className="btn-primary"
                  style={{ flex: 1, fontSize: '0.76rem', padding: '0.45rem', justifyContent: 'center', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                >
                  <MessageSquare size={14} /> Send SMS Reminder
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* SMS Modal */}
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
          <div className="glass-panel" style={{ width: '100%', maxWidth: '540px', padding: '1.75rem', background: 'var(--bg-surface)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <Smartphone size={20} color="#38bdf8" />
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>SMS Payment Reminder</h3>
                <span className="pill pill-indigo" style={{ fontSize: '0.68rem', padding: '0.15rem 0.45rem' }}>Transactional SMS</span>
              </div>
              <button onClick={() => setActiveModalCust(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}>×</button>
            </div>

            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Drafted for <strong>{activeModalCust.name}</strong> • Overdue: <span style={{ color: 'var(--rose-danger)', fontWeight: 600 }}>{formatINR(activeModalCust.overdueAmount)}</span>
            </p>

            {/* Recipient Phone Input */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem', fontWeight: 600 }}>
                Recipient Mobile Number (E.164 format)
              </label>
              <input
                type="text"
                value={recipientPhone}
                onChange={(e) => setRecipientPhone(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-medium)',
                  borderRadius: '6px',
                  padding: '0.5rem 0.75rem',
                  color: 'var(--text-primary)',
                  fontSize: '0.85rem',
                  outline: 'none',
                }}
                placeholder="+91 98250 12345"
              />
            </div>

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
            }}>
              {getSMSTemplate(activeModalCust, reminderTone)}
            </div>

            {/* Character & Segment Counter */}
            {(() => {
              const text = getSMSTemplate(activeModalCust, reminderTone);
              const isUnder160 = text.length <= 160;
              return (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.4rem', marginBottom: '1rem' }}>
                  <span style={{ color: isUnder160 ? 'var(--emerald-success)' : 'var(--amber-warning)', fontWeight: 600 }}>
                    {text.length} / 160 characters • {Math.ceil(text.length / 160)} SMS Part{Math.ceil(text.length / 160) > 1 ? 's' : ''}
                  </span>
                  <span>DLT Header: RMSTXT</span>
                </div>
              );
            })()}

            {/* Status alerts */}
            {smsStatus === 'sent' && (
              smsIsSimulated ? (
                <div style={{
                  background: 'rgba(245, 158, 11, 0.12)',
                  border: '1px solid var(--amber-warning)',
                  borderRadius: '8px',
                  padding: '0.75rem 0.95rem',
                  fontSize: '0.8rem',
                  color: 'var(--text-primary)',
                  marginBottom: '1rem',
                  lineHeight: 1.5,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: 'var(--amber-warning)', marginBottom: '0.3rem' }}>
                    <AlertTriangle size={16} />
                    <span>Simulated Gateway Mode • Ref: {smsDispatchId}</span>
                  </div>
                  <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.78rem' }}>
                    Logged to MongoDB audit trail. No telecom SMS provider (AWS SNS / Twilio / Fast2SMS) credentials are set in <code>backend/.env</code>, so cellular transmission was simulated.
                  </p>
                  <p style={{ margin: '0.4rem 0 0 0', color: '#38bdf8', fontSize: '0.78rem', fontWeight: 600 }}>
                    👉 Click "Send via WhatsApp" below to deliver directly to {recipientPhone} right now!
                  </p>
                </div>
              ) : (
                <div style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid var(--emerald-success)',
                  borderRadius: '8px',
                  padding: '0.65rem 0.9rem',
                  fontSize: '0.8rem',
                  color: 'var(--emerald-success)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '1rem'
                }}>
                  <Check size={16} />
                  <span>Real SMS dispatched via {smsDeliveryChannel}! Ref: <strong>{smsDispatchId}</strong></span>
                </div>
              )
            )}
            {smsStatus === 'error' && (
              <div style={{
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid var(--rose-danger)',
                borderRadius: '8px',
                padding: '0.65rem 0.9rem',
                fontSize: '0.8rem',
                color: 'var(--rose-danger)',
                marginBottom: '1rem'
              }}>
                {smsErrorMsg}
              </div>
            )}

            {/* CTA */}
            {(() => {
              const cleanDigits = recipientPhone.replace(/\D/g, '');
              const waTarget = cleanDigits.startsWith('91') ? cleanDigits : `91${cleanDigits}`;
              const cleanSmsPhone = recipientPhone.replace(/\s+/g, '');
              const messageText = getSMSTemplate(activeModalCust, reminderTone);

              return (
                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', flexWrap: 'wrap', alignItems: 'center' }}>
                  <button onClick={() => setActiveModalCust(null)} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
                    Close
                  </button>
                  <a
                    href={`https://wa.me/${waTarget}?text=${encodeURIComponent(messageText)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary"
                    style={{
                      fontSize: '0.8rem',
                      textDecoration: 'none',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      background: '#25D366',
                      color: '#000',
                      fontWeight: 700,
                      border: 'none',
                    }}
                    title="Deliver reminder instantly to receiver's phone via WhatsApp"
                  >
                    <MessageCircle size={15} /> Send via WhatsApp
                  </a>
                  <a
                    href={`sms:${cleanSmsPhone}?body=${encodeURIComponent(messageText)}`}
                    className="btn-secondary"
                    style={{ fontSize: '0.8rem', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                    title="Open native mobile device Messages app"
                  >
                    <Smartphone size={14} /> Open Phone SMS
                  </a>
                  <button
                    onClick={handleSendSMS}
                    disabled={smsStatus === 'sending'}
                    className="btn-secondary"
                    style={{ fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                    title="Send via backend SMS gateway (simulated or live if configured)"
                  >
                    {smsStatus === 'sending' ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                    {smsStatus === 'sent' ? 'Resend via Gateway' : 'Send via SMS Gateway'}
                  </button>
                </div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
};
