import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES_METADATA, setAppLanguage } from '../i18n';
import { LanguageSelectorModal } from '../components/LanguageSelectorModal';

export function LandingPage({ onExploreSchemes, onStartForm, onViewDashboard }) {
  const { t, i18n } = useTranslation();
  const [isLangModalOpen, setIsLangModalOpen] = useState(false);
  const currentLang = i18n.language;

  return (
    <div className="civic-container" style={{ paddingTop: 'var(--space-2xl)', paddingBottom: 'var(--space-3xl)' }}>
      {/* Editorial Hero Section */}
      <div style={{ maxWidth: '840px', marginBottom: 'var(--space-2xl)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <span className="badge badge-civic">{t('landing.badgeCivic')}</span>
          <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
            Eighth Schedule • 22 Official Languages
          </span>
        </div>

        <h1 style={{ fontSize: '2.5rem', marginBottom: '16px', lineHeight: '1.2' }}>
          {t('landing.headline')}
        </h1>

        <p style={{ fontSize: '1.15rem', color: 'var(--color-text-secondary)', lineHeight: '1.6', marginBottom: '28px' }}>
          {t('landing.description')}
        </p>

        {/* Action CTAs */}
        <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={onExploreSchemes || onStartForm}>
            🏛️ {currentLang === 'hi' ? 'सरकारी योजनाएं खोजें' : 'Explore All Schemes'} →
          </button>
          <button className="btn btn-saffron btn-lg" onClick={onStartForm}>
            ✍️ {t('landing.primaryCta')}
          </button>
          <button className="btn btn-secondary btn-lg" onClick={onViewDashboard}>
            📊 {t('landing.secondaryCta')}
          </button>
        </div>
      </div>

      {/* Immediate Language Selection Grid (Before Starting) */}
      <div className="civic-card" style={{ marginBottom: 'var(--space-2xl)' }}>
        <div className="civic-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.35rem', marginBottom: '4px' }}>
              {t('app.language')} / अपनी भाषा चुनें (Select Your Language)
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', margin: 0 }}>
              आप किसी भी भाषा में आवेदन को समझ सकते हैं (Assistance available in all 22 official languages):
            </p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => setIsLangModalOpen(true)}>
            {t('app.changeLanguage')}
          </button>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
            gap: '8px',
          }}
        >
          {LANGUAGES_METADATA.map((lang) => {
            const isSelected = currentLang === lang.code;
            return (
              <button
                key={lang.code}
                onClick={() => setAppLanguage(lang.code)}
                style={{
                  padding: '10px 12px',
                  backgroundColor: isSelected ? 'var(--color-teal)' : 'var(--color-surface)',
                  color: isSelected ? '#FFFFFF' : 'var(--color-navy)',
                  border: isSelected ? '1px solid var(--color-teal)' : '1px solid var(--color-border)',
                  borderRadius: 'var(--border-radius)',
                  cursor: 'pointer',
                  textAlign: 'center',
                  fontWeight: 600,
                  fontSize: '0.9375rem',
                  transition: 'all 0.15s ease',
                }}
              >
                <div>{lang.nativeName}</div>
                <div style={{ fontSize: '0.7rem', opacity: isSelected ? 0.9 : 0.65 }}>
                  {lang.englishName}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Civic Features Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <div className="civic-card" style={{ marginBottom: 0 }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🇮🇳</div>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>{t('landing.feature1Title')}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', margin: 0 }}>
            {t('landing.feature1Desc')}
          </p>
        </div>

        <div className="civic-card" style={{ marginBottom: 0 }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🔒</div>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>{t('landing.feature2Title')}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', margin: 0 }}>
            {t('landing.feature2Desc')}
          </p>
        </div>

        <div className="civic-card" style={{ marginBottom: 0 }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🤝</div>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>{t('landing.feature3Title')}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', margin: 0 }}>
            {t('landing.feature3Desc')}
          </p>
        </div>
      </div>

      <LanguageSelectorModal isOpen={isLangModalOpen} onClose={() => setIsLangModalOpen(false)} />
    </div>
  );
}
