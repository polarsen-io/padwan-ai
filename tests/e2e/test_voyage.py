import pytest

from padwan_ai import VoyageClient

from .conftest import skip_no_voyage

pytestmark = [pytest.mark.e2e, skip_no_voyage]


async def test_embeddings() -> None:
    async with VoyageClient() as client:
        resp = await client.fetch_embeddings(
            ["Hello", "World"], dimensions=256, extra_params={"input_type": "query"}
        )
        assert len(resp["data"]) == 2
        assert len(resp["data"][0]["embedding"]) == 256
        assert resp["usage"]["total_tokens"] > 0
