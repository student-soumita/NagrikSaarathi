import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { SpeechService } from '../services/speech';
import { LANGUAGES_METADATA } from '../i18n';

export function VoiceControl({
  onApplyTranscript,
  textToRead = '',
  stepTitle = '',
  fieldKey = '',
}) {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language;
  const currentMeta = LANGUAGES_METADATA.find((l) => l.code === currentLang) || LANGUAGES_METADATA[0];

  const [isListening, setIsListening] = useState(false);
  const [playbackState, setPlaybackState] = useState('idle'); // 'idle' | 'playing' | 'paused'
  const [voiceMatchInfo, setVoiceMatchInfo] = useState({ supported: false, voiceName: '' });
  const [transcriptDraft, setTranscriptDraft] = useState('');
  const [voiceNotice, setVoiceNotice] = useState(null);
  const [voiceError, setVoiceError] = useState(null);

  // Check voice availability for current language
  useEffect(() => {
    SpeechService.stopSpeaking();
    setPlaybackState('idle');
    setIsListening(false);
    setTranscriptDraft('');
    setVoiceError(null);
    setVoiceNotice(null);

    const CLOUD_TTS_SUPPORTED = new Set(['bn', 'te', 'ta', 'ur', 'hi', 'mr', 'gu', 'kn', 'ml', 'pa', 'ne', 'en']);
    const checkVoice = () => {
      const match = SpeechService.getMatchingVoice(currentLang);
      setVoiceMatchInfo(match);
      if (!match.supported && !CLOUD_TTS_SUPPORTED.has(currentLang)) {
        setVoiceNotice(
          t(
            'audio.voiceUnavailable',
            `${currentMeta.nativeName || currentMeta.englishName} audio synthesis is not available. Showing full written instructions below.`
          )
        );
      } else {
        setVoiceNotice(null);
      }
    };

    checkVoice();
    SpeechService.onVoicesChanged(checkVoice);

    return () => {
      SpeechService.stopSpeaking();
    };
  }, [currentLang, fieldKey]);

  // Stop speaking when step or field changes
  useEffect(() => {
    SpeechService.stopSpeaking();
    setPlaybackState('idle');
  }, [fieldKey, textToRead]);

  const handleStartListening = () => {
    setVoiceError(null);
    setTranscriptDraft('');
    setIsListening(true);

    const rec = SpeechService.startListening({
      languageCode: currentLang,
      onResult: (text) => {
        setTranscriptDraft(text);
      },
      onError: (err) => {
        setVoiceError(typeof err === 'string' ? err : 'Microphone error or permission denied');
        setIsListening(false);
      },
      onEnd: () => {
        setIsListening(false);
      },
    });

    if (!rec) {
      setIsListening(false);
    }
  };

  const handlePlay = async () => {
    if (!textToRead || !textToRead.trim()) {
      setVoiceError(t('audio.noInstructions', 'No instructions available to read aloud for this step.'));
      return;
    }

    setVoiceError(null);
    setPlaybackState('playing');

    const started = await SpeechService.speakGuidance({
      text: textToRead,
      languageCode: currentLang,
      onStart: (info) => {
        setPlaybackState('playing');
        if (info && info.source === 'cloud') {
          setVoiceNotice(t('audio.cloudNotice', 'Playing audio via Cloud Speech Synthesis.'));
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
          setVoiceError(typeof err === 'string' ? err : 'Speech playback error occurred.');
        }
      },
    });

    if (!started && playbackState === 'playing') {
      setPlaybackState('idle');
    }
  };

  const handlePause = () => {
    SpeechService.pauseSpeaking();
    setPlaybackState('paused');
  };

  const handleResume = () => {
    SpeechService.resumeSpeaking();
    setPlaybackState('playing');
  };

  const handleReplay = () => {
    SpeechService.stopSpeaking();
    handlePlay();
  };

  const handleStop = () => {
    SpeechService.stopSpeaking();
    setPlaybackState('idle');
  };

  const handleApply = () => {
    if (transcriptDraft.trim() && onApplyTranscript) {
      onApplyTranscript(transcriptDraft.trim());
      setTranscriptDraft('');
    }
  };

  return (
    <div
      className="civic-audio-guidance"
      style={{
        marginTop: '12px',
        padding: '10px 14px',
        backgroundColor: '#F8F9FA',
        border: '1px solid #E2E8F0',
        borderRadius: '6px',
      }}
      role="region"
      aria-label="Audio Guidance Controls"
    >
      {/* Audio Status Banner */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '8px',
          marginBottom: '8px',
          fontSize: '0.8125rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '1.1rem' }} aria-hidden="true">
            {playbackState === 'playing' ? '🔊' : playbackState === 'paused' ? '⏸️' : '🎧'}
          </span>
          <span style={{ fontWeight: 600, color: 'var(--color-navy)' }}>
            {t('audio.guidance', 'Audio Guidance')}
          </span>
          {stepTitle && (
            <span style={{ color: 'var(--color-text-secondary)' }}>
              • {stepTitle}
            </span>
          )}
        </div>

        <div style={{ fontSize: '0.75rem', color: 'var(--color-teal)', fontWeight: 500 }}>
          <span>{currentMeta.nativeName} ({currentMeta.englishName})</span>
          {voiceMatchInfo.voiceName && (
            <span style={{ color: 'var(--color-text-muted)' }}> · {voiceMatchInfo.voiceName}</span>
          )}
        </div>
      </div>

      {/* Playback Controls & Voice Input */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
        {/* Play / Resume Button */}
        {playbackState === 'idle' && (
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={handlePlay}
            disabled={!textToRead}
            aria-label={`${t('audio.play', 'Play audio guidance for')} ${stepTitle || 'this step'}`}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          >
            <span aria-hidden="true">▶️</span>
            <span>{t('audio.play', 'Play Guidance')}</span>
          </button>
        )}

        {playbackState === 'playing' && (
          <button
            type="button"
            className="btn btn-sm btn-saffron"
            onClick={handlePause}
            aria-label={t('audio.pause', 'Pause audio guidance')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          >
            <span aria-hidden="true">⏸️</span>
            <span>{t('audio.pause', 'Pause')}</span>
          </button>
        )}

        {playbackState === 'paused' && (
          <button
            type="button"
            className="btn btn-sm btn-saffron"
            onClick={handleResume}
            aria-label={t('audio.resume', 'Resume audio guidance')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          >
            <span aria-hidden="true">▶️</span>
            <span>{t('audio.resume', 'Resume')}</span>
          </button>
        )}

        {/* Replay Button */}
        {playbackState !== 'idle' && (
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={handleReplay}
            aria-label={t('audio.replay', 'Replay from start')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          >
            <span aria-hidden="true">🔄</span>
            <span>{t('audio.replay', 'Replay')}</span>
          </button>
        )}

        {/* Stop Button */}
        {playbackState !== 'idle' && (
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={handleStop}
            aria-label={t('audio.stop', 'Stop audio guidance')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          >
            <span aria-hidden="true">⏹️</span>
            <span>{t('audio.stop', 'Stop')}</span>
          </button>
        )}

        {/* Voice Input (Speech-to-Text) Button */}
        {onApplyTranscript && (
          <button
            type="button"
            className={`btn btn-sm ${isListening ? 'btn-saffron' : 'btn-secondary'}`}
            onClick={handleStartListening}
            disabled={isListening}
            aria-label={t('form.voiceInput', 'Voice Input')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', marginLeft: 'auto' }}
          >
            <span aria-hidden="true">🎙️</span>
            <span>{isListening ? t('form.listening', 'Listening...') : t('form.voiceInput', 'Speak Answer')}</span>
          </button>
        )}
      </div>

      {/* Voice notice if browser voice is missing */}
      {voiceNotice && (
        <div
          style={{
            fontSize: '0.75rem',
            color: '#B45309',
            backgroundColor: '#FEF3C7',
            padding: '4px 8px',
            borderRadius: '4px',
            marginTop: '8px',
            border: '1px solid #FCD34D',
          }}
          role="status"
        >
          ℹ️ {voiceNotice}
        </div>
      )}

      {/* Voice error feedback */}
      {voiceError && (
        <div
          style={{
            fontSize: '0.75rem',
            color: '#B91C1C',
            backgroundColor: '#FEE2E2',
            padding: '4px 8px',
            borderRadius: '4px',
            marginTop: '8px',
            border: '1px solid #FCA5A5',
          }}
          role="alert"
        >
          ⚠️ {voiceError}
        </div>
      )}

      {/* Voice Transcription Review Box */}
      {(transcriptDraft || isListening) && onApplyTranscript && (
        <div
          style={{
            marginTop: '10px',
            padding: '10px',
            backgroundColor: 'var(--color-teal-light)',
            border: '1px solid var(--color-teal)',
            borderRadius: 'var(--border-radius)',
          }}
        >
          <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-teal-dark)', marginBottom: '4px' }}>
            {isListening ? t('form.speakNow', 'Listening... speak clearly into microphone') : t('form.applySpeech', 'Review recognized text before applying')}:
          </div>
          <input
            type="text"
            className="form-control"
            style={{ marginBottom: '8px', backgroundColor: '#FFFFFF' }}
            value={transcriptDraft}
            onChange={(e) => setTranscriptDraft(e.target.value)}
            placeholder="Transcribed voice text..."
          />
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={handleApply}
              disabled={!transcriptDraft.trim()}
            >
              ✓ {t('form.applyToField', 'Apply to Field')}
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => setTranscriptDraft('')}
            >
              ✕ {t('form.discard', 'Discard')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
