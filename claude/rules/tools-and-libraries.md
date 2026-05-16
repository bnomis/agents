# Tools and libraries

## Prefer what's already in the project

Before adding a new dependency, check whether the project already has
something that does the job. The cheapest dependency is the one already
in `pyproject.toml` / `package.json` / `go.mod`.

If the stdlib (or framework already in use) can handle it, use that.

## Verify maintenance status before recommending

Don't rely on training-data recall - check the current state:

- GitHub: last commit, open-issue triage, archived/deprecated flags.
- Registry: latest release date on PyPI / npm / crates.io.
- Use [Context7](https://context7.com) for current docs.

Flag a library to the user if any of these are true:

- The repo is archived, marked deprecated, or has an EOL notice.
- No commits in >2 years and open unresolved security advisories.
- A known CVE applies to the version being recommended.
- License is incompatible with the project (e.g., GPL into a
  proprietary codebase).

Note: slow release cadence alone is not a red flag. Some libraries are
feature-complete. Look for *abandonment*, not *quietness*.

## When flagging, give alternatives

Name 1-2 maintained alternatives, why they're preferable (active
maintenance, smaller surface area, stdlib equivalent), and the
migration cost. Let the user decide.

## Don't add dependencies casually

Adding a library is a long-term commitment. For small/trivial helpers,
prefer writing the code inline over pulling in a dependency.
