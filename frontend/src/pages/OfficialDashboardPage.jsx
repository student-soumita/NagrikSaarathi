import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

/**
 * NagrikSaarathi — Department Official Dashboard & Operational Workbench
 *
 * Priorities Implemented:
 * - Scheme Rule Change Radar (Diff analysis, source citations, draft candidate sets)
 * - Citizen Difficulty Heatmap (Privacy-preserving metrics, < 3 session threshold)
 * - Evidence-Linked Scheme Editor (Traceable citations, broken URL / stale review diagnostics)
 * - Translation Drift Monitor (22 Scheduled Languages, drift tracking on rule updates)
 * - Task Lifecycle & Proposals (Draft -> Submitted -> Under Review -> Revision Required -> Approved -> Published)
 * - Civic Editorial Theme: Navy #102A43, Ivory #F8F5EF, Teal #0F766E, Saffron #E7A93B
 */

const STATUS_LABELS = {
  draft:             { label: 'Draft',             color: 'var(--color-text-muted)',    bg: 'var(--color-surface-subtle)' },
  submitted:         { label: 'Submitted',         color: '#1D4ED8',                   bg: '#EFF6FF' },
  under_review:      { label: 'Under Review',      color: 'var(--color-saffron-dark)',  bg: 'var(--color-saffron-light)' },
  revision_required: { label: 'Revision Required', color: 'var(--color-error)',         bg: 'var(--color-error-bg)' },
  approved:          { label: 'Approved',          color: 'var(--color-success)',       bg: 'var(--color-success-bg)' },
  rejected:          { label: 'Rejected',          color: '#7F1D1D',                   bg: '#FEF2F2' },
  published:         { label: 'Published',         color: '#047857',                   bg: '#D1FAE5' },
};

function StatusBadge({ status }) {
  const meta = STATUS_LABELS[status] || { label: status, color: 'var(--color-text-muted)', bg: 'var(--color-surface-subtle)' };
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 8px',
      borderRadius: 'var(--border-radius-sm)',
      fontSize: '0.7rem',
      fontWeight: 700,
      textTransform: 'uppercase',
      letterSpacing: '0.04em',
      background: meta.bg,
      color: meta.color,
      border: `1px solid ${meta.color}40`,
    }}>
      {meta.label}
    </span>
  );
}

export function OfficialDashboardPage({ currentUser, onNavigate, onLogout }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // 1. Overview & Department Data
  const [stats, setStats] = useState(null);
  const [schemes, setSchemes] = useState([]);
  const [schemeSearch, setSchemeSearch] = useState('');

  // 2. Proposals
  const [proposals, setProposals] = useState([]);
  const [proposalFilter, setProposalFilter] = useState('all');
  const [showProposalModal, setShowProposalModal] = useState(false);
  const [proposalForm, setProposalForm] = useState({
    proposal_type: 'eligibility_update',
    scheme_name: '',
    category: 'agriculture',
    government_level: 'central',
    description: '',
    benefit_summary: '',
    official_source_url: '',
    source_evidence: '',
  });
  const [proposalSubmitting, setProposalSubmitting] = useState(false);

  // Revision Modal
  const [revisionModal, setRevisionModal] = useState(null);
  const [revisionText, setRevisionText] = useState('');
  const [revisionSubmitting, setRevisionSubmitting] = useState(false);

  // 3. Scheme Rule Change Radar
  const [radarRecords, setRadarRecords] = useState([]);
  const [selectedSchemeId, setSelectedSchemeId] = useState('');
  const [sourceUrlInput, setSourceUrlInput] = useState('');
  const [docTextInput, setDocTextInput] = useState('');
  const [sourceVersionInput, setSourceVersionInput] = useState('2026-v2');
  const [analyzingRadar, setAnalyzingRadar] = useState(false);
  const [radarAnalysisResult, setRadarAnalysisResult] = useState(null);
  const [submittingRadar, setSubmittingRadar] = useState(false);

  // 4. Evidence-Linked Editor
  const [evidenceList, setEvidenceList] = useState([]);
  const [evidenceSummary, setEvidenceSummary] = useState(null);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [evidenceForm, setEvidenceForm] = useState({
    scheme_id: '',
    field_name: 'eligibility_criteria',
    claim_value: '',
    source_url: '',
    source_title: '',
    quotation_or_section: '',
  });
  const [evidenceSubmitting, setEvidenceSubmitting] = useState(false);

  // 5. Citizen Difficulty Heatmap
  const [heatmapData, setHeatmapData] = useState(null);
  const [heatmapDays, setHeatmapDays] = useState('30');
  const [heatmapStepFilter, setHeatmapStepFilter] = useState('');
  const [loadingHeatmap, setLoadingHeatmap] = useState(false);

  // 6. Translation Drift Monitor
  const [driftAlerts, setDriftAlerts] = useState([]);

  /* ── Master Data Loader ────────────────────────────────────────────── */
  const loadDepartmentData = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const [statsRes, schemesRes, proposalsRes, radarRes, evRes, evSumRes, driftRes] = await Promise.allSettled([
        api.getDepartmentStats(),
        api.getDepartmentSchemes(),
        api.getDepartmentProposals(),
        api.getDepartmentRadar(),
        api.getDepartmentEvidence(),
        api.getDepartmentEvidenceSummary(),
        api.getDepartmentTranslationDrift(),
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value);
      if (schemesRes.status === 'fulfilled') {
        const sList = schemesRes.value || [];
        setSchemes(sList);
        if (sList.length > 0 && !selectedSchemeId) {
          setSelectedSchemeId(sList[0].id);
          setEvidenceForm(prev => ({ ...prev, scheme_id: sList[0].id }));
        }
      }
      if (proposalsRes.status === 'fulfilled') setProposals(proposalsRes.value || []);
      if (radarRes.status === 'fulfilled') setRadarRecords(radarRes.value || []);
      if (evRes.status === 'fulfilled') setEvidenceList(evRes.value || []);
      if (evSumRes.status === 'fulfilled') setEvidenceSummary(evSumRes.value || null);
      if (driftRes.status === 'fulfilled') setDriftAlerts(driftRes.value || []);
    } catch (err) {
      setError(err.message || 'Failed to load department operational data.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedSchemeId]);

  useEffect(() => {
    loadDepartmentData();
  }, [loadDepartmentData]);

  // Load heatmap when switching to heatmap tab or changing days
  useEffect(() => {
    if (activeTab === 'heatmap') {
      fetchHeatmap();
    }
  }, [activeTab, heatmapDays, heatmapStepFilter]);

  const fetchHeatmap = async () => {
    setLoadingHeatmap(true);
    try {
      const data = await api.getDepartmentHeatmap({
        days: heatmapDays,
        form_step: heatmapStepFilter || undefined,
      });
      setHeatmapData(data);
    } catch (err) {
      console.error('Heatmap load error:', err);
    } finally {
      setLoadingHeatmap(false);
    }
  };

  /* ── Radar: Analyze Document / URL Diff ────────────────────────────── */
  const handleAnalyzeRadar = async (e) => {
    e.preventDefault();
    if (!selectedSchemeId) {
      setError('Please select a scheme to analyze.');
      return;
    }
    if (!docTextInput.trim() && !sourceUrlInput.trim()) {
      setError('Please provide either official document notification text or an official URL.');
      return;
    }

    setAnalyzingRadar(true);
    setError('');
    try {
      const result = await api.analyzeRadarChanges({
        scheme_id: parseInt(selectedSchemeId, 10),
        source_url: sourceUrlInput.trim() || undefined,
        document_text: docTextInput.trim() || undefined,
        source_version: sourceVersionInput.trim() || 'v2026',
      });
      setRadarAnalysisResult(result);
    } catch (err) {
      setError(err.message || 'Failed to analyze rule changes.');
    } finally {
      setAnalyzingRadar(false);
    }
  };

  /* ── Radar: Submit Candidate Change Set ───────────────────────────── */
  const handleSubmitRadarCandidate = async () => {
    if (!radarAnalysisResult) return;
    setSubmittingRadar(true);
    setError('');
    try {
      await api.submitRadarChange({
        scheme_id: parseInt(selectedSchemeId, 10),
        source_url: sourceUrlInput.trim() || undefined,
        document_text: docTextInput.trim() || undefined,
        source_version: sourceVersionInput.trim() || 'v2026',
        official_notes: 'Candidate extracted via Official Rule Change Radar diff engine.',
      });
      setSuccessMsg('Candidate change set created and queued for Principal Administrator approval!');
      setRadarAnalysisResult(null);
      setDocTextInput('');
      // Reload radar records
      const updated = await api.getDepartmentRadar();
      setRadarRecords(updated || []);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to submit candidate change set.');
    } finally {
      setSubmittingRadar(false);
    }
  };

  /* ── Evidence: Submit Field Evidence ──────────────────────────────── */
  const handleSubmitEvidence = async (e) => {
    e.preventDefault();
    if (!evidenceForm.claim_value.trim() || !evidenceForm.source_url.trim()) {
      setError('Claim value and official source URL are required.');
      return;
    }
    setEvidenceSubmitting(true);
    setError('');
    try {
      await api.submitDepartmentEvidence({
        scheme_id: parseInt(evidenceForm.scheme_id, 10),
        field_name: evidenceForm.field_name,
        claim_value: evidenceForm.claim_value.trim(),
        source_url: evidenceForm.source_url.trim(),
        source_title: evidenceForm.source_title.trim() || undefined,
        quotation_or_section: evidenceForm.quotation_or_section.trim() || undefined,
      });
      setSuccessMsg('Field evidence linked successfully! Queued for verification review.');
      setShowEvidenceModal(false);
      setEvidenceForm(prev => ({
        ...prev,
        claim_value: '',
        source_url: '',
        source_title: '',
        quotation_or_section: '',
      }));
      const [evListRes, evSumRes] = await Promise.all([
        api.getDepartmentEvidence(),
        api.getDepartmentEvidenceSummary(),
      ]);
      setEvidenceList(evListRes || []);
      setEvidenceSummary(evSumRes || null);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to submit field evidence.');
    } finally {
      setEvidenceSubmitting(false);
    }
  };

  /* ── Proposal: Create Proposal ────────────────────────────────────── */
  const handleProposalSubmit = async (e) => {
    e.preventDefault();
    if (!proposalForm.scheme_name.trim() || !proposalForm.description.trim() || !proposalForm.source_evidence.trim()) {
      setError('Scheme name, description, and source evidence are required.');
      return;
    }
    setProposalSubmitting(true);
    setError('');
    try {
      await api.createSchemeProposal(proposalForm);
      setSuccessMsg('Proposal submitted! Queued for Principal Administrator review.');
      setShowProposalModal(false);
      const updated = await api.getDepartmentProposals();
      setProposals(updated || []);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Proposal submission failed.');
    } finally {
      setProposalSubmitting(false);
    }
  };

  /* ── Proposal: Revision Response ──────────────────────────────────── */
  const handleRevisionResubmit = async (proposalId) => {
    setRevisionSubmitting(true);
    try {
      await api.updateSchemeProposal(proposalId, {
        source_evidence: revisionText || undefined,
        submit_now: true,
      });
      setRevisionModal(null);
      setRevisionText('');
      setSuccessMsg('Revision submitted for re-review.');
      const updated = await api.getDepartmentProposals();
      setProposals(updated || []);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      alert(err.message || 'Resubmission failed.');
    } finally {
      setRevisionSubmitting(false);
    }
  };

  const dept = currentUser?.department || 'Assigned Department';
  const scope = currentUser?.state_scope ? ` (${currentUser.state_scope})` : ' (Central / All-India)';

  const filteredSchemes = schemes.filter(s =>
    !schemeSearch ||
    (s.display_name && s.display_name.toLowerCase().includes(schemeSearch.toLowerCase())) ||
    (s.slug && s.slug.toLowerCase().includes(schemeSearch.toLowerCase()))
  );

  const filteredProposals = proposals.filter(p =>
    proposalFilter === 'all' || p.status === proposalFilter
  );

  return (
    <div style={{ paddingBottom: 'var(--space-3xl)' }}>
      {/* ── 1. Role & Department Identity Banner ─────────────────────── */}
      <div style={{
        background: 'var(--color-navy)',
        color: '#fff',
        padding: '24px 0',
        borderBottom: '3px solid var(--color-saffron)',
        marginBottom: 'var(--space-xl)',
      }}>
        <div className="civic-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <span style={{ fontSize: '1.6rem' }}>🏢</span>
              <h1 style={{ color: '#fff', fontSize: '1.45rem', margin: 0, fontFamily: 'var(--font-serif)' }}>
                Department Operations Platform
              </h1>
              <span style={{
                backgroundColor: 'rgba(231,169,59,0.2)',
                color: 'var(--color-saffron)',
                border: '1px solid var(--color-saffron)',
                fontSize: '0.7rem',
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.04em'
              }}>
                Authoritative Workspace
              </span>
            </div>
            <div style={{ fontSize: '0.875rem', color: '#CBD5E1' }}>
              <strong>{dept}</strong>{scope}
              {currentUser?.designation ? ` • ${currentUser.designation}` : ''}
              {currentUser?.email ? ` • ${currentUser.email}` : ''}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn btn-sm btn-primary"
              style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
              onClick={() => { setActiveTab('radar'); }}
            >
              🎯 Rule Change Radar
            </button>
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => setShowProposalModal(true)}
            >
              ✍️ New Proposal
            </button>
            <button
              className="btn btn-sm"
              onClick={loadDepartmentData}
              style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.25)', color: '#fff' }}
            >
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="civic-container">
        {/* ── 2. Primary Navigation Tabs ────────────────────────────────── */}
        <div style={{
          display: 'flex', gap: '4px',
          borderBottom: '2px solid var(--color-border)',
          marginBottom: 'var(--space-xl)',
          overflowX: 'auto',
        }}>
          {[
            { key: 'overview',   icon: '📊', label: 'Workbench Overview' },
            { key: 'schemes',    icon: '📋', label: `Assigned Schemes (${schemes.length})` },
            { key: 'radar',      icon: '🎯', label: `Rule Change Radar (${radarRecords.length})` },
            { key: 'evidence',   icon: '📎', label: `Evidence-Linked Editor (${evidenceList.length})` },
            { key: 'heatmap',    icon: '🔥', label: 'Citizen Difficulty Heatmap' },
            { key: 'drift',      icon: '🌐', label: `Translation Drift (${driftAlerts.length})` },
            { key: 'proposals',  icon: '📝', label: `Proposals (${proposals.length})` },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => { setActiveTab(tab.key); setError(''); setSuccessMsg(''); }}
              className={activeTab === tab.key ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-secondary'}
              style={{
                borderRadius: 'var(--border-radius) var(--border-radius) 0 0',
                borderBottom: activeTab === tab.key ? '3px solid var(--color-teal)' : '3px solid transparent',
                whiteSpace: 'nowrap',
                fontWeight: activeTab === tab.key ? 800 : 600,
              }}
            >
              <span>{tab.icon}</span> {tab.label}
            </button>
          ))}
        </div>

        {/* ── Alert Banners ────────────────────────────────────────────── */}
        {isLoading && (
          <div className="civic-card" style={{ textAlign: 'center', padding: 'var(--space-2xl)', color: 'var(--color-text-muted)' }}>
            <div style={{ fontSize: '1.75rem', marginBottom: '8px' }}>⏳</div>
            Loading department records and authoritative evidence…
          </div>
        )}

        {error && (
          <div className="gov-alert-error" role="alert" style={{ marginBottom: '16px' }}>
            ✕ {error}
          </div>
        )}

        {successMsg && (
          <div className="gov-alert-success" role="status" style={{ marginBottom: '16px' }}>
            ✓ {successMsg}
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            TAB 1: WORKBENCH OVERVIEW
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === 'overview' && stats && (
          <div>
            {/* Real Stats Metric Cards */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
              gap: '16px',
              marginBottom: 'var(--space-2xl)',
            }}>
              <div className="civic-card" style={{ padding: '18px', borderLeft: '4px solid var(--color-navy)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Assigned Schemes
                </div>
                <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-navy)', fontFamily: 'var(--font-serif)', marginTop: '4px' }}>
                  {stats.total_schemes}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                  Active in Department Catalogue
                </div>
              </div>

              <div className="civic-card" style={{ padding: '18px', borderLeft: '4px solid #1D4ED8' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Active Change Sets
                </div>
                <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#1D4ED8', fontFamily: 'var(--font-serif)', marginTop: '4px' }}>
                  {radarRecords.filter(r => r.status === 'submitted' || r.status === 'draft').length}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                  Radar rule comparisons in flight
                </div>
              </div>

              <div className="civic-card" style={{ padding: '18px', borderLeft: '4px solid var(--color-teal)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Verified Field Evidence
                </div>
                <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-teal)', fontFamily: 'var(--font-serif)', marginTop: '4px' }}>
                  {evidenceSummary ? evidenceSummary.verified_claims : evidenceList.filter(e => e.verification_status === 'verified').length}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                  {evidenceSummary ? `${evidenceSummary.total_claims} total documented claims` : 'Claims with verified source citations'}
                </div>
              </div>

              <div className="civic-card" style={{ padding: '18px', borderLeft: '4px solid var(--color-saffron)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Translation Drift Alerts
                </div>
                <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-saffron-dark)', fontFamily: 'var(--font-serif)', marginTop: '4px' }}>
                  {driftAlerts.length}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                  Language versions needing update
                </div>
              </div>

              <div className="civic-card" style={{ padding: '18px', borderLeft: '4px solid #7B341E' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Outdated Source Reviews
                </div>
                <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#7B341E', fontFamily: 'var(--font-serif)', marginTop: '4px' }}>
                  {evidenceSummary ? evidenceSummary.outdated_reviews : 0}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                  Reviews &gt; 180 days old
                </div>
              </div>
            </div>

            {/* Quick Actions & Department Work Queue */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '20px', alignItems: 'start' }}>
              <div className="civic-card">
                <div className="civic-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                      Operational Action Items
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                      Tasks requiring official verification or revision in {dept}
                    </p>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {evidenceSummary && evidenceSummary.broken_or_unreachable_urls > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', backgroundColor: '#FEF2F2', borderRadius: '6px', border: '1px solid #FECACA' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '1.2rem' }}>⚠️</span>
                        <div>
                          <strong style={{ fontSize: '0.875rem', color: '#991B1B' }}>Broken or Unreachable Source URLs Detected</strong>
                          <div style={{ fontSize: '0.75rem', color: '#7F1D1D' }}>{evidenceSummary.broken_or_unreachable_urls} scheme claims have dead external links.</div>
                        </div>
                      </div>
                      <button className="btn btn-sm btn-secondary" onClick={() => setActiveTab('evidence')}>Fix Evidence</button>
                    </div>
                  )}

                  {driftAlerts.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', backgroundColor: '#FFFBEB', borderRadius: '6px', border: '1px solid #FDE68A' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '1.2rem' }}>🌐</span>
                        <div>
                          <strong style={{ fontSize: '0.875rem', color: '#92400E' }}>Translation Drift Detected</strong>
                          <div style={{ fontSize: '0.75rem', color: '#78350F' }}>{driftAlerts.length} language translations are outdated following recent scheme updates.</div>
                        </div>
                      </div>
                      <button className="btn btn-sm btn-secondary" onClick={() => setActiveTab('drift')}>Review Drift</button>
                    </div>
                  )}

                  {proposals.filter(p => p.status === 'revision_required').length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', backgroundColor: '#EFF6FF', borderRadius: '6px', border: '1px solid #BFDBFE' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '1.2rem' }}>📝</span>
                        <div>
                          <strong style={{ fontSize: '0.875rem', color: '#1E40AF' }}>Revisions Requested by Administrator</strong>
                          <div style={{ fontSize: '0.75rem', color: '#1E3A8A' }}>Proposals awaiting your updated evidence or clarifications.</div>
                        </div>
                      </div>
                      <button className="btn btn-sm btn-secondary" onClick={() => setActiveTab('proposals')}>Respond</button>
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', backgroundColor: '#F8FAFC', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '1.2rem' }}>🎯</span>
                      <div>
                        <strong style={{ fontSize: '0.875rem', color: '#334155' }}>Maintain Scheme Accuracy with Rule Change Radar</strong>
                        <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Analyze fresh gazette notifications or department website updates against published records.</div>
                      </div>
                    </div>
                    <button className="btn btn-sm btn-primary" style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }} onClick={() => setActiveTab('radar')}>
                      Run Radar
                    </button>
                  </div>
                </div>
              </div>

              {/* Department Summary & Coverage Info */}
              <div className="civic-card">
                <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)', marginBottom: '12px' }}>
                  Authoritative Metadata
                </h3>
                <div style={{ fontSize: '0.8125rem', color: '#334155', display: 'grid', gap: '8px' }}>
                  <div><strong>Ministry / Dept:</strong> {dept}</div>
                  <div><strong>Jurisdictional Scope:</strong> {currentUser?.state_scope || 'Central / All-India'}</div>
                  <div><strong>Official Identifier:</strong> {currentUser?.identifier}</div>
                  <div><strong>Designation:</strong> {currentUser?.designation || 'Department Nodal Officer'}</div>
                  <div><strong>Active Schemes Managed:</strong> {schemes.length}</div>
                  <div><strong>Total Proposals Submitted:</strong> {proposals.length}</div>
                </div>

                <div style={{ marginTop: '16px', padding: '10px 12px', backgroundColor: '#F1F5F9', borderRadius: '6px', fontSize: '0.75rem', color: '#475569' }}>
                  <strong>Separation of Duties Notice:</strong> Department Officials can submit scheme rule changes, link evidence, and propose revisions. Final publication requires Principal Administrator approval.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            TAB 2: ASSIGNED SCHEMES
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === 'schemes' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
              <input
                type="text"
                placeholder="Search assigned schemes by name or code..."
                value={schemeSearch}
                onChange={(e) => setSchemeSearch(e.target.value)}
                style={{
                  padding: '9px 14px',
                  borderRadius: '6px',
                  border: '1px solid var(--color-border)',
                  fontSize: '0.875rem',
                  width: '320px',
                }}
              />
              <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                Showing {filteredSchemes.length} of {schemes.length} assigned schemes
              </div>
            </div>

            {filteredSchemes.length === 0 ? (
              <div className="civic-card" style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                📭 No matching schemes found for this department.
              </div>
            ) : (
              <div style={{ display: 'grid', gap: '14px' }}>
                {filteredSchemes.map((s) => (
                  <div key={s.id} className="civic-card" style={{ padding: '18px', marginBottom: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
                      <div style={{ flex: 1, minWidth: '280px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <span style={{ fontSize: '0.75rem', backgroundColor: '#F1F5F9', color: '#475569', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
                            {s.slug}
                          </span>
                          <span style={{ fontSize: '0.75rem', backgroundColor: '#EFF6FF', color: '#1D4ED8', padding: '2px 6px', borderRadius: '4px', textTransform: 'uppercase', fontWeight: 700 }}>
                            {s.category || 'General'}
                          </span>
                        </div>
                        <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                          {s.display_name}
                        </h3>
                        <p style={{ margin: '6px 0 0 0', fontSize: '0.8125rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                          {s.description || 'No description provided.'}
                        </p>
                      </div>

                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                        <button
                          className="btn btn-sm btn-primary"
                          style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                          onClick={() => {
                            setSelectedSchemeId(s.id);
                            setActiveTab('radar');
                          }}
                        >
                          🎯 Scan Changes (Radar)
                        </button>
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => {
                            setEvidenceForm(prev => ({ ...prev, scheme_id: s.id }));
                            setShowEvidenceModal(true);
                          }}
                        >
                          📎 Link Evidence
                        </button>
                        {s.official_portal_url && (
                          <a
                            href={s.official_portal_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-sm btn-secondary"
                            style={{ textDecoration: 'none' }}
                          >
                            🔗 Official Portal
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            TAB 3: SCHEME RULE CHANGE RADAR (Priority 2)
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === 'radar' && (
          <div>
            <div className="civic-card" style={{ marginBottom: 'var(--space-xl)' }}>
              <div className="civic-card-header">
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--color-navy)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>🎯</span>
                  <span>Scheme Rule Change Radar Engine</span>
                </h3>
                <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                  Submit newer official gazette notifications, department circulars, or revised URLs to extract candidate changes and compare with the published baseline.
                </p>
              </div>

              <form onSubmit={handleAnalyzeRadar}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                      Select Assigned Scheme *
                    </label>
                    <select
                      value={selectedSchemeId}
                      onChange={(e) => setSelectedSchemeId(e.target.value)}
                      required
                      style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                    >
                      <option value="">-- Choose Scheme --</option>
                      {schemes.map((s) => (
                        <option key={s.id} value={s.id}>{s.display_name} ({s.slug})</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                      Source Notification Version / Identifier
                    </label>
                    <input
                      type="text"
                      value={sourceVersionInput}
                      onChange={(e) => setSourceVersionInput(e.target.value)}
                      placeholder="e.g. Gazette Ref #2026/04-A, Circular v2.4"
                      style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '14px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                    New Official Source URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={sourceUrlInput}
                    onChange={(e) => setSourceUrlInput(e.target.value)}
                    placeholder="https://official.department.gov.in/scheme-guidelines-2026.pdf"
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                    Paste Source Document / Circular Notification Text *
                  </label>
                  <textarea
                    rows={4}
                    value={docTextInput}
                    onChange={(e) => setDocTextInput(e.target.value)}
                    placeholder="Paste the excerpt of the amended guidelines, revised eligibility conditions, benefit amounts, or application deadlines..."
                    style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.875rem', fontFamily: 'inherit' }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={analyzingRadar}
                    style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                  >
                    {analyzingRadar ? 'Analyzing Rule Changes…' : '🔍 Analyze Rule Differences (Diff)'}
                  </button>
                </div>
              </form>
            </div>

            {/* Radar Analysis Diff View */}
            {radarAnalysisResult && (
              <div className="civic-card" style={{ border: '2px solid var(--color-teal)', marginBottom: 'var(--space-xl)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
                  <div>
                    <span style={{
                      backgroundColor: radarAnalysisResult.change_magnitude === 'major' ? '#FEE2E2' : '#FEF3C7',
                      color: radarAnalysisResult.change_magnitude === 'major' ? '#991B1B' : '#92400E',
                      fontSize: '0.75rem',
                      fontWeight: 800,
                      padding: '3px 8px',
                      borderRadius: '4px',
                      textTransform: 'uppercase',
                    }}>
                      Magnitude: {radarAnalysisResult.change_magnitude}
                    </span>
                    <h3 style={{ margin: '6px 0 0 0', fontSize: '1.2rem', color: 'var(--color-navy)' }}>
                      Detected Rule Changes for: {radarAnalysisResult.scheme_name}
                    </h3>
                  </div>

                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleSubmitRadarCandidate}
                    disabled={submittingRadar}
                    style={{ backgroundColor: 'var(--color-navy)', borderColor: 'var(--color-navy)' }}
                  >
                    {submittingRadar ? 'Submitting…' : '✅ Submit Draft Change Set to Administrator'}
                  </button>
                </div>

                <p style={{ fontSize: '0.875rem', color: '#334155', lineHeight: 1.5 }}>
                  {radarAnalysisResult.summary}
                </p>

                {/* Diff Viewer Grid */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '16px',
                  backgroundColor: '#F8FAFC',
                  padding: '16px',
                  borderRadius: '8px',
                  border: '1px solid #E2E8F0',
                  marginTop: '14px',
                }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', marginBottom: '8px' }}>
                      Currently Published Baseline
                    </div>
                    <pre style={{ margin: 0, padding: '12px', backgroundColor: '#FFFFFF', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.8125rem', overflowX: 'auto', whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(radarAnalysisResult.published_baseline, null, 2)}
                    </pre>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-teal)', textTransform: 'uppercase', marginBottom: '8px' }}>
                      Candidate Extracted Content (Newer Source)
                    </div>
                    <pre style={{ margin: 0, padding: '12px', backgroundColor: '#F0FDFA', borderRadius: '6px', border: '1px solid #99F6E4', fontSize: '0.8125rem', overflowX: 'auto', whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(radarAnalysisResult.candidate_content, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Supporting Source Passage Citation */}
                <div style={{ marginTop: '14px', padding: '12px 14px', backgroundColor: '#FFFBEB', borderRadius: '6px', border: '1px solid #FDE68A' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#92400E', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Supporting Source Citation Evidence:
                  </div>
                  <div style={{ fontSize: '0.8125rem', color: '#78350F', fontStyle: 'italic' }}>
                    "{radarAnalysisResult.supporting_passage}"
                  </div>
                </div>
              </div>
            )}

            {/* Radar History Table */}
            <div className="civic-card">
              <h3 style={{ margin: '0 0 14px 0', fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                Department Change Set Submission Queue
              </h3>

              {radarRecords.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-text-muted)' }}>
                  No radar change sets created yet for this department. Use the analyzer above to create one.
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>ID / Ref</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Scheme</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Version</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Magnitude</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Submitted At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {radarRecords.map((r) => (
                        <tr key={r.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                          <td style={{ padding: '10px 12px', fontFamily: 'monospace', fontWeight: 700 }}>#{r.id}</td>
                          <td style={{ padding: '10px 12px', fontWeight: 600 }}>{r.scheme_id}</td>
                          <td style={{ padding: '10px 12px' }}>{r.source_version || 'v2026'}</td>
                          <td style={{ padding: '10px 12px' }}>
                            <span style={{ textTransform: 'capitalize', fontWeight: 600 }}>{r.change_magnitude}</span>
                          </td>
                          <td style={{ padding: '10px 12px' }}>
                            <StatusBadge status={r.status} />
                          </td>
                          <td style={{ padding: '10px 12px', color: '#64748B' }}>
                            {new Date(r.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            TAB 4: EVIDENCE-LINKED SCHEME EDITOR (Priority 4)
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === 'evidence' && (
          <div>
            {/* Evidence Diagnostic Summary Banner */}
            {evidenceSummary && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
                gap: '12px',
                marginBottom: 'var(--space-xl)',
              }}>
                <div className="civic-card" style={{ padding: '14px', marginBottom: 0 }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Total Linked Claims</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--color-navy)' }}>
                    {evidenceSummary.total_claims}
                  </div>
                </div>

                <div className="civic-card" style={{ padding: '14px', marginBottom: 0 }}>
                  <div style={{ fontSize: '0.75rem', color: '#166534' }}>Verified Claims</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#166534' }}>
                    {evidenceSummary.verified_claims}
                  </div>
                </div>

                <div className="civic-card" style={{ padding: '14px', marginBottom: 0 }}>
                  <div style={{ fontSize: '0.75rem', color: '#DC2626' }}>Broken / Unreachable URLs</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#DC2626' }}>
                    {evidenceSummary.broken_or_unreachable_urls}
                  </div>
                </div>

                <div className="civic-card" style={{ padding: '14px', marginBottom: 0 }}>
                  <div style={{ fontSize: '0.75rem', color: '#92400E' }}>Outdated Reviews (&gt;180d)</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#92400E' }}>
                    {evidenceSummary.outdated_reviews}
                  </div>
                </div>

                <div className="civic-card" style={{ padding: '14px', marginBottom: 0 }}>
                  <div style={{ fontSize: '0.75rem', color: '#B45309' }}>Unverified Benefit Claims</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#B45309' }}>
                    {evidenceSummary.unverified_benefit_amounts}
                  </div>
                </div>
              </div>
            )}

            <div className="civic-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.15rem', color: 'var(--color-navy)' }}>
                    Traceable Field-Level Source Evidence
                  </h3>
                  <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                    Every factual scheme parameter must link to an official government URL and supporting citation.
                  </p>
                </div>

                <button
                  type="button"
                  className="btn btn-sm btn-primary"
                  onClick={() => setShowEvidenceModal(true)}
                  style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
                >
                  ✚ Link New Evidence Citation
                </button>
              </div>

              {evidenceList.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>
                  No field evidence recorded yet. Click "Link New Evidence Citation" above to add traceable source citations.
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Scheme</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Field Name</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Claim Content</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Official URL & Citation</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evidenceList.map((ev) => (
                        <tr key={ev.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                          <td style={{ padding: '10px 12px', fontWeight: 700 }}>#{ev.scheme_id}</td>
                          <td style={{ padding: '10px 12px', fontFamily: 'monospace', color: '#1D4ED8' }}>{ev.field_name}</td>
                          <td style={{ padding: '10px 12px', maxWidth: '240px' }}>{ev.claim_value}</td>
                          <td style={{ padding: '10px 12px', maxWidth: '300px' }}>
                            <a href={ev.source_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-teal)', fontWeight: 600 }}>
                              🔗 {ev.source_title || ev.source_url}
                            </a>
                            {ev.quotation_or_section && (
                              <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '2px', fontStyle: 'italic' }}>
                                Quotation: "{ev.quotation_or_section}"
                              </div>
                            )}
                          </td>
                          <td style={{ padding: '10px 12px' }}>
                            <StatusBadge status={ev.verification_status} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            TAB 5: CITIZEN DIFFICULTY HEATMAP (Priority 3)
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === 'heatmap' && (
          <div>
            <div className="civic-card" style={{ marginBottom: 'var(--space-xl)' }}>
              <div className="civic-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--color-navy)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>🔥</span>
                    <span>Citizen Difficulty Heatmap (Privacy Safeguarded)</span>
                  </h3>
                  <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                    Identifies form friction, confusing fields, and abandonment points across {dept} schemes without identifying individual citizens.
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

                  <select
                    value={heatmapStepFilter}
                    onChange={(e) => setHeatmapStepFilter(e.target.value)}
                    style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.8125rem' }}
                  >
                    <option value="">All Form Steps</option>
                    <option value="step_1">Step 1: Basic Profile</option>
                    <option value="step_2">Step 2: Eligibility Check</option>
                    <option value="step_3">Step 3: Document Upload</option>
                    <option value="step_4">Step 4: Submission</option>
                  </select>
                </div>
              </div>

              {loadingHeatmap ? (
                <div style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                  Loading aggregated privacy metrics…
                </div>
              ) : heatmapData?.is_insufficient_data ? (
                /* Strict Privacy Protection Rule: < 3 sessions */
                <div style={{
                  padding: '32px',
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
                    {heatmapData.message || 'In accordance with privacy safeguards, difficulty charts are hidden until at least 3 completed citizen sessions exist within this filter to prevent de-anonymization.'}
                  </p>
                </div>
              ) : heatmapData ? (
                <div>
                  {/* Aggregated Heatmap Metric Cards */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px', marginBottom: '20px' }}>
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

                  {/* Confusing Fields Breakdown */}
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '0.95rem', color: 'var(--color-navy)' }}>
                    Top Confusing Form Fields
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {(heatmapData.confusing_fields || []).map((cf, idx) => (
                      <div key={idx} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '10px 14px',
                        backgroundColor: '#FFFFFF',
                        border: '1px solid var(--color-border)',
                        borderRadius: '6px',
                      }}>
                        <div>
                          <strong style={{ fontSize: '0.875rem', color: 'var(--color-navy)' }}>{cf.field_name}</strong>
                          <span style={{ fontSize: '0.75rem', color: '#64748B', marginLeft: '8px' }}>({cf.form_step})</span>
                          <div style={{ fontSize: '0.75rem', color: '#DC2626', marginTop: '2px' }}>
                            Top Error: {cf.top_error_category}
                          </div>
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
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            TAB 6: TRANSLATION DRIFT MONITOR (Priority 5)
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === 'drift' && (
          <div>
            <div className="civic-card">
              <div className="civic-card-header">
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--color-navy)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>🌐</span>
                  <span>Translation Drift Monitor (22 Scheduled Languages)</span>
                </h3>
                <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                  When approved scheme rules change in the master language, translated versions are flagged here to ensure citizens in all 22 languages receive accurate eligibility and benefit information.
                </p>
              </div>

              {driftAlerts.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                  ✅ No active translation drift alerts for this department. All language translations are in sync.
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '2px solid var(--color-border)' }}>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Scheme</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Language</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Field Name</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Drift Reason</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Status</th>
                        <th style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--color-navy)' }}>Detected At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {driftAlerts.map((d) => (
                        <tr key={d.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                          <td style={{ padding: '10px 12px', fontWeight: 700 }}>#{d.scheme_id}</td>
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
                            <StatusBadge status={d.status} />
                          </td>
                          <td style={{ padding: '10px 12px', color: '#64748B' }}>
                            {new Date(d.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            TAB 7: PROPOSALS & REVISIONS LIFECYCLE
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === 'proposals' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: '#334155' }}>Status:</span>
                <select
                  value={proposalFilter}
                  onChange={(e) => setProposalFilter(e.target.value)}
                  style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.8125rem' }}
                >
                  <option value="all">All Proposals</option>
                  <option value="draft">Draft</option>
                  <option value="submitted">Submitted</option>
                  <option value="under_review">Under Review</option>
                  <option value="revision_required">Revision Required</option>
                  <option value="approved">Approved</option>
                  <option value="published">Published</option>
                </select>
              </div>

              <button
                type="button"
                className="btn btn-sm btn-primary"
                onClick={() => setShowProposalModal(true)}
                style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}
              >
                ✍️ Create Scheme Proposal
              </button>
            </div>

            {filteredProposals.length === 0 ? (
              <div className="civic-card" style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
                No proposals found under this filter.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {filteredProposals.map((prop) => (
                  <div key={prop.id} className="civic-card" style={{ padding: '16px', marginBottom: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <span style={{ fontWeight: 800, color: 'var(--color-navy)', fontSize: '1rem' }}>
                            {prop.scheme_name}
                          </span>
                          <span style={{ fontSize: '0.75rem', backgroundColor: '#F1F5F9', color: '#475569', padding: '2px 6px', borderRadius: '4px', textTransform: 'capitalize' }}>
                            {prop.proposal_type.replace(/_/g, ' ')}
                          </span>
                        </div>
                        <p style={{ margin: '4px 0 0 0', fontSize: '0.8125rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                          {prop.description}
                        </p>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <StatusBadge status={prop.status} />
                        {prop.status === 'revision_required' && (
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() => { setRevisionModal(prop); setRevisionText(''); }}
                            style={{ backgroundColor: '#B45309', borderColor: '#B45309' }}
                          >
                            Respond to Revision
                          </button>
                        )}
                      </div>
                    </div>

                    {prop.review_notes && (
                      <div style={{ marginTop: '10px', padding: '8px 12px', backgroundColor: '#FEF3C7', borderRadius: '4px', border: '1px solid #FDE68A', fontSize: '0.75rem', color: '#92400E' }}>
                        <strong>Administrator Feedback:</strong> {prop.review_notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Modal: Create New Proposal ────────────────────────────────── */}
      {showProposalModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
        }}>
          <div style={{ backgroundColor: '#fff', borderRadius: '12px', maxWidth: '580px', width: '100%', padding: '24px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                ✍️ Create Scheme Proposal
              </h3>
              <button type="button" onClick={() => setShowProposalModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.4rem', cursor: 'pointer', color: '#64748B' }}>✕</button>
            </div>

            <form onSubmit={handleProposalSubmit}>
              <div style={{ display: 'grid', gap: '12px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Proposal Type *</label>
                  <select
                    value={proposalForm.proposal_type}
                    onChange={(e) => setProposalForm(prev => ({ ...prev, proposal_type: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  >
                    <option value="new_scheme">New Scheme Addition</option>
                    <option value="eligibility_update">Eligibility Rule Update</option>
                    <option value="benefit_update">Benefit Amount Revision</option>
                    <option value="url_correction">Official URL Correction</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Scheme Name *</label>
                  <input
                    type="text"
                    required
                    value={proposalForm.scheme_name}
                    onChange={(e) => setProposalForm(prev => ({ ...prev, scheme_name: e.target.value }))}
                    placeholder="e.g. Pradhan Mantri Kisan Samman Nidhi (Amended 2026)"
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Description *</label>
                  <textarea
                    rows={3}
                    required
                    value={proposalForm.description}
                    onChange={(e) => setProposalForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Provide details about this scheme proposal..."
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Official Source URL</label>
                  <input
                    type="url"
                    value={proposalForm.official_source_url}
                    onChange={(e) => setProposalForm(prev => ({ ...prev, official_source_url: e.target.value }))}
                    placeholder="https://..."
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Source Evidence Quotation *</label>
                  <textarea
                    rows={2}
                    required
                    value={proposalForm.source_evidence}
                    onChange={(e) => setProposalForm(prev => ({ ...prev, source_evidence: e.target.value }))}
                    placeholder="Exact gazette paragraph or section citation..."
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowProposalModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={proposalSubmitting} style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}>
                  {proposalSubmitting ? 'Submitting…' : 'Submit for Admin Review'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal: Link Field Evidence ─────────────────────────────────── */}
      {showEvidenceModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
        }}>
          <div style={{ backgroundColor: '#fff', borderRadius: '12px', maxWidth: '540px', width: '100%', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                📎 Link Field-Level Evidence Citation
              </h3>
              <button type="button" onClick={() => setShowEvidenceModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.4rem', cursor: 'pointer', color: '#64748B' }}>✕</button>
            </div>

            <form onSubmit={handleSubmitEvidence}>
              <div style={{ display: 'grid', gap: '12px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Scheme *</label>
                  <select
                    value={evidenceForm.scheme_id}
                    onChange={(e) => setEvidenceForm(prev => ({ ...prev, scheme_id: e.target.value }))}
                    required
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  >
                    <option value="">-- Choose Scheme --</option>
                    {schemes.map(s => <option key={s.id} value={s.id}>{s.display_name}</option>)}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Field Name *</label>
                  <select
                    value={evidenceForm.field_name}
                    onChange={(e) => setEvidenceForm(prev => ({ ...prev, field_name: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  >
                    <option value="eligibility_criteria">Eligibility Criteria</option>
                    <option value="benefit_amount">Benefit Amount</option>
                    <option value="required_documents">Required Documents</option>
                    <option value="official_source_url">Official Portal Link</option>
                    <option value="application_instructions">Application Instructions</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Claim Value / Parameter *</label>
                  <input
                    type="text"
                    required
                    value={evidenceForm.claim_value}
                    onChange={(e) => setEvidenceForm(prev => ({ ...prev, claim_value: e.target.value }))}
                    placeholder="e.g. ₹6,000 per annum paid in 3 instalments"
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Official Source URL *</label>
                  <input
                    type="url"
                    required
                    value={evidenceForm.source_url}
                    onChange={(e) => setEvidenceForm(prev => ({ ...prev, source_url: e.target.value }))}
                    placeholder="https://pmkisan.gov.in/guidelines.pdf"
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Supporting Quotation / Page & Section</label>
                  <textarea
                    rows={2}
                    value={evidenceForm.quotation_or_section}
                    onChange={(e) => setEvidenceForm(prev => ({ ...prev, quotation_or_section: e.target.value }))}
                    placeholder="e.g. Section 4.1, Page 12: 'Eligible landholder farmer families will receive...'"
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowEvidenceModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={evidenceSubmitting} style={{ backgroundColor: 'var(--color-teal)', borderColor: 'var(--color-teal)' }}>
                  {evidenceSubmitting ? 'Linking…' : 'Save & Link Citation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal: Revision Response ──────────────────────────────────── */}
      {revisionModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
        }}>
          <div style={{ backgroundColor: '#fff', borderRadius: '12px', maxWidth: '520px', width: '100%', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--color-navy)', fontWeight: 800 }}>
                Respond to Revision Request
              </h3>
              <button type="button" onClick={() => setRevisionModal(null)} style={{ background: 'none', border: 'none', fontSize: '1.4rem', cursor: 'pointer', color: '#64748B' }}>✕</button>
            </div>

            <div style={{ padding: '10px 12px', backgroundColor: '#FEF3C7', borderRadius: '6px', marginBottom: '14px', fontSize: '0.8125rem', color: '#92400E' }}>
              <strong>Administrator Feedback:</strong> {revisionModal.review_notes || 'Please provide updated documentation or citation.'}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>Updated Evidence or Clarification *</label>
              <textarea
                rows={4}
                required
                value={revisionText}
                onChange={(e) => setRevisionText(e.target.value)}
                placeholder="Explain the correction and supply verified source evidence..."
                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', marginBottom: '16px' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button type="button" className="btn btn-secondary" onClick={() => setRevisionModal(null)}>Cancel</button>
              <button
                type="button"
                className="btn btn-primary"
                disabled={revisionSubmitting || !revisionText.trim()}
                onClick={() => handleRevisionResubmit(revisionModal.id)}
                style={{ backgroundColor: 'var(--color-navy)', borderColor: 'var(--color-navy)' }}
              >
                {revisionSubmitting ? 'Resubmitting…' : 'Submit Revision'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
