import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { SchemeCataloguePage } from './pages/SchemeCataloguePage';
import { GuidedFormPage } from './pages/GuidedFormPage';
import { DashboardPage } from './pages/DashboardPage';
import { OfficialDashboardPage } from './pages/OfficialDashboardPage';
import { LoginPage } from './pages/LoginPage';
import { ProfileModal } from './components/ProfileModal';
import { SchemeRequestsModal } from './components/SchemeRequestsModal';
import { HelpSupportModal } from './components/HelpSupportModal';
import { api } from './services/api';

/**
 * NagrikSaarathi — Application Shell
 *
 * Three strictly separated workspaces share the same Navbar + Footer shell:
 *
 *   citizen  → pages: home, schemes, form
 *   official → page:  official
 *   admin    → page:  dashboard
 *
 * Route guards run on EVERY navigation event:
 *  - Unauthenticated users → login
 *  - Wrong-role access → user's own workspace + notification
 *  - Role is ALWAYS read from the server-verified JWT stored at login
 *    (never from client-side state manipulation)
 *
 * Users cannot change their role via profile settings or URL parameters.
 * The reset-password endpoint on the backend is the only role-change path,
 * and it is admin-authenticated there.
 */

/* ─── helpers ──────────────────────────────────────────────────────────────── */

/** The canonical home page for each role. */
function homePageForRole(role) {
  if (role === 'admin')    return 'dashboard';
  if (role === 'official') return 'official';
  return 'schemes';
}

/** Pages each role is permitted to visit. */
const ALLOWED_PAGES = {
  citizen:  new Set(['home', 'schemes', 'form', 'login']),
  official: new Set(['official', 'schemes', 'login']),  // officials may browse public catalogue
  admin:    new Set(['dashboard', 'schemes', 'login']),
};

/** Pages that require authentication. */
const PROTECTED_PAGES = new Set(['dashboard', 'form', 'official']);

/** Public pages accessible without login. */
const PUBLIC_PAGES = new Set(['home', 'schemes', 'login']);

/* ─── load user from storage (never trust role from storage alone — ME endpoint re-validates) */
function loadStoredUser() {
  try {
    const raw = sessionStorage.getItem('nagrik_user') || localStorage.getItem('nagrik_user');
    return raw ? JSON.parse(raw) : null;
  } catch (_) {
    return null;
  }
}

/* ─── App ──────────────────────────────────────────────────────────────────── */

export function App() {
  const { t } = useTranslation();

  const [currentUser, setCurrentUser] = useState(() => loadStoredUser());
  const [selectedSchemeId, setSelectedSchemeId] = useState(null);
  const [intendedPage, setIntendedPage] = useState(null);
  const [accessDeniedMsg, setAccessDeniedMsg] = useState('');

  // Modals
  const [isProfileOpen, setIsProfileOpen]    = useState(false);
  const [isRequestsOpen, setIsRequestsOpen]  = useState(false);
  const [isHelpOpen, setIsHelpOpen]          = useState(false);
  const [initialTrackingId, setInitialTrackingId] = useState('');

  /* ── compute initial page from URL hash ─────────────────────────────────── */
  const [activePage, setActivePage] = useState(() => {
    const rawHash = window.location.hash.replace('#', '');
    const page    = rawHash.split('?')[0] || '';
    const user    = loadStoredUser();

    if (!user) {
      // Only permit public pages without auth
      return PUBLIC_PAGES.has(page) ? page : 'login';
    }

    const allowed = ALLOWED_PAGES[user.role] || ALLOWED_PAGES.citizen;
    if (page && allowed.has(page)) return page;
    return homePageForRole(user.role);
  });

  /* ── core navigate function ─────────────────────────────────────────────── */
  const handleNavigate = (page, schemeId = null) => {
    setAccessDeniedMsg('');

    if (schemeId) {
      setSelectedSchemeId(schemeId);
      window.location.hash = `${page}?scheme=${schemeId}`;
    } else {
      window.location.hash = page;
    }
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /* ── guard: enforce role restrictions on page navigation ────────────────── */
  const guardedNavigate = (page, schemeId = null) => {
    setAccessDeniedMsg('');

    // Unauthenticated
    if (!currentUser) {
      if (PROTECTED_PAGES.has(page)) {
        setIntendedPage(page);
        handleNavigate('login');
        return;
      }
      if (PUBLIC_PAGES.has(page)) {
        handleNavigate(page, schemeId);
        return;
      }
      handleNavigate('login');
      return;
    }

    const role    = currentUser.role || 'citizen';
    const allowed = ALLOWED_PAGES[role] || ALLOWED_PAGES.citizen;

    if (!allowed.has(page)) {
      // Redirect to own workspace with message
      const ownHome = homePageForRole(role);
      setAccessDeniedMsg(
        `You do not have permission to access "${page}". Redirecting to your workspace.`
      );
      handleNavigate(ownHome);
      return;
    }

    handleNavigate(page, schemeId);
  };

  /* ── hash change listener ───────────────────────────────────────────────── */
  useEffect(() => {
    const handleHash = () => {
      const rawHash = window.location.hash.replace('#', '');
      const parts   = rawHash.split('?');
      const page    = parts[0];

      if (parts[1]) {
        const params = new URLSearchParams(parts[1]);
        const sId = params.get('scheme');
        if (sId) setSelectedSchemeId(Number(sId));
      }

      if (!page) return;
      guardedNavigate(page);
    };

    handleHash();
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUser]);

  /* ── login success ──────────────────────────────────────────────────────── */
  const handleLoginSuccess = (user, _token) => {
    setCurrentUser(user);
    setAccessDeniedMsg('');

    // If user was trying to visit a specific page and they are permitted
    if (intendedPage) {
      const allowed = ALLOWED_PAGES[user.role] || ALLOWED_PAGES.citizen;
      const target  = intendedPage;
      setIntendedPage(null);
      if (allowed.has(target)) {
        handleNavigate(target, selectedSchemeId);
        return;
      }
    }

    // Default: send to role's home
    handleNavigate(homePageForRole(user.role));
  };

  /* ── logout ─────────────────────────────────────────────────────────────── */
  const handleLogout = async () => {
    try { await api.logout(); } catch (_) { /* ignore */ }
    sessionStorage.removeItem('nagrik_token');
    sessionStorage.removeItem('nagrik_user');
    localStorage.removeItem('nagrik_token');
    localStorage.removeItem('nagrik_user');
    setCurrentUser(null);
    setIntendedPage(null);
    setAccessDeniedMsg('');
    handleNavigate('login');
  };

  const handleOpenTracking = (trackingId = '') => {
    setInitialTrackingId(trackingId);
    setIsRequestsOpen(true);
  };

  /* ── render login page (no shared navbar) ───────────────────────────────── */
  if (
    activePage === 'login' ||
    (!currentUser && PROTECTED_PAGES.has(activePage))
  ) {
    return (
      <>
        <LoginPage
          onLoginSuccess={handleLoginSuccess}
          onNavigateDashboard={() => handleNavigate('dashboard')}
          onNavigateForm={() => handleNavigate('form')}
          onNavigateHome={() => handleNavigate('schemes')}
        />
        <HelpSupportModal
          isOpen={isHelpOpen}
          onClose={() => setIsHelpOpen(false)}
          currentUser={currentUser}
          currentPageRef="Login Page"
        />
      </>
    );
  }

  /* ── compute what to render in the main area ─────────────────────────────── */
  const role = currentUser?.role || 'citizen';

  // Access-control: if logged-in user is on a page not in their allow-list,
  // show their workspace home instead (belt-and-suspenders in addition to guardedNavigate).
  const renderPage = (() => {
    const allowed = ALLOWED_PAGES[role] || ALLOWED_PAGES.citizen;
    if (!allowed.has(activePage)) {
      return homePageForRole(role);
    }
    return activePage;
  })();

  /* ── main render ─────────────────────────────────────────────────────────── */
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* Shared Navbar — all three workspaces */}
      <Navbar
        activePage={renderPage}
        setActivePage={guardedNavigate}
        currentUser={currentUser}
        onLogout={handleLogout}
        onOpenProfile={() => setIsProfileOpen(true)}
        onOpenRequests={() => { setInitialTrackingId(''); setIsRequestsOpen(true); }}
        onOpenHelp={() => setIsHelpOpen(true)}
      />

      {/* Access-denied notification */}
      {accessDeniedMsg && (
        <div
          role="alert"
          aria-live="polite"
          style={{
            background: '#FEF3C7',
            borderBottom: '1px solid #F59E0B',
            borderLeft: '4px solid #B45309',
            padding: '10px 24px',
            fontSize: '0.875rem',
            color: '#78350F',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <span>⚠️</span>
          <span>{accessDeniedMsg}</span>
          <button
            type="button"
            onClick={() => setAccessDeniedMsg('')}
            style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 700, color: '#B45309' }}
            aria-label="Dismiss"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <main id="main-content" style={{ flex: 1 }}>

        {/* ── CITIZEN WORKSPACE ──────────────────────────────────────────── */}
        {renderPage === 'home' && (
          <LandingPage
            onExploreSchemes={() => guardedNavigate('schemes')}
            onStartForm={() => guardedNavigate('form')}
            onViewDashboard={() => guardedNavigate(homePageForRole(role))}
          />
        )}

        {renderPage === 'schemes' && (
          <SchemeCataloguePage
            onSelectScheme={schemeId => guardedNavigate('form', schemeId)}
            onNavigateHome={() => guardedNavigate('home')}
            onOpenTracking={handleOpenTracking}
            onOpenHelp={() => setIsHelpOpen(true)}
          />
        )}

        {/* Citizen-only: Guided Application Form */}
        {renderPage === 'form' && role === 'citizen' && (
          <GuidedFormPage
            initialSchemeId={selectedSchemeId}
            onNavigateCatalogue={() => guardedNavigate('schemes')}
            onNavigateDashboard={() => guardedNavigate('dashboard')}
            onNavigateHome={() => guardedNavigate('home')}
            onOpenHelp={() => setIsHelpOpen(true)}
          />
        )}

        {/* ── PRINCIPAL ADMINISTRATOR WORKSPACE ────────────────────────── */}
        {renderPage === 'dashboard' && role === 'admin' && (
          <DashboardPage
            currentUser={currentUser}
            onOpenTracking={handleOpenTracking}
          />
        )}

        {/* ── DEPARTMENT OFFICIAL WORKSPACE ────────────────────────────── */}
        {renderPage === 'official' && role === 'official' && (
          <OfficialDashboardPage
            currentUser={currentUser}
            onNavigate={guardedNavigate}
            onLogout={handleLogout}
          />
        )}

        {/* ── Cross-role access attempt (should not reach here, belt & suspenders) */}
        {renderPage === 'form'      && role !== 'citizen' && null}
        {renderPage === 'dashboard' && role !== 'admin'   && null}
        {renderPage === 'official'  && role !== 'official' && null}
      </main>

      {/* ── Shared Footer ──────────────────────────────────────────────────── */}
      <footer className="civic-footer">
        <div
          className="civic-container"
          style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}
        >
          <div>
            <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--color-navy)' }}>
              NagrikSaarathi • नागरिक सारथी
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              Digital Citizen Service Assistance Platform • Supporting 22 Official Languages
            </div>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            {/* Citizens can track scheme requests */}
            {role === 'citizen' && (
              <button
                type="button"
                onClick={() => { setInitialTrackingId(''); setIsRequestsOpen(true); }}
                style={{ background: 'none', border: 'none', color: 'var(--color-teal)', cursor: 'pointer', fontSize: '0.85rem' }}
              >
                📋 Track Scheme Request
              </button>
            )}
            <button
              type="button"
              onClick={() => setIsHelpOpen(true)}
              style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer', fontSize: '0.85rem' }}
            >
              ❓ Need Help?
            </button>
          </div>
        </div>
      </footer>

      {/* ── Global Modals ─────────────────────────────────────────────────── */}
      <ProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        currentUser={currentUser}
        onUserUpdated={updatedUser => setCurrentUser(updatedUser)}
        onOpenRequests={() => { setInitialTrackingId(''); setIsRequestsOpen(true); }}
        onOpenHelp={() => setIsHelpOpen(true)}
        onLogout={handleLogout}
      />

      <SchemeRequestsModal
        isOpen={isRequestsOpen}
        onClose={() => { setIsRequestsOpen(false); setInitialTrackingId(''); }}
        currentUser={currentUser}
        initialTrackingId={initialTrackingId}
        onOpenScheme={schemeId => guardedNavigate('form', schemeId)}
      />

      <HelpSupportModal
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
        currentUser={currentUser}
        currentPageRef={renderPage}
      />
    </div>
  );
}

export default App;
