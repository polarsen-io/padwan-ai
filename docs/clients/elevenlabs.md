---
icon: lucide/audio-lines
---

# ElevenLabs Client

!!! warning "Experimental"
    The ElevenLabs client is experimental: its interface and typed payloads may change between minor releases without a deprecation cycle.

ElevenLabs is an audio provider: text-to-speech, speech-to-text, speech-to-speech, sound effects and music, no chat
models. `ElevenLabsClient` is standalone, like
the [TypeSafe client](typesafe.md): it is not an `LLMClientBase` subclass and `LLMClient` does not route to it.

## Configuration

Set `ELEVENLABS_API_KEY` in your environment or pass `api_key=` explicitly. `base_url` defaults to
`https://api.elevenlabs.io/v1/`; point it at a data-residency host (e.g. `https://api.eu.residency.elevenlabs.io/v1/`) if
your account needs one.

Requests retry up to three times on connection errors, HTTP 429 and 5xx, respecting `Retry-After`. Exhausted rate limits
raise `TooManyRequestsError`, an exhausted credit quota raises `QuotaExceededError`, and other API errors raise
`LLMError` with `provider="elevenlabs"`. Bad arguments (no voice, no or two audio sources) raise `ValueError`.

The realtime clients need the `realtime` extra (niquests WebSocket support):

```bash
uv add "padwan-ai[realtime]"
```

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

`generate_speech` returns an `ElevenLabsAudio` with the raw `audio` bytes, its `mime_type` and the ElevenLabs
`request_id`. To keep prosody consistent across chunks of a long text, pass earlier IDs as `previous_request_ids` (or
the surrounding text as `previous_text` / `next_text`). Voice IDs come from your ElevenLabs voice library; pass one
per call or set a client default with `voice_id=`.

### Streaming

`stream_speech` takes the same arguments and yields audio chunks as they are generated, so playback can start before
the whole text is synthesized:

```python
async with ElevenLabsClient(voice_id="JBFqnCBsd6RMkjVDRZzb") as client:
    with Path("hello.mp3").open("wb") as f:
        async for chunk in client.stream_speech("Hello from Padwan."):
            f.write(chunk)
```

### Realtime input (WebSocket)

When the text itself arrives in pieces (e.g. from an LLM stream), `ElevenLabsRealtimeTTSClient` sends it over a
WebSocket as it comes and yields audio back. `stream()` accepts a sync or async iterable of text:

```python
from padwan_ai import ElevenLabsRealtimeTTSClient


async def llm_tokens():
    yield "Hello there, "
    yield "this is realtime speech."


async with ElevenLabsRealtimeTTSClient(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model="eleven_flash_v2_5",  # default
    output_format="pcm_16000",
) as tts:
    async for audio in tts.stream(llm_tokens()):
        ...  # play or buffer the PCM chunk
```

For finer control, call `send_text(text, flush=False)` and `end_input()` yourself and iterate the connection: each
message's `audio_bytes()` holds audio and `is_final()` marks the end. `chunk_length_schedule` and `auto_mode` tune the
latency/quality trade-off.

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

### Realtime transcription (WebSocket)

`ElevenLabsRealtimeSTTClient` streams microphone audio to Scribe (`scribe_v2_realtime`) and returns partial and
committed transcripts. Send audio in the client's `audio_format` (default mono PCM16 at 16 kHz). With the default
manual strategy you `commit()` each segment; `commit_strategy="vad"` lets the server commit on silence.

```python
from padwan_ai import ElevenLabsRealtimeSTTClient

async with ElevenLabsRealtimeSTTClient(language_code="en") as stt:
    for chunk in pcm16_chunks:
        await stt.append_audio(chunk)
    await stt.commit()
    async for message in stt:
        print(message["message_type"], stt.transcript(message))
        if stt.is_committed(message):
            break
```

Error frames (auth, quota, rate limits, bad input) raise `LLMError` (or `QuotaExceededError`) while iterating.

## Speech-to-speech

`speech_to_speech` re-voices a recording with another voice, keeping its delivery, emotion and timing (the ElevenLabs
voice changer). It takes a path or raw bytes and returns an `ElevenLabsAudio`; `stream_speech_to_speech` yields the
audio in chunks instead:

```python
async with ElevenLabsClient(voice_id="JBFqnCBsd6RMkjVDRZzb") as client:
    speech = await client.speech_to_speech(
        "my_recording.mp3",
        model="eleven_multilingual_sts_v2",  # default; or eleven_english_sts_v2
        remove_background_noise=True,
    )
```

Pass `file_format="pcm_s16le_16"` for raw 16 kHz mono PCM input to skip decoding and lower latency.

## Sound effects and music

Both return an `ElevenLabsAudio` (MP3 unless `output_format` says otherwise):

```python
async with ElevenLabsClient() as client:
    knock = await client.generate_sound_effect("a door knock", duration_seconds=1.5)
    jingle = await client.compose_music(
        "calm piano jingle", music_length_ms=10_000, force_instrumental=True
    )
```

`compose_music` takes either a text `prompt` or a structured `composition_plan` (see the
[music reference](https://elevenlabs.io/docs/api-reference/music/compose)).

## Voices

```python
async with ElevenLabsClient() as client:
    voices = await client.list_voices()
    voice = await client.get_voice("JBFqnCBsd6RMkjVDRZzb")
    voice_id = await client.clone_voice("Narrator", ["sample1.mp3", "sample2.mp3"])
    await client.delete_voice(voice_id)
```

`clone_voice` creates an instant voice clone (paid plans only) and returns its ID.

## Not covered yet

Dubbing, voice design, professional voice cloning and the Agents platform (conversational speech-to-speech) are not
implemented.
