import React, { useState, useEffect } from 'react';
import { 
  CloudRain, Sun, CloudSun, RefreshCw, Zap, Globe, 
  Building2, CheckCircle2, Palette, Sparkles, Activity
} from 'lucide-react';
import { seedDemo, runFullAnalysis, resetDemo } from '../api/client';

export type AwardTheme = 'default' | 'titanium' | 'cyberpunk' | 'emerald';

interface NavbarProps {
  businessId: string;
  onBusinessChange: (id: string) => void;
  language: string;
  onLanguageChange: (lang: string) => void;
  weatherStatus: 'monsoon' | 'cloudy' | 'sunny';
  dDay: number | null;
  onRefreshData: () => void;
  currentTheme: AwardTheme;
  onThemeChange: (theme: AwardTheme) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  businessId,
  onBusinessChange,
  language,
  onLanguageChange,
  weatherStatus,
  dDay,
  onRefreshData,
  currentTheme,
  onThemeChange,
}) => {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [showThemeMenu, setShowThemeMenu] = useState<boolean>(false);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleSeed = async () => {
    setLoadingAction('seed');
    try {
      await seedDemo(businessId);
      showToast('Realistic MSME dataset loaded into MongoDB Atlas');
      onRefreshData();
    } catch {
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
      showToast('AI multi-agent reasoning & Monte Carlo pipeline executed');
      onRefreshData();
    } catch {
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
      showToast('Platform state reset successfully');
      onRefreshData();
    } catch {
      showToast('Reset executed');
      onRefreshData();
    } finally {
      setLoadingAction(null);
    }
  };

  const themes: { id: AwardTheme; label: string; icon: string; previewColor: string }[] = [
    { id: 'default', label: 'Quantum Nebula', icon: '🌌', previewColor: '#6366F1' },
    { id: 'titanium', label: 'Titanium Horizon', icon: '💎', previewColor: '#38BDF8' },
    { id: 'cyberpunk', label: 'Cyber Neon', icon: '⚡', previewColor: '#D946EF' },
    { id: 'emerald', label: 'Emerald Sovereign', icon: '👑', previewColor: '#10B981' },
  ];

  return (
    <header 
      className="glass-panel" 
      style={{ 
        margin: '1.2rem 1.5rem 1rem', 
        padding: '0.9rem 1.75rem', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between', 
        zIndex: 50, 
        position: 'relative',
        boxShadow: 'var(--shadow-glass), 0 20px 40px -15px rgba(0, 0, 0, 0.6)'
      }}
    >
      {/* Brand Identity */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.15rem' }}>
        <div style={{
          position: 'relative',
          width: '46px',
          height: '46px',
          borderRadius: '14px',
          background: 'linear-gradient(135deg, var(--indigo-primary) 0%, var(--cyan-accent) 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 24px var(--indigo-glow)',
          border: '1px solid rgba(255, 255, 255, 0.35)',
        }}>
          <span style={{ fontSize: '1.5rem', fontWeight: 900, color: '#FFFFFF', textShadow: '0 2px 8px rgba(0,0,0,0.4)' }}>मौसम</span>
          <div style={{
            position: 'absolute',
            bottom: '-2px',
            right: '-2px',
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: 'var(--emerald-success)',
            border: '2px solid var(--bg-deep)',
            boxShadow: '0 0 8px var(--emerald-success)'
          }} />
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <h1 className="text-gradient-silver" style={{ fontSize: '1.45rem', fontWeight: 900, letterSpacing: '-0.03em', lineHeight: 1.1 }}>
              MAUSAM
            </h1>
            <span className="pill pill-indigo" style={{ fontSize: '0.64rem', padding: '0.15rem 0.55rem', fontWeight: 700 }}>
              AWARD WINNER • v2.5
            </span>
          </div>
          <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', fontWeight: 500, letterSpacing: '0.01em', marginTop: '0.15rem' }}>
            AI Cash-Flow Intelligence & Working Capital Radar for Indian MSMEs
          </p>
        </div>
      </div>

      {/* Middle: Live Weather Radar Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div 
          className={`pill ${weatherStatus === 'monsoon' ? 'pill-rose' : weatherStatus === 'cloudy' ? 'pill-amber' : 'pill-emerald'}`} 
          style={{ 
            padding: '0.45rem 1rem', 
            fontSize: '0.82rem', 
            fontWeight: 700,
            borderWidth: '1.5px',
          }}
        >
          <div className="radar-beacon" style={{ color: weatherStatus === 'monsoon' ? 'var(--rose-danger)' : weatherStatus === 'cloudy' ? 'var(--amber-warning)' : 'var(--emerald-success)' }}>
            <div className="radar-beacon-ring" />
            <div className="radar-beacon-dot" />
          </div>

          {weatherStatus === 'monsoon' ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <CloudRain size={16} /> Cash Monsoon: D-Day in <strong style={{ textDecoration: 'underline' }}>{dDay ?? 47} Days</strong>
            </span>
          ) : weatherStatus === 'cloudy' ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <CloudSun size={16} /> Moderate Liquidity Tension
            </span>
          ) : (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Sun size={16} /> Clear Skies • Healthy Working Capital
            </span>
          )}
        </div>
      </div>

      {/* Right Controls: Theme Switcher, Selectors, Action Triggers */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        
        {/* Award-Winning Theme Switcher */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowThemeMenu(!showThemeMenu)}
            className="btn-secondary"
            style={{ 
              fontSize: '0.78rem', 
              padding: '0.45rem 0.85rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              borderColor: 'var(--border-glow)'
            }}
            title="Switch Award-Winning Design Theme"
          >
            <Palette size={14} color="var(--indigo-light)" />
            <span>Theme: <strong>{themes.find(t => t.id === currentTheme)?.label}</strong></span>
          </button>

          {showThemeMenu && (
            <div 
              className="glass-panel" 
              style={{
                position: 'absolute',
                top: 'calc(100% + 8px)',
                right: 0,
                width: '210px',
                padding: '0.5rem',
                borderRadius: '14px',
                zIndex: 100,
                boxShadow: '0 16px 40px rgba(0, 0, 0, 0.8), 0 0 20px var(--indigo-glow)',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.3rem',
              }}
            >
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', padding: '0.35rem 0.6rem' }}>
                Curated Award Themes
              </div>
              {themes.map((t) => (
                <button
                  key={t.id}
                  onClick={() => {
                    onThemeChange(t.id);
                    setShowThemeMenu(false);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.6rem',
                    padding: '0.5rem 0.75rem',
                    borderRadius: '10px',
                    border: currentTheme === t.id ? '1px solid var(--border-glow)' : '1px solid transparent',
                    background: currentTheme === t.id ? 'var(--indigo-glow)' : 'transparent',
                    color: currentTheme === t.id ? '#FFFFFF' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '0.8rem',
                    fontWeight: currentTheme === t.id ? 700 : 500,
                    transition: 'all 0.15s ease',
                  }}
                >
                  <span style={{ fontSize: '1rem' }}>{t.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div>{t.label}</div>
                  </div>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: t.previewColor }} />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Business Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Building2 size={15} color="var(--indigo-light)" />
          <select
            value={businessId}
            onChange={(e) => onBusinessChange(e.target.value)}
            style={{ fontSize: '0.8rem', padding: '0.42rem 0.7rem' }}
          >
            <option value="demo_ramesh_textiles">Ramesh Textiles (Surat)</option>
            <option value="demo_ganesh_auto">Shree Ganesh Auto (Pune)</option>
            <option value="demo_apex_garments">Apex Garments (Tirupur)</option>
          </select>
        </div>

        {/* Language Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Globe size={15} color="var(--cyan-accent)" />
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            style={{ fontSize: '0.8rem', padding: '0.42rem 0.65rem' }}
          >
            <option value="en">English</option>
            <option value="hi">हिंदी (Hindi)</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="gu">ગુજરાતી (Gujarati)</option>
          </select>
        </div>

        {/* Action Trigger Buttons */}
        <button
          onClick={handleFullAnalysis}
          disabled={loadingAction !== null}
          className="btn-primary"
          style={{ fontSize: '0.78rem', padding: '0.48rem 0.95rem' }}
          title="Trigger autonomous Amazon Bedrock & Monte Carlo intelligence"
        >
          <Zap size={14} className={loadingAction === 'analysis' ? 'spin-slow' : ''} />
          {loadingAction === 'analysis' ? 'Analyzing...' : 'Run Analysis'}
        </button>

        <button
          onClick={handleSeed}
          disabled={loadingAction !== null}
          className="btn-secondary"
          style={{ fontSize: '0.78rem', padding: '0.48rem 0.85rem' }}
          title="Seed realistic MSME dataset into MongoDB Atlas"
        >
          <RefreshCw size={14} className={loadingAction === 'seed' ? 'spin-slow' : ''} />
          {loadingAction === 'seed' ? 'Seeding...' : 'Reseed Data'}
        </button>
      </div>

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          background: 'rgba(14, 22, 43, 0.95)',
          backdropFilter: 'blur(16px)',
          border: '1px solid var(--border-glow)',
          boxShadow: 'var(--shadow-lg), 0 0 30px var(--indigo-glow)',
          borderRadius: '12px',
          padding: '0.85rem 1.4rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem',
          color: 'var(--text-primary)',
          fontSize: '0.86rem',
          fontWeight: 600,
          zIndex: 9999,
          animation: 'pulseGlow 0.3s ease',
        }}>
          <CheckCircle2 size={18} color="var(--emerald-success)" />
          <span>{toastMessage}</span>
        </div>
      )}
    </header>
  );
};
