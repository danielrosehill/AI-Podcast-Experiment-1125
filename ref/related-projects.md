# Related Projects - AI Podcast Generation

A collection of interesting open-source projects for AI-powered podcast generation and automation.

---

## NotebookLM-Style Generators

### podcastfy
**URL**: https://github.com/souzatharsis/podcastfy

Multi-modal content to podcast converter. Likely the most mature option in this space.

---

### PageLM
**URL**: https://github.com/CaviraOSS/PageLM

NotebookLM alternative - converts pages/documents into podcast-style audio.

---

### notebooklm-podcast-automator
**URL**: https://github.com/upamune/notebooklm-podcast-automator

Automation layer specifically for NotebookLM podcast generation workflow.

---

## Multi-Host / Conversational Podcasts

### mulmocast-cli
**URL**: https://github.com/receptron/mulmocast-cli

CLI tool for generating multi-modal podcasts. Worth investigating for multi-voice support.

---

### Twocast
**URL**: https://github.com/panyanyany/Twocast

Two-host podcast generator - specifically designed for conversational format between AI hosts.

---

### neuralnoise
**URL**: https://github.com/leopiney/neuralnoise

Neural network-based podcast generation with focus on natural-sounding output.

---

## General AI Podcast Generators

### ai-podcast-generator (aastroza)
**URL**: https://github.com/aastroza/ai-podcast-generator

General-purpose AI podcast generation tool.

---

### podcast-llm
**URL**: https://github.com/evandempsey/podcast-llm

LLM-powered podcast content generation.

---

### AI-Podcast-Generator (NeuralFalconYT)
**URL**: https://github.com/NeuralFalconYT/AI-Podcast-Generator

Another AI podcast generator - check for unique features or approaches.

---

## TTS / Audio Specific

### gemini-2-tts
**URL**: https://github.com/agituts/gemini-2-tts

Gemini 2 text-to-speech integration - directly relevant since we're using Gemini for the AI processing pipeline.

---

## Evaluation Notes

**To investigate:**
- Which projects support custom voice cloning?
- Which have the cleanest architecture to borrow from?
- Any N8N/automation integrations?
- Audio quality and normalization approaches used

**Priority to review:**
1. `podcastfy` - appears most mature
2. `Twocast` - multi-host is relevant for Herman/Corn concept
3. `gemini-2-tts` - direct Gemini integration
4. `mulmocast-cli` - CLI approach matches our workflow
