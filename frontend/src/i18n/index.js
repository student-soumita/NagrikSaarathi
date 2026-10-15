/**
 * NagrikSaarathi i18n Configuration.
 * Loads English and all 22 Eighth Schedule Indian languages.
 * English is the default language, and users can switch to/from any language at any time.
 * Handles document text-direction (LTR/RTL) and script shaping.
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import all locale resources (English + 22 Eighth Schedule Indian languages)
import enLocale from './locales/en.json';
import asLocale from './locales/as.json';
import bnLocale from './locales/bn.json';
import brxLocale from './locales/brx.json';
import doiLocale from './locales/doi.json';
import guLocale from './locales/gu.json';
import hiLocale from './locales/hi.json';
import knLocale from './locales/kn.json';
import ksLocale from './locales/ks.json';
import kokLocale from './locales/kok.json';
import maiLocale from './locales/mai.json';
import mlLocale from './locales/ml.json';
import mniLocale from './locales/mni.json';
import mrLocale from './locales/mr.json';
import neLocale from './locales/ne.json';
import orLocale from './locales/or.json';
import paLocale from './locales/pa.json';
import saLocale from './locales/sa.json';
import satLocale from './locales/sat.json';
import sdLocale from './locales/sd.json';
import taLocale from './locales/ta.json';
import teLocale from './locales/te.json';
import urLocale from './locales/ur.json';

export const LANGUAGES_METADATA = [
  { code: 'en', englishName: 'English', nativeName: 'English', script: 'Latin', direction: 'ltr', supportsVoice: true },
  { code: 'hi', englishName: 'Hindi', nativeName: 'हिन्दी', script: 'Devanagari', direction: 'ltr', supportsVoice: true },
  { code: 'bn', englishName: 'Bengali', nativeName: 'বাংলা', script: 'Eastern Nagari (Bengali)', direction: 'ltr', supportsVoice: true },
  { code: 'te', englishName: 'Telugu', nativeName: 'తెలుగు', script: 'Telugu', direction: 'ltr', supportsVoice: true },
  { code: 'mr', englishName: 'Marathi', nativeName: 'मराठी', script: 'Devanagari', direction: 'ltr', supportsVoice: true },
  { code: 'ta', englishName: 'Tamil', nativeName: 'தமிழ்', script: 'Tamil', direction: 'ltr', supportsVoice: true },
  { code: 'ur', englishName: 'Urdu', nativeName: 'اردو', script: 'Perso-Arabic (Nastaliq)', direction: 'rtl', supportsVoice: true },
  { code: 'gu', englishName: 'Gujarati', nativeName: 'ગુજરાતી', script: 'Gujarati', direction: 'ltr', supportsVoice: true },
  { code: 'kn', englishName: 'Kannada', nativeName: 'ಕನ್ನಡ', script: 'Kannada', direction: 'ltr', supportsVoice: true },
  { code: 'ml', englishName: 'Malayalam', nativeName: 'മലയാളം', script: 'Malayalam', direction: 'ltr', supportsVoice: true },
  { code: 'or', englishName: 'Odia', nativeName: 'ଓଡ଼ିଆ', script: 'Odia', direction: 'ltr', supportsVoice: false },
  { code: 'pa', englishName: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', script: 'Gurmukhi', direction: 'ltr', supportsVoice: true },
  { code: 'as', englishName: 'Assamese', nativeName: 'অসমীয়া', script: 'Eastern Nagari (Assamese)', direction: 'ltr', supportsVoice: false },
  { code: 'mai', englishName: 'Maithili', nativeName: 'मैथिली', script: 'Devanagari', direction: 'ltr', supportsVoice: false },
  { code: 'sat', englishName: 'Santali', nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ', script: 'Ol Chiki', direction: 'ltr', supportsVoice: false },
  { code: 'ks', englishName: 'Kashmiri', nativeName: 'कॉशुर / كٲशُر', script: 'Perso-Arabic / Devanagari', direction: 'rtl', supportsVoice: false },
  { code: 'ne', englishName: 'Nepali', nativeName: 'नेपाली', script: 'Devanagari', direction: 'ltr', supportsVoice: true },
  { code: 'kok', englishName: 'Konkani', nativeName: 'कोंकणी', script: 'Devanagari', direction: 'ltr', supportsVoice: false },
  { code: 'sd', englishName: 'Sindhi', nativeName: 'سنڌي / सिन्धी', script: 'Perso-Arabic / Devanagari', direction: 'rtl', supportsVoice: false },
  { code: 'doi', englishName: 'Dogri', nativeName: 'डोगरी', script: 'Devanagari', direction: 'ltr', supportsVoice: false },
  { code: 'mni', englishName: 'Manipuri', nativeName: 'মৈতৈলোন্', script: 'Meitei Mayek / Bengali', direction: 'ltr', supportsVoice: false },
  { code: 'brx', englishName: 'Bodo', nativeName: 'बड़ो', script: 'Devanagari', direction: 'ltr', supportsVoice: false },
  { code: 'sa', englishName: 'Sanskrit', nativeName: 'संस्कृतम्', script: 'Devanagari', direction: 'ltr', supportsVoice: false },
];

const resources = {
  en: { translation: enLocale },
  as: { translation: asLocale },
  bn: { translation: bnLocale },
  brx: { translation: brxLocale },
  doi: { translation: doiLocale },
  gu: { translation: guLocale },
  hi: { translation: hiLocale },
  kn: { translation: knLocale },
  ks: { translation: ksLocale },
  kok: { translation: kokLocale },
  mai: { translation: maiLocale },
  ml: { translation: mlLocale },
  mni: { translation: mniLocale },
  mr: { translation: mrLocale },
  ne: { translation: neLocale },
  or: { translation: orLocale },
  pa: { translation: paLocale },
  sa: { translation: saLocale },
  sat: { translation: satLocale },
  sd: { translation: sdLocale },
  ta: { translation: taLocale },
  te: { translation: teLocale },
  ur: { translation: urLocale },
};

// Set English as the default language
const LANG_MIGRATION_KEY = 'nagrik_lang_migrated_en_v2';
let savedLang = localStorage.getItem('nagrik_lang');
if (!localStorage.getItem(LANG_MIGRATION_KEY)) {
  if (!savedLang || savedLang === 'hi') {
    savedLang = 'en';
    localStorage.setItem('nagrik_lang', 'en');
  }
  localStorage.setItem(LANG_MIGRATION_KEY, 'true');
} else if (!savedLang) {
  savedLang = 'en';
}

export const missingTranslationLog = [];

i18n.use(initReactI18next).init({
  resources,
  lng: savedLang || 'en',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
  saveMissing: true,
  missingKeyHandler: (lng, ns, key) => {
    if (lng !== 'en') {
      missingTranslationLog.push({
        lang: lng,
        key: key,
        time: new Date().toISOString(),
      });
    }
  },
  parseMissingKeyHandler: (key) => {
    // Never show raw internal keys like "guided_form.next_step" to citizens
    if (typeof key !== 'string') return '';
    const parts = key.split('.');
    const leaf = parts[parts.length - 1];
    return leaf
      .replace(/([A-Z])/g, ' $1')
      .replace(/[_-]/g, ' ')
      .replace(/^./, (s) => s.toUpperCase())
      .trim();
  },
});

export function setAppLanguage(langCode) {
  const meta = LANGUAGES_METADATA.find((l) => l.code === langCode);
  const dir = meta ? meta.direction : 'ltr';

  i18n.changeLanguage(langCode);
  localStorage.setItem('nagrik_lang', langCode);
  localStorage.setItem(LANG_MIGRATION_KEY, 'true');

  // Set document-level direction and lang attribute for accessibility & text shaping
  document.documentElement.setAttribute('lang', langCode);
  document.documentElement.setAttribute('dir', dir);

  if (dir === 'rtl') {
    document.documentElement.classList.add('rtl-layout');
  } else {
    document.documentElement.classList.remove('rtl-layout');
  }

  // Also notify user profile if logged in
  const storedUser = sessionStorage.getItem('nagrik_user') || localStorage.getItem('nagrik_user');
  if (storedUser) {
    try {
      import('../services/api').then(({ api }) => {
        api.updateProfile({ preferred_language: langCode }).catch(() => {});
      });
    } catch (_) {}
  }
}

// Initial direction setting
const initialMeta = LANGUAGES_METADATA.find((l) => l.code === (savedLang || 'en'));
if (initialMeta) {
  document.documentElement.setAttribute('lang', savedLang || 'en');
  document.documentElement.setAttribute('dir', initialMeta.direction);
  if (initialMeta.direction === 'rtl') {
    document.documentElement.classList.add('rtl-layout');
  }
}

export default i18n;
