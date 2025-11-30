# Kokoro TTS Docker Setup (ROCm)

Local text-to-speech using [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) with AMD GPU acceleration via ROCm.

## Overview

- **Model**: Kokoro-82M (82M parameters, Apache 2.0 license)
- **Quality**: Comparable to larger models, very natural sounding
- **Cost**: Zero (runs locally)
- **Speed**: ~57s startup per invocation (includes model loading), actual TTS generation is fast
- **GPU**: AMD Radeon RX 7700 XT / 7800 XT via ROCm

## Docker Image

**Image name**: `kokoro-tts-rocm:latest`
**Size**: ~29.8 GB

### Available Voices

The ROCm Docker image includes these voices:

| Voice Code | Description |
|------------|-------------|
| `af_bella` | American Female |
| `af_sarah` | American Female |
| `am_adam` | American Male |
| `am_michael` | American Male |
| `bf_emma` | British Female |
| `bm_george` | British Male |
| `bm_lewis` | British Male |

Full Kokoro model supports 54 voices across 8 languages - see [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).

## Usage

### Basic CLI Usage

```bash
docker run --rm \
  --device=/dev/kfd --device=/dev/dri \
  --group-add video --group-add render \
  --security-opt seccomp=unconfined \
  -e HSA_OVERRIDE_GFX_VERSION=11.0.1 \
  --shm-size=8gb \
  -v /path/to/output:/output \
  kokoro-tts-rocm:latest \
  --voice am_adam \
  --output /output/speech.wav \
  "Your text here"
```

### CLI Options

```
usage: tts.py [-h] [-f FILE] [-o OUTPUT] [-v VOICE] [-s SPEED] [--list-voices] [text]

Kokoro-82M Text-to-Speech

positional arguments:
  text                  Text to synthesize (or use --file)

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Input text file
  -o OUTPUT, --output OUTPUT
                        Output audio file (default: /output/output.wav)
  -v VOICE, --voice VOICE
                        Voice: af_bella, af_sarah, am_adam, am_michael, bf_emma, bm_george, bm_lewis
  -s SPEED, --speed SPEED
                        Speech speed (default: 1.0)
  --list-voices         List available voices
```

### List Available Voices

```bash
docker run --rm kokoro-tts-rocm:latest --list-voices
```

## Performance Notes

### Timing (AMD RX 7700 XT)

- **Cold start**: ~57 seconds (includes downloading spacy model, loading Kokoro weights)
- **TTS generation**: Very fast once model is loaded
- **Real-time factor**: Approximately 3-4x (i.e., 1 minute of audio takes ~15-20 seconds to generate after startup)

### Current Limitations

1. **No persistent container**: Each invocation starts fresh, requiring model reload
2. **Spacy download**: Downloads `en_core_web_sm` on each run (could be cached in volume)
3. **MIOpen warnings**: Workspace warnings are benign, TTS still works

### Optimization Ideas

1. Run as a persistent service/API instead of CLI invocations
2. Consider using [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) for API-based access
3. Pre-cache spacy models in the Docker image
4. Use Docker volumes for model caching

## Integration with Podcast Generator

The Kokoro TTS is integrated via `pipeline/generators/kokoro_dialogue.py`:

```bash
# Generate a full episode
python pipeline/generators/kokoro_dialogue.py path/to/prompt.mp3

# Test with limited segments (first 5 turns)
python pipeline/generators/kokoro_dialogue.py path/to/prompt.mp3 --max-segments 5
```

### Voice Mapping

The podcast generator uses:
- **Herman** (host): `am_adam` - American male, warm conversational
- **Emma** (co-host): `bf_emma` - British female, authoritative

## Comparison with Other TTS Options

| TTS Engine | Cost | Quality | Speed | Local |
|------------|------|---------|-------|-------|
| Kokoro (Docker) | Free | High | Medium | Yes |
| edge-tts | Free | Good | Fast | No (API) |
| Gemini TTS | ~$0.03/episode | Excellent | Fast | No |
| ElevenLabs | ~$0.30/episode | Excellent | Fast | No |
| Resemble AI | ~$0.50/episode | Excellent | Medium | No |

## Sources

- [Kokoro-82M on Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro GitHub](https://github.com/hexgrad/kokoro)
- [Kokoro-FastAPI (API wrapper)](https://github.com/remsky/Kokoro-FastAPI)
