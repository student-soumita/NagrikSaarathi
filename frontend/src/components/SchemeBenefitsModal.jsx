import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { SpeechService } from '../services/speech';
import { LANGUAGES_METADATA } from '../i18n';
import { api } from '../services/api';

export function SchemeBenefitsModal({
  isOpen,
  onClose,
  scheme,
  onRequestReview,
}) {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language;
  const currentMeta = LANGUAGES_METADATA.find((l) => l.code === currentLang) || LANGUAGES_METADATA[0];

  const [localizedData, setLocalizedData] = useState(null);
  const [loadingBenefits, setLoadingBenefits] = useState(false);
  const [playbackState, setPlaybackState] = useState('idle'); // 'idle' | 'playing' | 'paused'
  const [audioVoiceInfo, setAudioVoiceInfo] = useState(null);
  const [voiceNotice, setVoiceNotice] = useState(null);

  // Stop audio on close or unmount
  useEffect(() => {
    SpeechService.stopSpeaking();
    setPlaybackState('idle');
    setVoiceNotice(null);
    return () => {
      SpeechService.stopSpeaking();
    };
  }, [isOpen, scheme, currentLang]);

  // Load localized benefit details from multilingual service
  useEffect(() => {
    if (!isOpen || !scheme) return;

    let isMounted = true;
    setLoadingBenefits(true);

    const schemeRef = scheme.id || scheme.slug;
    api.getSchemeBenefits(schemeRef, currentLang)
      .then((data) => {
        if (isMounted) {
          setLocalizedData(data);
          setLoadingBenefits(false);
        }
      })
      .catch((err) => {
        console.warn('Could not fetch localized benefits, using scheme payload:', err);
        if (isMounted) {
          setLocalizedData(scheme.benefit_details || {});
          setLoadingBenefits(false);
        }
      });

    // Check voice support for current language
    const status = SpeechService.getLanguageAudioStatus(currentLang);
    setAudioVoiceInfo(status);

    return () => {
      isMounted = false;
    };
  }, [isOpen, scheme, currentLang]);

  if (!isOpen || !scheme) return null;

  const b = localizedData || scheme.benefit_details || {};
  const isVerified = b.is_verified || scheme.verification_status === 'verified';
  const assistanceType = b.assistance_type || t('benefits.defaultAssistance', 'Welfare Assistance & Citizen Support');
  const benefitAmount = b.benefit_amount;
  const duration = b.frequency_or_duration;
  const benefitsProvided = b.benefits_provided || scheme.description;
  const beneficiaries = b.intended_beneficiaries || scheme.beneficiary_groups || [];
  const conditions = b.conditions_limitations || t('benefits.defaultConditions', 'Subject to verified citizen eligibility rules and valid application submission.');

  const officialSourceUrl = b.official_source_url || scheme.official_source_url || scheme.official_application_url;
  const verificationDate = b.last_verified_at || scheme.last_verified_at;

  // Build spoken guidance text in the citizen's actual active language (never English fallback for other languages)
  const textToRead = [
    scheme.display_name,
    `${t('benefits.assistanceType', 'Assistance Type')}: ${assistanceType}`,
    benefitAmount ? `${t('benefits.amount', 'Benefit Amount')}: ${benefitAmount}` : '',
    duration ? `${t('benefits.duration', 'Duration')}: ${duration}` : '',
    benefitsProvided,
    conditions ? `${t('benefits.conditions', 'Conditions')}: ${conditions}` : '',
  ].filter(Boolean).join('. ');

  const handlePlayAudio = async () => {
    setVoiceNotice(null);
    setPlaybackState('playing');

    const started = await SpeechService.speakGuidance({
      text: textToRead,
      languageCode: currentLang,
      onStart: (info) => {
        setPlaybackState('playing');
        if (info.source === 'cloud') {
          setVoiceNotice(t('audio.cloudNotice', 'Playing via Cloud Audio Synthesis.'));
        }
      },
      onPause: () => setPlaybackState('paused'),
      onResume: () => setPlaybackState('playing'),
      onEnd: () => setPlaybackState('idle'),
      onError: (err, details) => {
        setPlaybackState('idle');
        if (err === 'VOICE_UNAVAILABLE') {
          setVoiceNotice(
            `${currentMeta.nativeName} ${t('audio.voiceUnavailable', 'audio synthesis is unavailable in this browser. Showing full written instructions below.')}`
          );
        } else {
          setVoiceNotice(typeof err === 'string' ? err : 'Speech playback error');
        }
      },
    });

    if (!started && playbackState === 'playing') {
      setPlaybackState('idle');
    }
  };

  const handlePauseAudio = () => {
    SpeechService.pauseSpeaking();
    setPlaybackState('paused');
  };

  const handleResumeAudio = () => {
    SpeechService.resumeSpeaking();
    setPlaybackState('playing');
  };

  const handleStopAudio = () => {
    SpeechService.stopSpeaking();
    setPlaybackState('idle');
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
      aria-labelledby="scheme-benefits-modal-title"
    >
      <div
        className="civic-card"
        style={{
          width: '100%',
          maxWidth: '700px',
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
            alignItems: 'flex-start',
          }}
        >
          <div>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-saffron)', letterSpacing: '0.5px', fontWeight: 600 }}>
              {t('benefits.title', 'Scheme Benefits & Assistance')}
            </div>
            <h2 id="scheme-benefits-modal-title" style={{ margin: '4px 0 0 0', fontSize: '1.25rem', color: '#FFFFFF' }}>
              🎁 {scheme.display_name}
            </h2>
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
            aria-label={t('common.close', 'Close')}
          >
            ✕
          </button>
        </div>

        {/* Audio bar & verification badge strip */}
        <div
          style={{
            padding: '10px 20px',
            backgroundColor: '#F8F9FA',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 10px',
                borderRadius: '14px',
                fontSize: '0.75rem',
                fontWeight: 600,
                backgroundColor: isVerified ? '#DCFCE7' : '#FEF3C7',
                color: isVerified ? '#166534' : '#92400E',
                border: `1px solid ${isVerified ? '#86EFAC' : '#FDE68A'}`,
              }}
            >
              {isVerified ? '✓ ' + t('benefits.verifiedBadge', 'Authoritatively Verified') : '⚠️ ' + t('benefits.unverifiedBadge', 'Pending Verification')}
            </span>

            {/* Translation Status Badge */}
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '3px 8px',
                borderRadius: '10px',
                fontSize: '0.7rem',
                fontWeight: 600,
                backgroundColor: b.is_reviewed ? '#E0F2FE' : '#F1F5F9',
                color: b.is_reviewed ? '#0369A1' : '#475569',
              }}
            >
              🌐 {currentMeta.nativeName}: {b.is_reviewed ? t('benefits.reviewedTranslation', 'Reviewed') : t('benefits.machineTranslation', 'Machine Localized')}
            </span>

            {verificationDate && (
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                {t('benefits.verifiedDate', 'Verified')}: {new Date(verificationDate).toLocaleDateString()}
              </span>
            )}
          </div>

          {/* Audio Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            {playbackState === 'idle' && (
              <button
                type="button"
                className="btn btn-sm btn-secondary"
                onClick={handlePlayAudio}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                aria-label={t('benefits.readAloud', 'Read Benefits Aloud')}
              >
                <span>🔊</span>
                <span>{t('benefits.readAloud', 'Read Aloud')}</span>
              </button>
            )}

            {playbackState === 'playing' && (
              <>
                <button
                  type="button"
                  className="btn btn-sm btn-saffron"
                  onClick={handlePauseAudio}
                  aria-label={t('audio.pause', 'Pause')}
                >
                  ⏸️ {t('audio.pause', 'Pause')}
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  onClick={handleStopAudio}
                  aria-label={t('audio.stop', 'Stop')}
                >
                  ⏹️ {t('audio.stop', 'Stop')}
                </button>
              </>
            )}

            {playbackState === 'paused' && (
              <>
                <button
                  type="button"
                  className="btn btn-sm btn-primary"
                  onClick={handleResumeAudio}
                  aria-label={t('audio.resume', 'Resume')}
                >
                  ▶️ {t('audio.resume', 'Resume')}
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  onClick={handleStopAudio}
                  aria-label={t('audio.stop', 'Stop')}
                >
                  ⏹️ {t('audio.stop', 'Stop')}
                </button>
              </>
            )}
          </div>
        </div>

        {voiceNotice && (
          <div style={{ padding: '8px 20px', backgroundColor: '#FEF3C7', fontSize: '0.75rem', color: '#92400E', borderBottom: '1px solid #FDE68A' }}>
            ℹ️ {voiceNotice}
          </div>
        )}

        {/* Modal body */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
          {loadingBenefits && (
            <div style={{ textAlign: 'center', padding: '12px', color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
              ⌛ {t('benefits.loadingLocalized', 'Loading verified multilingual benefits...')}
            </div>
          )}

          {/* Unverified alert if not verified */}
          {!isVerified && (
            <div
              className="scheme-benefits-unverified"
              style={{ marginTop: 0, marginBottom: '16px' }}
            >
              <div style={{ fontWeight: 600, color: '#92400E', marginBottom: '4px' }}>
                ⚠️ {t('benefits.unverified', 'Benefit details not yet verified from official gazette notification.')}
              </div>
              <div style={{ fontSize: '0.8125rem', color: '#78350F' }}>
                {t('benefits.unverifiedNotice', 'Numerical cash amounts or entitlements are not displayed until confirmed by official notifications to avoid misleading citizens.')}
              </div>
            </div>
          )}

          {/* 1. Assistance Type & Amount Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <div style={{ padding: '12px', backgroundColor: 'var(--color-surface-subtle)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>
                {t('benefits.assistanceType', 'Assistance Type')}
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--color-navy)', marginTop: '4px' }}>
                {assistanceType}
              </div>
            </div>

            <div style={{ padding: '12px', backgroundColor: 'var(--color-teal-light)', borderRadius: '6px', border: '1px solid var(--color-teal)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-teal-dark)', textTransform: 'uppercase', fontWeight: 600 }}>
                {t('benefits.amount', 'Benefit Amount / Coverage')}
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-teal-dark)', marginTop: '4px' }}>
                {benefitAmount || (isVerified ? t('benefits.nonFinancial', 'Official Non-Financial Assistance') : t('benefits.detailsPending', 'Details Not Yet Verified'))}
              </div>
            </div>
          </div>

          {/* 2. Frequency & Duration */}
          {duration && (
            <div style={{ marginBottom: '14px' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-navy)' }}>
                ⏱️ {t('benefits.duration', 'Frequency & Duration')}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--color-text-main)', marginTop: '2px' }}>
                {duration}
              </div>
            </div>
          )}

          {/* 3. Benefits Provided */}
          <div style={{ marginBottom: '14px' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-navy)' }}>
              🎁 {t('benefits.whatProvides', 'What this Scheme Provides')}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-main)', marginTop: '2px', lineHeight: 1.5 }}>
              {benefitsProvided}
            </div>
          </div>

          {/* 4. Intended Beneficiaries */}
          {beneficiaries.length > 0 && (
            <div style={{ marginBottom: '14px' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-navy)', marginBottom: '4px' }}>
                👥 {t('benefits.beneficiaries', 'Intended Beneficiaries')}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {beneficiaries.map((ben, i) => (
                  <span
                    key={i}
                    style={{
                      fontSize: '0.75rem',
                      backgroundColor: '#E2E8F0',
                      color: '#1E293B',
                      padding: '3px 8px',
                      borderRadius: '12px',
                      fontWeight: 500,
                    }}
                  >
                    {ben}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 5. Conditions and Limitations */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-navy)' }}>
              ⚠️ {t('benefits.conditions', 'Conditions & Limitations')}
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginTop: '2px', lineHeight: 1.45 }}>
              {conditions}
            </div>
          </div>

          {/* 6. Authoritative Source Link */}
          {officialSourceUrl && (
            <div
              style={{
                padding: '12px 14px',
                backgroundColor: '#F8F9FA',
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
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                  {t('benefits.officialPortal', 'Official Government Portal')}
                </div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-navy)' }}>
                  {scheme.department_name || t('benefits.competentDept', 'Competent Government Department')}
                </div>
              </div>
              <a
                href={officialSourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary btn-sm"
                style={{ textDecoration: 'none' }}
              >
                🔗 {t('benefits.visitSource', 'Visit Official Source ↗')}
              </a>
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '12px 20px',
            backgroundColor: '#F8F9FA',
            borderTop: '1px solid var(--color-border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '8px',
          }}
        >
          {onRequestReview && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => {
                onClose();
                onRequestReview(scheme);
              }}
            >
              🚩 {t('benefits.requestReview', 'Request Official Review')}
            </button>
          )}

          <button
            type="button"
            className="btn btn-primary"
            onClick={onClose}
            style={{ marginLeft: 'auto' }}
          >
            {t('common.done', 'Done')}
          </button>
        </div>
      </div>
    </div>
  );
}
