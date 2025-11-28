# The Idea - Audio Transcript

*Transcribed from theidea.mp3*

---

## Why This Repository Exists

I'm creating an audio file for this repository. Because it's an audio project, I thought I may as well stick with the audio setup here. I'm going to describe in audio format what the objective is with this project.

On GitHub, I use it as a first-entry notepad for experiments—over the last year, mostly AI stuff. A lot of my repositories have very similar names because they're different iterations of experiments I've tried. This is the latest iteration of my AI podcast idea, which I've actually got working before in a pretty reliable pipeline. It wasn't easy.

## The Problem with Existing Solutions

### Notebook LM
There are other implementations out there like Notebook LM. Notebook LM is fine—I think it's actually an amazing service. But I'm not too keen on the style of podcasts they generate: the very Americanized, California-esque host style. Nothing against Americans—my wife is American, and we'll talk about America in these introductions. But it's just not the production style I want to hear the podcast in.

### My Previous N8N Workflows
My original workflows were in N8N, where I would:
1. Record a prompt like this
2. Get that speech-to-text
3. Send that to the AI tool saying: "Here's your prompt, answer this in the style of a podcast. You are a podcast host called 'Daniel's Prompting' or something, respond to Daniel's prompt in the format of a host."
4. Finally, text-to-speech

The issue: you really need a good natural-sounding TTS, or it's horrible to listen to. So really, ElevenLabs. But the problem is ElevenLabs is very expensive. When you're doing 30-minute podcast episodes, you'll rack up significant API charges quite quickly.

## The Use Case

My idea is that during the day, I come up with detailed prompts and sometimes get really good, meaty outputs from AI tools. But it's not always the context I want to consume them in. I often say, "That was great, I'm going to get to this when I'm done with work." And frequently I don't, because I don't have a convenient way.

Sometimes I print out really good AI responses, but probably the most convenient way—especially as a new parent—would be audio. I can listen to a podcast:
- At the gym
- When walking
- When minding our newborn (put it on in the background)

It's a very versatile and enjoyable way to consume content. I really love listening to podcasts, so it's a format that makes a lot of sense for where I am in life and my preferences.

But I might want to do this a few times a day, so it has to be cost-effective. That's where finding TTS that was both not super expensive and good was tricky. But it worked.

## The Open Source Angle

One tweak I had in mind: I wanted to actually open-source the whole podcast. I come up with specific prompts about new subjects, I get good responses, and maybe someone else will want to listen to them.

I think for AI-generated podcasts, once the information is good and the voice is pleasant to listen to, I'm fully supportive of them. I think they're very powerful, in fact.

## The Key Insight: Use My Voice

It occurred to me—it's a pity if I'm recording my prompts as audio that I don't just use that in the podcast. So the podcast episode will:
1. Start with my prompt (my actual voice)
2. Cut to the TTS segment (AI response)

That's what I'm trying to do in this iteration: make it a bit more human. It really is me, a human being, coming up with prompts, and then we go over to the AI tools.

## The Planned Workflow

The reason I created this separate repository is because it's going to take some work and thinking to get this working. The workflow will involve:

1. **Record the prompts** (my voice)
2. **Send to a multimodal AI like Gemini** - That's my current thinking; it makes the most sense because it's the most powerful. I can do a transcription and say, "This is a prompt for a podcast."

Ideally, it would be totally one-shot: send that audio file to Gemini saying, "This is a prompt. Your task is to generate an audio podcast episode responding to the prompt."

3. **Assemble the final episode** - Even if that worked, I still need to get to the final step to make this really end-to-end:
   - Intro jingle
   - My prompt
   - A pause
   - The AI response
   - Outro jingle

   Then render that out to a normalized audio file.

4. **Optional: Auto-publish** - The only way it could be more end-to-end is if it were then published as an episode with title, cover art, and episode description. That totally could work. I looked into this—Transistor FM was the best option; they have an API for podcast publication.

But it's close enough for me if I'm doing this once or twice a day/week that it just generates the episode and I can put it up to Spotify myself.

---

That's the objective and what I'm trying to do in this repository.
