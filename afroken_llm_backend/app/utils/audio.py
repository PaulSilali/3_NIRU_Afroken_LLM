"""
Audio processing utilities for Whisper ASR and Coqui TTS.

This module provides:
- Speech-to-text using OpenAI Whisper
- Text-to-speech using Coqui TTS
"""

import os
import io
from pathlib import Path
from typing import Optional, BinaryIO
import tempfile

# Lazy imports to avoid errors if libraries not installed
_whisper_model = None
_tts_model = None
_tts_speaker = None


def _load_whisper_model():
    """Lazy load Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            # Load base model (smaller, faster - can upgrade to medium/large for better quality)
            _whisper_model = whisper.load_model("base")
        except ImportError:
            raise ImportError(
                "Whisper not installed. Install with: pip install openai-whisper"
            )
    return _whisper_model


def _load_tts_model(language: str = "sw"):
    """Lazy load Coqui TTS model."""
    global _tts_model, _tts_speaker
    if _tts_model is None:
        try:
            from TTS.api import TTS
            # Use multilingual model that supports Swahili and English
            # Coqui TTS has models for various languages
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            _tts_model = TTS(model_name)
            # Default speaker (can be customized)
            _tts_speaker = "default"
        except ImportError:
            raise ImportError(
                "Coqui TTS not installed. Install with: pip install TTS"
            )
    return _tts_model, _tts_speaker


async def transcribe_audio(
    audio_file: BinaryIO, 
    language: Optional[str] = None
) -> dict:
    """
    Transcribe audio file to text using Whisper ASR.
    
    Args:
        audio_file: Binary file-like object containing audio data
        language: Optional language code (e.g., "sw", "en"). Auto-detected if None.
    
    Returns:
        dict with keys:
            - text: Transcribed text
            - language: Detected language code
            - segments: List of transcription segments with timestamps
    """
    model = _load_whisper_model()
    
    # Save audio to temporary file (Whisper expects file path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        audio_file.seek(0)
        tmp_file.write(audio_file.read())
    
    try:
        # Transcribe with language detection if not specified
        if language:
            result = model.transcribe(tmp_path, language=language)
        else:
            result = model.transcribe(tmp_path)
        
        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip()
                }
                for seg in result.get("segments", [])
            ]
        }
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def synthesize_speech(
    text: str,
    language: str = "sw",
    output_format: str = "wav"
) -> bytes:
    """
    Convert text to speech using Coqui TTS.
    
    Args:
        text: Text to synthesize
        language: Language code ("sw" for Swahili, "en" for English)
        output_format: Audio format ("wav", "mp3")
    
    Returns:
        bytes: Audio file data
    """
    model, speaker = _load_tts_model(language)
    
    # Map language codes to TTS language codes
    lang_map = {
        "sw": "sw",  # Swahili
        "en": "en",  # English
    }
    tts_lang = lang_map.get(language, "en")
    
    # Generate speech to temporary file
    with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Synthesize speech
        model.tts_to_file(
            text=text,
            file_path=tmp_path,
            speaker=speaker,
            language=tts_lang
        )
        
        # Read generated audio file
        with open(tmp_path, "rb") as f:
            audio_data = f.read()
        
        return audio_data
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

