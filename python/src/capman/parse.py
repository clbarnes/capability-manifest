import tomllib
import tomli_w
from typing import IO
from .types import Manifest


def read_toml_str(s: str) -> Manifest:
    return Manifest.from_dict(tomllib.loads(s))


def read_toml(f: IO[bytes]) -> Manifest:
    return Manifest.from_dict(tomllib.load(f))


def write_toml_str(manifest: Manifest) -> str:
    return tomli_w.dumps(manifest.to_dict())


def write_toml(manifest: Manifest, f: IO[bytes]):
    return tomli_w.dump(manifest.to_dict(), f)
