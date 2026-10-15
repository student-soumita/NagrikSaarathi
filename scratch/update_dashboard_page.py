import re

DASHBOARD_PATH = r"c:\Users\chatt\OneDrive\Desktop\NagrikSaarathi\frontend\src\pages\DashboardPage.jsx"

with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. State expansion
old_state = """  // Admin Panel State
  const [adminTab, setAdminTab] = useState('requests'); // 'requests' | 'tickets' | 'i18n'
  const [schemeRequests, setSchemeRequests] = useState([]);
  const [srStatusFilter, setSrStatusFilter] = useState('');
  const [srLoading, setSrLoading] = useState(false);
  const [helpTickets, setHelpTickets] = useState([]);
  const [htCategoryFilter, setHtCategoryFilter] = useState('');
  const [htStatusFilter, setHtStatusFilter] = useState('');
  const [htLoading, setHtLoading] = useState(false);
  const [i18nAudit, setI18nAudit] = useState(null);
  const [i18nLoading, setI18nLoading] = useState(false);
  const [adminActionMsg, setAdminActionMsg] = useState(null);
  const [i18nFilter, setI18nFilter] = useState('all');
  const [testingVoiceCode, setTestingVoiceCode] = useState(null);
  const [voiceTestResult, setVoiceTestResult] = useState(null);"""

new_state = """  // Admin Panel State
  const [adminTab, setAdminTab] = useState('requests'); // 'requests' | 'tickets' | 'proposals' | 'officials' | 'i18n'
  const [schemeRequests, setSchemeRequests] = useState([]);
  const [srStatusFilter, setSrStatusFilter] = useState('');
  const [srLoading, setSrLoading] = useState(false);
  const [helpTickets, setHelpTickets] = useState([]);
  const [htCategoryFilter, setHtCategoryFilter] = useState('');
  const [htStatusFilter, setHtStatusFilter] = useState('');
  const [htLoading, setHtLoading] = useState(false);
  const [i18nAudit, setI18nAudit] = useState(null);
  const [i18nLoading, setI18nLoading] = useState(false);
  const [adminActionMsg, setAdminActionMsg] = useState(null);
  const [i18nFilter, setI18nFilter] = useState('all');
  const [testingVoiceCode, setTestingVoiceCode] = useState(null);
  const [voiceTestResult, setVoiceTestResult] = useState(null);

  // Scheme Proposals State (Official multi-stage submission governance)
  const [proposals, setProposals] = useState([]);
  const [propLoading, setPropLoading] = useState(false);
  const [propStatusFilter, setPropStatusFilter] = useState('');
  const [propTypeFilter, setPropTypeFilter] = useState('');
  const [selectedProposal, setSelectedProposal] = useState(null);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [reviewDecision, setReviewDecision] = useState('approve'); // 'approve' | 'request_revision' | 'reject'
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewSubmitting, setReviewSubmitting] = useState(false);

  // Department Officials State
  const [officials, setOfficials] = useState([]);
  const [officialsLoading, setOfficialsLoading] = useState(false);
  const [officialSearch, setOfficialSearch] = useState('');
  const [officialDeptFilter, setOfficialDeptFilter] = useState('');
  const [showCreateOfficialModal, setShowCreateOfficialModal] = useState(false);
  const [officialFormSubmitting, setOfficialFormSubmitting] = useState(false);
  const [officialForm, setOfficialForm] = useState({
    identifier: '',
    email: '',
    full_name: '',
    department: '',
    designation: '',
    state_scope: '',
    password: '',
  });"""

assert old_state in content, "old_state not found in DashboardPage.jsx"
content = content.replace(old_state, new_state)

# 2. Fetchers & useEffect expansion
old_fetchers = """  useEffect(() => {
    if (adminTab === 'requests') fetchSchemeRequests();
    else if (adminTab === 'tickets') fetchHelpTickets();
    else if (adminTab === 'i18n') fetchI18nAudit();
  }, [adminTab, srStatusFilter, htCategoryFilter, htStatusFilter, authApplied]);"""

new_fetchers = """  const fetchProposals = async () => {
    try {
      setPropLoading(true);
      const data = await api.getAdminProposals(propStatusFilter || null, null, propTypeFilter || null);
      setProposals(Array.isArray(data) ? data : []);
    } catch (err) {
      setProposals([]);
    } finally {
      setPropLoading(false);
    }
  };

  const handleReviewProposal = async () => {
    if (!selectedProposal) return;
    if (reviewDecision === 'request_revision' && !reviewNotes.trim()) {
      setAdminActionMsg({ type: 'error', text: 'Please specify revision instructions for the official.' });
      return;
    }
    if (reviewDecision === 'reject' && !reviewNotes.trim()) {
      setAdminActionMsg({ type: 'error', text: 'Please provide a formal rejection reason.' });
      return;
    }
    try {
      setReviewSubmitting(true);
      setAdminActionMsg(null);
      const payload = {
        action: reviewDecision,
        admin_notes: reviewNotes.trim(),
        revision_notes: reviewDecision === 'request_revision' ? reviewNotes.trim() : undefined,
        rejection_reason: reviewDecision === 'reject' ? reviewNotes.trim() : undefined,
      };
      await api.reviewSchemeProposal(selectedProposal.id, payload);
      setAdminActionMsg({
        type: 'success',
        text: `Proposal #${selectedProposal.proposal_number} successfully updated (${reviewDecision === 'approve' ? 'Approved & Published to Catalogue' : reviewDecision === 'request_revision' ? 'Revision Requested' : 'Rejected'}).`,
      });
      setReviewModalOpen(false);
      setSelectedProposal(null);
      setReviewNotes('');
      fetchProposals();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Review action failed.' });
    } finally {
      setReviewSubmitting(false);
    }
  };

  const fetchOfficials = async () => {
    try {
      setOfficialsLoading(true);
      const data = await api.getAdminOfficials({
        search: officialSearch || null,
        department: officialDeptFilter || null,
      });
      setOfficials(Array.isArray(data) ? data : []);
    } catch (err) {
      setOfficials([]);
    } finally {
      setOfficialsLoading(false);
    }
  };

  const handleCreateOfficial = async (e) => {
    if (e) e.preventDefault();
    if (!officialForm.full_name.trim() || !officialForm.identifier.trim() || !officialForm.department.trim() || !officialForm.password.trim()) {
      setAdminActionMsg({ type: 'error', text: 'Please complete all required fields.' });
      return;
    }
    if (officialForm.password.length < 8) {
      setAdminActionMsg({ type: 'error', text: 'Password must be at least 8 characters long.' });
      return;
    }
    try {
      setOfficialFormSubmitting(true);
      setAdminActionMsg(null);
      await api.createOfficialAccount({
        identifier: officialForm.identifier.trim(),
        email: officialForm.email.trim() || officialForm.identifier.trim(),
        full_name: officialForm.full_name.trim(),
        department: officialForm.department.trim(),
        designation: officialForm.designation.trim() || undefined,
        state_scope: officialForm.state_scope.trim() || null,
        password: officialForm.password,
      });
      setAdminActionMsg({
        type: 'success',
        text: `Official account created for ${officialForm.full_name} (${officialForm.department}).`,
      });
      setShowCreateOfficialModal(false);
      setOfficialForm({
        identifier: '',
        email: '',
        full_name: '',
        department: '',
        designation: '',
        state_scope: '',
        password: '',
      });
      fetchOfficials();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Failed to provision official account.' });
    } finally {
      setOfficialFormSubmitting(false);
    }
  };

  const handleToggleOfficialStatus = async (official) => {
    try {
      setAdminActionMsg(null);
      const nextActive = !official.is_active;
      await api.updateOfficialAccount(official.id, { is_active: nextActive });
      setAdminActionMsg({
        type: 'success',
        text: `Official ${official.full_name} status updated to ${nextActive ? 'Active' : 'Suspended'}.`,
      });
      fetchOfficials();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Failed to update official status.' });
    }
  };

  useEffect(() => {
    if (adminTab === 'requests') fetchSchemeRequests();
    else if (adminTab === 'tickets') fetchHelpTickets();
    else if (adminTab === 'proposals') fetchProposals();
    else if (adminTab === 'officials') fetchOfficials();
    else if (adminTab === 'i18n') fetchI18nAudit();
  }, [adminTab, srStatusFilter, htCategoryFilter, htStatusFilter, propStatusFilter, propTypeFilter, officialSearch, officialDeptFilter, authApplied]);"""

assert old_fetchers in content, "old_fetchers not found in DashboardPage.jsx"
content = content.replace(old_fetchers, new_fetchers)

# 3. Tab buttons expansion
old_tabs = """              {[
                { id: 'requests', icon: '📋', label: 'Scheme Requests' },
                { id: 'tickets', icon: '🎫', label: 'Help Tickets' },
                { id: 'i18n', icon: '🌐', label: 'Translation Audit' },
              ].map((tab) => ("""

new_tabs = """              {[
                { id: 'requests', icon: '📋', label: 'Scheme Requests' },
                { id: 'tickets', icon: '🎫', label: 'Help Tickets' },
                { id: 'proposals', icon: '📝', label: 'Scheme Proposals' },
                { id: 'officials', icon: '🏛️', label: 'Department Officials' },
                { id: 'i18n', icon: '🌐', label: 'Translation Audit' },
              ].map((tab) => ("""

assert old_tabs in content, "old_tabs not found in DashboardPage.jsx"
content = content.replace(old_tabs, new_tabs)

# 4. Tab contents for Proposals & Officials
target_i18n_tab = """            {/* ── TAB: Multilingual Quality & Audio Assurance ───────────── */}
            {adminTab === 'i18n' && ("""

proposals_and_officials_jsx = """            {/* ── TAB: Scheme Proposals (Official Submission Governance) ── */}
            {adminTab === 'proposals' && (
              <div style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
                  <div>
                    <h3 style={{ margin: '0 0 6px 0', fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                      📝 Department Scheme Proposals & Review Queue
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--color-text-secondary)', maxWidth: '780px' }}>
                      Review, audit, request revisions, or approve multi-stage scheme proposals submitted by verified departmental officials. Approved proposals instantly publish or update live catalogue records with audit logs.
                    </p>
                  </div>
                  <button className="btn btn-secondary btn-sm" onClick={fetchProposals} disabled={propLoading}>
                    ↺ {propLoading ? 'Refreshing...' : 'Refresh Proposals'}
                  </button>
                </div>

                {/* Proposals Metrics Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '24px' }}>
                  <div style={{ padding: '14px 18px', backgroundColor: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Total Proposals</div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--color-navy)', marginTop: '4px' }}>{proposals.length}</div>
                  </div>
                  <div style={{ padding: '14px 18px', backgroundColor: '#EFF6FF', borderRadius: '8px', border: '1px solid #BFDBFE' }}>
                    <div style={{ fontSize: '0.75rem', color: '#1D4ED8', fontWeight: 700, textTransform: 'uppercase' }}>Awaiting Review</div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#1E40AF', marginTop: '4px' }}>
                      {proposals.filter(p => ['submitted', 'under_review'].includes(p.status)).length}
                    </div>
                  </div>
                  <div style={{ padding: '14px 18px', backgroundColor: '#F5F3FF', borderRadius: '8px', border: '1px solid #DDD6FE' }}>
                    <div style={{ fontSize: '0.75rem', color: '#6D28D9', fontWeight: 700, textTransform: 'uppercase' }}>Revision Required</div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#5B21B6', marginTop: '4px' }}>
                      {proposals.filter(p => p.status === 'revision_required').length}
                    </div>
                  </div>
                  <div style={{ padding: '14px 18px', backgroundColor: '#ECFDF5', borderRadius: '8px', border: '1px solid #A7F3D0' }}>
                    <div style={{ fontSize: '0.75rem', color: '#047857', fontWeight: 700, textTransform: 'uppercase' }}>Approved & Published</div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#065F46', marginTop: '4px' }}>
                      {proposals.filter(p => p.status === 'approved').length}
                    </div>
                  </div>
                </div>

                {/* Filters */}
                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
                  <div>
                    <label style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-text-muted)', marginRight: '6px' }}>Status:</label>
                    <select
                      value={propStatusFilter}
                      onChange={(e) => setPropStatusFilter(e.target.value)}
                      style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                    >
                      <option value="">All Statuses</option>
                      <option value="submitted">Submitted</option>
                      <option value="under_review">Under Review</option>
                      <option value="revision_required">Revision Required</option>
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                      <option value="draft">Draft</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-text-muted)', marginRight: '6px' }}>Type:</label>
                    <select
                      value={propTypeFilter}
                      onChange={(e) => setPropTypeFilter(e.target.value)}
                      style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                    >
                      <option value="">All Types</option>
                      <option value="new_scheme">New Scheme</option>
                      <option value="metadata_update">Metadata Update</option>
                      <option value="url_correction">URL Correction</option>
                    </select>
                  </div>
                </div>

                {/* Proposals Table */}
                {propLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>
                    Loading scheme proposals...
                  </div>
                ) : proposals.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '48px', backgroundColor: '#F8FAFC', borderRadius: '8px', border: '1px dashed var(--color-border)' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>📭</div>
                    <div style={{ fontWeight: 700, color: 'var(--color-navy)' }}>No proposals match the filter criteria</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                      Proposals submitted by Department Officials will appear here for review and publication.
                    </div>
                  </div>
                ) : (
                  <div style={{ overflowX: 'auto', border: '1px solid var(--color-border)', borderRadius: '8px' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)', textAlign: 'left' }}>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Proposal #</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Scheme Name</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Department / Level</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Type</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Submitted</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)', textAlign: 'center' }}>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {proposals.map((prop, idx) => {
                          const statusConfig = {
                            draft: { label: 'Draft', color: '#64748B', bg: '#F1F5F9' },
                            submitted: { label: 'Submitted', color: '#1D4ED8', bg: '#EFF6FF' },
                            under_review: { label: 'Under Review', color: '#B45309', bg: '#FEF3C7' },
                            revision_required: { label: 'Revision Required', color: '#6D28D9', bg: '#F5F3FF' },
                            approved: { label: 'Approved & Live', color: '#047857', bg: '#ECFDF5' },
                            rejected: { label: 'Rejected', color: '#BE123C', bg: '#FFF1F2' },
                          }[prop.status] || { label: prop.status, color: '#334155', bg: '#F1F5F9' };

                          const typeBadge = {
                            new_scheme: { label: '✨ New Scheme', bg: '#E0E7FF', color: '#3730A3' },
                            metadata_update: { label: '✏️ Metadata Update', bg: '#FEF3C7', color: '#92400E' },
                            url_correction: { label: '🔗 URL Correction', bg: '#F1F5F9', color: '#334155' },
                          }[prop.proposal_type] || { label: prop.proposal_type, bg: '#F1F5F9', color: '#334155' };

                          return (
                            <tr
                              key={prop.id || idx}
                              style={{
                                borderBottom: '1px solid var(--color-border)',
                                backgroundColor: idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA',
                              }}
                            >
                              <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontWeight: 700, color: 'var(--color-navy)' }}>
                                #{prop.proposal_number}
                              </td>
                              <td style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>
                                {prop.scheme_name}
                              </td>
                              <td style={{ padding: '12px 16px', color: 'var(--color-text-secondary)', fontSize: '0.8125rem' }}>
                                <div style={{ fontWeight: 600 }}>{prop.department_name}</div>
                                <div style={{ color: 'var(--color-text-muted)' }}>{prop.government_level}{prop.state_code ? ` • ${prop.state_code}` : ''}</div>
                              </td>
                              <td style={{ padding: '12px 16px' }}>
                                <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, backgroundColor: typeBadge.bg, color: typeBadge.color }}>
                                  {typeBadge.label}
                                </span>
                              </td>
                              <td style={{ padding: '12px 16px' }}>
                                <span style={{ padding: '4px 10px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 800, backgroundColor: statusConfig.bg, color: statusConfig.color }}>
                                  {statusConfig.label}
                                </span>
                              </td>
                              <td style={{ padding: '12px 16px', color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>
                                {prop.submitted_at ? new Date(prop.submitted_at).toLocaleDateString() : (prop.created_at ? new Date(prop.created_at).toLocaleDateString() : '—')}
                              </td>
                              <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                <button
                                  type="button"
                                  className="btn btn-sm"
                                  onClick={() => {
                                    setSelectedProposal(prop);
                                    setReviewDecision(['submitted', 'under_review'].includes(prop.status) ? 'approve' : 'approve');
                                    setReviewNotes(prop.admin_notes || prop.revision_requested_notes || prop.rejection_reason || '');
                                    setReviewModalOpen(true);
                                  }}
                                  style={{
                                    fontSize: '0.8125rem',
                                    padding: '5px 12px',
                                    borderRadius: '6px',
                                    backgroundColor: ['submitted', 'under_review'].includes(prop.status) ? 'var(--color-navy)' : '#F1F5F9',
                                    color: ['submitted', 'under_review'].includes(prop.status) ? '#FFFFFF' : 'var(--color-navy)',
                                    fontWeight: 700,
                                    border: '1px solid var(--color-border)',
                                    cursor: 'pointer',
                                  }}
                                >
                                  {['submitted', 'under_review'].includes(prop.status) ? '⚖️ Review' : '👁️ View'}
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Review Modal */}
                {reviewModalOpen && selectedProposal && (
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
                        maxWidth: '750px',
                        width: '100%',
                        maxHeight: '90vh',
                        overflowY: 'auto',
                        padding: '28px',
                        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                        <div>
                          <div style={{ fontSize: '0.8125rem', fontFamily: 'monospace', color: 'var(--color-text-muted)' }}>
                            Proposal #{selectedProposal.proposal_number}
                          </div>
                          <h3 style={{ margin: '4px 0 0 0', fontSize: '1.35rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                            {selectedProposal.scheme_name}
                          </h3>
                        </div>
                        <button
                          type="button"
                          onClick={() => { setReviewModalOpen(false); setSelectedProposal(null); }}
                          style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: 'var(--color-text-muted)' }}
                        >
                          ✕
                        </button>
                      </div>

                      {/* Details Meta */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', padding: '14px', backgroundColor: '#F8FAFC', borderRadius: '8px', marginBottom: '16px', fontSize: '0.875rem' }}>
                        <div>
                          <span style={{ color: 'var(--color-text-muted)' }}>Department: </span>
                          <strong style={{ color: 'var(--color-navy)' }}>{selectedProposal.department_name}</strong>
                        </div>
                        <div>
                          <span style={{ color: 'var(--color-text-muted)' }}>Level / State: </span>
                          <strong style={{ color: 'var(--color-navy)' }}>{selectedProposal.government_level} {selectedProposal.state_code ? `(${selectedProposal.state_code})` : ''}</strong>
                        </div>
                        <div>
                          <span style={{ color: 'var(--color-text-muted)' }}>Proposal Type: </span>
                          <strong style={{ color: 'var(--color-navy)' }}>{selectedProposal.proposal_type}</strong>
                        </div>
                        <div>
                          <span style={{ color: 'var(--color-text-muted)' }}>Category: </span>
                          <strong style={{ color: 'var(--color-navy)' }}>{selectedProposal.category || 'General'}</strong>
                        </div>
                      </div>

                      {/* Content Preview */}
                      <div style={{ marginBottom: '16px' }}>
                        <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: '4px' }}>Description</div>
                        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-text-primary)', lineHeight: 1.5, backgroundColor: '#FAFAFA', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          {selectedProposal.description}
                        </p>
                      </div>

                      <div style={{ marginBottom: '16px' }}>
                        <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: '4px' }}>Benefit Summary</div>
                        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-text-primary)', lineHeight: 1.5, backgroundColor: '#FAFAFA', padding: '12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          {selectedProposal.benefit_summary}
                        </p>
                      </div>

                      {/* Official URLs */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
                        <div style={{ padding: '10px 14px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-muted)' }}>Official Source Portal</div>
                          <a href={selectedProposal.official_source_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.85rem', color: '#1D4ED8', textDecoration: 'none', wordBreak: 'break-all' }}>
                            {selectedProposal.official_source_url || '—'} ↗
                          </a>
                        </div>
                        <div style={{ padding: '10px 14px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-muted)' }}>Official Application URL</div>
                          <a href={selectedProposal.official_application_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.85rem', color: '#1D4ED8', textDecoration: 'none', wordBreak: 'break-all' }}>
                            {selectedProposal.official_application_url || '—'} ↗
                          </a>
                        </div>
                      </div>

                      {/* Official Submitter & Justification */}
                      {selectedProposal.justification && (
                        <div style={{ marginBottom: '20px', padding: '12px', backgroundColor: '#EFF6FF', borderRadius: '6px', border: '1px solid #BFDBFE' }}>
                          <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: '#1D4ED8', marginBottom: '4px' }}>Official Justification / Change Rationale</div>
                          <div style={{ fontSize: '0.875rem', color: '#1E3A8A' }}>{selectedProposal.justification}</div>
                        </div>
                      )}

                      {/* Past Admin Decision info if already decided */}
                      {['approved', 'rejected'].includes(selectedProposal.status) ? (
                        <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: selectedProposal.status === 'approved' ? '#ECFDF5' : '#FFF1F2', border: `1px solid ${selectedProposal.status === 'approved' ? '#A7F3D0' : '#FECDD3'}`, marginBottom: '20px' }}>
                          <div style={{ fontWeight: 800, color: selectedProposal.status === 'approved' ? '#047857' : '#BE123C' }}>
                            {selectedProposal.status === 'approved' ? '✓ Approved & Published' : '✕ Rejected'}
                          </div>
                          {selectedProposal.admin_notes && (
                            <div style={{ fontSize: '0.875rem', marginTop: '6px', color: 'var(--color-text-secondary)' }}>
                              <strong>Notes: </strong>{selectedProposal.admin_notes}
                            </div>
                          )}
                          {selectedProposal.rejection_reason && (
                            <div style={{ fontSize: '0.875rem', marginTop: '6px', color: '#BE123C' }}>
                              <strong>Reason: </strong>{selectedProposal.rejection_reason}
                            </div>
                          )}
                        </div>
                      ) : (
                        /* Review Decision Action Form */
                        <div style={{ borderTop: '2px solid var(--color-border)', paddingTop: '20px', marginTop: '20px' }}>
                          <h4 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                            Review Decision
                          </h4>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '16px' }}>
                            <label
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '12px',
                                borderRadius: '8px',
                                border: reviewDecision === 'approve' ? '2px solid #047857' : '1px solid var(--color-border)',
                                backgroundColor: reviewDecision === 'approve' ? '#ECFDF5' : '#FFFFFF',
                                cursor: 'pointer',
                                fontWeight: 700,
                                fontSize: '0.875rem',
                                color: reviewDecision === 'approve' ? '#047857' : 'var(--color-navy)',
                              }}
                            >
                              <input
                                type="radio"
                                name="reviewDecision"
                                value="approve"
                                checked={reviewDecision === 'approve'}
                                onChange={() => setReviewDecision('approve')}
                              />
                              Approve & Publish
                            </label>

                            <label
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '12px',
                                borderRadius: '8px',
                                border: reviewDecision === 'request_revision' ? '2px solid #D97706' : '1px solid var(--color-border)',
                                backgroundColor: reviewDecision === 'request_revision' ? '#FEF3C7' : '#FFFFFF',
                                cursor: 'pointer',
                                fontWeight: 700,
                                fontSize: '0.875rem',
                                color: reviewDecision === 'request_revision' ? '#92400E' : 'var(--color-navy)',
                              }}
                            >
                              <input
                                type="radio"
                                name="reviewDecision"
                                value="request_revision"
                                checked={reviewDecision === 'request_revision'}
                                onChange={() => setReviewDecision('request_revision')}
                              />
                              Request Revision
                            </label>

                            <label
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '12px',
                                borderRadius: '8px',
                                border: reviewDecision === 'reject' ? '2px solid #DC2626' : '1px solid var(--color-border)',
                                backgroundColor: reviewDecision === 'reject' ? '#FEE2E2' : '#FFFFFF',
                                cursor: 'pointer',
                                fontWeight: 700,
                                fontSize: '0.875rem',
                                color: reviewDecision === 'reject' ? '#991B1B' : 'var(--color-navy)',
                              }}
                            >
                              <input
                                type="radio"
                                name="reviewDecision"
                                value="reject"
                                checked={reviewDecision === 'reject'}
                                onChange={() => setReviewDecision('reject')}
                              />
                              Reject Proposal
                            </label>
                          </div>

                          <div style={{ marginBottom: '16px' }}>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
                              {reviewDecision === 'approve'
                                ? 'Admin Remarks / Notes (Optional):'
                                : reviewDecision === 'request_revision'
                                ? 'Revision Instructions for Department Official (Mandatory):'
                                : 'Formal Rejection Reason (Mandatory):'}
                            </label>
                            <textarea
                              rows={3}
                              value={reviewNotes}
                              onChange={(e) => setReviewNotes(e.target.value)}
                              placeholder={
                                reviewDecision === 'approve'
                                  ? 'e.g., Verified against gazette notification. Approved for citizen catalog.'
                                  : reviewDecision === 'request_revision'
                                  ? 'e.g., Please provide the updated portal link and upload the cabinet resolution reference.'
                                  : 'e.g., Duplicate scheme already exists in the national database.'
                              }
                              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                            />
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                            <button
                              type="button"
                              className="btn btn-secondary"
                              onClick={() => { setReviewModalOpen(false); setSelectedProposal(null); }}
                              disabled={reviewSubmitting}
                            >
                              Cancel
                            </button>
                            <button
                              type="button"
                              className="btn btn-primary"
                              onClick={handleReviewProposal}
                              disabled={reviewSubmitting}
                              style={{
                                backgroundColor: reviewDecision === 'approve' ? '#047857' : reviewDecision === 'request_revision' ? '#D97706' : '#DC2626',
                                borderColor: reviewDecision === 'approve' ? '#047857' : reviewDecision === 'request_revision' ? '#D97706' : '#DC2626',
                              }}
                            >
                              {reviewSubmitting ? 'Submitting...' : reviewDecision === 'approve' ? '✓ Approve & Publish Live' : reviewDecision === 'request_revision' ? '↩ Return for Revision' : '✕ Reject Proposal'}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Department Officials Management ────────────────────── */}
            {adminTab === 'officials' && (
              <div style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
                  <div>
                    <h3 style={{ margin: '0 0 6px 0', fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                      🏛️ Department Official Accounts & Decentralized Governance
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--color-text-secondary)', maxWidth: '780px' }}>
                      Provision and manage verified departmental nodal officers. Officials can submit scheme proposals, monitor citizen barrier analytics for their department, and respond to revision requests.
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button className="btn btn-secondary btn-sm" onClick={fetchOfficials} disabled={officialsLoading}>
                      ↺ {officialsLoading ? 'Refreshing...' : 'Refresh Officials'}
                    </button>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => setShowCreateOfficialModal(true)}
                      style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                    >
                      ➕ Provision Official
                    </button>
                  </div>
                </div>

                {/* Filters */}
                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder="Search by name, email, or identifier..."
                    value={officialSearch}
                    onChange={(e) => setOfficialSearch(e.target.value)}
                    style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem', minWidth: '280px' }}
                  />
                  <input
                    type="text"
                    placeholder="Filter by Department..."
                    value={officialDeptFilter}
                    onChange={(e) => setOfficialDeptFilter(e.target.value)}
                    style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem', minWidth: '220px' }}
                  />
                </div>

                {/* Officials Table */}
                {officialsLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>
                    Loading official accounts...
                  </div>
                ) : officials.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '48px', backgroundColor: '#F8FAFC', borderRadius: '8px', border: '1px dashed var(--color-border)' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🏛️</div>
                    <div style={{ fontWeight: 700, color: 'var(--color-navy)' }}>No department officials found</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                      Click "Provision Official" above to authorize department nodal officers.
                    </div>
                  </div>
                ) : (
                  <div style={{ overflowX: 'auto', border: '1px solid var(--color-border)', borderRadius: '8px' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)', textAlign: 'left' }}>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Official Name</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Username / Email</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Department</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Designation</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Scope</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                          <th style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)', textAlign: 'center' }}>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {officials.map((official, idx) => (
                          <tr
                            key={official.id || idx}
                            style={{
                              borderBottom: '1px solid var(--color-border)',
                              backgroundColor: idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA',
                            }}
                          >
                            <td style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-navy)' }}>
                              {official.full_name}
                            </td>
                            <td style={{ padding: '12px 16px', fontFamily: 'monospace', color: 'var(--color-text-secondary)', fontSize: '0.8125rem' }}>
                              {official.identifier || official.email}
                            </td>
                            <td style={{ padding: '12px 16px', color: 'var(--color-navy)', fontWeight: 600 }}>
                              {official.department || '—'}
                            </td>
                            <td style={{ padding: '12px 16px', color: 'var(--color-text-secondary)' }}>
                              {official.designation || 'Nodal Officer'}
                            </td>
                            <td style={{ padding: '12px 16px' }}>
                              <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, backgroundColor: '#E2E8F0', color: '#334155' }}>
                                {official.state_scope ? `State: ${official.state_scope}` : 'Central'}
                              </span>
                            </td>
                            <td style={{ padding: '12px 16px' }}>
                              <span
                                style={{
                                  padding: '3px 8px',
                                  borderRadius: '12px',
                                  fontSize: '0.75rem',
                                  fontWeight: 800,
                                  backgroundColor: official.is_active ? '#DCFCE7' : '#FEE2E2',
                                  color: official.is_active ? '#166534' : '#991B1B',
                                }}
                              >
                                {official.is_active ? 'Active' : 'Suspended'}
                              </span>
                            </td>
                            <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                              <button
                                type="button"
                                className="btn btn-sm"
                                onClick={() => handleToggleOfficialStatus(official)}
                                style={{
                                  fontSize: '0.75rem',
                                  padding: '4px 10px',
                                  borderRadius: '4px',
                                  backgroundColor: official.is_active ? '#FFF1F2' : '#ECFDF5',
                                  color: official.is_active ? '#BE123C' : '#047857',
                                  border: `1px solid ${official.is_active ? '#FECDD3' : '#A7F3D0'}`,
                                  fontWeight: 700,
                                  cursor: 'pointer',
                                }}
                              >
                                {official.is_active ? 'Suspend' : 'Activate'}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Provision Official Modal */}
                {showCreateOfficialModal && (
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
                        maxWidth: '560px',
                        width: '100%',
                        maxHeight: '90vh',
                        overflowY: 'auto',
                        padding: '28px',
                        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                        <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                          🏛️ Provision Department Official
                        </h3>
                        <button
                          type="button"
                          onClick={() => setShowCreateOfficialModal(false)}
                          style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: 'var(--color-text-muted)' }}
                        >
                          ✕
                        </button>
                      </div>

                      <form onSubmit={handleCreateOfficial}>
                        <div style={{ display: 'grid', gap: '14px' }}>
                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                              Full Name *
                            </label>
                            <input
                              type="text"
                              required
                              placeholder="e.g. Dr. Rajesh Verma"
                              value={officialForm.full_name}
                              onChange={(e) => setOfficialForm({ ...officialForm, full_name: e.target.value })}
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                            />
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                Username / Identifier *
                              </label>
                              <input
                                type="text"
                                required
                                placeholder="e.g. rverma.gov"
                                value={officialForm.identifier}
                                onChange={(e) => setOfficialForm({ ...officialForm, identifier: e.target.value })}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                Official Email
                              </label>
                              <input
                                type="email"
                                placeholder="rverma@nic.in"
                                value={officialForm.email}
                                onChange={(e) => setOfficialForm({ ...officialForm, email: e.target.value })}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                              />
                            </div>
                          </div>

                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                              Department / Ministry Name *
                            </label>
                            <input
                              type="text"
                              required
                              placeholder="e.g. Ministry of Agriculture & Farmers Welfare"
                              value={officialForm.department}
                              onChange={(e) => setOfficialForm({ ...officialForm, department: e.target.value })}
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                            />
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                Designation
                              </label>
                              <input
                                type="text"
                                placeholder="e.g. Nodal Officer / Joint Secretary"
                                value={officialForm.designation}
                                onChange={(e) => setOfficialForm({ ...officialForm, designation: e.target.value })}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                State Scope (Optional)
                              </label>
                              <input
                                type="text"
                                placeholder="e.g. DL, MH, UP (leave empty for Central)"
                                value={officialForm.state_scope}
                                onChange={(e) => setOfficialForm({ ...officialForm, state_scope: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                              />
                            </div>
                          </div>

                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                              Temporary Password * (Min 8 characters)
                            </label>
                            <input
                              type="password"
                              required
                              minLength={8}
                              placeholder="••••••••••••"
                              value={officialForm.password}
                              onChange={(e) => setOfficialForm({ ...officialForm, password: e.target.value })}
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                            />
                          </div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
                          <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => setShowCreateOfficialModal(false)}
                            disabled={officialFormSubmitting}
                          >
                            Cancel
                          </button>
                          <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={officialFormSubmitting}
                            style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                          >
                            {officialFormSubmitting ? 'Provisioning...' : 'Provision Account'}
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Multilingual Quality & Audio Assurance ───────────── */}
            {adminTab === 'i18n' && ("""

assert target_i18n_tab in content, "target_i18n_tab not found in DashboardPage.jsx"
content = content.replace(target_i18n_tab, proposals_and_officials_jsx)

with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("DashboardPage.jsx successfully updated with Proposals & Officials governance tabs!")
