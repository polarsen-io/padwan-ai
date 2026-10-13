---
icon: lucide/audio-waveform
---

# Gradium Client

[Gradium](https://gradium.ai) is a speech provider: low-latency text-to-speech and speech-to-text in English, French,
German, Spanish and Portuguese. `GradiumClient` is standalone like the [ElevenLabs client](elevenlabs.md): it is not an
`LLMClientBase` subclass and `LLMClient` does not route to it. It covers the REST endpoints; WebSocket streaming is not
implemented yet.

## Configuration

Set `GRADIUM_API_KEY` in your environment or pass `api_key=` explicitly. `base_url` defaults to
`https://api.gradium.ai/api/`; use `https://eu.api.gradium.ai/api/` or `https://us.api.gradium.ai/api/` for data
residency.

Requests retry up to three times on connection errors, HTTP 429, 502, 503 and 504. API errors, including errors streamed
after a successful response started, raise `LLMError` with `provider="gradium"`. Bad arguments (no voice, unknown audio
extension) raise `ValueError`.

## Text-to-speech

```python
from pathlib import Path

from padwan_ai import GradiumClient

async with GradiumClient(voice_id="YTpq7expH9539ERJ") as client:
    speech = await client.generate_speech(
        "Hello from Padwan.",
        output_format="wav",  # or pcm, opus, pcm_24000, ulaw_8000, ...
        config={"temp": 0.3, "padding_bonus": -1},  # lower padding_bonus speaks faster
    )
    Path("hello.wav").write_bytes(speech.audio)
```

`generate_speech` returns a `GradiumSpeech` with the raw `audio` bytes and their `mime_type`. `model="default"` selects
the latest production model. Voice IDs come from the
[voice library](https://docs.gradium.ai/guides/voices/flagship-voices) or your custom voices.

## Speech-to-text

```python
async with GradiumClient() as client:
    result = await client.transcribe(
        "meeting.wav",  # path or raw bytes: wav, raw pcm (24 kHz s16le mono) or Ogg Opus
        language="fr",  # default "any" auto-detects
        config={"keywords": {"words": ["Padwan", "Polarsen"], "boost": 3}},
    )
    print(result["text"])
    for segment in result["segments"]:
        print(segment["start"], segment["end"], segment["text"])
```

The input format is inferred from the file extension (`.wav`, `.pcm`/`.raw`, `.ogg`/`.opus`) and defaults to wav for
raw bytes; pass `input_format=` to override. MP3 is not accepted by the API. `transcribe` returns a
`GradiumTranscription` with the joined `text` and timed `segments` (`end` is `None` for a trailing open segment). See
[transcription settings](https://docs.gradium.ai/guides/transcription-settings) for `config` options.
