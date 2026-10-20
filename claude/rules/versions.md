# Versions that affect results

Where the version of something changes what a program produces - a library,
a model, a data file, a word list, an output schema - recording it is not
enough. Check it wherever saved work is used again, and refuse a mismatch.

## Record

Write the identity of everything that shaped an output into the output
itself or its provenance file: package versions, model names with their
version or revision, the settings the model was loaded with, and the schema
version. Build it in one place per project, so every writer records the same
thing.

## Check where saved work meets the current environment

Compare the recorded identity with the current one at every point where
something made earlier is combined with something made now:

- resuming a run into existing output;
- loading a fitted artifact (a vectoriser, scaler, classifier) to transform
  or score new input;
- merging, comparing or appending outputs from different runs;
- reading a cache keyed by content alone.

On a mismatch, stop with an error that names both identities and how to
proceed (refit, rerun, or an explicit override flag). Never warn and carry
on: a silent mix of two versions gives results that look right and are not.

An override, where one exists, is an explicit option the caller passes for
one run, and the output records that it was used.

## Pin what is checked

Pin each such dependency to an exact version in the environment, so an
upgrade happens only as a deliberate change, and the check then fails loudly
in every artifact made before it.

## When reviewing or planning

A review or spec that says a version "is recorded" also says where it is
checked. If nothing checks it, that is a finding, not a note.

## Related

- [reviews.md](reviews.md) - how such findings reach the user
- [python/dependencies.md](python/dependencies.md) - declaring dependencies
