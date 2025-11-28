# TTS Options for AI Podcast

Evaluation of text-to-speech options for generating the AI host voice in podcast episodes.

---

## Recommended Options

### 1. Chatterbox (Resemble AI) - Cloud API via Replicate

**URL**: https://replicate.com/resemble-ai/chatterbox

**Pros:**
- High-quality, natural-sounding voices
- Voice cloning capability (could create "Herman" and "Corn" personas)
- Runs on Replicate infrastructure (no local GPU needed)
- Fast generation times

**Cons:**
- Per-use API cost
- Requires internet connection
- Dependent on third-party service

**Cost Estimate:**
- Replicate pricing is per-second of compute time
- Chatterbox typically runs ~$0.0023/second on Replicate
- A 5-minute AI response (~300 words at podcast pace) might take 30-60 seconds to generate
- **Estimated cost per episode: $0.07 - $0.15** for the TTS portion
- Monthly (30 episodes): ~$2-5

**Voice Cloning Potential:**
- Could create distinct AI host voices ("Herman" and "Corn")
- Requires sample audio for voice cloning
- Adds character/branding to the podcast

---

### 2. Coqui XTTS v2 - Local Inference

**Pros:**
- Completely free (no API costs)
- Very natural-sounding output
- Voice cloning from short audio samples
- Runs locally on your hardware
- ROCm support for AMD GPUs

**Cons:**
- Requires GPU setup with ROCm (can be finicky)
- Generation speed ~1x real-time (2 min audio = ~2 min generation)
- More complex setup than cloud APIs
- Project is somewhat unmaintained (Coqui shut down, community forks exist)

**Your Hardware:**
- RX 7700 XT with ROCm should handle this well
- 64GB RAM is more than sufficient
- Expect reasonable speeds once configured

**Setup Complexity:** Medium-High (ROCm configuration required)

---

## Not Recommended

### Piper TTS

**Status:** Rejected

**Why:**
- Voice quality not natural enough for podcast use
- Sounds robotic/synthetic compared to alternatives
- Fine for accessibility/screen readers, not for content creation

---

### Bark

**Status:** Not recommended for this use case

**Why:**
- Extremely slow generation (~10x slower than real-time)
- Would make episode production tediously slow
- Quality is good but not worth the time cost

---

### Tortoise TTS

**Status:** Not recommended for this use case

**Why:**
- Same issue as Bark - generation time is impractical
- Beautiful output but not viable for frequent episode production

---

## Cloud Alternatives (For Reference)

### ElevenLabs
- Premium quality, industry standard
- $5/month for 30,000 characters (~30 min audio)
- Best quality but highest cost

### OpenAI TTS
- Good quality, moderate cost
- $15 per 1M characters
- ~$0.01-0.02 per episode

### edge-tts (Microsoft)
- Free
- Quality is decent but not as natural as Chatterbox/XTTS
- Good fallback option

---

## Recommendation

**Primary:** Chatterbox via Replicate
- Best balance of quality, ease of use, and cost
- Voice cloning enables the "Herman and Corn" concept
- ~$2-5/month for daily episodes is very reasonable

**Fallback:** Coqui XTTS locally
- Zero ongoing cost
- Good for batch processing or if API costs become a concern
- Worth setting up as backup option

---

## Next Steps

1. Test Chatterbox on Replicate with a sample script
2. Experiment with voice cloning for Herman/Corn personas
3. Compare output quality to make final decision
4. If going local, set up Coqui XTTS with ROCm
