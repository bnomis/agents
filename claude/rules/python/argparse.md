---
paths:
  - "**/*.py"
---

# argparse standards

Add a trailing comma to the arguments passed to argparse functions so the arguments are formatted one per line, see below:

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--model-name',
        required=True,
        help='Registered MLflow model name',
    )
    parser.add_argument(
        '--version',
        default=None,
        help='Registered model version (defaults to latest)',
    )
    parser.add_argument(
        '--features',
        required=True,
        help='Path to features.json (unlabelled inference input)',
    )
    parser.add_argument(
        '--output',
        default=None,
        help='CSV output path (defaults to stdout)',
    )
    parser.add_argument(
        '--tracking-uri',
        default=None,
        help='MLflow tracking URI (defaults to MLFLOW_TRACKING_URI / file store)',
    )
    return parser.parse_args()
```
