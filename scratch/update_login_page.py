import re

LOGIN_PAGE = r"c:\Users\chatt\OneDrive\Desktop\NagrikSaarathi\frontend\src\pages\LoginPage.jsx"

with open(LOGIN_PAGE, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Expand Register form state & Password Reset state
old_reg_state = """  // Register form state
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regMobile, setRegMobile] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [showRegPassword, setShowRegPassword] = useState(false);"""

new_reg_state = """  // Register form state (User choice of Role and Credentials)
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regMobile, setRegMobile] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [showRegPassword, setShowRegPassword] = useState(false);
  const [regRole, setRegRole] = useState('citizen'); // 'citizen' | 'official' | 'admin'
  const [regDepartment, setRegDepartment] = useState('');
  const [regDesignation, setRegDesignation] = useState('');
  const [regStateScope, setRegStateScope] = useState('');

  // Password / Role Customization Modal state
  const [showResetModal, setShowResetModal] = useState(false);
  const [resetIdentifier, setResetIdentifier] = useState('');
  const [resetNewPassword, setResetNewPassword] = useState('');
  const [resetRole, setResetRole] = useState('official');
  const [resetDepartment, setResetDepartment] = useState('');
  const [resetLoading, setResetLoading] = useState(false);
  const [resetFeedback, setResetFeedback] = useState(null);"""

assert old_reg_state in code, "old_reg_state not found"
code = code.replace(old_reg_state, new_reg_state)

# 2. Update handleRegister & add handleResetPassword
old_handle_register = """    setIsLoading(true);
    try {
      const response = await api.register({
        full_name: regFullName.trim(),
        email: regEmail.trim() || undefined,
        mobile: regMobile.trim() || undefined,
        password: regPassword,
      });

      sessionStorage.setItem('nagrik_token', response.access_token);
      sessionStorage.setItem('nagrik_user', JSON.stringify(response.user));

      setSuccessMessage(response.message || 'Account created successfully! Welcome to NagrikSaarathi.');

      if (onLoginSuccess) {
        onLoginSuccess(response.user, response.access_token);
      }
    } catch (err) {
      if (err.status === 409) {
        setErrorMessage('An account with this email or mobile already exists. Please sign in instead.');
      } else {
        setErrorMessage(err.message || 'Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };"""

new_handle_register = """    if (regRole === 'official' && !regDepartment.trim()) {
      setErrorMessage('Please specify your Ministry or Department name.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.register({
        full_name: regFullName.trim(),
        email: regEmail.trim() || undefined,
        mobile: regMobile.trim() || undefined,
        password: regPassword,
        role: regRole,
        department: regRole !== 'citizen' ? (regDepartment.trim() || undefined) : undefined,
        designation: regRole !== 'citizen' ? (regDesignation.trim() || undefined) : undefined,
        state_scope: regRole === 'official' ? (regStateScope.trim() || undefined) : undefined,
      });

      sessionStorage.setItem('nagrik_token', response.access_token);
      sessionStorage.setItem('nagrik_user', JSON.stringify(response.user));

      setSuccessMessage(response.message || `Account created successfully with role '${regRole}'! Welcome to NagrikSaarathi.`);

      if (onLoginSuccess) {
        onLoginSuccess(response.user, response.access_token);
      }
    } catch (err) {
      if (err.status === 409) {
        setErrorMessage('An account with this email or mobile already exists. Click "Set / Reset Password & Role" below to update it.');
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
        role: resetRole,
        department: resetRole !== 'citizen' ? (resetDepartment.trim() || undefined) : undefined,
      });

      setResetFeedback({
        type: 'success',
        text: res.message || 'Credentials and role updated! You can now log in immediately.',
      });

      setTimeout(() => {
        setShowResetModal(false);
        setResetFeedback(null);
        if (resetRole === 'citizen') {
          setFormMode('login');
          setIdentifier(resetIdentifier.trim());
        } else {
          setFormMode('portal');
          setPortalRole(resetRole);
          setPortalIdentifier(resetIdentifier.trim());
        }
      }, 1500);
    } catch (err) {
      setResetFeedback({ type: 'error', text: err.message || 'Failed to update credentials. Please check details.' });
    } finally {
      setResetLoading(false);
    }
  };"""

assert old_handle_register in code, "old_handle_register not found"
code = code.replace(old_handle_register, new_handle_register)

# 3. Add "Reset / Set My Password" in portal login form
old_portal_pwd_label = """                    <label htmlFor="portal-password" className="gov-form-label">
                      Password <span className="gov-required" aria-hidden="true">*</span>
                    </label>"""

new_portal_pwd_label = """                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <label htmlFor="portal-password" className="gov-form-label" style={{ margin: 0 }}>
                        Password <span className="gov-required" aria-hidden="true">*</span>
                      </label>
                      <button
                        type="button"
                        className="gov-link-subtle"
                        style={{ fontSize: '0.8125rem', color: 'var(--color-teal)' }}
                        onClick={() => {
                          setResetIdentifier(portalIdentifier);
                          setResetRole(portalRole);
                          setShowResetModal(true);
                        }}
                      >
                        Set / Reset My Password 🔑
                      </button>
                    </div>"""

assert old_portal_pwd_label in code, "old_portal_pwd_label not found"
code = code.replace(old_portal_pwd_label, new_portal_pwd_label)

# 4. Update Citizen login forgot password button
old_cit_forgot = """                      <button
                        type="button"
                        className="gov-link-subtle"
                        onClick={() => setIsHelpModalOpen(true)}
                      >
                        {t('login.forgotPassword')}
                      </button>"""

new_cit_forgot = """                      <button
                        type="button"
                        className="gov-link-subtle"
                        onClick={() => {
                          setResetIdentifier(identifier);
                          setResetRole('citizen');
                          setShowResetModal(true);
                        }}
                      >
                        {t('login.forgotPassword')}
                      </button>"""

assert old_cit_forgot in code, "old_cit_forgot not found"
code = code.replace(old_cit_forgot, new_cit_forgot)

# 5. Enhance Registration Form with Role Choice & Custom Department Fields
old_reg_form_top = """                {/* ── REGISTER FORM ── */}
                {formMode === 'register' && (
                <form id="register-form-content" onSubmit={handleRegister} noValidate>
                  {/* Full Name */}"""

new_reg_form_top = """                {/* ── REGISTER FORM ── */}
                {formMode === 'register' && (
                <form id="register-form-content" onSubmit={handleRegister} noValidate>
                  {/* Account Type Selector (User choice) */}
                  <div style={{ marginBottom: '18px', backgroundColor: '#F8FAFC', padding: '14px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Select Account Type / Role of Your Choice <span className="gov-required">*</span>
                    </label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                      <button
                        type="button"
                        onClick={() => setRegRole('citizen')}
                        style={{
                          padding: '10px 8px',
                          borderRadius: '6px',
                          border: regRole === 'citizen' ? '2px solid var(--color-teal)' : '1px solid var(--color-border)',
                          backgroundColor: regRole === 'citizen' ? '#FFFFFF' : 'transparent',
                          color: regRole === 'citizen' ? 'var(--color-navy)' : 'var(--color-text-secondary)',
                          fontWeight: regRole === 'citizen' ? 800 : 600,
                          fontSize: '0.8125rem',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        <span style={{ fontSize: '1.25rem' }}>👤</span>
                        <span>Citizen</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => setRegRole('official')}
                        style={{
                          padding: '10px 8px',
                          borderRadius: '6px',
                          border: regRole === 'official' ? '2px solid var(--color-teal)' : '1px solid var(--color-border)',
                          backgroundColor: regRole === 'official' ? '#FFFFFF' : 'transparent',
                          color: regRole === 'official' ? 'var(--color-navy)' : 'var(--color-text-secondary)',
                          fontWeight: regRole === 'official' ? 800 : 600,
                          fontSize: '0.8125rem',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        <span style={{ fontSize: '1.25rem' }}>🏛️</span>
                        <span>Dept. Official</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => setRegRole('admin')}
                        style={{
                          padding: '10px 8px',
                          borderRadius: '6px',
                          border: regRole === 'admin' ? '2px solid var(--color-teal)' : '1px solid var(--color-border)',
                          backgroundColor: regRole === 'admin' ? '#FFFFFF' : 'transparent',
                          color: regRole === 'admin' ? 'var(--color-navy)' : 'var(--color-text-secondary)',
                          fontWeight: regRole === 'admin' ? 800 : 600,
                          fontSize: '0.8125rem',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        <span style={{ fontSize: '1.25rem' }}>🛡️</span>
                        <span>Administrator</span>
                      </button>
                    </div>

                    <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#64748B' }}>
                      {regRole === 'citizen' && 'Access public schemes, guided forms, and personal eligibility tracking.'}
                      {regRole === 'official' && 'Access the Department Official Portal to submit scheme proposals, update guidelines, and monitor analytics.'}
                      {regRole === 'admin' && 'Access the Principal Admin Intelligence Dashboard with full approval authority and governance.'}
                    </div>
                  </div>

                  {/* Official / Admin specific department fields */}
                  {regRole !== 'citizen' && (
                    <div style={{ display: 'grid', gap: '12px', marginBottom: '16px', padding: '14px', backgroundColor: '#EFF6FF', borderRadius: '8px', border: '1px solid #BFDBFE' }}>
                      <div className="gov-form-group" style={{ margin: 0 }}>
                        <label htmlFor="reg-department" className="gov-form-label">
                          Assigned Ministry or Department <span className="gov-required">*</span>
                        </label>
                        <input
                          id="reg-department"
                          type="text"
                          value={regDepartment}
                          onChange={(e) => setRegDepartment(e.target.value)}
                          placeholder="e.g. Ministry of Agriculture & Farmers Welfare, MEITY, Education..."
                          className="gov-input"
                          required
                        />
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                        <div className="gov-form-group" style={{ margin: 0 }}>
                          <label htmlFor="reg-designation" className="gov-form-label">
                            Designation / Title
                          </label>
                          <input
                            id="reg-designation"
                            type="text"
                            value={regDesignation}
                            onChange={(e) => setRegDesignation(e.target.value)}
                            placeholder="e.g. Nodal Officer, Director"
                            className="gov-input"
                          />
                        </div>

                        {regRole === 'official' && (
                          <div className="gov-form-group" style={{ margin: 0 }}>
                            <label htmlFor="reg-state-scope" className="gov-form-label">
                              State Scope (Optional)
                            </label>
                            <input
                              id="reg-state-scope"
                              type="text"
                              value={regStateScope}
                              onChange={(e) => setRegStateScope(e.target.value.toUpperCase())}
                              placeholder="e.g. DL, MH, WB (blank = Central)"
                              className="gov-input"
                              maxLength={10}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Full Name */}"""

assert old_reg_form_top in code, "old_reg_form_top not found"
code = code.replace(old_reg_form_top, new_reg_form_top)

# 6. Add Custom Credentials / Password Reset Modal before closing div
target_modal_insertion = """      {/* Help Modal */}"""

custom_reset_modal_jsx = """      {/* Set / Reset Password & Role of Your Choice Modal */}
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
              maxWidth: '520px',
              width: '100%',
              padding: '28px',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                🔑 Set Your Password & Role
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
              Set your own custom password and select your desired account role (Citizen, Department Official, or Admin) for any existing email or username.
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
                    Email, Mobile, or Username *
                  </label>
                  <input
                    type="text"
                    required
                    value={resetIdentifier}
                    onChange={(e) => setResetIdentifier(e.target.value)}
                    placeholder="e.g. chatterjeesoumita0@gmail.com"
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                    New Password of Your Choice * (Min 8 chars)
                  </label>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={resetNewPassword}
                    onChange={(e) => setResetNewPassword(e.target.value)}
                    placeholder="Enter your new password"
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                    Set Account Role
                  </label>
                  <select
                    value={resetRole}
                    onChange={(e) => setResetRole(e.target.value)}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                  >
                    <option value="official">🏛️ Department Official</option>
                    <option value="admin">🛡️ Principal Administrator</option>
                    <option value="citizen">👤 Citizen</option>
                  </select>
                </div>

                {resetRole !== 'citizen' && (
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                      Assigned Department / Ministry Name
                    </label>
                    <input
                      type="text"
                      value={resetDepartment}
                      onChange={(e) => setResetDepartment(e.target.value)}
                      placeholder="e.g. Ministry of Electronics and Information Technology"
                      style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                    />
                  </div>
                )}
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
                  {resetLoading ? 'Updating...' : 'Set Password & Role'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Help & Support Modal */}"""

assert target_modal_insertion in code, "target_modal_insertion not found"
code = code.replace(target_modal_insertion, custom_reset_modal_jsx)

with open(LOGIN_PAGE, "w", encoding="utf-8") as f:
    f.write(code)

print("LoginPage.jsx successfully updated with role choices and custom password/role setter!")
