import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import { LANGUAGES_METADATA, setAppLanguage } from '../i18n';

export function ProfileModal({
  isOpen,
  onClose,
  currentUser,
  onUserUpdated,
  onOpenRequests,
  onOpenHelp,
  onLogout,
}) {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language;

  const [displayName, setDisplayName] = useState(currentUser?.full_name || '');
  const [selectedLang, setSelectedLang] = useState(currentUser?.preferred_language || currentLang || 'en');
  const [fontScale, setFontScale] = useState(1);
  const [isHighContrast, setIsHighContrast] = useState(false);

  const [loading, setLoading] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (currentUser) {
      setDisplayName(currentUser.full_name || '');
      setSelectedLang(currentUser.preferred_language || currentLang || 'en');
      if (currentUser.accessibility_settings) {
        setFontScale(currentUser.accessibility_settings.fontScale || 1);
        setIsHighContrast(Boolean(currentUser.accessibility_settings.highContrast));
      }
    }
  }, [currentUser, currentLang]);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    setSavedSuccess(false);

    try {
      // 1. Update app language
      if (selectedLang !== currentLang) {
        setAppLanguage(selectedLang);
      }

      // 2. Persist to backend if authenticated
      if (currentUser) {
        const updated = await api.updateProfile({
          full_name: displayName.trim(),
          preferred_language: selectedLang,
          accessibility_settings: {
            fontScale,
            highContrast: isHighContrast,
          },
        });

        // Update local session
        const stored = sessionStorage.getItem('nagrik_user') ? sessionStorage : localStorage;
        stored.setItem('nagrik_user', JSON.stringify(updated));

        if (onUserUpdated) onUserUpdated(updated);
      }

      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update preferences.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(16, 42, 67, 0.75)',
        zIndex: 1100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
        backdropFilter: 'blur(3px)',
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="profile-modal-title"
    >
      <div
        className="civic-card"
        style={{
          width: '100%',
          maxWidth: '560px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#FFFFFF',
          borderRadius: '10px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.25)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '16px 20px',
            backgroundColor: 'var(--color-navy)',
            color: '#FFFFFF',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div className="profile-avatar-circle" style={{ width: '32px', height: '32px', fontSize: '0.9rem' }}>
              {(displayName || currentUser?.identifier || 'C')[0].toUpperCase()}
            </div>
            <div>
              <h2 id="profile-modal-title" style={{ margin: 0, fontSize: '1.15rem', color: '#FFFFFF' }}>
                {t('profile.myProfile', 'Citizen Profile & Preferences')}
              </h2>
              <div style={{ fontSize: '0.75rem', color: '#CBD5E1' }}>
                {currentUser?.email || currentUser?.identifier || 'Anonymous Citizen'}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#FFFFFF',
              fontSize: '1.4rem',
              cursor: 'pointer',
              lineHeight: 1,
            }}
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Quick Shortcut Buttons */}
        <div
          style={{
            padding: '12px 20px',
            backgroundColor: '#F8F9FA',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap',
          }}
        >
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={() => {
              onClose();
              if (onOpenRequests) onOpenRequests();
            }}
          >
            📋 {t('profile.myRequests', 'My Scheme Requests')}
          </button>

          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={() => {
              onClose();
              if (onOpenHelp) onOpenHelp();
            }}
          >
            ❓ {t('profile.myTickets', 'My Support Tickets')}
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSave} style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
          {errorMsg && (
            <div style={{ color: '#991B1B', backgroundColor: '#FEE2E2', border: '1px solid #FCA5A5', padding: '10px 14px', borderRadius: '6px', marginBottom: '14px', fontSize: '0.875rem' }}>
              ⚠️ {errorMsg}
            </div>
          )}

          {savedSuccess && (
            <div style={{ color: '#166534', backgroundColor: '#DCFCE7', border: '1px solid #86EFAC', padding: '10px 14px', borderRadius: '6px', marginBottom: '14px', fontSize: '0.875rem' }}>
              ✓ {t('profile.saved', 'Profile preferences updated successfully.')}
            </div>
          )}

          {/* Display Name */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
              {t('profile.displayName', 'Display Name')}
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Aarav Sharma"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>

          {/* Preferred Language */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
              {t('profile.preferredLanguage', 'Preferred Language (22 Official Languages)')}
            </label>
            <select
              className="form-control"
              value={selectedLang}
              onChange={(e) => setSelectedLang(e.target.value)}
            >
              {LANGUAGES_METADATA.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.nativeName} ({l.englishName}) {l.direction === 'rtl' ? '— RTL' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Accessibility Settings */}
          <div style={{ marginBottom: '18px', padding: '14px', backgroundColor: '#F8F9FA', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
            <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-navy)', marginBottom: '8px' }}>
              ♿ {t('profile.accessibility', 'Accessibility Settings')}
            </div>

            {/* Font Scale */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.8125rem' }}>Text Size Preference:</span>
              <div style={{ display: 'flex', gap: '4px' }}>
                <button
                  type="button"
                  className={`btn btn-sm ${fontScale === 0.875 ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setFontScale(0.875)}
                >
                  Small
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${fontScale === 1 ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setFontScale(1)}
                >
                  Normal
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${fontScale === 1.125 ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setFontScale(1.125)}
                >
                  Large
                </button>
              </div>
            </div>

            {/* High Contrast */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.8125rem' }}>High Contrast Mode:</span>
              <label style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '0.8125rem' }}>
                <input
                  type="checkbox"
                  checked={isHighContrast}
                  onChange={(e) => setIsHighContrast(e.target.checked)}
                />
                Enable High Contrast
              </label>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid var(--color-border)' }}>
            {currentUser && onLogout && (
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  onClose();
                  onLogout();
                }}
                style={{ color: '#991B1B' }}
              >
                🚪 {t('profile.logout', 'Sign Out')}
              </button>
            )}

            <div style={{ display: 'flex', gap: '8px', marginLeft: 'auto' }}>
              <button type="button" className="btn btn-secondary btn-sm" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary btn-sm" disabled={loading}>
                {loading ? 'Saving...' : t('profile.save', 'Save Changes')}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
