import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import { Badge } from './Badge';

export function SchemeRequestsModal({
  isOpen,
  onClose,
  currentUser,
  onOpenScheme,
  initialTrackingId = '',
}) {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState(initialTrackingId ? 'track' : 'track');
  const [trackingInput, setTrackingInput] = useState(initialTrackingId);
  const [trackedRequest, setTrackedRequest] = useState(null);
  const [myRequests, setMyRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [createdTrackingId, setCreatedTrackingId] = useState(null);

  // Submit form state
  const [form, setForm] = useState({
    scheme_name: '',
    government_level: 'central',
    state_code: '',
    department_name: '',
    description: '',
    official_portal_url: '',
    citizen_contact: currentUser?.email || currentUser?.mobile || '',
  });

  useEffect(() => {
    if (initialTrackingId) {
      setTrackingInput(initialTrackingId);
      handleTrack(initialTrackingId);
    }
  }, [initialTrackingId]);

  useEffect(() => {
    if (isOpen && currentUser) {
      loadMyRequests();
    }
  }, [isOpen, currentUser]);

  const loadMyRequests = async () => {
    try {
      const data = await api.getMySchemeRequests(currentUser?.email || currentUser?.identifier);
      setMyRequests(data || []);
    } catch (_) {}
  };

  const handleTrack = async (idToTrack = null) => {
    const id = (idToTrack || trackingInput).trim();
    if (!id) return;
    setErrorMsg('');
    setLoading(true);
    setTrackedRequest(null);
    try {
      const res = await api.trackSchemeRequest(id);
      setTrackedRequest(res);
    } catch (err) {
      setErrorMsg(err.message || t('requests.notFound', 'No scheme request found with this ID.'));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');
    if (!form.scheme_name.trim()) {
      setErrorMsg('Please enter the scheme name.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.submitSchemeRequest({
        ...form,
        citizen_contact: form.citizen_contact || currentUser?.identifier || undefined,
      });
      setCreatedTrackingId(res.tracking_id);
      setTrackedRequest(res);
      setSuccessMsg(
        res.status === 'Already Exists'
          ? 'This scheme was already found in the catalogue!'
          : 'Scheme request submitted successfully.'
      );
      // Reset form
      setForm({
        scheme_name: '',
        government_level: 'central',
        state_code: '',
        department_name: '',
        description: '',
        official_portal_url: '',
        citizen_contact: currentUser?.email || currentUser?.mobile || '',
      });
      loadMyRequests();
    } catch (err) {
      setErrorMsg(err.message || 'Submission failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Request Received': return 'badge-status-received';
      case 'Under Review': return 'badge-status-review';
      case 'Information Needed': return 'badge-status-info';
      case 'Verified': return 'badge-status-verified';
      case 'Added to Catalogue': return 'badge-status-added';
      case 'Already Exists': return 'badge-status-exists';
      case 'Rejected': return 'badge-status-rejected';
      case 'Unable to Verify': return 'badge-status-unable';
      default: return 'badge-status-received';
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(16, 42, 67, 0.7)',
        zIndex: 1100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
        backdropFilter: 'blur(3px)',
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="scheme-requests-modal-title"
    >
      <div
        className="civic-card"
        style={{
          width: '100%',
          maxWidth: '680px',
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
          <div>
            <h2 id="scheme-requests-modal-title" style={{ margin: 0, fontSize: '1.2rem', color: '#FFFFFF' }}>
              📋 {t('requests.title', 'Scheme Requests & Tracking')}
            </h2>
            <div style={{ fontSize: '0.8rem', color: '#CBD5E1', marginTop: '2px' }}>
              Submit missing central or state schemes and track review progress in real time
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

        {/* Tab navigation */}
        <div style={{ display: 'flex', borderBottom: '1px solid var(--color-border)', backgroundColor: '#F8F9FA' }}>
          <button
            type="button"
            className={`gov-tab-btn ${activeTab === 'track' ? 'active' : ''}`}
            onClick={() => { setActiveTab('track'); setErrorMsg(''); setSuccessMsg(''); }}
            style={{ flex: 1, padding: '12px', border: 'none', fontWeight: 600, cursor: 'pointer', borderBottom: activeTab === 'track' ? '3px solid var(--color-teal)' : 'none' }}
          >
            🔍 {t('requests.trackRequest', 'Track Request')}
          </button>
          <button
            type="button"
            className={`gov-tab-btn ${activeTab === 'submit' ? 'active' : ''}`}
            onClick={() => { setActiveTab('submit'); setErrorMsg(''); setSuccessMsg(''); setCreatedTrackingId(null); }}
            style={{ flex: 1, padding: '12px', border: 'none', fontWeight: 600, cursor: 'pointer', borderBottom: activeTab === 'submit' ? '3px solid var(--color-teal)' : 'none' }}
          >
            ➕ {t('requests.submitRequest', 'Submit Missing Scheme')}
          </button>
          {currentUser && (
            <button
              type="button"
              className={`gov-tab-btn ${activeTab === 'my' ? 'active' : ''}`}
              onClick={() => { setActiveTab('my'); loadMyRequests(); setErrorMsg(''); setSuccessMsg(''); }}
              style={{ flex: 1, padding: '12px', border: 'none', fontWeight: 600, cursor: 'pointer', borderBottom: activeTab === 'my' ? '3px solid var(--color-teal)' : 'none' }}
            >
              📂 {t('requests.myRequestsTitle', 'My Requests')} ({myRequests.length})
            </button>
          )}
        </div>

        {/* Content body */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
          {errorMsg && (
            <div style={{ color: '#991B1B', backgroundColor: '#FEE2E2', border: '1px solid #FCA5A5', padding: '10px 14px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.875rem' }}>
              ⚠️ {errorMsg}
            </div>
          )}

          {successMsg && (
            <div style={{ color: '#166534', backgroundColor: '#DCFCE7', border: '1px solid #86EFAC', padding: '10px 14px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.875rem' }}>
              ✓ {successMsg}
            </div>
          )}

          {/* TAB 1: TRACK REQUEST */}
          {activeTab === 'track' && (
            <div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <input
                  type="text"
                  className="form-control"
                  placeholder={t('requests.trackPlaceholder', 'Enter Tracking ID e.g. REQ-2026-ABC123')}
                  value={trackingInput}
                  onChange={(e) => setTrackingInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleTrack()}
                  style={{ textTransform: 'uppercase' }}
                />
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => handleTrack()}
                  disabled={loading || !trackingInput.trim()}
                >
                  {loading ? 'Tracking...' : 'Search'}
                </button>
              </div>

              {trackedRequest && (
                <div
                  style={{
                    border: '1px solid var(--color-border)',
                    borderRadius: '8px',
                    padding: '16px',
                    backgroundColor: '#FFFFFF',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                    <div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                        {t('requests.trackingId', 'Tracking ID')}: <strong>{trackedRequest.tracking_id}</strong>
                      </div>
                      <h3 style={{ margin: '4px 0', fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                        {trackedRequest.scheme_name}
                      </h3>
                      <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                        {trackedRequest.government_level.toUpperCase()}
                        {trackedRequest.state_code ? ` · ${trackedRequest.state_code}` : ''}
                        {trackedRequest.department_name ? ` · ${trackedRequest.department_name}` : ''}
                      </div>
                    </div>

                    <span
                      className={`badge ${getStatusBadgeClass(trackedRequest.status)}`}
                      style={{ padding: '6px 12px', fontSize: '0.875rem', fontWeight: 600, borderRadius: '20px' }}
                    >
                      {trackedRequest.status}
                    </span>
                  </div>

                  {/* Submission date & timestamps */}
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '12px' }}>
                    {t('requests.submittedOn', 'Submitted on')}: {new Date(trackedRequest.created_at).toLocaleString()}
                    {trackedRequest.reviewed_at && (
                      <span> · Last reviewed: {new Date(trackedRequest.reviewed_at).toLocaleString()}</span>
                    )}
                  </div>

                  {/* Status explanation */}
                  <div
                    style={{
                      padding: '12px',
                      backgroundColor: 'var(--color-teal-light)',
                      border: '1px solid var(--color-teal)',
                      borderRadius: '6px',
                      marginBottom: '12px',
                      fontSize: '0.875rem',
                    }}
                  >
                    <strong>Status Meaning: </strong>
                    {trackedRequest.status === 'Request Received' && 'Your request has been securely stored on the server and is in the ingestion backlog.'}
                    {trackedRequest.status === 'Under Review' && 'An administrator is verifying the scheme details against official notifications.'}
                    {trackedRequest.status === 'Information Needed' && 'Additional official gazette or portal links are required to confirm this scheme.'}
                    {trackedRequest.status === 'Verified' && 'Scheme has been confirmed using an authoritative government source.'}
                    {trackedRequest.status === 'Added to Catalogue' && 'This scheme record exists in the database and is searchable in the live catalogue!'}
                    {trackedRequest.status === 'Already Exists' && 'This scheme is already present in the NagrikSaarathi catalogue.'}
                    {trackedRequest.status === 'Rejected' && 'The request could not be accepted as an official government welfare scheme.'}
                    {trackedRequest.status === 'Unable to Verify' && 'Available evidence was insufficient to confirm the scheme.'}
                  </div>

                  {/* Admin notes if present */}
                  {trackedRequest.admin_notes && (
                    <div style={{ marginBottom: '10px', fontSize: '0.875rem' }}>
                      <strong>{t('requests.adminNotes', 'Official Review Notes')}:</strong> {trackedRequest.admin_notes}
                    </div>
                  )}

                  {/* Rejection reason if present */}
                  {trackedRequest.rejection_reason && (
                    <div style={{ marginBottom: '10px', fontSize: '0.875rem', color: '#991B1B' }}>
                      <strong>{t('requests.rejectionReason', 'Rejection Explanation')}:</strong> {trackedRequest.rejection_reason}
                    </div>
                  )}

                  {/* Link to catalogue if Added to Catalogue or Already Exists */}
                  {(trackedRequest.status === 'Added to Catalogue' || trackedRequest.status === 'Already Exists') && trackedRequest.linked_scheme_id && (
                    <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--color-border)' }}>
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => {
                          onClose();
                          if (onOpenScheme) onOpenScheme(trackedRequest.linked_scheme_id);
                        }}
                      >
                        🚀 {t('requests.viewDetail', 'Open Scheme in Catalogue')} →
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: SUBMIT MISSING SCHEME */}
          {activeTab === 'submit' && (
            <div>
              {createdTrackingId ? (
                <div style={{ textAlign: 'center', padding: '24px 16px' }}>
                  <div style={{ fontSize: '3rem', marginBottom: '8px' }}>🎉</div>
                  <h3 style={{ color: 'var(--color-navy)', marginBottom: '8px' }}>Scheme Request Stored!</h3>
                  <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px' }}>
                    {t('requests.requestSubmitted', 'Please save your unique Tracking ID to check status at any time:')}
                  </p>
                  <div
                    style={{
                      display: 'inline-block',
                      backgroundColor: 'var(--color-surface-subtle)',
                      border: '2px dashed var(--color-teal)',
                      padding: '10px 24px',
                      borderRadius: '8px',
                      fontSize: '1.25rem',
                      fontWeight: 700,
                      color: 'var(--color-teal-dark)',
                      letterSpacing: '1px',
                      marginBottom: '20px',
                    }}
                  >
                    {createdTrackingId}
                  </div>
                  <div>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => {
                        setActiveTab('track');
                        setTrackingInput(createdTrackingId);
                        handleTrack(createdTrackingId);
                      }}
                    >
                      View Live Status Timeline
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('requests.schemeName', 'Scheme Name')} *
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. Mukhyamantri Yuva Sambal Yojana"
                      value={form.scheme_name}
                      onChange={(e) => setForm({ ...form, scheme_name: e.target.value })}
                      required
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                    <div>
                      <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                        {t('requests.governmentLevel', 'Government Level')}
                      </label>
                      <select
                        className="form-control"
                        value={form.government_level}
                        onChange={(e) => setForm({ ...form, government_level: e.target.value })}
                      >
                        <option value="central">Central Government</option>
                        <option value="state">State Government</option>
                        <option value="ut">Union Territory</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                        {t('requests.state', 'State / UT Code (e.g. MH, DL, RJ)')}
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="e.g. RJ"
                        maxLength={5}
                        value={form.state_code}
                        onChange={(e) => setForm({ ...form, state_code: e.target.value.toUpperCase() })}
                      />
                    </div>
                  </div>

                  <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('requests.department', 'Department / Ministry (if known)')}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. Department of Employment & Training"
                      value={form.department_name}
                      onChange={(e) => setForm({ ...form, department_name: e.target.value })}
                    />
                  </div>

                  <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('requests.officialUrl', 'Official Portal or Gazette URL (if known)')}
                    </label>
                    <input
                      type="url"
                      className="form-control"
                      placeholder="https://..."
                      value={form.official_portal_url}
                      onChange={(e) => setForm({ ...form, official_portal_url: e.target.value })}
                    />
                  </div>

                  <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('requests.contact', 'Your Email or 10-digit Mobile (for tracking notifications)')}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. citizen@example.in or 9876543210"
                      value={form.citizen_contact}
                      onChange={(e) => setForm({ ...form, citizen_contact: e.target.value })}
                    />
                  </div>

                  <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('requests.description', 'Scheme Details / Description')}
                    </label>
                    <textarea
                      className="form-control"
                      rows={3}
                      placeholder="Describe what assistance or benefits this scheme provides..."
                      value={form.description}
                      onChange={(e) => setForm({ ...form, description: e.target.value })}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                    <button type="button" className="btn btn-secondary" onClick={onClose}>
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                      {loading ? 'Submitting...' : 'Submit Scheme Request'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* TAB 3: MY REQUESTS (Logged-in citizen) */}
          {activeTab === 'my' && (
            <div>
              {myRequests.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--color-text-muted)' }}>
                  You have not submitted any missing scheme requests yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {myRequests.map((req) => (
                    <div
                      key={req.id}
                      style={{
                        padding: '12px 16px',
                        border: '1px solid var(--color-border)',
                        borderRadius: '6px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        flexWrap: 'wrap',
                        gap: '8px',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-teal-dark)', fontWeight: 600 }}>
                          {req.tracking_id}
                        </div>
                        <div style={{ fontWeight: 600, color: 'var(--color-navy)' }}>
                          {req.scheme_name}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                          {new Date(req.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span className={`badge ${getStatusBadgeClass(req.status)}`} style={{ fontSize: '0.75rem' }}>
                          {req.status}
                        </span>
                        <button
                          type="button"
                          className="btn btn-sm btn-secondary"
                          onClick={() => {
                            setActiveTab('track');
                            setTrackingInput(req.tracking_id);
                            handleTrack(req.tracking_id);
                          }}
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
