# zarr-capabilities

A metadata file specification for zarr implementations to self-report their compatibility with the core spec and extensions.
In future, this could be generated automatically with a conformance test suite.

See [SPEC.md](./SPEC.md) for the specification and the [examples/](./examples/) directory for examples.

## Why YAML?

Every time I use YAML in a project I am compelled to remind people [not to use YAML](https://noyaml.com/), where it can be avoided.
Unfortunately, its broad support and human-accessibility of deeply nested data makes it one of the better formats available for this application.
