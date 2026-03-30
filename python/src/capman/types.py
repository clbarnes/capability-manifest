from __future__ import annotations
from abc import ABC
from collections import defaultdict
from collections.abc import Callable, Iterable
from abc import abstractmethod
from copy import copy
import itertools
import os
import tomllib
from typing import Self, Any
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from .resolver import DefaultFetcher, TFetcher, UrlCanonicalizer


class AsDict(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    @abstractmethod
    def from_dict(cls, d: dict[str, Any]) -> Self: ...


class Mergeable(ABC):
    @abstractmethod
    def merge(self, *others: Self) -> Self: ...


def first_non_null[T](*options: T | None) -> T | None:
    for o in options:
        if o is not None:
            return o
    return None


@dataclass
class Capability(Mergeable, AsDict):
    description: str | None = None
    url: str | None = None
    support: bool | None = None

    def merge(self, *others: Self) -> Self:
        return type(self)(
            description=first_non_null(*(o.description for o in others)),
            url=first_non_null(*(o.url for o in others)),
            support=any(o.support for o in others),
        )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Self:
        desc = d.get("description")
        if desc is not None:
            desc = str(desc)
        url = d.get("url")
        if url is not None:
            url = str(url)
        support = d.get("support")
        if support is not None and not isinstance(support, bool):
            support = bool(support)
        return cls(desc, url, support)

    def to_dict(self) -> dict[str, Any]:
        d = dict()
        if self.description is not None:
            d["description"] = self.description
        if self.url is not None:
            d["url"] = self.url
        if self.support is not None:
            d["support"] = self.support
        return d


class NotGiven:
    pass


def merge_same[T](*args: T, default: NotGiven | T = NotGiven()) -> T:
    if not args:
        if isinstance(default, NotGiven):
            raise ValueError("No arguments or default given")
        return default
    arg, *others = args
    for o in others:
        if o != arg:
            raise ValueError("Different arguments given")
    return arg


def ensure_same[T](args: Iterable[T]) -> T:
    not_given = NotGiven()
    out: NotGiven | T = not_given
    for a in args:
        if out is not_given:
            out = a
        elif a != out:
            raise ValueError("arguments are not the same")
    if isinstance(out, NotGiven):
        raise ValueError("no arguments given")
    return out


def merge_any[T, C](
    accessor: Callable[[C], T], merger: Callable[[Iterable[T]], T], *args: C
) -> T:
    return merger(accessor(a) for a in args)


@dataclass
class Manifest(Mergeable, AsDict):
    version: int
    imports: list[str] = field(default_factory=list)
    capabilities: dict[str, Capability] = field(default_factory=dict)

    def merge(self, *others: Self) -> Self:
        if not others:
            return copy(self)

        version = merge_any(lambda x: x.version, ensure_same, self, *others)
        all_caps: defaultdict[str, list[Capability]] = defaultdict(list)
        for item in (self, *others):
            for key, c in item.capabilities.items():
                all_caps[key].append(c)
        capabilities = {
            k: Capability.merge(*values) for k, values in sorted(all_caps.items())
        }
        visited = set(self.imports)
        merged_imports = list(self.imports)
        for imp in itertools.chain.from_iterable(o.imports for o in others):
            if not is_absolute(imp):
                raise ValueError("cannot merge relative imports")
            if imp in visited:
                continue
            merged_imports.append(imp)
            visited.add(imp)

        return type(self)(
            version=version,
            imports=merged_imports,
            capabilities=capabilities,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "imports": self.imports,
            "capabilities": {k: v.to_dict() for k, v in self.capabilities.items()},
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Self:
        version = int(d["version"])
        capabilities = {
            k: Capability.from_dict(v) for k, v in d["capabilities"].items()
        }
        return cls(version, d.get("imports", []), capabilities)


def is_absolute(imp: str) -> bool:
    p = urlsplit(imp).path
    return p.startswith(("/", os.path.sep))


class ResolutionCache:
    def __init__(self) -> None:
        self.in_progress: set[str] = set()
        self.completed: dict[str, Manifest] = dict()


def resolve_import(
    path: str | os.PathLike,
    fetcher: TFetcher | None = None,
    cache: ResolutionCache | None = None,
) -> Manifest:
    if fetcher is None:
        fetcher = DefaultFetcher()
    if cache is None:
        cache = ResolutionCache()

    canonicalizer = UrlCanonicalizer(str(path))
    canonical = canonicalizer.relative_to
    if canonical in cache.in_progress:
        raise ValueError("circular import detected")
    b = fetcher(canonical)
    if b is None:
        raise FileNotFoundError(f"{canonical} (from {path}) not found")
    d = tomllib.loads(b.decode())
    m = Manifest.from_dict(d)
    cache.in_progress.add(canonical)
    others = []
    for i in m.imports:
        i_c = canonicalizer(i)
        if cached := cache.completed.get(i_c):
            return cached
        other = resolve_import(i_c, fetcher, cache)
        others.append(other)

    m.imports.clear()

    cache.in_progress.remove(canonical)
    m2 = m.merge(*others)
    cache.completed[canonical] = m2

    return m2
