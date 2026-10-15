import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES_METADATA } from '../i18n';
import { LanguageSelectorModal } from './LanguageSelectorModal';
import { useAccessibility } from '../context/AccessibilityContext';

/**
 * NagrikSaarathi — Shared Navigation Bar
 *
 * Renders role-specific navigation menus while keeping the identical
 * visual design (gov-access-strip + civic-header) across all three workspaces.
 *
 * Roles:
 *  citizen  → Explore Schemes, Guided Form, My Requests, Help & Support
 *  official → Department Schemes, Scheme Proposals, Review Feedback, Profile
 *  admin    → Scheme Catalogue, Review Proposals, Scheme Requests,
 *              Department Mgmt, User Management, Help Desk, Audit Logs
 *
 * Menu items only appear when the corresponding page actually exists.
 * Dead links are never shown.
 */
export function Navbar({
  activePage,
  setActivePage,
  currentUser,
  onLogout,
  onOpenProfile,
  onOpenRequests,
  onOpenHelp,
}) {
  const { t, i18n } = useTranslation();
  const { fontScale, isHighContrast, setFontScale, toggleHighContrast } = useAccessibility();
  const [isLangModalOpen, setIsLangModalOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef(null);

  const currentMeta = LANGUAGES_METADATA.find(l => l.code === i18n.language) || LANGUAGES_METADATA[0];

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
        setIsProfileMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getInitials = () => {
    if (currentUser?.full_name) {
      const parts = currentUser.full_name.trim().split(/\s+/);
      if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
      return parts[0][0].toUpperCase();
    }
    if (currentUser?.identifier) return currentUser.identifier[0].toUpperCase();
    return 'U';
  };

  const getDisplayName = () => {
    if (currentUser?.full_name) return currentUser.full_name;
    if (currentUser?.identifier) return currentUser.identifier.split('@')[0];
    return t('profile.guest', 'User');
  };

  const getRoleBadge = () => {
    switch (currentUser?.role) {
      case 'admin':    return '🛡️ Administrator';
      case 'official': return '🏢 Dept. Official';
      default:         return '👤 Citizen';
    }
  };

  /* ── Nav items by role ──────────────────────────────────────────────────── */

  // CITIZEN workspace navigation
  const citizenNav = [
    { key: 'home',    label: t('app.home', 'Home') },
    { key: 'schemes', label: `🏛️ ${t('app.schemes', 'Explore Schemes')}` },
    { key: 'form',    label: `✍️ ${t('app.guidedForm', 'Apply')}` },
  ];

  // DEPARTMENT OFFICIAL workspace navigation
  const officialNav = [
    { key: 'official', label: '📊 Dashboard' },
    { key: 'schemes',  label: '🏛️ Scheme Catalogue', title: 'Browse the public scheme catalogue' },
  ];

  // PRINCIPAL ADMINISTRATOR workspace navigation
  const adminNav = [
    { key: 'dashboard', label: '📊 Admin Dashboard' },
    { key: 'schemes',   label: '🏛️ Scheme Catalogue' },
  ];

  const getNavItems = () => {
    if (!currentUser) return citizenNav;
    switch (currentUser.role) {
      case 'admin':    return adminNav;
      case 'official': return officialNav;
      default:         return citizenNav;
    }
  };

  const navItems = getNavItems();

  return (
    <>
      {/* ── Global Accessibility Strip ──────────────────────────────────── */}
      <div className="gov-access-strip" role="region" aria-label="Accessibility Controls">
        <div
          className="gov-access-inner"
          style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.7rem', opacity: 0.9 }}>
            <span className="badge-civic-service" style={{ fontSize: '0.65rem' }}>नागरिक सेवा</span>
            <span>{t('app.disclaimer')}</span>
          </div>
          <div className="gov-access-tools">
            {/* Text Resizing Controls */}
            <div className="gov-text-resizer" aria-label={t('login.accessibilityStrip.textSize', 'Text Size')}>
              <span className="gov-tool-label" style={{ color: 'inherit' }}>
                {t('login.accessibilityStrip.textSize', 'Text Size')}:
              </span>
              {[
                { scale: 0.875, label: 'A-' },
                { scale: 1,     label: 'A'  },
                { scale: 1.125, label: 'A+' },
              ].map(({ scale, label }) => (
                <button
                  key={scale}
                  type="button"
                  className={`gov-resizer-btn ${fontScale === scale ? 'active' : ''}`}
                  onClick={() => setFontScale(scale)}
                  title={`${label} text size`}
                  aria-pressed={fontScale === scale}
                >
                  {label}
                </button>
              ))}
            </div>
            <div className="gov-divider" aria-hidden="true" />
            {/* High Contrast Toggle */}
            <button
              type="button"
              className={`gov-contrast-btn ${isHighContrast ? 'active' : ''}`}
              onClick={toggleHighContrast}
              aria-pressed={isHighContrast}
              title={isHighContrast
                ? t('login.accessibilityStrip.normalContrast', 'Normal Contrast')
                : t('login.accessibilityStrip.highContrast', 'High Contrast')}
            >
              <span aria-hidden="true">◐</span>
              <span>{isHighContrast
                ? t('login.accessibilityStrip.normalContrast', 'Normal')
                : t('login.accessibilityStrip.highContrast', 'High Contrast')}
              </span>
            </button>
            <div className="gov-divider" aria-hidden="true" />
            <span style={{ fontSize: '0.7rem', opacity: 0.8 }}>22 भाषीय समर्थन</span>
          </div>
        </div>
      </div>

      {/* ── Main Civic Header ───────────────────────────────────────────── */}
      <header className="civic-header">
        <div className="civic-container civic-header-inner">
          {/* Brand */}
          <a
            href="#home"
            className="civic-brand"
            onClick={e => {
              e.preventDefault();
              // Navigate to role-appropriate home
              if (currentUser?.role === 'admin')    setActivePage('dashboard');
              else if (currentUser?.role === 'official') setActivePage('official');
              else setActivePage('home');
            }}
          >
            <span className="wordmark-en">NagrikSaarathi</span>
            <span className="wordmark-hi">नागरिक सारथी</span>
          </a>

          {/* Role-specific workspace label */}
          {currentUser && (
            <div style={{
              padding: '3px 10px',
              borderRadius: 'var(--border-radius)',
              background: currentUser.role === 'admin'    ? 'var(--color-navy)'
                         : currentUser.role === 'official' ? 'var(--color-teal)'
                         : 'var(--color-ivory-dark)',
              color: currentUser.role === 'citizen' ? 'var(--color-navy)' : '#fff',
              fontSize: '0.7rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              whiteSpace: 'nowrap',
            }}>
              {currentUser.role === 'admin' ? '🛡️ Admin Portal'
               : currentUser.role === 'official' ? '🏢 Official Portal'
               : '👤 Citizen Portal'}
            </div>
          )}

          <nav className="civic-nav-actions" aria-label="Main Navigation">
            {/* Role-specific navigation items */}
            {navItems.map(item => (
              <button
                key={item.key}
                className={`btn btn-sm ${activePage === item.key ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActivePage(item.key)}
                title={item.title}
              >
                {item.label}
              </button>
            ))}

            {/* Citizen-only: Help button */}
            {(!currentUser || currentUser.role === 'citizen') && (
              <button
                type="button"
                className="btn btn-sm btn-secondary"
                onClick={() => onOpenHelp && onOpenHelp()}
                title="Get help with forms, translations, or technical issues"
              >
                ❓ {t('help.needHelp', 'Help')}
              </button>
            )}

            {/* Admin-only: direct links to admin panels within DashboardPage */}
            {currentUser?.role === 'admin' && (
              <>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  onClick={() => onOpenHelp && onOpenHelp()}
                  title="Help Desk"
                >
                  🎫 Help Desk
                </button>
              </>
            )}

            {/* Language Switcher — all roles */}
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => setIsLangModalOpen(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', borderColor: 'var(--color-teal)' }}
              title={t('app.changeLanguage')}
            >
              <span aria-hidden="true">🌐</span>
              <span style={{ fontWeight: 700, color: 'var(--color-navy)' }}>{currentMeta.nativeName}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>({currentMeta.code.toUpperCase()})</span>
            </button>

            {/* User Profile Menu or Login button */}
            {currentUser ? (
              <div style={{ position: 'relative' }} ref={profileMenuRef}>
                <button
                  type="button"
                  className="profile-bar-btn"
                  onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                  aria-expanded={isProfileMenuOpen}
                  aria-haspopup="true"
                  aria-label="User Profile Menu"
                >
                  <div className="profile-avatar-circle">{getInitials()}</div>
                  <span style={{ maxWidth: '110px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {getDisplayName()}
                  </span>
                  <span style={{ fontSize: '0.7rem' }}>▼</span>
                </button>

                {isProfileMenuOpen && (
                  <div className="profile-dropdown-menu" role="menu">
                    <div className="profile-dropdown-header">
                      <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{getDisplayName()}</div>
                      <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{currentUser.email || currentUser.identifier}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-saffron)', marginTop: '2px' }}>
                        {getRoleBadge()}
                      </div>
                      {currentUser.department && (
                        <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                          {currentUser.department}
                        </div>
                      )}
                    </div>

                    <div style={{ padding: '4px 0' }}>
                      {/* Profile — all roles */}
                      <button
                        type="button"
                        className="profile-dropdown-item"
                        onClick={() => { setIsProfileMenuOpen(false); if (onOpenProfile) onOpenProfile(); }}
                        role="menuitem"
                      >
                        <span>👤</span>
                        <span>{t('profile.myProfile', 'My Profile & Preferences')}</span>
                      </button>

                      {/* Citizen-only items */}
                      {currentUser.role === 'citizen' && (
                        <>
                          <button
                            type="button"
                            className="profile-dropdown-item"
                            onClick={() => { setIsProfileMenuOpen(false); if (onOpenRequests) onOpenRequests(); }}
                            role="menuitem"
                          >
                            <span>📋</span>
                            <span>{t('profile.myRequests', 'My Scheme Requests')}</span>
                          </button>
                          <button
                            type="button"
                            className="profile-dropdown-item"
                            onClick={() => { setIsProfileMenuOpen(false); setActivePage('form'); }}
                            role="menuitem"
                          >
                            <span>📁</span>
                            <span>{t('profile.myPassport', 'Saved Application Progress')}</span>
                          </button>
                          <button
                            type="button"
                            className="profile-dropdown-item"
                            onClick={() => { setIsProfileMenuOpen(false); if (onOpenHelp) onOpenHelp(); }}
                            role="menuitem"
                          >
                            <span>🎫</span>
                            <span>{t('profile.myTickets', 'My Support Tickets')}</span>
                          </button>
                        </>
                      )}

                      {/* Official-only items */}
                      {currentUser.role === 'official' && (
                        <>
                          <button
                            type="button"
                            className="profile-dropdown-item"
                            onClick={() => { setIsProfileMenuOpen(false); setActivePage('official'); }}
                            role="menuitem"
                          >
                            <span>📊</span>
                            <span>My Department Dashboard</span>
                          </button>
                        </>
                      )}

                      {/* Language preferences — all roles */}
                      <button
                        type="button"
                        className="profile-dropdown-item"
                        onClick={() => { setIsProfileMenuOpen(false); setIsLangModalOpen(true); }}
                        role="menuitem"
                      >
                        <span>🌐</span>
                        <span>{t('profile.preferences', 'Language Preferences')}</span>
                      </button>

                      <div style={{ borderTop: '1px solid var(--color-border-subtle)', margin: '4px 0' }} />

                      <button
                        type="button"
                        className="profile-dropdown-item"
                        onClick={() => { setIsProfileMenuOpen(false); onLogout(); }}
                        style={{ color: '#BA2525' }}
                        role="menuitem"
                      >
                        <span>🚪</span>
                        <span>{t('profile.logout', 'Sign Out')}</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button
                type="button"
                className={`btn btn-sm ${activePage === 'login' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActivePage('login')}
                style={{ fontWeight: 700 }}
              >
                {t('app.login', 'Login')}
              </button>
            )}
          </nav>
        </div>
      </header>

      {/* Language Selector Modal */}
      <LanguageSelectorModal
        isOpen={isLangModalOpen}
        onClose={() => setIsLangModalOpen(false)}
      />
    </>
  );
}
