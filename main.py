#!/usr/bin/env python3
from __future__ import annotations
from abc import ABC
from collections.abc import Callable, Iterable
import datetime as dt
from itertools import chain
from pathlib import Path
from abc import abstractmethod
from typing import Self, Hashable
from pydantic import BaseModel, Field
import networkx as nx
from pydantic_yaml import parse_yaml_file_as


class Mergeable(ABC):
    @abstractmethod
    def merge(self, *others: Self) -> Self: ...


class Zarr3(BaseModel, Mergeable):
    codec: dict[str, Codec] = Field(default_factory=dict)
    data_type: dict[str, DataType] = Field(default_factory=dict)
    chunk_grid: dict[str, ChunkGrid] = Field(default_factory=dict)
    chunk_key_encoding: dict[str, ChunkKeyEncoding] = Field(default_factory=dict)
    store: dict[str, Store] = Field(default_factory=dict)
    storage_transformer: dict[str, StorageTransformer] = Field(default_factory=dict)


def merge_dicts[T: HasMetadata](d1: dict[str, T], d2: dict[str, T]) -> dict[str, T]:
    g: nx.Graph[str] = nx.Graph()
    index = 0
    for k, value in chain(d1.items(), d2.items()):
        if not g.has_node(k):
            g.add_node(k, priority=index, value=value)
            index += 1
        for alias in value.meta.alias:
            if not g.has_node(alias):
                g.add_node(alias, priority=index, value=value)
                index += 1
            g.add_edge(k, alias)
    return dict()


class Spec(BaseModel, Mergeable):
    zarr3: Zarr3 = Field(default_factory=Zarr3)


def same_value[T](versions: Iterable[T]) -> T:
    this = None
    for v in versions:
        if this is None:
            this = v
        elif this != v:
            raise ValueError("field mismatch")
    if this is None:
        raise ValueError("no field values")
    return this


def latest_opt_date(dates: Iterable[dt.date | None]) -> dt.date | None:
    latest = None
    for d in dates:
        if d is None:
            continue
        if latest is None or d > latest:
            latest = d
    return latest


def first_some[T](items: Iterable[T | None]) -> T | None:
    for i in items:
        if i is not None:
            return i
    return None


def merge_any[T, R](
    accessor: Callable[[T], R],
    merger: Callable[[Iterable[R]], R],
    *objs: T,
) -> R:
    return merger(accessor(obj) for obj in objs)


def sorted_set[T: Hashable](items: Iterable[Iterable[T]]) -> list[T]:
    return sorted(set(chain.from_iterable(items)))  # type:ignore


def merged[T: Mergeable](items: Iterable[T]) -> T:
    it = iter(items)

    try:
        first = next(it)
    except StopIteration as e:
        raise ValueError("no items given") from e
    return first.merge(*it)


class Root(BaseModel, Mergeable):
    version: int = 1
    spec: Spec = Field(default_factory=Spec)
    is_definition: bool = False
    last_updated: dt.date | None = None

    def merge(self, *others: Self) -> Self:
        return type(self)(
            version=merge_any(lambda x: x.version, same_value, self, *others),
            is_definition=merge_any(
                lambda x: x.is_definition, same_value, self, *others
            ),
            last_updated=merge_any(
                lambda x: x.last_updated, latest_opt_date, self, *others
            ),
            spec=merge_any(lambda x: x.spec, merged, self, *others),
        )


class Metadata(BaseModel, Mergeable):
    description: str | None = None
    url: str | None = None
    notes: str | None = None
    alias: list[str] = Field(default_factory=list)

    def merge(self, *others: Self) -> Self:
        aliases = set(self.alias)
        aliases.update(chain.from_iterable((o.alias for o in others)))
        return type(self)(
            description=merge_any(lambda x: x.description, first_some, self, *others),
            url=merge_any(lambda x: x.description, first_some, self, *others),
            notes=merge_any(lambda x: x.notes, first_some, self, *others),
            alias=merge_any(lambda x: x.alias, sorted_set, self, *others),
        )


class HasMetadata(BaseModel, Mergeable, ABC):
    meta: Metadata = Field(default_factory=Metadata)

    def merge(self, *others: Self) -> Self:
        return type(self)(meta=self.meta.merge(*(o.meta for o in others)))


class Codec(HasMetadata):
    decode: bool = False
    decode_partial: bool = False
    encode: bool = False
    encode_partial: bool = False

    def merge(self, *others: Self) -> Self:
        return type(self)(
            decode=self.decode or any(o.decode for o in others),
            decode_partial=self.decode_partial or any(o.decode_partial for o in others),
            encode=self.encode or any(o.encode for o in others),
            encode_partial=self.encode_partial or any(o.encode_partial for o in others),
            meta=self.meta.merge(*(o.meta for o in others)),
        )


class HasSupport(HasMetadata, ABC):
    support: bool = False

    def merge(self, *others: Self) -> Self:
        return type(self)(
            support=self.support or any(o.support for o in others),
            meta=self.meta.merge(*(o.meta for o in others)),
        )


class DataType(HasSupport):
    pass


class ChunkGrid(HasSupport):
    pass


class ChunkKeyEncoding(HasSupport):
    pass


class Store(HasMetadata):
    read: bool = False
    read_partial: bool = False
    list: bool = False
    write: bool = False
    write_partial: bool = False

    def merge(self, *others: Self) -> Self:
        return type(self)(
            read=self.read or any((o.read for o in others)),
            read_partial=self.read_partial or any((o.read_partial for o in others)),
            list=self.list or any((o.list for o in others)),
            write=self.write or any((o.write for o in others)),
            write_partial=self.write_partial or any((o.write_partial for o in others)),
        )


class StorageTransformer(HasMetadata):
    def merge(self, *others: Self) -> Self:
        return self


def main():
    project_dir = Path(__file__).resolve().parent
    examples_dir = project_dir / "examples"
    zarr_specs_cap_path = examples_dir / "zarr-specs" / "capabilities.yaml"
    root = parse_yaml_file_as(Root, zarr_specs_cap_path)
    print(root)

if __name__ == "__main__":
    main()