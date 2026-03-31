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
