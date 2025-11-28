# AI Podcast Experiment 1125

An experiment in creating a semi-automated AI podcast workflow that combines human-recorded prompts with AI-generated responses, rendered as listenable audio episodes.

## The Idea

This is an iteration of an AI podcast concept that addresses several limitations with existing solutions:

### Why Not Notebook LM?
Notebook LM produces great content, but the podcast style tends toward a specific Americanized, California-esque host format that doesn't suit everyone's preferences.

### Why Not Pure TTS Workflows?
Previous N8N workflows (speech-to-text → LLM → text-to-speech) work but have issues:
- Quality TTS (like ElevenLabs) is expensive for regular 30-minute episodes
- Fully synthetic output lacks the human element

### The Solution
A hybrid approach:
1. **Human prompts** - Recorded audio prompts from the creator
2. **AI responses** - Multimodal AI (like Gemini) generates podcast-style responses
3. **Combined output** - Final episode includes: intro jingle → human prompt → pause → AI response → outro jingle

## Use Case

Perfect for:
- Converting detailed AI conversations into listenable content
- Consuming AI-generated explanations while multitasking (gym, walking, childcare)
- Cost-effective podcast creation for frequent episodes (daily/weekly)
- Open-sourcing interesting prompts and AI responses as audio content

## Planned Workflow

```
[Audio Prompt Recording]
        ↓
[Send to Multimodal AI (Gemini)]
        ↓
[Generate Podcast Response]
        ↓
[Assemble Episode]
   - Intro jingle
   - Human prompt audio
   - Transition/pause
   - AI response audio
   - Outro jingle
        ↓
[Render Normalized Audio File]
        ↓
[Manual Upload to Spotify/Transistor FM]
```

## Status

Early stage - workflow design and implementation in progress.

## Files

- `theidea.mp3` - Audio description of the project concept
- `audio-files/` - Directory for audio assets
