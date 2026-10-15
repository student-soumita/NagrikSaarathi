import React, { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import { SchemeBenefitsModal } from '../components/SchemeBenefitsModal';

const INDIAN_STATES = [
  // 28 States
  { code: 'AP', name: 'Andhra Pradesh', type: 'state' },
  { code: 'AR', name: 'Arunachal Pradesh', type: 'state' },
  { code: 'AS', name: 'Assam', type: 'state' },
  { code: 'BR', name: 'Bihar', type: 'state' },
  { code: 'CG', name: 'Chhattisgarh', type: 'state' },
  { code: 'GA', name: 'Goa', type: 'state' },
  { code: 'GJ', name: 'Gujarat', type: 'state' },
  { code: 'HR', name: 'Haryana', type: 'state' },
  { code: 'HP', name: 'Himachal Pradesh', type: 'state' },
  { code: 'JH', name: 'Jharkhand', type: 'state' },
  { code: 'KA', name: 'Karnataka', type: 'state' },
  { code: 'KL', name: 'Kerala', type: 'state' },
  { code: 'MP', name: 'Madhya Pradesh', type: 'state' },
  { code: 'MH', name: 'Maharashtra', type: 'state' },
  { code: 'MN', name: 'Manipur', type: 'state' },
  { code: 'ML', name: 'Meghalaya', type: 'state' },
  { code: 'MZ', name: 'Mizoram', type: 'state' },
  { code: 'NL', name: 'Nagaland', type: 'state' },
  { code: 'OD', name: 'Odisha', type: 'state' },
  { code: 'PB', name: 'Punjab', type: 'state' },
  { code: 'RJ', name: 'Rajasthan', type: 'state' },
  { code: 'SK', name: 'Sikkim', type: 'state' },
  { code: 'TN', name: 'Tamil Nadu', type: 'state' },
  { code: 'TG', name: 'Telangana', type: 'state' },
  { code: 'TR', name: 'Tripura', type: 'state' },
  { code: 'UP', name: 'Uttar Pradesh', type: 'state' },
  { code: 'UK', name: 'Uttarakhand', type: 'state' },
  { code: 'WB', name: 'West Bengal', type: 'state' },
  // 8 Union Territories
  { code: 'AN', name: 'Andaman & Nicobar Islands', type: 'ut' },
  { code: 'CH', name: 'Chandigarh', type: 'ut' },
  { code: 'DN', name: 'Dadra & Nagar Haveli and Daman & Diu', type: 'ut' },
  { code: 'DL', name: 'Delhi (NCT)', type: 'ut' },
  { code: 'JK', name: 'Jammu & Kashmir', type: 'ut' },
  { code: 'LA', name: 'Ladakh', type: 'ut' },
  { code: 'LD', name: 'Lakshadweep', type: 'ut' },
  { code: 'PY', name: 'Puducherry', type: 'ut' },
];

const CATEGORIES = [
  { key: 'all', tKey: 'allCategories', labelEn: 'All Categories' },
  { key: 'agriculture', tKey: 'catAgriculture', labelEn: '🌾 Agriculture & Farmers' },
  { key: 'healthcare', tKey: 'catHealthcare', labelEn: '🏥 Healthcare' },
  { key: 'education', tKey: 'catEducation', labelEn: '🎓 Education & Scholarships' },
  { key: 'housing', tKey: 'catHousing', labelEn: '🏠 Housing' },
  { key: 'women_child', tKey: 'catWomenChild', labelEn: '👧 Women & Child Development' },
  { key: 'pension', tKey: 'catPension', labelEn: '👴 Pensions & Social Security' },
  { key: 'employment', tKey: 'catEmployment', labelEn: '💼 Small Business & Loans' },
  { key: 'welfare', tKey: 'catWelfare', labelEn: '🤝 Welfare & Assistance' },
];

export function SchemeCataloguePage({ onSelectScheme, onNavigateHome, onOpenTracking, onOpenHelp }) {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language || 'en';

  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Selected scheme for Benefits Modal
  const [selectedBenefitsScheme, setSelectedBenefitsScheme] = useState(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const PAGE_SIZE = 12;

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState('all'); // all, central, state, ut
  const [stateFilter, setStateFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Candidate Submission Modal
  const [isCandidateModalOpen, setIsCandidateModalOpen] = useState(false);
  const [candidateModalTab, setCandidateModalTab] = useState('submit'); // 'submit' | 'extract'
  const [candidateForm, setCandidateForm] = useState({
    display_name: '',
    official_source_url: '',
    department_name: '',
    government_level: 'central',
    state_code: '',
    category: 'other',
    description: '',
    user_notes: '',
  });
  const [candidateSubmitting, setCandidateSubmitting] = useState(false);
  const [candidateSuccess, setCandidateSuccess] = useState(null);

  // Form Extract
  const [extractForm, setExtractForm] = useState({ scheme_name: '', form_text_or_url: '', state_code: '', category: 'other' });
  const [extracting, setExtracting] = useState(false);
  const [extractResult, setExtractResult] = useState(null);

  // Benefit Combination Finder
  const [isBenefitFinderOpen, setIsBenefitFinderOpen] = useState(false);
  const [benefitProfile, setBenefitProfile] = useState({
    age: '',
    state_code: '',
    gender: '',
    category_interests: [],
    beneficiary_groups: [],
  });
  const [benefitResults, setBenefitResults] = useState(null);
  const [benefitLoading, setBenefitLoading] = useState(false);
  const [benefitError, setBenefitError] = useState(null);

  const BENEFICIARY_GROUP_OPTIONS = [
    { key: 'students', tKey: 'grpStudents', labelEn: '🎓 Students' },
    { key: 'farmers', tKey: 'grpFarmers', labelEn: '🌾 Farmers' },
    { key: 'women', tKey: 'grpWomen', labelEn: '👩 Women' },
    { key: 'senior_citizens', tKey: 'grpSeniorCitizens', labelEn: '👴 Senior Citizens' },
    { key: 'persons_with_disability', tKey: 'grpPwd', labelEn: '♿ Persons with Disability' },
    { key: 'bpl', tKey: 'grpBpl', labelEn: '📋 Below Poverty Line' },
    { key: 'sc', tKey: 'grpSc', labelEn: '🏷️ Scheduled Caste' },
    { key: 'st', tKey: 'grpSt', labelEn: '🏷️ Scheduled Tribe' },
    { key: 'obc', tKey: 'grpObc', labelEn: '🏷️ OBC' },
    { key: 'urban_poor', tKey: 'grpUrbanPoor', labelEn: '🏙️ Urban Poor' },
    { key: 'rural', tKey: 'grpRural', labelEn: '🏡 Rural Residents' },
    { key: 'self_employed', tKey: 'grpSelfEmployed', labelEn: '🛠️ Self-Employed / Artisans' },
  ];

  const toggleBenefitGroup = (key) => {
    setBenefitProfile((prev) => {
      const existing = prev.beneficiary_groups;
      return {
        ...prev,
        beneficiary_groups: existing.includes(key)
          ? existing.filter((g) => g !== key)
          : [...existing, key],
      };
    });
  };

  const toggleBenefitCategory = (key) => {
    setBenefitProfile((prev) => {
      const existing = prev.category_interests;
      return {
        ...prev,
        category_interests: existing.includes(key)
          ? existing.filter((c) => c !== key)
          : [...existing, key],
      };
    });
  };

  const handleBenefitSearch = async () => {
    try {
      setBenefitLoading(true);
      setBenefitError(null);
      const payload = {
        age: benefitProfile.age ? parseInt(benefitProfile.age, 10) : null,
        state_code: benefitProfile.state_code || null,
        gender: benefitProfile.gender || null,
        category_interests: benefitProfile.category_interests,
        beneficiary_groups: benefitProfile.beneficiary_groups,
        max_results: 12,
      };
      const result = await api.findBenefitCombinations(payload);
      setBenefitResults(result);
    } catch (err) {
      setBenefitError(err.message || 'Unable to fetch benefit combinations.');
    } finally {
      setBenefitLoading(false);
    }
  };

  const fetchSchemes = async (page = currentPage) => {
    try {
      setLoading(true);
      setError(null);
      const params = { page, pageSize: PAGE_SIZE };
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (levelFilter !== 'all') params.level = levelFilter;
      if (stateFilter) params.state = stateFilter;
      if (categoryFilter !== 'all') params.category = categoryFilter;

      const data = await api.getSchemes(params);
      // Paginated response returns { items, total, page, page_size, total_pages }
      if (data && Array.isArray(data.items)) {
        setSchemes(data.items);
        setTotalCount(data.total || data.items.length);
        setTotalPages(data.total_pages || 1);
        setCurrentPage(data.page || page);
      } else if (Array.isArray(data)) {
        // Backward compat for unpaginated
        setSchemes(data);
        setTotalCount(data.length);
        setTotalPages(1);
      }
    } catch (err) {
      console.error('Error fetching schemes:', err);
      setError(err.message || 'Unable to load schemes catalogue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    const timer = setTimeout(() => {
      fetchSchemes(1);
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery, levelFilter, stateFilter, categoryFilter]);

  const handlePageChange = (newPage) => {
    if (newPage < 1 || newPage > totalPages) return;
    setCurrentPage(newPage);
    fetchSchemes(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCandidateSubmit = async (e) => {
    e.preventDefault();
    if (!candidateForm.display_name.trim()) return;

    try {
      setCandidateSubmitting(true);
      const res = await api.submitCandidateScheme(candidateForm);
      setCandidateSuccess({ type: 'submit', data: res });
      setCandidateForm({
        display_name: '',
        official_source_url: '',
        department_name: '',
        government_level: 'central',
        state_code: '',
        category: 'other',
        description: '',
        user_notes: '',
      });
    } catch (err) {
      alert(`Submission error: ${err.message}`);
    } finally {
      setCandidateSubmitting(false);
    }
  };

  const handleExtractSubmit = async (e) => {
    e.preventDefault();
    if (!extractForm.scheme_name.trim() || !extractForm.form_text_or_url.trim()) return;
    try {
      setExtracting(true);
      const res = await api.extractFormSchema(extractForm);
      setExtractResult(res);
      setCandidateSuccess({ type: 'extract', data: res });
    } catch (err) {
      alert(`Extraction error: ${err.message}`);
    } finally {
      setExtracting(false);
    }
  };

  const capabilityLabels = {
    GUIDED_PREPARATION: {
      label: t('catalogue.guidedPrepLabel', 'Guided Preparation Available'),
      color: '#065F46',
      bg: '#D1FAE5',
      icon: '📝',
    },
    DISCOVERY_ONLY: {
      label: t('catalogue.discoveryLabel', 'Official Information & Advisory'),
      color: '#1E40AF',
      bg: '#DBEAFE',
      icon: 'ℹ️',
    },
    DRAFT_EXPORT: {
      label: t('catalogue.draftExportLabel', 'Draft Export Supported'),
      color: '#92400E',
      bg: '#FEF3C7',
      icon: '📄',
    },
  };

  return (
    <div className="civic-container" style={{ padding: '24px 16px 48px' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="badge-civic-service">अखिल भारतीय योजना निर्देशिका</span>
          <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
            Pan-India Scheme Registry
          </span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-navy)', margin: '0 0 8px 0' }}>
          {t('catalogue.pageTitle', 'Government Schemes Catalogue')}
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9375rem', margin: 0, maxWidth: '750px' }}>
          {t('catalogue.pageSubtitle', 'Explore central and state public schemes across India. Check eligibility, required documents, and prepare your application independently with multilingual assistance.')}
        </p>
      </div>

      {/* Search & Filter Toolbar */}
      <div
        className="civic-card scheme-filter-toolbar"
        style={{
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
        }}
      >
        {/* Search Bar Row */}
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '16px' }}>
          <div style={{ flex: '1 1 280px', position: 'relative' }}>
            <input
              type="text"
              className="form-control"
              placeholder={t('catalogue.searchPlaceholder', 'Search by scheme name, keyword, beneficiary, or ministry...')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                fontSize: '0.9375rem',
                borderRadius: '6px',
                border: '1px solid var(--color-border)',
              }}
            />
          </div>

          {/* Level Filter */}
          <div style={{ flex: '0 0 auto', display: 'flex', gap: '6px' }}>
            {[
              { id: 'all', label: t('catalogue.allLevels', 'All') },
              { id: 'central', label: `🏛️ ${t('catalogue.centralGovt', 'Central')}` },
              { id: 'state', label: `🗺️ ${t('catalogue.stateGovt', 'State')}` },
              { id: 'ut', label: `📍 ${t('catalogue.unionTerritory', 'UT')}` },
            ].map((lvl) => (
              <button
                key={lvl.id}
                type="button"
                className={`btn btn-sm ${levelFilter === lvl.id ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => {
                  setLevelFilter(lvl.id);
                  if (lvl.id === 'central') setStateFilter('');
                }}
                style={{ borderRadius: '6px', fontWeight: levelFilter === lvl.id ? 700 : 500 }}
              >
                {lvl.label}
              </button>
            ))}
          </div>

          {/* State Select Dropdown */}
          <div style={{ flex: '0 1 200px' }}>
            <select
              className="form-control"
              value={stateFilter}
              onChange={(e) => {
                setStateFilter(e.target.value);
                if (e.target.value && levelFilter === 'central') {
                  setLevelFilter('all');
                }
              }}
              style={{
                width: '100%',
                padding: '10px 12px',
                fontSize: '0.875rem',
                borderRadius: '6px',
                border: '1px solid var(--color-border)',
              }}
            >
              <option value="">{t('catalogue.allStates', '🌐 All States / UTs')}</option>
              {INDIAN_STATES.map((st) => (
                <option key={st.code} value={st.code}>
                  {st.name} ({st.code})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Category Filter Chips */}
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
          {CATEGORIES.map((cat) => {
            const isSelected = categoryFilter === cat.key;
            return (
              <button
                key={cat.key}
                type="button"
                onClick={() => setCategoryFilter(cat.key)}
                className={`gov-category-chip ${isSelected ? 'active' : ''}`}
                style={{
                  padding: '6px 14px',
                  borderRadius: '16px',
                  fontSize: '0.8125rem',
                  fontWeight: isSelected ? 700 : 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                }}
              >
                {t(`catalogue.${cat.tKey || 'allCategories'}`, cat.labelEn)}
              </button>
            );
          })}
        </div>
      </div>

      {/* Results Header, Submit Candidate Link & Benefit Finder */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
          {loading ? (
            'योजनाएं लोड हो रही हैं...'
          ) : (
            <span>
              {totalCount} {t('catalogue.compatibleFound', 'schemes found')}
              {stateFilter && ` • ${INDIAN_STATES.find((s) => s.code === stateFilter)?.name || stateFilter}`}
              {levelFilter !== 'all' && ` • ${levelFilter.toUpperCase()}`}
              {totalPages > 1 && ` • Page ${currentPage}/${totalPages}`}
            </span>
          )}
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {/* Benefit Combination Finder CTA */}
          <button
            type="button"
            id="benefit-finder-btn"
            onClick={() => {
              setIsBenefitFinderOpen(true);
              setBenefitResults(null);
              setBenefitError(null);
            }}
            className="btn btn-sm"
            style={{
              fontWeight: 700,
              background: 'linear-gradient(135deg, #0F766E 0%, #115E59 100%)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              boxShadow: '0 2px 6px rgba(15,118,110,0.25)',
            }}
          >
            ✨ {t('catalogue.benefitFinder', 'Benefit Finder')}
          </button>

          <button
            type="button"
            onClick={() => {
              setIsCandidateModalOpen(true);
              setCandidateSuccess(null);
            }}
            className="btn btn-secondary btn-sm"
            style={{
              fontWeight: 600,
              color: 'var(--color-navy)',
              borderColor: 'var(--color-navy)',
              backgroundColor: '#EFF6FF',
            }}
          >
            ➕ {t('catalogue.cantFindScheme', 'Scheme not listed? Request assistance')}
          </button>
        </div>
      </div>

      {/* ─── Benefit Combination Finder Modal ─────────────────────────────── */}
      {isBenefitFinderOpen && (
        <div
          id="benefit-finder-modal"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(10,25,47,0.65)',
            zIndex: 1200,
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            overflowY: 'auto',
            padding: '32px 16px',
          }}
          onClick={(e) => { if (e.target === e.currentTarget) setIsBenefitFinderOpen(false); }}
        >
          <div
            style={{
              background: '#FFFFFF',
              borderRadius: '12px',
              width: '100%',
              maxWidth: '780px',
              boxShadow: '0 24px 60px rgba(0,0,0,0.22)',
              overflow: 'hidden',
            }}
          >
            {/* Modal Header */}
            <div
              style={{
                background: 'linear-gradient(135deg, #0F766E 0%, #064E3B 100%)',
                padding: '20px 24px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ color: '#A7F3D0', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: '4px' }}>
                  ✨ BENEFIT COMBINATION FINDER
                </div>
                <h2 style={{ color: '#FFFFFF', fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
                  {t('catalogue.finderTitle', 'Find Compatible Scheme Combinations')}
                </h2>
                <p style={{ color: '#A7F3D0', fontSize: '0.8125rem', margin: '4px 0 0' }}>
                  {t('catalogue.finderSubtitle', 'Based on your profile, discover schemes you may be eligible for simultaneously')}
                </p>
              </div>
              <button
                onClick={() => setIsBenefitFinderOpen(false)}
                style={{ background: 'none', border: 'none', color: '#FFFFFF', fontSize: '1.5rem', cursor: 'pointer', lineHeight: 1 }}
                aria-label="Close"
              >×</button>
            </div>

            <div style={{ padding: '24px' }}>
              {/* Profile Form */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                  gap: '16px',
                  marginBottom: '20px',
                }}
              >
                {/* Age */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '4px' }}>
                    👤 {t('catalogue.ageLabel', 'Age (years)')}
                  </label>
                  <input
                    type="number"
                    min="0" max="120"
                    placeholder="e.g. 35"
                    value={benefitProfile.age}
                    onChange={(e) => setBenefitProfile({ ...benefitProfile, age: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem' }}
                  />
                </div>

                {/* State */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '4px' }}>
                    🗺️ {t('catalogue.stateLabel', 'State / UT')}
                  </label>
                  <select
                    value={benefitProfile.state_code}
                    onChange={(e) => setBenefitProfile({ ...benefitProfile, state_code: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem' }}
                  >
                    <option value="">{t('catalogue.allCentral', 'All / Central')}</option>
                    {INDIAN_STATES.map((s) => (
                      <option key={s.code} value={s.code}>{s.name}</option>
                    ))}
                  </select>
                </div>

                {/* Gender */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '4px' }}>
                    🧬 {t('catalogue.genderLabel', 'Gender')}
                  </label>
                  <select
                    value={benefitProfile.gender}
                    onChange={(e) => setBenefitProfile({ ...benefitProfile, gender: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem' }}
                  >
                    <option value="">{t('catalogue.selectGender', 'Select')}</option>
                    <option value="female">{t('catalogue.female', 'Female')}</option>
                    <option value="male">{t('catalogue.male', 'Male')}</option>
                    <option value="other">{t('catalogue.otherGender', 'Other')}</option>
                  </select>
                </div>
              </div>

              {/* Category Interests */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '8px' }}>
                  🏷️ {t('catalogue.categoriesInterest', 'Scheme Categories of Interest (select multiple)')}
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {CATEGORIES.filter((c) => c.key !== 'all').map((cat) => {
                    const isSelected = benefitProfile.category_interests.includes(cat.key);
                    return (
                      <button
                        key={cat.key}
                        type="button"
                        onClick={() => toggleBenefitCategory(cat.key)}
                        style={{
                          padding: '5px 10px',
                          borderRadius: '14px',
                          fontSize: '0.8125rem',
                          fontWeight: isSelected ? 700 : 500,
                          border: isSelected ? '1.5px solid #0F766E' : '1px solid var(--color-border)',
                          backgroundColor: isSelected ? '#D1FAE5' : '#F8FAFC',
                          color: isSelected ? '#065F46' : 'var(--color-text-primary)',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {t(`catalogue.${cat.tKey || 'allCategories'}`, cat.labelEn)}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Beneficiary Groups */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '8px' }}>
                  👥 {t('catalogue.beneficiaryGroups', 'Beneficiary Groups (select all that apply)')}
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {BENEFICIARY_GROUP_OPTIONS.map((grp) => {
                    const isSelected = benefitProfile.beneficiary_groups.includes(grp.key);
                    return (
                      <button
                        key={grp.key}
                        type="button"
                        onClick={() => toggleBenefitGroup(grp.key)}
                        style={{
                          padding: '5px 10px',
                          borderRadius: '14px',
                          fontSize: '0.8125rem',
                          fontWeight: isSelected ? 700 : 500,
                          border: isSelected ? '1.5px solid var(--color-navy)' : '1px solid var(--color-border)',
                          backgroundColor: isSelected ? '#DBEAFE' : '#F8FAFC',
                          color: isSelected ? 'var(--color-navy)' : 'var(--color-text-primary)',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {t(`catalogue.${grp.tKey || 'grpStudents'}`, grp.labelEn)}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Search Button */}
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '20px' }}>
                <button
                  type="button"
                  onClick={handleBenefitSearch}
                  disabled={benefitLoading}
                  style={{
                    padding: '10px 28px',
                    borderRadius: '8px',
                    fontWeight: 800,
                    fontSize: '0.9375rem',
                    background: benefitLoading ? '#94A3B8' : 'linear-gradient(135deg, #0F766E, #115E59)',
                    color: '#FFFFFF',
                    border: 'none',
                    cursor: benefitLoading ? 'default' : 'pointer',
                    boxShadow: '0 2px 8px rgba(15,118,110,0.3)',
                  }}
                >
                  {benefitLoading
                    ? `🔍 ${t('catalogue.searching', 'Searching...')}`
                    : `✨ ${t('catalogue.findMySchemes', 'Find My Schemes')}`}
                </button>
                {(benefitProfile.category_interests.length > 0 || benefitProfile.beneficiary_groups.length > 0 || benefitProfile.age || benefitProfile.state_code) && (
                  <button
                    type="button"
                    onClick={() => {
                      setBenefitProfile({ age: '', state_code: '', gender: '', category_interests: [], beneficiary_groups: [] });
                      setBenefitResults(null);
                      setBenefitError(null);
                    }}
                    style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer', fontSize: '0.875rem' }}
                  >
                    ✕ {t('catalogue.clear', 'Clear')}
                  </button>
                )}
              </div>

              {/* Error */}
              {benefitError && (
                <div style={{ padding: '12px', backgroundColor: '#FEE2E2', borderRadius: '6px', color: '#B91C1C', marginBottom: '16px', fontSize: '0.875rem' }}>
                  {benefitError}
                </div>
              )}

              {/* Results */}
              {benefitResults && (
                <div>
                  {/* Summary bar */}
                  <div
                    style={{
                      backgroundColor: '#F0FDF4',
                      border: '1px solid #BBF7D0',
                      borderRadius: '8px',
                      padding: '12px 16px',
                      marginBottom: '16px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}
                  >
                    <div>
                      <span style={{ fontWeight: 700, color: '#065F46', fontSize: '0.9375rem' }}>
                        {benefitResults.total_matched} {t('catalogue.compatibleFound', 'compatible schemes found')}
                      </span>
                      <span style={{ color: '#6B7280', fontSize: '0.8125rem', marginLeft: '8px' }}>
                        — {benefitResults.profile_summary}
                      </span>
                    </div>
                  </div>

                  {/* Disclaimer */}
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: '#6B7280',
                      backgroundColor: '#FFFBEB',
                      border: '1px solid #FDE68A',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      marginBottom: '16px',
                    }}
                  >
                    ⚠️ {benefitResults.disclaimer}
                  </div>

                  {benefitResults.total_matched === 0 ? (
                    <div style={{ textAlign: 'center', padding: '32px', color: '#6B7280' }}>
                      <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔍</div>
                      <div>{t('catalogue.noMatchingProfile', 'No matching schemes for your profile. Try selecting different categories or groups.')}</div>
                    </div>
                  ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '14px' }}>
                      {benefitResults.matches.map((match) => {
                        const scorePercent = Math.round(match.compatibility_score * 100);
                        const scoreColor = scorePercent >= 70 ? '#065F46' : scorePercent >= 45 ? '#92400E' : '#1E40AF';
                        const scoreBg = scorePercent >= 70 ? '#D1FAE5' : scorePercent >= 45 ? '#FEF3C7' : '#DBEAFE';
                        return (
                          <div
                            key={match.scheme.id}
                            style={{
                              border: '1px solid #E2E8F0',
                              borderRadius: '8px',
                              overflow: 'hidden',
                              backgroundColor: '#FFFFFF',
                              boxShadow: '0 2px 6px rgba(0,0,0,0.05)',
                              transition: 'box-shadow 0.2s ease',
                            }}
                          >
                            {/* Score bar */}
                            <div
                              style={{
                                height: '4px',
                                backgroundColor: scoreBg,
                                background: `linear-gradient(to right, ${scoreColor} ${scorePercent}%, #E5E7EB ${scorePercent}%)`,
                              }}
                            />
                            <div style={{ padding: '14px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
                                <h4 style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--color-navy)', margin: 0, flex: 1 }}>
                                  {match.scheme.display_name}
                                </h4>
                                <span
                                  style={{
                                    padding: '2px 8px',
                                    borderRadius: '10px',
                                    backgroundColor: scoreBg,
                                    color: scoreColor,
                                    fontSize: '0.75rem',
                                    fontWeight: 800,
                                    whiteSpace: 'nowrap',
                                  }}
                                >
                                  {scorePercent}% match
                                </span>
                              </div>
                              <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '8px' }}>
                                {match.scheme.department_name}
                                {match.scheme.state_code && ` · ${match.scheme.state_code}`}
                                {' · '}
                                <span style={{ textTransform: 'capitalize' }}>{match.scheme.category?.replace(/_/g, ' ')}</span>
                              </div>
                              <ul style={{ margin: '0 0 10px', padding: '0 0 0 14px', fontSize: '0.8125rem', color: '#374151', lineHeight: 1.5 }}>
                                {match.match_reasons.map((r, i) => <li key={i}>{r}</li>)}
                              </ul>
                              <button
                                type="button"
                                onClick={() => {
                                  setIsBenefitFinderOpen(false);
                                  onSelectScheme && onSelectScheme(match.scheme.id);
                                }}
                                style={{
                                  padding: '6px 14px',
                                  borderRadius: '6px',
                                  background: 'var(--color-navy)',
                                  color: '#FFFFFF',
                                  border: 'none',
                                  fontSize: '0.8125rem',
                                  fontWeight: 700,
                                  cursor: 'pointer',
                                }}
                              >
                                📋 {t('catalogue.getGuidance', 'Get Guidance')}
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Schemes Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--color-text-muted)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔄</div>
          <div>योजना निर्देशिका लोड हो रही है...</div>
        </div>
      ) : error ? (
        <div
          style={{
            backgroundColor: '#FEE2E2',
            border: '1px solid #FCA5A5',
            color: '#B91C1C',
            padding: '16px',
            borderRadius: '6px',
            textAlign: 'center',
          }}
        >
          {error}
        </div>
      ) : schemes.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: '48px 16px',
            backgroundColor: '#FFFFFF',
            border: '1px dashed var(--color-border)',
            borderRadius: '8px',
          }}
        >
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>🔍</div>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '4px' }}>
            {t('catalogue.noSchemesFound', 'No matching schemes found')}
          </h3>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '16px' }}>
            {t('catalogue.tryAdjusting', 'Try adjusting your search filters, or submit a request if you cannot find your required scheme.')}
          </p>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => {
              setIsCandidateModalOpen(true);
              setCandidateSuccess(null);
            }}
          >
            ➕ {t('catalogue.submitCandidate', 'Submit Scheme for Verification')}
          </button>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: '20px',
          }}
        >
          {schemes.map((scheme) => {
            const cap = capabilityLabels[scheme.portal_capability] || capabilityLabels.GUIDED_PREPARATION;
            const desc =
              scheme.descriptions_by_language?.[currentLang] ||
              scheme.descriptions_by_language?.hi ||
              scheme.description;

            return (
              <div
                key={scheme.id}
                className="civic-card scheme-card"
                style={{
                  borderRadius: '8px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.03)',
                  transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                }}
              >
                <div>
                  {/* Top Badges */}
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>

                    <span
                      style={{
                        fontSize: '0.6875rem',
                        fontWeight: 700,
                        backgroundColor: scheme.government_level === 'central' ? '#EFF6FF' : '#F0FDF4',
                        color: scheme.government_level === 'central' ? '#1D4ED8' : '#15803D',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        border: '1px solid var(--color-border)',
                      }}
                    >
                      {scheme.government_level === 'central'
                        ? '🏛️ Central'
                        : scheme.government_level === 'ut'
                        ? `📍 UT (${scheme.state_code || ''})`
                        : `🗺️ State (${scheme.state_code || ''})`}
                    </span>

                    <span
                      style={{
                        fontSize: '0.6875rem',
                        fontWeight: 600,
                        backgroundColor: '#F1F5F9',
                        color: '#475569',
                        padding: '2px 6px',
                        borderRadius: '4px',
                      }}
                    >
                      {scheme.category?.toUpperCase() || 'GENERAL'}
                    </span>

                    {scheme.verification_status === 'verified' && (
                      <span
                        style={{
                          fontSize: '0.6875rem',
                          fontWeight: 600,
                          backgroundColor: '#DCFCE7',
                          color: '#166534',
                          padding: '2px 6px',
                          borderRadius: '4px',
                        }}
                        title="Verified against official ministry notification"
                      >
                        ✓ Verified
                      </span>
                    )}
                  </div>

                  {/* Scheme Title */}
                  <h2
                    style={{
                      fontSize: '1.125rem',
                      fontWeight: 700,
                      color: 'var(--color-navy)',
                      margin: '0 0 6px 0',
                      lineHeight: 1.35,
                    }}
                  >
                    {scheme.display_name}
                  </h2>

                  {/* Verified Benefits Pill if present */}
                  {scheme.benefit_details?.benefit_amount && (
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '0.8125rem',
                        fontWeight: 700,
                        backgroundColor: '#ECFDF5',
                        color: '#065F46',
                        border: '1px solid #A7F3D0',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        marginBottom: '8px',
                      }}
                    >
                      <span>🎁 {scheme.benefit_details.benefit_amount}</span>
                      {scheme.benefit_details.frequency_or_duration && (
                        <span style={{ fontSize: '0.75rem', color: '#047857', fontWeight: 500 }}>
                          • {scheme.benefit_details.frequency_or_duration}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Department */}
                  <div
                    style={{
                      fontSize: '0.8125rem',
                      color: 'var(--color-text-secondary)',
                      marginBottom: '12px',
                      fontWeight: 500,
                    }}
                  >
                    🏛️ {scheme.department_name}
                  </div>

                  {/* Description */}
                  <p
                    style={{
                      fontSize: '0.875rem',
                      color: 'var(--color-text-primary)',
                      lineHeight: 1.5,
                      marginBottom: '16px',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                  >
                    {desc}
                  </p>

                  {/* Capability & Submission Badges */}
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '16px' }}>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        backgroundColor: cap.bg,
                        color: cap.color,
                        padding: '3px 7px',
                        borderRadius: '4px',
                      }}
                    >
                      <span>{cap.icon}</span>
                      <span>{cap.label}</span>
                    </div>

                    {scheme.application_portal_type === 'OFFLINE_OFFICE' && (
                      <div
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          backgroundColor: '#FEF3C7',
                          color: '#92400E',
                          padding: '3px 7px',
                          borderRadius: '4px',
                        }}
                      >
                        <span>🏛️</span>
                        <span>{t('catalogue.officeSubmission', 'Office / Panchayat Submission')}</span>
                      </div>
                    )}

                    {scheme.official_source_is_fallback && (
                      <div
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '0.7rem',
                          fontWeight: 500,
                          backgroundColor: '#F1F5F9',
                          color: '#475569',
                          padding: '3px 6px',
                          borderRadius: '4px',
                        }}
                        title="Linked to verified state discovery portal"
                      >
                        <span>🌐</span>
                        <span>{t('catalogue.statePortal', 'State Portal')}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Bottom Actions */}
                <div
                  style={{
                    borderTop: '1px solid var(--color-border)',
                    paddingTop: '14px',
                    display: 'flex',
                    gap: '8px',
                    flexWrap: 'wrap',
                  }}
                >
                  <button
                    type="button"
                    className="btn btn-primary btn-sm"
                    onClick={() => onSelectScheme(scheme.id)}
                    style={{ flex: '1 1 auto', fontWeight: 700, padding: '8px 12px' }}
                  >
                    ✍️ {t('catalogue.guidedApplication', 'Guided Form Preparation')}
                  </button>

                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => setSelectedBenefitsScheme(scheme)}
                    style={{
                      fontWeight: 700,
                      backgroundColor: '#FEF3C7',
                      color: '#92400E',
                      borderColor: '#FCD34D',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '8px 10px',
                      fontSize: '0.78rem',
                    }}
                    title="View verified benefits, coverage, and eligibility rules"
                  >
                    🎁 {t('catalogue.viewBenefits', 'Benefits')}
                  </button>

                  {scheme.official_application_url && scheme.application_portal_type !== 'OFFLINE_OFFICE' && (
                    <a
                      href={scheme.official_application_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '0.75rem', padding: '8px 10px', color: 'var(--color-navy)', fontWeight: 600 }}
                      title={scheme.official_application_label || "Open official application portal"}
                    >
                      🚀 {scheme.application_portal_type === 'STATE_SSO_EDISTRICT'
                        ? t('catalogue.statePortal', 'State Portal')
                        : t('catalogue.applyOnline', 'Apply Online')}
                    </a>
                  )}

                  {scheme.official_source_url && (
                    <a
                      href={scheme.official_source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '0.75rem', padding: '8px 10px' }}
                      title={scheme.official_source_label || "Open official department portal in new tab"}
                    >
                      🔗 {t('catalogue.externalPortal', 'Official Portal')}
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && !loading && !error && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', padding: '24px 0', flexWrap: 'wrap' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
          >
            «
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            ‹ {t('catalogue.previous', 'Prev')}
          </button>
          {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
            let page;
            if (totalPages <= 7) {
              page = i + 1;
            } else if (currentPage <= 4) {
              page = i + 1;
            } else if (currentPage >= totalPages - 3) {
              page = totalPages - 6 + i;
            } else {
              page = currentPage - 3 + i;
            }
            return (
              <button
                key={page}
                className={`btn btn-sm ${currentPage === page ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => handlePageChange(page)}
                style={{ minWidth: 36, fontWeight: currentPage === page ? 800 : 500 }}
              >
                {page}
              </button>
            );
          })}
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            {t('catalogue.next', 'Next')} ›
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
          >
            »
          </button>
          <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginLeft: 8 }}>
            {currentPage}/{totalPages}
          </span>
        </div>
      )}

      {/* Candidate Scheme Modal */}
      {isCandidateModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '16px',
          }}
        >
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '8px',
              maxWidth: '560px',
              width: '100%',
              padding: '24px',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-navy)', margin: 0 }}>
                {t('catalogue.submitModalTitle', 'Request Assistance for Unlisted Scheme')}
              </h3>
              <button
                type="button"
                onClick={() => setIsCandidateModalOpen(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.25rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            {/* Tab Switcher */}
            <div style={{ display: 'flex', borderBottom: '2px solid var(--color-border)', marginBottom: 18 }}>
              {[{ id: 'submit', label: '✏️ Request Listing' }, { id: 'extract', label: '🔍 Auto-Extract Form' }].map(tab => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setCandidateModalTab(tab.id)}
                  style={{
                    padding: '8px 16px', background: 'none', border: 'none',
                    fontWeight: candidateModalTab === tab.id ? 700 : 500,
                    fontSize: '0.875rem', cursor: 'pointer',
                    borderBottom: candidateModalTab === tab.id ? '2px solid var(--color-navy)' : '2px solid transparent',
                    color: candidateModalTab === tab.id ? 'var(--color-navy)' : 'var(--color-text-muted)',
                    marginBottom: -2,
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {candidateSuccess ? (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>✅</div>
                <h4 style={{ color: '#065F46', fontWeight: 700, marginBottom: '6px' }}>
                  {candidateSuccess.type === 'extract' ? t('catalogue.extractModalTitle', 'Form Schema Extracted!') : t('catalogue.successTitle', 'Candidate Scheme Submitted!')}
                </h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '16px' }}>
                  {candidateSuccess.type === 'extract'
                    ? `Extracted ${candidateSuccess.data?.extracted_fields?.length || 0} form fields from provided text. Draft marked for admin review.`
                    : t('catalogue.successNotice', `Scheme "${candidateSuccess.data?.display_name}" has been recorded for editorial review.`)}
                </p>

                {candidateSuccess.data?.tracking_id && (
                  <div
                    style={{
                      backgroundColor: '#EFF6FF',
                      border: '1px solid #BFDBFE',
                      borderRadius: '8px',
                      padding: '12px 16px',
                      marginBottom: '16px',
                      display: 'inline-block',
                      textAlign: 'center',
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1E40AF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Citizen Tracking ID
                    </div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1D4ED8', letterSpacing: '0.05em', margin: '4px 0 8px' }}>
                      {candidateSuccess.data.tracking_id}
                    </div>
                    <button
                      type="button"
                      className="btn btn-primary btn-sm"
                      onClick={() => {
                        const tid = candidateSuccess.data.tracking_id;
                        setIsCandidateModalOpen(false);
                        setCandidateSuccess(null);
                        onOpenTracking && onOpenTracking(tid);
                      }}
                      style={{ fontSize: '0.8125rem', padding: '6px 12px' }}
                    >
                      📋 {t('catalogue.trackRequestNow', 'Track This Request Now')}
                    </button>
                  </div>
                )}

                <div>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => {
                      setIsCandidateModalOpen(false);
                      setCandidateSuccess(null);
                      fetchSchemes(currentPage);
                    }}
                  >
                    {t('catalogue.done', 'Done')}
                  </button>
                </div>
              </div>
            ) : candidateModalTab === 'extract' ? (
              <form onSubmit={handleExtractSubmit}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '14px' }}>
                  Paste the text from a government notice or blank application form. NagrikSaarathi will auto-detect fields and create a draft guided form.
                </p>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>Scheme Name *</label>
                  <input type="text" required className="form-control" placeholder="e.g. PM Awas Yojana Gramin" value={extractForm.scheme_name}
                    onChange={e => setExtractForm({ ...extractForm, scheme_name: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }} />
                </div>
                <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>State (if applicable)</label>
                    <select className="form-control" value={extractForm.state_code} onChange={e => setExtractForm({ ...extractForm, state_code: e.target.value })}
                      style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
                      <option value="">-- Central / NA --</option>
                      {INDIAN_STATES.map(s => <option key={s.code} value={s.code}>{s.name} ({s.code})</option>)}
                    </select>
                  </div>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>Category</label>
                    <select className="form-control" value={extractForm.category} onChange={e => setExtractForm({ ...extractForm, category: e.target.value })}
                      style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
                      {CATEGORIES.filter(c => c.key !== 'all').map(c => <option key={c.key} value={c.key}>{c.labelEn}</option>)}
                    </select>
                  </div>
                </div>
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>Form Text / Notice Content *</label>
                  <textarea rows={7} required className="form-control" placeholder="Paste the form instructions, field labels, or official notice text here..."
                    value={extractForm.form_text_or_url} onChange={e => setExtractForm({ ...extractForm, form_text_or_url: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)', fontFamily: 'monospace', fontSize: '0.8125rem' }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => setIsCandidateModalOpen(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary btn-sm" disabled={extracting}>
                    {extracting ? '🔍 Analyzing...' : '🔍 Extract Form Fields'}
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleCandidateSubmit}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '16px' }}>
                  {t('catalogue.cantFindNotice', 'If a scheme is not in our verified registry, enter its name and official link. Our civic team will verify and prepare guided self-application forms.')}
                </p>

                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                    {t('catalogue.schemeNameLabel', 'Scheme Name / Title *')}
                  </label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="e.g. Mukhyamantri Vayoshri Yojana"
                    value={candidateForm.display_name}
                    onChange={(e) => setCandidateForm({ ...candidateForm, display_name: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                    {t('catalogue.officialUrlLabel', 'Official Portal / Notification URL')}
                  </label>
                  <input
                    type="url"
                    className="form-control"
                    placeholder="https://..."
                    value={candidateForm.official_source_url}
                    onChange={(e) => setCandidateForm({ ...candidateForm, official_source_url: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                      {t('catalogue.govtLevelLabel', 'Level')}
                    </label>
                    <select
                      className="form-control"
                      value={candidateForm.government_level}
                      onChange={(e) => setCandidateForm({ ...candidateForm, government_level: e.target.value })}
                      style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                    >
                      <option value="central">Central (केंद्रीय)</option>
                      <option value="state">State (राज्य)</option>
                      <option value="ut">Union Territory (UT)</option>
                    </select>
                  </div>

                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                      {t('catalogue.stateLabel', 'State (if applicable)')}
                    </label>
                    <select
                      className="form-control"
                      value={candidateForm.state_code}
                      onChange={(e) => setCandidateForm({ ...candidateForm, state_code: e.target.value })}
                      style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                    >
                      <option value="">-- Central / NA --</option>
                      {INDIAN_STATES.map((s) => (
                        <option key={s.code} value={s.code}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, marginBottom: '4px' }}>
                    {t('catalogue.notesLabel', 'Your Note or Challenge')}
                  </label>
                  <textarea
                    rows={3}
                    className="form-control"
                    placeholder={t('catalogue.notesLabel', 'What guidance do you need or what difficulty are you facing with this scheme?')}
                    value={candidateForm.user_notes}
                    onChange={(e) => setCandidateForm({ ...candidateForm, user_notes: e.target.value })}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => setIsCandidateModalOpen(false)}
                  >
                    {t('catalogue.cancel', 'Cancel')}
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary btn-sm"
                    disabled={candidateSubmitting}
                  >
                    {candidateSubmitting
                      ? t('catalogue.submitting', 'Submitting...')
                      : t('catalogue.submitBtn', 'Submit Request')}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Scheme Benefits Modal */}
      <SchemeBenefitsModal
        isOpen={Boolean(selectedBenefitsScheme)}
        scheme={selectedBenefitsScheme}
        onClose={() => setSelectedBenefitsScheme(null)}
        onRequestReview={(s) => {
          setSelectedBenefitsScheme(null);
          onOpenTracking && onOpenTracking();
        }}
      />
    </div>
  );
}
export default SchemeCataloguePage;
