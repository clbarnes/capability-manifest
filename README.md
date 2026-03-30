# zarr-capabilities

A metadata file specification for zarr implementations to self-report their compatibility with the core spec and extensions.
In future, this could be generated automatically with a conformance test suite.

See [SPEC.md](./SPEC.md) for the specification and the [examples/](./examples/) directory for examples.

## Intended use

Websites or code repositories for Zarr-related tools can provide a Zarr Capability Manifest file.
Users can then easily determine whether a particular tool is suitable for their data.

Tools could also provide the capability manifest as part of their API.

Third parties (e.g. downstream dependants, or projects which compare tools' compatibility) can then easily access the manifest in a standardised format.
