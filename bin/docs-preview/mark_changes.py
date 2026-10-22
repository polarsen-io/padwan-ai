#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["beautifulsoup4>=4.13"]
# ///
# DESCRIPTION: mark what a docs PR preview changes against the production site, for the PR comment
# USAGE: mark_changes.py <production site dir> <preview site dir> <preview url> <comment.md>
import posixpath
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from bs4 import BeautifulSoup, Tag

__all__ = ("PageDiff", "diff_page", "mark_site", "render_comment")

CONTENT = ".md-content__inner"
# Leaf blocks compared one by one; components are compared whole.
_BLOCKS = {"p", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "dt", "dd"}
_COMPONENTS = ("admonition", "tabbed-set", "highlight")
# Blocks at least this similar count as edited rather than added + removed.
_EDIT_RATIO = 0.5

_HERE = Path(__file__).parent


@dataclass
class PageDiff:
    route: str
    added: int = 0
    changed: int = 0
    removed: int = 0
    new_page: bool = False
    marked: list[Tag] = field(default_factory=list)

    @property
    def any(self) -> bool:
        return self.new_page or bool(self.added or self.changed or self.removed)


def _blocks(soup: BeautifulSoup) -> list[Tag]:
    """Leaf blocks of the page content in document order; a component counts as one block."""
    content = soup.select_one(CONTENT)
    if content is None:
        return []
    found: list[Tag] = []

    def walk(node: Tag) -> None:
        for child in node.children:
            if not isinstance(child, Tag):
                continue
            classes = child.get("class") or []
            if child.name in _BLOCKS or any(c in classes for c in _COMPONENTS):
                found.append(child)
            else:
                walk(child)

    walk(content)
    return found


def _signature(block: Tag) -> str:
    # Text only: links and anchors differ by base path, so no attributes.
    return f"{block.name} {' '.join(block.get_text(' ').split())}"


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def diff_page(
    base: BeautifulSoup | None, preview: BeautifulSoup, route: str
) -> PageDiff:
    """Mark the preview's added/changed blocks against the production page."""
    result = PageDiff(route=route)
    if base is None:
        result.new_page = True
        return result
    old, new = _blocks(base), _blocks(preview)
    old_sigs, new_sigs = [_signature(b) for b in old], [_signature(b) for b in new]
    matcher = SequenceMatcher(None, old_sigs, new_sigs, autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        # In a replaced run, a new block close to an unused old one is an edit, anything else is new.
        unused = list(range(i1, i2))
        for j in range(j1, j2):
            best = max(
                unused,
                key=lambda i: _similarity(old_sigs[i], new_sigs[j]),
                default=None,
            )
            if (
                best is not None
                and _similarity(old_sigs[best], new_sigs[j]) >= _EDIT_RATIO
            ):
                unused.remove(best)
                kind = "changed"
                result.changed += 1
            else:
                kind = "added"
                result.added += 1
            new[j]["data-pr-diff"] = kind
            result.marked.append(new[j])
        result.removed += len(unused)
    return result


def _add_style(soup: BeautifulSoup) -> None:
    """Add the diff stylesheet once: changed pages need it, and so does every page showing a sidebar badge."""
    if soup.head is not None and soup.select_one("style#pr-diff") is None:
        css = (_HERE / "pr-diff.css").read_text()
        soup.head.append(
            BeautifulSoup(f"<style id=pr-diff>{css}</style>", "html.parser")
        )


def _decorate(soup: BeautifulSoup, diff: PageDiff) -> None:
    """Add the style, script and summary bar to a changed page."""
    content, body = soup.select_one(CONTENT), soup.body
    if content is None or body is None:
        return
    _add_style(soup)
    js = (_HERE / "pr-diff.js").read_text()
    body.append(BeautifulSoup(f"<script>{js}</script>", "html.parser"))
    if diff.new_page:
        summary, buttons = "<b>New page in this PR</b>", ""
    else:
        counts = f"<span class=a>{diff.added} added</span> · <span class=c>{diff.changed} changed</span>"
        summary = f"<b>This PR:</b> {counts} · {diff.removed} removed"
        buttons = "<button data-next>next change</button><button data-toggle>hide changes</button>"
    bar = f"<div class=pr-diff-bar>{summary}{buttons}</div>"
    content.insert(0, BeautifulSoup(bar, "html.parser"))


def _resolve(route: str, href: str) -> str:
    """Route a relative sidebar link points at from the page at `route` (both end with "/", root is "")."""
    target = posixpath.normpath(posixpath.join(route, href))
    return "" if target == "." else target + "/"


def mark_site(base_dir: Path, preview_dir: Path) -> tuple[list[PageDiff], list[str]]:
    """Diff preview pages against production, mark changes, badge the sidebar; returns (changed, removed routes)."""
    pages = {
        p.relative_to(preview_dir).as_posix(): p
        for p in preview_dir.rglob("index.html")
    }
    soups = {
        rel: BeautifulSoup(p.read_text(), "html.parser") for rel, p in pages.items()
    }
    changed: list[PageDiff] = []
    for rel, soup in soups.items():
        if soup.select_one(CONTENT) is None:
            continue
        base_file = base_dir / rel
        base = (
            BeautifulSoup(base_file.read_text(), "html.parser")
            if base_file.is_file()
            else None
        )
        diff = diff_page(base, soup, rel.removesuffix("index.html"))
        if diff.any:
            _decorate(soup, diff)
            changed.append(diff)
    routes = {d.route for d in changed}
    for rel, soup in soups.items():
        route = rel.removesuffix("index.html")
        for link in soup.select("a.md-nav__link[href]"):
            href = str(link["href"])
            if not href.startswith("#") and _resolve(route, href) in routes:
                link.append(
                    BeautifulSoup("<span class=pr-diff-badge>PR</span>", "html.parser")
                )
                _add_style(soup)
    for rel, soup in soups.items():
        pages[rel].write_text(str(soup))
    removed = sorted(
        p.relative_to(base_dir).as_posix().removesuffix("index.html")
        for p in base_dir.rglob("index.html")
        if not p.relative_to(base_dir).as_posix().startswith("pr-preview/")
        and not (preview_dir / p.relative_to(base_dir)).exists()
    )
    return sorted(changed, key=lambda d: d.route), removed


def render_comment(changed: list[PageDiff], removed: list[str], url: str) -> str:
    lines = [f"### Docs preview: {url}", "", "Changes against production:", ""]
    for d in changed:
        what = (
            "new page"
            if d.new_page
            else f"{d.added} added · {d.changed} changed · {d.removed} removed"
        )
        lines.append(
            f"- {'✚' if d.new_page else '✎'} [`/{d.route}`]({url}{d.route}) · {what}"
        )
    lines += [f"- ✖ `/{r}` · page removed" for r in removed]
    if not changed and not removed:
        lines.append("No rendered page changed.")
    lines += [
        "",
        "Changed blocks are highlighted on each page (green added, amber changed); the sidebar marks them **PR**.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    if len(sys.argv) != 5:
        sys.exit(
            "usage: mark_changes.py <production dir> <preview site> <preview url> <comment.md>"
        )
    base_dir, preview_dir, url, out = (
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        sys.argv[3],
        Path(sys.argv[4]),
    )
    changed, removed = mark_site(base_dir, preview_dir)
    out.write_text(render_comment(changed, removed, url))
    print(f"{len(changed)} changed, {len(removed)} removed page(s)")


if __name__ == "__main__":
    main()
