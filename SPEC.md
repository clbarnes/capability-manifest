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
| spec | MUST | [Spec](#object-spec) | |

Manifests with different values for `version` _or_ `is_definition` MUST not be merged or directly compared.

### Object: Spec

Set of root specifications supported by a given tool.

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| zarr3 | SHOULD | [Zarr3](#object-zarr3) | |

### Object: Zarr3

Feature groups belonging to the Zarr v3 specification.

These are mainly referred to in the Zarr specification as extension points.
Note that stores are not strictly extension points because they describe how the data is accessed,
and so cannot be represented by Zarr metadata.

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| codec | MAY | Map of [Codec](#object-codec) | |
| chunk_grid | MAY | Map of [ChunkGrid](#object-chunkgrid) | |
| chunk_key_encoding | MAY | Map of [ChunkKeyEncoding](#object-chunkkeyencoding) | |
| data_type | MAY | Map of [DataType](#object-datatype) | |
| store | MAY | Map of [Store](#object-store) | |
| storage_transformer | MAY | Map of [StorageTransformer](#object-storagetransformer) | |

### Object: Codec

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| meta | MAY | [Metadata](#object-metadata) | General information about this feature and its implementation. |
| decode | SHOULD | boolean; default `false` | Whether decoding of whole chunks is supported. |
| decode_partial | SHOULD | boolean; default `false` | Whether decoding of part of a chunk is supported. |
| encode | SHOULD | boolean; default `false` | Whether encoding of full chunks is supported. |
| encode_partial | SHOULD | boolean; default `false` | whether encoding of partial chunks is supported. |

### Object: ChunkGrid

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| meta | MAY | [Metadata](#object-metadata) | General information about this feature and its implementation. |
| support | SHOULD | boolean; default `false` | Whether this feature is supported. |

### Object: ChunkKeyEncoding

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| meta | MAY | [Metadata](#object-metadata) | General information about this feature and its implementation. |
| support | SHOULD | boolean; default `false` | Whether this feature is supported. |

### Object: DataType

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| meta | MAY | [Metadata](#object-metadata) | General information about this feature and its implementation. |
| support | SHOULD | boolean; default `false` | Whether this feature is supported. |

### Object: Store

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| meta | MAY | [Metadata](#object-metadata) | General information about this feature and its implementation. |
| read | SHOULD | boolean; default `false` | Whether this store can be used to read whole chunks. |
| read_partial | SHOULD | boolean; default `false` | Whether this store can be used to read ranges within chunks. |
| list | SHOULD | boolean; default `false` | Whether this store can be used to list storage keys and prefixes. |
| write | SHOULD | boolean; default `false` | Whether this store can be used to write whole chunks. |
| write_partial | SHOULD | boolean; default `false` | Whether this store can be used to write ranges within chunks. |

Definitions of these capabilities should approximately match the Zarr v3 abstract storage interface.

### Object: StorageTransformer

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| meta | MAY | [Metadata](#object-metadata) | General information about this feature and its implementation. |

At time of writing, no storage transformers definitions are known.

### Object: Metadata

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| alias | MAY | array of string | Other keys by which this feature is known. |
| description | MAY | string | Short description of this feature. |
| url | MAY | string | URL to canonical description of this feature. |
| notes | MAY | string | Information about this implementation of the feature. |

Definition manifests ([`Root.is_definition = true`](#object-root)) SHOULD include the `description` field, and `alias` if any are defined.

Implementation manifests SHOULD include the `url`,
and SHOULD list any aliases recognised by the implementation.
