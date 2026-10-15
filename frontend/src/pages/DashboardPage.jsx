import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import { Badge } from '../components/Badge';
import { SpeechService } from '../services/speech';

export function DashboardPage({ currentUser, onOpenTracking }) {
  const { t } = useTranslation();

  // Filters & Auth
  const isOfficial = currentUser?.role === 'official';
  const [includeDemo, setIncludeDemo] = useState(!isOfficial);
  const [adminKey, setAdminKey] = useState('');
  const [authApplied, setAuthApplied] = useState(false);

  // Analytics Data
  const [summary, setSummary] = useState(null);
  const [barriers, setBarriers] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [fields, setFields] = useState([]);
  const [recovery, setRecovery] = useState(null);
  const [translations, setTranslations] = useState(null);
  const [coverage, setCoverage] = useState(null);
  const [radarData, setRadarData] = useState(null);
  const [radarExpanded, setRadarExpanded] = useState(false);

  // Coverage UI
  const [coverageSearch, setCoverageSearch] = useState('');
  const [coverageTab, setCoverageTab] = useState('all'); // 'all' | 'state' | 'ut' | 'central'

  // Admin Panel State
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
  });

  // Controlled Official Invitations State (Priority 1)
  const [invitations, setInvitations] = useState([]);
  const [invLoading, setInvLoading] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    full_name: '',
    department_name: '',
    state_scope: '',
    expires_in_days: 7,
  });

  // Scheme Rule Change Radar Review Queue (Priority 2)
  const [radarRecords, setRadarRecords] = useState([]);
  const [radarLoading, setRadarLoading] = useState(false);
  const [selectedRadar, setSelectedRadar] = useState(null);
  const [radarReviewModal, setRadarReviewModal] = useState(false);
  const [radarDecision, setRadarDecision] = useState('approve');
  const [radarReviewNotes, setRadarReviewNotes] = useState('');
  const [radarSubmitting, setRadarSubmitting] = useState(false);

  // Evidence Verification Queue (Priority 4)
  const [evidenceList, setEvidenceList] = useState([]);
  const [evidenceLoading, setEvidenceLoading] = useState(false);

  // Translation Drift Monitor (Priority 5)
  const [driftAlerts, setDriftAlerts] = useState([]);
  const [driftLoading, setDriftLoading] = useState(false);

  // Citizen Difficulty Heatmap (Priority 3)
  const [heatmapData, setHeatmapData] = useState(null);
  const [heatmapLoading, setHeatmapLoading] = useState(false);
  const [heatmapDays, setHeatmapDays] = useState('30');
  const [heatmapDept, setHeatmapDept] = useState('');

  const handleTestAudio = async (langCode, langName) => {
    SpeechService.stopSpeaking();
    setTestingVoiceCode(langCode);
    setVoiceTestResult(null);

    const testPhrases = {
      bn: 'নাগরিক সারথী সরকারি পরিষেবা সহায়তা প্ল্যাটফর্মে আপনাকে স্বাগতম।',
      hi: 'नागरिक सारथी सरकारी सेवा सहायता पोर्टल में आपका स्वागत है।',
      ta: 'நாகரிக் சாரதி அரசு சேவை உதவி தளத்திற்கு வரவேற்கிறோம்.',
      te: 'నాగరిక్ సారథి ప్రభుత్వ సేవా సహాయ పోర్టల్‌కు స్వాగతం.',
      mr: 'नागरिक सारथी शासकीय सेवा सहाय्य पोर्टलवर आपले स्वागत आहे.',
      gu: 'નાગરિક સારથિ સરકારી સેવા સહાય પોર્ટલ પર આપનું સ્વાગત છે.',
      kn: 'ನಾಗರಿಕ್ ಸಾರಥಿ ಸರ್ಕಾರಿ ಸೇವಾ ಸಹಾಯ ಪೋರ್ಟಲ್‌ಗೆ ಸುಸ್ವಾಗತ.',
      ml: 'നാഗരിക് സാരഥി സർക്കാർ സേവന സഹായ പോർട്ടലിലേക്ക് സ്വാഗതം.',
      pa: 'ਨਾਗਰਿਕ ਸਾਰਥੀ ਸਰਕਾਰੀ ਸੇਵਾ ਸਹਾਇਤਾ ਪੋਰਟਲ \'ਤੇ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ।',
      ur: 'ناگرک سارتھی سرکاری خدمات کے پورٹل میں خوش آمدید۔',
      ne: 'नागरिक सारथी सरकारी सेवा सहायता पोर्टलमा यहाँलाई स्वागत छ।',
      en: 'Welcome to NagrikSaarathi citizen public service assistance portal.',
    };

    const text = testPhrases[langCode] || `Welcome to NagrikSaarathi assistance for ${langName}.`;

    try {
      const ok = await SpeechService.speakGuidance({
        text,
        languageCode: langCode,
        onStart: (info) => {
          setVoiceTestResult({ type: 'success', msg: `🔊 Playing ${langName} audio (${info.voiceName || info.source})` });
        },
        onEnd: () => {
          setTestingVoiceCode(null);
        },
        onError: (err, details) => {
          setTestingVoiceCode(null);
          if (err === 'VOICE_UNAVAILABLE') {
            setVoiceTestResult({
              type: 'warning',
              msg: details?.reason || `${langName}: Speech synthesis voice unavailable. Showing full written instructions.`,
            });
          } else {
            setVoiceTestResult({ type: 'error', msg: typeof err === 'string' ? err : 'Speech playback error' });
          }
        },
      });
      if (!ok) {
        setTestingVoiceCode(null);
      }
    } catch (err) {
      setTestingVoiceCode(null);
      setVoiceTestResult({ type: 'error', msg: err.message });
    }
  };

  // UI state
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setErrorMsg(null);
    const keyToUse = adminKey.trim() || null;

    try {
      const [sumRes, barRes, langRes, fieldRes, recRes, transRes, covRes, radarRes] = await Promise.all([
        api.getDashboardSummary(includeDemo, keyToUse),
        api.getDashboardBarriers(includeDemo, keyToUse),
        api.getDashboardLanguages(includeDemo, keyToUse),
        api.getDashboardFields(includeDemo, keyToUse),
        api.getDashboardRecovery(includeDemo, keyToUse),
        api.getDashboardTranslationQuality(keyToUse),
        api.getDashboardCoverage(keyToUse).catch(() => null),
        api.getMissingSchemeRadar(keyToUse).catch(() => null),
      ]);

      setSummary(sumRes);
      setBarriers(barRes.items || []);
      setLanguages(langRes.items || []);
      setFields(fieldRes.items || []);
      setRecovery(recRes);
      setTranslations(transRes);
      setCoverage(covRes);
      setRadarData(radarRes);
    } catch (err) {
      if (err.status === 401) {
        setErrorMsg('अनधिकृत: लाइव विभागीय विश्लेषण के लिए अधिकृत API कुंजी की आवश्यकता है।');
      } else {
        setErrorMsg(`Failed to load analytics: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [includeDemo, authApplied]);

  // ── Admin Panel Data Fetchers ──────────────────────────────────────
  const fetchSchemeRequests = async () => {
    try {
      setSrLoading(true);
      const data = await api.getAdminSchemeRequests(srStatusFilter || null, adminKey.trim() || null);
      setSchemeRequests(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      setSchemeRequests([]);
    } finally {
      setSrLoading(false);
    }
  };

  const fetchHelpTickets = async () => {
    try {
      setHtLoading(true);
      const data = await api.getAdminHelpTickets(
        htCategoryFilter || null,
        htStatusFilter || null,
        adminKey.trim() || null,
      );
      setHelpTickets(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      setHelpTickets([]);
    } finally {
      setHtLoading(false);
    }
  };

  const fetchI18nAudit = async () => {
    try {
      setI18nLoading(true);
      const data = await api.getTranslationAudit(adminKey.trim() || null);
      setI18nAudit(data);
    } catch (err) {
      setI18nAudit(null);
    } finally {
      setI18nLoading(false);
    }
  };

  const fetchProposals = async () => {
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

  const fetchInvitations = async () => {
    try {
      setInvLoading(true);
      const data = await api.getAdminInvitations();
      setInvitations(Array.isArray(data) ? data : []);
    } catch (err) {
      setInvitations([]);
    } finally {
      setInvLoading(false);
    }
  };

  const handleCreateInvitationSubmit = async (e) => {
    e.preventDefault();
    if (!inviteForm.email.trim() || !inviteForm.full_name.trim() || !inviteForm.department_name.trim()) {
      setAdminActionMsg({ type: 'error', text: 'Email, full name, and department are required.' });
      return;
    }
    try {
      const res = await api.createAdminInvitation(inviteForm);
      setAdminActionMsg({
        type: 'success',
        text: `Official invitation created! Single-use token: ${res.invitation_token}`,
      });
      setShowInviteModal(false);
      setInviteForm({
        email: '',
        full_name: '',
        department_name: '',
        state_scope: '',
        expires_in_days: 7,
      });
      fetchInvitations();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Failed to issue invitation.' });
    }
  };

  const handleRevokeInvitationAction = async (id) => {
    const reason = window.prompt('Enter reason for revoking official invitation:', 'Administrator security discretion');
    if (!reason) return;
    try {
      await api.revokeAdminInvitation(id, reason);
      setAdminActionMsg({ type: 'success', text: `Invitation #${id} revoked.` });
      fetchInvitations();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Revocation failed.' });
    }
  };

  const fetchRadar = async () => {
    try {
      setRadarLoading(true);
      const data = await api.getAdminRadar();
      setRadarRecords(Array.isArray(data) ? data : []);
    } catch (err) {
      setRadarRecords([]);
    } finally {
      setRadarLoading(false);
    }
  };

  const handleRadarReviewSubmit = async (e) => {
    e.preventDefault();
    if (!selectedRadar) return;
    setRadarSubmitting(true);
    try {
      const res = await api.reviewAdminRadar(selectedRadar.id, {
        decision: radarDecision,
        review_notes: radarReviewNotes || undefined,
      });
      setAdminActionMsg({
        type: 'success',
        text: res.message || `Radar change set #${selectedRadar.id} marked as ${radarDecision}.`,
      });
      setRadarReviewModal(false);
      setSelectedRadar(null);
      setRadarReviewNotes('');
      fetchRadar();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Radar review failed.' });
    } finally {
      setRadarSubmitting(false);
    }
  };

  const fetchEvidence = async () => {
    try {
      setEvidenceLoading(true);
      const data = await api.getAdminEvidence();
      setEvidenceList(Array.isArray(data) ? data : []);
    } catch (err) {
      setEvidenceList([]);
    } finally {
      setEvidenceLoading(false);
    }
  };

  const handleVerifyEvidenceAction = async (id, approved) => {
    try {
      await api.verifyFieldEvidence(id, {
        approved,
        notes: approved ? 'Source verified by Administrator.' : 'Evidence rejected due to source mismatch.',
      });
      setAdminActionMsg({
        type: 'success',
        text: `Field evidence #${id} marked as ${approved ? 'Verified' : 'Rejected'}.`,
      });
      fetchEvidence();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Evidence verification failed.' });
    }
  };

  const fetchDrift = async () => {
    try {
      setDriftLoading(true);
      const data = await api.getAdminTranslationDrift();
      setDriftAlerts(Array.isArray(data) ? data : []);
    } catch (err) {
      setDriftAlerts([]);
    } finally {
      setDriftLoading(false);
    }
  };

  const handleReviewDriftAction = async (id, status) => {
    try {
      await api.reviewAdminTranslationDrift(id, {
        status,
        notes: `Marked as ${status} by Principal Administrator.`,
      });
      setAdminActionMsg({
        type: 'success',
        text: `Translation drift alert #${id} updated to ${status}.`,
      });
      fetchDrift();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Drift review failed.' });
    }
  };

  const fetchHeatmap = async () => {
    try {
      setHeatmapLoading(true);
      const data = await api.getAdminHeatmap({
        days: heatmapDays,
        department: heatmapDept || undefined,
      });
      setHeatmapData(data);
    } catch (err) {
      setHeatmapData(null);
    } finally {
      setHeatmapLoading(false);
    }
  };

  useEffect(() => {
    if (adminTab === 'requests') fetchSchemeRequests();
    else if (adminTab === 'tickets') fetchHelpTickets();
    else if (adminTab === 'proposals') fetchProposals();
    else if (adminTab === 'officials') fetchOfficials();
    else if (adminTab === 'i18n') fetchI18nAudit();
    else if (adminTab === 'invitations') fetchInvitations();
    else if (adminTab === 'radar') fetchRadar();
    else if (adminTab === 'evidence') fetchEvidence();
    else if (adminTab === 'drift') fetchDrift();
    else if (adminTab === 'heatmap') fetchHeatmap();
  }, [adminTab, srStatusFilter, htCategoryFilter, htStatusFilter, propStatusFilter, propTypeFilter, officialSearch, officialDeptFilter, authApplied, heatmapDays, heatmapDept]);

  const handleSchemeRequestAction = async (id, newStatus, reason = '') => {
    try {
      setAdminActionMsg(null);
      await api.updateAdminSchemeRequest(id, { status: newStatus, admin_notes: reason }, adminKey.trim() || null);
      setAdminActionMsg({ type: 'success', text: `Request #${id} updated to "${newStatus}"` });
      fetchSchemeRequests();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Update failed' });
    }
  };

  const handleHelpTicketAction = async (id, newStatus, resolution = '') => {
    try {
      setAdminActionMsg(null);
      await api.updateAdminHelpTicket(id, { status: newStatus, resolution_message: resolution }, adminKey.trim() || null);
      setAdminActionMsg({ type: 'success', text: `Ticket #${id} updated to "${newStatus}"` });
      fetchHelpTickets();
    } catch (err) {
      setAdminActionMsg({ type: 'error', text: err.message || 'Update failed' });
    }
  };

  const SR_STATUSES = ['Request Received','Under Review','Information Needed','Verified','Added to Catalogue','Already Exists','Rejected','Unable to Verify'];
  const HT_STATUSES = ['Received','Open','In Progress','Waiting for Citizen','Resolved','Closed'];
  const HT_CATEGORIES = ['translation','guided_form_difficulty','eligibility_confusion','missing_scheme','incorrect_official_link','technical_error','other'];

  return (
    <div className="civic-container" style={{ paddingTop: 'var(--space-xl)', paddingBottom: 'var(--space-3xl)' }}>
      {/* Editorial Dashboard Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: 'var(--space-xl)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            {includeDemo ? (
              <Badge variant="demo">{t('dashboard.simulatedBadge')}</Badge>
            ) : (
              <Badge variant="reviewed">{t('dashboard.realBadge')}</Badge>
            )}
            <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
              NagrikSaarathi Civic Intelligence Engine
            </span>
          </div>

          <h1 style={{ fontSize: '2rem', marginBottom: '4px' }}>{t('dashboard.title')}</h1>
          <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.9375rem' }}>
            {t('dashboard.subtitle')}
          </p>
        </div>

        {/* Filter & Admin Controls */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.875rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={includeDemo}
              onChange={(e) => setIncludeDemo(e.target.checked)}
            />
            <span>{t('dashboard.includeDemo')}</span>
          </label>

          <button className="btn btn-secondary btn-sm" onClick={fetchDashboardData} disabled={loading}>
            ↺ {t('dashboard.retry')}
          </button>
        </div>
      </div>

      {/* Admin Key Gate or Official Authenticated Banner */}
      {isOfficial ? (
        <div
          style={{
            backgroundColor: '#DCFCE7',
            border: '1px solid #86EFAC',
            borderLeft: '4px solid #16A34A',
            borderRadius: 'var(--border-radius)',
            padding: '12px 16px',
            marginBottom: 'var(--space-xl)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div style={{ fontSize: '0.875rem', color: '#14532D', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>🏛️</span>
            <span>
              <strong>प्रमाणित विभागीय सत्र:</strong> {currentUser.identifier} ({currentUser.department || 'सामान्य प्रशासन'})
            </span>
          </div>
          <div style={{ fontSize: '0.8125rem', color: '#166534', fontWeight: 600 }}>
            सत्यापित विभागीय अभिगम सक्रिय ✓
          </div>
        </div>
      ) : (
        <div
          style={{
            backgroundColor: 'var(--color-surface-subtle)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--border-radius)',
            padding: '12px 16px',
            marginBottom: 'var(--space-xl)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
            🔑 <strong>{t('dashboard.adminAuth')}</strong>: रियल प्रोडक्शन डेटा देखने के लिए विभागीय लॉगिन या एडमिन कुंजी दर्ज करें।
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <input
              type="password"
              className="form-control"
              style={{ width: '220px', padding: '6px 10px', fontSize: '0.8125rem' }}
              placeholder={t('dashboard.adminKeyPlaceholder')}
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
            />
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setAuthApplied((prev) => !prev)}
            >
              {t('dashboard.applyAuth')}
            </button>
          </div>
        </div>
      )}

      {/* Error / Loading notices */}
      {errorMsg && (
        <div
          style={{
            backgroundColor: 'var(--color-error-bg)',
            border: '1px solid var(--color-error-border)',
            padding: '12px var(--space-md)',
            borderRadius: 'var(--border-radius)',
            color: 'var(--color-error)',
            marginBottom: 'var(--space-xl)',
          }}
        >
          ⚠️ {errorMsg}
        </div>
      )}

      {loading && !summary && (
        <div style={{ textAlign: 'center', padding: 'var(--space-2xl)', color: 'var(--color-text-muted)' }}>
          {t('dashboard.loading')}
        </div>
      )}

      {/* Metrics Row */}
      {summary && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: 'var(--space-xl)' }}>
            <div className="civic-card" style={{ padding: '16px', marginBottom: 0 }}>
              <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                {t('dashboard.totalSessions')}
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-navy)', fontFamily: 'var(--font-serif)' }}>
                {summary.total_consented_sessions}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                सहमति आधारित सत्र (Consented)
              </div>
            </div>

            <div className="civic-card" style={{ padding: '16px', marginBottom: 0 }}>
              <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                {t('dashboard.completionRate')}
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-teal)', fontFamily: 'var(--font-serif)' }}>
                {summary.completion_rate_pct}%
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                {summary.completed_sessions} पूर्ण आवेदन
              </div>
            </div>

            <div className="civic-card" style={{ padding: '16px', marginBottom: 0 }}>
              <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                {t('dashboard.abandonmentRate')}
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-saffron-dark)', fontFamily: 'var(--font-serif)' }}>
                {summary.abandonment_rate_pct}%
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                {summary.abandoned_sessions} बीच में छूटे सत्र
              </div>
            </div>

            <div className="civic-card" style={{ padding: '16px', marginBottom: 0 }}>
              <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                {t('dashboard.humanAssistanceRequests')}
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-navy)', fontFamily: 'var(--font-serif)' }}>
                {summary.needs_human_help_sessions}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                डेस्क सहायता हेतु अनुरोध
              </div>
            </div>

            {recovery && (
              <div className="civic-card" style={{ padding: '16px', marginBottom: 0 }}>
                <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  {t('dashboard.recoveryRate')}
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-teal)', fontFamily: 'var(--font-serif)' }}>
                  {recovery.resolution_rate_pct}%
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                  {recovery.resolved_count} / {recovery.total_resolution_attempts} समाधान
                </div>
              </div>
            )}
          </div>

          {/* Analytical Charts Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '20px', marginBottom: 'var(--space-xl)' }}>
            {/* Barrier Breakdown Chart */}
            <div className="civic-card" style={{ marginBottom: 0 }}>
              <div className="civic-card-header">
                <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{t('dashboard.barrierBreakdown')}</h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', margin: 0 }}>
                  आवेदन प्रक्रिया में रुकावट डालने वाले प्रमुख कारण
                </p>
              </div>

              {barriers.length === 0 ? (
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>कोई बाधा दर्ज नहीं हुई।</p>
              ) : (
                <div className="chart-bar-container">
                  {barriers.map((b) => (
                    <div key={b.barrier_category} className="chart-bar-row">
                      <span className="chart-bar-label" title={b.barrier_category}>
                        {b.barrier_category.replace(/_/g, ' ')}
                      </span>
                      <div className="chart-bar-track">
                        <div
                          className="chart-bar-fill"
                          style={{ width: `${Math.min(b.percentage_of_barriers, 100)}%` }}
                        />
                      </div>
                      <span className="chart-bar-value">{b.count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Problematic Fields */}
            <div className="civic-card" style={{ marginBottom: 0 }}>
              <div className="civic-card-header">
                <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{t('dashboard.problematicFields')}</h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', margin: 0 }}>
                  वे फ़ील्ड जिनमें नागरिकों को सर्वाधिक सहायता अथवा त्रुटि का सामना करना पड़ा
                </p>
              </div>

              {fields.length === 0 ? (
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>कोई फ़ील्ड त्रुटि दर्ज नहीं।</p>
              ) : (
                <div className="chart-bar-container">
                  {fields.map((f) => (
                    <div key={f.field_key} className="chart-bar-row">
                      <span className="chart-bar-label" title={f.field_key}>
                        {f.field_key}
                      </span>
                      <div className="chart-bar-track">
                        <div
                          className="chart-bar-fill"
                          style={{
                            width: `${Math.min((f.issue_count / (fields[0]?.issue_count || 1)) * 100, 100)}%`,
                            backgroundColor: 'var(--color-saffron-dark)',
                          }}
                        />
                      </div>
                      <span className="chart-bar-value">{f.issue_count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Languages Breakdown Table */}
          <div className="civic-card">
            <div className="civic-card-header">
              <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{t('dashboard.languageBreakdown')}</h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', margin: 0 }}>
                22 आधिकारिक भाषाओं में सत्रों और बाधाओं का वितरण
              </p>
            </div>

            <table className="civic-table">
              <thead>
                <tr>
                  <th>भाषा (Language)</th>
                  <th>कोड</th>
                  <th>सत्र संख्या (Sessions)</th>
                  <th>बाधा घटनाएं (Barrier Events)</th>
                </tr>
              </thead>
              <tbody>
                {languages.map((l) => (
                  <tr key={l.language_code}>
                    <td>
                      <strong>{l.native_name}</strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginLeft: '6px' }}>
                        ({l.language_name})
                      </span>
                    </td>
                    <td><code>{l.language_code}</code></td>
                    <td>{l.session_count}</td>
                    <td>{l.barrier_event_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Translation Quality Audit */}
          {translations && (
            <div className="civic-card">
              <div className="civic-card-header">
                <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{t('dashboard.translationQuality')}</h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', margin: 0 }}>
                  22 भाषाओं में मानकीकृत समीक्षा स्थिति (Approved vs Reviewed vs Draft)
                </p>
              </div>

              <div style={{ display: 'flex', gap: '24px', marginBottom: '16px', fontSize: '0.875rem' }}>
                <div>कुल भाषाएं: <strong>{translations.total_configured_languages}</strong></div>
                <div>स्वीकृत अनुवाद: <strong style={{ color: 'var(--color-success)' }}>{translations.overall_approved_count}</strong></div>
                <div>समीक्षित अनुवाद: <strong style={{ color: 'var(--color-teal)' }}>{translations.overall_reviewed_count}</strong></div>
                <div>प्रारूप (ड्राफ्ट): <strong style={{ color: 'var(--color-saffron-dark)' }}>{translations.overall_draft_count}</strong></div>
              </div>

              <table className="civic-table">
                <thead>
                  <tr>
                    <th>भाषा</th>
                    <th>कवरेज</th>
                    <th>स्वीकृत (Approved)</th>
                    <th>समीक्षित (Reviewed)</th>
                    <th>प्रारूप (Draft)</th>
                  </tr>
                </thead>
                <tbody>
                  {translations.languages.map((tl) => (
                    <tr key={tl.language_code}>
                      <td><strong>{tl.native_name}</strong> ({tl.language_code})</td>
                      <td>{tl.coverage_pct}%</td>
                      <td>{tl.approved_count}</td>
                      <td>{tl.reviewed_count}</td>
                      <td>{tl.draft_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* ── Nationwide Scheme Coverage & Gaps ── */}
          {coverage && (
            <div className="civic-card" style={{ marginTop: 'var(--space-xl)' }}>
              <div className="civic-card-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <h3 style={{ fontSize: '1.2rem', margin: 0 }}>🗺️ Nationwide Scheme Coverage &amp; Gaps</h3>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                      {coverage.summary_note}
                    </p>
                  </div>
                </div>
              </div>

              {/* KPI cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', margin: '20px 0 24px' }}>
                {[
                  { label: 'Total Schemes', value: coverage.total_schemes_discovered, color: 'var(--color-navy)' },
                  { label: 'Central', value: coverage.central_schemes_count, color: 'var(--color-teal)' },
                  { label: 'State', value: coverage.state_schemes_count, color: 'var(--color-saffron-dark)' },
                  { label: 'UT', value: coverage.ut_schemes_count, color: '#7C3AED' },
                  { label: 'Verified URLs', value: coverage.verified_sources_count, color: 'var(--color-success)' },
                  { label: 'Missing URLs', value: coverage.missing_sources_count, color: 'var(--color-error)' },
                  { label: 'Needs Re-verify', value: coverage.needs_reverification_count, color: '#D97706' },
                  { label: 'States Covered', value: `${coverage.states_represented}/28`, color: coverage.all_28_states_covered ? 'var(--color-success)' : 'var(--color-error)' },
                  { label: 'UTs Covered', value: `${coverage.uts_represented}/8`, color: coverage.all_8_uts_covered ? 'var(--color-success)' : 'var(--color-error)' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="civic-card" style={{ padding: '12px 14px', marginBottom: 0, borderTop: `3px solid ${color}` }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>{label}</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 800, color, fontFamily: 'var(--font-serif)' }}>{value}</div>
                  </div>
                ))}
              </div>

              {/* Form-status breakdown */}
              <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '20px', fontSize: '0.875rem' }}>
                {Object.entries(coverage.form_status_breakdown || {}).map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{
                      display: 'inline-block', width: 10, height: 10, borderRadius: '50%',
                      background: k === 'VERIFIED_SCHEMA' ? 'var(--color-success)' : k === 'EXTRACTED_DRAFT' ? '#F59E0B' : '#94A3B8'
                    }} />
                    <span>{k}: <strong>{v}</strong></span>
                  </div>
                ))}
              </div>

              {/* Coverage Table */}
              <div style={{ display: 'flex', gap: '10px', marginBottom: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
                <input
                  type="text"
                  className="form-control"
                  style={{ maxWidth: 260, padding: '6px 10px', fontSize: '0.8125rem' }}
                  placeholder="Search state or UT…"
                  value={coverageSearch}
                  onChange={e => setCoverageSearch(e.target.value)}
                />
                {['all', 'state', 'ut'].map(tab => (
                  <button
                    key={tab}
                    className={`btn btn-sm ${coverageTab === tab ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setCoverageTab(tab)}
                  >
                    {tab === 'all' ? 'All (36)' : tab === 'state' ? 'States (28)' : 'UTs (8)'}
                  </button>
                ))}
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table className="civic-table">
                  <thead>
                    <tr>
                      <th>State / UT</th>
                      <th>Type</th>
                      <th>Total Schemes</th>
                      <th>✅ Verified URL</th>
                      <th>❌ Missing URL</th>
                      <th>📋 Form Ready</th>
                      <th>🏛️ Official State Portal</th>
                      <th>🌐 Citizen Services / e-District</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(coverage.state_ut_coverage || [])
                      .filter(row =>
                        (coverageTab === 'all' || row.jurisdiction_type === coverageTab) &&
                        row.state_name.toLowerCase().includes(coverageSearch.toLowerCase())
                      )
                      .map(row => (
                        <tr key={row.state_code}>
                          <td><strong>{row.state_name}</strong> <code style={{ fontSize: '0.75rem', marginLeft: 4 }}>{row.state_code}</code></td>
                          <td>
                            <span style={{
                              fontSize: '0.75rem', padding: '2px 7px', borderRadius: '9999px', fontWeight: 600,
                              background: row.jurisdiction_type === 'ut' ? '#EDE9FE' : '#DCFCE7',
                              color: row.jurisdiction_type === 'ut' ? '#6D28D9' : '#166534'
                            }}>
                              {row.jurisdiction_type === 'ut' ? 'UT' : 'State'}
                            </span>
                          </td>
                          <td style={{ fontWeight: 700 }}>{row.total_schemes}</td>
                          <td style={{ color: 'var(--color-success)', fontWeight: 600 }}>{row.verified_sources}</td>
                          <td style={{ color: row.missing_sources > 0 ? 'var(--color-error)' : 'var(--color-text-muted)' }}>{row.missing_sources}</td>
                          <td>
                            <span style={{
                              fontSize: '0.75rem', padding: '2px 7px', borderRadius: '9999px',
                              background: row.form_ready_count > 0 ? '#D1FAE5' : '#FEF3C7',
                              color: row.form_ready_count > 0 ? '#065F46' : '#92400E', fontWeight: 600
                            }}>
                              {row.form_ready_count > 0 ? `${row.form_ready_count} ready` : 'None'}
                            </span>
                          </td>
                          <td>
                            {row.official_portal_url ? (
                              <a
                                href={row.official_portal_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ fontSize: '0.8125rem', color: 'var(--color-navy)', textDecoration: 'underline', fontWeight: 600 }}
                                title={`Open official government portal for ${row.state_name}`}
                              >
                                🔗 {row.state_name}
                              </a>
                            ) : (
                              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>—</span>
                            )}
                          </td>
                          <td>
                            {row.official_services_url ? (
                              <a
                                href={row.official_services_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ fontSize: '0.8125rem', color: '#166534', textDecoration: 'underline', fontWeight: 600 }}
                                title={`Open official e-District/Services portal for ${row.state_name}`}
                              >
                                🏛️ Citizen Services
                              </a>
                            ) : (
                              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>

              {/* Methodology disclaimer */}
              <div style={{
                marginTop: 16, padding: '10px 14px', borderRadius: 'var(--border-radius)',
                background: 'var(--color-surface-subtle)', border: '1px solid var(--color-border)',
                fontSize: '0.8125rem', color: 'var(--color-text-muted)', lineHeight: 1.6
              }}>
                ⚠️ <strong>Transparency Note:</strong> {coverage.coverage_methodology_disclaimer}
              </div>
            </div>
          )}

          {/* ─── Missing Scheme Radar ─────────────────────────────────────────── */}
          {radarData && (
            <div
              style={{
                marginTop: 'var(--space-2xl)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--border-radius)',
                overflow: 'hidden',
              }}
            >
              {/* Radar Header */}
              <button
                type="button"
                onClick={() => setRadarExpanded((v) => !v)}
                style={{
                  width: '100%',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '16px 20px',
                  background: radarData.total_gaps > 0
                    ? 'linear-gradient(135deg, #7F1D1D 0%, #991B1B 100%)'
                    : 'linear-gradient(135deg, #065F46 0%, #047857 100%)',
                  border: 'none',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div>
                  <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', marginBottom: '4px' }}>
                    🎯 MISSING SCHEME RADAR
                  </div>
                  <div style={{ color: '#FFFFFF', fontSize: '1.0625rem', fontWeight: 800 }}>
                    {radarData.total_gaps} Coverage Gap{radarData.total_gaps !== 1 ? 's' : ''} Detected
                  </div>
                  <div style={{ color: 'rgba(255,255,255,0.75)', fontSize: '0.8125rem', marginTop: '4px' }}>
                    {radarData.zero_coverage_jurisdictions} zero-coverage · {radarData.low_coverage_jurisdictions} low-coverage ·
                    {' '}{radarData.stale_records} stale records · {radarData.pending_candidates} pending candidates ·
                    {' '}{radarData.no_form_schema_schemes} without form schema
                  </div>
                </div>
                <span style={{ color: '#FFFFFF', fontSize: '1.25rem', marginLeft: '12px' }}>
                  {radarExpanded ? '▲' : '▼'}
                </span>
              </button>

              {radarExpanded && (
                <div style={{ padding: '0' }}>
                  {radarData.items.length === 0 ? (
                    <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                      ✅ No coverage gaps detected. All 36 jurisdictions have scheme coverage.
                    </div>
                  ) : (
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                        <thead>
                          <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                            <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)', width: '100px' }}>Severity</th>
                            <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)', width: '130px' }}>Type</th>
                            <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)', width: '120px' }}>Jurisdiction</th>
                            <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Detail</th>
                            <th style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Suggested Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {radarData.items.map((item, idx) => {
                            const sevColor = item.severity === 'high' ? '#B91C1C' : item.severity === 'medium' ? '#92400E' : '#1D4ED8';
                            const sevBg = item.severity === 'high' ? '#FEE2E2' : item.severity === 'medium' ? '#FEF3C7' : '#DBEAFE';
                            const typeLabel = {
                              zero_coverage: '🔴 Zero Coverage',
                              low_coverage: '🟡 Low Coverage',
                              stale_record: '🟠 Stale Record',
                              pending_candidate: '🔵 Pending Review',
                              no_form_schema: '⚪ No Form Schema',
                            }[item.radar_type] || item.radar_type;
                            return (
                              <tr
                                key={idx}
                                style={{
                                  borderBottom: '1px solid var(--color-border)',
                                  backgroundColor: idx % 2 === 0 ? '#FFFFFF' : '#F8FAFC',
                                }}
                              >
                                <td style={{ padding: '10px 14px' }}>
                                  <span
                                    style={{
                                      padding: '2px 8px',
                                      borderRadius: '10px',
                                      backgroundColor: sevBg,
                                      color: sevColor,
                                      fontWeight: 700,
                                      fontSize: '0.75rem',
                                      textTransform: 'uppercase',
                                    }}
                                  >
                                    {item.severity}
                                  </span>
                                </td>
                                <td style={{ padding: '10px 14px', color: '#374151', fontWeight: 600 }}>{typeLabel}</td>
                                <td style={{ padding: '10px 14px', color: 'var(--color-navy)', fontWeight: 700 }}>
                                  {item.jurisdiction || '—'}
                                  {item.jurisdiction_code && (
                                    <span style={{ color: 'var(--color-text-muted)', fontWeight: 400, marginLeft: '4px' }}>({item.jurisdiction_code})</span>
                                  )}
                                </td>
                                <td style={{ padding: '10px 14px', color: '#374151', maxWidth: '300px' }}>
                                  {item.scheme_name && (
                                    <div style={{ fontWeight: 700, color: 'var(--color-navy)', marginBottom: '2px' }}>{item.scheme_name}</div>
                                  )}
                                  {item.detail}
                                </td>
                                <td style={{ padding: '10px 14px', color: '#6B7280', fontStyle: 'italic', maxWidth: '280px' }}>
                                  {item.suggested_action || '—'}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                  <div style={{
                    padding: '10px 16px',
                    backgroundColor: '#F8FAFC',
                    borderTop: '1px solid var(--color-border)',
                    fontSize: '0.75rem',
                    color: 'var(--color-text-muted)',
                  }}>
                    Generated at: {new Date(radarData.generated_at).toLocaleString()} · Showing up to 130 gap items across all 36 Indian jurisdictions.
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════
              ADMIN OPERATIONS PANELS — Scheme Requests, Help Tickets, i18n
              ═══════════════════════════════════════════════════════════════ */}
          <div
            style={{
              marginTop: 'var(--space-2xl)',
              border: '1px solid var(--color-border)',
              borderRadius: '10px',
              overflow: 'hidden',
              backgroundColor: '#FFFFFF',
            }}
          >
            {/* Tab Bar */}
            <div
              style={{
                display: 'flex',
                borderBottom: '2px solid var(--color-border)',
                backgroundColor: '#F8FAFC',
              }}
            >
              {[
                { id: 'invitations', icon: '🎟️', label: 'Official Invitations' },
                { id: 'radar', icon: '🎯', label: 'Rule Change Radar' },
                { id: 'evidence', icon: '📎', label: 'Evidence Queue' },
                { id: 'drift', icon: '🌐', label: 'Translation Drift' },
                { id: 'heatmap', icon: '🔥', label: 'Difficulty Heatmap' },
                { id: 'proposals', icon: '📝', label: 'Scheme Proposals' },
                { id: 'officials', icon: '🏛️', label: 'Official Accounts' },
                { id: 'requests', icon: '📋', label: 'Scheme Requests' },
                { id: 'tickets', icon: '🎫', label: 'Help Tickets' },
                { id: 'i18n', icon: '🗺️', label: 'Translation Audit' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => { setAdminTab(tab.id); setAdminActionMsg(null); }}
                  style={{
                    padding: '12px 14px',
                    border: 'none',
                    borderBottom: adminTab === tab.id ? '3px solid var(--color-teal)' : '3px solid transparent',
                    backgroundColor: adminTab === tab.id ? '#FFFFFF' : 'transparent',
                    color: adminTab === tab.id ? 'var(--color-navy)' : 'var(--color-text-muted)',
                    fontWeight: adminTab === tab.id ? 800 : 600,
                    fontSize: '0.8125rem',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </div>

            {/* Admin Action Feedback */}
            {adminActionMsg && (
              <div
                style={{
                  padding: '10px 16px',
                  backgroundColor: adminActionMsg.type === 'success' ? '#DCFCE7' : '#FEE2E2',
                  color: adminActionMsg.type === 'success' ? '#166534' : '#991B1B',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  borderBottom: '1px solid var(--color-border)',
                }}
              >
                {adminActionMsg.type === 'success' ? '✅' : '❌'} {adminActionMsg.text}
              </div>
            )}

            {/* ── TAB: Scheme Request Review Queue ──────────────── */}
            {adminTab === 'requests' && (
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
                  <select
                    value={srStatusFilter}
                    onChange={(e) => setSrStatusFilter(e.target.value)}
                    style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.8125rem' }}
                  >
                    <option value="">All Statuses</option>
                    {SR_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <button className="btn btn-secondary btn-sm" onClick={fetchSchemeRequests} disabled={srLoading}>
                    ↺ Refresh
                  </button>
                  <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                    {schemeRequests.length} request(s)
                  </span>
                </div>

                {srLoading ? (
                  <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-text-muted)' }}>Loading…</div>
                ) : schemeRequests.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>
                    📭 No scheme requests found.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {schemeRequests.map((req) => {
                      const statusColors = {
                        'Request Received': { bg: '#DBEAFE', color: '#1D4ED8' },
                        'Under Review': { bg: '#FEF3C7', color: '#92400E' },
                        'Information Needed': { bg: '#FDE68A', color: '#78350F' },
                        'Verified': { bg: '#D1FAE5', color: '#065F46' },
                        'Added to Catalogue': { bg: '#DCFCE7', color: '#166534' },
                        'Already Exists': { bg: '#F1F5F9', color: '#475569' },
                        'Rejected': { bg: '#FEE2E2', color: '#991B1B' },
                        'Unable to Verify': { bg: '#FCE7F3', color: '#9D174D' },
                      };
                      const sc = statusColors[req.status] || { bg: '#F1F5F9', color: '#475569' };
                      return (
                        <div
                          key={req.id}
                          style={{
                            border: '1px solid var(--color-border)',
                            borderRadius: '8px',
                            padding: '14px 16px',
                            backgroundColor: '#FAFBFC',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
                            <div>
                              <span style={{ fontWeight: 800, color: 'var(--color-navy)', fontSize: '0.9375rem' }}>
                                {req.display_name || req.scheme_name || '(unnamed)'}
                              </span>
                              {req.tracking_id && (
                                <span style={{ marginLeft: '8px', fontSize: '0.75rem', fontWeight: 600, color: '#1D4ED8', backgroundColor: '#EFF6FF', padding: '2px 6px', borderRadius: '4px' }}>
                                  {req.tracking_id}
                                </span>
                              )}
                            </div>
                            <span
                              style={{
                                padding: '3px 10px',
                                borderRadius: '10px',
                                backgroundColor: sc.bg,
                                color: sc.color,
                                fontWeight: 700,
                                fontSize: '0.75rem',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              {req.status}
                            </span>
                          </div>

                          {req.official_source_url && (
                            <div style={{ fontSize: '0.8125rem', color: '#2563EB', marginBottom: '4px' }}>
                              🔗 <a href={req.official_source_url} target="_blank" rel="noopener noreferrer" style={{ color: '#2563EB' }}>{req.official_source_url}</a>
                            </div>
                          )}

                          <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                            {req.department_name && <span>🏛️ {req.department_name} · </span>}
                            <span>{req.government_level?.toUpperCase()}</span>
                            {req.state_code && <span> · {req.state_code}</span>}
                            {req.created_at && <span> · {new Date(req.created_at).toLocaleDateString()}</span>}
                          </div>

                          {req.description && (
                            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-primary)', marginBottom: '8px', lineHeight: 1.4 }}>
                              {req.description}
                            </div>
                          )}

                          {req.admin_notes && (
                            <div style={{ fontSize: '0.8125rem', fontStyle: 'italic', color: '#6B7280', backgroundColor: '#F1F5F9', padding: '6px 10px', borderRadius: '4px', marginBottom: '8px' }}>
                              📝 Admin: {req.admin_notes}
                            </div>
                          )}

                          {/* Action buttons */}
                          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                            {req.status === 'Request Received' && (
                              <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem' }} onClick={() => handleSchemeRequestAction(req.id, 'Under Review')}>
                                📖 Mark Under Review
                              </button>
                            )}
                            {['Request Received', 'Under Review', 'Information Needed'].includes(req.status) && (
                              <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem', color: '#065F46', borderColor: '#10B981' }} onClick={() => handleSchemeRequestAction(req.id, 'Verified')}>
                                ✓ Verify
                              </button>
                            )}
                            {req.status === 'Verified' && (
                              <button className="btn btn-primary btn-sm" style={{ fontSize: '0.75rem', backgroundColor: '#0F766E' }} onClick={() => handleSchemeRequestAction(req.id, 'Added to Catalogue')}>
                                📥 Add to Catalogue
                              </button>
                            )}
                            {!['Rejected', 'Added to Catalogue', 'Already Exists'].includes(req.status) && (
                              <>
                                <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem', color: '#92400E' }} onClick={() => handleSchemeRequestAction(req.id, 'Already Exists', 'This scheme already exists in the catalogue.')}>
                                  ⚠️ Already Exists
                                </button>
                                <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem', color: '#991B1B' }} onClick={() => handleSchemeRequestAction(req.id, 'Rejected', 'Does not meet verification criteria.')}>
                                  ✕ Reject
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Help Ticket Support Queue ────────────────── */}
            {adminTab === 'tickets' && (
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
                  <select
                    value={htCategoryFilter}
                    onChange={(e) => setHtCategoryFilter(e.target.value)}
                    style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.8125rem' }}
                  >
                    <option value="">All Categories</option>
                    {HT_CATEGORIES.map((c) => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
                  </select>
                  <select
                    value={htStatusFilter}
                    onChange={(e) => setHtStatusFilter(e.target.value)}
                    style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.8125rem' }}
                  >
                    <option value="">All Statuses</option>
                    {HT_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <button className="btn btn-secondary btn-sm" onClick={fetchHelpTickets} disabled={htLoading}>
                    ↺ Refresh
                  </button>
                  <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                    {helpTickets.length} ticket(s)
                  </span>
                </div>

                {htLoading ? (
                  <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-text-muted)' }}>Loading…</div>
                ) : helpTickets.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>
                    📭 No help tickets found.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {helpTickets.map((tkt) => {
                      const tktStatusColors = {
                        'Received': { bg: '#DBEAFE', color: '#1D4ED8' },
                        'Open': { bg: '#FEF3C7', color: '#92400E' },
                        'In Progress': { bg: '#E0E7FF', color: '#4338CA' },
                        'Waiting for Citizen': { bg: '#FDE68A', color: '#78350F' },
                        'Resolved': { bg: '#D1FAE5', color: '#065F46' },
                        'Closed': { bg: '#F1F5F9', color: '#475569' },
                      };
                      const tc = tktStatusColors[tkt.status] || { bg: '#F1F5F9', color: '#475569' };
                      return (
                        <div
                          key={tkt.id}
                          style={{
                            border: '1px solid var(--color-border)',
                            borderRadius: '8px',
                            padding: '14px 16px',
                            backgroundColor: '#FAFBFC',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
                            <div>
                              <span style={{ fontWeight: 800, color: 'var(--color-navy)', fontSize: '0.9375rem' }}>
                                {tkt.ticket_number || `TKT-${tkt.id}`}
                              </span>
                              <span style={{ marginLeft: '8px', fontSize: '0.75rem', fontWeight: 600, color: '#7C3AED', backgroundColor: '#EDE9FE', padding: '2px 6px', borderRadius: '4px', textTransform: 'capitalize' }}>
                                {(tkt.category || 'other').replace(/_/g, ' ')}
                              </span>
                            </div>
                            <span
                              style={{
                                padding: '3px 10px',
                                borderRadius: '10px',
                                backgroundColor: tc.bg,
                                color: tc.color,
                                fontWeight: 700,
                                fontSize: '0.75rem',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              {tkt.status}
                            </span>
                          </div>

                          <div style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', marginBottom: '8px', lineHeight: 1.4 }}>
                            {tkt.description || tkt.subject || '(no description)'}
                          </div>

                          {tkt.contact_info && (
                            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                              📧 {tkt.contact_info}
                            </div>
                          )}

                          {tkt.resolution_message && (
                            <div style={{ fontSize: '0.8125rem', fontStyle: 'italic', color: '#065F46', backgroundColor: '#ECFDF5', padding: '6px 10px', borderRadius: '4px', marginBottom: '8px' }}>
                              ✅ Resolution: {tkt.resolution_message}
                            </div>
                          )}

                          {tkt.created_at && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
                              Created: {new Date(tkt.created_at).toLocaleString()}
                            </div>
                          )}

                          {/* Action buttons */}
                          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                            {tkt.status === 'Received' && (
                              <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem' }} onClick={() => handleHelpTicketAction(tkt.id, 'Open')}>
                                📖 Open
                              </button>
                            )}
                            {['Received', 'Open'].includes(tkt.status) && (
                              <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem', color: '#4338CA' }} onClick={() => handleHelpTicketAction(tkt.id, 'In Progress')}>
                                🔧 In Progress
                              </button>
                            )}
                            {['Open', 'In Progress', 'Waiting for Citizen'].includes(tkt.status) && (
                              <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem', color: '#065F46', borderColor: '#10B981' }} onClick={() => handleHelpTicketAction(tkt.id, 'Resolved', 'Issue addressed by support team.')}>
                                ✅ Resolve
                              </button>
                            )}
                            {tkt.status === 'Resolved' && (
                              <button className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem' }} onClick={() => handleHelpTicketAction(tkt.id, 'Closed')}>
                                🔒 Close
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Scheme Proposals (Official Submission Governance) ── */}
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
            {adminTab === 'i18n' && (
              <div style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
                  <div>
                    <h3 style={{ margin: '0 0 4px 0', fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                      🌐 {t('dashboard.qualityTitle', 'Multilingual Quality & Audio Assurance')}
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--color-text-secondary)', maxWidth: '800px' }}>
                      {t('dashboard.qualitySubtitle', 'Real-time verification of localization completeness, translation review statuses, and voice synthesis support across all 22 Eighth Schedule languages.')}
                    </p>
                  </div>
                  <button className="btn btn-secondary btn-sm" onClick={fetchI18nAudit} disabled={i18nLoading}>
                    ↺ {i18nLoading ? 'Scanning...' : 'Refresh Audit'}
                  </button>
                </div>

                {voiceTestResult && (
                  <div
                    style={{
                      padding: '10px 16px',
                      borderRadius: '8px',
                      marginBottom: '16px',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      backgroundColor: voiceTestResult.type === 'success' ? '#DCFCE7' : voiceTestResult.type === 'warning' ? '#FEF3C7' : '#FEE2E2',
                      color: voiceTestResult.type === 'success' ? '#166534' : voiceTestResult.type === 'warning' ? '#92400E' : '#B91C1C',
                      border: `1px solid ${voiceTestResult.type === 'success' ? '#86EFAC' : voiceTestResult.type === 'warning' ? '#FDE68A' : '#FCA5A5'}`,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span>{voiceTestResult.msg}</span>
                    <button
                      type="button"
                      onClick={() => { SpeechService.stopSpeaking(); setVoiceTestResult(null); }}
                      style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontWeight: 700 }}
                    >
                      ✕
                    </button>
                  </div>
                )}

                {i18nLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔄</div>
                    <div>Scanning canonical interface keys and database translations across 22 languages...</div>
                  </div>
                ) : !i18nAudit ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>
                    No audit data available. Click "Refresh Audit" to scan.
                  </div>
                ) : (
                  <div>
                    {/* Executive Stat Cards */}
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
                        gap: '12px',
                        marginBottom: '20px',
                      }}
                    >
                      <div style={{ backgroundColor: '#EFF6FF', padding: '14px', borderRadius: '8px', border: '1px solid #BFDBFE' }}>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#1D4ED8' }}>{i18nAudit.total_canonical_keys || 390}</div>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1E40AF', marginTop: '2px' }}>Canonical Interface Keys</div>
                      </div>
                      <div style={{ backgroundColor: '#ECFDF5', padding: '14px', borderRadius: '8px', border: '1px solid #A7F3D0' }}>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#065F46' }}>
                          {i18nAudit.overall_coverage != null ? `${i18nAudit.overall_coverage}%` : '100%'}
                        </div>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#047857', marginTop: '2px' }}>Overall Interface Coverage</div>
                      </div>
                      <div style={{ backgroundColor: '#F0FDF4', padding: '14px', borderRadius: '8px', border: '1px solid #BBF7D0' }}>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#15803D' }}>{i18nAudit.languages_audited || 23}</div>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#166534', marginTop: '2px' }}>Languages Audited (22+En)</div>
                      </div>
                      <div style={{ backgroundColor: '#FEF3C7', padding: '14px', borderRadius: '8px', border: '1px solid #FDE68A' }}>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#92400E' }}>
                          {(i18nAudit.results || []).filter((r) => r.external_tts || r.browser_tts).length} / {i18nAudit.languages_audited || 23}
                        </div>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#78350F', marginTop: '2px' }}>Audio Synthesis Ready</div>
                      </div>
                      <div style={{ backgroundColor: '#F3E8FF', padding: '14px', borderRadius: '8px', border: '1px solid #E9D5FF' }}>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#6B21A8' }}>
                          {(i18nAudit.results || []).filter((r) => r.review_status === 'Reviewed').length} / {i18nAudit.languages_audited || 23}
                        </div>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#581C87', marginTop: '2px' }}>Officially Reviewed</div>
                      </div>
                    </div>

                    {/* Filter Pills */}
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                      {[
                        { id: 'all', label: `All Languages (${(i18nAudit.results || []).length})` },
                        { id: 'reviewed', label: `Reviewed (${(i18nAudit.results || []).filter((r) => r.review_status === 'Reviewed').length})` },
                        { id: 'machine', label: `Machine Localized (${(i18nAudit.results || []).filter((r) => r.review_status !== 'Reviewed').length})` },
                        { id: 'rtl', label: `RTL Scripts (${(i18nAudit.results || []).filter((r) => r.is_rtl).length})` },
                        { id: 'tts_ready', label: `Audio Synthesis Ready (${(i18nAudit.results || []).filter((r) => r.external_tts || r.browser_tts).length})` },
                        { id: 'written_only', label: `Written Guidance Only (${(i18nAudit.results || []).filter((r) => !r.external_tts && !r.browser_tts).length})` },
                      ].map((btn) => (
                        <button
                          key={btn.id}
                          type="button"
                          onClick={() => setI18nFilter(btn.id)}
                          style={{
                            padding: '6px 12px',
                            borderRadius: '16px',
                            fontSize: '0.78rem',
                            fontWeight: i18nFilter === btn.id ? 700 : 500,
                            backgroundColor: i18nFilter === btn.id ? 'var(--color-navy)' : '#F1F5F9',
                            color: i18nFilter === btn.id ? '#FFFFFF' : 'var(--color-text-primary)',
                            border: '1px solid var(--color-border)',
                            cursor: 'pointer',
                          }}
                        >
                          {btn.label}
                        </button>
                      ))}
                    </div>

                    {/* Detailed Multi-dimensional Table */}
                    {i18nAudit.results && i18nAudit.results.length > 0 && (
                      <div style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                          <thead>
                            <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                              <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Language & Script</th>
                              <th style={{ padding: '12px 14px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)', minWidth: '160px' }}>Interface Keys</th>
                              <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 700, color: 'var(--color-navy)' }}>Benefits</th>
                              <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 700, color: 'var(--color-navy)' }}>Form Fields</th>
                              <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 700, color: 'var(--color-navy)' }}>Rules & Docs</th>
                              <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 700, color: 'var(--color-navy)' }}>Review Status</th>
                              <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 700, color: 'var(--color-navy)' }}>Audio Synthesis</th>
                              <th style={{ padding: '12px 14px', textAlign: 'center', fontWeight: 700, color: 'var(--color-navy)' }}>Test Audio</th>
                            </tr>
                          </thead>
                          <tbody>
                            {i18nAudit.results
                              .filter((lang) => {
                                if (i18nFilter === 'reviewed') return lang.review_status === 'Reviewed';
                                if (i18nFilter === 'machine') return lang.review_status !== 'Reviewed';
                                if (i18nFilter === 'rtl') return lang.is_rtl;
                                if (i18nFilter === 'tts_ready') return lang.external_tts || lang.browser_tts;
                                if (i18nFilter === 'written_only') return !lang.external_tts && !lang.browser_tts;
                                return true;
                              })
                              .map((lang, idx) => {
                                const coverage = lang.coverage_pct ?? 100;
                                const isAudioTesting = testingVoiceCode === lang.code;

                                return (
                                  <tr
                                    key={lang.code || idx}
                                    style={{
                                      borderBottom: '1px solid var(--color-border)',
                                      backgroundColor: idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA',
                                    }}
                                  >
                                    <td style={{ padding: '10px 14px' }}>
                                      <div style={{ fontWeight: 700, color: 'var(--color-navy)' }}>
                                        {lang.name} {lang.native_name && lang.native_name !== lang.name && `(${lang.native_name})`}
                                        {lang.is_rtl && (
                                          <span style={{ marginLeft: '6px', fontSize: '0.65rem', padding: '1px 5px', borderRadius: '4px', backgroundColor: '#EDE9FE', color: '#7C3AED', fontWeight: 700 }}>
                                            RTL
                                          </span>
                                        )}
                                      </div>
                                      <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                                        {lang.code.toUpperCase()} · {lang.writing_system || 'Indic Script'}
                                      </div>
                                    </td>

                                    <td style={{ padding: '10px 14px' }}>
                                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px', fontWeight: 600 }}>
                                        <span>{lang.translated_keys} / {lang.total_keys}</span>
                                        <span style={{ color: coverage >= 90 ? '#166534' : '#92400E' }}>{coverage}%</span>
                                      </div>
                                      <div style={{ height: '6px', backgroundColor: '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
                                        <div
                                          style={{
                                            width: `${coverage}%`,
                                            height: '100%',
                                            backgroundColor: coverage >= 90 ? '#10B981' : '#F59E0B',
                                            borderRadius: '3px',
                                          }}
                                        />
                                      </div>
                                    </td>

                                    <td style={{ padding: '10px 14px', textAlign: 'center', fontWeight: 600, color: 'var(--color-navy)' }}>
                                      <span style={{ padding: '2px 8px', borderRadius: '10px', backgroundColor: '#ECFDF5', color: '#065F46', fontSize: '0.75rem' }}>
                                        {lang.benefits_translated || 3} schemes
                                      </span>
                                    </td>

                                    <td style={{ padding: '10px 14px', textAlign: 'center', fontWeight: 600, color: 'var(--color-navy)' }}>
                                      <span style={{ padding: '2px 8px', borderRadius: '10px', backgroundColor: '#F1F5F9', color: '#334155', fontSize: '0.75rem' }}>
                                        {lang.form_questions_translated || 6} fields
                                      </span>
                                    </td>

                                    <td style={{ padding: '10px 14px', textAlign: 'center', fontWeight: 600, color: 'var(--color-navy)' }}>
                                      <span style={{ padding: '2px 8px', borderRadius: '10px', backgroundColor: '#F1F5F9', color: '#334155', fontSize: '0.75rem' }}>
                                        {(lang.eligibility_translated || 0) + (lang.documents_translated || 0)} rules
                                      </span>
                                    </td>

                                    <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                                      <span
                                        style={{
                                          padding: '3px 8px',
                                          borderRadius: '12px',
                                          fontSize: '0.72rem',
                                          fontWeight: 700,
                                          backgroundColor: lang.review_status === 'Reviewed' ? '#DCFCE7' : '#E0F2FE',
                                          color: lang.review_status === 'Reviewed' ? '#166534' : '#0369A1',
                                          border: `1px solid ${lang.review_status === 'Reviewed' ? '#86EFAC' : '#BAE6FD'}`,
                                        }}
                                      >
                                        {lang.review_status === 'Reviewed' ? '✓ Reviewed' : '🌐 Machine Localized'}
                                      </span>
                                    </td>

                                    <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                                      <span
                                        style={{
                                          padding: '3px 8px',
                                          borderRadius: '12px',
                                          fontSize: '0.72rem',
                                          fontWeight: 700,
                                          backgroundColor: (lang.external_tts || lang.browser_tts) ? '#ECFDF5' : '#FEF3C7',
                                          color: (lang.external_tts || lang.browser_tts) ? '#065F46' : '#92400E',
                                          border: `1px solid ${(lang.external_tts || lang.browser_tts) ? '#A7F3D0' : '#FDE68A'}`,
                                        }}
                                      >
                                        {(lang.external_tts || lang.browser_tts) ? '🔊 Neural TTS Ready' : '📄 Written Only'}
                                      </span>
                                    </td>

                                    <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                                      <button
                                        type="button"
                                        onClick={() => handleTestAudio(lang.code, lang.name)}
                                        className="btn btn-sm"
                                        style={{
                                          fontSize: '0.75rem',
                                          padding: '4px 8px',
                                          backgroundColor: isAudioTesting ? '#EF4444' : '#F8FAFC',
                                          color: isAudioTesting ? '#FFFFFF' : 'var(--color-navy)',
                                          border: '1px solid var(--color-border)',
                                          cursor: 'pointer',
                                          borderRadius: '4px',
                                          fontWeight: 600,
                                        }}
                                      >
                                        {isAudioTesting ? '⏹️ Stop' : '🔊 Test Voice'}
                                      </button>
                                    </td>
                                  </tr>
                                );
                              })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Official Invitations & Access Control (Priority 1) ── */}
            {adminTab === 'invitations' && (
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                      Authoritative Official Invitations
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                      Controlled onboarding via secure, single-use, expiring invitation tokens. Public official registration is strictly prohibited.
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-secondary btn-sm" onClick={fetchInvitations} disabled={invLoading}>
                      ↺ Refresh
                    </button>
                    <button
                      type="button"
                      className="btn btn-primary btn-sm"
                      onClick={() => setShowInviteModal(true)}
                      style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                    >
                      ✚ Issue Official Invitation Token
                    </button>
                  </div>
                </div>

                {invLoading ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>Loading invitations…</div>
                ) : invitations.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                    No invitations issued yet. Click "Issue Official Invitation Token" to onboard a verified official.
                  </div>
                ) : (
                  <div style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Invitee</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Department & Scope</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Single-Use Token</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Expires</th>
                          <th style={{ padding: '10px 12px', textAlign: 'right', fontWeight: 700, color: 'var(--color-navy)' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {invitations.map((inv) => (
                          <tr key={inv.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                            <td style={{ padding: '10px 12px' }}>
                              <strong style={{ color: 'var(--color-navy)' }}>{inv.full_name}</strong>
                              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{inv.email}</div>
                            </td>
                            <td style={{ padding: '10px 12px' }}>
                              <div>{inv.department_name}</div>
                              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{inv.state_scope || 'Central / All-India'}</div>
                            </td>
                            <td style={{ padding: '10px 12px', fontFamily: 'monospace', color: '#1D4ED8' }}>
                              {inv.invitation_token}
                            </td>
                            <td style={{ padding: '10px 12px' }}>
                              <span style={{
                                padding: '3px 8px', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase',
                                backgroundColor: inv.status === 'activated' ? '#DCFCE7' : inv.status === 'pending' ? '#FEF3C7' : '#FEE2E2',
                                color: inv.status === 'activated' ? '#166534' : inv.status === 'pending' ? '#92400E' : '#991B1B'
                              }}>
                                {inv.status}
                              </span>
                            </td>
                            <td style={{ padding: '10px 12px', color: '#64748B' }}>
                              {new Date(inv.expires_at).toLocaleString()}
                            </td>
                            <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                              {inv.status === 'pending' && (
                                <button
                                  type="button"
                                  className="btn btn-sm btn-secondary"
                                  onClick={() => handleRevokeInvitationAction(inv.id)}
                                  style={{ color: '#DC2626', borderColor: '#FCA5A5', fontSize: '0.75rem', padding: '3px 8px' }}
                                >
                                  Revoke
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Issue Invitation Modal */}
                {showInviteModal && (
                  <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
                    <div style={{ backgroundColor: '#fff', borderRadius: '12px', maxWidth: '520px', width: '100%', padding: '26px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                          🎟️ Issue Official Invitation
                        </h3>
                        <button type="button" onClick={() => setShowInviteModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.4rem', cursor: 'pointer', color: '#64748B' }}>✕</button>
                      </div>

                      <form onSubmit={handleCreateInvitationSubmit}>
                        <div style={{ display: 'grid', gap: '12px', marginBottom: '16px' }}>
                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Official Email Address *</label>
                            <input
                              type="email"
                              required
                              placeholder="officer@dept.gov.in"
                              value={inviteForm.email}
                              onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                            />
                          </div>

                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Full Name *</label>
                            <input
                              type="text"
                              required
                              placeholder="Dr. Rajesh Verma"
                              value={inviteForm.full_name}
                              onChange={(e) => setInviteForm({ ...inviteForm, full_name: e.target.value })}
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                            />
                          </div>

                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Department / Ministry Name *</label>
                            <input
                              type="text"
                              required
                              placeholder="e.g. Ministry of Agriculture & Farmers Welfare"
                              value={inviteForm.department_name}
                              onChange={(e) => setInviteForm({ ...inviteForm, department_name: e.target.value })}
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                            />
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>State Scope (Optional)</label>
                              <input
                                type="text"
                                placeholder="Blank = Central / All-India"
                                value={inviteForm.state_scope}
                                onChange={(e) => setInviteForm({ ...inviteForm, state_scope: e.target.value.toUpperCase() })}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Token Expiry (Days)</label>
                              <input
                                type="number"
                                min={1}
                                max={30}
                                value={inviteForm.expires_in_days}
                                onChange={(e) => setInviteForm({ ...inviteForm, expires_in_days: parseInt(e.target.value, 10) || 7 })}
                                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                              />
                            </div>
                          </div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                          <button type="button" className="btn btn-secondary" onClick={() => setShowInviteModal(false)}>Cancel</button>
                          <button type="submit" className="btn btn-primary" style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}>
                            Generate Single-Use Token
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Scheme Rule Change Radar Review Queue (Priority 2) ── */}
            {adminTab === 'radar' && (
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                      Scheme Rule Change Radar Review Queue
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                      Compare candidate rule changes against the published baseline with verifiable source evidence. Publishing commits updates to the database and automatically flags affected translations for review.
                    </p>
                  </div>
                  <button className="btn btn-secondary btn-sm" onClick={fetchRadar} disabled={radarLoading}>
                    ↺ Refresh
                  </button>
                </div>

                {radarLoading ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>Loading radar records…</div>
                ) : radarRecords.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                    No radar change submissions pending review.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {radarRecords.map((r) => (
                      <div key={r.id} style={{ border: '1px solid var(--color-border)', borderRadius: '8px', padding: '16px', backgroundColor: '#FAFBFC' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                              <strong style={{ fontSize: '0.95rem', color: 'var(--color-navy)' }}>
                                Scheme #{r.scheme_id} Change Set #{r.id}
                              </strong>
                              <span style={{ fontSize: '0.72rem', backgroundColor: '#EFF6FF', color: '#1D4ED8', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
                                {r.source_version || 'v2026'}
                              </span>
                              <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 700, color: r.change_magnitude === 'major' ? '#DC2626' : '#D97706' }}>
                                [{r.change_magnitude}]
                              </span>
                            </div>
                            <div style={{ fontSize: '0.8125rem', color: '#334155', marginTop: '2px' }}>
                              Department: <strong>{r.department_name}</strong> · Submitted by: {r.submitter_identifier}
                            </div>
                            {r.source_url && (
                              <div style={{ fontSize: '0.75rem', color: '#2563EB', marginTop: '2px' }}>
                                🔗 Source: <a href={r.source_url} target="_blank" rel="noopener noreferrer" style={{ color: '#2563EB' }}>{r.source_url}</a>
                              </div>
                            )}
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span style={{
                              padding: '3px 8px', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase',
                              backgroundColor: r.status === 'published' ? '#DCFCE7' : r.status === 'approved' ? '#D1FAE5' : r.status === 'submitted' ? '#EFF6FF' : '#F1F5F9',
                              color: r.status === 'published' ? '#166534' : r.status === 'approved' ? '#047857' : r.status === 'submitted' ? '#1D4ED8' : '#475569'
                            }}>
                              {r.status}
                            </span>
                            {r.status !== 'published' && r.status !== 'rejected' && (
                              <button
                                type="button"
                                className="btn btn-sm btn-primary"
                                onClick={() => { setSelectedRadar(r); setRadarDecision('approve'); setRadarReviewModal(true); }}
                                style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                              >
                                Review & Publish
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Candidate Summary */}
                        <div style={{ marginTop: '10px', fontSize: '0.8125rem', color: '#475569', backgroundColor: '#FFFFFF', padding: '10px 12px', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
                          <strong>Candidate Notes:</strong> {r.official_notes || 'Extracted via Scheme Rule Change Radar diff engine.'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Radar Review & Publish Modal */}
                {radarReviewModal && selectedRadar && (
                  <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
                    <div style={{ backgroundColor: '#fff', borderRadius: '12px', maxWidth: '640px', width: '100%', maxHeight: '90vh', overflowY: 'auto', padding: '26px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                        <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                          🎯 Review & Authorize Rule Change Set #{selectedRadar.id}
                        </h3>
                        <button type="button" onClick={() => setRadarReviewModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.4rem', cursor: 'pointer', color: '#64748B' }}>✕</button>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', marginBottom: '4px' }}>
                            Published Baseline
                          </div>
                          <pre style={{ margin: 0, padding: '10px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid #E2E8F0', fontSize: '0.75rem', overflowX: 'auto', whiteSpace: 'pre-wrap', maxHeight: '180px' }}>
                            {selectedRadar.published_baseline_json ? JSON.stringify(JSON.parse(selectedRadar.published_baseline_json), null, 2) : 'Baseline data'}
                          </pre>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-teal)', textTransform: 'uppercase', marginBottom: '4px' }}>
                            Candidate Proposal
                          </div>
                          <pre style={{ margin: 0, padding: '10px', backgroundColor: '#F0FDFA', borderRadius: '6px', border: '1px solid #99F6E4', fontSize: '0.75rem', overflowX: 'auto', whiteSpace: 'pre-wrap', maxHeight: '180px' }}>
                            {selectedRadar.candidate_content_json ? JSON.stringify(JSON.parse(selectedRadar.candidate_content_json), null, 2) : 'Candidate data'}
                          </pre>
                        </div>
                      </div>

                      <form onSubmit={handleRadarReviewSubmit}>
                        <div style={{ display: 'grid', gap: '12px', marginBottom: '16px' }}>
                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                              Governance Decision *
                            </label>
                            <select
                              value={radarDecision}
                              onChange={(e) => setRadarDecision(e.target.value)}
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                            >
                              <option value="approve">Approve & Publish to Official Database (Triggers Drift Monitor)</option>
                              <option value="request_revision">Request Revision from Department Official</option>
                              <option value="reject">Reject Change Set</option>
                            </select>
                          </div>

                          <div>
                            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                              Review Notes / Approval Rationale
                            </label>
                            <textarea
                              rows={3}
                              value={radarReviewNotes}
                              onChange={(e) => setRadarReviewNotes(e.target.value)}
                              placeholder="Document source verification and gazette cross-check..."
                              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                            />
                          </div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                          <button type="button" className="btn btn-secondary" onClick={() => setRadarReviewModal(false)}>Cancel</button>
                          <button type="submit" className="btn btn-primary" disabled={radarSubmitting} style={{ backgroundColor: 'var(--color-navy)', borderColor: 'var(--color-navy)' }}>
                            {radarSubmitting ? 'Processing…' : 'Confirm & Commit Action'}
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Evidence Verification Queue (Priority 4) ── */}
            {adminTab === 'evidence' && (
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                      Field-Level Evidence Verification Queue
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                      Authoritative audit of scheme claim quotations, official source links, and verification timestamps.
                    </p>
                  </div>
                  <button className="btn btn-secondary btn-sm" onClick={fetchEvidence} disabled={evidenceLoading}>
                    ↺ Refresh
                  </button>
                </div>

                {evidenceLoading ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>Loading evidence records…</div>
                ) : evidenceList.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                    No field evidence claims recorded yet.
                  </div>
                ) : (
                  <div style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Scheme / Dept</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Field Name</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Claim Content</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Official URL & Citation</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                          <th style={{ padding: '10px 12px', textAlign: 'right', fontWeight: 700, color: 'var(--color-navy)' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {evidenceList.map((ev) => (
                          <tr key={ev.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                            <td style={{ padding: '10px 12px' }}>
                              <strong>Scheme #{ev.scheme_id}</strong>
                              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{ev.department_name}</div>
                            </td>
                            <td style={{ padding: '10px 12px', fontFamily: 'monospace', color: '#1D4ED8' }}>
                              {ev.field_name}
                            </td>
                            <td style={{ padding: '10px 12px', maxWidth: '200px' }}>
                              {ev.claim_value}
                            </td>
                            <td style={{ padding: '10px 12px', maxWidth: '280px' }}>
                              <a href={ev.source_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-teal)', fontWeight: 600 }}>
                                🔗 {ev.source_title || ev.source_url}
                              </a>
                              {ev.quotation_or_section && (
                                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '2px', fontStyle: 'italic' }}>
                                  "{ev.quotation_or_section}"
                                </div>
                              )}
                            </td>
                            <td style={{ padding: '10px 12px' }}>
                              <span style={{
                                padding: '3px 8px', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase',
                                backgroundColor: ev.verification_status === 'verified' ? '#DCFCE7' : ev.verification_status === 'pending' ? '#FEF3C7' : '#FEE2E2',
                                color: ev.verification_status === 'verified' ? '#166534' : ev.verification_status === 'pending' ? '#92400E' : '#991B1B'
                              }}>
                                {ev.verification_status}
                              </span>
                            </td>
                            <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                              {ev.verification_status !== 'verified' && (
                                <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                                  <button
                                    type="button"
                                    className="btn btn-sm btn-primary"
                                    onClick={() => handleVerifyEvidenceAction(ev.id, true)}
                                    style={{ backgroundColor: '#059669', borderColor: '#059669', fontSize: '0.72rem', padding: '3px 8px' }}
                                  >
                                    Verify
                                  </button>
                                  <button
                                    type="button"
                                    className="btn btn-sm btn-secondary"
                                    onClick={() => handleVerifyEvidenceAction(ev.id, false)}
                                    style={{ color: '#DC2626', borderColor: '#FCA5A5', fontSize: '0.72rem', padding: '3px 8px' }}
                                  >
                                    Reject
                                  </button>
                                </div>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Translation Drift Monitor (Priority 5) ── */}
            {adminTab === 'drift' && (
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                      Translation Drift Master Monitor
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                      Monitors all 22 Eighth Schedule Indian languages for stale localized content following scheme rule updates.
                    </p>
                  </div>
                  <button className="btn btn-secondary btn-sm" onClick={fetchDrift} disabled={driftLoading}>
                    ↺ Refresh
                  </button>
                </div>

                {driftLoading ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>Loading drift alerts…</div>
                ) : driftAlerts.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                    ✅ All multilingual versions across the 22 Eighth Schedule languages are synchronized.
                  </div>
                ) : (
                  <div style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Scheme / Dept</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Language</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Field Name</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Drift Reason</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                          <th style={{ padding: '10px 12px', textAlign: 'right', fontWeight: 700, color: 'var(--color-navy)' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {driftAlerts.map((d) => (
                          <tr key={d.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                            <td style={{ padding: '10px 12px' }}>
                              <strong>Scheme #{d.scheme_id}</strong>
                              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{d.department_name}</div>
                            </td>
                            <td style={{ padding: '10px 12px', fontWeight: 700, color: 'var(--color-navy)' }}>
                              {d.language_code.toUpperCase()}
                            </td>
                            <td style={{ padding: '10px 12px', fontFamily: 'monospace', color: '#1D4ED8' }}>
                              {d.field_name}
                            </td>
                            <td style={{ padding: '10px 12px', color: '#334155' }}>
                              {d.drift_reason}
                            </td>
                            <td style={{ padding: '10px 12px' }}>
                              <span style={{
                                padding: '3px 8px', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase',
                                backgroundColor: d.status === 'verified' ? '#DCFCE7' : d.status === 'human_reviewed' ? '#EFF6FF' : '#FEF3C7',
                                color: d.status === 'verified' ? '#166534' : d.status === 'human_reviewed' ? '#1D4ED8' : '#92400E'
                              }}>
                                {d.status}
                              </span>
                            </td>
                            <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                              {d.status !== 'verified' && (
                                <button
                                  type="button"
                                  className="btn btn-sm btn-primary"
                                  onClick={() => handleReviewDriftAction(d.id, 'verified')}
                                  style={{ backgroundColor: '#059669', borderColor: '#059669', fontSize: '0.72rem', padding: '3px 8px' }}
                                >
                                  Verify Translation
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* ── TAB: Citizen Difficulty Heatmap (Priority 3) ── */}
            {adminTab === 'heatmap' && (
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                      Citizen Difficulty Heatmap (Pan-Government Analytics)
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                      Privacy-preserving aggregations across guided forms, confusing fields, and assistance requests.
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <select
                      value={heatmapDays}
                      onChange={(e) => setHeatmapDays(e.target.value)}
                      style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.8125rem' }}
                    >
                      <option value="7">Last 7 Days</option>
                      <option value="30">Last 30 Days</option>
                      <option value="90">Last 90 Days</option>
                    </select>

                    <button className="btn btn-secondary btn-sm" onClick={fetchHeatmap} disabled={heatmapLoading}>
                      ↺ Refresh
                    </button>
                  </div>
                </div>

                {heatmapLoading ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>Loading aggregated metrics…</div>
                ) : heatmapData?.is_insufficient_data ? (
                  <div style={{
                    padding: '36px',
                    backgroundColor: '#F8FAFC',
                    borderRadius: '8px',
                    border: '1.5px dashed #CBD5E1',
                    textAlign: 'center',
                  }}>
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🛡️</div>
                    <h4 style={{ margin: '0 0 6px 0', fontSize: '1.1rem', color: 'var(--color-navy)' }}>
                      Not Enough Data Yet
                    </h4>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748B', maxWidth: '540px', marginInline: 'auto', lineHeight: 1.5 }}>
                      {heatmapData.message || 'Minimum privacy threshold of 3 completed citizen sessions required to display aggregated difficulty metrics without risk of de-anonymization.'}
                    </p>
                  </div>
                ) : heatmapData ? (
                  <div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', marginBottom: '20px' }}>
                      <div style={{ padding: '14px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
                        <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Total Analyzed Sessions</div>
                        <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-navy)' }}>
                          {heatmapData.total_sessions}
                        </div>
                      </div>
                      <div style={{ padding: '14px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
                        <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Help Request Rate</div>
                        <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-teal)' }}>
                          {heatmapData.help_request_rate_pct}%
                        </div>
                      </div>
                      <div style={{ padding: '14px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
                        <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Median Resolution Time</div>
                        <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#1D4ED8' }}>
                          {heatmapData.median_time_to_resolve_minutes}m
                        </div>
                      </div>
                      <div style={{ padding: '14px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
                        <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Support Resolution Rate</div>
                        <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#166534' }}>
                          {heatmapData.support_ticket_resolution_rate_pct}%
                        </div>
                      </div>
                    </div>

                    <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem', color: 'var(--color-navy)' }}>
                      Top Confusing Form Fields
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {(heatmapData.confusing_fields || []).map((cf, idx) => (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '6px' }}>
                          <div>
                            <strong style={{ fontSize: '0.875rem', color: 'var(--color-navy)' }}>{cf.field_name}</strong>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', marginLeft: '8px' }}>({cf.form_step})</span>
                            <div style={{ fontSize: '0.75rem', color: '#DC2626', marginTop: '2px' }}>Top Error: {cf.top_error_category}</div>
                          </div>
                          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                            <div style={{ textAlign: 'right' }}>
                              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Help Requests</div>
                              <strong style={{ fontSize: '0.875rem', color: 'var(--color-navy)' }}>{cf.help_requests_count}</strong>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Error Freq</div>
                              <strong style={{ fontSize: '0.875rem', color: '#DC2626' }}>{cf.validation_error_frequency}</strong>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
