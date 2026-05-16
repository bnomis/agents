# Environment variables

Use [direnv](https://direnv.net/) to load environment variables from
`.envrc` when entering the project directory.

## Do not modify `.envrc` without explicit instruction

`.envrc` contains user-specific paths and may reference secrets. Editing
it can break the user's shell or leak credentials into the repo. If the
user asks you to change it, run `direnv allow` afterwards so the new
values take effect.

For secrets at runtime, see [security.md](security.md).
