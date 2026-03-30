# Capability Manifest Specification

## Motivation

Zarr is extensible by design.
What, then, does it mean for a tool to "support Zarr"?
The Zarr Capability Manifest allows tools to provide human-editable, machine-readable summaries of supported features.

## Definitions vs implementations

This schema should be used both by projects _defining_ capabilities,
and those _implementing_ them.

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

This specification is defined in terms of the [TOML 1.1](https://toml.io/en/v1.1.0) data model.

## Object specifications

### Object: Root

Representation of the root object of the Zarr Capability Manifest.

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| version | MUST | integer | |
| imports | MAY | array of string | IRI references to other capability manifests to be imported into this one |
| capabilities | MUST | table of [Capability](#object-capability) | |

Manifests with different values for `version` MUST not be merged or directly compared.

The keys of the `capabilities` table are canonical identifiers of capabilities/ features.
They SHOULD use `/`-separated namespaces; for example, to define the partial decoding capability of the blosc codec in the third version of the Zarr specification, the key could look like `zarr/v3/codec/blosc/encode_partial`.

Capabilities or groups of capabilities with aliases can include that alias as a capability.
For example, if `blosc1` was an acceptable alias for the example above,
the resulting capability key could be `zarr/v3/codec/blosc/alias/blosc1`.

### Object: Capability

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| description | MAY | string | Free text description of feature or level of support |
| url | MAY | string | URL to definition of capability |
| support | MAY | boolean, default `false` | Whether this capability is supported |

Definition manifests SHOULD include the `description` and `url` keys.

Implementation manifests SHOULD include the `support` key.

Aliases for a group of features SHOULD be listed as a feature.
For example, for feature `a/b/c`, if `b` has an alias `bee`,
add a feature `a/b/alias/bee`.

## Merging manifests

A list of manifests `[m0, m1, m2, ..., mN]` MAY be merged into a single manifest if they have the same `version`.
The following algorithm MUST be used:

- resolve each manifest's `imports` where possible
  - relative imports MUST be resolved unless they belong to the leftmost manifest
- traverse the list from left to right
  - add any new keys to the merged `capabilities` table
  - if the key exists, overwrite the existing capability fields with new values where:
    - the existing `description` is omitted
    - the existing `url` is omitted
    - the existing `support` is omitted; additionally `false` should be overwritten if the new value is `true`

## Imports

Capability manifests MAY list other manifests whose capabilities they inherit.
This is useful:

- when support for a set of features comes from some underlying library;
  import the library's capability manifest to avoid duplication
- when your own project is split up into subprojects, which each implement some subset of the total;
  define each subproject's capabilities and import them at the root
- where capabilities are defined elsewhere with descriptions and URLs,
  and you want those descriptions and URLs reflected in your manifest without copy-and-pasting them
- where you want your manifest to explicitly list features which are defined in some specification,
  but not implemented in your project

Imports are [IRI References](https://datatracker.ietf.org/doc/html/rfc3987),
which SHOULD also be locators,
and SHOULD either be relative OR use the `https` or `file` schemes.
Clients SHOULD resolve these IRIs to contents as appropriate to the scheme.
Relative IRI References MUST be resolved against the manifest being parsed.

The resulting manifest MUST be the result of merging the manifests [as described above](#merging-manifests),
starting with the contents of this manifest,
followed by the imported manifests in the given order.
