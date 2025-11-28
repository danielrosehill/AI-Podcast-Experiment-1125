# Replicate TTS Models

Text-to-speech models available on Replicate for podcast generation.

**Collection**: https://replicate.com/collections/text-to-speech

---

## Models of Interest

### Chatterbox (Resemble AI)
**URL**: https://replicate.com/resemble-ai/chatterbox

- High-quality, natural voices
- Voice cloning capability
- Primary candidate for Herman/Corn personas

---

### MiniMax Speech 2.6 Turbo
**URL**: https://replicate.com/minimax/speech-2.6-turbo

- Fast generation ("turbo" variant)
- Worth testing for speed vs quality tradeoff

---

### Kokoro 82M
**URL**: https://replicate.com/jaaari/kokoro-82m

- Lightweight model (82M parameters)
- Likely very fast inference
- Check quality for podcast use

---

### XTTS v2 (lucataco)
**URL**: https://replicate.com/lucataco/xtts-v2

- Coqui XTTS v2 hosted on Replicate
- Voice cloning support
- Alternative to running XTTS locally
- Good option if local ROCm setup is problematic

---

## Comparison Notes

| Model | Voice Cloning | Speed | Quality | Cost |
|-------|---------------|-------|---------|------|
| Chatterbox | Yes | Fast | High | ~$0.002/sec |
| MiniMax Speech 2.6 Turbo | ? | Very Fast | ? | TBD |
| Kokoro 82M | ? | Very Fast | ? | TBD |
| XTTS v2 | Yes | Medium | High | TBD |

---

## Testing Plan

1. Generate same sample text with each model
2. Compare voice naturalness
3. Test voice cloning (Chatterbox, XTTS v2)
4. Calculate actual cost per episode
5. Measure generation speed
