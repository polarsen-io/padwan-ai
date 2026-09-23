---
icon: lucide/sailboat
---

# Voyage AI Client

Voyage AI is an embeddings-only provider (the one Anthropic recommends alongside Claude). The client shares the OpenAI-compatible base, so only `fetch_embeddings` is meaningful; chat methods are not served by the API.

## Configuration

```python
from padwan_ai import vectors
from padwan_ai.voyage import VoyageClient

client = VoyageClient(
    api_key="...",  # or set VOYAGE_API_KEY env var
    model="voyage-4",  # default model
)
```

## Usage

```python
async with VoyageClient() as client:
    docs = await client.fetch_embeddings(
        ["text 1", "text 2"],
        dimensions=512,
        extra_params={"input_type": "document"},
    )
    query = await client.fetch_embeddings(
        "search text", extra_params={"input_type": "query"}
    )
    doc_vectors = vectors(docs, "voyage")  # one list[float] per input, in input order
```

`input_type` prepends Voyage's retrieval prompts; leave it out for symmetric use cases. See the [Voyage embeddings docs](https://docs.voyageai.com/docs/embeddings) for models and dimensions.
