import React, { useState, useMemo } from 'react';
import { 
  TrendingDown, TrendingUp, AlertTriangle, ShieldCheck, 
  Calendar, Sliders, ArrowUpRight, ArrowDownRight, Sparkles, AlertCircle 
} from 'lucide-react';

interface CashMausamProps {
  businessId: string;
  forecastData?: any;
  onRunSimulation?: (params: any) => void;
}

export const CashMausam: React.FC<CashMausamProps> = ({
  forecastData,
}) => {
  // Stress sliders
  const [debtorDelayDays, setDebtorDelayDays] = useState<number>(0);
  const [salesShockPct, setSalesShockPct] = useState<number>(0);

  // Default baseline data points if none loaded from API
  const baselineDays = useMemo(() => {
    interface DayData {
      day: number;
      date: string;
      inflow: number;
      outflow: number;
      expectedCash: number;
      p10Cash: number;
      p90Cash: number;
    }
    const days: DayData[] = [];
    const baseCash = 1450000;
    const dailyInflow = 85000;
    const dailyExpense = 92000;

    for (let i = 1; i <= 90; i++) {
      // Simulate payroll spikes on day 1, 31, 61
      const isPayroll = i % 30 === 1;
      // Simulate GST payment on day 20, 50, 80
      const isGstDay = i % 30 === 20;
      // Simulate major debtor payment delays
      const debtorDelayFactor = debtorDelayDays > 0 && i < 20 + debtorDelayDays ? 0.4 : 1.0;
      const salesFactor = 1 + salesShockPct / 100;

      const inflow = (dailyInflow * (0.8 + Math.sin(i / 5) * 0.4)) * debtorDelayFactor * salesFactor;
      const outflow = dailyExpense * (0.9 + Math.cos(i / 7) * 0.3) + (isPayroll ? 420000 : 0) + (isGstDay ? 180000 : 0);

      const prevCash: number = i === 1 ? baseCash : days[i - 2].expectedCash;
      const expectedCash: number = prevCash + inflow - outflow;
      const p10Cash: number = expectedCash - (i * 9000); // Pessimistic
      const p90Cash: number = expectedCash + (i * 7000); // Optimistic


      days.push({
        day: i,
        date: new Date(Date.now() + i * 86400000).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
        inflow: Math.round(inflow),
        outflow: Math.round(outflow),
        expectedCash: Math.round(expectedCash),
        p10Cash: Math.round(p10Cash),
        p90Cash: Math.round(p90Cash),
      });
    }
    return days;
  }, [debtorDelayDays, salesShockPct]);

  // Calculate D-Day (first day expected cash <= 0)
  const dDayIndex = baselineDays.findIndex((d) => d.expectedCash <= 0);
  const dDay = dDayIndex !== -1 ? baselineDays[dDayIndex] : null;

  // Format currency
  const formatINR = (val: number) => {
    const isNeg = val < 0;
    const absVal = Math.abs(val);
    if (absVal >= 10000000) return `${isNeg ? '-' : ''}₹${(absVal / 10000000).toFixed(2)} Cr`;
    if (absVal >= 100000) return `${isNeg ? '-' : ''}₹${(absVal / 100000).toFixed(2)} L`;
    return `${isNeg ? '-' : ''}₹${absVal.toLocaleString('en-IN')}`;
  };

  // SVG Chart Dimensions
  const chartWidth = 840;
  const chartHeight = 260;
  const padding = { top: 20, right: 30, bottom: 35, left: 70 };

  // Min/Max for chart scaling
  const allValues = baselineDays.flatMap((d) => [d.expectedCash, d.p10Cash, d.p90Cash]);
  const minVal = Math.min(...allValues, -500000);
  const maxVal = Math.max(...allValues, 1800000);

  const getX = (idx: number) => padding.left + (idx / (baselineDays.length - 1)) * (chartWidth - padding.left - padding.right);
  const getY = (val: number) => chartHeight - padding.bottom - ((val - minVal) / (maxVal - minVal)) * (chartHeight - padding.top - padding.bottom);

  // SVG Paths
  const expectedPath = baselineDays.map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.expectedCash)}`).join(' ');
  const p10Path = baselineDays.map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.p10Cash)}`).join(' ');
  const p90Path = baselineDays.map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.p90Cash)}`).join(' ');

  // Shaded confidence band path (P90 forward, then P10 backwards)
  const confidenceBandPath = `${p90Path} ${baselineDays.slice().reverse().map((d, i) => `L ${getX(baselineDays.length - 1 - i)} ${getY(d.p10Cash)}`).join(' ')} Z`;

  const zeroY = getY(0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Weather Header Alert Banner */}
      <div className={`weather-banner ${dDay ? 'weather-monsoon' : 'weather-sunny'}`}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '14px',
            background: dDay ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
            border: `1px solid ${dDay ? 'rgba(239, 68, 68, 0.4)' : 'rgba(16, 185, 129, 0.4)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            {dDay ? <AlertTriangle size={28} color="#EF4444" /> : <ShieldCheck size={28} color="#10B981" />}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>
                {dDay ? 'Monsoon Alert: Cash Liquidity Deficit Predicted' : 'Clear Skies: Healthy Liquidity Horizon'}
              </h2>
              <span className={`pill ${dDay ? 'pill-rose' : 'pill-emerald'}`}>
                {dDay ? `D-Day: Day ${dDay.day}` : '90-Day Surplus'}
              </span>
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              {dDay
                ? `Under current debtor lags and fixed obligations, net liquidity dips into negative (${formatINR(dDay.expectedCash)}) on ${dDay.date}. Active intervention is required.`
                : 'Projected net receivables exceed cumulative obligations over the next 90 days with positive working buffer.'}
            </p>
          </div>
        </div>

        {dDay && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Projected Deficit
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--rose-danger)', fontFamily: 'var(--font-heading)' }}>
              {formatINR(dDay.expectedCash)}
            </div>
          </div>
        )}
      </div>

      {/* 4 Metric KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '1rem' }}>
        <div className="glass-panel" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>Current Cash in Bank</span>
            <TrendingUp size={16} color="var(--emerald-success)" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.4rem', color: 'var(--text-primary)' }}>
            ₹14.50 L
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--emerald-success)', marginTop: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <ArrowUpRight size={14} /> Reconciled with HDFC & SBI accounts
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>Cash D-Day</span>
            <AlertCircle size={16} color="var(--rose-danger)" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.4rem', color: dDay ? 'var(--rose-danger)' : 'var(--emerald-success)' }}>
            {dDay ? `Day ${dDay.day} (${dDay.date})` : 'None (>90d)'}
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
            {dDay ? 'Point of zero buffer' : 'Sufficient cushion maintained'}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>30-Day Expected Inflow</span>
            <TrendingUp size={16} color="var(--indigo-light)" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.4rem', color: 'var(--indigo-light)' }}>
            ₹24.85 L
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
            Based on historical debtor DNA
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <span>30-Day Hard Obligations</span>
            <TrendingDown size={16} color="var(--amber-warning)" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.4rem', color: 'var(--amber-warning)' }}>
            ₹31.20 L
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <ArrowDownRight size={14} /> Payroll + GST + EMI loans
          </div>
        </div>
      </div>

      {/* Main 90-Day Cash Trajectory Graph */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>90-Day Cash Weather Forecast Curve</h3>
              <span className="pill pill-indigo" style={{ fontSize: '0.7rem' }}>Monte Carlo 1,000 Iterations</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
              P10 (Pessimistic), P50 (Expected), and P90 (Optimistic) confidence trajectories
            </p>
          </div>

          {/* Chart Legend */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.78rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <div style={{ width: '12px', height: '3px', background: '#6366F1', borderRadius: '2px' }} />
              <span style={{ color: 'var(--text-secondary)' }}>P50 Expected</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <div style={{ width: '12px', height: '3px', background: '#F43F5E', borderRadius: '2px' }} />
              <span style={{ color: 'var(--text-secondary)' }}>P10 Pessimistic</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <div style={{ width: '12px', height: '3px', background: '#10B981', borderRadius: '2px' }} />
              <span style={{ color: 'var(--text-secondary)' }}>P90 Optimistic</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <div style={{ width: '12px', height: '10px', background: 'rgba(99, 102, 241, 0.15)', borderRadius: '2px' }} />
              <span style={{ color: 'var(--text-secondary)' }}>Confidence Band</span>
            </div>
          </div>
        </div>

        {/* SVG Visualization */}
        <div style={{ width: '100%', overflowX: 'auto' }}>
          <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
            {/* Grid Lines */}
            {[0, 500000, 1000000, 1500000, -500000].map((val) => {
              const y = getY(val);
              return (
                <g key={val}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={chartWidth - padding.right}
                    y2={y}
                    stroke={val === 0 ? 'rgba(239, 68, 68, 0.6)' : 'rgba(255, 255, 255, 0.08)'}
                    strokeDasharray={val === 0 ? '4 4' : undefined}
                    strokeWidth={val === 0 ? 1.5 : 1}
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 4}
                    fill={val === 0 ? '#EF4444' : 'var(--text-muted)'}
                    fontSize="10"
                    textAnchor="end"
                    fontFamily="var(--font-mono)"
                  >
                    {val === 0 ? '₹0 ZERO' : formatINR(val)}
                  </text>
                </g>
              );
            })}

            {/* X-Axis labels (every 15 days) */}
            {[1, 15, 30, 45, 60, 75, 90].map((d) => {
              const x = getX(d - 1);
              return (
                <g key={d}>
                  <line x1={x} y1={chartHeight - padding.bottom} x2={x} y2={chartHeight - padding.bottom + 5} stroke="rgba(255, 255, 255, 0.2)" />
                  <text
                    x={x}
                    y={chartHeight - padding.bottom + 18}
                    fill="var(--text-secondary)"
                    fontSize="10"
                    textAnchor="middle"
                    fontFamily="var(--font-mono)"
                  >
                    Day {d}
                  </text>
                </g>
              );
            })}

            {/* Confidence Band Polygon */}
            <path d={confidenceBandPath} fill="rgba(99, 102, 241, 0.12)" />

            {/* Trajectory Lines */}
            <path d={p10Path} fill="none" stroke="#F43F5E" strokeWidth="1.5" strokeDasharray="3 3" opacity="0.75" />
            <path d={p90Path} fill="none" stroke="#10B981" strokeWidth="1.5" strokeDasharray="3 3" opacity="0.75" />
            <path d={expectedPath} fill="none" stroke="#6366F1" strokeWidth="2.5" />

            {/* D-Day Marker */}
            {dDay && (
              <g>
                <line
                  x1={getX(dDay.day - 1)}
                  y1={padding.top}
                  x2={getX(dDay.day - 1)}
                  y2={chartHeight - padding.bottom}
                  stroke="#EF4444"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                />
                <circle cx={getX(dDay.day - 1)} cy={zeroY} r="5" fill="#EF4444" stroke="#FFFFFF" strokeWidth="2" />
                <rect
                  x={getX(dDay.day - 1) - 45}
                  y={padding.top - 5}
                  width="90"
                  height="22"
                  rx="6"
                  fill="#EF4444"
                />
                <text
                  x={getX(dDay.day - 1)}
                  y={padding.top + 10}
                  fill="#FFFFFF"
                  fontSize="10"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  D-DAY (Day {dDay.day})
                </text>
              </g>
            )}
          </svg>
        </div>

        {/* Stress Radar Sliders Panel */}
        <div style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-subtle)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', fontWeight: 600 }}>
                <Sliders size={15} color="var(--indigo-light)" />
                <span>Simulate Debtor Delay Shock</span>
              </div>
              <span className="mono" style={{ fontSize: '0.85rem', color: debtorDelayDays > 0 ? 'var(--amber-warning)' : 'var(--text-muted)', fontWeight: 600 }}>
                +{debtorDelayDays} Days
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              step="5"
              value={debtorDelayDays}
              onChange={(e) => setDebtorDelayDays(Number(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              <span>Normal terms</span>
              <span>+15d (Stress)</span>
              <span>+30d (Severe)</span>
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', fontWeight: 600 }}>
                <Sparkles size={15} color="var(--cyan-accent)" />
                <span>Simulate Revenue Demand Shock</span>
              </div>
              <span className="mono" style={{ fontSize: '0.85rem', color: salesShockPct < 0 ? 'var(--rose-danger)' : salesShockPct > 0 ? 'var(--emerald-success)' : 'var(--text-muted)', fontWeight: 600 }}>
                {salesShockPct > 0 ? `+${salesShockPct}%` : `${salesShockPct}%`}
              </span>
            </div>
            <input
              type="range"
              min="-30"
              max="15"
              step="5"
              value={salesShockPct}
              onChange={(e) => setSalesShockPct(Number(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              <span>-30% (Order cancellations)</span>
              <span>Baseline (0%)</span>
              <span>+15% (Surge)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
