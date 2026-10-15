import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';

export function HelpSupportModal({
  isOpen,
  onClose,
  currentUser,
  currentSchemeName = '',
  currentPageRef = '',
  initialCategory = 'other',
}) {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('new'); // 'new' | 'track' | 'my'
  const [category, setCategory] = useState(initialCategory);
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [contact, setContact] = useState(currentUser?.email || currentUser?.mobile || '');
  const [citizenName, setCitizenName] = useState(currentUser?.full_name || '');
  const [pageRef, setPageRef] = useState(currentPageRef || currentSchemeName || '');

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [createdTicket, setCreatedTicket] = useState(null);

  // Track ticket state
  const [ticketInput, setTicketInput] = useState('');
  const [trackedTicket, setTrackedTicket] = useState(null);
  const [myTickets, setMyTickets] = useState([]);
  const [feedbackNotes, setFeedbackNotes] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  useEffect(() => {
    if (currentPageRef || currentSchemeName) {
      setPageRef(currentPageRef || currentSchemeName);
    }
  }, [currentPageRef, currentSchemeName]);

  useEffect(() => {
    if (isOpen && currentUser) {
      loadMyTickets();
    }
  }, [isOpen, currentUser]);

  const loadMyTickets = async () => {
    try {
      const data = await api.getMyHelpTickets(currentUser?.email || currentUser?.identifier);
      setMyTickets(data || []);
    } catch (_) {}
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!contact.trim()) {
      setErrorMsg('Please enter your email address or mobile number.');
      return;
    }
    if (!subject.trim()) {
      setErrorMsg('Please enter a brief subject.');
      return;
    }
    if (!description.trim() || description.trim().length < 10) {
      setErrorMsg('Please provide a description of at least 10 characters.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.createHelpTicket({
        citizen_name: citizenName.trim() || undefined,
        citizen_contact: contact.trim(),
        category,
        subject: subject.trim(),
        description: description.trim(),
        page_or_scheme_ref: pageRef.trim() || undefined,
      });

      setCreatedTicket(res);
      setTrackedTicket(res);
      setSuccessMsg('Your support ticket has been received and stored securely.');
      loadMyTickets();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to submit help ticket.');
    } finally {
      setLoading(false);
    }
  };

  const handleTrack = async (numToTrack = null) => {
    const num = (numToTrack || ticketInput).trim();
    if (!num) return;
    setErrorMsg('');
    setLoading(true);
    setTrackedTicket(null);
    setFeedbackSubmitted(false);
    try {
      const res = await api.trackHelpTicket(num);
      setTrackedTicket(res);
    } catch (err) {
      setErrorMsg(err.message || 'Ticket not found.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (solved, reopen = false) => {
    if (!trackedTicket) return;
    setLoading(true);
    setErrorMsg('');
    try {
      const updated = await api.submitTicketFeedback(trackedTicket.ticket_number, {
        satisfaction_solved: solved,
        feedback_notes: feedbackNotes.trim() || undefined,
        reopen: reopen,
      });
      setTrackedTicket(updated);
      setFeedbackSubmitted(true);
      setFeedbackNotes('');
      loadMyTickets();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to record feedback.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getStatusColor = (status) => {
    switch (status) {
      case 'Received': return '#64748B';
      case 'Open': return '#0284C7';
      case 'In Progress': return '#D97706';
      case 'Waiting for Citizen': return '#7C3AED';
      case 'Resolved': return '#16A34A';
      case 'Closed': return '#475569';
      default: return '#64748B';
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
      aria-labelledby="help-support-modal-title"
    >
      <div
        className="civic-card"
        style={{
          width: '100%',
          maxWidth: '640px',
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
            <h2 id="help-support-modal-title" style={{ margin: 0, fontSize: '1.2rem', color: '#FFFFFF' }}>
              ❓ {t('help.title', 'Citizen Help & Support Desk')}
            </h2>
            <div style={{ fontSize: '0.8rem', color: '#CBD5E1', marginTop: '2px' }}>
              Structured assistance with translation, forms, links, and technical barriers
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
            className={`gov-tab-btn ${activeTab === 'new' ? 'active' : ''}`}
            onClick={() => { setActiveTab('new'); setErrorMsg(''); setSuccessMsg(''); }}
            style={{ flex: 1, padding: '12px', border: 'none', fontWeight: 600, cursor: 'pointer', borderBottom: activeTab === 'new' ? '3px solid var(--color-teal)' : 'none' }}
          >
            ✍️ {t('help.needHelp', 'Request Help')}
          </button>
          <button
            type="button"
            className={`gov-tab-btn ${activeTab === 'track' ? 'active' : ''}`}
            onClick={() => { setActiveTab('track'); setErrorMsg(''); setSuccessMsg(''); }}
            style={{ flex: 1, padding: '12px', border: 'none', fontWeight: 600, cursor: 'pointer', borderBottom: activeTab === 'track' ? '3px solid var(--color-teal)' : 'none' }}
          >
            🔍 {t('help.ticketNumber', 'Track Ticket')}
          </button>
          {currentUser && (
            <button
              type="button"
              className={`gov-tab-btn ${activeTab === 'my' ? 'active' : ''}`}
              onClick={() => { setActiveTab('my'); loadMyTickets(); setErrorMsg(''); setSuccessMsg(''); }}
              style={{ flex: 1, padding: '12px', border: 'none', fontWeight: 600, cursor: 'pointer', borderBottom: activeTab === 'my' ? '3px solid var(--color-teal)' : 'none' }}
            >
              📁 {t('help.myTicketsTitle', 'My Tickets')} ({myTickets.length})
            </button>
          )}
        </div>

        {/* Body */}
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

          {/* TAB 1: NEW TICKET */}
          {activeTab === 'new' && (
            <div>
              {createdTicket ? (
                <div style={{ textAlign: 'center', padding: '24px 16px' }}>
                  <div style={{ fontSize: '3rem', marginBottom: '8px' }}>🎫</div>
                  <h3 style={{ color: 'var(--color-navy)', marginBottom: '8px' }}>Help Ticket Stored!</h3>
                  <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px' }}>
                    {t('help.ticketCreated', 'Your support ticket has been registered. Please note your Ticket Number:')}
                  </p>
                  <div
                    style={{
                      display: 'inline-block',
                      backgroundColor: 'var(--color-surface-subtle)',
                      border: '2px dashed var(--color-teal)',
                      padding: '10px 24px',
                      borderRadius: '8px',
                      fontSize: '1.3rem',
                      fontWeight: 700,
                      color: 'var(--color-teal-dark)',
                      letterSpacing: '1px',
                      marginBottom: '20px',
                    }}
                  >
                    {createdTicket.ticket_number}
                  </div>
                  <div>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => {
                        setActiveTab('track');
                        setTicketInput(createdTicket.ticket_number);
                        handleTrack(createdTicket.ticket_number);
                      }}
                    >
                      Track Ticket Resolution
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('help.category', 'Category')} *
                    </label>
                    <select
                      className="form-control"
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      required
                    >
                      <option value="translation">Translation / Language Issue</option>
                      <option value="guided_form_difficulty">Guided-Form Difficulty</option>
                      <option value="eligibility_confusion">Eligibility Rules Confusion</option>
                      <option value="missing_scheme">Missing Government Scheme</option>
                      <option value="incorrect_official_link">Broken or Incorrect Official Portal Link</option>
                      <option value="technical_error">Technical Error / Page Crash</option>
                      <option value="other">Other Inquiry</option>
                    </select>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                    <div>
                      <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                        Your Full Name
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="e.g. Aarav Sharma"
                        value={citizenName}
                        onChange={(e) => setCitizenName(e.target.value)}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                        {t('help.contact', 'Contact Email or 10-digit Mobile')} *
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="e.g. aarav@example.in or 9876543210"
                        value={contact}
                        onChange={(e) => setContact(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('help.subject', 'Subject')} *
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Brief summary of what you need assistance with"
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                      required
                    />
                  </div>

                  <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      Related Scheme or Page Reference (optional)
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. PM-KISAN, Step 3, or https://..."
                      value={pageRef}
                      onChange={(e) => setPageRef(e.target.value)}
                    />
                  </div>

                  <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>
                      {t('help.description', 'Detailed Description')} *
                    </label>
                    <textarea
                      className="form-control"
                      rows={4}
                      placeholder="Please explain the barrier or problem you encountered so our support staff can resolve it effectively..."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      required
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                    <button type="button" className="btn btn-secondary" onClick={onClose}>
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                      {loading ? 'Submitting...' : t('help.submit', 'Submit Support Request')}
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* TAB 2: TRACK TICKET */}
          {activeTab === 'track' && (
            <div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter Ticket Number e.g. TKT-2026-ABC123"
                  value={ticketInput}
                  onChange={(e) => setTicketInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleTrack()}
                  style={{ textTransform: 'uppercase' }}
                />
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => handleTrack()}
                  disabled={loading || !ticketInput.trim()}
                >
                  {loading ? 'Searching...' : 'Track'}
                </button>
              </div>

              {trackedTicket && (
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
                        Ticket: <strong>{trackedTicket.ticket_number}</strong> · Category: {trackedTicket.category}
                      </div>
                      <h3 style={{ margin: '4px 0', fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                        {trackedTicket.subject}
                      </h3>
                    </div>

                    <span
                      style={{
                        padding: '4px 12px',
                        borderRadius: '20px',
                        color: '#FFFFFF',
                        backgroundColor: getStatusColor(trackedTicket.status),
                        fontSize: '0.8125rem',
                        fontWeight: 600,
                      }}
                    >
                      {trackedTicket.status}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '12px' }}>
                    Submitted: {new Date(trackedTicket.created_at).toLocaleString()}
                    {trackedTicket.resolved_at && (
                      <span> · Resolved: {new Date(trackedTicket.resolved_at).toLocaleString()}</span>
                    )}
                  </div>

                  <div style={{ backgroundColor: '#F8F9FA', padding: '12px', borderRadius: '6px', fontSize: '0.875rem', marginBottom: '14px' }}>
                    <strong>Your Description:</strong>
                    <div style={{ marginTop: '4px', whiteSpace: 'pre-wrap' }}>{trackedTicket.description}</div>
                  </div>

                  {/* Resolution Section */}
                  {trackedTicket.resolution_message && (
                    <div
                      style={{
                        padding: '14px',
                        backgroundColor: '#F0FDF4',
                        border: '1px solid #BBF7D0',
                        borderRadius: '6px',
                        marginBottom: '16px',
                      }}
                    >
                      <div style={{ fontWeight: 700, color: '#166534', marginBottom: '6px' }}>
                        ✓ {t('help.resolution', 'Official Resolution')}:
                      </div>
                      <div style={{ fontSize: '0.9rem', color: '#14532D', whiteSpace: 'pre-wrap' }}>
                        {trackedTicket.resolution_message}
                      </div>
                    </div>
                  )}

                  {/* Resolution Feedback Question (Requirement 4) */}
                  {trackedTicket.status === 'Resolved' && (
                    <div
                      style={{
                        padding: '14px',
                        backgroundColor: 'var(--color-surface-subtle)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '6px',
                        marginTop: '12px',
                      }}
                    >
                      {feedbackSubmitted || trackedTicket.satisfaction_solved !== null ? (
                        <div style={{ color: '#166534', fontWeight: 600, fontSize: '0.875rem' }}>
                          ✓ {t('help.feedbackRecorded', 'Thank you! Your feedback has been recorded.')}
                          {trackedTicket.satisfaction_solved === true ? ' (Marked as problem resolved)' : ' (Marked as needing further assistance)'}
                        </div>
                      ) : (
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-navy)', marginBottom: '8px' }}>
                            {t('help.didThisSolve', 'Did this solution resolve your problem?')}
                          </div>

                          <textarea
                            className="form-control"
                            rows={2}
                            placeholder="Optional notes or feedback..."
                            value={feedbackNotes}
                            onChange={(e) => setFeedbackNotes(e.target.value)}
                            style={{ marginBottom: '10px' }}
                          />

                          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                            <button
                              type="button"
                              className="btn btn-primary btn-sm"
                              onClick={() => handleFeedback(true, false)}
                              disabled={loading}
                            >
                              ✓ {t('help.yes', 'Yes, Problem Solved')}
                            </button>

                            <button
                              type="button"
                              className="btn btn-secondary btn-sm"
                              onClick={() => handleFeedback(false, true)}
                              disabled={loading}
                              style={{ color: '#991B1B', borderColor: '#FCA5A5' }}
                            >
                              ✕ {t('help.noReopen', 'No, I Need Further Help (Reopen)')}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Status Timeline History */}
                  {trackedTicket.history && trackedTicket.history.length > 0 && (
                    <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--color-border)' }}>
                      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '8px', textTransform: 'uppercase' }}>
                        Activity Log
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {trackedTicket.history.map((h, i) => (
                          <div key={i} style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                            • {new Date(h.timestamp).toLocaleTimeString()}: {h.details} ({h.actor})
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: MY TICKETS */}
          {activeTab === 'my' && (
            <div>
              {myTickets.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--color-text-muted)' }}>
                  You have not submitted any help tickets yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {myTickets.map((tkt) => (
                    <div
                      key={tkt.id}
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
                          {tkt.ticket_number} · {tkt.category}
                        </div>
                        <div style={{ fontWeight: 600, color: 'var(--color-navy)' }}>
                          {tkt.subject}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                          {new Date(tkt.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span
                          style={{
                            padding: '3px 8px',
                            borderRadius: '12px',
                            color: '#FFFFFF',
                            backgroundColor: getStatusColor(tkt.status),
                            fontSize: '0.75rem',
                            fontWeight: 600,
                          }}
                        >
                          {tkt.status}
                        </span>
                        <button
                          type="button"
                          className="btn btn-sm btn-secondary"
                          onClick={() => {
                            setActiveTab('track');
                            setTicketInput(tkt.ticket_number);
                            handleTrack(tkt.ticket_number);
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
