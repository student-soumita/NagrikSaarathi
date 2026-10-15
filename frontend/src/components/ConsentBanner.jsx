import React from 'react';
import { useTranslation } from 'react-i18next';

export function ConsentBanner({ consentStatus, onAcceptConsent, onDeclineConsent }) {
  const { t } = useTranslation();

  // If already chosen, render compact status badge
  if (consentStatus !== null) {
    return (
      <div
        style={{
          backgroundColor: consentStatus ? 'var(--color-teal-light)' : 'var(--color-surface-subtle)',
          border: `1px solid ${consentStatus ? 'var(--color-teal)' : 'var(--color-border)'}`,
          borderRadius: 'var(--border-radius)',
          padding: '8px 16px',
          fontSize: '0.8125rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--space-md)',
        }}
      >
        <span style={{ fontWeight: 600, color: consentStatus ? 'var(--color-teal-dark)' : 'var(--color-text-secondary)' }}>
          {consentStatus ? `✓ ${t('consent.statusAllowed')}` : `ℹ ${t('consent.statusDeclined')}`}
        </span>
        <button
          className="btn btn-secondary btn-sm"
          style={{ padding: '2px 8px', fontSize: '0.75rem' }}
          onClick={() => (consentStatus ? onDeclineConsent() : onAcceptConsent())}
        >
          {consentStatus ? t('consent.decline') : t('consent.allow')}
        </button>
      </div>
    );
  }

  return (
    <div
      className="civic-card"
      style={{
        borderLeft: '4px solid var(--color-teal)',
        backgroundColor: '#FCFAF5',
        marginBottom: 'var(--space-xl)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <span style={{ fontSize: '1.25rem' }}>🛡️</span>
        <h3 style={{ margin: 0, fontSize: '1.15rem' }}>{t('consent.title')}</h3>
      </div>

      <p style={{ fontSize: '0.9375rem', marginBottom: '12px', color: 'var(--color-text-main)' }}>
        {t('consent.explanation')}
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          backgroundColor: 'var(--color-surface)',
          padding: '12px',
          border: '1px solid var(--color-border-subtle)',
          borderRadius: 'var(--border-radius)',
          fontSize: '0.8125rem',
          marginBottom: '16px',
        }}
      >
        <div style={{ color: 'var(--color-teal-dark)' }}>
          <strong>{t('consent.whatIsCollected')}</strong>
        </div>
        <div style={{ color: 'var(--color-error)' }}>
          <strong>{t('consent.whatIsNotCollected')}</strong>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
        <button className="btn btn-primary" onClick={onAcceptConsent}>
          {t('consent.allow')}
        </button>
        <button className="btn btn-secondary" onClick={onDeclineConsent}>
          {t('consent.decline')}
        </button>
        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
          {t('consent.privacyGuaranteed')}
        </span>
      </div>
    </div>
  );
}
