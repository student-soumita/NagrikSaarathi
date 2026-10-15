import React from 'react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES_METADATA, setAppLanguage } from '../i18n';

export function LanguageSelectorModal({ isOpen, onClose }) {
  const { t, i18n } = useTranslation();

  if (!isOpen) return null;

  const currentLang = i18n.language;

  const handleSelect = (code) => {
    setAppLanguage(code);
    onClose();
  };

  return (
    <div className="civic-modal-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="lang-modal-title">
      <div className="civic-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '720px' }}>
        <div className="civic-modal-header">
          <div>
            <h2 id="lang-modal-title" style={{ fontSize: '1.4rem', marginBottom: '4px' }}>
              {t('app.changeLanguage')} / Choose Language
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', margin: 0 }}>
              संविधान की 8वीं अनुसूची की सभी 22 भारतीय भाषाएं समर्थित हैं। (All 22 Eighth Schedule Indian languages supported)
            </p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose} aria-label={t('common.close')}>
            ✕
          </button>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '10px',
            marginTop: '16px',
            maxHeight: '60vh',
            overflowY: 'auto',
            paddingRight: '6px',
          }}
        >
          {LANGUAGES_METADATA.map((lang) => {
            const isSelected = currentLang === lang.code;
            return (
              <button
                key={lang.code}
                onClick={() => handleSelect(lang.code)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '12px 14px',
                  backgroundColor: isSelected ? 'var(--color-teal-light)' : 'var(--color-surface)',
                  border: isSelected ? '2px solid var(--color-teal)' : '1px solid var(--color-border)',
                  borderRadius: 'var(--border-radius)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                }}
                className="civic-lang-option"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                  <span
                    style={{
                      fontSize: '1.15rem',
                      fontWeight: 700,
                      color: isSelected ? 'var(--color-teal-dark)' : 'var(--color-navy)',
                    }}
                  >
                    {lang.nativeName}
                  </span>
                  {lang.supportsVoice && (
                    <span
                      title="Supports Voice / ध्वनि समर्थित"
                      style={{ fontSize: '0.75rem', color: 'var(--color-teal)', fontWeight: 600 }}
                    >
                      🎙️
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                  {lang.englishName} • {lang.script}
                </div>
                {lang.direction === 'rtl' && (
                  <span style={{ fontSize: '0.6875rem', color: 'var(--color-saffron-dark)', marginTop: '4px' }}>
                    Right-to-Left (RTL)
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div style={{ marginTop: '20px', borderTop: '1px solid var(--color-border-subtle)', paddingTop: '12px', textAlign: 'right' }}>
          <button className="btn btn-secondary" onClick={onClose}>
            {t('common.close')}
          </button>
        </div>
      </div>
    </div>
  );
}
