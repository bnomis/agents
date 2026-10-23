# Design choices that have gone wrong before

## Per-input details are runtime config

A tool that runs against many inputs (files, corpora, surveys) takes
everything specific to one input - paths, column names, mappings, field
lists - from the user's runtime config. None of it is a built-in default, and
none of it is derived from a sample input while the tool is being written.

- Ship a concrete case as an example config, not as the defaults.
- Make the input-specific keys required, with no default.
- Give defaults only to structural behaviour: output file names, filters,
  log level.

## A guess needs evidence for it, not only no evidence against

A fallback that infers a value (a prefix, a type, a language) when nothing
states it must be corroborated by something positive ("accept only when Y
supports it"), not only guarded by a negative ("accept unless X"). With a
negative guard alone, an unrelated input that matches by coincidence is read
as a real match.

- Before implementing an inference path from a spec, check that it has a
  positive guard, and add one if it has not.
- Run the project's existing tests over it, not only the new feature's: a
  coincidental match in an unrelated fixture is how this bug shows itself.

## Related

- [python/testing.md](python/testing.md) - which tests to run
