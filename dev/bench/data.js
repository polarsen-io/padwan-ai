window.BENCHMARK_DATA = {
  "lastUpdate": 1793194642911,
  "repoUrl": "https://github.com/polarsen-io/padwan-ai",
  "entries": {
    "Import Performance": [
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dad7148968a9864fbf1297c09c606bbebd14156f",
          "message": "feat: audio input content parts across providers (#43)\n\n* feat: audio input content parts across providers\n\nAdd ContentAudioPart (OpenAI input_audio shape, wav/mp3) with an audio_part\nbuilder and content_parts inference. OpenAI/Grok receive parts verbatim,\nGemini converts to inlineData, Mistral rewrites to its base64 input_audio\nchunk via a new _prepare_messages hook. supports_audio mirrors\nsupports_vision with per-provider curated checks.\n\n* feat: accept str paths in audio_part like image_part\n\n* docs: use parentheses instead of em-dashes in audio docs\n\n* feat: per-provider audio format support\n\nWiden AudioFormat to wav/mp3/flac/ogg/aac/aiff/m4a and make supports_audio\nformat-aware (fmt param). Curated per provider: OpenAI wav/mp3 (API schema),\nGemini all formats, Mistral voxtral wav/mp3/flac/ogg (verified against the\nchat API; m4a rejected). Providers expose AUDIO_FORMATS.\n\n* test(otel): multimodal parts captured without binary payloads\n\n* fix: lazy-module registration and otel fixture rename after rebase\n\nRegister padwan_llm.audio in the top-level __lazy_modules__ set (Python\n3.15) and adapt the binary-parts capture test to the otel_logging fixture.",
          "timestamp": "2026-08-23T08:04:56+02:00",
          "tree_id": "be8dc374e3b4a3c08717137427581df6fc264dfa",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/dad7148968a9864fbf1297c09c606bbebd14156f"
        },
        "date": 1787465136855,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 217.05,
            "unit": "ms",
            "range": 5.21
          },
          {
            "name": "padwan_llm.openai",
            "value": 217.6,
            "unit": "ms",
            "range": 4.34
          },
          {
            "name": "padwan_llm.otel",
            "value": 234.23,
            "unit": "ms",
            "range": 6.07
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "99394ca05996f5e3699aae9fbcf94f8f2f748593",
          "message": "chore(release): release 0.9.0 (#45)",
          "timestamp": "2026-08-23T08:15:33+02:00",
          "tree_id": "631e8b661f2d02d36a318d6da02e3f768264e2ee",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/99394ca05996f5e3699aae9fbcf94f8f2f748593"
        },
        "date": 1787465776650,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 217.23,
            "unit": "ms",
            "range": 5.21
          },
          {
            "name": "padwan_llm.openai",
            "value": 213.91,
            "unit": "ms",
            "range": 2.62
          },
          {
            "name": "padwan_llm.otel",
            "value": 232.3,
            "unit": "ms",
            "range": 4.86
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cbeec528ea996530aca98fdcda6ee1943cc3d81a",
          "message": "fix: close half-read SSE streams before returning connections to the pool (#46)\n\n* fix: close half-read SSE streams before returning connections to the pool\n\nA stream that breaks on [DONE] (or is abandoned by its consumer) left the\nSSE response half-read; the pooled connection could then hang the next\nstream request. Abort the extension in a finally across all providers.\n\n* refactor: dedupe the SSE stream loop into LLMClientBase._iter_sse\n\next.close() alone releases the pooled connection (verified against a live\nSSE backend on HTTP/1.1 and HTTP/2), so drop the raw-response teardown and\nthe mock-only regression test. Providers wrap the shared iterator in\naclosing so an abandoned stream closes deterministically.",
          "timestamp": "2026-08-23T15:30:06+02:00",
          "tree_id": "0433f9b8ccda881b64b9afdfce3de0d876aa4458",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/cbeec528ea996530aca98fdcda6ee1943cc3d81a"
        },
        "date": 1787491846516,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 228.07,
            "unit": "ms",
            "range": 1.62
          },
          {
            "name": "padwan_llm.openai",
            "value": 229.37,
            "unit": "ms",
            "range": 2.23
          },
          {
            "name": "padwan_llm.otel",
            "value": 242.42,
            "unit": "ms",
            "range": 2.51
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "101126627a97f748a515d5fafa6b56bd4c34450d",
          "message": "chore(release): release 0.9.1 (#47)",
          "timestamp": "2026-08-24T07:01:01+02:00",
          "tree_id": "923f2aa8c4df21aad9522d6cef8b2eb5f52516e8",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/101126627a97f748a515d5fafa6b56bd4c34450d"
        },
        "date": 1787547693881,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 210.55,
            "unit": "ms",
            "range": 1.54
          },
          {
            "name": "padwan_llm.openai",
            "value": 211.36,
            "unit": "ms",
            "range": 3.3
          },
          {
            "name": "padwan_llm.otel",
            "value": 223.83,
            "unit": "ms",
            "range": 0.94
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "943aabe4da8e06752e31853089e969c24ce38d7e",
          "message": "fix: best-effort SSE cleanup; tolerate HTTP/2 abort quirk (#48)\n\nClosing an already-finished HTTP/2 stream raises KeyError inside\nurllib3-future; the unguarded finally corrupted every successful stream\nover h2 backends (missing message end, spurious error event). Cleanup is\nnow best-effort per step and restores the raw-response teardown and pool\nrelease that the 0.9.1 refactor dropped (the ext-only close leaves the\nlease held until GC on HTTP/1.1).",
          "timestamp": "2026-08-24T16:49:18+02:00",
          "tree_id": "2d5f3f865af799f7e26f91ef5ae080070a843a02",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/943aabe4da8e06752e31853089e969c24ce38d7e"
        },
        "date": 1787583003526,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 209.33,
            "unit": "ms",
            "range": 2.16
          },
          {
            "name": "padwan_llm.openai",
            "value": 210,
            "unit": "ms",
            "range": 6.78
          },
          {
            "name": "padwan_llm.otel",
            "value": 224.53,
            "unit": "ms",
            "range": 2.15
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a6aff107fdfbdb9c4037918daacfd43e5c3c25d7",
          "message": "chore(release): release 0.9.2 (#50)",
          "timestamp": "2026-08-24T17:00:32+02:00",
          "tree_id": "0aff4bc9436e73d803c41d4b4e18ca3ed82b4bd3",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/a6aff107fdfbdb9c4037918daacfd43e5c3c25d7"
        },
        "date": 1787583672929,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 225.45,
            "unit": "ms",
            "range": 3.85
          },
          {
            "name": "padwan_llm.openai",
            "value": 224.44,
            "unit": "ms",
            "range": 3.56
          },
          {
            "name": "padwan_llm.otel",
            "value": 238.08,
            "unit": "ms",
            "range": 3.21
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "918b5dba5b0a112bd30cc3dc9ba4eaf3660bf852",
          "message": "chore: require urllib3-future 2.24.904 (#51)\n\nCarries the upstream fix for the HTTP/2 stream reset raising on\nalready-closed SSE streams (jawah/urllib3.future#406).",
          "timestamp": "2026-08-25T07:48:42+02:00",
          "tree_id": "ca67fc1f0cbffb68f8fdce475bb137cf0f9a845a",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/918b5dba5b0a112bd30cc3dc9ba4eaf3660bf852"
        },
        "date": 1787636964937,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 216.05,
            "unit": "ms",
            "range": 2.73
          },
          {
            "name": "padwan_llm.openai",
            "value": 216.05,
            "unit": "ms",
            "range": 8.72
          },
          {
            "name": "padwan_llm.otel",
            "value": 226.9,
            "unit": "ms",
            "range": 2.17
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "44ad0ebf0f3aade1e223c009fc64bb6abe091e83",
          "message": "chore(release): release 0.9.3 (#52)",
          "timestamp": "2026-08-25T07:58:09+02:00",
          "tree_id": "3ef9b9d70966d604affc758240aa898a37b76905",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/44ad0ebf0f3aade1e223c009fc64bb6abe091e83"
        },
        "date": 1787637532063,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 177.6,
            "unit": "ms",
            "range": 2.36
          },
          {
            "name": "padwan_llm.openai",
            "value": 178.2,
            "unit": "ms",
            "range": 1.66
          },
          {
            "name": "padwan_llm.otel",
            "value": 189.84,
            "unit": "ms",
            "range": 1.92
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a378470482e05fa814b73efa9f2dcdc2ac0fe55c",
          "message": "chore: weekly LLM SDK refresh (#49)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: add glm-5-2 and zai-glm-5-2 to MistralModel\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n* fix: restore Anthropic compatibility and Mistral routing\n\n* chore: require Anthropic 1.0\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-08-25T08:45:17+02:00",
          "tree_id": "87cf71a9e658d44441468efec7110e4e3708dbf7",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/a378470482e05fa814b73efa9f2dcdc2ac0fe55c"
        },
        "date": 1787640355893,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 218.04,
            "unit": "ms",
            "range": 2.85
          },
          {
            "name": "padwan_llm.openai",
            "value": 217.4,
            "unit": "ms",
            "range": 5.78
          },
          {
            "name": "padwan_llm.otel",
            "value": 228.43,
            "unit": "ms",
            "range": 2.6
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "40022bb75ab4ae0b6698102d362da2df522c9a50",
          "message": "chore(release): release 0.9.4 (#53)",
          "timestamp": "2026-08-25T16:01:50+02:00",
          "tree_id": "c99b20de729d81b7af17eb132aad10e25a051640",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/40022bb75ab4ae0b6698102d362da2df522c9a50"
        },
        "date": 1787666552224,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 215.49,
            "unit": "ms",
            "range": 2.88
          },
          {
            "name": "padwan_llm.openai",
            "value": 215.51,
            "unit": "ms",
            "range": 3.85
          },
          {
            "name": "padwan_llm.otel",
            "value": 229.44,
            "unit": "ms",
            "range": 2.21
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8c607e2633e80a4d93d71dd050b9a135dfc433f5",
          "message": "chore: weekly LLM SDK refresh (#54)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* feat(gemini): add gemini-3.5-transcribe, gemini-omni-1.1-flash, gemini-3.5-transcribe-live\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-08-31T21:53:25+02:00",
          "tree_id": "8ac03643185ca3336b874a72d2ff10c92bb1ea07",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/8c607e2633e80a4d93d71dd050b9a135dfc433f5"
        },
        "date": 1788206045635,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 209.71,
            "unit": "ms",
            "range": 2.05
          },
          {
            "name": "padwan_llm.openai",
            "value": 208.76,
            "unit": "ms",
            "range": 3.33
          },
          {
            "name": "padwan_llm.otel",
            "value": 223.66,
            "unit": "ms",
            "range": 1.65
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dfb179f56a73ce2140875182c26c5f23d5d33b12",
          "message": "chore: weekly LLM SDK refresh (#56)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: add drifted provider model literals\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-09-07T17:29:17+02:00",
          "tree_id": "ef67670966be1a7f8044e9ecc1895a39c9828f8f",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/dfb179f56a73ce2140875182c26c5f23d5d33b12"
        },
        "date": 1788794991008,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 182.53,
            "unit": "ms",
            "range": 2.05
          },
          {
            "name": "padwan_llm.openai",
            "value": 181.51,
            "unit": "ms",
            "range": 1.83
          },
          {
            "name": "padwan_llm.otel",
            "value": 192.23,
            "unit": "ms",
            "range": 2.63
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9524251e84392e30831c6cdcf13e279d101f3ec7",
          "message": "fix: infer supported audio formats from file extensions (#57)",
          "timestamp": "2026-09-08T09:46:54+02:00",
          "tree_id": "c5099efdb624191865fd018695a2a28320770833",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/9524251e84392e30831c6cdcf13e279d101f3ec7"
        },
        "date": 1788853646852,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 180.92,
            "unit": "ms",
            "range": 6.1
          },
          {
            "name": "padwan_llm.openai",
            "value": 180.75,
            "unit": "ms",
            "range": 3.55
          },
          {
            "name": "padwan_llm.otel",
            "value": 190.25,
            "unit": "ms",
            "range": 1.84
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "61604486f616e2485066be2690b77fb48b2b8cd5",
          "message": "fix(otel): trace raw OpenAI complete()/stream() calls (#55)\n\n* fix(otel): open a span for raw OpenAI complete()/stream() calls\n\nRaw OpenAIClient.complete()/stream() only enriched a chat span opened by\ncomplete_chat()/stream_chat(); callers using the raw API (padwan-proxy) got\nno telemetry at all. They now open their own span when none is active, with\nusage, finish reasons, tool names, time to first chunk and error status.\n\n* feat(otel): capture content on raw OpenAI complete()/stream() calls\n\nWith capture_content, raw calls now record gen_ai.input.messages,\ngen_ai.tool.definitions and gen_ai.output.messages (text and tool calls,\naccumulated from stream deltas) and emit the inference details log event,\nas the chat API already did.\n\n* fix(otel): preserve raw choices and isolate streaming context\n\n- Capture custom tool calls and keep response choices separate.\n- Restore caller context between chunks and close interrupted streams.\n- Declare typed MCP session timestamps and add regression coverage.",
          "timestamp": "2026-09-11T22:27:25+02:00",
          "tree_id": "c72877df84d110a169bd4eb2cf63fbd8f989ab58",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/61604486f616e2485066be2690b77fb48b2b8cd5"
        },
        "date": 1789158481730,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 210.16,
            "unit": "ms",
            "range": 1.92
          },
          {
            "name": "padwan_llm.openai",
            "value": 210.76,
            "unit": "ms",
            "range": 1.46
          },
          {
            "name": "padwan_llm.otel",
            "value": 224.8,
            "unit": "ms",
            "range": 2.92
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a9aaaa21efce1d22b15979632a0359d7f50bde3c",
          "message": "fix(otel): restore caller context between chat stream chunks (#58)\n\n- Limit active chat context to advancing the provider iterator.\n- Preserve metric trace links and cover cross-task stream lifecycle.",
          "timestamp": "2026-09-11T23:13:51+02:00",
          "tree_id": "b62648d77284041dccdfb215ba8ae6efc435a4ca",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/a9aaaa21efce1d22b15979632a0359d7f50bde3c"
        },
        "date": 1789161269908,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 213.85,
            "unit": "ms",
            "range": 2.34
          },
          {
            "name": "padwan_llm.openai",
            "value": 216.41,
            "unit": "ms",
            "range": 2.98
          },
          {
            "name": "padwan_llm.otel",
            "value": 232.84,
            "unit": "ms",
            "range": 3.31
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d7605973bafec0d42defc41620f6b09e87e8a34b",
          "message": "chore: weekly LLM SDK refresh (#65)\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>",
          "timestamp": "2026-09-14T18:35:03+02:00",
          "tree_id": "bec5e8de9b4f11d862e6062269c23923642eecfa",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/d7605973bafec0d42defc41620f6b09e87e8a34b"
        },
        "date": 1789403742820,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 215.52,
            "unit": "ms",
            "range": 2.76
          },
          {
            "name": "padwan_llm.openai",
            "value": 211.3,
            "unit": "ms",
            "range": 4.42
          },
          {
            "name": "padwan_llm.otel",
            "value": 227.44,
            "unit": "ms",
            "range": 4.13
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1582d3b35dac07cb297dd7506aaa405b9f6c456f",
          "message": "ci(perf): skip benchmark PR comments on fork PRs (#68)\n\nThe GITHUB_TOKEN is read-only on pull requests from forks, so posting the\nbenchmark comment fails with \"Resource not accessible by integration\" and\nmarks the job failed. Only comment when the head repo is this repo.",
          "timestamp": "2026-09-14T18:51:29+02:00",
          "tree_id": "e2a9ed43df0372653552769ff47c69425484977e",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/1582d3b35dac07cb297dd7506aaa405b9f6c456f"
        },
        "date": 1789404730404,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 219.01,
            "unit": "ms",
            "range": 3.69
          },
          {
            "name": "padwan_llm.openai",
            "value": 217.67,
            "unit": "ms",
            "range": 6.14
          },
          {
            "name": "padwan_llm.otel",
            "value": 229.65,
            "unit": "ms",
            "range": 3.46
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f0f3eb05a241fa1bf9ea4ff4a235d7cc13c541fd",
          "message": "feat(testing): ScriptedClient, a scripted stand-in for any client (#59)\n\n* feat(testing): ScriptedClient, a scripted stand-in for any client\n\nA client that replays a script of rounds (text and/or tool calls) instead of calling a\nprovider, records what the model would have seen round by round, and fails loudly when\nthe script runs out. Drives an AgentSession end to end in tests without a key or a socket.\n\n* fix(testing): snapshot recorded requests, align ScriptedClient with repo conventions (#63)\n\n* fix(testing): snapshot recorded requests, align ScriptedClient with repo conventions\n\nDeep-copy messages, tools and extra_params when recording a round so later\nmutation by the caller does not alter the record. Drop the future import and\nmodule docstring, use text: str | None, parametrize tests, and fix the\nNotRequired access that failed pyright on tests/.\n\n* refactor(testing): make ScriptedClient a dataclass\n\n* test(testing): keep only the essential ScriptedClient tests\n\n* test(testing): type recorded messages as Message\n\n* refactor(agent): type the session client as a ChatClient protocol\n\nAny async context manager with stream_chat now satisfies AgentSession, so\ntest doubles no longer need cast(LLMClientBase, ...). ScriptedClient uses\nMapping[str, object] instead of Any for tool arguments and extra_params.\n\n* docs(agents): client accepts any ChatClient\n\n* docs(agents): drop roadmap prose from limitations\n\n* docs(agents): keep the testing example ruff-format stable\n\n* docs(testing): one-line docstrings on ScriptedClient helpers\n\n(cherry picked from commit 2f76772748f98013458a7fb47d34b31b6c583500)\n\n---------\n\nCo-authored-by: Julien Brayere <julien.brayere@obitrain.com>",
          "timestamp": "2026-09-14T21:05:48+02:00",
          "tree_id": "25ebc58ff46254841c95e7d2c9743c2f985edde2",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/f0f3eb05a241fa1bf9ea4ff4a235d7cc13c541fd"
        },
        "date": 1789412779677,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 213.45,
            "unit": "ms",
            "range": 3.47
          },
          {
            "name": "padwan_llm.openai",
            "value": 211.38,
            "unit": "ms",
            "range": 2.08
          },
          {
            "name": "padwan_llm.otel",
            "value": 232.2,
            "unit": "ms",
            "range": 5.18
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ad9666e3d60604b321dccb59de03bf5deac29190",
          "message": "feat(tools): pluggable validator for tool() (msgspec or pydantic) (#67)\n\n* feat(tools): build an McpTool from a typed async function\n\ntool(fn) turns a typed async function into an McpTool: the signature becomes the JSON\nSchema the model sees, the docstring the description, and the arguments the model sends\nare validated (and coerced) before the function runs. Pydantic does the work, behind a\nnew optional extra: pip install \"padwan-llm[pydantic]\".\n\n* feat(tools): validate tool arguments with msgspec instead of pydantic\n\nSwap the pydantic extra for msgspec: single wheel, no transitive deps, and the\nconsumers already use it. Keep Annotated constraints in the schema\n(include_extras), refuse positional-only and variadic parameters at build time,\ndrop per-property title noise from the schema, and dump results through\nmsgspec.to_builtins.\n\n* feat(tools): let the caller pick the validator (msgspec or pydantic)\n\ntool() takes validator=\"msgspec\" | \"pydantic\" | ToolValidator instance. With\nnone given it uses the only installed backend and raises when both are, since\nconstraint annotations are library-specific and a guessed backend would drop\nthem silently. Neither library is a dependency or extra; both are dev deps so\nthe suite covers both. Pydantic results are dumped with\npydantic_core.to_jsonable_python; unserialisable results now raise inside the\nhandler so they reach the model as a tool error instead of crashing the session.\n\n* feat(tools): pick the validator from the annotations\n\nWith no validator= given, a msgspec.Meta constraint or Struct type selects\nmsgspec and a pydantic.Field constraint or BaseModel type selects pydantic,\nthrough Annotated metadata, unions and generics. Mixed annotations raise. Plain\nsignatures keep the only-installed rule.\n\n* docs(agents): examples for msgspec, pydantic and explicit validators\n\n* docs(agents): msgspec / pydantic examples as content tabs\n\n* docs(agents): ruff-format the code blocks\n\n---------\n\nCo-authored-by: Carlo Abi Chahine <carlo.abichahine@gmail.com>",
          "timestamp": "2026-09-14T22:03:21+02:00",
          "tree_id": "65057c50de962d572c98f4f584d0104f3e98f29a",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/ad9666e3d60604b321dccb59de03bf5deac29190"
        },
        "date": 1789416235132,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 210.05,
            "unit": "ms",
            "range": 3.06
          },
          {
            "name": "padwan_llm.openai",
            "value": 211.71,
            "unit": "ms",
            "range": 3.73
          },
          {
            "name": "padwan_llm.otel",
            "value": 225.4,
            "unit": "ms",
            "range": 4.69
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0d6d67298105e71cddafb878af69aaf2c45a6714",
          "message": "feat(langfuse): time to first token as completion_start_time (#69)\n\n* feat(langfuse): map the first streamed chunk to completion_start_time\n\nStreams already carried `gen_ai.response.time_to_first_chunk` (a duration), but\nLangfuse only shows time to first token when a generation has an absolute\n`completion_start_time`, and the OTel mask hook does not expose span start\ntimes, so the duration alone could not be converted.\n\n- otel: the two streaming paths share `_record_first_chunk`, which also stamps\n  `padwan_llm.response.first_chunk_time` (ISO 8601 UTC) on the chat span.\n- langfuse: `_mapped_attributes` serializes that instant as\n  `langfuse.observation.completion_start_time`, the same JSON form the SDK uses.\n- docs: both attribute tables list the new mapping.\n\n* fix(otel): count the first raw provider chunk on the active chat span\n\nThe chat wrapper only sees the text chunks a `ChatStream` yields, so a\nstream that answers with tool calls or reasoning alone never recorded a\ntime to first chunk. The raw `stream()` wrapper, which already enriches\nthe active chat span, now records the first provider chunk on it; the\nchat wrapper's own text-chunk record becomes a fallback for providers\nwhose raw stream is not wrapped. `_record_first_chunk` records once per\nspan.\n\nThe wall-clock instant now uses the `Z` suffix, like the Langfuse SDK.\n\n* fix(otel): keep the stream label on the raw first-chunk histogram\n\nThe raw stream wrapper recorded time_to_first_chunk without\ngen_ai.request.stream=True, unlike the chat wrapper it replaces. Also\nshortens the new docstring and comment, and states in the docs which\nproviders count the first raw chunk versus the first text chunk.\n\n---------\n\nCo-authored-by: Carlo Abi Chahine <carlo.abichahine@gmail.com>",
          "timestamp": "2026-09-14T22:37:07+02:00",
          "tree_id": "040f8bcd481ea9c1779a9989a8d6268c44b4500d",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/0d6d67298105e71cddafb878af69aaf2c45a6714"
        },
        "date": 1789418268912,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 154.72,
            "unit": "ms",
            "range": 5.14
          },
          {
            "name": "padwan_llm.openai",
            "value": 148.97,
            "unit": "ms",
            "range": 5.24
          },
          {
            "name": "padwan_llm.otel",
            "value": 157.84,
            "unit": "ms",
            "range": 4.09
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "97bc53b47bd648dc18793902234b1ed9daaa65b3",
          "message": "feat(langfuse): instrument() passes span_exporter and httpx_client to the client (#70)\n\n* feat(langfuse): instrument() passes span_exporter and httpx_client to the client\n\nBoth are Langfuse client options already; exposing them lets a test run the real integration\non an in-memory span exporter and a mock HTTP transport, and assert on every attribute the\nadapter and the SDK would send, without a socket.\n\n* docs(langfuse): keep the instrument() docstring to one line\n\n* test(langfuse): drop the passthrough test, it restates the forwarding\n\n---------\n\nCo-authored-by: Carlo Abi Chahine <carlo.abichahine@gmail.com>",
          "timestamp": "2026-09-14T22:38:59+02:00",
          "tree_id": "40e7a3e5e259d601729fa519ccdcb282c052f5df",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/97bc53b47bd648dc18793902234b1ed9daaa65b3"
        },
        "date": 1789418379151,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 229.59,
            "unit": "ms",
            "range": 13.22
          },
          {
            "name": "padwan_llm.openai",
            "value": 210.89,
            "unit": "ms",
            "range": 1.46
          },
          {
            "name": "padwan_llm.otel",
            "value": 224.84,
            "unit": "ms",
            "range": 2.82
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6b6d48b2da64ff4091d6d292a9cc857b7dc96a9f",
          "message": "fix(langfuse): import httpx at runtime, the annotation is evaluated on Python 3.13 (#71)",
          "timestamp": "2026-09-14T22:41:46+02:00",
          "tree_id": "8423b6193f65cfe249308f0464ec8d40751680d0",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/6b6d48b2da64ff4091d6d292a9cc857b7dc96a9f"
        },
        "date": 1789418574161,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 209.9,
            "unit": "ms",
            "range": 1.38
          },
          {
            "name": "padwan_llm.openai",
            "value": 211.75,
            "unit": "ms",
            "range": 1.31
          },
          {
            "name": "padwan_llm.otel",
            "value": 224.13,
            "unit": "ms",
            "range": 1.8
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3587b1ae4c583f69854606bdc8662b52844556ba",
          "message": "refactor(langfuse): keep httpx a type-only import (#72)",
          "timestamp": "2026-09-14T22:46:22+02:00",
          "tree_id": "96ead28b58fc1f33c8d9b3698ac7b4bb7b4dcbd6",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/3587b1ae4c583f69854606bdc8662b52844556ba"
        },
        "date": 1789418821868,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 210.99,
            "unit": "ms",
            "range": 2.02
          },
          {
            "name": "padwan_llm.openai",
            "value": 210.69,
            "unit": "ms",
            "range": 1.73
          },
          {
            "name": "padwan_llm.otel",
            "value": 223.64,
            "unit": "ms",
            "range": 1.51
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "julien",
            "username": "Andarius"
          },
          "committer": {
            "email": "julien.brayere@obitrain.com",
            "name": "julien",
            "username": "Andarius"
          },
          "distinct": true,
          "id": "793ca31ada775f20042a3d59029a26ec400f7760",
          "message": "chore(just): docs recipe takes a port\n\nClaude-Session: https://claude.ai/code/session_01KTHPAvoDsiAWntwyc8JSF1",
          "timestamp": "2026-09-14T22:50:52+02:00",
          "tree_id": "be6ddcbd482cd8c52314521e18262ef7e766f5d1",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/793ca31ada775f20042a3d59029a26ec400f7760"
        },
        "date": 1789419090272,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 223.29,
            "unit": "ms",
            "range": 2.67
          },
          {
            "name": "padwan_llm.openai",
            "value": 224.34,
            "unit": "ms",
            "range": 1.61
          },
          {
            "name": "padwan_llm.otel",
            "value": 241.44,
            "unit": "ms",
            "range": 4.82
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ad0a31abab8ccd05935b0707daeda3dc35bb984f",
          "message": "feat(agent): typed final answer through an output tool (#73)\n\n* feat(agent): typed final answer through an output tool\n\nAgentSession(output=Model) adds a `submit` tool whose parameters are the\nanswer's schema; run() drives the loop until a call validates and returns\nthe instance. Invalid calls go back to the model up to max_repairs times,\nthen OutputError; a text answer or the round limit raise OutputError too.\n\nThe answer class goes through the tool() validators: ToolValidator gains\nschema(cls) and convert(obj, cls), compile() is built on them, and the\nbackend is resolved from the class (Struct, BaseModel) or output_validator=.\n\n* perf(tools): build the validator adapter once per class\n\nToolValidator.schema/convert become adapt(cls) -> (schema, convert): a pydantic\nTypeAdapter is built once and reused, per the pydantic performance docs, instead\nof once per tool call.\n\n* refactor(agent): group the typed-answer settings in AgentOutput\n\nAgentSession(output=AgentOutput(cls, validator=, tool=, max_repairs=)) replaces\nfour output_* fields; per-run state moves to a private _OutputRun so one\nAgentOutput can be shared across sessions.\n\n* fix(agent): settle the typed answer once, reject broken JSON, keep recursive schemas valid\n\n- the first accepted submit or the exhausted repair budget settles a run;\n  later calls in the round are answered with an error and ignored\n- tool arguments that are not valid JSON are returned as an error instead\n  of running the handler on {}; for the output tool it counts as a repair\n- ToolValidator.adapt keeps a recursive class under $defs so its inner\n  $refs resolve, for msgspec and pydantic alike\n- AgentOutput[T] / AgentSession[T = Any]: run() returns T, load() infers it\n- docs: output= in the configuration block, approval and sibling-tool notes\n\n* refactor(agent): type the output handler's result\n\n* refactor(agent): default the session's answer type to object, not Any\n\n* refactor(agent): bound the answer type to Struct | BaseModel\n\nThe bound lives under TYPE_CHECKING (PEP 695 bounds are lazy), so neither\nlibrary is imported at runtime. A Struct or BaseModel always names its\nvalidator, so AgentOutput loses validator= and dataclass answers.\n\n* docs(agent): generic triage example for typed answers\n\n* docs(agent): note how the answer bound behaves with one library missing\n\n* refactor(agent): build AgentSession[O] in load() instead of casting",
          "timestamp": "2026-09-14T23:47:01+02:00",
          "tree_id": "5b91285faabbc60c98dcf9f96b77ec931811a20d",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/ad0a31abab8ccd05935b0707daeda3dc35bb984f"
        },
        "date": 1789422452989,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 229.69,
            "unit": "ms",
            "range": 3.51
          },
          {
            "name": "padwan_llm.openai",
            "value": 227.87,
            "unit": "ms",
            "range": 4.22
          },
          {
            "name": "padwan_llm.otel",
            "value": 241.75,
            "unit": "ms",
            "range": 3.32
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "711cf1ac41f28e4eef84cc6708b64b087a6cce9d",
          "message": "chore(release): release 0.10.0 (#74)",
          "timestamp": "2026-09-14T23:55:31+02:00",
          "tree_id": "1508c74a0a6ee28b436b1165881af859d8b599ee",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/711cf1ac41f28e4eef84cc6708b64b087a6cce9d"
        },
        "date": 1789422961502,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 216.43,
            "unit": "ms",
            "range": 4.55
          },
          {
            "name": "padwan_llm.openai",
            "value": 215.96,
            "unit": "ms",
            "range": 2.63
          },
          {
            "name": "padwan_llm.otel",
            "value": 229.82,
            "unit": "ms",
            "range": 2.85
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3b1f8a6dd81a8359f4df9dc61a1f416da888a5a5",
          "message": "fix(otel): instrument raw calls on all OpenAI-compatible clients (#76)\n\n`complete`/`stream` were patched on OpenAIClient, but they are defined on\n_OpenAIBase, so sibling subclasses (MistralClient, and anything LLMClient\nroutes to a custom base_url) emitted no spans for the raw call path.",
          "timestamp": "2026-09-16T18:32:11+02:00",
          "tree_id": "5c6ac41c6836c0724188e8f55d25f6f95e9ddf68",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/3b1f8a6dd81a8359f4df9dc61a1f416da888a5a5"
        },
        "date": 1789576369247,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 215.55,
            "unit": "ms",
            "range": 0.92
          },
          {
            "name": "padwan_llm.openai",
            "value": 218.14,
            "unit": "ms",
            "range": 4.49
          },
          {
            "name": "padwan_llm.otel",
            "value": 234.18,
            "unit": "ms",
            "range": 9.44
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "49192ccca8905df916e0db71174f1fe86eceffaa",
          "message": "chore(release): release 0.10.1 (#77)",
          "timestamp": "2026-09-16T21:08:13+02:00",
          "tree_id": "383bfb10e59b3e8405449100abb7c96e82871e7c",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/49192ccca8905df916e0db71174f1fe86eceffaa"
        },
        "date": 1789585724715,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 185.86,
            "unit": "ms",
            "range": 1.27
          },
          {
            "name": "padwan_llm.openai",
            "value": 187.35,
            "unit": "ms",
            "range": 7.82
          },
          {
            "name": "padwan_llm.otel",
            "value": 198.36,
            "unit": "ms",
            "range": 4.79
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "29e7947401650114539a92b0f9c54dbc0184e9ba",
          "message": "chore: rename project to padwan-ai (#79)\n\n* feat: add native JEV support and weekly model tracking\n\n* refactor(typesafe): let the API validate payloads, reuse env_api_key\n\nDrop the client-side question/JSON normalizers and per-field response\nchecks; the server 422s bad input and _error_message already surfaces\nthe detail. Remove the redundant SystemOneRequest and JSONValue types,\nthe tests that covered them, and the duplicated e2e/drift docs section.\n\n* chore: rename project to padwan-ai\n\nBREAKING: import path `padwan_llm` -> `padwan_ai`, PyPI dist `padwan-llm` -> `padwan-ai`,\nconsole script `padwan-llm` -> `padwan-ai`. No compat shim is kept.\n\nAlso renamed: logger and OTel instrumentation scope (`padwan_ai`), span attribute\nnamespace (`padwan_ai.*`), MCP clientInfo.name default (`padwan-ai`), Grafana dashboard\nuid (`padwan-ai-genai`), Langfuse dev project id, docs site and repo URLs.\n\n* chore: add padwan-llm tombstone package depending on padwan-ai",
          "timestamp": "2026-09-19T23:23:01+02:00",
          "tree_id": "ab2d94d9f8a7c4ba920bb81098d7482104c5764a",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/29e7947401650114539a92b0f9c54dbc0184e9ba"
        },
        "date": 1789853016805,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 222.86,
            "unit": "ms",
            "range": 5.24
          },
          {
            "name": "padwan_ai.openai",
            "value": 219.3,
            "unit": "ms",
            "range": 17.49
          },
          {
            "name": "padwan_ai.otel",
            "value": 226.51,
            "unit": "ms",
            "range": 5.5
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bd01e4596d73165b2c121f7e0b020eca04401a1e",
          "message": "chore(release): release 0.11.0 (#80)",
          "timestamp": "2026-09-19T23:45:50+02:00",
          "tree_id": "3de39f38c0e7091d1216959fe6e385b5fa65b51c",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/bd01e4596d73165b2c121f7e0b020eca04401a1e"
        },
        "date": 1789854382348,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 171.02,
            "unit": "ms",
            "range": 1.2
          },
          {
            "name": "padwan_ai.openai",
            "value": 170.66,
            "unit": "ms",
            "range": 2.24
          },
          {
            "name": "padwan_ai.otel",
            "value": 179.09,
            "unit": "ms",
            "range": 0.92
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5590a202a99e3aaf2703b284e692dc5043698efe",
          "message": "ci(release): make the release job re-dispatchable for an existing tag (#81)",
          "timestamp": "2026-09-20T09:55:33+02:00",
          "tree_id": "41e842169f58061ede1df50301b1bb74b1e76b67",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/5590a202a99e3aaf2703b284e692dc5043698efe"
        },
        "date": 1789890977074,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 228.61,
            "unit": "ms",
            "range": 4.2
          },
          {
            "name": "padwan_ai.openai",
            "value": 226.91,
            "unit": "ms",
            "range": 1.68
          },
          {
            "name": "padwan_ai.otel",
            "value": 240.28,
            "unit": "ms",
            "range": 6.37
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "310eb63113e6984abe022a805d7a0143d5e375c3",
          "message": "docs: revamp README into a short landing page (#82)\n\n* docs: revamp README into a short landing page\n\n* docs(readme): add PyPI version, Python and CI badges\n\n* build: add trove classifiers so the PyPI Python-versions badge renders",
          "timestamp": "2026-09-20T10:21:47+02:00",
          "tree_id": "4b0a2b95485d5b5b25e2448308815bc251014df6",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/310eb63113e6984abe022a805d7a0143d5e375c3"
        },
        "date": 1789892540753,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 195.37,
            "unit": "ms",
            "range": 3.89
          },
          {
            "name": "padwan_ai.openai",
            "value": 190.69,
            "unit": "ms",
            "range": 2.14
          },
          {
            "name": "padwan_ai.otel",
            "value": 204.28,
            "unit": "ms",
            "range": 1.92
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e8bba1414b508bc92373276ac2fc89528f00b347",
          "message": "release 0.11.1 (#83)\n\n* chore(release): release 0.11.1\n\n* docs: mention TypeSafe (JEV) in the project tagline",
          "timestamp": "2026-09-20T10:29:35+02:00",
          "tree_id": "2cebcc40411c1561ef0d6f7fb86cd331cd9dc758",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/e8bba1414b508bc92373276ac2fc89528f00b347"
        },
        "date": 1789893006247,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 224.75,
            "unit": "ms",
            "range": 3.15
          },
          {
            "name": "padwan_ai.openai",
            "value": 223.74,
            "unit": "ms",
            "range": 4.74
          },
          {
            "name": "padwan_ai.otel",
            "value": 248.8,
            "unit": "ms",
            "range": 15.31
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2853d674204fde8b6b32c0888291e518e28d16c4",
          "message": "docs: mark TypeSafe (JEV) as experimental (#84)",
          "timestamp": "2026-09-20T10:38:23+02:00",
          "tree_id": "5e954c00d8a906baefd99976e75086a57646d1e4",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/2853d674204fde8b6b32c0888291e518e28d16c4"
        },
        "date": 1789893536189,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 231.46,
            "unit": "ms",
            "range": 4.06
          },
          {
            "name": "padwan_ai.openai",
            "value": 223.12,
            "unit": "ms",
            "range": 4.78
          },
          {
            "name": "padwan_ai.otel",
            "value": 237.39,
            "unit": "ms",
            "range": 3.53
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d176383a043b78c88b2559273c4a0f4663a80cf1",
          "message": "feat: add embeddings for every provider (#85)\n\n* feat: add embeddings for every provider\n\nLift `fetch_embeddings` into the OpenAI-compatible base (OpenAI, Mistral,\nGrok, custom endpoints), add a native Gemini implementation and a Voyage AI\nclient (the embeddings provider Anthropic recommends). Every method shares\none signature: `fetch_embeddings(input, model=None, *, dimensions=None,\nextra_params=None)` returning the raw provider payload.\n\n- `padwan_ai.vectors(resp, provider)` extracts vectors in input order from\n  either payload shape (Gemini is ordered by contract, OpenAI-shaped is\n  sorted by `index`)\n- `OpenAIEmbeddingModel`, `GeminiEmbeddingModel`, `VoyageModel` Literals;\n  `LLMClient` routes `text-embedding-*` and `voyage-*` ids\n- otel instruments `fetch_embeddings` on `_OpenAIBase` and `GeminiClient`;\n  the span keeps the client's default model when `model=` is omitted\n- drift report tracks OpenAI and Gemini embedding models\n- docs matrices distinguish \"not implemented yet\" (❌) from \"provider has\n  no such API\" (➖)\n- OpenAI TypedDicts regenerated with `/embeddings`; Mistral's dropped\n\nBREAKING CHANGE: `MistralClient.fetch_embeddings` no longer defaults to\n`mistral-embed`; set `model=` on the client or the call.\n\n* test(e2e): voyage usage can report zero tokens\n\n* docs: mention voyage in otel intro, use vectors() in voyage page\n\n* feat(otel): emit the semconv recommended embeddings attributes\n\nDedicated fetch_embeddings wrapper: gen_ai.embeddings.dimension.count, gen_ai.request.encoding_formats, gen_ai.response.model and gen_ai.usage.input_tokens (also recorded on gen_ai.client.token.usage). The batch wrapper drops its unused model_param.\n\n* feat(otel): derive embeddings dimension count from the returned vectors\n\n* fix(ci): normalise import benchmarks against interpreter startup\n\nRunner-class variance scaled every import time by the same factor (cv ~12%\nacross master runs), tripping the 120% gate 15 times in 65 runs. Each import\nis now reported as a multiple of bare interpreter startup, so machine speed\ncancels out (cv ~2%, worst consecutive ratio 1.45 down to 1.06).\n\nThe version matrix also collapses into a single job, so the action posts one\ntable covering every Python version instead of one comment per version.",
          "timestamp": "2026-09-20T20:23:36+02:00",
          "tree_id": "13d6eb9a2b7c2e7e536cb1493b4f5732166a447e",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/d176383a043b78c88b2559273c4a0f4663a80cf1"
        },
        "date": 1789928949178,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade) [3.13]",
            "value": 9.609,
            "unit": "x startup",
            "range": 0.074
          },
          {
            "name": "padwan_ai (facade) [3.15]",
            "value": 2.271,
            "unit": "x startup",
            "range": 0.037
          },
          {
            "name": "padwan_ai.openai [3.13]",
            "value": 9.803,
            "unit": "x startup",
            "range": 0.247
          },
          {
            "name": "padwan_ai.openai [3.15]",
            "value": 8.788,
            "unit": "x startup",
            "range": 0.171
          },
          {
            "name": "padwan_ai.otel [3.13]",
            "value": 10.459,
            "unit": "x startup",
            "range": 0.155
          },
          {
            "name": "padwan_ai.otel [3.15]",
            "value": 10.297,
            "unit": "x startup",
            "range": 0.103
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dd2ad918a59e696079883fea055491d164b4a1cb",
          "message": "fix(ci): benchmark imports in a minimal environment (#86)\n\n* fix(ci): benchmark imports in a minimal environment\n\nThe perf job synced --all-extras --all-groups (178 packages) to time three\nimports that need 24. The 3.15 prerelease has no wheels for the dev-group\nnative packages, so every run rebuilt pydantic-core, pandas, pyyaml, jiter,\nmsgspec and markupsafe from source (3m33s), and setup-uv skips saving its\ncache on a key hit, so the build was discarded each run.\n\nSyncing only the otel extra removes every source build. bench-imports.sh now\nhonours a preset PY, since its own uv run would re-add the default groups to\nthe lean environment.\n\nBaselines drop by about 6%: __init__ calls importlib.metadata.version() at\nimport time, which scans every installed dist-info.\n\n* fix(ci): report benchmark times in ms, grouped by version\n\nPrefix rows with the Python version so each version's benchmarks are\nadjacent, and rescale the startup-normalised ratio by a reference startup\nconstant so the table reads in ms instead of multiples.",
          "timestamp": "2026-09-20T20:47:02+02:00",
          "tree_id": "0b8993c3490baf653931e06d88fdedef1b91798e",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/dd2ad918a59e696079883fea055491d164b4a1cb"
        },
        "date": 1789930067711,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 205,
            "unit": "ms",
            "range": 1.24
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 204.59,
            "unit": "ms",
            "range": 1.32
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 220.04,
            "unit": "ms",
            "range": 2.49
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.16,
            "unit": "ms",
            "range": 0.58
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 181.27,
            "unit": "ms",
            "range": 2.9
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 216.72,
            "unit": "ms",
            "range": 3.81
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dd85a59eb7982269b1fb663467085c949f0cb4d6",
          "message": "chore(release): release 0.12.0 (#87)",
          "timestamp": "2026-09-20T21:39:11+02:00",
          "tree_id": "fdd8867a11ef1b3d3f12ec62f2ab2245e51a8908",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/dd85a59eb7982269b1fb663467085c949f0cb4d6"
        },
        "date": 1789933199858,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 208.72,
            "unit": "ms",
            "range": 2.45
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 207.11,
            "unit": "ms",
            "range": 1.45
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 224.38,
            "unit": "ms",
            "range": 2.41
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 50.93,
            "unit": "ms",
            "range": 0.53
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 181.44,
            "unit": "ms",
            "range": 2.91
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 215.5,
            "unit": "ms",
            "range": 4.16
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1001bfb482ba018838854c98bc6e96299ec0bb02",
          "message": "fix: populate PyPI package metadata and ship py.typed (#88)\n\n* fix: populate PyPI package metadata\n\nThe PyPI page rendered blank: no summary, README, license or links. Adds\ndescription, readme, license expression and project URLs, and absolutizes\nthe two relative README links so they resolve on PyPI.\n\n* fix: ship py.typed marker\n\nThe package declares the Typing :: Typed classifier but had no marker, so\ndownstream type checkers ignored its inline annotations (PEP 561).",
          "timestamp": "2026-09-20T23:01:55+02:00",
          "tree_id": "bd7ec10b9e218347e174e2a42d5b5e47ba0534c1",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/1001bfb482ba018838854c98bc6e96299ec0bb02"
        },
        "date": 1789938160006,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 204.59,
            "unit": "ms",
            "range": 3.18
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 204.58,
            "unit": "ms",
            "range": 1.98
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 218.2,
            "unit": "ms",
            "range": 1.44
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.75,
            "unit": "ms",
            "range": 0.47
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 183.8,
            "unit": "ms",
            "range": 1.43
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 218.56,
            "unit": "ms",
            "range": 1.54
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2c2f81cd746c93287135a2e0059c404d5d0650e0",
          "message": "chore(release): release 0.12.1 (#89)",
          "timestamp": "2026-09-20T23:09:20+02:00",
          "tree_id": "e70461e9b2f60f7e792e3daf57a01ff40c744701",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/2c2f81cd746c93287135a2e0059c404d5d0650e0"
        },
        "date": 1789938605479,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 211.06,
            "unit": "ms",
            "range": 2.1
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 210.3,
            "unit": "ms",
            "range": 1.44
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 223.88,
            "unit": "ms",
            "range": 1.75
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.25,
            "unit": "ms",
            "range": 0.75
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 186.47,
            "unit": "ms",
            "range": 2.45
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 221.64,
            "unit": "ms",
            "range": 2.59
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "aeb263c70f8da6b6b7f0b08ce82352d5cf93dd26",
          "message": "chore: weekly LLM SDK refresh (#90)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: track new provider model aliases\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n* test: cover new mistral model aliases\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n* test: cover gemini live alias routing\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-09-21T19:49:18+02:00",
          "tree_id": "75a824e0cc8a572a52150595ed51bf0f5cb5814a",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/aeb263c70f8da6b6b7f0b08ce82352d5cf93dd26"
        },
        "date": 1790013006816,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 223.95,
            "unit": "ms",
            "range": 2.44
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 223.44,
            "unit": "ms",
            "range": 2.44
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 243.09,
            "unit": "ms",
            "range": 1.85
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.5,
            "unit": "ms",
            "range": 1.08
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 196.78,
            "unit": "ms",
            "range": 1.54
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 236.44,
            "unit": "ms",
            "range": 1.83
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bb7f69a43c164a435df1fb37f240e35b236c3e8b",
          "message": "fix: adopt urllib3-future fixes and preserve MCP cancellation (#92)\n\n* fix: adopt urllib3-future realtime and retry fixes\n\n* style: format Gemini retry method\n\n* fix: preserve MCP cancellation and update reasoning tests\n\n* fix: route SSE through a cancellation-preserving extension\n\nSubclass urllib3-future's async SSE extension under the sse+ai scheme so\ntask cancellation propagates instead of returning None\n(jawah/urllib3.future#419). Compare cancelling() to its pre-call value\nsince urllib3-future's Timeout leaks cancel requests. Inline Gemini's\nalt=sse query: niquests drops params on custom SSE schemes.\n\n* test: import urllib3 webextensions directly for pyright",
          "timestamp": "2026-09-23T20:23:21+02:00",
          "tree_id": "8a7be01a79c4686032552d9aadedcda7da47849c",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/bb7f69a43c164a435df1fb37f240e35b236c3e8b"
        },
        "date": 1790187851036,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 206.59,
            "unit": "ms",
            "range": 1.15
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 206.53,
            "unit": "ms",
            "range": 0.74
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 221.2,
            "unit": "ms",
            "range": 1.44
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.38,
            "unit": "ms",
            "range": 1.97
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 187.85,
            "unit": "ms",
            "range": 3.3
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 216.52,
            "unit": "ms",
            "range": 1.48
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2996148b99bb4522003c918bb4ebd01f3719718e",
          "message": "ci: run e2e on label or dispatch, parallelized per test file (#96)",
          "timestamp": "2026-09-23T22:01:59+02:00",
          "tree_id": "e48e99bcbf36a446f4ae9af166f3351664b83f3a",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/2996148b99bb4522003c918bb4ebd01f3719718e"
        },
        "date": 1790193774555,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 207.7,
            "unit": "ms",
            "range": 5.31
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 212.8,
            "unit": "ms",
            "range": 3.23
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 230.75,
            "unit": "ms",
            "range": 18.05
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.83,
            "unit": "ms",
            "range": 1.7
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 203.63,
            "unit": "ms",
            "range": 39.52
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 229.2,
            "unit": "ms",
            "range": 10.61
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "337a8ea3698955ccd7bb13801d8aec023c49c777",
          "message": "chore: move observability recipes into a just module (#97)\n\nMoves otel/langfuse recipes to bin/observability/justfile (just obs::<recipe>) and replaces inline bash with scripts.",
          "timestamp": "2026-09-23T22:05:28+02:00",
          "tree_id": "e636b803763ab3a808dec80fc6a9dc29c168f445",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/337a8ea3698955ccd7bb13801d8aec023c49c777"
        },
        "date": 1790193979795,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 220.85,
            "unit": "ms",
            "range": 10.45
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 212,
            "unit": "ms",
            "range": 3.05
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 232.73,
            "unit": "ms",
            "range": 2.34
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.29,
            "unit": "ms",
            "range": 2.66
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 190.87,
            "unit": "ms",
            "range": 10.79
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 226.97,
            "unit": "ms",
            "range": 6.45
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "june.bug4@proton.me",
            "name": "JwinPBE",
            "username": "jwinpbe"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9de04963903d49795811f8fd41d5d7506bee6a92",
          "message": "Expand reasoning_content check to accept vllm reasoning deltas (#94)\n\n* Expand reasoning_content check to accept vllm reasoning deltas\n\n* test: add vLLM e2e test for reasoning deltas\n\nAdds just e2e-vllm / vllm-up / vllm-down to run it against a local vLLM server.\n\n* ci: run vLLM e2e as its own job, skipped unless VLLM_BASE_URL is set\n\n* test: run vLLM e2e server in Docker, simplify thought payload docstring\n\n* test: run vLLM e2e server via docker compose with healthcheck\n\n* ci: drop vLLM e2e job, run it locally with just e2e-vllm\n\n* chore: add --full to just e2e to also run vLLM tests\n\n* docs: document vLLM reasoning via on_thought\n\n---------\n\nCo-authored-by: Julien Brayere <julien.brayere@obitrain.com>",
          "timestamp": "2026-09-23T23:01:07+02:00",
          "tree_id": "88d93eb1eaafa99de532ad65e512ec7b817faa0e",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/9de04963903d49795811f8fd41d5d7506bee6a92"
        },
        "date": 1790197317258,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 210.71,
            "unit": "ms",
            "range": 1.26
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 210.53,
            "unit": "ms",
            "range": 1.96
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 224.5,
            "unit": "ms",
            "range": 1.43
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.57,
            "unit": "ms",
            "range": 0.81
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 185.12,
            "unit": "ms",
            "range": 3.5
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 221.55,
            "unit": "ms",
            "range": 2.81
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "33b1987cf610b31c96c2e8b15c752e3260cef870",
          "message": "feat(gemini): add text-to-speech via generate_speech (#95)\n\n* feat(gemini): add text-to-speech via generate_speech\n\nSupports Gemini 3.8 TTS models, single and multi-speaker (per-line speechMetadata).\n\n* docs: list Gemini text-to-speech in feature overviews\n\n* feat(drift): track Gemini TTS models and speech TypedDict fields\n\n* style: format TTS docs example\n\n* test: compare full Gemini Live speechConfig",
          "timestamp": "2026-09-23T23:40:54+02:00",
          "tree_id": "93c063e4f41843eb7ade535653afb31b48005963",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/33b1987cf610b31c96c2e8b15c752e3260cef870"
        },
        "date": 1790199704555,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 226.76,
            "unit": "ms",
            "range": 5.13
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 223.89,
            "unit": "ms",
            "range": 2.58
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 245.16,
            "unit": "ms",
            "range": 8.92
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.44,
            "unit": "ms",
            "range": 0.7
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 206.39,
            "unit": "ms",
            "range": 5.79
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 247.56,
            "unit": "ms",
            "range": 5.46
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8ee9b3d90e5aa4eefebd0718532584b3a4d3a780",
          "message": "fix: align docs with code and fix bugs found in review (#98)\n\n* fix(openai): never send OPENAI_API_KEY to a non-OpenAI base_url\n\nCustom endpoints without api_key now fall back to PADWAN_API_KEY, then \"no-key-required\".\n\n* fix(mcp): send progress tokens, cancel in-flight requests, await async on_mcp_connect\n\nAlso warn when the GET listener gives up after max reconnect failures.\n\n* fix(grok): forward the full request body in batch requests\n\n* docs: align docs with code, add nav icons\n\n* docs: keep code-block comments within ruff line length\n\n* test(mcp): type progress callbacks as ProgressEvent\n\n* docs(mcp): clarify _cancel_on_abort contract\n\n* refactor(mcp): type tools/call params as TypedDict",
          "timestamp": "2026-09-23T23:59:54+02:00",
          "tree_id": "ded5d0772a5ab8f1ac44151d342632a6b26bd64c",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/8ee9b3d90e5aa4eefebd0718532584b3a4d3a780"
        },
        "date": 1790200844327,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 213.23,
            "unit": "ms",
            "range": 6.81
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 224.36,
            "unit": "ms",
            "range": 22.58
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 263.17,
            "unit": "ms",
            "range": 20.46
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 50.34,
            "unit": "ms",
            "range": 1.69
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 181.99,
            "unit": "ms",
            "range": 5.55
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 207.61,
            "unit": "ms",
            "range": 6.19
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d0d260557205e64ebedb64b02f7dbdd7a7148a83",
          "message": "chore(release): release 0.13.0 (#99)",
          "timestamp": "2026-09-24T00:05:27+02:00",
          "tree_id": "d6c93600ff8d716c4285dd95dbf0128404c00042",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/d0d260557205e64ebedb64b02f7dbdd7a7148a83"
        },
        "date": 1790201181115,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 209.06,
            "unit": "ms",
            "range": 2.54
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 215.37,
            "unit": "ms",
            "range": 7.72
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 223.27,
            "unit": "ms",
            "range": 2.86
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.87,
            "unit": "ms",
            "range": 0.75
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 185.16,
            "unit": "ms",
            "range": 2.09
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 220.37,
            "unit": "ms",
            "range": 2.76
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "662a6f5914c1790cf0e588eabfc52dc1eab6fbbc",
          "message": "docs: add TTS column to provider matrices (#100)",
          "timestamp": "2026-09-24T00:15:07+02:00",
          "tree_id": "4ea282e3f8b8de5597127dd163d5c02c20757a47",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/662a6f5914c1790cf0e588eabfc52dc1eab6fbbc"
        },
        "date": 1790201773190,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 202.99,
            "unit": "ms",
            "range": 1.07
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 202.1,
            "unit": "ms",
            "range": 1.07
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 217.88,
            "unit": "ms",
            "range": 1.94
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.26,
            "unit": "ms",
            "range": 0.8
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 181.87,
            "unit": "ms",
            "range": 2.54
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 220.08,
            "unit": "ms",
            "range": 3.28
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d91f8c7f50cdd1033762f9027103bc0f68510e87",
          "message": "ci: run import benchmark on PRs only with the import-bench label (#102)",
          "timestamp": "2026-09-24T18:21:47+02:00",
          "tree_id": "4ed908eecda00d4c58d1ec4a3ebe2112142c2b83",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/d91f8c7f50cdd1033762f9027103bc0f68510e87"
        },
        "date": 1790266961533,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 212.8,
            "unit": "ms",
            "range": 3.09
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 211.84,
            "unit": "ms",
            "range": 2.22
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 229.68,
            "unit": "ms",
            "range": 3.42
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.67,
            "unit": "ms",
            "range": 2.05
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 186,
            "unit": "ms",
            "range": 6.13
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 222.63,
            "unit": "ms",
            "range": 5.53
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b8ff26cb2422c4898d57d6c226ab74e42cc6e784",
          "message": "docs: add AGENTS.md and CONTRIBUTING.md (#101)\n\n* docs: add AGENTS.md and CONTRIBUTING.md\n\n* docs: add issue, AI-use and release guidance to CONTRIBUTING.md",
          "timestamp": "2026-09-24T18:25:18+02:00",
          "tree_id": "4e78ace85e3a79ae83ca947e133dcb3626ec4591",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/b8ff26cb2422c4898d57d6c226ab74e42cc6e784"
        },
        "date": 1790267181729,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 208.43,
            "unit": "ms",
            "range": 4.18
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 212.37,
            "unit": "ms",
            "range": 9.47
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 223.89,
            "unit": "ms",
            "range": 6.54
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 50.8,
            "unit": "ms",
            "range": 1.2
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 189.88,
            "unit": "ms",
            "range": 4.56
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 220.05,
            "unit": "ms",
            "range": 2.76
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3dde7d7b83cb7b2eb4256d7366225e1d120d69d1",
          "message": "fix: require urllib3-future>=2.25.901 (#108)",
          "timestamp": "2026-09-28T21:53:51+02:00",
          "tree_id": "8771c69553a8090dd127995502215fadbf8b4678",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/3dde7d7b83cb7b2eb4256d7366225e1d120d69d1"
        },
        "date": 1790625280311,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 217.38,
            "unit": "ms",
            "range": 8.93
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 211.55,
            "unit": "ms",
            "range": 1.76
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 228.31,
            "unit": "ms",
            "range": 5.93
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.45,
            "unit": "ms",
            "range": 0.79
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 184.24,
            "unit": "ms",
            "range": 1.79
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 220.64,
            "unit": "ms",
            "range": 1.71
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6bb517fe04d68bb2df127a928449085e8ef40951",
          "message": "test: rename SSE pending-cancel case and drop redundant comment (#109)",
          "timestamp": "2026-09-28T21:57:30+02:00",
          "tree_id": "56b8d142c2e233590fb5b49e8cf3779d87c2c7cc",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/6bb517fe04d68bb2df127a928449085e8ef40951"
        },
        "date": 1790625499665,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 202.87,
            "unit": "ms",
            "range": 2.85
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 206.51,
            "unit": "ms",
            "range": 3.98
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 218.74,
            "unit": "ms",
            "range": 1.41
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.78,
            "unit": "ms",
            "range": 1.36
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 179.61,
            "unit": "ms",
            "range": 4.91
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 224.96,
            "unit": "ms",
            "range": 3.81
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b61e1a58e6a3a250885f0854442badd7b653c0c4",
          "message": "feat(langfuse): export SpanAdapter and SpanFilter (#105)\n\n* feat(langfuse): export SpanAdapter and SpanFilter\n\nA second Langfuse client on the same tracer provider (another project, its\nown exporter) needs the same mapping and span selection instrument() uses;\nboth were private, so callers imported _SpanAdapter or re-coded the filter.\n\n* docs(langfuse): the second client flushes at exit; flush() sends earlier\n\n---------\n\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-09-29T21:21:25+02:00",
          "tree_id": "9d042d078b528b597e9f33d6a1e86835cf70d7ee",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/b61e1a58e6a3a250885f0854442badd7b653c0c4"
        },
        "date": 1790709747622,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 205.2,
            "unit": "ms",
            "range": 0.78
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 206.01,
            "unit": "ms",
            "range": 1.33
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 219.41,
            "unit": "ms",
            "range": 1.08
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.14,
            "unit": "ms",
            "range": 0.33
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 181.23,
            "unit": "ms",
            "range": 0.9
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 217.34,
            "unit": "ms",
            "range": 1.05
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "685fb9deec60e05dbedf59e6bf2cc2c240e3cae7",
          "message": "chore: weekly LLM SDK refresh (#107)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: add drifted model literals\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n* fix(embeddings): decode base64 embeddings in vectors()\n\nThe regenerated OpenAI types allow a base64 string per item (encoding_format=\"base64\");\nvectors() now decodes it to floats instead of returning the string.\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-09-29T21:40:23+02:00",
          "tree_id": "c6dfc5f4ff6113825e4f5c8b39ee1069b722021e",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/685fb9deec60e05dbedf59e6bf2cc2c240e3cae7"
        },
        "date": 1790710886219,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 210.23,
            "unit": "ms",
            "range": 3.61
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 211.34,
            "unit": "ms",
            "range": 6.24
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 222.7,
            "unit": "ms",
            "range": 4.57
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 50.78,
            "unit": "ms",
            "range": 0.93
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 178.94,
            "unit": "ms",
            "range": 2.83
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 225.61,
            "unit": "ms",
            "range": 3.6
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8270b31bed8d2a00734b40e4090263f473ff0755",
          "message": "fix(agent): log a tool failure's traceback only on DEBUG (#106)\n\n* fix(agent): log a tool failure's traceback only on DEBUG\n\nThe model already gets the error as the tool result and usually recovers,\nso a full traceback at WARNING for every tool error floods the logs. The\nfailure stays one WARNING line; the traceback is attached when the\npadwan_ai logger is enabled for DEBUG.\n\n* test(agent): fold the tool-failure log check into test_tool_failure_modes\n\n---------\n\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-09-29T21:41:12+02:00",
          "tree_id": "060602c7ebdb6d410286fb21cbbfa03fd886ad6f",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/8270b31bed8d2a00734b40e4090263f473ff0755"
        },
        "date": 1790710929930,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 219.22,
            "unit": "ms",
            "range": 5.38
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 217.13,
            "unit": "ms",
            "range": 3.65
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 233.32,
            "unit": "ms",
            "range": 10.6
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.9,
            "unit": "ms",
            "range": 1.89
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 189.41,
            "unit": "ms",
            "range": 3.77
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 232.02,
            "unit": "ms",
            "range": 4.97
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bfc6571b50d2df582fdb81d1af70f97d142df651",
          "message": "feat(agent): say why a run ended: OutputError.reason and AgentSession.stop_reason (#103)\n\n* feat(agent): say why a run ended: OutputError.reason and AgentSession.stop_reason\n\nA typed run's OutputError now carries reason (invalid_answer, text_answer,\nround_limit), so callers stop matching on its message. A text run records\nstop_reason (answer, empty, round_limit), since it yields a placeholder for\nan empty answer and for the round limit instead of raising.\n\n* fix(agent): leave stop_reason None when a typed run raises OutputError\n\nA text answer without submit left stop_reason at \"answer\" and the round limit at\n\"round_limit\" although the run failed; the failure is on OutputError.reason.\n\n---------\n\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-09-29T21:48:41+02:00",
          "tree_id": "798bbcf4ddbe1d9d7322c534b467c8eba33067d1",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/bfc6571b50d2df582fdb81d1af70f97d142df651"
        },
        "date": 1790711375778,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 208.32,
            "unit": "ms",
            "range": 1.15
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 207.55,
            "unit": "ms",
            "range": 0.9
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 221.98,
            "unit": "ms",
            "range": 1.24
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.22,
            "unit": "ms",
            "range": 0.32
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 182.57,
            "unit": "ms",
            "range": 2.85
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 217.78,
            "unit": "ms",
            "range": 1.37
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "695573d1e286e29f0aeb08892fea4ba64f242a49",
          "message": "chore(release): release 0.14.0 (#110)",
          "timestamp": "2026-09-29T21:59:41+02:00",
          "tree_id": "67899254884bdc52ec042721705287e69fb1ff9a",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/695573d1e286e29f0aeb08892fea4ba64f242a49"
        },
        "date": 1790712031106,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 208.82,
            "unit": "ms",
            "range": 1.3
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 207.53,
            "unit": "ms",
            "range": 1.06
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 222.76,
            "unit": "ms",
            "range": 1.95
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.1,
            "unit": "ms",
            "range": 0.53
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 182.64,
            "unit": "ms",
            "range": 0.89
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 219.67,
            "unit": "ms",
            "range": 1.26
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "695573d1e286e29f0aeb08892fea4ba64f242a49",
          "message": "chore(release): release 0.14.0 (#110)",
          "timestamp": "2026-09-29T21:59:41+02:00",
          "tree_id": "67899254884bdc52ec042721705287e69fb1ff9a",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/695573d1e286e29f0aeb08892fea4ba64f242a49"
        },
        "date": 1790712065842,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 209.46,
            "unit": "ms",
            "range": 0.82
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 210,
            "unit": "ms",
            "range": 2.34
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 226.22,
            "unit": "ms",
            "range": 5.42
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.51,
            "unit": "ms",
            "range": 0.18
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 183.89,
            "unit": "ms",
            "range": 0.56
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 220.9,
            "unit": "ms",
            "range": 1.01
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "14a933e2defd7970125bd91798eb4e9ccc3156a3",
          "message": "chore: weekly LLM SDK refresh (#111)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* fix: accept stable model drift aliases\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-10-05T20:33:59+02:00",
          "tree_id": "e7cbcf6a076ccf074e1dcd427bec068acf1b4cee",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/14a933e2defd7970125bd91798eb4e9ccc3156a3"
        },
        "date": 1791225289355,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 223.21,
            "unit": "ms",
            "range": 2.68
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 221.98,
            "unit": "ms",
            "range": 2.02
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 238.64,
            "unit": "ms",
            "range": 4.15
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.85,
            "unit": "ms",
            "range": 1.18
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 199.59,
            "unit": "ms",
            "range": 8.59
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 242.73,
            "unit": "ms",
            "range": 4.34
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "16805fea270d61ca58fd586d182ef536a9391b76",
          "message": "fix: Anthropic bridge usage, tool-result images, otel content capture, Gemini default (#112)\n\n* fix(anthropic): exclude cache reads from input_tokens, keep tool messages contiguous, capture structured content\n\n* fix(gemini): default to gemini-3.8-flash",
          "timestamp": "2026-10-08T21:39:31+02:00",
          "tree_id": "347177fdef1f4cb2a493a486aa298aadf4d53b68",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/16805fea270d61ca58fd586d182ef536a9391b76"
        },
        "date": 1791488435886,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 213.95,
            "unit": "ms",
            "range": 3.84
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 215.17,
            "unit": "ms",
            "range": 7.08
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 228.52,
            "unit": "ms",
            "range": 3.44
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.8,
            "unit": "ms",
            "range": 0.83
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 185.72,
            "unit": "ms",
            "range": 2.68
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 226.02,
            "unit": "ms",
            "range": 2.95
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1a42e1278f415ce31cd18fb628ebc89b9baae515",
          "message": "chore(release): release 0.14.1 (#113)",
          "timestamp": "2026-10-08T21:39:55+02:00",
          "tree_id": "d80f53dd1ac837ff359202ed96460bfff6464f2a",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/1a42e1278f415ce31cd18fb628ebc89b9baae515"
        },
        "date": 1791488489497,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 216.8,
            "unit": "ms",
            "range": 4.4
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 215.06,
            "unit": "ms",
            "range": 3.55
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 233.64,
            "unit": "ms",
            "range": 5.66
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 50.74,
            "unit": "ms",
            "range": 0.7
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 188.08,
            "unit": "ms",
            "range": 2.46
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 224.91,
            "unit": "ms",
            "range": 4.22
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4dfc65b543ceb483136f59a56f08421a68b1d348",
          "message": "chore: weekly LLM SDK refresh (#115)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: add drifted provider model aliases\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-10-12T20:44:49+02:00",
          "tree_id": "56bc14abc9c36a34628ec6f89d44116c04a3dbb7",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/4dfc65b543ceb483136f59a56f08421a68b1d348"
        },
        "date": 1791830736895,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 225.38,
            "unit": "ms",
            "range": 8.52
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 224.48,
            "unit": "ms",
            "range": 5.44
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 240.96,
            "unit": "ms",
            "range": 5.18
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.77,
            "unit": "ms",
            "range": 1.63
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 200.21,
            "unit": "ms",
            "range": 6.63
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 237.35,
            "unit": "ms",
            "range": 5.77
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e161d187a82bcb0e4e5d1a6d2b35fadc41118547",
          "message": "ci: add Copilot coding agent setup steps (#122)\n\nCopilot ran on bare ubuntu-latest (Python 3.12, no uv) and could not lint, type-check or test.",
          "timestamp": "2026-10-19T18:54:54+02:00",
          "tree_id": "d5f85e0c8df028a0abb4783cc21cb39d205d97ef",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/e161d187a82bcb0e4e5d1a6d2b35fadc41118547"
        },
        "date": 1792428953284,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 220.95,
            "unit": "ms",
            "range": 2.66
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 223.68,
            "unit": "ms",
            "range": 3.02
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 237.93,
            "unit": "ms",
            "range": 1.35
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.07,
            "unit": "ms",
            "range": 0.77
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 189.25,
            "unit": "ms",
            "range": 0.64
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 227.59,
            "unit": "ms",
            "range": 1.85
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8cb34bf02ca8b3e69d16ecc4a43d2328658d24cc",
          "message": "chore: weekly LLM SDK refresh (#121)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: add Gemini 4 Argon model alias\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-10-19T18:57:24+02:00",
          "tree_id": "de5eeeaea85f4efd28a3f3128f2084bdcfbea51d",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/8cb34bf02ca8b3e69d16ecc4a43d2328658d24cc"
        },
        "date": 1792429096696,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 216.28,
            "unit": "ms",
            "range": 2.31
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 221.21,
            "unit": "ms",
            "range": 3.68
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 234.11,
            "unit": "ms",
            "range": 3.72
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.65,
            "unit": "ms",
            "range": 0.55
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 186.81,
            "unit": "ms",
            "range": 1.49
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 222.65,
            "unit": "ms",
            "range": 1.75
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7ad8bdd5c07597c840627e96a88c78e6f7c6b9b5",
          "message": "feat(openai): transcribe audio through /audio/transcriptions (#125)\n\n* feat(openai): headers= on complete() and stream() for one request\n\nA client shared by many users behind a gateway (LiteLLM's x-litellm-end-user-id and\nx-litellm-tags) has to name the user on each request; session headers are fixed when the\nclient opens, and changing them on a shared client races between users.\n\n* fix(openai): forward headers= through complete_chat and stream_chat\n\nType it as a read-only Mapping instead of niquests' HeadersType, and document that\nper-request headers replace same-named session ones.\n\n* feat(openai): stream_raw relays a chat completion's SSE bytes unchanged\n\nA backend in front of a browser that already speaks the OpenAI wire format\nhas nothing to parse: it needs the provider's bytes as they come, with the\nstatus checked before the first one so an error still maps to padwan's\nexceptions.\n\n* fix(openai): stream_raw yields bytes as they arrive and tolerates a failing close\n\nThe 8 KiB default buffered a short completion until it ended; -1 yields each chunk on arrival.\nClose is best-effort as in _iter_sse, since aborting an HTTP/2 stream can raise.\n\n* feat(openai): transcribe audio through /audio/transcriptions\n\nAn OpenAI-compatible gateway serves Whisper on the OpenAI multipart route,\nwith a prompt for spelling hints and a file name that tells the format. The\nMistral transcribe has neither, and names raw bytes \"audio\".\n\n* test(openai): run stream_raw through the existing stream tests\n\nParametrize the stream tests over stream and stream_raw instead of a separate class;\nmake_sse_resp now also serves its events as raw bytes and honours an error status.\n\n* fix(openai): keyword-only transcribe file, read off the event loop, and an e2e test\n\nfile= is keyword-only as in Mistral and is read through content._read_audio; raw bytes\nwithout a filename raise ValueError. Usage is typed, headers use RequestHeaders, and the\nmocked multipart tests give way to an e2e round trip on tests/fixtures/audio.wav.\n\n* test(e2e): commit a synthetic speech clip for the transcribe tests\n\nA 2.3 s, 16 kHz mono wav of \"Two pallets of bricks.\" generated with OpenAI TTS, so the\nOpenAI and Mistral transcribe e2e tests run in CI instead of skipping.\n\n* test(openai): check per-call headers on the chat wrappers and stream_raw only\n\ncomplete_chat and stream_chat forward to complete and stream, so their cases cover both.\n\n* docs(openai): shorten the stream_raw docstring\n\n* refactor(content): _read_audio returns a named file tuple and owns the name and mime overrides\n\ntranscribe passes it straight to niquests; the mime now always follows the name sent.\n\n---------\n\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-10-20T21:55:08+02:00",
          "tree_id": "c28f6d861c9bb6bab135f38c9ce7b20ccc1c8926",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/7ad8bdd5c07597c840627e96a88c78e6f7c6b9b5"
        },
        "date": 1792526158606,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 210.2,
            "unit": "ms",
            "range": 11.5
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 211.07,
            "unit": "ms",
            "range": 7.88
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 239.02,
            "unit": "ms",
            "range": 15.69
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.14,
            "unit": "ms",
            "range": 3.99
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 186.16,
            "unit": "ms",
            "range": 5.84
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 220.69,
            "unit": "ms",
            "range": 12.31
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "459a096689d4678f4e80fff5def1703629d60e6b",
          "message": "fix(openai): a 429 maps to TooManyRequestsError whatever its body and Retry-After (#126)\n\n* fix(openai): a 429 maps to TooManyRequestsError whatever its body and Retry-After\n\nA gateway's 429 can carry a plain-text body, which escaped as a bare\nHTTPError, and Retry-After may be an HTTP date, which crashed int(). The\ndelay is now parsed as urllib3 parses it, 60 s when unreadable.\n\n* fix(openai): share Retry-After parsing with typesafe and wait at least 1s\n\nretry_after_delay in _base replaces the two copies; a past HTTP date no longer gives a\nzero delay. The 429 tests fold into test_check_resp and cover a non-JSON 429 on stream_raw.\n\n* fix(openai): fall back to the HTTP error only when the error body is not JSON\n\nA failure reading the body now propagates instead of being reported as the HTTP status.\n\n* test: test Retry-After parsing once, through typesafe\n\nThe OpenAI table keeps only its own paths: a non-JSON 429 and a non-JSON 502.\n\n* docs(openai): one-line _raise_http_error docstring\n\n* refactor: name the 60s fallback as DEFAULT_RETRY_DELAY\n\n---------\n\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-10-20T22:34:30+02:00",
          "tree_id": "c71b3435aa5dbb58780f335ae8cfd2ee156ff84d",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/459a096689d4678f4e80fff5def1703629d60e6b"
        },
        "date": 1792528518558,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 207.51,
            "unit": "ms",
            "range": 1.07
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 206.84,
            "unit": "ms",
            "range": 1.06
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 221.32,
            "unit": "ms",
            "range": 1.28
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.28,
            "unit": "ms",
            "range": 0.22
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 183.19,
            "unit": "ms",
            "range": 12.76
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 220.8,
            "unit": "ms",
            "range": 5.61
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1de693f82f13cd80df37f45d467aa0721a05e09e",
          "message": "chore(release): release 0.15.0 (#127)",
          "timestamp": "2026-10-20T22:43:36+02:00",
          "tree_id": "e17b39c27bee2eda149682dfd268f672639992c5",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/1de693f82f13cd80df37f45d467aa0721a05e09e"
        },
        "date": 1792529075072,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 220.45,
            "unit": "ms",
            "range": 4.48
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 217.01,
            "unit": "ms",
            "range": 2.71
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 239.84,
            "unit": "ms",
            "range": 7.56
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.82,
            "unit": "ms",
            "range": 1.56
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 179.73,
            "unit": "ms",
            "range": 2.95
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 218.11,
            "unit": "ms",
            "range": 6.9
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "56709111d0ce46d840484d5fb2db992978976f9e",
          "message": "ci: skip the research group when installing test dependencies (#128)\n\njupyter and pandas are unused by the suite; on a cold 3.15 cache pandas builds from source.",
          "timestamp": "2026-10-20T23:54:07+02:00",
          "tree_id": "bc669e635f12a6debdcedbab5135e31766dfd0e3",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/56709111d0ce46d840484d5fb2db992978976f9e"
        },
        "date": 1792533298544,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 228,
            "unit": "ms",
            "range": 11.18
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 223.52,
            "unit": "ms",
            "range": 1.45
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 239.69,
            "unit": "ms",
            "range": 4.81
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.57,
            "unit": "ms",
            "range": 2.67
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 191.49,
            "unit": "ms",
            "range": 4.59
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 234.64,
            "unit": "ms",
            "range": 6.58
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2e33ca14d8ede0f572b2d81f4dc17fe370cdf196",
          "message": "ci(docs): preview docs PRs on GitHub Pages (#132)\n\n* ci(docs): preview docs PRs on GitHub Pages\n\nPublish master to the gh-pages root and each docs PR under pr-preview/pr-<N>/, with the preview link commented on the PR and removed on close, as in sre-config.\n\n* ci(docs): mark what a docs PR changes on its preview\n\nPort of sre-config's docs/pr-preview marking to the Material theme: added and changed blocks are highlighted on the preview pages, the sidebar badges changed pages, and the sticky PR comment lists each changed, new or removed page.\n\n* ci(docs): keep the benchmark history when deploying the site root\n\nperf.yml stores import benchmark results under dev/bench on gh-pages; the master deploy must not clean them.",
          "timestamp": "2026-10-22T23:28:17+02:00",
          "tree_id": "2f8c6a6924069805ae6c7582b81ebf00d3a7d866",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/2e33ca14d8ede0f572b2d81f4dc17fe370cdf196"
        },
        "date": 1792704548211,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 225.84,
            "unit": "ms",
            "range": 2.62
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 225.37,
            "unit": "ms",
            "range": 2.95
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 242.84,
            "unit": "ms",
            "range": 5.4
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.82,
            "unit": "ms",
            "range": 0.93
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 201.53,
            "unit": "ms",
            "range": 8.51
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 237.43,
            "unit": "ms",
            "range": 5.81
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f7258afafdacb84a4f59e8751cbc37a56e95cb5b",
          "message": "ci(docs): ignore the benchmark history when listing removed pages (#133)",
          "timestamp": "2026-10-23T14:34:41+02:00",
          "tree_id": "2ec479b44ac57780a9150502c1572de3d14dfcb3",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/f7258afafdacb84a4f59e8751cbc37a56e95cb5b"
        },
        "date": 1792758961870,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 216.09,
            "unit": "ms",
            "range": 2.57
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 228.33,
            "unit": "ms",
            "range": 16.96
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 248.74,
            "unit": "ms",
            "range": 6.52
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 50.66,
            "unit": "ms",
            "range": 1.41
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 186.06,
            "unit": "ms",
            "range": 7.77
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 229.46,
            "unit": "ms",
            "range": 13.85
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ab8e1fe358569c482ed14b7b4f8e8d01375b39e5",
          "message": "feat(openai): transcribe takes extra_params for provider-only form fields (#129)\n\n* feat(openai): transcribe takes extra_params for provider-only form fields\n\nA gateway reads its trace fields (LiteLLM's metadata, as a JSON string) from\nthe multipart form, which transcribe had no way to add to.\n\n* feat(openai): transcribe extra_params accepts pairs to repeat a form field\n\n---------\n\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-10-23T15:08:24+02:00",
          "tree_id": "a958f8b196e56b5e99824bd6d1210420ad087974",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/ab8e1fe358569c482ed14b7b4f8e8d01375b39e5"
        },
        "date": 1792760962875,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 215.97,
            "unit": "ms",
            "range": 3.6
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 219.53,
            "unit": "ms",
            "range": 5.72
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 230.89,
            "unit": "ms",
            "range": 3.47
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.67,
            "unit": "ms",
            "range": 0.9
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 191.67,
            "unit": "ms",
            "range": 2.32
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 233.91,
            "unit": "ms",
            "range": 2.39
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a94e07057116af350bea4de115ef642f16816bf4",
          "message": "fix: cap the Retry-After wait before a 429 is raised (#130)\n\nurllib3 slept the full Retry-After of a 429 or 503 (a gateway token bucket\nanswered with its refill time, up to 21 min) before the client ever saw it.\nEvery client Retry now caps that sleep at 30 s; the TooManyRequestsError\nkeeps the server's real retry_delay.",
          "timestamp": "2026-10-23T15:10:48+02:00",
          "tree_id": "f9587faee330ec24e441b778e39e3d3552012c50",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/a94e07057116af350bea4de115ef642f16816bf4"
        },
        "date": 1792761099209,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 227.52,
            "unit": "ms",
            "range": 3.6
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 224.35,
            "unit": "ms",
            "range": 1.64
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 243.17,
            "unit": "ms",
            "range": 4.88
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.81,
            "unit": "ms",
            "range": 2.89
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 195.52,
            "unit": "ms",
            "range": 2.82
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 227.53,
            "unit": "ms",
            "range": 3.2
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "49d187567cc663638515ec098b9aa667c643c196",
          "message": "fix(mcp): open the notification GET stream without a read timeout (#131)\n\n* fix(mcp): open the notification GET stream without a read timeout\n\nThe listener inherited niquests' 30 s default read timeout, so a quiet streamable-HTTP server timed the GET out every ~33 s, each logged as a listener error with a ReadTimeout trace and reconnected.\n\n* test(mcp): assert the listener read timeout in the existing reconnect test",
          "timestamp": "2026-10-23T15:20:08+02:00",
          "tree_id": "fd6026ff11b233e115942bdf2a8ce461f5044a77",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/49d187567cc663638515ec098b9aa667c643c196"
        },
        "date": 1792761667864,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 226.7,
            "unit": "ms",
            "range": 1.48
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 226.79,
            "unit": "ms",
            "range": 2.5
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 241.81,
            "unit": "ms",
            "range": 2.15
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.02,
            "unit": "ms",
            "range": 0.7
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 188.19,
            "unit": "ms",
            "range": 2.36
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 226.04,
            "unit": "ms",
            "range": 3.81
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "163cbee24784da3326bf501cbb63bb42ef16632a",
          "message": "docs(agents): a new case of an existing behaviour extends its parametrized test (#134)",
          "timestamp": "2026-10-23T15:21:57+02:00",
          "tree_id": "9c4d32994e83a1378804d5873247e5267c8356cc",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/163cbee24784da3326bf501cbb63bb42ef16632a"
        },
        "date": 1792761782920,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 223.68,
            "unit": "ms",
            "range": 4.69
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 226.85,
            "unit": "ms",
            "range": 3.85
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 232.65,
            "unit": "ms",
            "range": 8.19
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.15,
            "unit": "ms",
            "range": 1.17
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 188.47,
            "unit": "ms",
            "range": 2.86
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 226.99,
            "unit": "ms",
            "range": 3.94
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "04376785f5457763007725efd93bfb055567ea6b",
          "message": "docs(agents): logos on the msgspec and pydantic validator tabs (#136)",
          "timestamp": "2026-10-23T15:31:08+02:00",
          "tree_id": "e9a0b4fb2b733b3e3c9f40a08bcb1bc2f45384b1",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/04376785f5457763007725efd93bfb055567ea6b"
        },
        "date": 1792762324575,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 218.66,
            "unit": "ms",
            "range": 3.2
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 238.33,
            "unit": "ms",
            "range": 22.44
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 242.2,
            "unit": "ms",
            "range": 8.08
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.72,
            "unit": "ms",
            "range": 3.65
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 205.7,
            "unit": "ms",
            "range": 11.65
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 260.05,
            "unit": "ms",
            "range": 9.69
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "59a99892268e8da9c583d4e82ae72c535bbed93f",
          "message": "fix(openai): transcribe rejects extra_params that set a named argument (#135)",
          "timestamp": "2026-10-23T15:42:19+02:00",
          "tree_id": "eb0272683be3ad431699fdfd9821ad7c420a1d40",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/59a99892268e8da9c583d4e82ae72c535bbed93f"
        },
        "date": 1792763005996,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 221.47,
            "unit": "ms",
            "range": 1.27
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 221.19,
            "unit": "ms",
            "range": 1.64
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 236.53,
            "unit": "ms",
            "range": 1.99
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.83,
            "unit": "ms",
            "range": 0.45
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 190.57,
            "unit": "ms",
            "range": 3.33
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 228.69,
            "unit": "ms",
            "range": 1.68
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fa6f5b1f772e07130a416d0865a06b7a65c8a05e",
          "message": "feat(elevenlabs): add ElevenLabs text-to-speech and speech-to-text client (#116)\n\n* feat(elevenlabs): add ElevenLabs text-to-speech and speech-to-text client\n\nStandalone ElevenLabsClient with generate_speech and transcribe (Scribe).\nShare the session lifecycle with TypeSafeClient via StandaloneClientMixin and\nnon-blocking audio file reads via _read_audio (also used by Mistral transcribe).\nCross-check request/response types against the elevenlabs SDK and add an\nElevenLabs TTS section to the weekly model drift check.\n\n* ci(e2e): pass ELEVENLABS_API_KEY to the e2e job\n\n* fix(elevenlabs): share the standalone status check and retry policy, align transcribe with the other clients\n\n- 429 maps through retry_after_delay (HTTP dates, non-JSON bodies) via StandaloneClientMixin._check_resp_status\n- retry connection errors and 5xx only, as the chat clients do; a 429 is raised, not retried\n- transcribe: keyword-only file=, language= (not language_code=), filename=/content_type= passthrough\n- model parameters keep their Literal types; docs mark the client experimental",
          "timestamp": "2026-10-23T16:51:35+02:00",
          "tree_id": "559b9a91b940bf6f1ef88190ecadbf4ec0401f4f",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/fa6f5b1f772e07130a416d0865a06b7a65c8a05e"
        },
        "date": 1792767159990,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 221.8,
            "unit": "ms",
            "range": 4.28
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 221.35,
            "unit": "ms",
            "range": 0.99
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 236.62,
            "unit": "ms",
            "range": 0.92
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.89,
            "unit": "ms",
            "range": 0.55
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 190.46,
            "unit": "ms",
            "range": 1.21
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 228.76,
            "unit": "ms",
            "range": 1.17
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": false,
          "id": "0d88082b5c707cc58e05ae9bc707066b0a0c7089",
          "message": "feat(gradium): add Gradium text-to-speech and speech-to-text client (#117)\n\n* feat(gradium): add Gradium text-to-speech and speech-to-text client\n\nStandalone GradiumClient on StandaloneClientMixin: generate_speech over the TTS\nREST endpoint and transcribe over the ASR endpoint (NDJSON folded into segments).\nRequest fields are cross-checked against the gradium SDK.\n\n* ci(e2e): pass GRADIUM_API_KEY to the e2e job\n\n* fix(gradium): send json_config as a JSON string, map 429, reuse the standalone status check\n\nThe API and its SDK take TTS json_config as a string; a dict was rejected or ignored.\ntranscribe takes file= keyword-only like the other clients; malformed NDJSON raises LLMError.\n\n* docs: label the ElevenLabs and Gradium clients experimental like TypeSafe",
          "timestamp": "2026-10-23T17:31:10+02:00",
          "tree_id": "3e9c382e00bddbfcca499ba40c4aee87e4b7cdfc",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/0d88082b5c707cc58e05ae9bc707066b0a0c7089"
        },
        "date": 1792769520244,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 235.14,
            "unit": "ms",
            "range": 9.87
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 226.38,
            "unit": "ms",
            "range": 4.08
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 238.25,
            "unit": "ms",
            "range": 7.62
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.32,
            "unit": "ms",
            "range": 2.2
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 200.56,
            "unit": "ms",
            "range": 6.63
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 246.25,
            "unit": "ms",
            "range": 8.71
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "838b860fc22bac7b9ec19f877643ff828773f279",
          "message": "feat(elevenlabs): add streaming, realtime, speech-to-speech, voices, sound effects and music (#118)\n\n* feat(elevenlabs): add streaming, realtime, speech-to-speech, voices, sound effects and music\n\nStreaming TTS and speech-to-speech over REST, WebSocket TTS (stream-input) and\nrealtime Scribe STT clients, voice management, sound effects and music.\nMark the ElevenLabs client as experimental and check speech-to-speech models in\nthe weekly drift report.\n\n* fix(elevenlabs): harden stream lifecycles and rename ElevenLabsAudio\n\nAdd WsConnection.pump: the sender task is always cancelled and awaited, send\nerrors propagate, and a server close before the final message raises instead\nof hanging on a pending input source. Close nested streams promptly with\naclosing. Rename ElevenLabsSpeech to ElevenLabsAudio (also returned for sound\neffects and music) and register elevenlabs as an otel provider name.\n\n* fix(elevenlabs): reuse the standalone status checks, map realtime throttling, chain pump errors\n\n- HTTP and stream status checks come from StandaloneClientMixin (429 via retry_after_delay, 5xx-only retries)\n- realtime rate_limited/commit_throttled/queue_overflow frames raise TooManyRequestsError; is_committed accepts the\n  timestamped variant; the session_started wait has a deadline (WsConnection.wait_for)\n- pump reports the send failure when the reader then dies on the closed socket\n- scribe_v2_realtime gets its own Literal; transcribe takes file= keyword-only, language=, filename=/content_type=\n- voice cloning and music e2e tests are opt-in (-m 'e2e and paid'); matrices show realtime as supported",
          "timestamp": "2026-10-23T17:35:50+02:00",
          "tree_id": "cea88974ba45fbebde9b46148120c28a9e08ad62",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/838b860fc22bac7b9ec19f877643ff828773f279"
        },
        "date": 1792769804564,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 234.68,
            "unit": "ms",
            "range": 3.34
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 235.51,
            "unit": "ms",
            "range": 6.04
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 248.46,
            "unit": "ms",
            "range": 4.4
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 55.81,
            "unit": "ms",
            "range": 2.62
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 215.38,
            "unit": "ms",
            "range": 9.88
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 254.93,
            "unit": "ms",
            "range": 6.93
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a882553eee1b4ca1cdf7dd5e1c13e72200ef5ca1",
          "message": "feat(gradium): add streaming, realtime TTS/STT/S2S and voice management (#119)\n\n* feat(gradium): add streaming, realtime TTS/STT/S2S and voice management\n\nStreaming TTS over REST, WebSocket TTS, STT and speech-to-speech translation\nclients, and voice management (list, get, clone, update, delete).\nMark the Gradium and ElevenLabs clients as experimental.\n\n* fix(gradium): share the hardened stream pump and register otel provider\n\nGradium realtime streams use WsConnection.pump (sender always awaited, early\nserver close raises) with aclosing for nested generators; register gradium as an\notel provider name and footnote the Realtime matrix cell.\n\n* fix(gradium): keep the shared status checks, bound the ready handshake, never resend a POST\n\n- json_config is a JSON string, 429 maps to TooManyRequestsError, malformed NDJSON raises LLMError (as in #117)\n- POSTs bill or create voices, so Gradium retries them on connection errors only; GET/PUT/DELETE keep 502-504\n- the ready wait uses WsConnection.wait_for with the client timeout instead of blocking forever\n- send_audio is append_audio, as on the ElevenLabs, OpenAI and Gemini STT connections\n- the upgrade check, the sync-iterable adapter and the API-key auth mixin are shared with ElevenLabs\n- the voice e2e test is opt-in (paid); transcribe takes file= keyword-only",
          "timestamp": "2026-10-23T17:38:06+02:00",
          "tree_id": "2ae71000d73130759f5426bc04dda2115d56c4cb",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/a882553eee1b4ca1cdf7dd5e1c13e72200ef5ca1"
        },
        "date": 1792769957490,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 241.55,
            "unit": "ms",
            "range": 2.54
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 245.01,
            "unit": "ms",
            "range": 2.41
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 260.87,
            "unit": "ms",
            "range": 3.61
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.51,
            "unit": "ms",
            "range": 0.91
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 202.86,
            "unit": "ms",
            "range": 3.55
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 237.51,
            "unit": "ms",
            "range": 2.91
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5ea0f4a32a1c832146f2ae5676b81fb75879c40c",
          "message": "fix: keep the chat clients on HTTP/2 (#137)",
          "timestamp": "2026-10-23T21:29:33+02:00",
          "tree_id": "7227434b3faac11b4738ec75aa0425bcb6ae4cfa",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/5ea0f4a32a1c832146f2ae5676b81fb75879c40c"
        },
        "date": 1792783820268,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 236.41,
            "unit": "ms",
            "range": 10.73
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 252.69,
            "unit": "ms",
            "range": 22.59
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 246.47,
            "unit": "ms",
            "range": 10.95
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 52.47,
            "unit": "ms",
            "range": 1.6
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 203.54,
            "unit": "ms",
            "range": 12.2
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 245.43,
            "unit": "ms",
            "range": 13.3
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b17ffd9b8e7619d4e05c1e223da95fb877053a0e",
          "message": "feat: add Gemini translation for Anthropic messages (#91)\n\n* feat: add Gemini translation for Anthropic messages\n\n* fix: preserve Gemini compatibility tool calls and model routing\n\n* test(gemini-compat): ignore the inline ?alt=sse when matching the stream endpoint\n\n* fix(anthropic): report Gemini usage the way Anthropic counts it\n\ninput_tokens excludes cache reads (promptTokenCount includes them) and output_tokens includes thoughtsTokenCount, matching the OpenAI bridge and GeminiClient.complete.\n\n* fix(gemini): merge a body generationConfig with the client defaults in stream\n\nstream() used to replace the client's temperature and thinking config whenever the body carried a generationConfig; body keys now win key by key. complete() stays a raw pass-through: complete_chat and generate_speech build their own config, and speech models reject a thinkingConfig.\n\n* fix(anthropic): translate documents, tool-result media and errors to Gemini\n\nBase64 PDF/text documents become inlineData/text parts, tool_result images and documents follow the functionResponse run (as #112 does for OpenAI), and is_error results are sent as {\"error\": text} since the OpenAI bridge has no precedent to follow. Remaining drops log a warning.\n\n* fix(anthropic): omit thinking-only assistant turns in the Gemini translation\n\nA model turn left empty after dropping thinking blocks is skipped instead of sent as an empty text part.\n\n* fix(anthropic): map Gemini finish reasons explicitly\n\nMAX_TOKENS now wins over function calls. MALFORMED_FUNCTION_CALL, UNEXPECTED_TOOL_CALL and other unmapped reasons report end_turn with a log.warning (the OpenAI bridge has no analogue; it maps unknown reasons to end_turn). Image safety reasons map to refusal. STOP is not mapped to stop_sequence: Gemini does not report whether a stop sequence matched.\n\n* refactor(anthropic): type the Gemini bridge with its existing TypedDicts\n\nRequests build Content/GenerationConfig/StreamBody directly (no final cast), responses return MessagesResponse/AnthropicUsage and streams AnthropicEvent. The SDK GenerateContentResponseDict is snake_case while the wire is camelCase, so it is narrowed to a Mapping once at the boundary.\n\n* test(anthropic): fold the Gemini bridge tests into parametrized cases\n\nComplete and stream translations now share one block-level case table; single-case request, system and tool-ID tests join their siblings.\n\n* refactor(anthropic): share system-prompt flattening between the bridges\n\nUsage and tool-result encoding differ per backend (OpenAI tool messages take raw text, Gemini needs a JSON object), so only the system text helper is shared.\n\n* test(anthropic): e2e round trips for the Gemini bridge\n\n* fix(anthropic): send tool schemas to Gemini as parametersJsonSchema",
          "timestamp": "2026-10-23T21:29:28+02:00",
          "tree_id": "a5bc161648c7b5dc816542202ba1d087f75462fd",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/b17ffd9b8e7619d4e05c1e223da95fb877053a0e"
        },
        "date": 1792783830523,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 247.37,
            "unit": "ms",
            "range": 2.61
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 246.07,
            "unit": "ms",
            "range": 2.94
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 269.24,
            "unit": "ms",
            "range": 2.85
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.68,
            "unit": "ms",
            "range": 0.82
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 197.9,
            "unit": "ms",
            "range": 3.94
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 239.21,
            "unit": "ms",
            "range": 3.51
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2476bf405154d5e717fb7de020664d3b39226c87",
          "message": "fix(gemini): a 402 raises QuotaExceededError (#139)",
          "timestamp": "2026-10-23T22:06:10+02:00",
          "tree_id": "5499985196f6bee52b4bbd5be2ff2fc68991e865",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/2476bf405154d5e717fb7de020664d3b39226c87"
        },
        "date": 1792786024857,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 239.99,
            "unit": "ms",
            "range": 4.02
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 244.89,
            "unit": "ms",
            "range": 4.73
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 271.55,
            "unit": "ms",
            "range": 7.03
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.32,
            "unit": "ms",
            "range": 1.44
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 193.4,
            "unit": "ms",
            "range": 6.04
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 235.36,
            "unit": "ms",
            "range": 6.66
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "81782798dad60984adfea95cee354fd71e8cf2a2",
          "message": "release 0.16.0 (#138)\n\n* chore(release): release 0.16.0\n\n* test(gemini): e2e thought tests on a model that emits thoughts; tolerate missing candidatesTokenCount",
          "timestamp": "2026-10-23T22:07:26+02:00",
          "tree_id": "998bdcc1dd49994146c8526b724159de52e87841",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/81782798dad60984adfea95cee354fd71e8cf2a2"
        },
        "date": 1792786096992,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 234.02,
            "unit": "ms",
            "range": 11.46
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 227.54,
            "unit": "ms",
            "range": 5.27
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 241.53,
            "unit": "ms",
            "range": 2.65
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 51.93,
            "unit": "ms",
            "range": 1.04
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 187.87,
            "unit": "ms",
            "range": 2.73
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 226.56,
            "unit": "ms",
            "range": 2.67
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "44dc427e0418d84eca0e06b5a525717069a91281",
          "message": "docs(changelog): list the Gemini 402 mapping under 0.16.0 (#144)",
          "timestamp": "2026-10-23T22:15:59+02:00",
          "tree_id": "e57d537021327cb42182cb628e8bf2f2ab6b2e79",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/44dc427e0418d84eca0e06b5a525717069a91281"
        },
        "date": 1792786625549,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 220.02,
            "unit": "ms",
            "range": 5.16
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 216.33,
            "unit": "ms",
            "range": 3.26
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 237.49,
            "unit": "ms",
            "range": 17.58
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.41,
            "unit": "ms",
            "range": 3.6
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 185.41,
            "unit": "ms",
            "range": 10.7
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 223.48,
            "unit": "ms",
            "range": 3.8
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bb24070b7cfdc017c8ca07dc73ee1ba043edcee7",
          "message": "chore: remove the test-min recipe (#146)\n\nCI already runs the suite on 3.13, and the recipe dropped the llms group so it failed locally.",
          "timestamp": "2026-10-26T17:46:06+01:00",
          "tree_id": "6fdbba6afc537b4252abf53db2b3959f41343969",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/bb24070b7cfdc017c8ca07dc73ee1ba043edcee7"
        },
        "date": 1793033213999,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 235.73,
            "unit": "ms",
            "range": 3.27
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 237.05,
            "unit": "ms",
            "range": 7.66
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 250.41,
            "unit": "ms",
            "range": 4.42
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.75,
            "unit": "ms",
            "range": 1.34
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 195.28,
            "unit": "ms",
            "range": 3.45
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 242.19,
            "unit": "ms",
            "range": 7.47
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8c8cc7c134ad579755c29e07eaf629223680097c",
          "message": "chore: weekly LLM SDK refresh (#145)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: track stable Mistral model IDs\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n* test(anthropic): check Message keys against every MessageParam member\n\nanthropic 2.3.0 turned MessageParam into a union (user/assistant/system), which get_type_hints rejects.\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-10-26T17:46:32+01:00",
          "tree_id": "c952a461ddb114678faea19b2ae8b3d3b02e5c76",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/8c8cc7c134ad579755c29e07eaf629223680097c"
        },
        "date": 1793033243036,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 238.96,
            "unit": "ms",
            "range": 5.79
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 233.86,
            "unit": "ms",
            "range": 3.48
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 251.08,
            "unit": "ms",
            "range": 4.11
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.22,
            "unit": "ms",
            "range": 0.88
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 194.7,
            "unit": "ms",
            "range": 2.57
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 240.62,
            "unit": "ms",
            "range": 7.99
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e01a336c6128c7d8540418a1920990d4053f85ae",
          "message": "feat(anthropic): keep later system messages inline (#147)\n\nThe Messages API now accepts role \"system\" in messages (anthropic 2.3.0), except on Claude 3 and 4.x up to 4-7.\nLeading system messages still go to the top-level system field; the OpenAI and Gemini compat proxies accept inline\nsystem messages instead of treating them as user turns.",
          "timestamp": "2026-10-26T19:08:17+01:00",
          "tree_id": "bb300df30a6e46ba2512106d1c86b72ac30679f2",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/e01a336c6128c7d8540418a1920990d4053f85ae"
        },
        "date": 1793038153135,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 250.55,
            "unit": "ms",
            "range": 11.18
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 240.98,
            "unit": "ms",
            "range": 4.14
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 262.89,
            "unit": "ms",
            "range": 6.81
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.03,
            "unit": "ms",
            "range": 1.69
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 193.56,
            "unit": "ms",
            "range": 6.04
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 240.14,
            "unit": "ms",
            "range": 7.62
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "aca3c151df43ec50c8765b9bcb29b9693f0907a1",
          "message": "feat(otel): record request size on chat spans (#148)",
          "timestamp": "2026-10-26T21:01:06+01:00",
          "tree_id": "94526a331f2e108f8a407e8f6884919325dca686",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/aca3c151df43ec50c8765b9bcb29b9693f0907a1"
        },
        "date": 1793044912576,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 234.08,
            "unit": "ms",
            "range": 2.77
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 236.05,
            "unit": "ms",
            "range": 4.57
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 250.74,
            "unit": "ms",
            "range": 2.62
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.78,
            "unit": "ms",
            "range": 0.65
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 194.19,
            "unit": "ms",
            "range": 2.54
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 232.53,
            "unit": "ms",
            "range": 2.69
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "df6bde81fad5d6443d109eae749e67687ffb37f9",
          "message": "fix: restore HTTP/3 now that jawah/urllib3.future#440 is fixed (#150)\n\nDrop the disable_http3 pin from #137 and raise the floors to qh3 2.1.0 and\nurllib3-future 2.25.904, which carry the QUIC flow-control fix.",
          "timestamp": "2026-10-27T06:51:55+01:00",
          "tree_id": "5a374777fcd2848ad4e997441627f4ca7fab4d43",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/df6bde81fad5d6443d109eae749e67687ffb37f9"
        },
        "date": 1793080362806,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 237.18,
            "unit": "ms",
            "range": 2.44
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 238.88,
            "unit": "ms",
            "range": 1.39
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 254.36,
            "unit": "ms",
            "range": 1.86
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.45,
            "unit": "ms",
            "range": 0.79
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 195.39,
            "unit": "ms",
            "range": 3.1
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 235.16,
            "unit": "ms",
            "range": 3.78
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "52211726+Volkiaa@users.noreply.github.com",
            "name": "Volkiaa",
            "username": "Volkiaa"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "857e0145c39343be95d4c9f07875de85841b9447",
          "message": "fix: keep MCP credentials out of repr and the Gemini Live key out of the URL (#143)\n\n* fix(mcp): keep transport credentials out of repr\n\n`McpStreamable.token` and `McpStdio.env` were dataclass fields that appear\nin `repr()`, so logging a transport or an `AgentSession` printed a bearer\ntoken or the child's environment. Both fields now use `repr=False`, like the\nprovider `api_key` fields.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* fix(gemini): send the Live API key in a header, not the URL\n\n`GeminiRealtimeClient` put the key in the `key` query parameter of the\nwebsocket URL, so a failed handshake copied it into the exception text and\ninto OpenTelemetry spans. The key now goes in `x-goog-api-key`, as the chat\nclient and `google-genai` do.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n---------\n\nCo-authored-by: amsn <claude@massonalexandre.com>\nCo-authored-by: Claude Sonnet 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-28T14:35:41+01:00",
          "tree_id": "1b1d432b8326ff05f2d397e9da8b37d5a705e07e",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/857e0145c39343be95d4c9f07875de85841b9447"
        },
        "date": 1793194594523,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 237.32,
            "unit": "ms",
            "range": 3.5
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 239.79,
            "unit": "ms",
            "range": 5.48
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 253.62,
            "unit": "ms",
            "range": 4.08
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 53.1,
            "unit": "ms",
            "range": 1.38
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 191.57,
            "unit": "ms",
            "range": 5.74
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 229.24,
            "unit": "ms",
            "range": 5.65
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "52211726+Volkiaa@users.noreply.github.com",
            "name": "Volkiaa",
            "username": "Volkiaa"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ac891049b996e7e5feb53f6887cbceb127ddf674",
          "message": "fix(agent): reject non-object tool arguments before the approval hook (#141)\n\n* fix(agent): reject non-object tool arguments before the approval hook\n\nA tool call whose arguments parsed to valid JSON that is not an object\n(`[]`, `5`, `null`) skipped `approve_tool` and still reached the handler.\nSuch a call now gets an error result naming the received JSON type, and\nneither the hook nor the handler runs.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* refactor(agent): drop the JSON type-name helper\n\ntype(parsed).__name__ is enough for the rejection message.\n\n---------\n\nCo-authored-by: amsn <claude@massonalexandre.com>\nCo-authored-by: Claude Sonnet 5.5 <noreply@anthropic.com>\nCo-authored-by: julien <julien.brayere@obitrain.com>",
          "timestamp": "2026-10-28T14:36:26+01:00",
          "tree_id": "65ea662e68344f0c2cce34529d2ee5eaa08016cd",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/ac891049b996e7e5feb53f6887cbceb127ddf674"
        },
        "date": 1793194641991,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "3.13 · padwan_ai (facade)",
            "value": 245.45,
            "unit": "ms",
            "range": 1.74
          },
          {
            "name": "3.13 · padwan_ai.openai",
            "value": 247.83,
            "unit": "ms",
            "range": 1.64
          },
          {
            "name": "3.13 · padwan_ai.otel",
            "value": 262.16,
            "unit": "ms",
            "range": 1.41
          },
          {
            "name": "3.15 · padwan_ai (facade)",
            "value": 54.09,
            "unit": "ms",
            "range": 0.96
          },
          {
            "name": "3.15 · padwan_ai.openai",
            "value": 198.62,
            "unit": "ms",
            "range": 1.66
          },
          {
            "name": "3.15 · padwan_ai.otel",
            "value": 238.62,
            "unit": "ms",
            "range": 2.44
          }
        ]
      }
    ],
    "Import Performance (3.15)": [
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dad7148968a9864fbf1297c09c606bbebd14156f",
          "message": "feat: audio input content parts across providers (#43)\n\n* feat: audio input content parts across providers\n\nAdd ContentAudioPart (OpenAI input_audio shape, wav/mp3) with an audio_part\nbuilder and content_parts inference. OpenAI/Grok receive parts verbatim,\nGemini converts to inlineData, Mistral rewrites to its base64 input_audio\nchunk via a new _prepare_messages hook. supports_audio mirrors\nsupports_vision with per-provider curated checks.\n\n* feat: accept str paths in audio_part like image_part\n\n* docs: use parentheses instead of em-dashes in audio docs\n\n* feat: per-provider audio format support\n\nWiden AudioFormat to wav/mp3/flac/ogg/aac/aiff/m4a and make supports_audio\nformat-aware (fmt param). Curated per provider: OpenAI wav/mp3 (API schema),\nGemini all formats, Mistral voxtral wav/mp3/flac/ogg (verified against the\nchat API; m4a rejected). Providers expose AUDIO_FORMATS.\n\n* test(otel): multimodal parts captured without binary payloads\n\n* fix: lazy-module registration and otel fixture rename after rebase\n\nRegister padwan_llm.audio in the top-level __lazy_modules__ set (Python\n3.15) and adapt the binary-parts capture test to the otel_logging fixture.",
          "timestamp": "2026-08-23T08:04:56+02:00",
          "tree_id": "be8dc374e3b4a3c08717137427581df6fc264dfa",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/dad7148968a9864fbf1297c09c606bbebd14156f"
        },
        "date": 1787465444619,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 52.15,
            "unit": "ms",
            "range": 0.46
          },
          {
            "name": "padwan_llm.openai",
            "value": 197.98,
            "unit": "ms",
            "range": 1.07
          },
          {
            "name": "padwan_llm.otel",
            "value": 229.12,
            "unit": "ms",
            "range": 1.61
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "99394ca05996f5e3699aae9fbcf94f8f2f748593",
          "message": "chore(release): release 0.9.0 (#45)",
          "timestamp": "2026-08-23T08:15:33+02:00",
          "tree_id": "631e8b661f2d02d36a318d6da02e3f768264e2ee",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/99394ca05996f5e3699aae9fbcf94f8f2f748593"
        },
        "date": 1787466096437,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 53.48,
            "unit": "ms",
            "range": 0.59
          },
          {
            "name": "padwan_llm.openai",
            "value": 202.72,
            "unit": "ms",
            "range": 2.16
          },
          {
            "name": "padwan_llm.otel",
            "value": 235.91,
            "unit": "ms",
            "range": 2.64
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cbeec528ea996530aca98fdcda6ee1943cc3d81a",
          "message": "fix: close half-read SSE streams before returning connections to the pool (#46)\n\n* fix: close half-read SSE streams before returning connections to the pool\n\nA stream that breaks on [DONE] (or is abandoned by its consumer) left the\nSSE response half-read; the pooled connection could then hang the next\nstream request. Abort the extension in a finally across all providers.\n\n* refactor: dedupe the SSE stream loop into LLMClientBase._iter_sse\n\next.close() alone releases the pooled connection (verified against a live\nSSE backend on HTTP/1.1 and HTTP/2), so drop the raw-response teardown and\nthe mock-only regression test. Providers wrap the shared iterator in\naclosing so an abandoned stream closes deterministically.",
          "timestamp": "2026-08-23T15:30:06+02:00",
          "tree_id": "0433f9b8ccda881b64b9afdfce3de0d876aa4458",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/cbeec528ea996530aca98fdcda6ee1943cc3d81a"
        },
        "date": 1787491885242,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 53.76,
            "unit": "ms",
            "range": 1.31
          },
          {
            "name": "padwan_llm.openai",
            "value": 207.85,
            "unit": "ms",
            "range": 6.13
          },
          {
            "name": "padwan_llm.otel",
            "value": 234.55,
            "unit": "ms",
            "range": 2.64
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "101126627a97f748a515d5fafa6b56bd4c34450d",
          "message": "chore(release): release 0.9.1 (#47)",
          "timestamp": "2026-08-24T07:01:01+02:00",
          "tree_id": "923f2aa8c4df21aad9522d6cef8b2eb5f52516e8",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/101126627a97f748a515d5fafa6b56bd4c34450d"
        },
        "date": 1787548018489,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 54.72,
            "unit": "ms",
            "range": 1
          },
          {
            "name": "padwan_llm.openai",
            "value": 210.45,
            "unit": "ms",
            "range": 3.08
          },
          {
            "name": "padwan_llm.otel",
            "value": 242.97,
            "unit": "ms",
            "range": 2.35
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "943aabe4da8e06752e31853089e969c24ce38d7e",
          "message": "fix: best-effort SSE cleanup; tolerate HTTP/2 abort quirk (#48)\n\nClosing an already-finished HTTP/2 stream raises KeyError inside\nurllib3-future; the unguarded finally corrupted every successful stream\nover h2 backends (missing message end, spurious error event). Cleanup is\nnow best-effort per step and restores the raw-response teardown and pool\nrelease that the 0.9.1 refactor dropped (the ext-only close leaves the\nlease held until GC on HTTP/1.1).",
          "timestamp": "2026-08-24T16:49:18+02:00",
          "tree_id": "2d5f3f865af799f7e26f91ef5ae080070a843a02",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/943aabe4da8e06752e31853089e969c24ce38d7e"
        },
        "date": 1787583054559,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 58.71,
            "unit": "ms",
            "range": 2.28
          },
          {
            "name": "padwan_llm.openai",
            "value": 218.23,
            "unit": "ms",
            "range": 6.12
          },
          {
            "name": "padwan_llm.otel",
            "value": 271.52,
            "unit": "ms",
            "range": 23.46
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a6aff107fdfbdb9c4037918daacfd43e5c3c25d7",
          "message": "chore(release): release 0.9.2 (#50)",
          "timestamp": "2026-08-24T17:00:32+02:00",
          "tree_id": "0aff4bc9436e73d803c41d4b4e18ca3ed82b4bd3",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/a6aff107fdfbdb9c4037918daacfd43e5c3c25d7"
        },
        "date": 1787583993831,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 56.3,
            "unit": "ms",
            "range": 2.89
          },
          {
            "name": "padwan_llm.openai",
            "value": 209.69,
            "unit": "ms",
            "range": 4.69
          },
          {
            "name": "padwan_llm.otel",
            "value": 253.01,
            "unit": "ms",
            "range": 8.01
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "918b5dba5b0a112bd30cc3dc9ba4eaf3660bf852",
          "message": "chore: require urllib3-future 2.24.904 (#51)\n\nCarries the upstream fix for the HTTP/2 stream reset raising on\nalready-closed SSE streams (jawah/urllib3.future#406).",
          "timestamp": "2026-08-25T07:48:42+02:00",
          "tree_id": "ca67fc1f0cbffb68f8fdce475bb137cf0f9a845a",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/918b5dba5b0a112bd30cc3dc9ba4eaf3660bf852"
        },
        "date": 1787637184648,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 39.59,
            "unit": "ms",
            "range": 0.77
          },
          {
            "name": "padwan_llm.openai",
            "value": 150.82,
            "unit": "ms",
            "range": 2.61
          },
          {
            "name": "padwan_llm.otel",
            "value": 171.25,
            "unit": "ms",
            "range": 3.05
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "44ad0ebf0f3aade1e223c009fc64bb6abe091e83",
          "message": "chore(release): release 0.9.3 (#52)",
          "timestamp": "2026-08-25T07:58:09+02:00",
          "tree_id": "3ef9b9d70966d604affc758240aa898a37b76905",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/44ad0ebf0f3aade1e223c009fc64bb6abe091e83"
        },
        "date": 1787637828828,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 55.82,
            "unit": "ms",
            "range": 0.68
          },
          {
            "name": "padwan_llm.openai",
            "value": 207.81,
            "unit": "ms",
            "range": 2.92
          },
          {
            "name": "padwan_llm.otel",
            "value": 240.37,
            "unit": "ms",
            "range": 1.66
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "40022bb75ab4ae0b6698102d362da2df522c9a50",
          "message": "chore(release): release 0.9.4 (#53)",
          "timestamp": "2026-08-25T16:01:50+02:00",
          "tree_id": "c99b20de729d81b7af17eb132aad10e25a051640",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/40022bb75ab4ae0b6698102d362da2df522c9a50"
        },
        "date": 1787666859390,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 53.13,
            "unit": "ms",
            "range": 0.52
          },
          {
            "name": "padwan_llm.openai",
            "value": 200.55,
            "unit": "ms",
            "range": 3
          },
          {
            "name": "padwan_llm.otel",
            "value": 234.98,
            "unit": "ms",
            "range": 2.84
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8c607e2633e80a4d93d71dd050b9a135dfc433f5",
          "message": "chore: weekly LLM SDK refresh (#54)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* feat(gemini): add gemini-3.5-transcribe, gemini-omni-1.1-flash, gemini-3.5-transcribe-live\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-08-31T21:53:25+02:00",
          "tree_id": "8ac03643185ca3336b874a72d2ff10c92bb1ea07",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/8c607e2633e80a4d93d71dd050b9a135dfc433f5"
        },
        "date": 1788206357535,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 58.19,
            "unit": "ms",
            "range": 1.19
          },
          {
            "name": "padwan_llm.openai",
            "value": 224,
            "unit": "ms",
            "range": 6.36
          },
          {
            "name": "padwan_llm.otel",
            "value": 247.77,
            "unit": "ms",
            "range": 4.13
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dfb179f56a73ce2140875182c26c5f23d5d33b12",
          "message": "chore: weekly LLM SDK refresh (#56)\n\n* chore: weekly LLM SDK refresh\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\n* chore: add drifted provider model literals\n\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>\n\n---------\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>\nCo-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>\nCo-authored-by: Andarius <5070712+Andarius@users.noreply.github.com>",
          "timestamp": "2026-09-07T17:29:17+02:00",
          "tree_id": "ef67670966be1a7f8044e9ecc1895a39c9828f8f",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/dfb179f56a73ce2140875182c26c5f23d5d33b12"
        },
        "date": 1788795298854,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 54.15,
            "unit": "ms",
            "range": 0.73
          },
          {
            "name": "padwan_llm.openai",
            "value": 203.62,
            "unit": "ms",
            "range": 1.85
          },
          {
            "name": "padwan_llm.otel",
            "value": 234.1,
            "unit": "ms",
            "range": 0.93
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9524251e84392e30831c6cdcf13e279d101f3ec7",
          "message": "fix: infer supported audio formats from file extensions (#57)",
          "timestamp": "2026-09-08T09:46:54+02:00",
          "tree_id": "c5099efdb624191865fd018695a2a28320770833",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/9524251e84392e30831c6cdcf13e279d101f3ec7"
        },
        "date": 1788853687199,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 53.93,
            "unit": "ms",
            "range": 2.03
          },
          {
            "name": "padwan_llm.openai",
            "value": 201.18,
            "unit": "ms",
            "range": 1.86
          },
          {
            "name": "padwan_llm.otel",
            "value": 234.14,
            "unit": "ms",
            "range": 4.09
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "61604486f616e2485066be2690b77fb48b2b8cd5",
          "message": "fix(otel): trace raw OpenAI complete()/stream() calls (#55)\n\n* fix(otel): open a span for raw OpenAI complete()/stream() calls\n\nRaw OpenAIClient.complete()/stream() only enriched a chat span opened by\ncomplete_chat()/stream_chat(); callers using the raw API (padwan-proxy) got\nno telemetry at all. They now open their own span when none is active, with\nusage, finish reasons, tool names, time to first chunk and error status.\n\n* feat(otel): capture content on raw OpenAI complete()/stream() calls\n\nWith capture_content, raw calls now record gen_ai.input.messages,\ngen_ai.tool.definitions and gen_ai.output.messages (text and tool calls,\naccumulated from stream deltas) and emit the inference details log event,\nas the chat API already did.\n\n* fix(otel): preserve raw choices and isolate streaming context\n\n- Capture custom tool calls and keep response choices separate.\n- Restore caller context between chunks and close interrupted streams.\n- Declare typed MCP session timestamps and add regression coverage.",
          "timestamp": "2026-09-11T22:27:25+02:00",
          "tree_id": "c72877df84d110a169bd4eb2cf63fbd8f989ab58",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/61604486f616e2485066be2690b77fb48b2b8cd5"
        },
        "date": 1789158519833,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 57.09,
            "unit": "ms",
            "range": 0.79
          },
          {
            "name": "padwan_llm.openai",
            "value": 208.53,
            "unit": "ms",
            "range": 2.2
          },
          {
            "name": "padwan_llm.otel",
            "value": 243.59,
            "unit": "ms",
            "range": 3.78
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a9aaaa21efce1d22b15979632a0359d7f50bde3c",
          "message": "fix(otel): restore caller context between chat stream chunks (#58)\n\n- Limit active chat context to advancing the provider iterator.\n- Preserve metric trace links and cover cross-task stream lifecycle.",
          "timestamp": "2026-09-11T23:13:51+02:00",
          "tree_id": "b62648d77284041dccdfb215ba8ae6efc435a4ca",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/a9aaaa21efce1d22b15979632a0359d7f50bde3c"
        },
        "date": 1789161307975,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 54.37,
            "unit": "ms",
            "range": 1.29
          },
          {
            "name": "padwan_llm.openai",
            "value": 208.97,
            "unit": "ms",
            "range": 5.08
          },
          {
            "name": "padwan_llm.otel",
            "value": 240.61,
            "unit": "ms",
            "range": 7.86
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bot@polarsen.io",
            "name": "Polarsen-bot",
            "username": "Polarsen-bot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d7605973bafec0d42defc41620f6b09e87e8a34b",
          "message": "chore: weekly LLM SDK refresh (#65)\n\n- Bump openai, google-genai, xai-sdk, mcp to latest\n- Regenerate OpenAI/Mistral OpenAPI TypedDicts\n- Include provider model drift report\n\nCo-authored-by: Polarsen-bot <248777799+Polarsen-bot@users.noreply.github.com>",
          "timestamp": "2026-09-14T18:35:03+02:00",
          "tree_id": "bec5e8de9b4f11d862e6062269c23923642eecfa",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/d7605973bafec0d42defc41620f6b09e87e8a34b"
        },
        "date": 1789404052105,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 54.5,
            "unit": "ms",
            "range": 0.66
          },
          {
            "name": "padwan_llm.openai",
            "value": 205.89,
            "unit": "ms",
            "range": 1.75
          },
          {
            "name": "padwan_llm.otel",
            "value": 238.3,
            "unit": "ms",
            "range": 1.49
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1582d3b35dac07cb297dd7506aaa405b9f6c456f",
          "message": "ci(perf): skip benchmark PR comments on fork PRs (#68)\n\nThe GITHUB_TOKEN is read-only on pull requests from forks, so posting the\nbenchmark comment fails with \"Resource not accessible by integration\" and\nmarks the job failed. Only comment when the head repo is this repo.",
          "timestamp": "2026-09-14T18:51:29+02:00",
          "tree_id": "e2a9ed43df0372653552769ff47c69425484977e",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/1582d3b35dac07cb297dd7506aaa405b9f6c456f"
        },
        "date": 1789404768352,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 51.93,
            "unit": "ms",
            "range": 1.38
          },
          {
            "name": "padwan_llm.openai",
            "value": 206.14,
            "unit": "ms",
            "range": 6.53
          },
          {
            "name": "padwan_llm.otel",
            "value": 228.28,
            "unit": "ms",
            "range": 1.72
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "carlo.abichahine@gmail.com",
            "name": "Carlo Abi Chahine",
            "username": "cabichahine"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f0f3eb05a241fa1bf9ea4ff4a235d7cc13c541fd",
          "message": "feat(testing): ScriptedClient, a scripted stand-in for any client (#59)\n\n* feat(testing): ScriptedClient, a scripted stand-in for any client\n\nA client that replays a script of rounds (text and/or tool calls) instead of calling a\nprovider, records what the model would have seen round by round, and fails loudly when\nthe script runs out. Drives an AgentSession end to end in tests without a key or a socket.\n\n* fix(testing): snapshot recorded requests, align ScriptedClient with repo conventions (#63)\n\n* fix(testing): snapshot recorded requests, align ScriptedClient with repo conventions\n\nDeep-copy messages, tools and extra_params when recording a round so later\nmutation by the caller does not alter the record. Drop the future import and\nmodule docstring, use text: str | None, parametrize tests, and fix the\nNotRequired access that failed pyright on tests/.\n\n* refactor(testing): make ScriptedClient a dataclass\n\n* test(testing): keep only the essential ScriptedClient tests\n\n* test(testing): type recorded messages as Message\n\n* refactor(agent): type the session client as a ChatClient protocol\n\nAny async context manager with stream_chat now satisfies AgentSession, so\ntest doubles no longer need cast(LLMClientBase, ...). ScriptedClient uses\nMapping[str, object] instead of Any for tool arguments and extra_params.\n\n* docs(agents): client accepts any ChatClient\n\n* docs(agents): drop roadmap prose from limitations\n\n* docs(agents): keep the testing example ruff-format stable\n\n* docs(testing): one-line docstrings on ScriptedClient helpers\n\n(cherry picked from commit 2f76772748f98013458a7fb47d34b31b6c583500)\n\n---------\n\nCo-authored-by: Julien Brayere <julien.brayere@obitrain.com>",
          "timestamp": "2026-09-14T21:05:48+02:00",
          "tree_id": "25ebc58ff46254841c95e7d2c9743c2f985edde2",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/f0f3eb05a241fa1bf9ea4ff4a235d7cc13c541fd"
        },
        "date": 1789412812361,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 52.82,
            "unit": "ms",
            "range": 0.61
          },
          {
            "name": "padwan_llm.openai",
            "value": 205.13,
            "unit": "ms",
            "range": 7.66
          },
          {
            "name": "padwan_llm.otel",
            "value": 229.51,
            "unit": "ms",
            "range": 1.96
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ad9666e3d60604b321dccb59de03bf5deac29190",
          "message": "feat(tools): pluggable validator for tool() (msgspec or pydantic) (#67)\n\n* feat(tools): build an McpTool from a typed async function\n\ntool(fn) turns a typed async function into an McpTool: the signature becomes the JSON\nSchema the model sees, the docstring the description, and the arguments the model sends\nare validated (and coerced) before the function runs. Pydantic does the work, behind a\nnew optional extra: pip install \"padwan-llm[pydantic]\".\n\n* feat(tools): validate tool arguments with msgspec instead of pydantic\n\nSwap the pydantic extra for msgspec: single wheel, no transitive deps, and the\nconsumers already use it. Keep Annotated constraints in the schema\n(include_extras), refuse positional-only and variadic parameters at build time,\ndrop per-property title noise from the schema, and dump results through\nmsgspec.to_builtins.\n\n* feat(tools): let the caller pick the validator (msgspec or pydantic)\n\ntool() takes validator=\"msgspec\" | \"pydantic\" | ToolValidator instance. With\nnone given it uses the only installed backend and raises when both are, since\nconstraint annotations are library-specific and a guessed backend would drop\nthem silently. Neither library is a dependency or extra; both are dev deps so\nthe suite covers both. Pydantic results are dumped with\npydantic_core.to_jsonable_python; unserialisable results now raise inside the\nhandler so they reach the model as a tool error instead of crashing the session.\n\n* feat(tools): pick the validator from the annotations\n\nWith no validator= given, a msgspec.Meta constraint or Struct type selects\nmsgspec and a pydantic.Field constraint or BaseModel type selects pydantic,\nthrough Annotated metadata, unions and generics. Mixed annotations raise. Plain\nsignatures keep the only-installed rule.\n\n* docs(agents): examples for msgspec, pydantic and explicit validators\n\n* docs(agents): msgspec / pydantic examples as content tabs\n\n* docs(agents): ruff-format the code blocks\n\n---------\n\nCo-authored-by: Carlo Abi Chahine <carlo.abichahine@gmail.com>",
          "timestamp": "2026-09-14T22:03:21+02:00",
          "tree_id": "65057c50de962d572c98f4f584d0104f3e98f29a",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/ad9666e3d60604b321dccb59de03bf5deac29190"
        },
        "date": 1789416543616,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 55.54,
            "unit": "ms",
            "range": 1.41
          },
          {
            "name": "padwan_llm.openai",
            "value": 204.42,
            "unit": "ms",
            "range": 2.34
          },
          {
            "name": "padwan_llm.otel",
            "value": 239.41,
            "unit": "ms",
            "range": 1.71
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0d6d67298105e71cddafb878af69aaf2c45a6714",
          "message": "feat(langfuse): time to first token as completion_start_time (#69)\n\n* feat(langfuse): map the first streamed chunk to completion_start_time\n\nStreams already carried `gen_ai.response.time_to_first_chunk` (a duration), but\nLangfuse only shows time to first token when a generation has an absolute\n`completion_start_time`, and the OTel mask hook does not expose span start\ntimes, so the duration alone could not be converted.\n\n- otel: the two streaming paths share `_record_first_chunk`, which also stamps\n  `padwan_llm.response.first_chunk_time` (ISO 8601 UTC) on the chat span.\n- langfuse: `_mapped_attributes` serializes that instant as\n  `langfuse.observation.completion_start_time`, the same JSON form the SDK uses.\n- docs: both attribute tables list the new mapping.\n\n* fix(otel): count the first raw provider chunk on the active chat span\n\nThe chat wrapper only sees the text chunks a `ChatStream` yields, so a\nstream that answers with tool calls or reasoning alone never recorded a\ntime to first chunk. The raw `stream()` wrapper, which already enriches\nthe active chat span, now records the first provider chunk on it; the\nchat wrapper's own text-chunk record becomes a fallback for providers\nwhose raw stream is not wrapped. `_record_first_chunk` records once per\nspan.\n\nThe wall-clock instant now uses the `Z` suffix, like the Langfuse SDK.\n\n* fix(otel): keep the stream label on the raw first-chunk histogram\n\nThe raw stream wrapper recorded time_to_first_chunk without\ngen_ai.request.stream=True, unlike the chat wrapper it replaces. Also\nshortens the new docstring and comment, and states in the docs which\nproviders count the first raw chunk versus the first text chunk.\n\n---------\n\nCo-authored-by: Carlo Abi Chahine <carlo.abichahine@gmail.com>",
          "timestamp": "2026-09-14T22:37:07+02:00",
          "tree_id": "040f8bcd481ea9c1779a9989a8d6268c44b4500d",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/0d6d67298105e71cddafb878af69aaf2c45a6714"
        },
        "date": 1789418311748,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 57.34,
            "unit": "ms",
            "range": 0.65
          },
          {
            "name": "padwan_llm.openai",
            "value": 223.48,
            "unit": "ms",
            "range": 9.87
          },
          {
            "name": "padwan_llm.otel",
            "value": 256.52,
            "unit": "ms",
            "range": 5.88
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6b6d48b2da64ff4091d6d292a9cc857b7dc96a9f",
          "message": "fix(langfuse): import httpx at runtime, the annotation is evaluated on Python 3.13 (#71)",
          "timestamp": "2026-09-14T22:41:46+02:00",
          "tree_id": "8423b6193f65cfe249308f0464ec8d40751680d0",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/6b6d48b2da64ff4091d6d292a9cc857b7dc96a9f"
        },
        "date": 1789418612904,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 55.73,
            "unit": "ms",
            "range": 1.07
          },
          {
            "name": "padwan_llm.openai",
            "value": 210.17,
            "unit": "ms",
            "range": 3.53
          },
          {
            "name": "padwan_llm.otel",
            "value": 252.27,
            "unit": "ms",
            "range": 7.39
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3587b1ae4c583f69854606bdc8662b52844556ba",
          "message": "refactor(langfuse): keep httpx a type-only import (#72)",
          "timestamp": "2026-09-14T22:46:22+02:00",
          "tree_id": "96ead28b58fc1f33c8d9b3698ac7b4bb7b4dcbd6",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/3587b1ae4c583f69854606bdc8662b52844556ba"
        },
        "date": 1789418875138,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 37.91,
            "unit": "ms",
            "range": 4.39
          },
          {
            "name": "padwan_llm.openai",
            "value": 144.17,
            "unit": "ms",
            "range": 9.83
          },
          {
            "name": "padwan_llm.otel",
            "value": 166.34,
            "unit": "ms",
            "range": 11.2
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "julien",
            "username": "Andarius"
          },
          "committer": {
            "email": "julien.brayere@obitrain.com",
            "name": "julien",
            "username": "Andarius"
          },
          "distinct": true,
          "id": "793ca31ada775f20042a3d59029a26ec400f7760",
          "message": "chore(just): docs recipe takes a port\n\nClaude-Session: https://claude.ai/code/session_01KTHPAvoDsiAWntwyc8JSF1",
          "timestamp": "2026-09-14T22:50:52+02:00",
          "tree_id": "be6ddcbd482cd8c52314521e18262ef7e766f5d1",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/793ca31ada775f20042a3d59029a26ec400f7760"
        },
        "date": 1789419128194,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 55.24,
            "unit": "ms",
            "range": 0.41
          },
          {
            "name": "padwan_llm.openai",
            "value": 207.3,
            "unit": "ms",
            "range": 4.61
          },
          {
            "name": "padwan_llm.otel",
            "value": 241,
            "unit": "ms",
            "range": 2.31
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ad0a31abab8ccd05935b0707daeda3dc35bb984f",
          "message": "feat(agent): typed final answer through an output tool (#73)\n\n* feat(agent): typed final answer through an output tool\n\nAgentSession(output=Model) adds a `submit` tool whose parameters are the\nanswer's schema; run() drives the loop until a call validates and returns\nthe instance. Invalid calls go back to the model up to max_repairs times,\nthen OutputError; a text answer or the round limit raise OutputError too.\n\nThe answer class goes through the tool() validators: ToolValidator gains\nschema(cls) and convert(obj, cls), compile() is built on them, and the\nbackend is resolved from the class (Struct, BaseModel) or output_validator=.\n\n* perf(tools): build the validator adapter once per class\n\nToolValidator.schema/convert become adapt(cls) -> (schema, convert): a pydantic\nTypeAdapter is built once and reused, per the pydantic performance docs, instead\nof once per tool call.\n\n* refactor(agent): group the typed-answer settings in AgentOutput\n\nAgentSession(output=AgentOutput(cls, validator=, tool=, max_repairs=)) replaces\nfour output_* fields; per-run state moves to a private _OutputRun so one\nAgentOutput can be shared across sessions.\n\n* fix(agent): settle the typed answer once, reject broken JSON, keep recursive schemas valid\n\n- the first accepted submit or the exhausted repair budget settles a run;\n  later calls in the round are answered with an error and ignored\n- tool arguments that are not valid JSON are returned as an error instead\n  of running the handler on {}; for the output tool it counts as a repair\n- ToolValidator.adapt keeps a recursive class under $defs so its inner\n  $refs resolve, for msgspec and pydantic alike\n- AgentOutput[T] / AgentSession[T = Any]: run() returns T, load() infers it\n- docs: output= in the configuration block, approval and sibling-tool notes\n\n* refactor(agent): type the output handler's result\n\n* refactor(agent): default the session's answer type to object, not Any\n\n* refactor(agent): bound the answer type to Struct | BaseModel\n\nThe bound lives under TYPE_CHECKING (PEP 695 bounds are lazy), so neither\nlibrary is imported at runtime. A Struct or BaseModel always names its\nvalidator, so AgentOutput loses validator= and dataclass answers.\n\n* docs(agent): generic triage example for typed answers\n\n* docs(agent): note how the answer bound behaves with one library missing\n\n* refactor(agent): build AgentSession[O] in load() instead of casting",
          "timestamp": "2026-09-14T23:47:01+02:00",
          "tree_id": "5b91285faabbc60c98dcf9f96b77ec931811a20d",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/ad0a31abab8ccd05935b0707daeda3dc35bb984f"
        },
        "date": 1789422493394,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 43.4,
            "unit": "ms",
            "range": 0.87
          },
          {
            "name": "padwan_llm.openai",
            "value": 159.76,
            "unit": "ms",
            "range": 2.19
          },
          {
            "name": "padwan_llm.otel",
            "value": 187.14,
            "unit": "ms",
            "range": 1.06
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "711cf1ac41f28e4eef84cc6708b64b087a6cce9d",
          "message": "chore(release): release 0.10.0 (#74)",
          "timestamp": "2026-09-14T23:55:31+02:00",
          "tree_id": "1508c74a0a6ee28b436b1165881af859d8b599ee",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/711cf1ac41f28e4eef84cc6708b64b087a6cce9d"
        },
        "date": 1789423179907,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 39.13,
            "unit": "ms",
            "range": 0.77
          },
          {
            "name": "padwan_llm.openai",
            "value": 149.81,
            "unit": "ms",
            "range": 6.39
          },
          {
            "name": "padwan_llm.otel",
            "value": 173.86,
            "unit": "ms",
            "range": 4.01
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3b1f8a6dd81a8359f4df9dc61a1f416da888a5a5",
          "message": "fix(otel): instrument raw calls on all OpenAI-compatible clients (#76)\n\n`complete`/`stream` were patched on OpenAIClient, but they are defined on\n_OpenAIBase, so sibling subclasses (MistralClient, and anything LLMClient\nroutes to a custom base_url) emitted no spans for the raw call path.",
          "timestamp": "2026-09-16T18:32:11+02:00",
          "tree_id": "5c6ac41c6836c0724188e8f55d25f6f95e9ddf68",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/3b1f8a6dd81a8359f4df9dc61a1f416da888a5a5"
        },
        "date": 1789576416795,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 54.61,
            "unit": "ms",
            "range": 1.6
          },
          {
            "name": "padwan_llm.openai",
            "value": 206.43,
            "unit": "ms",
            "range": 3.14
          },
          {
            "name": "padwan_llm.otel",
            "value": 243.87,
            "unit": "ms",
            "range": 2.81
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3b1f8a6dd81a8359f4df9dc61a1f416da888a5a5",
          "message": "fix(otel): instrument raw calls on all OpenAI-compatible clients (#76)\n\n`complete`/`stream` were patched on OpenAIClient, but they are defined on\n_OpenAIBase, so sibling subclasses (MistralClient, and anything LLMClient\nroutes to a custom base_url) emitted no spans for the raw call path.",
          "timestamp": "2026-09-16T18:32:11+02:00",
          "tree_id": "5c6ac41c6836c0724188e8f55d25f6f95e9ddf68",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/3b1f8a6dd81a8359f4df9dc61a1f416da888a5a5"
        },
        "date": 1789577652166,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 59.78,
            "unit": "ms",
            "range": 1.17
          },
          {
            "name": "padwan_llm.openai",
            "value": 231.85,
            "unit": "ms",
            "range": 7.05
          },
          {
            "name": "padwan_llm.otel",
            "value": 281.56,
            "unit": "ms",
            "range": 6.87
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "49192ccca8905df916e0db71174f1fe86eceffaa",
          "message": "chore(release): release 0.10.1 (#77)",
          "timestamp": "2026-09-16T21:08:13+02:00",
          "tree_id": "383bfb10e59b3e8405449100abb7c96e82871e7c",
          "url": "https://github.com/polarsen-io/padwan-llm/commit/49192ccca8905df916e0db71174f1fe86eceffaa"
        },
        "date": 1789585958883,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_llm (facade)",
            "value": 42.9,
            "unit": "ms",
            "range": 1.63
          },
          {
            "name": "padwan_llm.openai",
            "value": 161.72,
            "unit": "ms",
            "range": 3.92
          },
          {
            "name": "padwan_llm.otel",
            "value": 191.54,
            "unit": "ms",
            "range": 2.02
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "29e7947401650114539a92b0f9c54dbc0184e9ba",
          "message": "chore: rename project to padwan-ai (#79)\n\n* feat: add native JEV support and weekly model tracking\n\n* refactor(typesafe): let the API validate payloads, reuse env_api_key\n\nDrop the client-side question/JSON normalizers and per-field response\nchecks; the server 422s bad input and _error_message already surfaces\nthe detail. Remove the redundant SystemOneRequest and JSONValue types,\nthe tests that covered them, and the duplicated e2e/drift docs section.\n\n* chore: rename project to padwan-ai\n\nBREAKING: import path `padwan_llm` -> `padwan_ai`, PyPI dist `padwan-llm` -> `padwan-ai`,\nconsole script `padwan-llm` -> `padwan-ai`. No compat shim is kept.\n\nAlso renamed: logger and OTel instrumentation scope (`padwan_ai`), span attribute\nnamespace (`padwan_ai.*`), MCP clientInfo.name default (`padwan-ai`), Grafana dashboard\nuid (`padwan-ai-genai`), Langfuse dev project id, docs site and repo URLs.\n\n* chore: add padwan-llm tombstone package depending on padwan-ai",
          "timestamp": "2026-09-19T23:23:01+02:00",
          "tree_id": "ab2d94d9f8a7c4ba920bb81098d7482104c5764a",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/29e7947401650114539a92b0f9c54dbc0184e9ba"
        },
        "date": 1789853326080,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 54.93,
            "unit": "ms",
            "range": 0.84
          },
          {
            "name": "padwan_ai.openai",
            "value": 206.48,
            "unit": "ms",
            "range": 3.6
          },
          {
            "name": "padwan_ai.otel",
            "value": 257.09,
            "unit": "ms",
            "range": 8.21
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bd01e4596d73165b2c121f7e0b020eca04401a1e",
          "message": "chore(release): release 0.11.0 (#80)",
          "timestamp": "2026-09-19T23:45:50+02:00",
          "tree_id": "3de39f38c0e7091d1216959fe6e385b5fa65b51c",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/bd01e4596d73165b2c121f7e0b020eca04401a1e"
        },
        "date": 1789854750926,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 57.26,
            "unit": "ms",
            "range": 1.28
          },
          {
            "name": "padwan_ai.openai",
            "value": 217.46,
            "unit": "ms",
            "range": 4.7
          },
          {
            "name": "padwan_ai.otel",
            "value": 253.28,
            "unit": "ms",
            "range": 5.99
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "310eb63113e6984abe022a805d7a0143d5e375c3",
          "message": "docs: revamp README into a short landing page (#82)\n\n* docs: revamp README into a short landing page\n\n* docs(readme): add PyPI version, Python and CI badges\n\n* build: add trove classifiers so the PyPI Python-versions badge renders",
          "timestamp": "2026-09-20T10:21:47+02:00",
          "tree_id": "4b0a2b95485d5b5b25e2448308815bc251014df6",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/310eb63113e6984abe022a805d7a0143d5e375c3"
        },
        "date": 1789892846715,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 54.05,
            "unit": "ms",
            "range": 1.08
          },
          {
            "name": "padwan_ai.openai",
            "value": 202.44,
            "unit": "ms",
            "range": 2.37
          },
          {
            "name": "padwan_ai.otel",
            "value": 238.58,
            "unit": "ms",
            "range": 2.09
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "julien.brayere@obitrain.com",
            "name": "Julien Brayere",
            "username": "Andarius"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2853d674204fde8b6b32c0888291e518e28d16c4",
          "message": "docs: mark TypeSafe (JEV) as experimental (#84)",
          "timestamp": "2026-09-20T10:38:23+02:00",
          "tree_id": "5e954c00d8a906baefd99976e75086a57646d1e4",
          "url": "https://github.com/polarsen-io/padwan-ai/commit/2853d674204fde8b6b32c0888291e518e28d16c4"
        },
        "date": 1789893579450,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "padwan_ai (facade)",
            "value": 44.61,
            "unit": "ms",
            "range": 2.32
          },
          {
            "name": "padwan_ai.openai",
            "value": 159.61,
            "unit": "ms",
            "range": 8
          },
          {
            "name": "padwan_ai.otel",
            "value": 199.24,
            "unit": "ms",
            "range": 8.94
          }
        ]
      }
    ]
  }
}