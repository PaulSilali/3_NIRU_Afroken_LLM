"""
Audio processing endpoints for Whisper ASR and Coqui TTS.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.schemas import (
    AudioTranscribeRequest, AudioTranscribeResponse,
    AudioSynthesizeRequest
)
from app.utils.audio import transcribe_audio, synthesize_speech
import io

router = APIRouter()


@router.post("/transcribe", response_model=AudioTranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    language: str = None
):
    """
    Transcribe audio file to text using Whisper ASR.
    
    Accepts audio files (WAV, MP3, M4A, etc.) and returns transcribed text.
    """
    try:
        # Read audio file
        audio_data = await file.read()
        audio_file = io.BytesIO(audio_data)
        
        # Transcribe
        result = await transcribe_audio(audio_file, language)
        
        return AudioTranscribeResponse(
            text=result["text"],
            language=result["language"],
            segments=result["segments"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/synthesize")
async def synthesize(
    request: AudioSynthesizeRequest
):
    """
    Convert text to speech using Coqui TTS.
    
    Returns audio file (WAV or MP3) based on output_format.
    """
    try:
        # Synthesize speech
        audio_data = await synthesize_speech(
            text=request.text,
            language=request.language,
            output_format=request.output_format
        )
        
        # Determine content type
        content_type = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg"
        }.get(request.output_format, "audio/wav")
        
        return Response(
            content=audio_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="speech.{request.output_format}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

