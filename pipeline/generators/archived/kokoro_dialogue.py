#!/usr/bin/env python3
"""
AI Podcast Generator (Kokoro TTS Version)

Uses local Kokoro-82M TTS running via Docker with ROCm GPU acceleration
for zero-cost, high-quality multi-speaker podcast generation.

Workflow:
1. Takes a human-recorded audio prompt
2. Sends to Gemini to transcribe and generate a diarized podcast dialogue script
3. Generates multi-speaker audio using Kokoro TTS (Docker)
4. Concatenates: intro jingle + user prompt + AI dialogue + outro jingle

Requires:
    - Docker with kokoro-tts-rocm:latest image
    - pip install google-genai python-dotenv

Environment:
    GEMINI_API_KEY - Your Gemini API key (can be in .env file)
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configuration
PIPELINE_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = PIPELINE_ROOT.parent

# Queue-based directory structure
PROMPTS_TO_PROCESS_DIR = PIPELINE_ROOT / "prompts" / "to-process"
PROMPTS_DONE_DIR = PIPELINE_ROOT / "prompts" / "done"

# Output directories
OUTPUT_DIR = PIPELINE_ROOT / "output"
EPISODES_DIR = OUTPUT_DIR / "episodes"
JINGLES_DIR = PIPELINE_ROOT / "show-elements" / "mixed"

# Ensure output directories exist
EPISODES_DIR.mkdir(parents=True, exist_ok=True)
PROMPTS_DONE_DIR.mkdir(parents=True, exist_ok=True)

# Podcast configuration
PODCAST_NAME = "AI Conversations"
HOST_NAME = "Herman"      # Male host - curious, enthusiastic
CO_HOST_NAME = "Emma"     # Female co-host - knowledgeable, authoritative

# Kokoro TTS voice mapping
# Available voices in the ROCm Docker image:
#   American Female: af_bella, af_sarah
#   American Male:   am_adam, am_michael
#   British Female:  bf_emma
#   British Male:    bm_george, bm_lewis
SPEAKER_VOICE_MAP = {
    HOST_NAME: "am_adam",      # American male - warm, conversational
    CO_HOST_NAME: "bf_emma",   # British female - knowledgeable, authoritative
}

# Docker configuration
KOKORO_DOCKER_IMAGE = "kokoro-api-rocm:latest"
KOKORO_API_URL = "http://localhost:8880"

# Target episode length (~15 minutes at ~150 words per minute)
TARGET_WORD_COUNT = 2250  # ~15 minutes of dialogue

# System prompt for generating a diarized podcast dialogue script
PODCAST_SCRIPT_PROMPT = """You are a podcast script writer creating an engaging two-host dialogue for "{podcast_name}".

The user has recorded an audio prompt with a topic/question. Listen carefully and generate a comprehensive ~15 minute podcast episode script as a natural conversation between two AI hosts.

## The Hosts

- **{host_name}**: The curious, enthusiastic host who asks probing questions, shares relatable examples, and keeps the conversation accessible. Tends to think out loud and make connections to everyday life.

- **{co_host_name}**: The knowledgeable expert who provides deep insights, technical details, and authoritative explanations. Balances depth with clarity, using analogies to explain complex topics.

## Script Format

You MUST output the script in this exact diarized format - each line starting with the speaker name followed by a colon:

{host_name}: [dialogue]
{co_host_name}: [dialogue]
{host_name}: [dialogue]
...

## Episode Structure (~15 minutes total when spoken, approximately 2000-2500 words)

1. **Opening Hook** (30 seconds)
   - {host_name} introduces the topic with an intriguing angle
   - {co_host_name} adds a surprising fact or stakes

2. **Topic Introduction** (2 minutes)
   - Both hosts establish what they'll cover
   - Set up why listeners should care

3. **Core Discussion** (8-10 minutes)
   - Deep, substantive back-and-forth exploration of the topic
   - {co_host_name} provides expert insights with specific details
   - {host_name} asks clarifying questions, plays devil's advocate
   - Include specific examples, data, case studies, historical context
   - Natural tangents that add value
   - Multiple sub-topics within the main theme

4. **Practical Takeaways** (2-3 minutes)
   - What can listeners actually do with this information?
   - Real-world applications
   - Different perspectives on implementation

5. **Closing Thoughts** (1-2 minutes)
   - Future implications and predictions
   - What questions remain unanswered
   - Tease potential follow-up topics
   - Sign off

## Dialogue Guidelines

- **Natural speech patterns**: Include occasional filler words ("you know", "I mean", "right"), brief pauses indicated by "..." or "hmm", and natural flow
- **Reactions**: "That's fascinating!", "Wait, really?", "Hmm, that's a good point", "Okay so let me make sure I understand..."
- **Length variety**: Mix short reactive lines (1-2 sentences) with longer explanatory passages (3-5 sentences)
- **Chemistry**: The hosts should build on each other's points, occasionally express genuine surprise, and respectfully challenge assumptions
- **Engagement hooks**: "Here's the thing...", "What most people don't realize...", "This is where it gets interesting...", "But here's what blew my mind..."

## Content Requirements

- **Depth**: Provide substantive, educational content - go beyond surface-level. This should feel like a real podcast people learn from.
- **Specificity**: Use real numbers, names, dates, examples when possible
- **Accuracy**: Be precise on technical topics. Mark speculation clearly with phrases like "from what we know" or "current research suggests"
- **Accessibility**: Explain jargon when used, use analogies for complex concepts
- **Length**: AIM FOR 2000-2500 WORDS TOTAL. This is critical for reaching ~15 minutes.

## Output

Generate ONLY the diarized script. No stage directions, no [brackets], no metadata - just speaker names and their dialogue.

Example format:
{host_name}: Welcome back to {podcast_name}! Today we're diving into something that's been all over the headlines lately, and honestly, I've been really curious to dig into this one.
{co_host_name}: Yeah, and I think what's interesting is that most of the coverage has been missing the real story here. There's this whole dimension that people aren't talking about.
{host_name}: Okay, so break it down for us. What's actually going on beneath the surface?

Now generate the full ~15 minute episode script (2000-2500 words) based on the user's audio prompt.
""".format(podcast_name=PODCAST_NAME, host_name=HOST_NAME, co_host_name=CO_HOST_NAME)


def get_gemini_client() -> genai.Client:
    """Initialize Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Add it to .env file.")
    return genai.Client(api_key=api_key)


def transcribe_and_generate_script(client: genai.Client, audio_path: Path) -> str:
    """
    Send audio to Gemini, transcribe it, and generate a diarized podcast dialogue script.
    """
    print(f"Uploading audio file: {audio_path}")
    audio_file = client.files.upload(file=str(audio_path))
    print(f"Uploaded file: {audio_file.name}")

    print("Generating diarized podcast script (~15 min episode)...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[PODCAST_SCRIPT_PROMPT, audio_file],
        config=types.GenerateContentConfig(
            max_output_tokens=16000,
        )
    )

    script = response.text
    word_count = len(script.split())
    print(f"Generated script with ~{word_count} words")
    print(f"Script preview:\n{'-'*40}\n{script[:1500]}...\n{'-'*40}")

    return script


def parse_diarized_script(script: str) -> list[dict]:
    """Parse a diarized script into a list of speaker segments."""
    segments = []
    pattern = rf'^({HOST_NAME}|{CO_HOST_NAME}):\s*(.+?)(?=^(?:{HOST_NAME}|{CO_HOST_NAME}):|\Z)'
    matches = re.findall(pattern, script, re.MULTILINE | re.DOTALL)

    for speaker, text in matches:
        text = text.strip()
        if text:
            segments.append({
                'speaker': speaker,
                'text': text,
                'voice': SPEAKER_VOICE_MAP[speaker]
            })

    # Fallback: line-by-line parsing
    if not segments:
        print("Using fallback line-by-line parsing...")
        for line in script.split('\n'):
            line = line.strip()
            if line.startswith(f"{HOST_NAME}:"):
                text = line[len(f"{HOST_NAME}:"):].strip()
                if text:
                    segments.append({
                        'speaker': HOST_NAME,
                        'text': text,
                        'voice': SPEAKER_VOICE_MAP[HOST_NAME]
                    })
            elif line.startswith(f"{CO_HOST_NAME}:"):
                text = line[len(f"{CO_HOST_NAME}:"):].strip()
                if text:
                    segments.append({
                        'speaker': CO_HOST_NAME,
                        'text': text,
                        'voice': SPEAKER_VOICE_MAP[CO_HOST_NAME]
                    })

    print(f"Parsed {len(segments)} dialogue segments")
    return segments


def generate_segment_audio_kokoro(
    text: str,
    voice: str,
    output_path: Path,
    speed: float = 1.0,
) -> tuple[Path, float]:
    """
    Generate audio for a single segment using Kokoro TTS API.

    Returns:
        Tuple of (output_path, generation_time_seconds)
    """
    import requests

    output_path.parent.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    response = requests.post(
        f"{KOKORO_API_URL}/generate",
        json={"text": text, "voice": voice, "speed": speed},
        timeout=300,
    )

    generation_time = time.time() - start_time

    if response.status_code != 200:
        raise RuntimeError(f"Kokoro API error: {response.status_code} - {response.text}")

    # Save the audio
    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path, generation_time


def generate_multispeaker_audio_kokoro(
    segments: list[dict],
    output_dir: Path,
) -> tuple[list[Path], dict]:
    """
    Generate multi-speaker audio by generating each segment separately with Kokoro.

    Returns:
        Tuple of (list of segment audio paths, timing statistics dict)
    """
    segment_files = []
    total_gen_time = 0.0
    segment_times = []

    print(f"\nGenerating {len(segments)} dialogue segments with Kokoro TTS...")

    for i, segment in enumerate(segments):
        segment_path = output_dir / f"segment_{i:04d}_{segment['speaker']}.wav"
        print(f"  [{i+1}/{len(segments)}] {segment['speaker']}: {segment['text'][:50]}...")

        try:
            audio_path, gen_time = generate_segment_audio_kokoro(
                text=segment['text'],
                voice=segment['voice'],
                output_path=segment_path,
            )
            segment_files.append(audio_path)
            total_gen_time += gen_time
            segment_times.append({
                'segment': i,
                'speaker': segment['speaker'],
                'chars': len(segment['text']),
                'generation_time': gen_time,
            })
            print(f"      Generated in {gen_time:.1f}s")
        except Exception as e:
            print(f"      ERROR: {e}")
            raise

    stats = {
        'total_segments': len(segments),
        'total_generation_time': total_gen_time,
        'avg_time_per_segment': total_gen_time / len(segments) if segments else 0,
        'segment_times': segment_times,
    }

    return segment_files, stats


def concatenate_audio_files(audio_files: list[Path], output_path: Path) -> Path:
    """Concatenate multiple audio files using ffmpeg."""
    if not audio_files:
        raise ValueError("No audio files to concatenate")

    temp_dir = output_path.parent / "_temp_concat"
    temp_dir.mkdir(exist_ok=True)

    # Normalize all files to same format
    normalized_files = []
    for i, audio_file in enumerate(audio_files):
        normalized_path = temp_dir / f"norm_{i:04d}.wav"
        cmd = [
            "ffmpeg", "-y", "-i", str(audio_file),
            "-ar", "24000", "-ac", "1", "-sample_fmt", "s16",
            str(normalized_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        normalized_files.append(normalized_path)

    # Create file list
    filelist_path = temp_dir / "filelist.txt"
    with open(filelist_path, "w") as f:
        for nf in normalized_files:
            f.write(f"file '{nf}'\n")

    # Concatenate
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(filelist_path),
        "-c:a", "pcm_s16le",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    # Cleanup
    shutil.rmtree(temp_dir)

    return output_path


def concatenate_episode(
    dialogue_audio: Path,
    output_path: Path,
    user_prompt_audio: Path = None,
    intro_jingle: Path = None,
    outro_jingle: Path = None,
) -> Path:
    """Concatenate all episode audio: intro + user prompt + dialogue + outro."""
    print("Assembling final episode...")

    audio_files = []
    if intro_jingle and intro_jingle.exists():
        audio_files.append(intro_jingle)
    if user_prompt_audio and user_prompt_audio.exists():
        audio_files.append(user_prompt_audio)
    audio_files.append(dialogue_audio)
    if outro_jingle and outro_jingle.exists():
        audio_files.append(outro_jingle)

    if len(audio_files) == 1:
        # No jingles, just convert to MP3
        cmd = [
            "ffmpeg", "-y", "-i", str(dialogue_audio),
            "-c:a", "libmp3lame", "-b:a", "128k",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    temp_dir = output_path.parent / "_temp_episode"
    temp_dir.mkdir(exist_ok=True)

    normalized_files = []
    for i, audio_file in enumerate(audio_files):
        normalized_path = temp_dir / f"temp_normalized_{i}.wav"
        cmd = [
            "ffmpeg", "-y", "-i", str(audio_file),
            "-ar", "44100", "-ac", "1", "-sample_fmt", "s16",
            str(normalized_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        normalized_files.append(normalized_path)

    filelist_path = temp_dir / "filelist.txt"
    with open(filelist_path, "w") as f:
        for nf in normalized_files:
            f.write(f"file '{nf}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(filelist_path),
        "-c:a", "libmp3lame", "-b:a", "128k",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    shutil.rmtree(temp_dir)
    print(f"Final episode saved to: {output_path}")
    return output_path


def generate_episode_metadata(client: genai.Client, script: str) -> dict:
    """Generate episode title and description from the script."""
    print("Generating episode metadata...")

    metadata_prompt = """Based on this podcast script, generate:

1. A catchy, engaging episode title (max 60 characters)
2. A compelling episode description for podcast platforms (2-3 sentences, ~150-200 words)

Output format (use exactly these labels):
TITLE: [your title here]
DESCRIPTION: [your description here]

Script:
""" + script[:8000]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=metadata_prompt,
    )

    result_text = response.text
    title = ""
    description = ""

    if "TITLE:" in result_text:
        title_start = result_text.index("TITLE:") + len("TITLE:")
        title_end = result_text.index("DESCRIPTION:") if "DESCRIPTION:" in result_text else len(result_text)
        title = result_text[title_start:title_end].strip()

    if "DESCRIPTION:" in result_text:
        desc_start = result_text.index("DESCRIPTION:") + len("DESCRIPTION:")
        description = result_text[desc_start:].strip()

    return {'title': title, 'description': description}


def save_metadata_files(metadata: dict, episode_dir: Path):
    """Save metadata in both JSON and plain text formats."""
    json_path = episode_dir / "metadata.json"
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=2)

    txt_path = episode_dir / "metadata.txt"
    txt_content = f"""EPISODE METADATA
================

Title:
{metadata.get('title', 'N/A')}

Description:
{metadata.get('description', 'N/A')}

---

Episode Name: {metadata.get('episode_name', 'N/A')}
Generated: {metadata.get('generated_at', 'N/A')}
TTS Engine: {metadata.get('tts_engine', 'N/A')}
Dialogue Segments: {metadata.get('segments_count', 'N/A')}

Voices:
"""
    voices = metadata.get('voices', {})
    for host, voice in voices.items():
        txt_content += f"  - {host}: {voice}\n"

    txt_content += f"""
Generation Stats:
  Total TTS Time: {metadata.get('total_tts_time', 'N/A'):.1f}s
  Avg per Segment: {metadata.get('avg_segment_time', 'N/A'):.1f}s
  Audio Duration: {metadata.get('audio_duration', 'N/A'):.1f}s
  Real-time Factor: {metadata.get('realtime_factor', 'N/A'):.2f}x

Files:
  - Audio: {Path(metadata.get('audio_file', '')).name}
  - Script: {Path(metadata.get('script_file', '')).name}
"""

    with open(txt_path, "w") as f:
        f.write(txt_content)

    print(f"Metadata saved to: {json_path}")


def get_audio_duration(audio_path: Path) -> float:
    """Get duration of audio file in seconds."""
    result = subprocess.run(
        ["ffprobe", "-i", str(audio_path), "-show_entries", "format=duration",
         "-v", "quiet", "-of", "csv=p=0"],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def generate_podcast_episode(
    prompt_audio_path: Path,
    episode_name: str = None,
    max_segments: int = None,  # For testing: limit number of segments
) -> Path:
    """
    Generate a complete podcast episode from a user's audio prompt using Kokoro TTS.
    """
    if episode_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        episode_name = f"kokoro_episode_{timestamp}"

    episode_dir = EPISODES_DIR / episode_name
    episode_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Generating podcast episode: {episode_name}")
    print(f"Using Kokoro TTS (Local Docker with ROCm)")
    print(f"Hosts: {HOST_NAME} ({SPEAKER_VOICE_MAP[HOST_NAME]}) & {CO_HOST_NAME} ({SPEAKER_VOICE_MAP[CO_HOST_NAME]})")
    print(f"Output folder: {episode_dir}")
    print(f"{'='*60}\n")

    client = get_gemini_client()

    # Step 1: Generate script
    print("Step 1: Generating diarized dialogue script with Gemini...")
    script = transcribe_and_generate_script(client, prompt_audio_path)

    script_path = episode_dir / "script.txt"
    with open(script_path, "w") as f:
        f.write(script)
    print(f"Script saved to: {script_path}")

    # Step 2: Parse script
    print("\nStep 2: Parsing diarized script...")
    segments = parse_diarized_script(script)

    if not segments:
        raise ValueError("Failed to parse any dialogue segments from the script")

    # Optionally limit segments for testing
    if max_segments:
        print(f"Testing mode: limiting to first {max_segments} segments")
        segments = segments[:max_segments]

    segments_path = episode_dir / "segments.json"
    with open(segments_path, "w") as f:
        json.dump(segments, f, indent=2)

    # Step 3: Generate audio with Kokoro
    print(f"\nStep 3: Generating multi-speaker audio with Kokoro TTS...")
    segment_dir = episode_dir / "_segments"
    segment_dir.mkdir(exist_ok=True)

    segment_files, tts_stats = generate_multispeaker_audio_kokoro(segments, segment_dir)

    # Step 4: Concatenate segments
    print("\nStep 4: Concatenating dialogue segments...")
    dialogue_audio_path = episode_dir / "dialogue.wav"
    concatenate_audio_files(segment_files, dialogue_audio_path)

    # Get audio duration
    audio_duration = get_audio_duration(dialogue_audio_path)
    realtime_factor = tts_stats['total_generation_time'] / audio_duration if audio_duration > 0 else 0

    # Step 5: Assemble final episode
    print("\nStep 5: Assembling final episode...")
    episode_path = episode_dir / f"{episode_name}.mp3"
    intro_jingle = JINGLES_DIR / "mixed-intro.mp3"
    outro_jingle = JINGLES_DIR / "mixed-outro.mp3"

    concatenate_episode(
        dialogue_audio=dialogue_audio_path,
        output_path=episode_path,
        user_prompt_audio=prompt_audio_path,
        intro_jingle=intro_jingle if intro_jingle.exists() else None,
        outro_jingle=outro_jingle if outro_jingle.exists() else None,
    )

    # Cleanup segment files
    shutil.rmtree(segment_dir)
    if dialogue_audio_path.exists():
        dialogue_audio_path.unlink()

    # Step 6: Generate metadata
    print("\nStep 6: Generating episode metadata...")
    metadata = generate_episode_metadata(client, script)

    full_metadata = {
        'title': metadata['title'],
        'description': metadata['description'],
        'episode_name': episode_name,
        'audio_file': str(episode_path),
        'script_file': str(script_path),
        'segments_count': len(segments),
        'tts_engine': 'kokoro-82m-rocm',
        'docker_image': KOKORO_DOCKER_IMAGE,
        'voices': {HOST_NAME: SPEAKER_VOICE_MAP[HOST_NAME], CO_HOST_NAME: SPEAKER_VOICE_MAP[CO_HOST_NAME]},
        'generated_at': datetime.now().isoformat(),
        'total_tts_time': tts_stats['total_generation_time'],
        'avg_segment_time': tts_stats['avg_time_per_segment'],
        'audio_duration': audio_duration,
        'realtime_factor': realtime_factor,
    }

    save_metadata_files(full_metadata, episode_dir)

    print(f"\n{'='*60}")
    print(f"Episode generated successfully!")
    print(f"{'='*60}")
    print(f"\nTITLE:")
    print(f"  {metadata['title']}")
    print(f"\nDESCRIPTION:")
    print(f"  {metadata['description']}")
    print(f"\nGENERATION STATS:")
    print(f"  Total TTS Time: {tts_stats['total_generation_time']:.1f}s")
    print(f"  Audio Duration: {audio_duration:.1f}s")
    print(f"  Real-time Factor: {realtime_factor:.2f}x (lower is faster)")
    print(f"\nEPISODE FOLDER: {episode_dir}")
    print(f"  - {episode_path.name}")
    print(f"  - script.txt")
    print(f"  - segments.json")
    print(f"  - metadata.json")
    print(f"  ({len(segments)} dialogue turns)")
    print(f"{'='*60}\n")

    return episode_path


def process_queue():
    """Process all audio files in the to-process queue."""
    audio_extensions = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}

    to_process = [
        f for f in PROMPTS_TO_PROCESS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]

    if not to_process:
        print("No audio files found in the to-process queue.")
        print(f"Add audio files to: {PROMPTS_TO_PROCESS_DIR}")
        return

    print(f"Found {len(to_process)} file(s) to process:")
    for f in to_process:
        print(f"  - {f.name}")
    print()

    for prompt_path in to_process:
        try:
            episode_name = prompt_path.stem
            episode_path = generate_podcast_episode(prompt_path, episode_name)

            done_path = PROMPTS_DONE_DIR / prompt_path.name
            prompt_path.rename(done_path)
            print(f"Moved {prompt_path.name} to done folder")

        except Exception as e:
            print(f"Error processing {prompt_path.name}: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate podcast episode with Kokoro TTS")
    parser.add_argument("prompt", nargs="?", help="Path to audio prompt file")
    parser.add_argument("--max-segments", "-m", type=int, help="Limit segments for testing")
    parser.add_argument("--name", "-n", help="Episode name")

    args = parser.parse_args()

    if args.prompt:
        prompt_path = Path(args.prompt)
        if not prompt_path.exists():
            print(f"Error: Audio file not found: {prompt_path}")
            sys.exit(1)
        episode_path = generate_podcast_episode(
            prompt_path,
            episode_name=args.name,
            max_segments=args.max_segments
        )
        print(f"Done! Episode saved to: {episode_path}")
    else:
        process_queue()


if __name__ == "__main__":
    main()
