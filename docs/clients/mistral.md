---
icon: simple/mistralai
---

# Mistral Client

The Mistral client provides access to Mistral AI models. It shares [`OpenAIClient`](openai.md)'s OpenAI-compatible chat base (no batch API) since Mistral uses an OpenAI-compatible API.

## Configuration

```python
from padwan_ai.mistral import MistralClient

client = MistralClient(
    api_key="...",  # or set MISTRAL_API_KEY env var
    model="mistral-large-latest",  # default model
)
```

`padwan_ai.mistral.supports_audio(model, fmt=None)` / `supports_vision(model)` check model capabilities; `AUDIO_FORMATS` lists supported formats.

## Usage

### Basic Chat

```python
from padwan_ai.conversation import Message

async with MistralClient() as client:
    response, usage = await client.complete_chat(
        [Message(role="user", content="Hello!")]
    )
    print(response["content"])
```

### Streaming

```python
from padwan_ai.conversation import Message

async with MistralClient() as client:
    stream = client.stream_chat([Message(role="user", content="Tell me a story")])
    async for chunk in stream:
        print(chunk, end="")
```

### With System Prompt

```python
from padwan_ai import ConversationState

state = ConversationState(system="You are a helpful assistant.")
state.add_user_message("Hello!")

async with MistralClient() as client:
    response, usage = await client.complete_chat(state.messages)
    state.add_assistant_response(response)
    state.accumulate_usage(usage)
```

## Audio Transcription

Transcribe audio using the `voxtral-mini-latest` model (the default; pass `model=` to override).

```python
async with MistralClient() as client:
    # From a local file
    result = await client.transcribe(file="recording.mp3")
    print(result["text"])

    # From a URL
    result = await client.transcribe(file_url="https://example.com/audio.mp3")

    # From an uploaded file ID
    result = await client.transcribe(file_id="file-abc123")
```

Exactly one of `file`, `file_id`, or `file_url` must be provided. `file` accepts a path (`str`/`Path`) or raw `bytes`.

Optional parameters: `model`, `language`, `temperature`, `diarize` (speaker detection), and `timestamp_granularities` (`["segment"]` and/or `["word"]`).

```python
result = await client.transcribe(
    file="meeting.mp3",
    language="en",
    diarize=True,
    timestamp_granularities=["segment", "word"],
)
for segment in result.get("segments", []):
    print(f"[{segment['start']:.1f}s] {segment['text']}")
```

## Embeddings

Generate text embeddings with `mistral-embed` or `codestral-embed`. The model is the client's default unless passed explicitly.

```python
from padwan_ai import vectors

async with MistralClient(model="mistral-embed") as client:
    resp = await client.fetch_embeddings("Hello, world!")
    # Or batch multiple texts, optionally with a reduced vector size
    resp = await client.fetch_embeddings(["text 1", "text 2"], dimensions=512)
    vecs = vectors(resp, "mistral")  # one list[float] per input, in input order
```

Mistral-only fields (e.g. `output_dtype`) go through `extra_params={"output_dtype": "int8"}`.
