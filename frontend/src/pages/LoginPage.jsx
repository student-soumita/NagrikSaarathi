import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import { LanguageSelectorModal } from '../components/LanguageSelectorModal';
import { LANGUAGES_METADATA } from '../i18n';
import { useAccessibility } from '../context/AccessibilityContext';

export function LoginPage({ onLoginSuccess, onNavigateDashboard, onNavigateForm, onNavigateHome }) {
  const { t, i18n } = useTranslation();
  const [formMode, setFormMode] = useState('login'); // 'login' | 'register' | 'portal'
  const [portalRole, setPortalRole] = useState('official'); // 'official' | 'admin'
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isLangModalOpen, setIsLangModalOpen] = useState(false);
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);

  // Portal identifiers (separate state for portal login)
  const [portalIdentifier, setPortalIdentifier] = useState('');
  const [portalPassword, setPortalPassword] = useState('');
  const [showPortalPassword, setShowPortalPassword] = useState(false);

  // Register form state (Strictly Citizen Self-Registration)
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regMobile, setRegMobile] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [showRegPassword, setShowRegPassword] = useState(false);

  // Standard Citizen Password Reset Modal state (No role escalation)
  const [showResetModal, setShowResetModal] = useState(false);
  const [resetIdentifier, setResetIdentifier] = useState('');
  const [resetNewPassword, setResetNewPassword] = useState('');
  const [resetLoading, setResetLoading] = useState(false);
  const [resetFeedback, setResetFeedback] = useState(null);

  // Controlled Official Onboarding / Invitation Token Activation Modal
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteToken, setInviteToken] = useState('GOV-INV-DEMO-SAMPLE-TOKEN-2026');
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteDetails, setInviteDetails] = useState(null);
  const [invitePassword, setInvitePassword] = useState('');
  const [inviteConfirmPassword, setInviteConfirmPassword] = useState('');
  const [inviteFeedback, setInviteFeedback] = useState(null);

  // Government SSO Integration Status Modal
  const [showSSOModal, setShowSSOModal] = useState(false);
  const [ssoConfig, setSSOConfig] = useState(null);
  const [ssoLoading, setSSOLoading] = useState(false);

  // Accessibility Controls — from global context so settings persist across pages
  const { fontScale, setFontScale, isHighContrast, toggleHighContrast } = useAccessibility();

  const currentMeta = LANGUAGES_METADATA.find((l) => l.code === i18n.language) || LANGUAGES_METADATA[0];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!identifier.trim() || !password) {
      setErrorMessage(t('login.errorGeneric'));
      return;
    }

    setIsLoading(true);

    try {
      const response = await api.login({
        identifier: identifier.trim(),
        password,
        role: 'citizen',
      });

      // Persist session
      const storage = rememberMe ? localStorage : sessionStorage;
      storage.setItem('nagrik_token', response.access_token);
      storage.setItem('nagrik_user', JSON.stringify(response.user));

      setSuccessMessage(t('login.loginSuccess'));

      if (onLoginSuccess) {
        onLoginSuccess(response.user, response.access_token);
      }
    } catch (err) {
      if (err.status === 429) {
        setErrorMessage(t('login.errorRateLimit'));
      } else {
        setErrorMessage(err.message || t('login.errorGeneric'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handlePortalLogin = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!portalIdentifier.trim() || !portalPassword) {
      setErrorMessage('Please enter your official email/identifier and password.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.login({
        identifier: portalIdentifier.trim(),
        password: portalPassword,
        role: portalRole,
      });

      const storage = rememberMe ? localStorage : sessionStorage;
      storage.setItem('nagrik_token', response.access_token);
      storage.setItem('nagrik_user', JSON.stringify(response.user));

      setSuccessMessage(`Welcome, ${response.user.full_name || response.user.identifier}`);

      if (onLoginSuccess) {
        onLoginSuccess(response.user, response.access_token);
      }
    } catch (err) {
      if (err.status === 429) {
        setErrorMessage('Too many attempts. Please wait before trying again.');
      } else if (err.status === 403) {
        setErrorMessage('Account deactivated or not yet verified by Administrator.');
      } else {
        setErrorMessage(err.message || 'Invalid credentials. Official accounts require authorized onboarding.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!regFullName.trim()) {
      setErrorMessage('Please enter your full name.');
      return;
    }
    if (!regEmail.trim() && !regMobile.trim()) {
      setErrorMessage('Please provide at least an email address or mobile number.');
      return;
    }
    if (regPassword.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }
    if (regPassword !== regConfirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter.');
      return;
    }

    setIsLoading(true);
    try {
      // Strictly register as citizen - no roles or elevated privileges allowed publicly
      const response = await api.register({
        full_name: regFullName.trim(),
        email: regEmail.trim() || undefined,
        mobile: regMobile.trim() || undefined,
        password: regPassword,
      });

      sessionStorage.setItem('nagrik_token', response.access_token);
      sessionStorage.setItem('nagrik_user', JSON.stringify(response.user));

      setSuccessMessage(response.message || 'Citizen account registered successfully! Welcome to NagrikSaarathi.');

      if (onLoginSuccess) {
        onLoginSuccess(response.user, response.access_token);
      }
    } catch (err) {
      if (err.status === 409) {
        setErrorMessage('An account with this email or mobile already exists. Please log in or reset your password.');
      } else {
        setErrorMessage(err.message || 'Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomReset = async (e) => {
    e.preventDefault();
    if (!resetIdentifier.trim()) {
      setResetFeedback({ type: 'error', text: 'Please enter your account email, username, or mobile number.' });
      return;
    }
    if (resetNewPassword.length < 8) {
      setResetFeedback({ type: 'error', text: 'New password must be at least 8 characters long.' });
      return;
    }

    setResetLoading(true);
    setResetFeedback(null);
    try {
      const res = await api.resetPassword({
        identifier: resetIdentifier.trim(),
        new_password: resetNewPassword,
      });

      setResetFeedback({
        type: 'success',
        text: res.message || 'Password updated successfully. You can now log in.',
      });

      setTimeout(() => {
        setShowResetModal(false);
        setResetFeedback(null);
        setResetNewPassword('');
        setIdentifier(resetIdentifier.trim());
        setPortalIdentifier(resetIdentifier.trim());
      }, 1500);
    } catch (err) {
      setResetFeedback({ type: 'error', text: err.message || 'Failed to update credentials. Please check details.' });
    } finally {
      setResetLoading(false);
    }
  };

  const handleVerifyInviteToken = async () => {
    if (!inviteToken.trim()) {
      setInviteFeedback({ type: 'error', text: 'Please enter an invitation token.' });
      return;
    }
    setInviteLoading(true);
    setInviteFeedback(null);
    try {
      const details = await api.getInvitationDetails(inviteToken.trim());
      setInviteDetails(details);
      setInviteFeedback({ type: 'success', text: `Valid Invitation: Assigned to ${details.department_name}` });
    } catch (err) {
      setInviteDetails(null);
      setInviteFeedback({ type: 'error', text: err.message || 'Invalid or expired invitation token.' });
    } finally {
      setInviteLoading(false);
    }
  };

  const handleActivateInviteAccount = async (e) => {
    e.preventDefault();
    if (!inviteDetails) return;
    if (invitePassword.length < 8) {
      setInviteFeedback({ type: 'error', text: 'Password must be at least 8 characters long.' });
      return;
    }
    if (invitePassword !== inviteConfirmPassword) {
      setInviteFeedback({ type: 'error', text: 'Passwords do not match.' });
      return;
    }

    setInviteLoading(true);
    setInviteFeedback(null);
    try {
      const res = await api.activateInvitation({
        token: inviteDetails.invitation_token,
        password: invitePassword,
      });
      setInviteFeedback({
        type: 'success',
        text: res.message || 'Official account activated successfully! You may now sign in.',
      });
      setTimeout(() => {
        setShowInviteModal(false);
        setFormMode('portal');
        setPortalRole('official');
        setPortalIdentifier(inviteDetails.email);
        setInviteFeedback(null);
        setInviteDetails(null);
      }, 2000);
    } catch (err) {
      setInviteFeedback({ type: 'error', text: err.message || 'Activation failed.' });
    } finally {
      setInviteLoading(false);
    }
  };

  const handleOpenGovSSO = async () => {
    setShowSSOModal(true);
    setSSOLoading(true);
    try {
      const cfg = await api.getGovSSOConfig();
      setSSOConfig(cfg);
    } catch (err) {
      setSSOConfig({
        provider: 'Parichay (e-Pramaan OIDC)',
        is_configured: false,
        error: err.message,
      });
    } finally {
      setSSOLoading(false);
    }
  };

  return (
    <div
      className={`gov-portal-root ${isHighContrast ? 'gov-high-contrast' : ''}`}
      style={{
        fontSize: `${fontScale * 16}px`,
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* ── 1. Top Government Accessibility Strip ─────────────────────── */}
      <div className="gov-access-strip" role="region" aria-label="Accessibility Controls">
        <div className="gov-access-inner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: '#CBD5E1' }}>
            <span style={{ backgroundColor: 'var(--gov-saffron, #E89B31)', color: '#000', padding: '1px 6px', borderRadius: '2px', fontWeight: 700, fontSize: '0.6875rem' }}>नागरिक सेवा</span>
            <span>Digital Citizen Service Assistance • 22 Official Languages</span>
          </div>

          <div className="gov-access-tools">
            {/* Text Resizing Controls */}
            <div className="gov-text-resizer" aria-label={t('login.accessibilityStrip.textSize')}>
              <span className="gov-tool-label">{t('login.accessibilityStrip.textSize')}:</span>
              <button
                type="button"
                className={`gov-resizer-btn ${fontScale === 0.875 ? 'active' : ''}`}
                onClick={() => setFontScale(0.875)}
                title="A- Decrease text size"
                aria-pressed={fontScale === 0.875}
              >
                A-
              </button>
              <button
                type="button"
                className={`gov-resizer-btn ${fontScale === 1 ? 'active' : ''}`}
                onClick={() => setFontScale(1)}
                title="A Default text size"
                aria-pressed={fontScale === 1}
              >
                A
              </button>
              <button
                type="button"
                className={`gov-resizer-btn ${fontScale === 1.125 ? 'active' : ''}`}
                onClick={() => setFontScale(1.125)}
                title="A+ Increase text size"
                aria-pressed={fontScale === 1.125}
              >
                A+
              </button>
            </div>

            <div className="gov-divider" aria-hidden="true" />

            {/* High Contrast Toggle */}
            <button
              type="button"
              className={`gov-contrast-btn ${isHighContrast ? 'active' : ''}`}
              onClick={toggleHighContrast}
              aria-pressed={isHighContrast}
              title={isHighContrast ? t('login.accessibilityStrip.normalContrast') : t('login.accessibilityStrip.highContrast')}
            >
              <span aria-hidden="true">◐</span>
              <span>{isHighContrast ? t('login.accessibilityStrip.normalContrast') : t('login.accessibilityStrip.highContrast')}</span>
            </button>

            <div className="gov-divider" aria-hidden="true" />

            {/* Language Switcher */}
            <button
              type="button"
              className="gov-lang-btn"
              onClick={() => setIsLangModalOpen(true)}
              aria-label={t('app.changeLanguage')}
            >
              <span aria-hidden="true">🌐</span>
              <span className="gov-lang-name">{currentMeta.nativeName}</span>
              <span className="gov-lang-code">[{currentMeta.code.toUpperCase()}]</span>
            </button>
          </div>
        </div>
      </div>

      {/* ── 2. Formal Institutional Portal Header ──────────────────────── */}
      <header className="gov-header" role="banner">
        <div className="gov-header-inner">
          <div className="gov-header-brand">
            {/* Dignified Civic Emblem SVG (Clean Geometric Seal, NOT fake national emblem) */}
            <svg
              className="gov-emblem"
              viewBox="0 0 48 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <circle cx="24" cy="24" r="22" stroke="var(--gov-navy, #12345A)" strokeWidth="2.5" fill="#FFFFFF" />
              <circle cx="24" cy="24" r="18" stroke="var(--gov-saffron, #E89B31)" strokeWidth="1.5" strokeDasharray="2 3" />
              {/* Central Pillar & Dharma Star Geometry */}
              <path
                d="M24 10 L26 18 L34 20 L27 25 L29 34 L24 28 L19 34 L21 25 L14 20 L22 18 Z"
                fill="var(--gov-navy, #12345A)"
              />
              <circle cx="24" cy="24" r="4" fill="var(--gov-saffron, #E89B31)" />
              <rect x="20" y="35" width="8" height="2" fill="var(--gov-green, #24734A)" />
            </svg>

            <div className="gov-brand-titles">
              <div className="gov-title-row">
                <h1 className="gov-title-hi">नागरिक सारथी</h1>
                <span className="gov-title-en">NagrikSaarathi</span>
              </div>
              <div className="gov-subtitle">
                {t('login.portalSubtitle')} • Digital Public Infrastructure
              </div>
            </div>
          </div>

          <div className="gov-header-actions" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {onNavigateHome && (
              <button
                type="button"
                className="gov-btn-text"
                onClick={onNavigateHome}
                style={{ fontWeight: 600, color: 'var(--gov-navy, #12345A)', cursor: 'pointer' }}
              >
                ← {t('app.home') || 'होम (Home)'}
              </button>
            )}
            <button
              type="button"
              className="gov-btn-text"
              onClick={() => setIsHelpModalOpen(true)}
            >
              <span aria-hidden="true">ⓘ</span> {t('login.helpDesk')}
            </button>
          </div>
        </div>
      </header>

      {/* ── 3. Main Login Content (Two-Column Civic Layout) ───────────── */}
      <main className="gov-main" id="login-main-form">
        <div className="gov-main-container">
          <div className="gov-grid">
            {/* Left Column: Context, Benefits & Dignified Illustration */}
            <div className="gov-left-col">
              <div className="gov-eyebrow-badge">
                <span className="gov-badge-dot" />
                <span>{t('login.eyebrow')}</span>
              </div>

              <h2 className="gov-hero-heading">{t('login.heading')}</h2>
              <p className="gov-hero-subheading">{t('login.subheading')}</p>

              {/* 3 Key Benefits */}
              <div className="gov-benefits-list">
                <div className="gov-benefit-card">
                  <div className="gov-benefit-icon-wrapper saffron">
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="2" y1="12" x2="22" y2="12" />
                      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="gov-benefit-title">{t('login.benefits.benefit1Title')}</h3>
                    <p className="gov-benefit-desc">{t('login.benefits.benefit1Desc')}</p>
                  </div>
                </div>

                <div className="gov-benefit-card">
                  <div className="gov-benefit-icon-wrapper green">
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                      <polyline points="9 12 11 14 15 10" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="gov-benefit-title">{t('login.benefits.benefit2Title')}</h3>
                    <p className="gov-benefit-desc">{t('login.benefits.benefit2Desc')}</p>
                  </div>
                </div>

                <div className="gov-benefit-card">
                  <div className="gov-benefit-icon-wrapper navy">
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                      <line x1="12" y1="17" x2="12.01" y2="17" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="gov-benefit-title">{t('login.benefits.benefit3Title')}</h3>
                    <p className="gov-benefit-desc">{t('login.benefits.benefit3Desc')}</p>
                  </div>
                </div>
              </div>

              {/* Dignified Institutional Civic Vector */}
              <div className="gov-civic-illustration-card" aria-hidden="true">
                <svg viewBox="0 0 380 90" width="100%" height="90" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="10" y="10" width="360" height="70" rx="4" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1.5" />
                  {/* Digital Document lines */}
                  <rect x="30" y="25" width="28" height="38" rx="2" fill="#FFFFFF" stroke="#94A3B8" strokeWidth="1.5" />
                  <line x1="36" y1="34" x2="50" y2="34" stroke="#0F766E" strokeWidth="2" strokeLinecap="round" />
                  <line x1="36" y1="41" x2="48" y2="41" stroke="#94A3B8" strokeWidth="1.5" strokeLinecap="round" />
                  <line x1="36" y1="48" x2="44" y2="48" stroke="#94A3B8" strokeWidth="1.5" strokeLinecap="round" />

                  {/* Flow Arrow */}
                  <path d="M72 44 L92 44 M88 40 L92 44 L88 48" stroke="#12345A" strokeWidth="1.5" strokeLinecap="round" />

                  {/* Multilingual Translation Bridge */}
                  <circle cx="120" cy="44" r="18" fill="#F1F5F9" stroke="#E89B31" strokeWidth="1.5" />
                  <text x="114" y="48" fill="#12345A" fontSize="12" fontWeight="700">अ</text>
                  <text x="123" y="44" fill="#0F766E" fontSize="9" fontWeight="600">A</text>

                  {/* Flow Arrow */}
                  <path d="M148 44 L168 44 M164 40 L168 44 L164 48" stroke="#12345A" strokeWidth="1.5" strokeLinecap="round" />

                  {/* Verified Public Service Shield */}
                  <rect x="180" y="22" width="170" height="44" rx="3" fill="#FFFFFF" stroke="#CBD5E1" strokeWidth="1" />
                  <circle cx="198" cy="44" r="10" fill="#E6FFFA" stroke="#24734A" strokeWidth="1.5" />
                  <path d="M194 44 L197 47 L202 41" stroke="#24734A" strokeWidth="1.8" strokeLinecap="round" />
                  <text x="216" y="38" fill="#12345A" fontSize="11" fontWeight="700">सुरक्षित नागरिक प्रमाणीकरण</text>
                  <text x="216" y="52" fill="#64748B" fontSize="9">शून्य डेटा संग्रह • पूर्ण गोपनीयता</text>
                </svg>
              </div>
            </div>

            {/* Right Column: Formal Government Login Card */}
            <div className="gov-right-col">
              <div className="gov-login-panel">
                <div className="gov-panel-header">
                  <div className="gov-panel-emblem-small">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="gov-panel-title">{t('login.panelTitle')}</h2>
                    <p className="gov-panel-subtitle">{t('login.panelSubtitle')}</p>
                  </div>
                </div>

                {/* Mode Tabs */}
                <div className="gov-tabs" role="tablist" aria-label="Portal Access">
                  <button
                    type="button"
                    role="tab"
                    id="signin-tab"
                    aria-selected={formMode === 'login'}
                    aria-controls="login-form-content"
                    className={`gov-tab-btn ${formMode === 'login' ? 'active' : ''}`}
                    onClick={() => {
                      setFormMode('login');
                      setErrorMessage('');
                      setSuccessMessage('');
                    }}
                  >
                    <span className="gov-tab-icon" aria-hidden="true">👤</span>
                    <span>Citizen Login</span>
                  </button>

                  <button
                    type="button"
                    role="tab"
                    id="register-tab"
                    aria-selected={formMode === 'register'}
                    aria-controls="register-form-content"
                    className={`gov-tab-btn ${formMode === 'register' ? 'active' : ''}`}
                    onClick={() => {
                      setFormMode('register');
                      setErrorMessage('');
                      setSuccessMessage('');
                    }}
                  >
                    <span className="gov-tab-icon" aria-hidden="true">✚</span>
                    <span>Create Account</span>
                  </button>

                  <button
                    type="button"
                    role="tab"
                    id="portal-tab"
                    aria-selected={formMode === 'portal'}
                    aria-controls="portal-form-content"
                    className={`gov-tab-btn ${formMode === 'portal' ? 'active' : ''}`}
                    style={{
                      borderColor: formMode === 'portal' ? '#E89B31' : undefined,
                      color: formMode === 'portal' ? '#7A4A10' : undefined,
                    }}
                    onClick={() => {
                      setFormMode('portal');
                      setErrorMessage('');
                      setSuccessMessage('');
                    }}
                  >
                    <span className="gov-tab-icon" aria-hidden="true">🏛️</span>
                    <span>Dept. Portal</span>
                  </button>
                </div>

                {/* Error Banner */}
                {errorMessage && (
                  <div className="gov-alert-error" role="alert" aria-live="assertive">
                    <span className="gov-alert-icon">✕</span>
                    <span>{errorMessage}</span>
                  </div>
                )}

                {/* Success Banner */}
                {successMessage && (
                  <div className="gov-alert-success" role="status" aria-live="polite">
                    <span className="gov-alert-icon">✓</span>
                    <span>{successMessage}</span>
                  </div>
                )}

                {/* ── LOGIN FORM ── */}
                {formMode === 'login' && (
                <form id="login-form-content" onSubmit={handleSubmit} noValidate>
                  {/* Identifier Input */}
                  <div className="gov-form-group">
                    <label htmlFor="gov-identifier" className="gov-form-label">
                      {t('login.citizenIdLabel')}
                      <span className="gov-required" aria-hidden="true">*</span>
                    </label>
                    <input
                      id="gov-identifier"
                      name="identifier"
                      type="text"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      placeholder={t('login.citizenIdPlaceholder')}
                      className="gov-input"
                      required
                      autoComplete="username tel email"
                    />
                  </div>

                  {/* Password Input */}
                  <div className="gov-form-group">
                    <div className="gov-label-row">
                      <label htmlFor="gov-password" className="gov-form-label">
                        {t('login.passwordLabel')}
                        <span className="gov-required" aria-hidden="true">*</span>
                      </label>
                      <button
                        type="button"
                        className="gov-link-subtle"
                        onClick={() => {
                          setResetIdentifier(identifier);
                          setShowResetModal(true);
                        }}
                      >
                        {t('login.forgotPassword')}
                      </button>
                    </div>

                    <div className="gov-input-wrapper">
                      <input
                        id="gov-password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder={t('login.passwordPlaceholder')}
                        className="gov-input gov-input-with-button"
                        required
                        autoComplete="current-password"
                      />
                      <button
                        type="button"
                        className="gov-password-toggle-btn"
                        onClick={() => setShowPassword(!showPassword)}
                        title={showPassword ? t('login.hidePassword') : t('login.showPassword')}
                        aria-label={showPassword ? t('login.hidePassword') : t('login.showPassword')}
                      >
                        {showPassword ? '👁️' : '👁️‍🗨️'}
                      </button>
                    </div>
                  </div>

                  {/* Remember Me Checkbox */}
                  <div className="gov-form-options">
                    <label className="gov-checkbox-label">
                      <input
                        type="checkbox"
                        checked={rememberMe}
                        onChange={(e) => setRememberMe(e.target.checked)}
                        className="gov-checkbox"
                      />
                      <span>{t('login.rememberMe')}</span>
                    </label>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    className="gov-submit-btn"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="gov-btn-loading">
                        <span className="gov-spinner" />
                        <span>{t('login.signingIn')}</span>
                      </span>
                    ) : (
                      <span>{t('login.signInCitizen')}</span>
                    )}
                  </button>

                  {/* Create Account Prompt */}
                  <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.875rem', color: '#64748B' }}>
                    Don't have an account?{' '}
                    <button
                      type="button"
                      className="gov-link-subtle"
                      style={{ fontWeight: 600, color: 'var(--gov-green, #24734A)' }}
                      onClick={() => { setFormMode('register'); setErrorMessage(''); setSuccessMessage(''); }}
                    >
                      Create one for free
                    </button>
                  </div>
                </form>
                )}

                {/* ── REGISTER FORM (Strictly Citizen Registration) ── */}
                {formMode === 'register' && (
                <form id="register-form-content" onSubmit={handleRegister} noValidate>
                  <div style={{
                    marginBottom: '18px',
                    backgroundColor: '#EFF6FF',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    border: '1px solid #BFDBFE',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px'
                  }}>
                    <span style={{ fontSize: '1.25rem' }}>🛡️</span>
                    <div>
                      <div style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--color-navy)' }}>
                        Citizen Public Registration Only
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '2px', lineHeight: 1.4 }}>
                        Public sign-up is strictly restricted to Citizens seeking scheme guidance. Government Department Officials must be invited and verified by a Principal Administrator.
                      </div>
                    </div>
                  </div>

                  {/* Full Name */}
                  <div className="gov-form-group">
                    <label htmlFor="reg-fullname" className="gov-form-label">
                      Full Name <span className="gov-required" aria-hidden="true">*</span>
                    </label>
                    <input
                      id="reg-fullname"
                      type="text"
                      value={regFullName}
                      onChange={(e) => setRegFullName(e.target.value)}
                      placeholder="Enter your full name"
                      className="gov-input"
                      required
                      autoComplete="name"
                    />
                  </div>

                  {/* Email */}
                  <div className="gov-form-group">
                    <label htmlFor="reg-email" className="gov-form-label">
                      Email Address
                    </label>
                    <input
                      id="reg-email"
                      type="email"
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="gov-input"
                      autoComplete="email"
                    />
                  </div>

                  {/* Mobile */}
                  <div className="gov-form-group">
                    <label htmlFor="reg-mobile" className="gov-form-label">
                      Mobile Number
                    </label>
                    <input
                      id="reg-mobile"
                      type="tel"
                      value={regMobile}
                      onChange={(e) => setRegMobile(e.target.value)}
                      placeholder="10-digit mobile number"
                      className="gov-input"
                      maxLength={10}
                      autoComplete="tel"
                    />
                    <p style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px', marginBottom: 0 }}>
                      Provide at least one — email or mobile
                    </p>
                  </div>

                  {/* Password */}
                  <div className="gov-form-group">
                    <label htmlFor="reg-password" className="gov-form-label">
                      Password <span className="gov-required" aria-hidden="true">*</span>
                    </label>
                    <div className="gov-input-wrapper">
                      <input
                        id="reg-password"
                        type={showRegPassword ? 'text' : 'password'}
                        value={regPassword}
                        onChange={(e) => setRegPassword(e.target.value)}
                        placeholder="Min. 8 characters"
                        className="gov-input gov-input-with-button"
                        required
                        autoComplete="new-password"
                      />
                      <button
                        type="button"
                        className="gov-password-toggle-btn"
                        onClick={() => setShowRegPassword(!showRegPassword)}
                        aria-label={showRegPassword ? 'Hide password' : 'Show password'}
                      >
                        {showRegPassword ? '👁️' : '👁️‍🗨️'}
                      </button>
                    </div>
                  </div>

                  {/* Confirm Password */}
                  <div className="gov-form-group">
                    <label htmlFor="reg-confirm-password" className="gov-form-label">
                      Confirm Password <span className="gov-required" aria-hidden="true">*</span>
                    </label>
                    <input
                      id="reg-confirm-password"
                      type={showRegPassword ? 'text' : 'password'}
                      value={regConfirmPassword}
                      onChange={(e) => setRegConfirmPassword(e.target.value)}
                      placeholder="Re-enter your password"
                      className="gov-input"
                      required
                      autoComplete="new-password"
                    />
                    {regConfirmPassword && regPassword !== regConfirmPassword && (
                      <p style={{ fontSize: '0.75rem', color: '#DC2626', marginTop: '4px', marginBottom: 0 }}>Passwords do not match</p>
                    )}
                  </div>

                  {/* Submit */}
                  <button
                    type="submit"
                    className="gov-submit-btn"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="gov-btn-loading">
                        <span className="gov-spinner" />
                        <span>Creating citizen account…</span>
                      </span>
                    ) : (
                      <span>✚ Register as Citizen</span>
                    )}
                  </button>

                  <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.8125rem', color: '#64748B' }}>
                    By registering you agree to the{' '}
                    <button type="button" className="gov-link-subtle" onClick={() => setIsHelpModalOpen(true)}>Privacy Policy</button>
                    . No unnecessary personal identifiers or Aadhaar numbers are collected.
                  </div>
                </form>
                )}

                {/* ── PORTAL FORM (Official / Admin) ── */}
                {formMode === 'portal' && (
                <div id="portal-form-content">
                  {/* Statutory & Security Notice */}
                  <div style={{
                    background: 'linear-gradient(135deg, #FEF9C3, #FEF3C7)',
                    border: '1.5px solid #E89B31',
                    borderRadius: '6px',
                    padding: '10px 14px',
                    marginBottom: '16px',
                    fontSize: '0.75rem',
                    color: '#7A4A10',
                    lineHeight: 1.5,
                  }}>
                    <strong>⚠️ Restricted Government Workspace:</strong> Public registration is prohibited. Officials are onboarded solely via administrator invitations with single-use tokens or verified Government SSO.
                  </div>

                  {/* Controlled Onboarding & SSO Quick Actions */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
                    <button
                      type="button"
                      onClick={() => setShowInviteModal(true)}
                      style={{
                        padding: '8px 10px',
                        borderRadius: '6px',
                        border: '1.5px solid #0F766E',
                        backgroundColor: '#F0FDFA',
                        color: '#0F766E',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        textAlign: 'center',
                      }}
                    >
                      🎟️ Activate Invitation Token
                    </button>
                    <button
                      type="button"
                      onClick={handleOpenGovSSO}
                      style={{
                        padding: '8px 10px',
                        borderRadius: '6px',
                        border: '1.5px solid #3B82F6',
                        backgroundColor: '#EFF6FF',
                        color: '#1D4ED8',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        textAlign: 'center',
                      }}
                    >
                      🇮🇳 Government SSO Status
                    </button>
                  </div>

                  {/* Role Selector */}
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                    <button
                      type="button"
                      onClick={() => { setPortalRole('official'); setErrorMessage(''); }}
                      style={{
                        flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1.5px solid',
                        borderColor: portalRole === 'official' ? '#12345A' : '#CBD5E1',
                        background: portalRole === 'official' ? '#12345A' : '#fff',
                        color: portalRole === 'official' ? '#fff' : '#64748B',
                        fontWeight: 600, fontSize: '0.8125rem', cursor: 'pointer', transition: 'all 0.2s'
                      }}
                    >
                      🏢 Dept. Official
                    </button>
                    <button
                      type="button"
                      onClick={() => { setPortalRole('admin'); setErrorMessage(''); }}
                      style={{
                        flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1.5px solid',
                        borderColor: portalRole === 'admin' ? '#7B341E' : '#CBD5E1',
                        background: portalRole === 'admin' ? '#7B341E' : '#fff',
                        color: portalRole === 'admin' ? '#fff' : '#64748B',
                        fontWeight: 600, fontSize: '0.8125rem', cursor: 'pointer', transition: 'all 0.2s'
                      }}
                    >
                      🔑 Principal Admin
                    </button>
                  </div>

                  <form onSubmit={handlePortalLogin} noValidate>
                    {/* Identifier */}
                    <div className="gov-form-group">
                      <label htmlFor="portal-identifier" className="gov-form-label">
                        Official Email / Username <span className="gov-required" aria-hidden="true">*</span>
                      </label>
                      <input
                        id="portal-identifier"
                        name="portal-identifier"
                        type="text"
                        value={portalIdentifier}
                        onChange={(e) => setPortalIdentifier(e.target.value)}
                        placeholder={portalRole === 'admin' ? 'admin@nagrik.gov.in' : 'officer@dept.gov.in'}
                        className="gov-input"
                        required
                        autoComplete="username"
                      />
                    </div>

                    {/* Password */}
                    <div className="gov-form-group">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <label htmlFor="portal-password" className="gov-form-label">
                          Password <span className="gov-required" aria-hidden="true">*</span>
                        </label>
                        <button
                          type="button"
                          className="gov-link-subtle"
                          onClick={() => {
                            setResetIdentifier(portalIdentifier);
                            setShowResetModal(true);
                          }}
                        >
                          {t('login.forgotPassword')}
                        </button>
                      </div>
                      <div className="gov-input-wrapper">
                        <input
                          id="portal-password"
                          name="portal-password"
                          type={showPortalPassword ? 'text' : 'password'}
                          value={portalPassword}
                          onChange={(e) => setPortalPassword(e.target.value)}
                          placeholder="Enter your password"
                          className="gov-input gov-input-with-button"
                          required
                          autoComplete="current-password"
                        />
                        <button
                          type="button"
                          className="gov-password-toggle-btn"
                          onClick={() => setShowPortalPassword(!showPortalPassword)}
                          aria-label={showPortalPassword ? 'Hide password' : 'Show password'}
                        >
                          {showPortalPassword ? '👁️' : '👁️‍🗨️'}
                        </button>
                      </div>
                    </div>

                    {/* Demo credentials */}
                    <div style={{
                      background: '#F8FAFC', border: '1px dashed #CBD5E1',
                      borderRadius: '6px', padding: '10px 12px', marginBottom: '14px',
                      fontSize: '0.75rem', color: '#334155'
                    }}>
                      <div style={{ fontWeight: 700, marginBottom: '6px', color: '#1E293B' }}>Verified Demo Credentials</div>
                      {portalRole === 'official' ? (
                        <>
                          <div><strong>Agriculture:</strong> officer@dept.gov.in / Officer@2026</div>
                          <div><strong>Education:</strong> officer.edu@dept.gov.in / Officer@2026</div>
                        </>
                      ) : (
                        <div><strong>Admin:</strong> admin@nagrik.gov.in / Admin@2026</div>
                      )}
                    </div>

                    {/* Submit */}
                    <button type="submit" className="gov-submit-btn" disabled={isLoading}
                      style={{ background: portalRole === 'admin' ? 'linear-gradient(135deg, #7B341E, #C05621)' : undefined }}
                    >
                      {isLoading ? (
                        <span className="gov-btn-loading">
                          <span className="gov-spinner" />
                          <span>Signing in…</span>
                        </span>
                      ) : (
                        <span>{portalRole === 'admin' ? '🔑 Administrator Sign In' : '🏢 Department Official Sign In'}</span>
                      )}
                    </button>
                  </form>
                </div>
                )}

              </div>
            </div>
          </div>
        </div>
      </main>

      {/* ── 4. Government Institutional Footer ─────────────────────────── */}
      <footer className="gov-footer" role="contentinfo">
        <div className="gov-footer-inner">
          <div className="gov-footer-details">
            <div>
              <div className="gov-footer-brand">नागरिक सारथी • NagrikSaarathi</div>
              <p className="gov-footer-sub">{t('common.officialDisclaimer')}</p>
            </div>
            <div className="gov-footer-meta">
              <div>संविधान की आठवीं अनुसूची की 22 भाषाएँ</div>
              <div>Accessibility Standard: GIGW &amp; WCAG 2.1 AA</div>
            </div>
          </div>
        </div>
      </footer>

      {/* Language Selector Modal */}
      <LanguageSelectorModal isOpen={isLangModalOpen} onClose={() => setIsLangModalOpen(false)} />

      {/* Citizen Password Reset Modal */}
      {showResetModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
        >
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              maxWidth: '460px',
              width: '100%',
              padding: '28px',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                🔑 Password Assistance
              </h3>
              <button
                type="button"
                onClick={() => { setShowResetModal(false); setResetFeedback(null); }}
                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#64748B' }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '0.875rem', color: '#64748B', marginTop: 0, marginBottom: '16px', lineHeight: 1.5 }}>
              Enter your registered email, username, or mobile number to set a new password.
            </p>

            {resetFeedback && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '6px',
                  marginBottom: '16px',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  backgroundColor: resetFeedback.type === 'success' ? '#DCFCE7' : '#FEE2E2',
                  color: resetFeedback.type === 'success' ? '#166534' : '#991B1B',
                  border: `1px solid ${resetFeedback.type === 'success' ? '#86EFAC' : '#FCA5A5'}`,
                }}
              >
                {resetFeedback.text}
              </div>
            )}

            <form onSubmit={handleCustomReset}>
              <div style={{ display: 'grid', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                    Email or Mobile *
                  </label>
                  <input
                    type="text"
                    required
                    value={resetIdentifier}
                    onChange={(e) => setResetIdentifier(e.target.value)}
                    placeholder="e.g. citizen@example.com"
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                    New Password * (Min 8 chars)
                  </label>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={resetNewPassword}
                    onChange={(e) => setResetNewPassword(e.target.value)}
                    placeholder="Enter new password"
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => { setShowResetModal(false); setResetFeedback(null); }}
                  disabled={resetLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={resetLoading}
                  style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                >
                  {resetLoading ? 'Updating...' : 'Update Password'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Official Invitation Token Activation Modal */}
      {showInviteModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
        >
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              maxWidth: '560px',
              width: '100%',
              padding: '28px',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.3)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>🎟️</span>
                <span>Activate Official Access Token</span>
              </h3>
              <button
                type="button"
                onClick={() => { setShowInviteModal(false); setInviteFeedback(null); }}
                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#64748B' }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '0.8125rem', color: '#475569', marginTop: 0, marginBottom: '16px', lineHeight: 1.5 }}>
              Department Official onboarding is controlled by Principal Administrators. Single-use invitation tokens authorize specific departments, geographic scopes, and permissions.
            </p>

            {inviteFeedback && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '6px',
                  marginBottom: '16px',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  backgroundColor: inviteFeedback.type === 'success' ? '#DCFCE7' : '#FEE2E2',
                  color: inviteFeedback.type === 'success' ? '#166534' : '#991B1B',
                  border: `1px solid ${inviteFeedback.type === 'success' ? '#86EFAC' : '#FCA5A5'}`,
                }}
              >
                {inviteFeedback.text}
              </div>
            )}

            {!inviteDetails ? (
              <div>
                <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                  Secure Invitation Token <span className="gov-required">*</span>
                </label>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                  <input
                    type="text"
                    value={inviteToken}
                    onChange={(e) => setInviteToken(e.target.value)}
                    placeholder="e.g. GOV-INV-DEMO-SAMPLE-TOKEN-2026"
                    style={{ flex: 1, padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem', fontFamily: 'monospace' }}
                  />
                  <button
                    type="button"
                    onClick={handleVerifyInviteToken}
                    disabled={inviteLoading}
                    style={{
                      padding: '10px 16px',
                      backgroundColor: 'var(--color-teal)',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '6px',
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    {inviteLoading ? 'Verifying...' : 'Verify Token'}
                  </button>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
                  Demo single-use token provided: <code>GOV-INV-DEMO-SAMPLE-TOKEN-2026</code>
                </div>
              </div>
            ) : (
              <form onSubmit={handleActivateInviteAccount}>
                <div style={{ backgroundColor: '#F8FAFC', padding: '14px', borderRadius: '8px', border: '1px solid #E2E8F0', marginBottom: '16px' }}>
                  <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: '#0F172A', marginBottom: '8px' }}>
                    Authoritative Invitation Details:
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.75rem', color: '#334155' }}>
                    <div><strong>Invitee:</strong> {inviteDetails.full_name}</div>
                    <div><strong>Email:</strong> {inviteDetails.email}</div>
                    <div><strong>Department:</strong> {inviteDetails.department_name}</div>
                    <div><strong>State Scope:</strong> {inviteDetails.state_scope || 'Central / All-India'}</div>
                    <div><strong>Status:</strong> <span style={{ color: '#166534', fontWeight: 700 }}>{inviteDetails.status.toUpperCase()}</span></div>
                    <div><strong>Expires:</strong> {new Date(inviteDetails.expires_at).toLocaleString()}</div>
                  </div>
                </div>

                <div style={{ display: 'grid', gap: '12px', marginBottom: '18px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                      Set Your Secure Account Password * (Min 8 chars)
                    </label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      value={invitePassword}
                      onChange={(e) => setInvitePassword(e.target.value)}
                      placeholder="Enter new password"
                      style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                      Confirm Password *
                    </label>
                    <input
                      type="password"
                      required
                      value={inviteConfirmPassword}
                      onChange={(e) => setInviteConfirmPassword(e.target.value)}
                      placeholder="Re-enter password"
                      style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                    />
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setInviteDetails(null)}
                    disabled={inviteLoading}
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={inviteLoading}
                    style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                  >
                    {inviteLoading ? 'Activating...' : 'Activate & Onboard Official'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Government SSO Integration Information Modal */}
      {showSSOModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
        >
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              maxWidth: '560px',
              width: '100%',
              padding: '28px',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.3)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>🇮🇳</span>
                <span>Government SSO (Parichay / e-Pramaan)</span>
              </h3>
              <button
                type="button"
                onClick={() => setShowSSOModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#64748B' }}
              >
                ✕
              </button>
            </div>

            {ssoLoading ? (
              <div style={{ padding: '24px', textAlign: 'center', color: '#64748B' }}>
                Loading Government SSO configuration...
              </div>
            ) : ssoConfig ? (
              <div>
                <div style={{
                  backgroundColor: ssoConfig.is_configured ? '#ECFDF5' : '#FFFBEB',
                  border: `1px solid ${ssoConfig.is_configured ? '#A7F3D0' : '#FDE68A'}`,
                  borderRadius: '8px',
                  padding: '14px',
                  marginBottom: '16px',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '1.25rem' }}>{ssoConfig.is_configured ? '🟢' : '⏳'}</span>
                    <strong style={{ color: ssoConfig.is_configured ? '#065F46' : '#92400E', fontSize: '0.875rem' }}>
                      Status: {ssoConfig.status}
                    </strong>
                  </div>
                  <div style={{ fontSize: '0.8125rem', color: '#334155', lineHeight: 1.5 }}>
                    {ssoConfig.message}
                  </div>
                </div>

                <div style={{ fontSize: '0.8125rem', color: '#334155', lineHeight: 1.6, marginBottom: '16px' }}>
                  <div style={{ fontWeight: 700, marginBottom: '6px', color: '#0F172A' }}>Architecture & Compliance:</div>
                  <ul style={{ paddingLeft: '20px', margin: 0 }}>
                    <li><strong>Protocol:</strong> {ssoConfig.protocol}</li>
                    <li><strong>Token Security:</strong> RS256 signature, issuer, audience, and expiry claim verification performed authoritative backend-only.</li>
                    <li><strong>Zero PII Exposure:</strong> No client secrets or token exchanges reside in browser memory.</li>
                    <li><strong>Role Mapping:</strong> Verified identities are mapped strictly against pre-approved administrator records.</li>
                  </ul>
                </div>

                <div style={{ backgroundColor: '#F8FAFC', padding: '12px', borderRadius: '6px', border: '1px solid #E2E8F0', fontSize: '0.75rem', color: '#64748B' }}>
                  <strong>Security Guarantee:</strong> NagrikSaarathi explicitly requires verified credentials before enabling live redirection. In the interim, official access is securely mediated through Principal Administrator single-use invitation tokens.
                </div>
              </div>
            ) : null}

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setShowSSOModal(false)}
                style={{ backgroundColor: 'var(--color-navy)', borderColor: 'var(--color-navy)' }}
              >
                Acknowledge & Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Help & Support Modal */}
      {isHelpModalOpen && (
        <div className="civic-modal-backdrop" onClick={() => setIsHelpModalOpen(false)}>
          <div className="civic-modal gov-help-modal" onClick={(e) => e.stopPropagation()}>
            <div className="civic-modal-header">
              <h3 style={{ margin: 0, color: 'var(--gov-navy, #12345A)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span aria-hidden="true">ℹ️</span>
                <span>{t('login.helpDesk')}</span>
              </h3>
              <button
                className="btn-icon"
                onClick={() => setIsHelpModalOpen(false)}
                aria-label={t('common.close')}
              >
                ✕
              </button>
            </div>
            <div className="civic-modal-body">
              <p style={{ lineHeight: 1.6, color: '#334155' }}>
                {t('login.helpDeskText')}
              </p>
              <div style={{ background: '#F1F5F9', padding: '12px', borderRadius: '4px', marginTop: '12px' }}>
                <div style={{ fontWeight: 600, fontSize: '0.875rem', color: '#1E293B' }}>
                  हेल्पलाइन: 1800-111-2026 (टोल-फ्री)
                </div>
                <div style={{ fontSize: '0.8125rem', color: '#475569', marginTop: '4px' }}>
                  ईमेल: support@nagriksaarathi.gov.in
                </div>
              </div>
            </div>
            <div className="civic-modal-footer">
              <button className="btn btn-primary btn-sm" onClick={() => setIsHelpModalOpen(false)}>
                {t('common.close')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
