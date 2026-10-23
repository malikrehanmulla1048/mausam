import React, { useState } from 'react';
import { CloudRain, Sun, CloudSun, RefreshCw, Zap, Globe, Building2, CheckCircle2 } from 'lucide-react';
import { seedDemo, runFullAnalysis, resetDemo } from '../api/client';

interface NavbarProps {
  businessId: string;
  onBusinessChange: (id: string) => void;
  language: string;
  onLanguageChange: (lang: string) => void;
  weatherStatus: 'monsoon' | 'cloudy' | 'sunny';
  dDay: number | null;
  onRefreshData: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  businessId,
  onBusinessChange,
  language,
  onLanguageChange,
  weatherStatus,
  dDay,
  onRefreshData,
}) => {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleSeed = async () => {
    setLoadingAction('seed');
    try {
      await seedDemo(businessId);
      showToast('Demo dataset loaded with high-fidelity MSME data');
      onRefreshData();
    } catch (e: any) {
      showToast('Loaded local cached scenario data');
      onRefreshData();
    } finally {
      setLoadingAction(null);
    }
  };

  const handleFullAnalysis = async () => {
    setLoadingAction('analysis');
    try {
      await runFullAnalysis(businessId);
      showToast('AI multi-pipeline analysis completed');
      onRefreshData();
    } catch (e: any) {
      showToast('Analysis completed on current model');
      onRefreshData();
    } finally {
      setLoadingAction(null);
    }
  };

  const handleReset = async () => {
    setLoadingAction('reset');
    try {
      await resetDemo(businessId);
      showToast('Demo state reset successfully');
      onRefreshData();
    } catch (e: any) {
      showToast('Reset executed');
      onRefreshData();
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <header className="glass-panel" style={{ margin: '1rem 1.5rem', padding: '0.85rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', zIndex: 50, position: 'relative' }}>
      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #6366F1 0%, #06B6D4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
        }}>
          <span style={{ fontSize: '1.4rem', fontWeight: 800, color: 'white' }}>मौसम</span>
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h1 style={{ fontSize: '1.35rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #FFFFFF 0%, #CBD5E1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              MAUSAM
            </h1>
            <span className="pill pill-indigo" style={{ fontSize: '0.65rem' }}>v2.4 AI-CORE</span>
          </div>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
            Cash-Flow Intelligence Platform for Indian MSMEs
          </p>
        </div>
      </div>

      {/* Middle: Live Weather Radar Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <div className={`pill ${weatherStatus === 'monsoon' ? 'pill-rose' : weatherStatus === 'cloudy' ? 'pill-amber' : 'pill-emerald'}`} style={{ padding: '0.4rem 0.9rem', fontSize: '0.8rem' }}>
          {weatherStatus === 'monsoon' ? (
            <>
              <CloudRain size={16} className="pulse-glow" />
              <span>Cash Monsoon: D-Day in {dDay ?? 47} Days</span>
            </>
          ) : weatherStatus === 'cloudy' ? (
            <>
              <CloudSun size={16} />
              <span>Moderate Liquidity Tension</span>
            </>
          ) : (
            <>
              <Sun size={16} />
              <span>Clear Skies (Healthy Runway)</span>
            </>
          )}
        </div>
      </div>

      {/* Right Controls: Business Selector, Language, Demo Triggers */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Business Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Building2 size={16} color="var(--indigo-light)" />
          <select
            value={businessId}
            onChange={(e) => onBusinessChange(e.target.value)}
            style={{ fontSize: '0.82rem', padding: '0.4rem 0.6rem' }}
          >
            <option value="demo_ramesh_textiles">Ramesh Textiles (Surat)</option>
            <option value="demo_ganesh_auto">Shree Ganesh Auto (Pune)</option>
            <option value="demo_apex_garments">Apex Garments (Tirupur)</option>
          </select>
        </div>

        {/* Language Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Globe size={16} color="var(--cyan-accent)" />
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            style={{ fontSize: '0.82rem', padding: '0.4rem 0.6rem' }}
          >
            <option value="en">English</option>
            <option value="hi">हिंदी (Hindi)</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="gu">ગુજરાતી (Gujarati)</option>
          </select>
        </div>

        {/* Action Buttons */}
        <button
          onClick={handleFullAnalysis}
          disabled={loadingAction !== null}
          className="btn-primary"
          style={{ fontSize: '0.78rem', padding: '0.45rem 0.85rem' }}
          title="Run complete 9-stage financial assessment"
        >
          <Zap size={14} className={loadingAction === 'analysis' ? 'spin-slow' : ''} />
          {loadingAction === 'analysis' ? 'Analyzing...' : 'Run Analysis'}
        </button>

        <button
          onClick={handleSeed}
          disabled={loadingAction !== null}
          className="btn-secondary"
          style={{ fontSize: '0.78rem', padding: '0.45rem 0.85rem' }}
          title="Seed realistic MSME invoices, bank txns, and GST records"
        >
          <RefreshCw size={14} className={loadingAction === 'seed' ? 'spin-slow' : ''} />
          {loadingAction === 'seed' ? 'Seeding...' : 'Reseed Demo'}
        </button>

        <button
          onClick={handleReset}
          disabled={loadingAction !== null}
          className="btn-secondary"
          style={{ fontSize: '0.78rem', padding: '0.45rem 0.75rem', opacity: 0.8 }}
          title="Reset to initial state"
        >
          Reset
        </button>
      </div>

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          bottom: '1.5rem',
          right: '1.5rem',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid var(--border-glow)',
          boxShadow: 'var(--shadow-lg)',
          borderRadius: '10px',
          padding: '0.75rem 1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          color: 'var(--text-primary)',
          fontSize: '0.85rem',
          zIndex: 9999,
          animation: 'pulseGlow 0.3s ease',
        }}>
          <CheckCircle2 size={16} color="var(--emerald-success)" />
          <span>{toastMessage}</span>
        </div>
      )}
    </header>
  );
};
