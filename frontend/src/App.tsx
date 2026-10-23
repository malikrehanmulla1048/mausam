import React, { useState, useEffect } from 'react';
import { 
  CloudSun, Users, ShieldAlert, Building, LifeBuoy, 
  Bot, Bell, FileBadge, Sparkles, Database, Cloud, Shield 
} from 'lucide-react';
import { Navbar } from './components/Navbar';
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
      // In standalone frontend development, fallback gracefully to mock demo
      setBackendOnline(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, [businessId]);

  const tabs = [
    { id: 'forecast', label: 'Cash Mausam', icon: CloudSun, badge: 'D-Day: 47d' },
    { id: 'debtor', label: 'Debtor DNA', icon: Users, badge: '5 Debtors' },
    { id: 'truth', label: 'Truth Check', icon: ShieldAlert, badge: '4 Anomalies' },
    { id: 'risk', label: "Bank's-Eye X-Ray", icon: Building, badge: 'Score 78' },
    { id: 'rescue', label: 'Rescue Planner', icon: LifeBuoy, badge: 'Live Levers' },
    { id: 'committee', label: 'AI Credit Committee', icon: Bot, badge: 'Bedrock' },
    { id: 'alerts', label: 'Alerts Centre', icon: Bell, badge: '3 Actions' },
    { id: 'passport', label: 'Health Passport', icon: FileBadge, badge: 'Verified' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <Navbar
        businessId={businessId}
        onBusinessChange={setBusinessId}
        language={language}
        onLanguageChange={setLanguage}
        weatherStatus={weatherStatus}
        dDay={dDay}
        onRefreshData={checkStatus}
      />

      {/* Main Container */}
      <main style={{ flex: 1, padding: '0 1.5rem 2.5rem', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
        {/* Navigation Tabs Bar */}
        <div
          className="glass-panel"
          style={{
            padding: '0.4rem',
            marginBottom: '1.5rem',
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
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.55rem',
                  padding: '0.65rem 1.1rem',
                  borderRadius: '10px',
                  border: 'none',
                  background: isActive
                    ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(79, 70, 229, 0.25) 100%)'
                    : 'transparent',
                  color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.84rem',
                  fontFamily: 'var(--font-heading)',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.2s ease',
                  borderBottom: isActive ? '2px solid var(--indigo-light)' : '2px solid transparent',
                }}
              >
                <Icon size={16} color={isActive ? 'var(--indigo-light)' : 'var(--text-muted)'} />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span
                    style={{
                      fontSize: '0.68rem',
                      padding: '0.15rem 0.45rem',
                      borderRadius: '6px',
                      background: isActive ? 'rgba(99, 102, 241, 0.35)' : 'rgba(255, 255, 255, 0.05)',
                      color: isActive ? 'white' : 'var(--text-muted)',
                      fontWeight: 600,
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
        {activeTab === 'forecast' && <CashMausam businessId={businessId} />}
        {activeTab === 'debtor' && <DebtorDNA businessId={businessId} language={language} />}
        {activeTab === 'truth' && <TruthCheck />}
        {activeTab === 'risk' && <BanksEyeXRay businessId={businessId} />}
        {activeTab === 'rescue' && <RescuePlanner />}
        {activeTab === 'committee' && <CreditCommittee businessId={businessId} />}
        {activeTab === 'alerts' && <AlertsCentre businessId={businessId} language={language} />}
        {activeTab === 'passport' && <HealthPassport businessId={businessId} />}
      </main>

      {/* Footer & Architecture Badges */}
      <footer
        style={{
          borderTop: '1px solid var(--border-subtle)',
          padding: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          fontSize: '0.78rem',
          color: 'var(--text-muted)',
          background: 'rgba(6, 9, 17, 0.8)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>MAUSAM</span>
          <span>•</span>
          <span>AWS + MongoDB Hackathon 2025 Edition</span>
        </div>

        {/* Architecture Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <span className="pill" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#34D399', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
            <Database size={13} /> MongoDB Atlas
          </span>
          <span className="pill" style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#FBBF24', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
            <Cloud size={13} /> AWS Lambda + Bedrock
          </span>
          <span className="pill" style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#A5B4FC', border: '1px solid rgba(99, 102, 241, 0.25)' }}>
            <Shield size={13} /> KMS Verified Signatures
          </span>
          <span className="pill" style={{ background: backendOnline ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)', color: backendOnline ? '#34D399' : '#FBBF24' }}>
            ● API: {backendOnline ? 'Live Backend Connected' : 'Local Demo Sandbox'}
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;
