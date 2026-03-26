# Zarr Capability Manifest Specification

## Motivation

Zarr is extensible by design.
What, then, does it mean for a tool to "support Zarr"?
The Zarr Capability Manifest allows tools to provide human-editable, machine-readable summaries of supported features.

## Definitions vs implementations

This schema should be used by projects _defining_ zarr capabilities,
and those _implementing_ them.

Capability definition manifests should describe whether particular kinds of support are possible.
For example, the `crc32c` codec does not allow partial encoding because a partial write will change the final checksum.
The `gzip` codec does not allow partial decoding because of information at the start of the GZip header.

Capability implementation manifests should describe whether the functionality exists.
For example, a new store implementation may only support complete reads and writes in its first release, with partial read and write support to be added later.

## Store names

The Zarr specification requires names for metadata items at extension points.
As stores (and storage layers) are not currently represented by metadata items,
they do not necessarily have canonical names or well-defined aliases.
This specification RECOMMENDS using a URI scheme associated with the store
(e.g. by [fsspec](https://filesystem-spec.readthedocs.io/en/latest/api.html#built-in-implementations)
or [OpenDAL](https://docs.rs/opendal/latest/opendal/services/index.html))

## Conventions

### Requirement levels

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

### Data model

This specification is largely defined using the JSON data model,
with the expectation that data is encoded using YAML 1.2+ (a superset of JSON).

The model is extended to include Maps.
These are JSON objects whose keys can be any (string) value,
and values are all the same type.

## Object specifications

### Object: Root

Representation of the root object of the Zarr Capability Manifest.

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| version | MUST | integer | |
| is_definition | SHOULD | boolean, default `false` | Whether this manifest represents capability definitions (rather than implementation capabilities). |
| last_updated | SHOULD | string | RFC-3339 date |
| capabilities | MUST | array of [Capability](#object-capability) | |

Manifests with different values for `version` _or_ `is_definition` MUST not be merged or directly compared.

### Object: Capability

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| key | MUST | string | SHOULD use `/`-delimited namespacing |
| description | MAY | string | Free text description of feature or level of support |
| url | MAY | string | URL to definition of capability |
| support | MAY | boolean, default `false` | Whether this capability is supported |

Definition manifests SHOULD include the `description` and `url` keys.

Implementation manifests SHOULD include the `support` key.

Aliases for a group of features SHOULD be listed as a feature.
For example, for feature `a/b/c`, if `b` has an alias `bee`,
add a feature `a/b/alias/bee`.
