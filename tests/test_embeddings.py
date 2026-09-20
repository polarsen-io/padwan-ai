from contextlib import nullcontext
from unittest.mock import AsyncMock

import pytest

from padwan_ai import (
    GeminiClient,
    GrokClient,
    MistralClient,
    OpenAIClient,
    VoyageClient,
    vectors,
)
from padwan_ai._base import LLMClientBase
from padwan_ai.errors import LLMError

OPENAI_PAYLOAD = {
    "object": "list",
    "model": "m",
    "data": [{"object": "embedding", "embedding": [0.1, 0.2], "index": 0}],
    "usage": {"prompt_tokens": 2, "total_tokens": 2},
}
GEMINI_PAYLOAD = {"embeddings": [{"values": [0.1, 0.2]}]}


@pytest.mark.parametrize(
    "client, kwargs, path, body, payload",
    [
        pytest.param(
            OpenAIClient(model="text-embedding-3-small", api_key="k"),
            {"dimensions": 256},
            "/embeddings",
            {"model": "text-embedding-3-small", "input": ["a", "b"], "dimensions": 256},
            OPENAI_PAYLOAD,
            id="openai-default-model",
        ),
        pytest.param(
            MistralClient(api_key="k"),
            {"model": "mistral-embed", "dimensions": 256},
            "/embeddings",
            {"model": "mistral-embed", "input": ["a", "b"], "output_dimension": 256},
            OPENAI_PAYLOAD,
            id="mistral-explicit-model",
        ),
        pytest.param(
            GrokClient(api_key="k"),
            {"model": "grok-embed", "extra_params": {"encoding_format": "base64"}},
            "/embeddings",
            {"model": "grok-embed", "input": ["a", "b"], "encoding_format": "base64"},
            OPENAI_PAYLOAD,
            id="grok-extra-params",
        ),
        pytest.param(
            VoyageClient(api_key="k"),
            {"extra_params": {"input_type": "query"}},
            "/embeddings",
            {"model": "voyage-4", "input": ["a", "b"], "input_type": "query"},
            OPENAI_PAYLOAD,
            id="voyage",
        ),
        pytest.param(
            GeminiClient(model="gemini-embedding-001", api_key="k"),
            {"dimensions": 768, "extra_params": {"taskType": "RETRIEVAL_QUERY"}},
            "/models/gemini-embedding-001:batchEmbedContents",
            {
                "requests": [
                    {
                        "model": "models/gemini-embedding-001",
                        "content": {"role": "user", "parts": [{"text": text}]},
                        "outputDimensionality": 768,
                        "taskType": "RETRIEVAL_QUERY",
                    }
                    for text in ("a", "b")
                ]
            },
            GEMINI_PAYLOAD,
            id="gemini",
        ),
    ],
)
async def test_fetch_embeddings_request(
    client: LLMClientBase, kwargs: dict, path: str, body: dict, payload: dict, make_resp
):
    client._session = AsyncMock()
    client._session.post.return_value = make_resp(200, payload)

    result = await client.fetch_embeddings(["a", "b"], **kwargs)  # type: ignore[attr-defined]

    client._session.post.assert_awaited_once_with(path, json=body)
    assert result == payload


@pytest.mark.parametrize(
    "client, input, expected_input, ctx",
    [
        pytest.param(
            OpenAIClient(model="text-embedding-3-small", api_key="k"),
            "solo",
            "solo",
            nullcontext(),
            id="openai-single-string-untouched",
        ),
        pytest.param(
            GeminiClient(model="gemini-embedding-001", api_key="k"),
            "solo",
            "solo",
            nullcontext(),
            id="gemini-single-string-wrapped",
        ),
        pytest.param(
            OpenAIClient(model=None, api_key="k"),
            "solo",
            None,
            pytest.raises(LLMError, match="No model specified"),
            id="openai-no-model",
        ),
        pytest.param(
            GeminiClient(model=None, api_key="k"),
            "solo",
            None,
            pytest.raises(LLMError, match="No model specified"),
            id="gemini-no-model",
        ),
    ],
)
async def test_fetch_embeddings_input_and_model_guard(
    client: LLMClientBase, input: str, expected_input: str | None, ctx, make_resp
):
    client._session = AsyncMock()
    client._session.post.return_value = make_resp(200, {})
    with ctx:
        await client.fetch_embeddings(input)  # type: ignore[attr-defined]
    if expected_input is None:
        client._session.post.assert_not_awaited()
        return
    sent = client._session.post.await_args.kwargs["json"]
    if isinstance(client, GeminiClient):
        assert [r["content"]["parts"][0]["text"] for r in sent["requests"]] == [
            expected_input
        ]
    else:
        assert sent["input"] == expected_input


@pytest.mark.parametrize(
    "resp, provider, expected",
    [
        pytest.param(
            {"embeddings": [{"values": [0.1]}, {"values": [0.2]}]},
            "gemini",
            [[0.1], [0.2]],
            id="gemini-input-order",
        ),
        pytest.param(
            {
                "data": [
                    {"object": "embedding", "embedding": [0.2], "index": 1},
                    {"object": "embedding", "embedding": [0.1], "index": 0},
                ]
            },
            "voyage",
            [[0.1], [0.2]],
            id="openai-shape-sorted-by-index",
        ),
    ],
)
def test_vectors(resp: dict, provider: str, expected: list[list[float]]):
    assert vectors(resp, provider) == expected  # type: ignore[arg-type]
