import React, { useState, useEffect } from 'react';
import { 
  CloudSun, Users, ShieldAlert, Building, LifeBuoy, 
  Bot, Bell, FileBadge, Sparkles, Database, Cloud, Shield,
  Activity, ArrowUpRight, CheckCircle2, AlertTriangle, Layers
} from 'lucide-react';
import { Navbar, type AwardTheme } from './components/Navbar';
import { CashMausam } from './components/CashMausam';
import { DebtorDNA } from './components/DebtorDNA';
import { TruthCheck } from './components/TruthCheck';
import { BanksEyeXRay } from './components/BanksEyeXRay';
import { RescuePlanner } from './components/RescuePlanner';
import { CreditCommittee } from './components/CreditCommittee';
import { AlertsCentre } from './components/AlertsCentre';
import { HealthPassport } from './components/HealthPassport';
import { getHealth, getOverview } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('forecast');
  const [businessId, setBusinessId] = useState<string>('demo_ramesh_textiles');
  const [language, setLanguage] = useState<string>('en');
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [dDay, setDDay] = useState<number | null>(47);
  const [weatherStatus, setWeatherStatus] = useState<'monsoon' | 'cloudy' | 'sunny'>('monsoon');
  const [currentTheme, setCurrentTheme] = useState<AwardTheme>('default');

  // Sync theme class onto document body
  useEffect(() => {
    const themeClass = currentTheme === 'default' ? '' : `theme-${currentTheme}`;
    document.body.className = themeClass;
  }, [currentTheme]);

  const checkStatus = async () => {
    try {
      const health = await getHealth();
      setBackendOnline(health?.status === 'ok' || health?.status === 'degraded');
      const overview = await getOverview(businessId);
      if (overview?.d_day) {
        setDDay(overview.d_day);
        setWeatherStatus(overview.d_day <= 30 ? 'monsoon' : overview.d_day <= 60 ? 'cloudy' : 'sunny');
      }
    } catch {
      // Standalone development fallback
      setBackendOnline(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, [businessId]);

  const tabs = [
    { id: 'forecast', label: 'Cash Mausam', icon: CloudSun, badge: 'D-Day: 47d', badgeColor: 'pill-rose' },
    { id: 'debtor', label: 'Debtor DNA', icon: Users, badge: '5 Chronic', badgeColor: 'pill-amber' },
    { id: 'truth', label: 'Truth Check', icon: ShieldAlert, badge: '4 Rings', badgeColor: 'pill-rose' },
    { id: 'risk', label: "Bank's-Eye X-Ray", icon: Building, badge: 'Score 78', badgeColor: 'pill-emerald' },
    { id: 'rescue', label: 'Rescue Planner', icon: LifeBuoy, badge: 'Live Levers', badgeColor: 'pill-cyan' },
    { id: 'committee', label: 'AI Credit Committee', icon: Bot, badge: 'Bedrock 3-Agent', badgeColor: 'pill-indigo' },
    { id: 'alerts', label: 'Alerts & WhatsApp', icon: Bell, badge: 'Direct Nudges', badgeColor: 'pill-emerald' },
    { id: 'passport', label: 'Health Passport', icon: FileBadge, badge: 'KMS Signed', badgeColor: 'pill-indigo' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      
      {/* 🌌 Atmospheric Ambient Background Glow Orbs */}
      <div className="ambient-glow-mesh">
        <div className="ambient-orb ambient-orb-1" />
        <div className="ambient-orb ambient-orb-2" />
        <div className="ambient-orb ambient-orb-3" />
      </div>

      {/* Top Navbar */}
      <Navbar
        businessId={businessId}
        onBusinessChange={setBusinessId}
        language={language}
        onLanguageChange={setLanguage}
        weatherStatus={weatherStatus}
        dDay={dDay}
        onRefreshData={checkStatus}
        currentTheme={currentTheme}
        onThemeChange={setCurrentTheme}
      />

      {/* Main Container */}
      <main style={{ flex: 1, padding: '0 1.5rem 2.5rem', maxWidth: '1440px', width: '100%', margin: '0 auto', zIndex: 10, position: 'relative' }}>
        
        {/* 📊 Real-Time Financial Telemetry Ticker (Award-Winning Fintech Header) */}
        <div 
          className="glass-panel" 
          style={{ 
            padding: '0.65rem 1.25rem', 
            marginBottom: '1.25rem', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem',
            fontSize: '0.76rem',
            borderLeft: '4px solid var(--indigo-primary)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: '#FFFFFF' }}>
            <Activity size={14} color="var(--indigo-light)" className="pulse-glow" />
            <span>LIVE MSME TELEMETRY</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap', color: 'var(--text-secondary)' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Working Capital Drag: </span>
              <strong style={{ color: 'var(--amber-warning)' }}>₹21.40 L</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>MSMED Section 16 Rate: </span>
              <strong style={{ color: '#38bdf8' }}>19.5% p.a. (3x RBI Repo)</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>TReDS Factoring Yield: </span>
              <strong style={{ color: 'var(--emerald-success)' }}>8.20% p.a. (RXIL / M1)</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Circular Billing Risk: </span>
              <strong style={{ color: 'var(--rose-danger)' }}>Ring Detected (1 Lot)</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Credit Readiness Score: </span>
              <strong style={{ color: '#A5B4FC' }}>78 / 100 (SIDBI Benchmark)</strong>
            </div>
          </div>
        </div>

        {/* 🚀 Navigation Tabs Dock Bar */}
        <div
          className="nav-dock-capsule"
          style={{
            padding: '0.45rem',
            marginBottom: '1.75rem',
            display: 'flex',
            gap: '0.35rem',
            overflowX: 'auto',
          }}
        >
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`nav-dock-tab ${isActive ? 'active' : ''}`}
                style={{
                  outline: 'none',
                }}
              >
                <Icon 
                  size={16} 
                  color={isActive ? 'var(--indigo-light)' : 'var(--text-muted)'} 
                  style={{ filter: isActive ? 'drop-shadow(0 0 6px var(--indigo-glow))' : 'none' }}
                />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span
                    className={`pill ${tab.badgeColor}`}
                    style={{
                      fontSize: '0.66rem',
                      padding: '0.12rem 0.45rem',
                      fontWeight: 700,
                      boxShadow: isActive ? '0 0 8px currentColor' : 'none',
                    }}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab Content Panels */}
        <div style={{ animation: 'fadeIn 0.25s ease' }}>
          {activeTab === 'forecast' && <CashMausam businessId={businessId} />}
          {activeTab === 'debtor' && <DebtorDNA businessId={businessId} language={language} />}
          {activeTab === 'truth' && <TruthCheck />}
          {activeTab === 'risk' && <BanksEyeXRay businessId={businessId} />}
          {activeTab === 'rescue' && <RescuePlanner />}
          {activeTab === 'committee' && <CreditCommittee businessId={businessId} />}
          {activeTab === 'alerts' && <AlertsCentre businessId={businessId} language={language} />}
          {activeTab === 'passport' && <HealthPassport businessId={businessId} />}
        </div>
      </main>

      {/* 💎 Footer & Architecture Badges */}
      <footer
        className="glass-panel"
        style={{
          margin: '2rem 1.5rem 1.5rem',
          padding: '1.25rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          fontSize: '0.78rem',
          color: 'var(--text-muted)',
          zIndex: 10,
          position: 'relative',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontWeight: 800, color: '#FFFFFF', letterSpacing: '0.05em' }}>MAUSAM PLATFORM</span>
          <span>•</span>
          <span style={{ color: 'var(--text-secondary)' }}>AWS + MongoDB Hackathon 2025 Edition</span>
          <span>•</span>
          <span className="pill pill-cyan" style={{ fontSize: '0.68rem', padding: '0.1rem 0.5rem' }}>
            Zero-Knowledge Privacy Architecture
          </span>
        </div>

        {/* Architecture Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
          <span className="pill pill-emerald" style={{ fontSize: '0.72rem' }}>
            <Database size={13} /> MongoDB Atlas (Sharded Compound Indexes)
          </span>
          <span className="pill pill-amber" style={{ fontSize: '0.72rem' }}>
            <Cloud size={13} /> AWS Bedrock Claude 3.5 Sonnet
          </span>
          <span className="pill pill-indigo" style={{ fontSize: '0.72rem' }}>
            <Shield size={13} /> AWS KMS HMAC-SHA256 Signatures
          </span>
          <span className="pill" style={{ 
            background: backendOnline ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)', 
            color: backendOnline ? '#34D399' : '#FBBF24',
            border: `1px solid ${backendOnline ? 'rgba(16, 185, 129, 0.35)' : 'rgba(245, 158, 11, 0.35)'}`,
            fontSize: '0.72rem'
          }}>
            <div className="radar-beacon" style={{ color: backendOnline ? 'var(--emerald-success)' : 'var(--amber-warning)', marginRight: '4px' }}>
              <div className="radar-beacon-ring" />
              <div className="radar-beacon-dot" />
            </div>
            API: {backendOnline ? 'Live Backend Connected (Port 8000)' : 'Local Demo Sandbox'}
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;
