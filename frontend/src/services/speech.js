/**
 * Voice & Accessibility Service for NagrikSaarathi.
 * Shared audio guidance engine supporting all 22 Eighth Schedule Indian languages + English.
 *
 * Capabilities:
 * - Detects compatible browser speech synthesis voices asynchronously (both BCP-47 tags and voice names).
 * - Transparently falls back to backend cloud Text-to-Speech (/api/voice/speak) when browser lacks local voice.
 * - Stops existing playback before changing languages, moving steps, or switching forms.
 * - Full controls: Play, Pause, Resume, Replay, Stop.
 * - Transparent status tracking: Browser voice availability, Cloud voice availability, Written guidance fallback.
 * - Invariant: Never speaks English fallback text while claiming to speak another language.
 */

import { api } from './api';

// BCP-47 tag mappings for Indian languages
export const BCP47_TAGS = {
  en: 'en-IN',
  hi: 'hi-IN',
  bn: 'bn-IN',
  te: 'te-IN',
  mr: 'mr-IN',
  ta: 'ta-IN',
  ur: 'ur-IN',
  gu: 'gu-IN',
  kn: 'kn-IN',
  ml: 'ml-IN',
  pa: 'pa-IN',
  ne: 'ne-NP',
  or: 'or-IN',
  as: 'as-IN',
  sa: 'sa-IN',
  ks: 'ks-IN',
  sd: 'sd-IN',
  kok: 'kok-IN',
  doi: 'doi-IN',
  mni: 'mni-IN',
  brx: 'brx-IN',
  sat: 'sat-IN',
  mai: 'mai-IN',
};

// Fallback voice language tags
const FALLBACK_VOICE_TAGS = {
  en: ['en-IN', 'en-GB', 'en-US', 'en'],
  hi: ['hi-IN', 'hi'],
  bn: ['bn-IN', 'bn-BD', 'bn'],
  te: ['te-IN', 'te'],
  mr: ['mr-IN', 'mr'],
  ta: ['ta-IN', 'ta-LK', 'ta-SG', 'ta'],
  ur: ['ur-IN', 'ur-PK', 'ur'],
  gu: ['gu-IN', 'gu'],
  kn: ['kn-IN', 'kn'],
  ml: ['ml-IN', 'ml'],
  pa: ['pa-IN', 'pa'],
  ne: ['ne-NP', 'ne-IN', 'ne'],
  or: ['or-IN', 'or'],
  as: ['as-IN', 'as'],
  sa: ['sa-IN', 'sa'],
  sd: ['sd-IN', 'sd-PK', 'sd'],
  ks: ['ks-IN', 'ks'],
  kok: ['kok-IN', 'kok'],
  doi: ['doi-IN', 'doi'],
  mni: ['mni-IN', 'mni'],
  brx: ['brx-IN', 'brx'],
  sat: ['sat-IN', 'sat'],
  mai: ['mai-IN', 'mai'],
};

// Language keywords in voice names (helps detect voices across OS vendors)
const VOICE_NAME_KEYWORDS = {
  en: ['english', 'india', 'uk', 'us'],
  hi: ['hindi', 'हिन्दी', 'kalpana', 'hemant', 'swara', 'madhur'],
  bn: ['bengali', 'bangla', 'বাংলা', 'tapan', 'bashkar'],
  te: ['telugu', 'తెలుగు', 'mohan', 'shruti'],
  mr: ['marathi', 'मराठी', 'aarohi', 'manohar'],
  ta: ['tamil', 'தமிழ்', 'valluvar', 'pallavi'],
  ur: ['urdu', 'اردو', 'gul', 'salman'],
  gu: ['gujarati', 'ગુજરાતી', 'dhwani', 'niranjan'],
  kn: ['kannada', 'ಕನ್ನಡ', 'gagan', 'sapna'],
  ml: ['malayalam', 'മലയാളം', 'midhun', 'sobhana'],
  pa: ['punjabi', 'ਪੰਜਾਬੀ', 'raajan', 'gurpreet'],
  ne: ['nepali', 'नेपाली'],
  or: ['odia', 'oriya', 'ଓଡ଼ିଆ'],
  as: ['assamese', 'অসমীয়া'],
  sa: ['sanskrit', 'संस्कृतम्'],
  sd: ['sindhi', 'سنڌي'],
  ks: ['kashmiri', 'कॉशुर'],
  kok: ['konkani', 'कोंकणी'],
  doi: ['dogri', 'डोगरी'],
  mni: ['manipuri', 'মৈতৈলোন্'],
  brx: ['bodo', 'बड़ो'],
  sat: ['santali', 'ᱥᱟᱱᱛᱟᱲᱤ'],
  mai: ['maithili', 'मैथिली'],
};

let cachedVoices = [];
let voicesListeners = [];
let activeAudioElement = null; // HTML5 Audio instance for backend cloud TTS
let activeMode = 'none'; // 'browser' | 'cloud' | 'none'

if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  const loadVoices = () => {
    cachedVoices = window.speechSynthesis.getVoices() || [];
    voicesListeners.forEach((fn) => fn(cachedVoices));
  };
  loadVoices();
  window.speechSynthesis.onvoiceschanged = loadVoices;
}

export class SpeechService {
  static isSpeechRecognitionSupported() {
    return typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
  }

  static isSpeechSynthesisSupported() {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  static onVoicesChanged(callback) {
    if (typeof callback === 'function') {
      voicesListeners.push(callback);
      if (cachedVoices.length > 0) callback(cachedVoices);
    }
  }

  static getAvailableVoices() {
    if (!this.isSpeechSynthesisSupported()) return [];
    if (!cachedVoices.length) cachedVoices = window.speechSynthesis.getVoices() || [];
    return cachedVoices;
  }

  /**
   * Find matching speech synthesis voice for a language code.
   * Checks BCP-47 tags, prefix matching, and voice descriptive names.
   */
  static getMatchingVoice(languageCode) {
    if (!this.isSpeechSynthesisSupported()) {
      return { supported: false, voice: null, voiceName: '', langTag: '' };
    }

    const voices = this.getAvailableVoices();
    const candidateTags = FALLBACK_VOICE_TAGS[languageCode] || [BCP47_TAGS[languageCode] || languageCode];

    // 1. Exact BCP-47 match
    for (const tag of candidateTags) {
      const tagLower = tag.toLowerCase().replace('_', '-');
      const exact = voices.find((v) => v.lang.toLowerCase().replace('_', '-') === tagLower);
      if (exact) {
        return { supported: true, voice: exact, voiceName: exact.name, langTag: exact.lang, source: 'browser' };
      }
    }

    // 2. Prefix match (e.g. 'bn' matches 'bn-IN' or 'bn-BD')
    for (const tag of candidateTags) {
      const prefixKey = tag.toLowerCase().split('-')[0].split('_')[0];
      const prefixMatch = voices.find((v) => {
        const vLang = v.lang.toLowerCase().replace('_', '-');
        return vLang === prefixKey || vLang.startsWith(prefixKey + '-');
      });
      if (prefixMatch) {
        return { supported: true, voice: prefixMatch, voiceName: prefixMatch.name, langTag: prefixMatch.lang, source: 'browser' };
      }
    }

    // 3. Name-based match (e.g. "Bengali" or "বাংলা" in voice title)
    const keywords = VOICE_NAME_KEYWORDS[languageCode] || [];
    for (const kw of keywords) {
      const kwLower = kw.toLowerCase();
      const namedVoice = voices.find((v) => v.name.toLowerCase().includes(kwLower));
      if (namedVoice) {
        return { supported: true, voice: namedVoice, voiceName: namedVoice.name, langTag: namedVoice.lang, source: 'browser' };
      }
    }

    return {
      supported: false,
      voice: null,
      voiceName: '',
      langTag: BCP47_TAGS[languageCode] || languageCode,
      source: 'none',
    };
  }

  /**
   * Checks audio guidance capability for a given language.
   * Returns complete status matrix: browser voice, cloud TTS, and tested status.
   */
  static getLanguageAudioStatus(languageCode) {
    const browserMatch = this.getMatchingVoice(languageCode);
    const hasBrowser = browserMatch.supported;

    // Supported cloud TTS languages in Bhashini / Indic TTS standards
    const cloudSupportedLangs = new Set([
      'hi', 'bn', 'ta', 'te', 'mr', 'gu', 'kn', 'ml', 'pa', 'ur', 'or', 'as', 'ne', 'en'
    ]);
    const hasCloud = cloudSupportedLangs.has(languageCode);

    return {
      languageCode,
      browserTTS: hasBrowser,
      browserVoiceName: browserMatch.voiceName || null,
      cloudTTS: hasCloud,
      audioAvailable: hasBrowser || hasCloud,
      writtenAvailable: true,
      isTested: hasBrowser,
    };
  }

  /**
   * Detects if text is a raw technical key rather than human guidance
   */
  static isRawTranslationKey(text) {
    if (!text || typeof text !== 'string') return true;
    const trimmed = text.trim();
    return /^[a-z0-9_-]+(\.[a-z0-9_-]+)+$/i.test(trimmed);
  }

  /**
   * Main speech playback method.
   * 1. Attempts browser Web Speech API.
   * 2. If browser voice is missing, seamlessly calls cloud TTS (/api/voice/speak).
   * 3. If neither is available, cleanly reports limitation without failing or speaking English.
   */
  static async speakGuidance({
    text,
    languageCode,
    onStart,
    onPause,
    onResume,
    onEnd,
    onError,
  }) {
    // Stop any existing playback first
    this.stopSpeaking();

    if (!text || !text.trim() || this.isRawTranslationKey(text)) {
      onError && onError('No valid guidance text available to read aloud.');
      return false;
    }

    const langCode = (languageCode || 'en').toLowerCase().trim();
    const voiceMatch = this.getMatchingVoice(langCode);

    // ── Path 1: Native Browser SpeechSynthesis ─────────────────────────
    if (voiceMatch.supported && this.isSpeechSynthesisSupported()) {
      try {
        const utterance = new SpeechSynthesisUtterance(text.trim());
        utterance.lang = voiceMatch.langTag || BCP47_TAGS[langCode] || 'en-IN';
        if (voiceMatch.voice) {
          utterance.voice = voiceMatch.voice;
        }
        utterance.rate = 0.92; // Comfortable civic guidance reading pace
        utterance.pitch = 1.0;

        utterance.onstart = () => {
          activeMode = 'browser';
          onStart && onStart({ voiceName: voiceMatch.voiceName, source: 'browser', langTag: utterance.lang });
        };
        utterance.onpause = () => {
          onPause && onPause();
        };
        utterance.onresume = () => {
          onResume && onResume();
        };
        utterance.onend = () => {
          activeMode = 'none';
          onEnd && onEnd();
        };
        utterance.onerror = (e) => {
          activeMode = 'none';
          if (e.error !== 'canceled' && e.error !== 'interrupted') {
            onError && onError(e.error || 'Speech error occurred.');
          }
          onEnd && onEnd();
        };

        window.speechSynthesis.speak(utterance);
        return true;
      } catch (err) {
        console.warn('Browser speech synthesis failed, attempting cloud fallback:', err);
      }
    }

    // ── Path 2: Backend Cloud Text-To-Speech Fallback (/api/voice/speak) ─
    try {
      const resp = await api.speakText({
        text: text.trim().slice(0, 1000),
        language_code: langCode,
      });

      if (resp && resp.audio_base64) {
        const audioSrc = `data:${resp.audio_format || 'audio/wav'};base64,${resp.audio_base64}`;
        const audio = new Audio(audioSrc);
        activeAudioElement = audio;
        activeMode = 'cloud';

        audio.onplay = () => {
          onStart && onStart({ voiceName: 'Indic Cloud Voice', source: 'cloud', langTag: langCode });
        };
        audio.onpause = () => {
          onPause && onPause();
        };
        audio.onended = () => {
          activeAudioElement = null;
          activeMode = 'none';
          onEnd && onEnd();
        };
        audio.onerror = () => {
          activeAudioElement = null;
          activeMode = 'none';
          onError && onError('Cloud audio playback encountered an error.');
          onEnd && onEnd();
        };

        await audio.play();
        return true;
      }

      // If backend reports unconfigured voice provider
      if (resp && resp.disclaimer) {
        activeMode = 'none';
        onError && onError('VOICE_UNAVAILABLE', {
          reason: resp.disclaimer,
          writtenAvailable: true,
          languageCode: langCode,
        });
        return false;
      }
    } catch (apiErr) {
      console.warn('Cloud TTS fallback request error:', apiErr);
    }

    // ── Path 3: Voice Unavailable Limitation ──────────────────────────
    // Strictly report limitation; NEVER speak English fallback for other languages
    activeMode = 'none';
    onError && onError('VOICE_UNAVAILABLE', {
      reason: `Audio voice is not natively installed in your browser for this language (${langCode.toUpperCase()}).`,
      writtenAvailable: true,
      languageCode: langCode,
    });
    return false;
  }

  static pauseSpeaking() {
    if (activeMode === 'browser' && this.isSpeechSynthesisSupported()) {
      window.speechSynthesis.pause();
    } else if (activeMode === 'cloud' && activeAudioElement) {
      activeAudioElement.pause();
    }
  }

  static resumeSpeaking() {
    if (activeMode === 'browser' && this.isSpeechSynthesisSupported()) {
      window.speechSynthesis.resume();
    } else if (activeMode === 'cloud' && activeAudioElement) {
      activeAudioElement.play().catch(() => {});
    }
  }

  static stopSpeaking() {
    if (this.isSpeechSynthesisSupported()) {
      window.speechSynthesis.cancel();
    }
    if (activeAudioElement) {
      try {
        activeAudioElement.pause();
        activeAudioElement.currentTime = 0;
      } catch (_) {}
      activeAudioElement = null;
    }
    activeMode = 'none';
  }

  static isSpeaking() {
    if (activeMode === 'browser' && this.isSpeechSynthesisSupported()) {
      return window.speechSynthesis.speaking && !window.speechSynthesis.paused;
    }
    if (activeMode === 'cloud' && activeAudioElement) {
      return !activeAudioElement.paused && !activeAudioElement.ended;
    }
    return false;
  }

  static isPaused() {
    if (activeMode === 'browser' && this.isSpeechSynthesisSupported()) {
      return window.speechSynthesis.paused;
    }
    if (activeMode === 'cloud' && activeAudioElement) {
      return activeAudioElement.paused && activeAudioElement.currentTime > 0;
    }
    return false;
  }

  /**
   * Start speech recognition for voice form input.
   */
  static startListening({ languageCode, onResult, onError, onEnd }) {
    if (!this.isSpeechRecognitionSupported()) {
      onError && onError('Your browser does not support speech recognition.');
      return null;
    }

    const bcpTag = BCP47_TAGS[languageCode] || 'hi-IN';
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = bcpTag;
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((r) => r[0].transcript)
        .join('');
      onResult && onResult(transcript, event.results[0].isFinal);
    };

    recognition.onerror = (event) => {
      onError && onError(event.error);
    };

    recognition.onend = () => {
      onEnd && onEnd();
    };

    try {
      recognition.start();
      return recognition;
    } catch (err) {
      onError && onError(err.message);
      return null;
    }
  }
}
