import importlib.util
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
from bs4 import BeautifulSoup

_INTRO, _OWN, _END = (
    "<p>Intro stays.</p>",
    "<p>The client retries transient failures.</p>",
    "<p>Closing note.</p>",
)
_BASE = [_INTRO, _OWN, _END]


@pytest.fixture(scope="module")
def mark_changes() -> Iterator[ModuleType]:
    path = Path(__file__).resolve().parents[1] / "bin/docs-preview/mark_changes.py"
    spec = importlib.util.spec_from_file_location("padwan_mark_changes", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load docs preview script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


def _page(blocks: list[str]) -> BeautifulSoup:
    html = f'<article class="md-content__inner md-typeset">{"".join(blocks)}</article>'
    return BeautifulSoup(
        f"<html><head></head><body>{html}</body></html>", "html.parser"
    )


@pytest.mark.parametrize(
    "base, preview, counts, marks",
    [
        pytest.param(_BASE, _BASE, (0, 0, 0), [], id="unchanged"),
        pytest.param(
            _BASE, [*_BASE, "<p>Brand new.</p>"], (1, 0, 0), ["added"], id="appended"
        ),
        pytest.param(
            _BASE,
            [
                _INTRO,
                "<p>The client retries transient failures with a backoff.</p>",
                _END,
            ],
            (0, 1, 0),
            ["changed"],
            id="edited",
        ),
        pytest.param(
            _BASE,
            [
                _INTRO,
                "<p>Brand new.</p>",
                "<p>The client retries all transient failures.</p>",
                _END,
            ],
            (1, 1, 0),
            ["added", "changed"],
            id="insert-next-to-edit",
        ),
        pytest.param(_BASE, [_INTRO, _OWN], (0, 0, 1), [], id="removed"),
        pytest.param(
            ['<p><a href="../x/">Link</a></p>'],
            ['<p><a href="../../x/">Link</a></p>'],
            (0, 0, 0),
            [],
            id="link-target-ignored",
        ),
        pytest.param(
            ['<div class="highlight"><pre><code>a = 1</code></pre></div>'],
            ['<div class="highlight"><pre><code>a = 2</code></pre></div>'],
            (0, 1, 0),
            ["changed"],
            id="code-block-is-one-block",
        ),
    ],
)
def test_diff_page(
    mark_changes: ModuleType,
    base: list[str],
    preview: list[str],
    counts: tuple[int, int, int],
    marks: list[str],
) -> None:
    preview_soup = _page(preview)
    diff = mark_changes.diff_page(_page(base), preview_soup, "p/")
    assert (diff.added, diff.changed, diff.removed) == counts
    assert [b["data-pr-diff"] for b in preview_soup.select("[data-pr-diff]")] == marks


def test_new_page_is_flagged_without_block_marks(mark_changes: ModuleType) -> None:
    preview = _page(["<p>Hello.</p>"])
    diff = mark_changes.diff_page(None, preview, "new/")
    assert diff.new_page and not preview.select("[data-pr-diff]")


def test_site_badges_relative_sidebar_links(
    mark_changes: ModuleType, tmp_path: Path
) -> None:
    """Material sidebar links are relative to the page; the badge and its style land on every page."""
    nav = '<nav><a class="md-nav__link" href="../a/">A</a><a class="md-nav__link" href="../b/">B</a></nav>'
    for root, a_text in ((tmp_path / "prod", "old"), (tmp_path / "preview", "new")):
        for page, text in (("a", a_text), ("b", "same"), ("gone", "bye")):
            if page == "gone" and root.name == "preview":
                continue
            (root / page).mkdir(parents=True)
            (root / page / "index.html").write_text(
                f'<html><head></head><body>{nav}<article class="md-content__inner"><p>{text}</p></article></body></html>'
            )
    changed, removed = mark_changes.mark_site(tmp_path / "prod", tmp_path / "preview")
    assert [d.route for d in changed] == ["a/"]
    assert removed == ["gone/"]
    unchanged = (tmp_path / "preview" / "b" / "index.html").read_text()
    assert unchanged.count('<span class="pr-diff-badge">') == 1
    assert unchanged.count('<style id="pr-diff">') == 1
    assert "pr-diff-bar" in (tmp_path / "preview" / "a" / "index.html").read_text()


def test_render_comment_lists_pages(mark_changes: ModuleType) -> None:
    diff = mark_changes.PageDiff(route="clients/openai/", added=1, changed=2)
    text = mark_changes.render_comment([diff], ["old/"], "https://x/pr-preview/pr-7/")
    assert (
        "[`/clients/openai/`](https://x/pr-preview/pr-7/clients/openai/) · 1 added · 2 changed · 0 removed"
        in text
    )
    assert "✖ `/old/` · page removed" in text
