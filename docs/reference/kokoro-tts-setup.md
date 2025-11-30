# Kokoro TTS Setup Guide (ROCm/AMD GPU)

This guide documents the setup and usage of Kokoro-82M TTS with AMD GPU acceleration via ROCm for the AI Podcast Experiment.

## Overview

| Property | Value |
|----------|-------|
| Model | [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) |
| License | Apache 2.0 |
| Parameters | 82 million |
| GPU | AMD Radeon RX 7700 XT / 7800 XT (gfx1101) |
| Acceleration | ROCm 6.x |
| Cost | Free (local inference) |

## Architecture

We use a two-layer Docker setup:

1. **Base Image** (`kokoro-tts-rocm:latest`) - CLI-based Kokoro with ROCm support
2. **API Image** (`kokoro-api-rocm:latest`) - FastAPI wrapper that keeps model loaded

The API approach eliminates the ~50s model load time per segment, reducing overall generation time by ~8x.

## Docker Images

### Base Image: `kokoro-tts-rocm:latest`

Pre-built image with Kokoro-82M and ROCm support. Size: ~29.8 GB

### API Image: `kokoro-api-rocm:latest`

FastAPI wrapper built on top of the base image. Adds:
- FastAPI + Uvicorn
- Pre-cached spacy `en_core_web_sm` model
- HTTP endpoints for TTS generation

**Build command:**
```bash
cd config/docker
docker build -f Dockerfile.kokoro-api -t kokoro-api-rocm:latest .
```

## Available Voices

| Voice Code | Language | Gender | Description |
|------------|----------|--------|-------------|
| `af_bella` | American English | Female | - |
| `af_sarah` | American English | Female | - |
| `am_adam` | American English | Male | Warm, conversational |
| `am_michael` | American English | Male | - |
| `bf_emma` | British English | Female | Authoritative |
| `bm_george` | British English | Male | - |
| `bm_lewis` | British English | Male | - |

The full Kokoro model supports 54 voices across 8 languages. See [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) for the complete list.

## Starting the API Server

```bash
docker run -d --name kokoro-api \
  --device=/dev/kfd --device=/dev/dri \
  --group-add video --group-add render \
  --security-opt seccomp=unconfined \
  -e HSA_OVERRIDE_GFX_VERSION=11.0.1 \
  --shm-size=8gb \
  -p 8880:8880 \
  kokoro-api-rocm:latest
```

**Startup time:** ~8-10 seconds for model loading

### Verifying the Server

```bash
# Health check
curl http://localhost:8880/health

# List voices
curl http://localhost:8880/voices
```

## API Endpoints

### `GET /health`

Returns server status and model load time.

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_load_time": 8.37
}
```

### `GET /voices`

Returns available voices.

```json
{
  "voices": {
    "af_bella": "American Female",
    "am_adam": "American Male",
    ...
  }
}
```

### `POST /generate`

Generate speech from text. Returns WAV audio.

**Request:**
```json
{
  "text": "Hello, welcome to the podcast!",
  "voice": "am_adam",
  "speed": 1.0
}
```

**Response:** Binary WAV audio with headers:
- `X-Generation-Time`: Time to generate (seconds)
- `X-Audio-Duration`: Audio length (seconds)

**Example:**
```bash
curl -X POST http://localhost:8880/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "am_adam"}' \
  -o output.wav
```

### `POST /generate_json`

Same as `/generate` but returns metadata instead of audio (useful for testing).

```json
{
  "success": true,
  "generation_time": 25.4,
  "audio_duration": 11.8,
  "realtime_factor": 2.15,
  "voice": "am_adam",
  "text_length": 150
}
```

## Performance Benchmarks

Tested on AMD Radeon RX 7700 XT with ROCm:

| Metric | CLI (per segment) | API (persistent) |
|--------|-------------------|------------------|
| Model load | ~50s each time | ~8s once |
| Generation (13s audio) | ~57s total | ~25-35s |
| Realtime factor | ~4.4x | ~2.0-2.7x |

### Full Episode Estimates (15 min, ~40 segments)

| Approach | Estimated Time |
|----------|----------------|
| CLI (spawning containers) | ~38 minutes |
| API (persistent server) | ~4-5 minutes |

## Integration with Podcast Generator

The `kokoro_dialogue.py` generator uses the API:

```python
KOKORO_API_URL = "http://localhost:8880"

# Generate audio via API
response = requests.post(
    f"{KOKORO_API_URL}/generate",
    json={"text": text, "voice": voice, "speed": speed},
    timeout=300,
)
```

### Usage

```bash
# Ensure API server is running first
docker start kokoro-api

# Generate episode
python pipeline/generators/kokoro_dialogue.py path/to/prompt.mp3

# Test with limited segments
python pipeline/generators/kokoro_dialogue.py path/to/prompt.mp3 --max-segments 5
```

## Stopping the Server

```bash
docker stop kokoro-api
docker rm kokoro-api
```

## Troubleshooting

### MIOpen Warnings

You may see warnings like:
```
MIOpen(HIP): Warning [IsEnoughWorkspace] Solver <GemmFwdRest>, workspace required: ...
```

These are benign and don't affect TTS quality.

### 422 Unprocessable Entity

Check for special characters in your text (smart quotes, etc.). The API expects plain text.

### Slow First Request

The first request after startup may be slower (~35s vs ~25s) due to GPU kernel compilation. Subsequent requests are faster.

### Container Won't Start

Ensure ROCm is properly configured:
```bash
# Check ROCm installation
rocm-smi

# Verify GPU access
docker run --rm --device=/dev/kfd --device=/dev/dri rocm/pytorch:latest rocm-smi
```

## File Locations

| File | Description |
|------|-------------|
| `config/docker/Dockerfile.kokoro-api` | API Docker build file |
| `config/docker/kokoro_api.py` | FastAPI server code |
| `config/docker/KOKORO-TTS.md` | Additional Docker notes |
| `pipeline/generators/kokoro_dialogue.py` | Podcast generator using Kokoro |

## Comparison with Other TTS Options

| Engine | Cost | Quality | Speed | Local | Notes |
|--------|------|---------|-------|-------|-------|
| **Kokoro (API)** | Free | High | ~2x RT | Yes | Best for cost-conscious production |
| edge-tts | Free | Good | Fast | No | Microsoft API, rate limits |
| Gemini TTS | ~$0.03/ep | Excellent | Fast | No | Best quality, cloud only |
| ElevenLabs | ~$0.30/ep | Excellent | Fast | No | Premium voices |
| Resemble AI | ~$0.50/ep | Excellent | Medium | No | Voice cloning |

## References

- [Kokoro-82M on Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro GitHub](https://github.com/hexgrad/kokoro)
- [ROCm Documentation](https://rocm.docs.amd.com/)
