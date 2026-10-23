import React, { useState } from 'react';
import { 
  LifeBuoy, Check, Sparkles, TrendingUp, DollarSign, 
  ArrowRight, ShieldCheck, Zap, Sliders, AlertCircle 
} from 'lucide-react';

export const RescuePlanner: React.FC = () => {
  // Lever toggles and values
  const [useEarlyDiscount, setUseEarlyDiscount] = useState<boolean>(true);
  const [earlyDiscountPct, setEarlyDiscountPct] = useState<number>(2);

  const [useInvoiceDiscounting, setUseInvoiceDiscounting] = useState<boolean>(true);
  const [tredsAmount, setTredsAmount] = useState<number>(650000);

  const [useWorkingCapitalLoan, setUseWorkingCapitalLoan] = useState<boolean>(false);
  const [loanAmount, setLoanAmount] = useState<number>(500000);

  const [useSupplierStaggering, setUseSupplierStaggering] = useState<boolean>(true);
  const [supplierDelayDays, setSupplierDelayDays] = useState<number>(15);

  const formatINR = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  // Calculations
  const earlyDiscountCashInjected = useEarlyDiscount ? 420000 : 0;
  const earlyDiscountCost = useEarlyDiscount ? (420000 * earlyDiscountPct) / 100 : 0;

  const invoiceDiscountCashInjected = useInvoiceDiscounting ? Math.round(tredsAmount * 0.98) : 0;
  const invoiceDiscountCost = useInvoiceDiscounting ? Math.round(tredsAmount * 0.02) : 0;

  const loanCashInjected = useWorkingCapitalLoan ? loanAmount : 0;
  const supplierCashSaved = useSupplierStaggering ? 280000 : 0;

  const totalLiquidityUnlocked =
    earlyDiscountCashInjected +
    invoiceDiscountCashInjected +
    loanCashInjected +
    supplierCashSaved;

  const baselineDeficit = -340000;
  const postRescueLowestDip = baselineDeficit + totalLiquidityUnlocked;
  const isRescueSuccessful = postRescueLowestDip > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Simulation Result Header */}
      <div className={`weather-banner ${isRescueSuccessful ? 'weather-sunny' : 'weather-monsoon'}`}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '14px',
            background: isRescueSuccessful ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
            border: `1px solid ${isRescueSuccessful ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            {isRescueSuccessful ? <ShieldCheck size={28} color="#10B981" /> : <AlertCircle size={28} color="#EF4444" />}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>
                {isRescueSuccessful ? 'Liquidity Deficit Successfully Eliminated!' : 'Deficit Remains: Additional Levers Needed'}
              </h2>
              <span className={`pill ${isRescueSuccessful ? 'pill-emerald' : 'pill-rose'}`}>
                {isRescueSuccessful ? 'D-Day Defused' : 'D-Day Imminent'}
              </span>
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              {isRescueSuccessful
                ? `Simulated interventions unlock ${formatINR(totalLiquidityUnlocked)} in working liquidity, turning the projected ₹3.4L deficit into a healthy ${formatINR(postRescueLowestDip)} surplus.`
                : 'Selected interventions are insufficient to bridge the projected Day 47 shortfall.'}
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Net Liquidity Delta</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--emerald-success)' }}>
            +{formatINR(totalLiquidityUnlocked)}
          </div>
        </div>
      </div>

      {/* Before vs After Comparison Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        {/* Baseline (Before) */}
        <div className="glass-panel" style={{ padding: '1.25rem', borderLeft: '4px solid var(--rose-danger)' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--rose-danger)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.05em' }}>
            Baseline Status (Do-Nothing Scenario)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Projected D-Day</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--rose-danger)', marginTop: '0.2rem' }}>Day 47</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Peak Cash Deficit</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--rose-danger)', marginTop: '0.2rem' }}>-₹3.40 Lakhs</div>
            </div>
          </div>
          <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.85rem' }}>
            High risk of dishonoured cheques, vendor supply freeze, and credit rating downgrade.
          </div>
        </div>

        {/* Post-Rescue (After) */}
        <div className="glass-panel" style={{ padding: '1.25rem', borderLeft: '4px solid var(--emerald-success)' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--emerald-success)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.05em' }}>
            Post-Intervention Trajectory
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>New D-Day</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--emerald-success)', marginTop: '0.2rem' }}>None (&gt;90d)</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Lowest Cash Cushion</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--emerald-success)', marginTop: '0.2rem' }}>+{formatINR(postRescueLowestDip)}</div>
            </div>
          </div>
          <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '0.85rem' }}>
            All statutory obligations, payrolls, and raw material purchase orders smoothly covered.
          </div>
        </div>
      </div>

      {/* Interactive Intervention Levers */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.35rem' }}>
          Intervention Simulator: Configure Working Capital Levers
        </h3>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          Toggle and fine-tune levers to immediately model the net cash impact.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          {/* Lever 1: Early Payment Discount */}
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '10px', border: useEarlyDiscount ? '1px solid var(--border-glow)' : '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>
                <Zap size={16} color="var(--indigo-light)" />
                <span>Early Payment Discount</span>
              </div>
              <input
                type="checkbox"
                checked={useEarlyDiscount}
                onChange={(e) => setUseEarlyDiscount(e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              Offer 2/10 Net 30 to prompt-paying debtors (Navkar Design & Kothari Exports).
            </p>
            {useEarlyDiscount && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                  <span>Discount Offered: {earlyDiscountPct}%</span>
                  <span className="mono" style={{ color: 'var(--emerald-success)' }}>+{formatINR(earlyDiscountCashInjected)}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="3"
                  step="0.5"
                  value={earlyDiscountPct}
                  onChange={(e) => setEarlyDiscountPct(Number(e.target.value))}
                />
              </div>
            )}
          </div>

          {/* Lever 2: TReDS Invoice Discounting */}
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '10px', border: useInvoiceDiscounting ? '1px solid var(--border-glow)' : '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>
                <DollarSign size={16} color="var(--cyan-accent)" />
                <span>TReDS Invoice Discounting</span>
              </div>
              <input
                type="checkbox"
                checked={useInvoiceDiscounting}
                onChange={(e) => setUseInvoiceDiscounting(e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              Discount approved Reliance Retail invoices on RXIL platform at ~8.5% annualized.
            </p>
            {useInvoiceDiscounting && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                  <span>Factoring Amount: {formatINR(tredsAmount)}</span>
                  <span className="mono" style={{ color: 'var(--emerald-success)' }}>+{formatINR(invoiceDiscountCashInjected)}</span>
                </div>
                <input
                  type="range"
                  min="200000"
                  max="1200000"
                  step="50000"
                  value={tredsAmount}
                  onChange={(e) => setTredsAmount(Number(e.target.value))}
                />
              </div>
            )}
          </div>

          {/* Lever 3: Supplier Payment Staggering */}
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '10px', border: useSupplierStaggering ? '1px solid var(--border-glow)' : '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>
                <Sliders size={16} color="var(--amber-warning)" />
                <span>Supplier Staggering</span>
              </div>
              <input
                type="checkbox"
                checked={useSupplierStaggering}
                onChange={(e) => setUseSupplierStaggering(e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              Renegotiate yarn suppliers from Net 30 to Net 45 without incurring interest penalties.
            </p>
            {useSupplierStaggering && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                  <span>Deferral: +{supplierDelayDays} Days</span>
                  <span className="mono" style={{ color: 'var(--amber-warning)' }}>Saved {formatINR(supplierCashSaved)}</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="25"
                  step="5"
                  value={supplierDelayDays}
                  onChange={(e) => setSupplierDelayDays(Number(e.target.value))}
                />
              </div>
            )}
          </div>

          {/* Lever 4: MSME Emergency Working Capital Line */}
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.25rem', borderRadius: '10px', border: useWorkingCapitalLoan ? '1px solid var(--border-glow)' : '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>
                <Sparkles size={16} color="var(--purple-agent)" />
                <span>SIDBI / Bank OD Line</span>
              </div>
              <input
                type="checkbox"
                checked={useWorkingCapitalLoan}
                onChange={(e) => setUseWorkingCapitalLoan(e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              Drawdown pre-approved SIDBI Prayaas or Bank Cash Credit overdraft limit.
            </p>
            {useWorkingCapitalLoan && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
                  <span>Drawdown: {formatINR(loanAmount)}</span>
                  <span className="mono" style={{ color: 'var(--emerald-success)' }}>+{formatINR(loanAmount)}</span>
                </div>
                <input
                  type="range"
                  min="200000"
                  max="1000000"
                  step="100000"
                  value={loanAmount}
                  onChange={(e) => setLoanAmount(Number(e.target.value))}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
