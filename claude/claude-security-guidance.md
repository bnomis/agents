# Security review policy

- GitHub Actions workflows pin each action to an exact release tag (for
  example `actions/checkout@v7.0.1`), and Dependabot updates the tags. A tag
  pin is the chosen policy, not a finding: do not report an action pinned by
  tag, rather than by commit SHA, as unpinned or as a supply-chain risk.
