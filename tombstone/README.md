# padwan-llm

This package was renamed to [`padwan-ai`](https://pypi.org/project/padwan-ai/).

`pip install padwan-llm` now installs `padwan-ai`. Replace `import padwan_llm` with `import padwan_ai`; the old import raises an `ImportError` pointing here.

Publish once, by hand, after the first `padwan-ai` release: `cd tombstone && uv build && uv publish`.
