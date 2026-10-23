---
icon: lucide/audio-waveform
---

# Gradium Client

!!! warning "Experimental"
    The Gradium client is experimental: its interface and typed payloads may change between minor releases without a deprecation cycle.

[Gradium](https://gradium.ai) is a speech provider: low-latency text-to-speech and speech-to-text in English, French,
German, Spanish and Portuguese. `GradiumClient` is standalone like the [ElevenLabs client](elevenlabs.md): it is not an
`LLMClientBase` subclass and `LLMClient` does not route to it. It covers the REST endpoints and voice management;
`GradiumRealtimeTTSClient`, `GradiumRealtimeSTTClient` and `GradiumRealtimeS2SClient` cover the WebSocket streams
(install the `realtime` extra).

## Configuration

Set `GRADIUM_API_KEY` in your environment or pass `api_key=` explicitly. `base_url` defaults to
`https://api.gradium.ai/api/`; use `https://eu.api.gradium.ai/api/` or `https://us.api.gradium.ai/api/` for data
residency.

The env key is used only when `base_url` is the official host over TLS on port 443. Any other `base_url` without
`api_key`, including a residency host, falls back to `PADWAN_API_KEY`, then `"no-key-required"`. The realtime clients
follow the same rule.

Requests retry up to three times on connection errors; GET, PUT and DELETE also on HTTP 502, 503 and 504 (Gradium
reports its own failures as 500, which is not retried, and a POST is billed or creates a voice, so it is never resent). A rate limit (429) raises `TooManyRequestsError`; other API errors, including errors streamed
after a successful transcription response started, raise `LLMError` with `provider="gradium"`. Bad arguments (no voice,
unknown audio extension) raise `ValueError`.

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

### Streaming

`stream_speech` takes the same arguments and yields audio chunks as they are generated, so playback can start before
the whole text is synthesized:

```python
async with GradiumClient(voice_id="YTpq7expH9539ERJ") as client:
    with Path("hello.wav").open("wb") as f:
        async for chunk in client.stream_speech("Hello from Padwan."):
            f.write(chunk)
```

### Realtime input (WebSocket)

When the text itself arrives in pieces (e.g. from an LLM stream), `GradiumRealtimeTTSClient` sends it over a WebSocket
as it comes and yields audio back. `stream()` accepts a sync or async iterable of text and regroups tokens on
whitespace, since the server joins consecutive messages with a space:

```python
from padwan_ai import GradiumRealtimeTTSClient


async def llm_tokens():
    yield "Hello there, "
    yield "this is realtime speech."


async with GradiumRealtimeTTSClient(
    voice_id="YTpq7expH9539ERJ",
    output_format="pcm",  # default: 48 kHz s16le mono; or pcm_24000, opus, ...
) as tts:
    print(tts.ready["request_id"])
    async for audio in tts.stream(llm_tokens()):
        ...  # play or buffer the PCM chunk
```

For finer control, call `send_text(text)` and `end_input()` yourself and iterate the connection: `audio_bytes()`
decodes `audio` messages, `transcript()` returns the timed `text` messages and `is_final()` marks the end.

## Speech-to-text

```python
async with GradiumClient() as client:
    result = await client.transcribe(
        file="meeting.wav",  # path or raw bytes: wav, raw pcm (24 kHz s16le mono) or Ogg Opus
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

### Realtime transcription (WebSocket)

`GradiumRealtimeSTTClient` streams audio (default `input_format="pcm"`: 24 kHz s16le mono, ideally in 80 ms chunks of
1920 samples) and yields server messages: `text` transcripts, `end_text` timestamps, `step` voice activity every 80 ms
and `flushed` replies to `flush()`.

```python
from padwan_ai import GradiumRealtimeSTTClient

async with GradiumRealtimeSTTClient(language="en") as stt:
    async for message in stt.stream(pcm_chunks):  # then sends end_of_stream
        if text := stt.transcript(message):
            print(text)
        elif message["type"] == "step" and message["vad"][2]["inactivity_prob"] > 0.5:
            ...  # the speaker has likely finished their turn
```

To drive the socket yourself, call `append_audio(chunk)`, `flush()` and `end_input()` and iterate the connection;
`stream()` ends the input, so a connection streams once.

## Speech-to-speech (WebSocket)

`GradiumRealtimeS2SClient` transcribes streamed audio, translates it into `target_language` and re-synthesizes it with
`voice_id`, returning both the translated `text` and the output `audio`:

```python
from padwan_ai import GradiumRealtimeS2SClient

async with GradiumRealtimeS2SClient(
    voice_id="YTpq7expH9539ERJ", target_language="fr"
) as s2s:
    async for message in s2s.stream(pcm_chunks):  # 24 kHz s16le mono by default
        if audio := s2s.audio_bytes(message):
            ...  # output PCM at the rate reported in s2s.ready["sample_rate"]
        elif text := s2s.transcript(message):
            print(text)
```

The defaults (`model="s2s-translate"`, `stt_model="stt-translate"`, `tts_model="default"`) are the only combination
the API accepts today.

Gradium has no plain voice conversion: a session without `target_language` is refused. To re-voice speech without
translating it, set `target_language` to the spoken language (e.g. `"en"` for English input) and pick a voice in that
language. The pipeline transcribes then re-synthesizes, so the words are kept but not the original tone, emotion or
pacing (unlike ElevenLabs' `speech_to_speech`).

Raw `pcm` input must be 24 kHz s16le mono, while `pcm` output is 48 kHz: feeding TTS `pcm` output straight back in
garbles the transcription. Send wav (`input_format="wav"`) or resample first.

Error frames on any of the WebSocket streams (bad key, unknown model, no capacity) raise `LLMError` while iterating.

## Voices

```python
async with GradiumClient() as client:
    voices = await client.list_voices(include_catalog=True)  # with flagship voices
    voice = await client.get_voice("YTpq7expH9539ERJ")
    voice_id = await client.clone_voice("Narrator", "sample.wav", language="en")
    await client.update_voice(voice_id, description="Calm narrator")
    await client.delete_voice(voice_id)
```

`clone_voice` creates a custom voice from one audio sample and returns its ID; the format is inferred from the file
extension (pass `input_format=` for raw bytes). Voice design (prompt-generated voices), voice enhancement, localization
and pronunciation dictionaries are not covered yet.
