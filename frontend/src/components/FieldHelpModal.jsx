import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Badge } from './Badge';

/**
 * FieldHelpModal — "Are you facing any difficulty?" overlay.
 *
 * Common Difficulty buttons now show real help panels:
 *   confusing_question  → simplified explanation + example
 *   missing_document    → document checklist guidance
 *   language_difficulty → language-switch prompt + terminology tips
 *   validation_error    → accepted-format tips + what to do next
 *
 * "Issue Resolved" → honest Yes/No confirmation flow.
 */
export function FieldHelpModal({
  isOpen,
  onClose,
  field,
  explanationData,
  onResolveIssue,     // (actionType: string, resolved?: boolean) => void
  onEscalateToHuman,
  onSwitchLanguage,   // optional: () => void  — opens language selector
}) {
  const { t } = useTranslation();

  // Which difficulty panel is active: null | 'confusing_question' | 'missing_document' | 'language_difficulty' | 'validation_error'
  const [activePanel, setActivePanel] = useState(null);

  // Honest resolution flow: null → 'ask' → 'resolved' | 'unresolved'
  const [resolvedState, setResolvedState] = useState(null); // null | 'ask' | 'yes' | 'no'

  if (!isOpen || !field) return null;

  const fieldLabel = explanationData?.localized_label || field.field_key;
  const fieldExplanation =
    explanationData?.localized_explanation ||
    field.explanations_by_language?.[field.lang] ||
    explanationData?.localized_explanation ||
    t('barriers.noExplanation', 'Please fill this field according to your official documents.');

  const handleDifficultyClick = (type) => {
    setActivePanel((prev) => (prev === type ? null : type));
    setResolvedState(null);
    // Log barrier selection
    if (onResolveIssue) onResolveIssue(type, false);
  };

  const handleMarkResolved = () => {
    setResolvedState('ask');
  };

  const handleResolvedYes = () => {
    setResolvedState('yes');
    if (onResolveIssue) onResolveIssue('resolved', true);
    setTimeout(onClose, 1200);
  };

  const handleResolvedNo = () => {
    setResolvedState('no');
    if (onResolveIssue) onResolveIssue('unresolved_after_ask', false);
  };

  const panelStyle = {
    backgroundColor: 'var(--color-surface-subtle)',
    border: '1px solid var(--color-teal)',
    borderRadius: 'var(--border-radius)',
    padding: '14px 16px',
    marginTop: '8px',
    marginBottom: '4px',
    fontSize: '0.9rem',
    lineHeight: '1.6',
    animation: 'fadeSlideIn 0.18s ease',
  };

  return (
    <div
      className="civic-modal-backdrop"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="help-modal-title"
    >
      <div className="civic-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '560px' }}>

        {/* ── Header ─────────────────────────────────────────── */}
        <div className="civic-modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '1.25rem' }}>💡</span>
              <h3 id="help-modal-title" style={{ margin: 0 }}>
                {t('barriers.title')}
              </h3>
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
              {t('form.fieldOf')}: <strong>{fieldLabel}</strong>
            </div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose} aria-label={t('common.close')}>
            ✕
          </button>
        </div>

        {/* ── Translation Quality Badge ───────────────────────── */}
        {explanationData && (
          <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
              {t('form.translationStatus')}:
            </span>
            <Badge variant={explanationData.translation_status}>
              {explanationData.translation_status === 'approved' || explanationData.translation_status === 'reviewed'
                ? t('form.reviewed')
                : explanationData.translation_status === 'missing'
                ? t('form.missingTranslation')
                : t('form.unreviewed')}
            </Badge>
          </div>
        )}

        {/* ── Simplified Explanation ──────────────────────────── */}
        <div
          style={{
            backgroundColor: 'var(--color-surface-subtle)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--border-radius)',
            padding: '14px',
            marginBottom: '16px',
          }}
        >
          <div style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--color-navy)', marginBottom: '4px' }}>
            {t('barriers.simplifiedExplanation')}
          </div>
          <p style={{ margin: 0, fontSize: '0.9375rem', lineHeight: '1.5' }}>
            {fieldExplanation}
          </p>
        </div>

        {/* ── Fallback warning ────────────────────────────────── */}
        {explanationData?.is_fallback && (
          <div
            style={{
              backgroundColor: 'var(--color-error-bg)',
              border: '1px solid var(--color-error-border)',
              borderRadius: 'var(--border-radius)',
              padding: '12px',
              fontSize: '0.875rem',
              color: 'var(--color-error)',
              marginBottom: '16px',
            }}
          >
            ⚠️ {explanationData.human_assistance_path}
          </div>
        )}

        {/* ── Common Difficulties ─────────────────────────────── */}
        <div style={{ marginBottom: '18px' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '8px' }}>
            {t('barriers.commonIssues')}:
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>

            {/* 1. Confusing Question */}
            <button
              className={`btn btn-secondary btn-sm ${activePanel === 'confusing_question' ? 'btn-primary' : ''}`}
              style={{ justifyContent: 'flex-start' }}
              onClick={() => handleDifficultyClick('confusing_question')}
              aria-expanded={activePanel === 'confusing_question'}
            >
              ❓ {t('barriers.issueConfusing')}
            </button>
            {activePanel === 'confusing_question' && (
              <div style={panelStyle}>
                <strong>🔍 {t('barriers.panelConfusing.heading', 'What this question means:')}</strong>
                <p style={{ margin: '8px 0 6px' }}>
                  {fieldExplanation}
                </p>
                <strong>{t('barriers.panelConfusing.exampleHeading', 'Example:')}</strong>
                <p style={{ margin: '6px 0 0', color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>
                  {explanationData?.localized_example ||
                    t('barriers.panelConfusing.exampleFallback',
                      'Fill this field exactly as it appears on your official government document (e.g., Aadhaar card, Ration card, Birth certificate).')}
                </p>
                <div style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                  💡 {t('barriers.panelConfusing.tip', 'Still confused? Try "Request Help Desk Assistance" below — a local CSC volunteer can explain this in person.')}
                </div>
              </div>
            )}

            {/* 2. Missing Document */}
            <button
              className={`btn btn-secondary btn-sm ${activePanel === 'missing_document' ? 'btn-primary' : ''}`}
              style={{ justifyContent: 'flex-start' }}
              onClick={() => handleDifficultyClick('missing_document')}
              aria-expanded={activePanel === 'missing_document'}
            >
              📄 {t('barriers.issueMissingDoc')}
            </button>
            {activePanel === 'missing_document' && (
              <div style={panelStyle}>
                <strong>📋 {t('barriers.panelMissingDoc.heading', 'If you do not have this document:')}</strong>
                <ol style={{ margin: '8px 0 0', paddingLeft: '20px', lineHeight: '1.8' }}>
                  <li>{t('barriers.panelMissingDoc.step1', 'Check whether an alternative document is accepted — for example, a Voter ID or Passport in place of Aadhaar.')}</li>
                  <li>{t('barriers.panelMissingDoc.step2', 'Visit your local Gram Panchayat or Municipal Office to obtain a fresh copy or a certified substitute.')}</li>
                  <li>{t('barriers.panelMissingDoc.step3', 'For income or caste certificates, apply at your nearest Tehsil / Taluk office — a CSC (Common Service Centre) can assist with the application.')}</li>
                  <li>{t('barriers.panelMissingDoc.step4', 'You may be able to proceed without this document today and submit it later — check the scheme\'s submission rules.')}</li>
                </ol>
                <div style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                  🏛️ {t('barriers.panelMissingDoc.cscNote', 'Your nearest CSC can help you apply for most certificates free of charge.')}
                </div>
              </div>
            )}

            {/* 3. Language / Terminology Difficulty */}
            <button
              className={`btn btn-secondary btn-sm ${activePanel === 'language_difficulty' ? 'btn-primary' : ''}`}
              style={{ justifyContent: 'flex-start' }}
              onClick={() => handleDifficultyClick('language_difficulty')}
              aria-expanded={activePanel === 'language_difficulty'}
            >
              🗣️ {t('barriers.issueLanguage')}
            </button>
            {activePanel === 'language_difficulty' && (
              <div style={panelStyle}>
                <strong>🌐 {t('barriers.panelLanguage.heading', 'Language & Terminology Help:')}</strong>
                <p style={{ margin: '8px 0' }}>
                  {t('barriers.panelLanguage.tip1', 'NagrikSaarathi supports all 22 scheduled Indian languages. If this field is hard to understand, try switching to your mother tongue — the explanation will automatically appear in that language.')}
                </p>
                {onSwitchLanguage && (
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ marginBottom: '10px' }}
                    onClick={() => { onSwitchLanguage(); }}
                  >
                    🌐 {t('barriers.panelLanguage.switchBtn', 'Change Application Language')}
                  </button>
                )}
                <p style={{ margin: '0', fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                  {t('barriers.panelLanguage.tip2', 'Technical terms (like "domicile", "encumbrance certificate") are explained in the simplified field description above. If you still need help, the Assistance Desk below connects you to a local language volunteer.')}
                </p>
              </div>
            )}

            {/* 4. Validation Error / Technical Issue */}
            <button
              className={`btn btn-secondary btn-sm ${activePanel === 'validation_error' ? 'btn-primary' : ''}`}
              style={{ justifyContent: 'flex-start' }}
              onClick={() => handleDifficultyClick('validation_error')}
              aria-expanded={activePanel === 'validation_error'}
            >
              ⚙️ {t('barriers.issueTechnical')}
            </button>
            {activePanel === 'validation_error' && (
              <div style={panelStyle}>
                <strong>🛠️ {t('barriers.panelTechnical.heading', 'Common reasons for validation errors:')}</strong>
                <ul style={{ margin: '8px 0 0', paddingLeft: '20px', lineHeight: '1.8' }}>
                  <li>{t('barriers.panelTechnical.tip1', 'Date fields: use the format DD/MM/YYYY (e.g., 15/08/1985).')}</li>
                  <li>{t('barriers.panelTechnical.tip2', 'Phone numbers: enter 10 digits without spaces or dashes.')}</li>
                  <li>{t('barriers.panelTechnical.tip3', 'Aadhaar: enter all 12 digits as printed — no spaces.')}</li>
                  <li>{t('barriers.panelTechnical.tip4', 'Name fields: use only letters and spaces — no punctuation or numbers.')}</li>
                  <li>{t('barriers.panelTechnical.tip5', 'Amounts: enter numbers only — do not include ₹ or commas.')}</li>
                </ul>
                <div style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                  {t('barriers.panelTechnical.reload', 'If the page appears frozen, try refreshing the browser — your progress is saved.')}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── Assistance Desk ─────────────────────────────────── */}
        <div
          style={{
            borderTop: '1px solid var(--color-border-subtle)',
            paddingTop: '14px',
            marginBottom: '16px',
          }}
        >
          <div style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--color-teal-dark)', marginBottom: '4px' }}>
            🏛️ {t('barriers.humanDeskHelp')}
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>
            {t('barriers.humanDeskText')}
          </p>
          <button className="btn btn-saffron btn-sm" onClick={onEscalateToHuman}>
            🤝 {t('barriers.requestHumanEscalation')}
          </button>
        </div>

        {/* ── Honest Resolution Flow ───────────────────────────── */}
        <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '14px' }}>
          {resolvedState === null && (
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px' }}>
              <button className="btn btn-primary btn-sm" onClick={handleMarkResolved}>
                ✓ {t('barriers.markResolved')}
              </button>
              <button className="btn btn-secondary btn-sm" onClick={onClose}>
                {t('common.close')}
              </button>
            </div>
          )}

          {resolvedState === 'ask' && (
            <div
              style={{
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--border-radius)',
                padding: '14px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontWeight: 700, marginBottom: '10px', fontSize: '0.9375rem' }}>
                🤔 {t('barriers.resolvedQuestion', 'Was your problem actually solved?')}
              </div>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
                <button className="btn btn-primary btn-sm" onClick={handleResolvedYes}>
                  ✅ {t('barriers.resolvedYes', 'Yes, it is resolved')}
                </button>
                <button className="btn btn-secondary btn-sm" onClick={handleResolvedNo}>
                  ❌ {t('barriers.resolvedNo', 'No, still having trouble')}
                </button>
              </div>
            </div>
          )}

          {resolvedState === 'yes' && (
            <div
              style={{
                backgroundColor: '#F0FDF4',
                border: '1px solid #86EFAC',
                borderRadius: 'var(--border-radius)',
                padding: '14px',
                textAlign: 'center',
                color: '#166534',
                fontWeight: 600,
              }}
            >
              ✅ {t('barriers.resolvedThanks', 'Great! This issue has been logged as resolved. Closing…')}
            </div>
          )}

          {resolvedState === 'no' && (
            <div
              style={{
                backgroundColor: 'var(--color-error-bg, #FEF2F2)',
                border: '1px solid var(--color-error-border, #FCA5A5)',
                borderRadius: 'var(--border-radius)',
                padding: '14px',
              }}
            >
              <div style={{ fontWeight: 700, color: 'var(--color-error, #B91C1C)', marginBottom: '8px' }}>
                {t('barriers.unresolvedTitle', 'We are sorry this was not resolved.')}
              </div>
              <p style={{ fontSize: '0.875rem', margin: '0 0 10px' }}>
                {t('barriers.unresolvedText', 'Please use the "Request Help Desk Assistance" button above to connect with a local support volunteer who will help you in person or by phone.')}
              </p>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-saffron btn-sm" onClick={onEscalateToHuman}>
                  🤝 {t('barriers.requestHumanEscalation')}
                </button>
                <button className="btn btn-secondary btn-sm" onClick={onClose}>
                  {t('common.close')}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
