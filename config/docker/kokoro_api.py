#!/usr/bin/env python3
"""
Kokoro TTS FastAPI Server (ROCm)

A simple persistent API wrapper for Kokoro-82M that keeps the model loaded in memory.
"""

import io
import os
import time
from typing import Optional

import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI(title="Kokoro TTS API (ROCm)", version="1.0.0")

# Global model instance
pipeline = None
model_load_time = None

AVAILABLE_VOICES = {
    "af_bella": "American Female",
    "af_sarah": "American Female",
    "am_adam": "American Male",
    "am_michael": "American Male",
    "bf_emma": "British Female",
    "bm_george": "British Male",
    "bm_lewis": "British Male",
}


class TTSRequest(BaseModel):
    text: str
    voice: str = "am_adam"
    speed: float = 1.0


class TTSResponse(BaseModel):
    success: bool
    message: str
    generation_time: Optional[float] = None
    audio_duration: Optional[float] = None


@app.on_event("startup")
async def load_model():
    """Load Kokoro model on startup."""
    global pipeline, model_load_time

    print("Loading Kokoro-82M model...")
    start = time.time()

    from kokoro import KPipeline
    pipeline = KPipeline(lang_code="a")  # 'a' for American/English

    model_load_time = time.time() - start
    print(f"Model loaded in {model_load_time:.1f}s")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": pipeline is not None,
        "model_load_time": model_load_time,
    }


@app.get("/voices")
async def list_voices():
    """List available voices."""
    return {"voices": AVAILABLE_VOICES}


@app.post("/generate", response_class=Response)
async def generate_speech(request: TTSRequest):
    """Generate speech from text. Returns WAV audio."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if request.voice not in AVAILABLE_VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice. Available: {list(AVAILABLE_VOICES.keys())}"
        )

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    start = time.time()

    try:
        # Generate audio
        generator = pipeline(request.text, voice=request.voice, speed=request.speed)

        audio_segments = []
        for gs, ps, audio in generator:
            audio_segments.append(audio)

        full_audio = np.concatenate(audio_segments)
        generation_time = time.time() - start

        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, full_audio, 24000, format='WAV')
        buffer.seek(0)

        audio_duration = len(full_audio) / 24000

        print(f"Generated {audio_duration:.1f}s audio in {generation_time:.1f}s "
              f"(voice={request.voice}, chars={len(request.text)})")

        return Response(
            content=buffer.read(),
            media_type="audio/wav",
            headers={
                "X-Generation-Time": str(generation_time),
                "X-Audio-Duration": str(audio_duration),
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_json")
async def generate_speech_json(request: TTSRequest):
    """Generate speech and return metadata (for testing)."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if request.voice not in AVAILABLE_VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice. Available: {list(AVAILABLE_VOICES.keys())}"
        )

    start = time.time()

    try:
        generator = pipeline(request.text, voice=request.voice, speed=request.speed)

        audio_segments = []
        for gs, ps, audio in generator:
            audio_segments.append(audio)

        full_audio = np.concatenate(audio_segments)
        generation_time = time.time() - start
        audio_duration = len(full_audio) / 24000

        return {
            "success": True,
            "generation_time": generation_time,
            "audio_duration": audio_duration,
            "realtime_factor": generation_time / audio_duration if audio_duration > 0 else 0,
            "voice": request.voice,
            "text_length": len(request.text),
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8880)
