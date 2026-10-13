---
icon: lucide/audio-lines
---

# ElevenLabs Client

ElevenLabs is a speech provider: text-to-speech and speech-to-text, no chat models. `ElevenLabsClient` is standalone, like
the [TypeSafe client](typesafe.md): it is not an `LLMClientBase` subclass and `LLMClient` does not route to it.

## Configuration

Set `ELEVENLABS_API_KEY` in your environment or pass `api_key=` explicitly. `base_url` defaults to
`https://api.elevenlabs.io/v1/`; point it at a data-residency host (e.g. `https://api.eu.residency.elevenlabs.io/v1/`) if
your account needs one.

Requests retry up to three times on connection errors, HTTP 429 and 5xx, respecting `Retry-After`. Exhausted rate limits
raise `TooManyRequestsError`, an exhausted credit quota raises `QuotaExceededError`, and other API errors raise
`LLMError` with `provider="elevenlabs"`. Bad arguments (no voice, no or two audio sources) raise `ValueError`.

## Text-to-speech

```python
from pathlib import Path

from padwan_ai import ElevenLabsClient

async with ElevenLabsClient(voice_id="JBFqnCBsd6RMkjVDRZzb") as client:
    speech = await client.generate_speech(
        "Hello from Padwan.",
        model="eleven_v3",  # default: eleven_multilingual_v2
        output_format="mp3_44100_128",
        voice_settings={"stability": 0.4, "speed": 1.1},
    )
    Path("hello.mp3").write_bytes(speech.audio)
```

`generate_speech` returns an `ElevenLabsSpeech` with the raw `audio` bytes, its `mime_type` and the ElevenLabs
`request_id`. To keep prosody consistent across chunks of a long text, pass earlier IDs as `previous_request_ids` (or
the surrounding text as `previous_text` / `next_text`). Voice IDs come from your ElevenLabs voice library; pass one
per call or set a client default with `voice_id=`.

## Speech-to-text

```python
async with ElevenLabsClient() as client:
    result = await client.transcribe(
        "meeting.wav",  # path or raw bytes; or source_url="https://..."
        diarize=True,
        keyterms=["Padwan", "Polarsen"],
    )
    print(result["text"])
    for word in result["words"]:
        print(word["start"], word.get("speaker_id"), word["text"])
```

`transcribe` uses `scribe_v2` by default and returns the API's `ElevenLabsTranscription` (`text`, `language_code`,
`language_probability`, and `words` with timestamps, types and speaker IDs). See the
[speech-to-text reference](https://elevenlabs.io/docs/api-reference/speech-to-text/convert) for each option.

## Not covered yet

Streaming TTS, realtime (WebSocket) TTS and STT, voice management, sound effects and music are not implemented.
