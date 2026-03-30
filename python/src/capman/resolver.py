from abc import ABC, abstractmethod
from typing import Callable
from urllib.parse import urlsplit, urljoin
import requests
import os


class ResolutionError(RuntimeError):
    def __init__(self, iri: str, canonicalized: str | None = None, *args) -> None:
        self.iri = iri
        self.canonicalized = canonicalized
        if canonicalized == iri:
            msg = f"could not resolve IRI Reference: {iri}"
        else:
            msg = f"could not resolve IRI Reference: {iri} canonicalized to {canonicalized}"
        super().__init__(msg, *args)


class UnknownSchemeError(ValueError):
    def __init__(self, scheme: str, known_schemes: tuple[str, ...], *args) -> None:
        self.scheme = scheme
        self.known_schemes = known_schemes
        msg = f"Unknown scheme '{scheme}'; expected one of {known_schemes}"
        super().__init__(msg, *args)

    @classmethod
    def check_scheme(cls, scheme: str, known_schemes: tuple[str, ...], *args):
        if scheme not in known_schemes:
            raise cls(scheme, known_schemes)


type TCanonicalizer = Callable[[str], str]
type TFetcher = Callable[[str], bytes | None]
type Cache = dict[str, bytes]


class Canonicalizer(ABC):
    @abstractmethod
    def __call__(self, iri: str) -> str: ...


class BaseFetcher(ABC):
    schemes: tuple[str, ...]

    def check_scheme(self, iri: str):
        split = urlsplit(iri)
        UnknownSchemeError.check_scheme(split.scheme, self.schemes)

    @abstractmethod
    def __call__(self, iri: str) -> bytes | None: ...


class UrlCanonicalizer(Canonicalizer):
    def __init__(self, relative_to: str) -> None:
        if not urlsplit(relative_to).scheme:
            relative_to = f"file:{os.path.realpath(relative_to)}"
        self.relative_to = relative_to

    def __call__(self, iri: str) -> str:
        return urljoin(self.relative_to, iri)


class HttpFetcher(BaseFetcher):
    schemes = ("http", "https")

    def __init__(self, session: requests.Session | None = None):
        if session is None:
            session = requests.Session()
        self.session = session

    def __call__(self, iri: str) -> bytes | None:
        split = urlsplit(iri)
        UnknownSchemeError.check_scheme(split.scheme, self.schemes)
        rsp = self.session.get(iri)
        if rsp.status_code == 404:
            return None
        rsp.raise_for_status()
        return rsp.content


class FileFetcher(BaseFetcher):
    schemes = ("file", "fs", "filesystem")

    def __call__(self, iri: str) -> bytes | None:
        split = urlsplit(iri)
        UnknownSchemeError.check_scheme(split.scheme, self.schemes)

        if not os.path.exists(split.path):
            return None

        with open(split.path, "rb") as f:
            return f.read()


class FallbackFetcher(BaseFetcher):
    def __init__(self, fetchers: list[TFetcher]) -> None:
        schemes = set()
        for f in fetchers:
            if isinstance(f, BaseFetcher):
                schemes.update(f.schemes)
        self.schemes = tuple(sorted(schemes))
        self.fetchers = fetchers

    def __call__(self, iri: str) -> bytes | None:
        for f in self.fetchers:
            try:
                return f(iri)
            except UnknownSchemeError:
                continue
        raise UnknownSchemeError(urlsplit(iri).scheme, self.schemes)


class DefaultFetcher(FallbackFetcher):
    def __init__(self, session: requests.Session | None = None) -> None:
        super().__init__([HttpFetcher(session), FileFetcher()])
