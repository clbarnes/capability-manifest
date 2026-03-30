from ..types import ResolutionCache, resolve_import
from ..resolver import DefaultFetcher
from typing import Annotated
from typer import Typer, echo, Option, Argument
from pathlib import Path
import tomli_w
from tabulate import tabulate

app = Typer(name="capman", no_args_is_help=True)


@app.command()
def resolve(
    paths: Annotated[
        list[str], Argument(help="List of paths or URLs to resolve and merge.")
    ],
    out_file: Annotated[
        Path | None, Option("--out-file", "-o", help="Path to write output file.")
    ] = None,
):
    if not paths:
        echo("Nothing to do", err=True)
    fetcher = DefaultFetcher()
    cache = ResolutionCache()

    m, *others = (resolve_import(p, fetcher, cache) for p in paths)

    merged = m.merge(*others)
    d = merged.to_dict()
    s = tomli_w.dumps(d)
    if out_file is None:
        echo(s)
    else:
        with out_file.open("w") as f:
            echo(s, f)


@app.command()
def table(
    paths: Annotated[list[str], Argument(help="List of paths or URLs to compare.")],
    out_file: Annotated[
        Path | None,
        Option(
            "--out-file",
            "-o",
            help="Path to write output file, possibly implying an output format.",
        ),
    ] = None,
    format: Annotated[str | None, Option(help="Explicit output format.")] = None,
):
    """Create a table for comparing capabilities.

    Uses tabulate's format options internally; see [1] for accepted formats.
    Some formats can be guessed from `out_file`.

    1: <https://github.com/astanin/python-tabulate?tab=readme-ov-file#table-format>
    """
    if not paths:
        echo("Nothing to do", err=True)
    fetcher = DefaultFetcher()
    cache = ResolutionCache()

    manifests = [resolve_import(p, fetcher, cache) for p in paths]
    m, *others = manifests
    merged = m.merge(*others)

    table = []
    for k in merged.capabilities:
        row = [k]
        for m in manifests:
            cap = m.capabilities.get(k)
            if cap is not None:
                if cap.support:
                    row.append("✅")
                    continue
                elif cap.support is False:
                    row.append("❌")
                    continue
            row.append("")

        cap = merged.capabilities[k]
        row.append(cap.description or "")
        row.append(cap.url or "")
        table.append(row)

    if format is None and out_file is not None:
        ext = out_file.suffix.lstrip(".").lower()
        match ext:
            case "adoc":
                format = "asciidoc"
            case "md" | "markdown":
                format = "github"
            case "tex":
                format = "latex"

    headers = ["feature", *paths, "description", "url"]
    s = tabulate(table, headers=headers)
    if out_file is None:
        echo(s)
    else:
        with out_file.open("w") as f:
            echo(s, f)


@app.command()
def stub(
    paths: Annotated[list[str], Argument(help="Source manifests to combine.")],
    out_file: Annotated[
        Path | None, Option("--out-file", "-o", help="Path to write output file.")
    ] = None,
    supported: bool = False,
    skip_imports: bool = False,
    description: bool = False,
    url: bool = False,
):
    if not paths:
        echo("Nothing to do", err=True)
    fetcher = DefaultFetcher()
    cache = ResolutionCache()

    m, *others = (resolve_import(p, fetcher, cache) for p in paths)
    merged = m.merge(*others)
    to_remove = []
    for key, cap in merged.capabilities.items():
        if cap.support and not skip_imports and not supported:
            to_remove.append(key)
            continue
        if not description:
            cap.description = None
        if not url:
            cap.url = None
    for k in to_remove:
        merged.capabilities.pop(k)

    if not skip_imports:
        merged.imports.extend(paths)

    d = merged.to_dict()
    s = tomli_w.dumps(d)
    if out_file is None:
        echo(s)
    else:
        with out_file.open("w") as f:
            echo(s, f)


def main():
    app()
