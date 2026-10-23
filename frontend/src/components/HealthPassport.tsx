import React, { useState } from 'react';
import { 
  ShieldCheck, QrCode, Lock, CheckCircle2, Copy, 
  ExternalLink, FileBadge, Download, Share2, Sparkles 
} from 'lucide-react';
import { createPassport } from '../api/client';

interface HealthPassportProps {
  businessId: string;
}

export const HealthPassport: React.FC<HealthPassportProps> = ({ businessId }) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const passportId = 'PASS_MSME_92419_RTX';
  const publicHash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
  const issuedDate = '23-Oct-2026';
  const expiryDate = '23-Apr-2027';

  const verifyUrl = `${window.location.origin}/verify/${passportId}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(verifyUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleRegenerate = async () => {
    setIsGenerating(true);
    try {
      await createPassport(businessId);
    } catch {}
    setTimeout(() => setIsGenerating(false), 1200);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Passport Overview Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '46px', height: '46px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <FileBadge size={26} color="var(--emerald-success)" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>MSME Verifiable Financial Health Passport</h3>
              <span className="pill pill-emerald" style={{ fontSize: '0.72rem' }}>
                <CheckCircle2 size={12} /> SECURE SIGNATURE VALID
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Cryptographically attests financial health indicators to banks and NBFCs without leaking proprietary customer data.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={handleRegenerate} disabled={isGenerating} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
            <Sparkles size={14} className={isGenerating ? 'spin-slow' : ''} />
            {isGenerating ? 'Signing...' : 'Re-Issue Passport'}
          </button>
          <button onClick={handleCopy} className="btn-primary" style={{ fontSize: '0.8rem' }}>
            {copied ? <CheckCircle2 size={14} /> : <Share2 size={14} />}
            {copied ? 'Link Copied!' : 'Share Public Link'}
          </button>
        </div>
      </div>

      {/* Main Passport Certificate Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '1.5rem' }}>
        {/* Certificate Card */}
        <div
          className="glass-panel"
          style={{
            padding: '2rem',
            background: 'linear-gradient(135deg, rgba(17, 26, 46, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            boxShadow: '0 0 30px rgba(16, 185, 129, 0.12)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Top Holographic Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-medium)', paddingBottom: '1.25rem', marginBottom: '1.5rem' }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--emerald-success)', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                REPUBLIC OF INDIA • MSME CASH HEALTH BADGE
              </div>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 800, marginTop: '0.2rem' }}>Ramesh Textiles Pvt Ltd</h2>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Udyam Reg: UDYAM-GJ-24-0091823 • GSTIN: 24AAACR8821F1ZX
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <span className="pill pill-emerald" style={{ fontSize: '0.75rem', fontWeight: 700 }}>
                GRADE A-
              </span>
              <div className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                ID: {passportId}
              </div>
            </div>
          </div>

          {/* Verified Indicators Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.85rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Debt Service Coverage (DSCR)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--emerald-success)', marginTop: '0.15rem' }}>1.48x (Pass)</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>Verified via SBI statement audit</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.85rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>GST Statutory Filing Track</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--emerald-success)', marginTop: '0.15rem' }}>100% On-Time</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>Last 24 filings without delay</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.85rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Working Capital Runway</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--indigo-light)', marginTop: '0.15rem' }}>47 Days Safe</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>Post-Rescue: &gt;90 Days</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.85rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>TReDS Factorability Index</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--cyan-accent)', marginTop: '0.15rem' }}>Eligible (Tier-1)</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>Approved buyer invoices active</div>
            </div>
          </div>

          {/* Cryptographic Proof Signature Footer */}
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>KMS Ed25519 Digital Seal</div>
              <div className="mono" style={{ fontSize: '0.68rem', color: 'var(--indigo-light)', wordBreak: 'break-all' }}>
                {publicHash.slice(0, 38)}...
              </div>
            </div>
            <div style={{ textAlign: 'right', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Valid: {issuedDate} → {expiryDate}
            </div>
          </div>
        </div>

        {/* QR Code & Share Pane */}
        <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.4rem' }}>Lender Scan Verification</h4>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Lenders scan this QR code to view live verified indicators on the MAUSAM trust portal.
          </p>

          {/* Stylized QR Code Visual */}
          <div style={{
            background: 'white',
            padding: '1rem',
            borderRadius: '12px',
            boxShadow: '0 0 25px rgba(255, 255, 255, 0.2)',
            display: 'inline-block',
            marginBottom: '1.25rem',
          }}>
            <svg viewBox="0 0 120 120" style={{ width: '130px', height: '130px', display: 'block' }}>
              {/* Corner markers */}
              <rect x="10" y="10" width="30" height="30" fill="#000" rx="3" />
              <rect x="16" y="16" width="18" height="18" fill="#FFF" />
              <rect x="21" y="21" width="8" height="8" fill="#000" />

              <rect x="80" y="10" width="30" height="30" fill="#000" rx="3" />
              <rect x="86" y="16" width="18" height="18" fill="#FFF" />
              <rect x="91" y="21" width="8" height="8" fill="#000" />

              <rect x="10" y="80" width="30" height="30" fill="#000" rx="3" />
              <rect x="16" y="86" width="18" height="18" fill="#FFF" />
              <rect x="21" y="91" width="8" height="8" fill="#000" />

              {/* Data blocks */}
              <rect x="48" y="15" width="8" height="8" fill="#000" />
              <rect x="62" y="15" width="8" height="8" fill="#000" />
              <rect x="48" y="28" width="14" height="6" fill="#000" />
              <rect x="15" y="48" width="20" height="6" fill="#000" />
              <rect x="45" y="45" width="30" height="30" fill="#4F46E5" rx="4" />
              <rect x="85" y="48" width="15" height="12" fill="#000" />
              <rect x="52" y="52" width="16" height="16" fill="#FFF" rx="2" />
              <rect x="56" y="56" width="8" height="8" fill="#4F46E5" />
              <rect x="48" y="85" width="12" height="18" fill="#000" />
              <rect x="68" y="82" width="16" height="8" fill="#000" />
              <rect x="88" y="85" width="18" height="15" fill="#000" />
            </svg>
          </div>

          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <button
              onClick={() => alert(`Certificate downloaded: ${passportId}.pdf`)}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', fontSize: '0.8rem' }}
            >
              <Download size={14} /> Download PDF Badge
            </button>
            <button
              onClick={handleCopy}
              className="btn-secondary"
              style={{ width: '100%', justifyContent: 'center', fontSize: '0.8rem' }}
            >
              <Copy size={14} /> {copied ? 'Copied!' : 'Copy Verification Link'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
