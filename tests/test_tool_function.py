from collections.abc import Awaitable, Callable, Sequence
from contextlib import nullcontext
from dataclasses import dataclass
from importlib.util import find_spec
from typing import Annotated, Any, Literal, cast, get_type_hints

import msgspec
import pydantic
import pytest

from padwan_ai.tools import (
    MsgspecValidator,
    PydanticValidator,
    ToolValidator,
    _resolve,
    tool,
)

BACKENDS = [
    pytest.param(
        lib,
        marks=pytest.mark.skipif(find_spec(lib) is None, reason=f"{lib} not installed"),
        id=lib,
    )
    for lib in ("msgspec", "pydantic")
]


@dataclass
class Backend:
    name: Literal["msgspec", "pydantic"]
    search: Callable[..., Awaitable[Any]]
    error: type[Exception]


def _make(
    name: Literal["msgspec", "pydantic"], ref: type, meta: Any, error: type[Exception]
) -> Backend:
    async def search(query: str, limit: Annotated[int, meta] = 5) -> list[Any]:
        """Search the references by name."""
        return [ref(id=1, name=f"{query} {limit}")]

    return Backend(name, search, error)


@pytest.fixture(params=BACKENDS)
def backend(request: pytest.FixtureRequest) -> Backend:
    if request.param == "msgspec":
        import msgspec

        class Ref(msgspec.Struct):
            id: int
            name: str

        return _make("msgspec", Ref, msgspec.Meta(ge=1, le=10), msgspec.ValidationError)
    import pydantic

    class Model(pydantic.BaseModel):
        id: int
        name: str

    return _make(
        "pydantic", Model, pydantic.Field(ge=1, le=10), pydantic.ValidationError
    )


def test_schema_and_metadata_come_from_the_signature(backend: Backend) -> None:
    t = tool(backend.search, validator=backend.name)
    assert (t.name, t.description) == ("search", "Search the references by name.")
    assert t.input_schema["properties"]["query"]["type"] == "string"
    # pydantic adds a per-property title, msgspec does not
    limit = {"type": "integer", "minimum": 1, "maximum": 10, "default": 5}
    assert limit.items() <= t.input_schema["properties"]["limit"].items()
    assert t.input_schema["required"] == ["query"]
    assert "title" not in t.input_schema
    t = tool(
        backend.search, name="find", description="Find things.", validator=backend.name
    )
    assert (t.name, t.description) == ("find", "Find things.")


@pytest.mark.parametrize(
    ("args", "expected", "match"),
    [
        pytest.param(
            {"query": "pelle", "limit": "3"},
            [{"id": 1, "name": "pelle 3"}],
            None,
            id="coerces_and_dumps",
        ),
        pytest.param({"limit": 3}, None, "query", id="missing_required"),
        pytest.param(
            {"query": "pelle", "limit": -100},
            None,
            r"(>=|greater than or equal to) 1",
            id="constraint_violated",
        ),
        pytest.param({"query": "pelle", "limit": "many"}, None, "int", id="wrong_type"),
    ],
)
async def test_handler_validates_before_calling(
    backend: Backend, args: dict[str, Any], expected: Any, match: str | None
) -> None:
    raises = pytest.raises(backend.error, match=match) if match else nullcontext()
    with raises:
        assert (
            await tool(backend.search, validator=backend.name).handler(args) == expected
        )


async def _unannotated(query, limit: int = 1) -> str:  # type: ignore[no-untyped-def]
    return query


async def _positional_only(query: str, /) -> str:
    return query


async def _var_keyword(query: str, **extra: Any) -> str:
    return query


async def _private_name(_id: str) -> str:
    return _id


async def _shadows_base_model(model_fields: str) -> str:
    return model_fields


async def _model_prefix(model_name: str) -> str:
    return model_name


@pytest.mark.parametrize(
    ("fn", "validator", "match"),
    [
        pytest.param(
            _unannotated, "msgspec", "needs a type annotation", id="unannotated"
        ),
        pytest.param(
            _positional_only, "msgspec", "passable by keyword", id="positional_only"
        ),
        pytest.param(_var_keyword, "msgspec", "passable by keyword", id="var_keyword"),
        pytest.param(
            _private_name,
            "pydantic",
            "reserved by pydantic",
            id="pydantic_drops_private_names",
        ),
        pytest.param(
            _shadows_base_model,
            "pydantic",
            "reserved by pydantic",
            id="pydantic_shadows_base_model",
        ),
        pytest.param(
            _model_prefix, "pydantic", None, id="pydantic_model_prefix_alone_is_fine"
        ),
    ],
)
def test_signature_checks_at_build_time(
    fn: Any, validator: str, match: str | None
) -> None:
    if find_spec(validator) is None:
        pytest.skip(f"{validator} not installed")
    raises = pytest.raises(TypeError, match=match) if match else nullcontext()
    with raises:
        tool(fn, validator=cast(Any, validator))


@pytest.mark.parametrize(
    ("installed", "expected", "raises"),
    [
        pytest.param({"msgspec"}, MsgspecValidator, nullcontext(), id="only_msgspec"),
        pytest.param(
            {"pydantic"}, PydanticValidator, nullcontext(), id="only_pydantic"
        ),
        pytest.param(
            set(),
            None,
            pytest.raises(ImportError, match="pip install msgspec or pydantic"),
            id="none_installed",
        ),
        pytest.param(
            {"msgspec", "pydantic"},
            None,
            pytest.raises(ValueError, match="pass validator="),
            id="both_installed",
        ),
    ],
)
def test_default_validator_is_the_only_installed_one(
    monkeypatch: pytest.MonkeyPatch, installed: set[str], expected: Any, raises: Any
) -> None:
    monkeypatch.setattr(
        "padwan_ai.tools.find_spec",
        lambda name: object() if name in installed else None,
    )
    with raises:
        assert isinstance(_resolve(None, {}), expected)


async def test_a_custom_validator_instance_is_used_as_is() -> None:
    class Passthrough:
        def compile(
            self, name: str, fields: Sequence[Any]
        ) -> tuple[dict[str, Any], Any]:
            return {"type": "object", "x": name}, dict

        def dump(self, result: Any) -> Any:
            return {"wrapped": result}

    async def echo(query: str) -> str:
        return query

    t = tool(echo, validator=cast(ToolValidator, Passthrough()))
    assert t.input_schema == {"type": "object", "x": "echo_args"}
    assert await t.handler({"query": "hi"}) == {"wrapped": "hi"}


@pytest.mark.skipif(
    find_spec("msgspec") is None or find_spec("pydantic") is None,
    reason="needs both libs",
)
@pytest.mark.parametrize(
    ("case", "expected"),
    [
        pytest.param("msgspec_meta", MsgspecValidator, id="msgspec_meta"),
        pytest.param("pydantic_field", PydanticValidator, id="pydantic_field"),
        pytest.param("struct_in_return", MsgspecValidator, id="struct_in_return"),
        pytest.param(
            "base_model_in_optional", PydanticValidator, id="base_model_in_optional"
        ),
        pytest.param("mixed", None, id="mixed_raises"),
    ],
)
def test_default_validator_follows_the_annotations(
    case: str, expected: type | None
) -> None:
    import msgspec
    import pydantic

    class Ref(msgspec.Struct):
        id: int

    class Model(pydantic.BaseModel):
        id: int

    async def msgspec_meta(n: Annotated[int, msgspec.Meta(ge=1)]) -> int:
        return n

    async def pydantic_field(n: Annotated[int, pydantic.Field(ge=1)]) -> int:
        return n

    async def struct_in_return(query: str) -> list[Ref]:
        return []

    async def base_model_in_optional(item: Model | None = None) -> str:
        return ""

    async def mixed(n: Annotated[int, msgspec.Meta(ge=1)]) -> Model:
        return Model(id=n)

    hints = get_type_hints(locals()[case], include_extras=True)
    raises = (
        pytest.raises(ValueError, match="mix msgspec and pydantic")
        if expected is None
        else nullcontext()
    )
    with raises:
        assert type(_resolve(None, hints)) is expected


class _MsgspecNode(msgspec.Struct):
    children: list["_MsgspecNode"] = []


class _PydanticNode(pydantic.BaseModel):
    children: list["_PydanticNode"] = []


@pytest.mark.parametrize(
    "validator, node",
    [
        pytest.param(MsgspecValidator(), _MsgspecNode, id="msgspec"),
        pytest.param(PydanticValidator(), _PydanticNode, id="pydantic"),
    ],
)
def test_adapt_keeps_a_recursive_class_reachable(
    validator: ToolValidator, node: type
) -> None:
    schema, convert = validator.adapt(node)
    assert "properties" in schema and "title" not in schema
    assert (
        "children" in schema["$defs"][node.__name__]["properties"]
    )  # inner $ref resolves
    tree = convert({"children": [{"children": []}]})
    assert len(tree.children) == 1
