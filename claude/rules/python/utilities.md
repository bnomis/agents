---
paths:
  - "**/*.py"
---

# python utility scripts

Follow these guidelines when creating utility scripts.

## Location

By default utility scripts are located in the `bin/` directory.

## Naming

When creating new files, separate words in the file name with dashes: this-is-a-good-example.py
NOT underscores this_is_a_bad_example.py

## Wrapper scripts

Always create wrapper scripts next to utility scripts to set up the environment and to run the python script. An example is given below:

```python
#!/usr/bin/env bash
THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# shellcheck disable=SC1091
source "$THIS_DIR/activate.sh"

"$THIS_DIR/this-is-a-good-example.py" "$@"
```

So, in this case, the `bin/` directory would include the below:

```shell
bin/activate.sh
bin/this-is-a-good-example.py
bin/this-is-a-good-example.sh
```
