# capability-manifest

A metadata file specification for functional specifications to self-report their list of features (capabilities),
and implementations to report which features they support.
This could be generated automatically with a conformance test suite.

See [SPEC.md](./SPEC.md) for the specification and the [examples/](./examples/) directory for examples.

## Intended use

Websites or code repositories for tools within a (possibly extensible) ecosystem can provide a Capability Manifest file.
Users can then easily determine whether a particular tool is suitable for their data.

Tools could also provide the capability manifest as part of their API.

Third parties (e.g. downstream dependants, or projects which compare tools' compatibility) can then easily access the manifest in a standardised format.

## Example

```toml
version = 1

# import local or HTTP(S) manifests to reduce duplication
# e.g. when your tool's capabilities are determined some underlying library,
# or when you implement a subset of capabilities defined elsewhere
imports = [
  "https://raw.githubusercontent.com/clbarnes/capability-manifest/refs/heads/main/examples/zarr-specs/capabilities.toml",
]

# the `capabilities` table maps arbitrary namespaced keys to their information
[capabilities."zarr/v3/codec/n5_default/decode"]
description = "Decode entire chunks with the n5_default array-to-bytes codec."
url = "https://github.com/zarr-developers/zarr-extensions/tree/n5/codecs/n5_default"

# whether or not the feature is supported;
# allows authors to specify but not implement a feature
support = true
```
