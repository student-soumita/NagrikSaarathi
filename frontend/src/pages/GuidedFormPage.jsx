import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import { ConsentBanner } from '../components/ConsentBanner';
import { VoiceControl } from '../components/VoiceControl';
import { FieldHelpModal } from '../components/FieldHelpModal';
import { Badge } from '../components/Badge';
import { SchemeBenefitsModal } from '../components/SchemeBenefitsModal';
import { LanguageSelectorModal } from '../components/LanguageSelectorModal';

// Explicit 8-state application statuses
export const APPLICATION_STATUS_CONFIG = {
  not_started: {
    label: 'Not Started',
    labelHi: 'शुरू नहीं हुआ',
    className: 'badge-status-received',
    badgeColor: '#64748B',
    bgColor: '#F1F5F9',
    borderColor: '#CBD5E1',
  },
  in_progress: {
    label: 'In Progress',
    labelHi: 'प्रगति में है',
    className: 'badge-status-review',
    badgeColor: '#0369A1',
    bgColor: '#E0F2FE',
    borderColor: '#7DD3FC',
  },
  ready_for_review: {
    label: 'Ready for Review',
    labelHi: 'समीक्षा के लिए तैयार',
    className: 'badge-status-info',
    badgeColor: '#B45309',
    bgColor: '#FEF3C7',
    borderColor: '#FCD34D',
  },
  submitted_externally: {
    label: 'Submitted on Official Portal',
    labelHi: 'आधिकारिक पोर्टल पर जमा किया',
    className: 'badge-status-review',
    badgeColor: '#0D9488',
    bgColor: '#CCFBF1',
    borderColor: '#5EEAD4',
  },
  submission_confirmation_recorded: {
    label: 'Acknowledgement Recorded',
    labelHi: 'पावती दर्ज की गई',
    className: 'badge-status-verified',
    badgeColor: '#15803D',
    bgColor: '#DCFCE7',
    borderColor: '#86EFAC',
  },
  verification_pending: {
    label: 'Verification Pending',
    labelHi: 'सत्यापन लंबित',
    className: 'badge-status-info',
    badgeColor: '#7E22CE',
    bgColor: '#F3E8FF',
    borderColor: '#D8B4FE',
  },
  completed: {
    label: 'Application Completed',
    labelHi: 'आवेदन पूर्ण',
    className: 'badge-status-verified',
    badgeColor: '#166534',
    bgColor: '#BBF7D0',
    borderColor: '#4ADE80',
  },
  additional_info_required: {
    label: 'Additional Info Required',
    labelHi: 'अतिरिक्त जानकारी आवश्यक',
    className: 'badge-status-rejected',
    badgeColor: '#C2410C',
    bgColor: '#FFEDD5',
    borderColor: '#FDBA74',
  },
};

// Fallback core fields to guarantee 0 dead-ends even if backend returns empty fields
const DEFAULT_FALLBACK_FIELDS = [
  {
    field_key: 'applicant_full_name',
    field_type: 'text',
    required: true,
    labels_by_language: { en: 'Full Name of Applicant', hi: 'आवेदक का पूरा नाम' },
    explanations_by_language: {
      en: 'Enter your full legal name as it appears on your Aadhaar card or government identity proof.',
      hi: 'अपना पूरा कानूनी नाम दर्ज करें जैसा कि आपके आधार कार्ड या सरकारी पहचान पत्र पर लिखा है।'
    },
    examples_by_language: { en: 'e.g. Ramesh Kumar Sharma', hi: 'उदा. रमेश कुमार शर्मा' },
  },
  {
    field_key: 'applicant_mobile',
    field_type: 'text',
    required: true,
    labels_by_language: { en: 'Mobile Number', hi: 'मोबाइल नंबर' },
    explanations_by_language: {
      en: '10-digit mobile number linked to Aadhaar or bank account for SMS notifications.',
      hi: 'एसएमएस सूचनाओं के लिए आधार या बैंक खाते से जुड़ा 10 अंकों का मोबाइल नंबर।'
    },
    examples_by_language: { en: 'e.g. 9876543210', hi: 'उदा. 9876543210' },
  },
  {
    field_key: 'applicant_gender',
    field_type: 'select',
    required: true,
    labels_by_language: { en: 'Gender', hi: 'लिंग' },
    explanations_by_language: {
      en: 'Select applicant legal gender.',
      hi: 'आवेदक का कानूनी लिंग चुनें।'
    },
  },
  {
    field_key: 'applicant_category',
    field_type: 'select',
    required: true,
    labels_by_language: { en: 'Social Category', hi: 'सामाजिक श्रेणी (वर्ग)' },
    explanations_by_language: {
      en: 'Select your reservation or social category as per state/central records.',
      hi: 'राज्य/केंद्रीय अभिलेखों के अनुसार अपनी श्रेणी चुनें।'
    },
  },
  {
    field_key: 'annual_family_income',
    field_type: 'number',
    required: true,
    labels_by_language: { en: 'Annual Family Income (₹)', hi: 'वार्षिक पारिवारिक आय (₹)' },
    explanations_by_language: {
      en: 'Total annual household income from all sources as stated in your Income Certificate.',
      hi: 'आय प्रमाण पत्र के अनुसार सभी स्रोतों से कुल वार्षिक पारिवारिक आय।'
    },
    examples_by_language: { en: 'e.g. 120000', hi: 'उदा. 120000' },
  },
  {
    field_key: 'residential_address',
    field_type: 'text',
    required: true,
    labels_by_language: { en: 'Permanent Residential Address', hi: 'स्थाई निवास का पता' },
    explanations_by_language: {
      en: 'Complete address with house/village name, post office, block/taluk, and PIN code.',
      hi: 'मकान/गाँव का नाम, डाकघर, ब्लॉक/तहसील और पिन कोड सहित पूरा पता।'
    },
    examples_by_language: { en: 'e.g. Vill Rampur, PO Shivpur, Dist Varanasi - 221001', hi: 'उदा. ग्राम रामपुर, जिला वाराणसी - 221001' },
  },
  {
    field_key: 'bank_account_number',
    field_type: 'text',
    required: false,
    labels_by_language: { en: 'Bank Account Number (for DBT)', hi: 'बैंक खाता संख्या (डीबीटी हेतु)' },
    explanations_by_language: {
      en: 'Aadhaar-seeded savings account for direct benefit transfer of scheme subsidy/pension.',
      hi: 'योजना सब्सिडी/पेंशन के प्रत्यक्ष लाभ अंतरण के लिए आधार से जुड़ा बैंक खाता।'
    },
  },
  {
    field_key: 'bank_ifsc_code',
    field_type: 'text',
    required: false,
    labels_by_language: { en: 'Bank IFSC Code', hi: 'बैंक आईएफएससी कोड' },
    explanations_by_language: {
      en: '11-character code printed on the first page of your bank passbook.',
      hi: 'आपकी बैंक पासबुक के पहले पन्ने पर छपा 11 अंकों का कोड।'
    },
    examples_by_language: { en: 'e.g. SBIN0001234', hi: 'उदा. SBIN0001234' },
  },
];

export function GuidedFormPage({
  initialSchemeId = null,
  onNavigateDashboard,
  onNavigateHome,
  onNavigateCatalogue,
  onOpenHelp,
}) {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language || 'en';

  // Step 1: scheme, Step 2: eligibility & documents, Step 3: fill_form, Step 4: review, Step 5: completed
  const [currentStep, setCurrentStep] = useState(initialSchemeId ? 2 : 1);

  // Schemes & Guidance Packet
  const [schemes, setSchemes] = useState([]);
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [guidancePacket, setGuidancePacket] = useState(null);
  const [fields, setFields] = useState([]);
  const [currentFieldIndex, setCurrentFieldIndex] = useState(0);

  // Interactive Checklist states
  const [checkedEligibility, setCheckedEligibility] = useState({});
  const [checkedDocuments, setCheckedDocuments] = useState({});

  // Form State (strictly in-memory, privacy preserved)
  const [formData, setFormData] = useState({});
  const [validationErrors, setValidationErrors] = useState({});

  // 8-State Application Status Tracking
  const [applicationStatus, setApplicationStatus] = useState('not_started');
  const [submissionDetails, setSubmissionDetails] = useState({
    acknowledgementNumber: '',
    submissionDate: new Date().toISOString().split('T')[0],
    portalRef: '',
    notes: '',
  });
  const [isRecordingSubmission, setIsRecordingSubmission] = useState(false);

  // Save Progress & Resume Later
  const [savedProgressFound, setSavedProgressFound] = useState(null);
  const [saveToast, setSaveToast] = useState(null);

  // Assistance Session State
  const [sessionId, setSessionId] = useState(null);
  const [consentStatus, setConsentStatus] = useState(null);
  const [fieldExplanation, setFieldExplanation] = useState(null);
  const [isLoadingExplanation, setIsLoadingExplanation] = useState(false);

  // Help Modal & Feedback
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isLangSwitcherOpen, setIsLangSwitcherOpen] = useState(false);
  const [isBenefitsModalOpen, setIsBenefitsModalOpen] = useState(false);
  const [apiError, setApiError] = useState(null);

  // Auto-dismiss save toast
  useEffect(() => {
    if (saveToast) {
      const timer = setTimeout(() => setSaveToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [saveToast]);

  // 1. Fetch available schemes on mount
  useEffect(() => {
    async function loadSchemes() {
      try {
        const data = await api.getSchemes();
        setSchemes(data);
        if (data && data.length > 0) {
          if (initialSchemeId) {
            const found = data.find((s) => s.id === Number(initialSchemeId));
            setSelectedScheme(found || data[0]);
          } else {
            setSelectedScheme(data[0]);
          }
        }
      } catch (err) {
        setApiError('Unable to connect to backend API. Please ensure the backend server is running.');
      }
    }
    loadSchemes();
  }, [initialSchemeId]);

  // Check saved progress for the active scheme whenever selectedScheme changes
  useEffect(() => {
    if (!selectedScheme) return;
    try {
      const storageKey = `nagrik_form_progress_${selectedScheme.id}`;
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && (parsed.formData || parsed.currentStep > 1)) {
          setSavedProgressFound(parsed);
        }
      } else {
        setSavedProgressFound(null);
      }
    } catch (_) {
      setSavedProgressFound(null);
    }
  }, [selectedScheme]);

  // 2. Fetch full guidance packet whenever selected scheme or language changes
  useEffect(() => {
    if (!selectedScheme) return;
    async function loadGuidance() {
      try {
        const packet = await api.getSchemeGuidance(selectedScheme.id, currentLang);
        setGuidancePacket(packet);
        if (packet.fields && packet.fields.length > 0) {
          setFields(packet.fields);
        } else {
          const fieldList = await api.getSchemeFields(selectedScheme.id);
          setFields(fieldList && fieldList.length > 0 ? fieldList : DEFAULT_FALLBACK_FIELDS);
        }
      } catch (err) {
        try {
          const fieldList = await api.getSchemeFields(selectedScheme.id);
          setFields(fieldList && fieldList.length > 0 ? fieldList : DEFAULT_FALLBACK_FIELDS);
        } catch (_) {
          setFields(DEFAULT_FALLBACK_FIELDS);
        }
      }
    }
    loadGuidance();
  }, [selectedScheme, currentLang]);

  // 3. Start Assistance Session
  const initAssistanceSession = async (consented) => {
    if (!selectedScheme) return;
    try {
      const resp = await api.createSession({
        scheme_id: selectedScheme.id,
        selected_language: currentLang,
        channel: 'web',
        analytics_consent: Boolean(consented),
        is_demo: selectedScheme.is_demo,
      });
      setSessionId(resp.session_id);
    } catch (err) {
      console.warn('Session initialization fallback:', err.message);
    }
  };

  const handleConsentAccept = () => {
    setConsentStatus(true);
    initAssistanceSession(true);
  };

  const handleConsentDecline = () => {
    setConsentStatus(false);
    initAssistanceSession(false);
  };

  // 4. Save progress & resume later handler
  const handleSaveProgressLater = () => {
    if (!selectedScheme) return;
    try {
      const storageKey = `nagrik_form_progress_${selectedScheme.id}`;
      const progressPayload = {
        schemeId: selectedScheme.id,
        schemeName: selectedScheme.display_name,
        currentStep,
        currentFieldIndex,
        formData,
        checkedEligibility,
        checkedDocuments,
        applicationStatus: applicationStatus === 'not_started' ? 'in_progress' : applicationStatus,
        submissionDetails,
        updatedAt: new Date().toISOString(),
      };
      localStorage.setItem(storageKey, JSON.stringify(progressPayload));

      // Update master directory in localStorage
      try {
        const dirStr = localStorage.getItem('nagrik_saved_applications_list');
        const dirList = dirStr ? JSON.parse(dirStr) : [];
        const filtered = dirList.filter((item) => item.schemeId !== selectedScheme.id);
        filtered.unshift({
          schemeId: selectedScheme.id,
          schemeName: selectedScheme.display_name,
          currentStep,
          status: progressPayload.applicationStatus,
          updatedAt: progressPayload.updatedAt,
        });
        localStorage.setItem('nagrik_saved_applications_list', JSON.stringify(filtered.slice(0, 20)));
      } catch (_) {}

      if (applicationStatus === 'not_started') {
        setApplicationStatus('in_progress');
      }
      setSaveToast(
        t(
          'progress.savedSuccess',
          'Your progress has been saved securely on this device! You can safely return and resume anytime.'
        )
      );
      setSavedProgressFound(null);
    } catch (err) {
      console.warn('Failed to save progress locally:', err);
    }
  };

  // Resume saved progress
  const handleResumeSavedProgress = () => {
    if (!savedProgressFound) return;
    try {
      if (savedProgressFound.formData) setFormData(savedProgressFound.formData);
      if (savedProgressFound.checkedEligibility) setCheckedEligibility(savedProgressFound.checkedEligibility);
      if (savedProgressFound.checkedDocuments) setCheckedDocuments(savedProgressFound.checkedDocuments);
      if (savedProgressFound.currentStep) setCurrentStep(savedProgressFound.currentStep);
      if (typeof savedProgressFound.currentFieldIndex === 'number') setCurrentFieldIndex(savedProgressFound.currentFieldIndex);
      if (savedProgressFound.applicationStatus) setApplicationStatus(savedProgressFound.applicationStatus);
      if (savedProgressFound.submissionDetails) setSubmissionDetails(savedProgressFound.submissionDetails);

      setSavedProgressFound(null);
      setSaveToast(t('progress.restoredSuccess', 'Saved progress restored successfully!'));
    } catch (err) {
      console.warn('Failed to restore saved progress:', err);
    }
  };

  // Discard saved progress and start fresh
  const handleDiscardSavedProgress = () => {
    if (!selectedScheme) return;
    try {
      localStorage.removeItem(`nagrik_form_progress_${selectedScheme.id}`);
      setSavedProgressFound(null);
      setFormData({});
      setCheckedEligibility({});
      setCheckedDocuments({});
      setCurrentFieldIndex(0);
      setCurrentStep(1);
      setApplicationStatus('not_started');
    } catch (_) {}
  };

  // Record government external submission confirmation
  const handleRecordSubmissionConfirmation = (e) => {
    e.preventDefault();
    if (!submissionDetails.acknowledgementNumber.trim()) {
      alert('Please enter your official Acknowledgement / Application Number.');
      return;
    }
    const newStatus = 'submission_confirmation_recorded';
    setApplicationStatus(newStatus);
    setIsRecordingSubmission(false);

    // Persist immediately
    try {
      const storageKey = `nagrik_form_progress_${selectedScheme.id}`;
      const payload = {
        schemeId: selectedScheme.id,
        schemeName: selectedScheme.display_name,
        currentStep: 5,
        currentFieldIndex,
        formData,
        checkedEligibility,
        checkedDocuments,
        applicationStatus: newStatus,
        submissionDetails,
        updatedAt: new Date().toISOString(),
      };
      localStorage.setItem(storageKey, JSON.stringify(payload));
      setSaveToast(
        t('progress.confirmationSaved', 'Government submission confirmation recorded successfully!')
      );
    } catch (_) {}
  };

  // Load explanation for current field
  const currentField = fields[currentFieldIndex] || DEFAULT_FALLBACK_FIELDS[0];
  useEffect(() => {
    if (!selectedScheme || !currentField) return;

    let isMounted = true;
    async function fetchExplanation() {
      setIsLoadingExplanation(true);
      try {
        const expl = await api.explainField({
          scheme_id: selectedScheme.id,
          field_key: currentField.field_key,
          target_language: currentLang,
        });
        if (isMounted) setFieldExplanation(expl);
      } catch (err) {
        if (isMounted) {
          setFieldExplanation({
            localized_label:
              currentField.labels_by_language?.[currentLang] ||
              currentField.labels_by_language?.hi ||
              currentField.labels_by_language?.en ||
              currentField.field_key,
            localized_explanation:
              currentField.explanations_by_language?.[currentLang] ||
              currentField.explanations_by_language?.hi ||
              currentField.explanations_by_language?.en ||
              '',
            translation_status: 'missing',
            is_fallback: true,
          });
        }
      } finally {
        if (isMounted) setIsLoadingExplanation(false);
      }
    }

    fetchExplanation();
    return () => {
      isMounted = false;
    };
  }, [selectedScheme, currentFieldIndex, currentField, currentLang]);

  // Log session events safely
  const logEvent = (eventType, barrierCategory = null, barrierResolution = null) => {
    if (!sessionId) return;
    api.recordSessionEvent(sessionId, {
      field_key: currentField?.field_key || null,
      event_type: eventType,
      barrier_category: barrierCategory,
      barrier_resolution: barrierResolution,
    }).catch(() => {});
  };

  // Form field manipulation
  const handleInputChange = (fieldKey, value) => {
    setFormData((prev) => ({ ...prev, [fieldKey]: value }));
    if (applicationStatus === 'not_started') {
      setApplicationStatus('in_progress');
    }
    if (validationErrors[fieldKey]) {
      setValidationErrors((prev) => ({ ...prev, [fieldKey]: null }));
    }
  };

  // Validate current field
  const validateCurrentField = async () => {
    if (!currentField || !selectedScheme) return true;
    const val = formData[currentField.field_key];

    try {
      const res = await api.validateField({
        scheme_id: selectedScheme.id,
        field_key: currentField.field_key,
        field_value: val,
        target_language: currentLang,
      });

      if (!res.is_valid) {
        setValidationErrors((prev) => ({
          ...prev,
          [currentField.field_key]: res.error_message,
        }));
        logEvent('validation_failed', 'validation_error');
        return false;
      }
      return true;
    } catch (err) {
      if (currentField.required && (!val || val.toString().trim() === '')) {
        setValidationErrors((prev) => ({
          ...prev,
          [currentField.field_key]: t('form.requiredField', 'This field is required'),
        }));
        return false;
      }
      return true;
    }
  };

  const handleNextField = async () => {
    const isValid = await validateCurrentField();
    if (!isValid) return;

    logEvent('field_completed');

    if (currentFieldIndex < fields.length - 1) {
      setCurrentFieldIndex((prev) => prev + 1);
    } else {
      setApplicationStatus('ready_for_review');
      setCurrentStep(4);
    }
  };

  const handlePrevField = () => {
    if (currentFieldIndex > 0) {
      setCurrentFieldIndex((prev) => prev - 1);
    }
  };

  const handleFinishReview = async () => {
    if (sessionId) {
      try {
        await api.updateSessionStatus(sessionId, 'completed');
        logEvent('application_completed');
      } catch (_) {}
    }
    setCurrentStep(5);
  };

  const handleResetSession = () => {
    setFormData({});
    setValidationErrors({});
    setCurrentFieldIndex(0);
    setCurrentStep(1);
    setSessionId(null);
    setApplicationStatus('not_started');
  };

  const handleResolveBarrier = (actionType, resolved = false) => {
    if (actionType === 'resolved' && resolved) {
      logEvent('issue_resolved', null, 'resolved');
    } else if (actionType === 'unresolved_after_ask') {
      logEvent('issue_unresolved_confirmed', null, 'unresolved');
    } else if (!resolved && actionType !== 'resolved') {
      logEvent('barrier_selected', actionType, 'barrier_reported');
    }
  };

  const handleEscalateToHuman = () => {
    logEvent('human_help_requested', null, 'escalated');
    if (sessionId) {
      api.updateSessionStatus(sessionId, 'needs_human_help').catch(() => {});
    }
    setIsHelpOpen(false);
    if (onOpenHelp) {
      onOpenHelp();
    }
  };

  // Eligibility check calculations
  const eligibilityList = guidancePacket?.eligibility_requirements || [];
  const mandatoryEligibility = eligibilityList.filter((r) => r.is_mandatory);
  const allMandatoryChecked =
    mandatoryEligibility.length === 0 ||
    mandatoryEligibility.every((r) => checkedEligibility[r.criterion_key]);

  const documentList = guidancePacket?.document_requirements || [];

  const localizedSchemeDesc =
    selectedScheme?.descriptions_by_language?.[currentLang] ||
    selectedScheme?.descriptions_by_language?.hi ||
    selectedScheme?.description;

  const localizedInstructions =
    selectedScheme?.application_instructions_by_language?.[currentLang] ||
    selectedScheme?.application_instructions_by_language?.hi ||
    selectedScheme?.application_instructions_by_language?.en;

  // Check if scheme has candidate / fallback status
  const isCandidateScheme =
    guidancePacket?.form_completeness === 'partial' ||
    guidancePacket?.is_fallback ||
    selectedScheme?.completeness_status === 'candidate' ||
    selectedScheme?.is_candidate;

  const currentStatusConfig =
    APPLICATION_STATUS_CONFIG[applicationStatus] || APPLICATION_STATUS_CONFIG.not_started;

  const statusLabel =
    t(`appStatuses.${applicationStatus}`, currentStatusConfig.label);

  return (
    <div className="civic-container" style={{ paddingTop: 'var(--space-xl)', paddingBottom: 'var(--space-3xl)' }}>
      {/* Toast Notification */}
      {saveToast && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            zIndex: 1200,
            backgroundColor: '#1E293B',
            color: '#FFFFFF',
            padding: '14px 20px',
            borderRadius: '8px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            border: '1px solid #7DD3FC',
            maxWidth: '420px',
            fontSize: '0.9rem',
          }}
        >
          <span>💾</span>
          <span>{saveToast}</span>
          <button
            type="button"
            onClick={() => setSaveToast(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#94A3B8',
              cursor: 'pointer',
              marginLeft: 'auto',
              fontSize: '1rem',
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Saved Draft Found Banner */}
      {savedProgressFound && selectedScheme && (
        <div
          style={{
            backgroundColor: 'var(--color-surface, #FFFFFF)',
            border: '2px solid #38BDF8',
            borderRadius: '8px',
            padding: '16px 20px',
            marginBottom: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <div style={{ fontWeight: 800, color: 'var(--color-navy)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>💾</span>
              <span>{t('progress.savedBannerTitle', 'Resume Saved Application')}</span>
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  backgroundColor: '#E0F2FE',
                  color: '#0369A1',
                  fontWeight: 700,
                }}
              >
                {t(`appStatuses.${savedProgressFound.applicationStatus || 'in_progress'}`, savedProgressFound.applicationStatus || 'In Progress')}
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              {t(
                'progress.savedBannerDesc',
                'You have saved progress for this scheme from {{time}}.',
                { time: new Date(savedProgressFound.updatedAt).toLocaleString() }
              )}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleResumeSavedProgress}
              style={{ fontWeight: 700 }}
            >
              ▶ {t('progress.resumeBtn', 'Resume Application')}
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleDiscardSavedProgress}
            >
              ↺ {t('progress.startFreshBtn', 'Start Fresh')}
            </button>
          </div>
        </div>
      )}

      {/* Active Scheme Header Banner */}
      {selectedScheme && (
        <div
          style={{
            backgroundColor: 'var(--color-surface, #FFFFFF)',
            border: '1px solid var(--color-border)',
            borderRadius: '8px',
            padding: '14px 18px',
            marginBottom: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                वर्तमान चयनित योजना (Selected Scheme)
              </span>
              {/* Application Status Badge */}
              <span
                className={`badge ${currentStatusConfig.className}`}
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  padding: '3px 10px',
                  borderRadius: '12px',
                  border: `1px solid ${currentStatusConfig.borderColor}`,
                  backgroundColor: currentStatusConfig.bgColor,
                  color: currentStatusConfig.badgeColor,
                }}
              >
                ● {statusLabel}
              </span>
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--color-navy)', marginTop: '2px' }}>
              {selectedScheme.display_name}
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
              🏛️ {selectedScheme.department_name} • {selectedScheme.government_level?.toUpperCase()}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            {/* Save Progress Button */}
            {currentStep > 1 && (
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handleSaveProgressLater}
                title="Save current progress securely in browser"
                style={{ fontWeight: 600 }}
              >
                💾 {t('progress.saveLaterBtn', 'Save Progress & Resume Later')}
              </button>
            )}

            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => setIsBenefitsModalOpen(true)}
              style={{
                fontSize: '0.8125rem',
                fontWeight: 700,
                backgroundColor: '#FEF3C7',
                color: '#92400E',
                borderColor: '#FCD34D',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              🎁 {t('catalogue.viewBenefits', 'View Benefits')}
            </button>

            {onNavigateCatalogue && (
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={onNavigateCatalogue}
                style={{ fontSize: '0.8125rem' }}
              >
                ← {t('form.changeScheme', 'Change Scheme')}
              </button>
            )}
            {selectedScheme.official_source_url && (
              <a
                href={selectedScheme.official_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary btn-sm"
                style={{ fontSize: '0.8125rem' }}
              >
                🔗 {t('form.officialPortal', 'Official Portal')}
              </a>
            )}
          </div>
        </div>
      )}

      {/* Candidate / Active Civic Verification Disclosure Banner */}
      {isCandidateScheme && (
        <div
          style={{
            backgroundColor: 'var(--color-surface-subtle, #F8FAFC)',
            border: '1px solid #FCD34D',
            borderLeft: '4px solid #F59E0B',
            borderRadius: '6px',
            padding: '12px 16px',
            marginBottom: '16px',
            fontSize: '0.85rem',
            color: 'var(--color-text-primary)',
            lineHeight: 1.5,
          }}
        >
          <strong>🏛️ {t('progress.civicVerificationNotice', 'Active Civic Verification')}:</strong>{' '}
          This scheme is actively supported for guided self-preparation. All necessary personal details and document readiness checklists are prepared for you to submit directly at the official portal or designated office.
        </div>
      )}

      {/* Stepper Navigation */}
      <nav className="stepper-nav" aria-label="Progress steps">
        <div className={`stepper-item ${currentStep === 1 ? 'active' : currentStep > 1 ? 'completed' : ''}`}>
          <span className="stepper-badge">1</span>
          <span>{t('steps.chooseScheme', 'Choose Scheme')}</span>
        </div>
        <div className={`stepper-item ${currentStep === 2 ? 'active' : currentStep > 2 ? 'completed' : ''}`}>
          <span className="stepper-badge">2</span>
          <span>{t('steps.eligibilityDocs', 'Eligibility & Docs')}</span>
        </div>
        <div className={`stepper-item ${currentStep === 3 ? 'active' : currentStep > 3 ? 'completed' : ''}`}>
          <span className="stepper-badge">3</span>
          <span>{t('steps.fillForm', 'Fill Form')}</span>
        </div>
        <div className={`stepper-item ${currentStep === 4 ? 'active' : currentStep > 4 ? 'completed' : ''}`}>
          <span className="stepper-badge">4</span>
          <span>{t('steps.review', 'Review')}</span>
        </div>
        <div className={`stepper-item ${currentStep === 5 ? 'active' : ''}`}>
          <span className="stepper-badge">5</span>
          <span>{t('steps.complete', 'Complete')}</span>
        </div>
      </nav>

      {/* Global Error Notice */}
      {apiError && (
        <div
          style={{
            backgroundColor: 'var(--color-error-bg)',
            border: '1px solid var(--color-error-border)',
            padding: '12px var(--space-md)',
            borderRadius: 'var(--border-radius)',
            color: 'var(--color-error)',
            marginBottom: 'var(--space-lg)',
          }}
        >
          ⚠️ {apiError}
        </div>
      )}

      {/* Consent Notice */}
      <ConsentBanner
        consentStatus={consentStatus}
        onAcceptConsent={handleConsentAccept}
        onDeclineConsent={handleConsentDecline}
      />

      {/* STEP 1: Scheme Selection & Overview */}
      {currentStep === 1 && (
        <div className="civic-form-container">
          <div className="civic-card">
            <div className="civic-card-header">
              <h2>{t('form.selectSchemeTitle', 'Select a Government Scheme')}</h2>
              <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.9375rem' }}>
                {t('form.selectSchemeSubtitle', 'Select the scheme you would like to prepare an application for:')}
              </p>
            </div>

            <div style={{ display: 'grid', gap: '12px', maxHeight: '420px', overflowY: 'auto', marginBottom: '20px' }}>
              {schemes.map((s) => {
                const isSelected = selectedScheme?.id === s.id;
                const d = s.descriptions_by_language?.[currentLang] || s.descriptions_by_language?.hi || s.description;
                return (
                  <div
                    key={s.id}
                    style={{
                      border: isSelected ? '2px solid var(--color-teal)' : '1px solid var(--color-border)',
                      backgroundColor: isSelected ? 'var(--color-teal-light)' : 'var(--color-surface, #FFFFFF)',
                      padding: '14px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    onClick={() => setSelectedScheme(s)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <h3 style={{ fontSize: '1.05rem', margin: 0, color: 'var(--color-navy)', fontWeight: 700 }}>
                        {s.display_name}
                      </h3>
                    </div>
                    <div style={{ fontSize: '0.78125rem', color: 'var(--color-text-muted)', marginBottom: '6px' }}>
                      🏛️ {s.department_name} • {s.government_level?.toUpperCase()}
                    </div>
                    <p style={{ fontSize: '0.84375rem', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>
                      {d}
                    </p>
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--color-border)', paddingTop: '16px' }}>
              {onNavigateCatalogue && (
                <button type="button" className="btn btn-secondary btn-sm" onClick={onNavigateCatalogue}>
                  🏛️ {t('form.exploreAll', 'Explore All Schemes')}
                </button>
              )}

              <button
                className="btn btn-primary"
                onClick={() => {
                  if (consentStatus === null) setConsentStatus(true);
                  initAssistanceSession(consentStatus !== false);
                  setApplicationStatus('in_progress');
                  setCurrentStep(2);
                }}
                disabled={!selectedScheme}
              >
                {t('form.reviewEligibilitySteps', 'Review Eligibility & Steps →')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 2: Understand Process, Eligibility Pre-Check & Document Checklist */}
      {currentStep === 2 && selectedScheme && (
        <div className="civic-form-container">
          <div className="civic-card">
            <div className="civic-card-header">
              <h2>{t('form.eligibilityCheckTitle', 'Eligibility & Document Readiness Check')}</h2>
              <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                {selectedScheme.display_name}
              </p>
            </div>

            {/* Scheme Summary Box */}
            <div
              style={{
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                padding: '14px',
                marginBottom: '20px',
              }}
            >
              <div style={{ fontWeight: 700, color: 'var(--color-navy)', marginBottom: '4px' }}>
                📋 {t('form.schemeOverviewInstructions', 'Scheme Overview & Instructions')}
              </div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', margin: '0 0 8px 0', lineHeight: 1.5 }}>
                {localizedSchemeDesc}
              </p>
              {localizedInstructions && (
                <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>
                  ℹ️ {localizedInstructions}
                </div>
              )}
            </div>

            {/* 1. Interactive Eligibility Pre-Check */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ fontSize: '1.05rem', color: 'var(--color-navy)', margin: 0, fontWeight: 700 }}>
                  ⚖️ {t('form.eligibilityChecklistTitle', 'Eligibility Pre-Check')}
                </h3>
                {allMandatoryChecked ? (
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      backgroundColor: '#DCFCE7',
                      color: '#166534',
                      padding: '4px 8px',
                      borderRadius: '4px',
                    }}
                  >
                    ✓ {t('form.eligibleToApply', 'Eligible to Apply')}
                  </span>
                ) : (
                  <span style={{ fontSize: '0.75rem', color: '#B45309', fontWeight: 600 }}>
                    ⚠️ {t('form.checkConditions', 'Check all conditions')}
                  </span>
                )}
              </div>

              {eligibilityList.length === 0 ? (
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                  {t('form.generalCriteriaApply', 'General public criteria apply.')}
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {eligibilityList.map((crit) => {
                    const isChecked = Boolean(checkedEligibility[crit.criterion_key]);
                    const title = crit.titles_by_language?.[currentLang] || crit.titles_by_language?.hi || crit.criterion_key;
                    const desc = crit.descriptions_by_language?.[currentLang] || crit.descriptions_by_language?.hi || '';

                    return (
                      <label
                        key={crit.id}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '10px',
                          padding: '10px 12px',
                          borderRadius: '6px',
                          border: isChecked ? '1px solid #10B981' : '1px solid var(--color-border)',
                          backgroundColor: isChecked ? '#F0FDF4' : 'var(--color-surface, #FFFFFF)',
                          cursor: 'pointer',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            setCheckedEligibility({ ...checkedEligibility, [crit.criterion_key]: e.target.checked });
                            if (applicationStatus === 'not_started') setApplicationStatus('in_progress');
                          }}
                          style={{ marginTop: '3px', cursor: 'pointer' }}
                        />
                        <div>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                            {title} {crit.is_mandatory && <span style={{ color: '#DC2626' }}>*</span>}
                          </div>
                          {desc && (
                            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                              {desc}
                            </div>
                          )}
                        </div>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>

            {/* 2. Document Readiness Checklist */}
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '1.05rem', color: 'var(--color-navy)', margin: '0 0 8px 0', fontWeight: 700 }}>
                📑 {t('form.docsChecklistTitle', 'Required Documents Checklist')}
              </h3>

              {documentList.length === 0 ? (
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                  {t('form.keepIdReady', 'Keep ID and Address proof ready.')}
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
                  {documentList.map((doc) => {
                    const isChecked = Boolean(checkedDocuments[doc.document_code]);
                    const title = doc.titles_by_language?.[currentLang] || doc.titles_by_language?.hi || doc.document_code;
                    const desc = doc.descriptions_by_language?.[currentLang] || doc.descriptions_by_language?.hi || '';

                    return (
                      <label
                        key={doc.id}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '10px',
                          padding: '10px 12px',
                          borderRadius: '6px',
                          border: isChecked ? '1px solid #10B981' : '1px solid var(--color-border)',
                          backgroundColor: isChecked ? '#F0FDF4' : 'var(--color-surface, #FFFFFF)',
                          cursor: 'pointer',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            setCheckedDocuments({ ...checkedDocuments, [doc.document_code]: e.target.checked });
                            if (applicationStatus === 'not_started') setApplicationStatus('in_progress');
                          }}
                          style={{ marginTop: '3px', cursor: 'pointer' }}
                        />
                        <div>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-navy)' }}>
                            {title}
                          </div>
                          {desc && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                              {desc}
                            </div>
                          )}
                          <div style={{ marginTop: '4px' }}>
                            <span
                              style={{
                                fontSize: '0.6875rem',
                                fontWeight: 600,
                                padding: '2px 6px',
                                borderRadius: '3px',
                                backgroundColor: doc.is_mandatory ? '#FEE2E2' : '#F1F5F9',
                                color: doc.is_mandatory ? '#991B1B' : '#475569',
                              }}
                            >
                              {doc.is_mandatory ? t('form.mandatory', 'Mandatory') : t('form.optional', 'Optional')}
                            </span>
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Step Navigation Actions */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--color-border)', paddingTop: '16px', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button className="btn btn-secondary" onClick={() => setCurrentStep(1)}>
                  ← {t('common.back')}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleSaveProgressLater}
                >
                  💾 {t('progress.saveLaterBtn', 'Save Progress & Resume Later')}
                </button>
              </div>

              <button
                className="btn btn-primary"
                onClick={() => {
                  setApplicationStatus('in_progress');
                  setCurrentStep(3);
                  logEvent('form_started');
                }}
              >
                ✍️ {t('form.startFormBtn', 'Start Guided Form →')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 3: Fill Form (Guided One-Field At-A-Time with Schema Rendering) */}
      {currentStep === 3 && currentField && (
        <div className="civic-form-container">
          <div className="civic-card">
            {/* Field Progress and Original Reference */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-teal)' }}>
                {t('form.progress')}: {currentFieldIndex + 1} / {fields.length}
              </span>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={handleSaveProgressLater}
                  style={{ fontSize: '0.78rem' }}
                >
                  💾 {t('progress.saveLaterBtn', 'Save Progress')}
                </button>
                {currentField.required ? (
                  <Badge variant="required">{t('form.required')}</Badge>
                ) : (
                  <Badge variant="optional">{t('form.optional')}</Badge>
                )}
                {fieldExplanation?.translation_status === 'approved' && (
                  <Badge variant="verified">✓ {t('status.verified')}</Badge>
                )}
              </div>
            </div>

            {/* Field Label & Explanations */}
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '8px', color: 'var(--color-navy)', fontWeight: 700 }}>
                {fieldExplanation?.localized_label ||
                  currentField.labels_by_language?.[currentLang] ||
                  currentField.labels_by_language?.en ||
                  currentField.labels_by_language?.hi ||
                  currentField.field_key}
              </h3>

              {/* Multilingual Plain-Language Guidance */}
              {isLoadingExplanation ? (
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                  {t('form.loadingGuidance', 'Loading guidance...')}
                </div>
              ) : (
                <div
                  style={{
                    backgroundColor: 'var(--color-surface-subtle)',
                    borderLeft: '4px solid var(--color-teal)',
                    padding: '12px 16px',
                    borderRadius: '0 6px 6px 0',
                    fontSize: '0.875rem',
                    lineHeight: '1.5',
                    color: 'var(--color-text-secondary)',
                    marginBottom: '16px',
                  }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--color-navy)', marginBottom: '4px' }}>
                    💡 {t('form.whatDoesThisMean', 'What does this mean?')}
                  </div>
                  <div>
                    {fieldExplanation?.localized_explanation ||
                      currentField.explanations_by_language?.[currentLang] ||
                      currentField.explanations_by_language?.en ||
                      currentField.explanations_by_language?.hi ||
                      t('form.fillAccurately')}
                  </div>

                  {/* Instructions / Examples */}
                  {(currentField.instructions_by_language?.[currentLang] ||
                    currentField.examples_by_language?.[currentLang]) && (
                    <div style={{ marginTop: '8px', fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                      {currentField.instructions_by_language?.[currentLang] && (
                        <div>📝 {currentField.instructions_by_language[currentLang]}</div>
                      )}
                      {currentField.examples_by_language?.[currentLang] && (
                        <div>📌 {t('common.example', 'Example:')} {currentField.examples_by_language[currentLang]}</div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Dynamic Field Input Control */}
              {currentField.field_type === 'select' ? (
                <select
                  className="form-control"
                  value={formData[currentField.field_key] || ''}
                  onChange={(e) => handleInputChange(currentField.field_key, e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', fontSize: '1rem', borderRadius: '6px' }}
                >
                  <option value="">-- {t('form.selectOption', 'Select an option')} --</option>
                  <option value="Yes">{t('form.yes', 'Yes')}</option>
                  <option value="No">{t('form.no', 'No')}</option>
                  <option value="Male">{t('common.male', 'Male')}</option>
                  <option value="Female">{t('common.female', 'Female')}</option>
                  <option value="Other">{t('common.other', 'Other')}</option>
                  <option value="General">General</option>
                  <option value="OBC">OBC</option>
                  <option value="SC">SC</option>
                  <option value="ST">ST</option>
                  <option value="EWS">EWS</option>
                </select>
              ) : currentField.field_type === 'date' ? (
                <input
                  type="date"
                  className="form-control"
                  value={formData[currentField.field_key] || ''}
                  onChange={(e) => handleInputChange(currentField.field_key, e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', fontSize: '1rem', borderRadius: '6px' }}
                />
              ) : currentField.field_type === 'number' ? (
                <input
                  type="number"
                  className="form-control"
                  placeholder={
                    currentField.examples_by_language?.[currentLang] ||
                    t('form.enterNumber', 'Enter number...')
                  }
                  value={formData[currentField.field_key] || ''}
                  onChange={(e) => handleInputChange(currentField.field_key, e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', fontSize: '1rem', borderRadius: '6px' }}
                />
              ) : (
                <input
                  type="text"
                  className="form-control"
                  placeholder={
                    currentField.examples_by_language?.[currentLang] ||
                    t('form.typeAnswerHere', 'Type your answer here...')
                  }
                  value={formData[currentField.field_key] || ''}
                  onChange={(e) => handleInputChange(currentField.field_key, e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', fontSize: '1rem', borderRadius: '6px' }}
                  autoFocus
                />
              )}

              {/* Validation Error Feedback */}
              {validationErrors[currentField.field_key] && (
                <div className="form-error-feedback" style={{ marginTop: '8px' }}>
                  <span>⚠️</span>
                  <span>{validationErrors[currentField.field_key]}</span>
                </div>
              )}

              {/* Voice Assistance Button */}
              <div style={{ marginTop: '12px' }}>
                <VoiceControl
                  onApplyTranscript={(text) => handleInputChange(currentField.field_key, text)}
                  textToRead={
                    fieldExplanation?.localized_explanation ||
                    currentField.labels_by_language?.[currentLang] ||
                    ''
                  }
                  stepTitle={`${t('form.progress')}: ${currentFieldIndex + 1} / ${fields.length}`}
                  fieldKey={currentField.field_key}
                />
              </div>
            </div>

            {/* Field Actions */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderTop: '1px solid var(--color-border-subtle)',
                paddingTop: '20px',
                marginTop: '24px',
                flexWrap: 'wrap',
                gap: '10px',
              }}
            >
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button
                  className="btn btn-secondary"
                  onClick={handlePrevField}
                  disabled={currentFieldIndex === 0}
                >
                  ← {t('form.previous')}
                </button>

                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    logEvent('help_requested');
                    setIsHelpOpen(true);
                  }}
                  style={{ color: 'var(--color-navy)', borderColor: 'var(--color-saffron-dark)' }}
                >
                  ❓ {t('form.needHelp')}
                </button>

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleSaveProgressLater}
                >
                  💾 {t('progress.saveLaterBtn', 'Save & Resume Later')}
                </button>
              </div>

              <button className="btn btn-primary" onClick={handleNextField}>
                {currentFieldIndex === fields.length - 1 ? `${t('steps.review')} →` : `${t('form.next')} →`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 4: Review Information */}
      {currentStep === 4 && (
        <div className="civic-form-container">
          <div className="civic-card">
            <div className="civic-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
              <div>
                <h2>{t('form.reviewTitle', 'Review Prepared Application')}</h2>
                <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                  {selectedScheme?.display_name} • {t('form.reviewSubtitle', 'Verify all entered information')}
                </p>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handleSaveProgressLater}
              >
                💾 {t('progress.saveLaterBtn', 'Save Progress & Resume Later')}
              </button>
            </div>

            <table className="civic-table" style={{ marginBottom: '24px' }}>
              <thead>
                <tr>
                  <th>{t('form.fieldHeader', 'Field')}</th>
                  <th>{t('form.enteredValueHeader', 'Entered Value')}</th>
                  <th style={{ width: '80px' }}>{t('form.editHeader', 'Edit')}</th>
                </tr>
              </thead>
              <tbody>
                {fields.map((f, idx) => (
                  <tr key={f.field_key}>
                    <td>
                      <strong>
                        {f.labels_by_language?.[currentLang] || f.labels_by_language?.hi || f.field_key}
                      </strong>
                    </td>
                    <td>
                      {formData[f.field_key] ? (
                        <span>{formData[f.field_key]}</span>
                      ) : (
                        <em style={{ color: 'var(--color-text-muted)' }}>—</em>
                      )}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => {
                          setCurrentFieldIndex(idx);
                          setCurrentStep(3);
                        }}
                      >
                        {t('review.edit')}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div
              style={{
                backgroundColor: 'var(--color-surface-subtle)',
                padding: '12px',
                borderRadius: 'var(--border-radius)',
                fontSize: '0.8125rem',
                color: 'var(--color-text-secondary)',
                marginBottom: '20px',
              }}
            >
              🔒 {t('review.memoryNotice')}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
              <button className="btn btn-secondary" onClick={() => setCurrentStep(3)}>
                ← {t('common.back')}
              </button>
              <button className="btn btn-saffron" onClick={handleFinishReview}>
                ✓ {t('form.finalizeBtn', 'Finalize Prepared Application')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 5: Application Guidance Complete & Official Submission Portal */}
      {currentStep === 5 && selectedScheme && (
        <div className="civic-form-container">
          <div className="civic-card" style={{ padding: '32px' }}>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <div style={{ fontSize: '3rem', marginBottom: '8px' }}>🇮🇳</div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-navy)', margin: '0 0 6px 0' }}>
                {t('form.completeTitle', 'Application Preparation Complete!')}
              </h2>
              <p style={{ color: 'var(--color-text-secondary)', margin: '0 0 10px 0' }}>
                {selectedScheme.display_name}
              </p>

              {/* Status Badge in Step 5 */}
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '20px', backgroundColor: currentStatusConfig.bgColor, border: `1px solid ${currentStatusConfig.borderColor}` }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: currentStatusConfig.badgeColor }}>
                  {t('progress.currentStatusLabel', 'Application Status')}: {statusLabel}
                </span>
              </div>
            </div>

            {/* Portal Capability & Guidance Box */}
            <div
              style={{
                backgroundColor: 'var(--color-surface-subtle, #EFF6FF)',
                border: '1px solid #BFDBFE',
                borderRadius: '8px',
                padding: '18px',
                marginBottom: '24px',
              }}
            >
              <div style={{ fontWeight: 700, color: '#1E40AF', marginBottom: '6px', fontSize: '0.9375rem' }}>
                🏛️ {t('form.selfSubmissionGuidance', 'Self-Submission Guidance')}
              </div>
              <p style={{ fontSize: '0.875rem', color: '#1E3A8A', margin: '0 0 16px 0', lineHeight: 1.5 }}>
                {selectedScheme.application_portal_type === 'OFFLINE_OFFICE'
                  ? t(
                      'form.offlineOfficeGuidance',
                      'This scheme requires in-person submission at your local Gram Panchayat / Taluk / Anganwadi office. NagrikSaarathi has prepared your document checklist. Print your application summary below and visit the designated office.'
                    )
                  : t(
                      'form.onlinePortalGuidance',
                      'NagrikSaarathi has prepared your application answers and document readiness checklist. You can now independently complete the official submission on the verified government portal below.'
                    )}
              </p>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {selectedScheme.application_portal_type === 'OFFLINE_OFFICE' ? (
                  <>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => window.print()}
                      style={{ fontWeight: 700 }}
                    >
                      🖨️ {t('form.printSummary', 'Print / Save Application Summary')}
                    </button>
                    {selectedScheme.official_source_url && (
                      <a
                        href={selectedScheme.official_source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary"
                      >
                        🔗 {t('form.viewOfficialGuidelines', 'View Official Guidelines')}
                      </a>
                    )}
                  </>
                ) : (
                  <>
                    {(selectedScheme.official_application_url || selectedScheme.official_source_url) && (
                      <a
                        href={selectedScheme.official_application_url || selectedScheme.official_source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-primary"
                        style={{ fontWeight: 700 }}
                        onClick={() => {
                          if (applicationStatus === 'not_started' || applicationStatus === 'ready_for_review') {
                            setApplicationStatus('submitted_externally');
                          }
                        }}
                      >
                        🚀 {selectedScheme.official_application_label || t('form.openOfficialPortal', 'Open Official Government Portal')}
                      </a>
                    )}
                    {selectedScheme.official_source_url && selectedScheme.official_source_url !== selectedScheme.official_application_url && (
                      <a
                        href={selectedScheme.official_source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary"
                      >
                        🔗 {t('form.departmentPortal', 'Department Portal')}
                      </a>
                    )}
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => window.print()}
                    >
                      🖨️ {t('form.printSummary', 'Print / Save Application Summary')}
                    </button>
                  </>
                )}

                {/* Mark as Submitted Externally */}
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setApplicationStatus('submitted_externally');
                    handleSaveProgressLater();
                  }}
                >
                  ✓ {t('progress.officialPortalSubmitPrompt', 'Mark as Submitted on Official Portal')}
                </button>

                {/* Record Official Acknowledgement Number Button */}
                <button
                  type="button"
                  className="btn btn-saffron"
                  onClick={() => setIsRecordingSubmission(!isRecordingSubmission)}
                >
                  📝 {isRecordingSubmission ? 'Close Acknowledgement Form' : t('progress.saveConfirmationBtn', 'Record Submission Confirmation')}
                </button>
              </div>
            </div>

            {/* Official Submission Confirmation Recorder Panel */}
            {isRecordingSubmission && (
              <form
                onSubmit={handleRecordSubmissionConfirmation}
                style={{
                  backgroundColor: 'var(--color-surface, #FFFFFF)',
                  border: '2px solid #86EFAC',
                  borderRadius: '8px',
                  padding: '20px',
                  marginBottom: '24px',
                }}
              >
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--color-navy)', margin: '0 0 6px 0' }}>
                  📝 {t('progress.recordConfirmationTitle', 'Official Government Submission Confirmation')}
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', margin: '0 0 16px 0' }}>
                  {t(
                    'progress.recordConfirmationDesc',
                    'Enter your official acknowledgement or application number received from the government portal/office to track your submission.'
                  )}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', marginBottom: '16px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                      {t('progress.ackNumberLabel', 'Official Acknowledgement / Application Number')} *
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      required
                      placeholder={t('progress.ackNumberPlaceholder', 'e.g. PMKISAN/2026/894231 or REG-987123')}
                      value={submissionDetails.acknowledgementNumber}
                      onChange={(e) =>
                        setSubmissionDetails({ ...submissionDetails, acknowledgementNumber: e.target.value })
                      }
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '4px' }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                      {t('progress.submissionDateLabel', 'Official Submission Date')}
                    </label>
                    <input
                      type="date"
                      className="form-control"
                      value={submissionDetails.submissionDate}
                      onChange={(e) =>
                        setSubmissionDetails({ ...submissionDetails, submissionDate: e.target.value })
                      }
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '4px' }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                      {t('progress.portalOfficeLabel', 'Portal / Submission Office')}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder={t('progress.portalOfficePlaceholder', 'e.g. State Agri Portal / Gram Panchayat')}
                      value={submissionDetails.portalRef}
                      onChange={(e) =>
                        setSubmissionDetails({ ...submissionDetails, portalRef: e.target.value })
                      }
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '4px' }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                      {t('progress.notesLabel', 'Submission Notes / Remarks')}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder={t('progress.notesPlaceholder', 'Optional reference notes or receipt details...')}
                      value={submissionDetails.notes}
                      onChange={(e) =>
                        setSubmissionDetails({ ...submissionDetails, notes: e.target.value })
                      }
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '4px' }}
                    />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button type="submit" className="btn btn-primary" style={{ fontWeight: 700 }}>
                    💾 {t('progress.saveConfirmationBtn', 'Record Submission Confirmation')}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setIsRecordingSubmission(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}

            {/* Recorded Acknowledgement Card */}
            {submissionDetails.acknowledgementNumber && (
              <div
                style={{
                  backgroundColor: '#F0FDF4',
                  border: '1px solid #86EFAC',
                  borderRadius: '6px',
                  padding: '16px 20px',
                  marginBottom: '24px',
                }}
              >
                <div style={{ fontWeight: 800, color: '#166534', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>✓</span>
                  <span>Official Submission Acknowledgement Recorded</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px', marginTop: '10px' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#166534', fontWeight: 600 }}>Acknowledgement No.</div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: '#14532D' }}>{submissionDetails.acknowledgementNumber}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#166534', fontWeight: 600 }}>Submission Date</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#14532D' }}>{submissionDetails.submissionDate}</div>
                  </div>
                  {submissionDetails.portalRef && (
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#166534', fontWeight: 600 }}>Submission Office / Portal</div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#14532D' }}>{submissionDetails.portalRef}</div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Status Update Controls */}
            <div
              style={{
                backgroundColor: 'var(--color-surface, #FFFFFF)',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                padding: '14px 18px',
                marginBottom: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
              }}
            >
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-navy)' }}>
                  {t('progress.updateStatus', 'Update Application Status')}:
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)' }}>
                  Keep track of your scheme application as the government department processes your submission.
                </div>
              </div>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                <select
                  value={applicationStatus}
                  onChange={(e) => {
                    setApplicationStatus(e.target.value);
                    handleSaveProgressLater();
                  }}
                  className="form-control"
                  style={{ padding: '6px 12px', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 600 }}
                >
                  {Object.keys(APPLICATION_STATUS_CONFIG).map((stKey) => (
                    <option key={stKey} value={stKey}>
                      {t(`appStatuses.${stKey}`, APPLICATION_STATUS_CONFIG[stKey].label)}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={handleSaveProgressLater}
                >
                  💾 Save Status
                </button>
              </div>
            </div>

            {/* Printable Application Summary Card */}
            <div
              style={{
                backgroundColor: 'var(--color-surface, #FFFFFF)',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                padding: '20px',
                marginBottom: '24px',
              }}
            >
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '14px', borderBottom: '1px solid var(--color-border)', paddingBottom: '8px' }}>
                📄 {t('form.applicationDraft', 'Your Application Summary')}
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
                {fields.map((f) => (
                  <div key={f.field_key} style={{ backgroundColor: 'var(--color-surface-subtle, #F8FAFC)', padding: '10px', borderRadius: '4px', border: '1px solid var(--color-border-subtle, #E2E8F0)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>
                      {f.labels_by_language?.[currentLang] || f.labels_by_language?.hi || f.field_key}
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-navy)', marginTop: '2px' }}>
                      {formData[f.field_key] || '—'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Actions */}
            <div style={{ display: 'flex', gap: '14px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button className="btn btn-secondary" onClick={handleResetSession}>
                ↺ {t('form.startAnother', 'Start Another Application')}
              </button>

              {onNavigateCatalogue && (
                <button className="btn btn-primary" onClick={onNavigateCatalogue}>
                  🏛️ {t('form.exploreAll', 'Explore All Schemes')}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Field Help / Barrier Resolver Modal */}
      <FieldHelpModal
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
        field={currentField}
        explanationData={fieldExplanation}
        onResolveIssue={handleResolveBarrier}
        onEscalateToHuman={handleEscalateToHuman}
        onSwitchLanguage={() => { setIsLangSwitcherOpen(true); }}
      />

      {/* Scheme Benefits Modal */}
      <SchemeBenefitsModal
        isOpen={isBenefitsModalOpen}
        scheme={selectedScheme}
        onClose={() => setIsBenefitsModalOpen(false)}
        onRequestReview={() => {
          setIsBenefitsModalOpen(false);
          if (onOpenHelp) onOpenHelp();
        }}
      />

      {/* Language Switcher (triggered from help modal) */}
      <LanguageSelectorModal
        isOpen={isLangSwitcherOpen}
        onClose={() => setIsLangSwitcherOpen(false)}
      />
    </div>
  );
}

export default GuidedFormPage;
