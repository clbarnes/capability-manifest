# Capability Manifest Specification Version 1

## Motivation

Some functional specifications define a broad set of capabilities;
implementations of these specifications may support only a subset of them.

Additionally, some specifications allow for extension.

Capability manifests allow other specifications to lay out a well-defined list of capabilities,
and implementors to clearly specify which capabilities are supported,
in a format which is easy for humans and machines to read and write.

Extension authors can then define their own capabilities,
which can then be implemented elsewhere.

This project was originally inspired by the [Zarr ecosystem](https://zarr.dev/),
but is context-agnostic.

## Definitions vs implementations

This schema should be used both by projects _defining_ capabilities,
and those _implementing_ them.

## Conventions

### Requirement levels

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

### Data model

This specification is defined in terms of the [TOML 1.1](https://toml.io/en/v1.1.0) data model.
Capability manifests SHOULD be accessible in TOML format.

### File name

Capability manifest file names SHOULD end with the `.toml` suffix.

Capability manifests SHOULD be named `capabilities.toml`.

## Object specifications

### Object: CapabilityManifest

Representation of the root object of the capability manifest.

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| version | MUST | integer | Capability Manifest specification version |
| imports | MAY | array of string | IRI References to other capability manifests to be imported into this one |
| capabilities | MUST | table of [Capability](#object-capability) | |

Manifests with different values for `version` MUST not be merged or directly compared.

The keys of the `capabilities` table are canonical identifiers of capabilities/ features.
They SHOULD use `/`-separated namespaces; for example, to define the partial decoding capability of the blosc codec in the third version of the Zarr specification, the key could look like `zarr/v3/codec/blosc/encode_partial`.

Keys components SHOULD use `snake_case` unless this conflicts with an existing naming scheme.

Capabilities or groups of capabilities with aliases can include that alias as a capability.
For example, if `blosc1` was an acceptable alias for `blosc` in the example above,
the resulting capability key could be `zarr/v3/codec/blosc/alias/blosc1`.

### Object: Capability

| field | necessity | type | description |
| ----- | --------- | ---- | ----------- |
| description | MAY | string | Free text description of feature or level of support |
| url | MAY | string | URL to definition of capability |
| support | MAY | boolean, default `false` | Whether this capability is supported |

Definition manifests SHOULD include the `description` and `url` keys.

Implementation manifests SHOULD include the `support` key.

## Merging manifests

A list of manifests `[m0, m1, m2, ..., mN]` MAY be merged into a single manifest if they have the same `version`.
The following algorithm MUST be used:

- resolve each manifest's `imports` where possible, from left to right
  - relative imports MUST be resolved unless they belong to the leftmost manifest `m0`
- traverse the list from left to right
  - add any new keys to the merged `capabilities` table
  - if the key exists, overwrite the existing capability fields with new values where:
    - the existing `description` is omitted
    - the existing `url` is omitted
    - the existing `support` is omitted; additionally `false` should be overwritten if the new value is `true`

Merges MUST be processed from left to right,
as the order may change the final result.

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

The resulting manifest MUST be the result of merging the manifests [as described above](#merging-manifests),
starting with the contents of this manifest,
followed by the imported manifests in the given order.
As with all merges, the `imports` array is order-sensitive.
Imported manifests which themselves import other manifests MUST be resolved in depth-first preorder.

### Relative imports

Relative IRI References MUST be resolved against the URL of the manifest being parsed.

Note that relative file paths are thought about in the context of the parent directory of a file,
due to conventions around working directories.
Relative IRIs are resolved against the last component of the base IRI path,
which in this case includes the manifest file name.

For example, for a layout

```text
root/
  subdir/
    capabilities.toml
    sibling.toml
    subsubdir/
      nibling.toml
  publing.toml
```

where `capabilities.toml` should import all of the other `.toml` files,
the imports should look like

```toml
version = 1
imports = [
  "../sibling.toml",
  "../subsubdir/nibling.toml",
  "../../pibling.toml",
]
```
