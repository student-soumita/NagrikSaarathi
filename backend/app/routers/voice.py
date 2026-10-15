"""
Speech Services router for NagrikSaarathi API.

Features:
- POST /api/voice/transcribe: Audio-to-text transcription with language capability checks.
- POST /api/voice/speak: Text-to-speech synthesis with language capability checks.
- Enforces strict payload limits, ephemeral audio processing, and zero retention of raw recordings.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import Language
from backend.app.schemas.voice import SpeakRequest, SpeakResponse, TranscribeResponse
from backend.app.services.bhashini_adapter import BhashiniAdapter

router = APIRouter(prefix="/voice", tags=["Speech Services"])

_adapter = BhashiniAdapter()

ALLOWED_AUDIO_MIME_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/webm",
    "audio/ogg",
    "application/octet-stream",
}


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_speech(
    language_code: str = Form(..., description="Language code of the speech input"),
    file: UploadFile = File(..., description="Audio file to transcribe"),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Transcribe speech audio into text.
    Verifies that the requested language supports speech recognition before calling the provider.
    Never persists audio recordings to disk.
    """
    lang_code = language_code.lower()

    # 1. Verify language capability in database
    lang = db.execute(
        select(Language).where(Language.language_code == lang_code)
    ).scalar_one_or_none()

    if not lang:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{lang_code}' is not configured.",
        )

    if not lang.supports_speech_recognition:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Speech recognition is not currently available for '{lang.english_name}' ({lang_code}). "
                f"Please use the text interface or request assistance at the desk."
            ),
        )

    # 2. Validate MIME type
    content_type = file.content_type or "audio/wav"
    if content_type.lower() not in ALLOWED_AUDIO_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio format '{content_type}'. Supported formats: wav, mp3, ogg, webm.",
        )

    # 3. Read and validate payload size
    audio_bytes = await file.read()
    if len(audio_bytes) > settings.max_voice_payload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio payload exceeds maximum limit of {settings.max_voice_payload_bytes} bytes.",
        )

    # 4. Check provider configuration
    if not _adapter.is_configured:
        # Graceful handling when external speech provider is unconfigured in development/test
        return TranscribeResponse(
            language_code=lang_code,
            transcript="(Simulated ASR output: voice provider not configured in current environment)",
            provider="mock_ephemeral_asr",
            audio_processed_bytes=len(audio_bytes),
        )

    transcript = await _adapter.transcribe_audio(
        audio_bytes=audio_bytes,
        language_code=lang_code,
        mime_type=content_type,
    )

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Speech provider failed to process the audio stream or timed out.",
        )

    return TranscribeResponse(
        language_code=lang_code,
        transcript=transcript,
        provider="bhashini",
        audio_processed_bytes=len(audio_bytes),
    )


@router.post("/speak", response_model=SpeakResponse)
async def text_to_speech(
    payload: SpeakRequest,
    db: Session = Depends(get_db),
):
    """
    Synthesize speech audio from localized text.
    Verifies that the requested language supports text-to-speech before calling the provider.
    """
    lang_code = payload.language_code.lower()

    # 1. Verify language capability in database
    lang = db.execute(
        select(Language).where(Language.language_code == lang_code)
    ).scalar_one_or_none()

    if not lang:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{lang_code}' is not configured.",
        )

    if not lang.supports_text_to_speech:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Text-to-speech synthesis is not currently available for '{lang.english_name}' ({lang_code}). "
                f"Please read the provided text guidance."
            ),
        )

    # 2. Check provider configuration or local high-fidelity Indic neural TTS fallback (gTTS)
    if not _adapter.is_configured:
        GTTS_SUPPORTED_LANGS = {"bn", "hi", "ta", "te", "mr", "gu", "kn", "ml", "pa", "ur", "ne", "en"}
        if lang_code in GTTS_SUPPORTED_LANGS:
            try:
                import base64
                import io
                from gtts import gTTS

                tts = gTTS(text=payload.text.strip(), lang=lang_code, slow=False)
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

                return SpeakResponse(
                    language_code=lang_code,
                    audio_base64=audio_base64,
                    audio_format="audio/mp3",
                    provider="gtts_indic_tts",
                    disclaimer="Synthesized via on-demand Indic Speech Engine. Audio is processed in-memory and never retained.",
                )
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("Local TTS fallback failed: %s", exc)

        return SpeakResponse(
            language_code=lang_code,
            audio_base64=None,
            audio_format="audio/wav",
            provider="tts_unavailable",
            disclaimer=f"Text-to-speech voice is currently unavailable for {lang.english_name} ({lang_code}). Complete written guidance is displayed on screen.",
        )

    audio_base64 = await _adapter.synthesize_speech(
        text=payload.text,
        language_code=lang_code,
    )

    if audio_base64 is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Speech synthesis provider timed out or encountered an error.",
        )

    return SpeakResponse(
        language_code=lang_code,
        audio_base64=audio_base64,
        audio_format="audio/wav",
        provider="bhashini",
    )
