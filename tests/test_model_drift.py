import ast
import importlib.util
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest


@pytest.fixture(scope="module")
def model_drift() -> Iterator[ModuleType]:
    path = Path(__file__).resolve().parents[1] / "bin/drift/check_model_drift.py"
    spec = importlib.util.spec_from_file_location("padwan_model_drift", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load model drift script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


@pytest.mark.parametrize(
    "has_key, payload, failure, expected",
    [
        pytest.param(
            True,
            {"models": [{"name": "jev-latest"}, {"name": "jev-next"}]},
            None,
            (
                "**Available but not tracked**",
                "`jev-next`",
                "**Tracked but absent",
                "`jev-preview`",
            ),
            id="additions-and-absences",
        ),
        pytest.param(
            True,
            {"models": [{"name": "jev-latest"}, {"name": "jev-preview"}]},
            None,
            ("No live drift",),
            id="unchanged",
        ),
        pytest.param(
            False,
            None,
            None,
            ("Skipped", "TYPESAFE_API_KEY is not configured"),
            id="missing-key",
        ),
        pytest.param(
            True,
            None,
            "HTTP 401 Unauthorized",
            ("Failed: HTTP 401 Unauthorized",),
            id="request-failure",
        ),
        pytest.param(
            True,
            {"data": []},
            None,
            ("Failed: response has no models list",),
            id="malformed-list",
        ),
        pytest.param(
            True,
            {"models": [{"name": "jev-latest"}, {"name": 123}]},
            None,
            ("Failed: response contains an invalid model name",),
            id="malformed-name",
        ),
    ],
)
def test_typesafe_drift_report(
    model_drift: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    has_key: bool,
    payload: object,
    failure: str | None,
    expected: tuple[str, ...],
) -> None:
    for provider in (
        "OPENAI",
        "GEMINI",
        "MISTRAL",
        "GROK",
        "ANTHROPIC",
        "TYPESAFE",
        "ELEVENLABS",
    ):
        monkeypatch.delenv(f"{provider}_API_KEY", raising=False)
    if has_key:
        monkeypatch.setenv("TYPESAFE_API_KEY", "test-typesafe-key")
    fetch = Mock(
        return_value=payload,
        side_effect=model_drift.FetchError(failure) if failure else None,
    )
    monkeypatch.setattr(model_drift, "_json_get", fetch)

    model_drift.check()

    report = capsys.readouterr().out.split("## TypeSafe (JEV)", 1)[1]
    for text in expected:
        assert text in report
    assert model_drift.TYPESAFE_MODELS == {"jev-latest", "jev-preview"}
    if has_key:
        fetch.assert_called_once_with(
            "https://api.typesafe.ai/v1/models",
            headers={"Authorization": "Bearer test-typesafe-key"},
        )
    else:
        fetch.assert_not_called()


@pytest.mark.parametrize(
    "has_key, payload, expected",
    [
        pytest.param(
            True,
            [
                {"model_id": "eleven_v3", "can_do_text_to_speech": True},
                {"model_id": "eleven_turbo_v2_5", "can_do_text_to_speech": True},
                {"model_id": "eleven_english_sts_v2", "can_do_text_to_speech": False},
            ],
            {"models": {"eleven_v3"}},
            id="tts-only-without-turbo",
        ),
        pytest.param(
            False,
            None,
            {"skipped": "ELEVENLABS_API_KEY is not configured"},
            id="no-key",
        ),
        pytest.param(
            True,
            {"detail": "x"},
            {"error": "response is not a model list"},
            id="not-list",
        ),
        pytest.param(
            True,
            [{"model_id": 1, "can_do_text_to_speech": True}],
            {"error": "response contains an invalid model id"},
            id="bad-id",
        ),
    ],
)
def test_elevenlabs_tts_models(
    model_drift: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    has_key: bool,
    payload: object,
    expected: dict,
) -> None:
    if has_key:
        monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    else:
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setattr(model_drift, "_json_get", Mock(return_value=payload))

    remote = model_drift._elevenlabs_models("can_do_text_to_speech")

    assert remote.models == expected.get("models", set())
    assert remote.skipped == expected.get("skipped")
    assert remote.error == expected.get("error")


@pytest.mark.parametrize(
    "model_id, expected",
    [
        pytest.param("gemini-3.8-flash-tts", True, id="ga"),
        pytest.param("gemini-2.5-flash-preview-tts", True, id="preview"),
        pytest.param("gemini-3.1-flash-tts-preview", True, id="preview-suffix"),
        pytest.param("gemini-3.8-flash", False, id="chat-model"),
        pytest.param("gemini-3.8-flash-tts-0925", False, id="dated"),
        pytest.param("gemini-2.0-flash-tts", False, id="old"),
    ],
)
def test_is_gemini_tts_model(
    model_drift: ModuleType, model_id: str, expected: bool
) -> None:
    assert model_drift._is_gemini_tts_model(model_id) is expected


def test_gemini_speech_type_drift(
    model_drift: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    from typing import NotRequired, TypedDict

    from padwan_ai.gemini import models

    class VoiceConfig(TypedDict):
        prebuiltVoiceConfig: models.PrebuiltVoiceConfig
        replicatedVoiceConfig: NotRequired[dict]
        voice: NotRequired[str]
        legacyField: NotRequired[str]

    monkeypatch.setattr(models, "VoiceConfig", VoiceConfig)
    drift = model_drift._gemini_speech_type_drift()
    assert set(drift) == {"VoiceConfig"}
    assert drift["VoiceConfig"].added == set()
    assert drift["VoiceConfig"].removed == {"legacy_field"}


_INJECTED_DATE = '2026-01-01", "x": __import__("os").getcwd(), "y": "'


def _deprecated_entries(source: str) -> tuple[ast.Module, dict[str, str]]:
    module = ast.parse(source)
    assign = next(
        node
        for node in module.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "DEPRECATED"
    )
    table = assign.value
    assert isinstance(table, ast.Dict)
    entries: dict[str, str] = {}
    for key, value in zip(table.keys, table.values, strict=True):
        assert isinstance(key, ast.Constant) and isinstance(key.value, str)
        assert isinstance(value, ast.Constant) and isinstance(value.value, str)
        entries[key.value] = value.value
    return module, entries


@pytest.mark.parametrize(
    "model_id, date",
    [
        pytest.param("mistral-large", _INJECTED_DATE, id="quote-in-date"),
        pytest.param("mistral\nlarge", "2026-01-01", id="newline-in-id"),
        pytest.param("mistral-large", "2026-01-01", id="valid-entry"),
    ],
)
def test_deprecations_writer_emits_inert_literals(
    model_drift: ModuleType, tmp_path: Path, model_id: str, date: str
) -> None:
    path = tmp_path / "_deprecations.py"
    model_drift._write_deprecations(path, "Mistral", {model_id: date})

    module, entries = _deprecated_entries(path.read_text(encoding="utf-8"))

    assert entries == {model_id: date}
    assert not any(isinstance(node, ast.Call) for node in ast.walk(module))


@pytest.mark.parametrize(
    "malformed",
    [
        pytest.param("not-a-date", id="words"),
        pytest.param("2026-01-01\n", id="trailing-newline"),
        pytest.param("２０２６-０１-０１", id="fullwidth-digits"),
    ],
)
def test_mistral_deprecations_skip_malformed_dates(
    model_drift: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    malformed: str,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-key")
    fetch = Mock(
        return_value={
            "data": [
                {"id": "mistral-large", "deprecation": "2026-01-01"},
                {"id": "mistral-medium", "deprecation": malformed},
            ]
        }
    )
    monkeypatch.setattr(model_drift, "_json_get", fetch)

    remote = model_drift._mistral_live_models()

    assert remote.deprecations == {"mistral-large": "2026-01-01"}
    warning = capsys.readouterr().err
    assert "invalid date" in warning
    assert "mistral-medium" in warning
