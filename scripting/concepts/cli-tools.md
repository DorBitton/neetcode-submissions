# CLI Tools — argparse + click

## When to use which

| Tool | Use when |
|---|---|
| `argparse` | stdlib only, no extra deps, simple scripts |
| `click` | complex CLIs, subcommands, cleaner decorators |

---

## argparse

```python
import argparse, logging, sys

def main():
    parser = argparse.ArgumentParser(description="Health check script")
    parser.add_argument("--url", required=True, help="URL to check")
    parser.add_argument("--timeout", type=int, default=5)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # ... do work ...
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Key argument types

```python
# Positional (required, no flag)
parser.add_argument("filename")

# Optional with default
parser.add_argument("--retries", type=int, default=3)

# Boolean flag
parser.add_argument("--dry-run", action="store_true")

# Restricted choices
parser.add_argument("--env", choices=["dev", "staging", "prod"])

# Accept multiple values
parser.add_argument("--hosts", nargs="+")  # 1+ values → list
parser.add_argument("--coords", nargs=2)   # exactly 2
```

---

## click

```python
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option("--url", required=True, help="URL to check")
@click.option("--timeout", default=5, show_default=True)
@click.option("-v", "--verbose", is_flag=True)
@click.argument("output_file")
def check(url, timeout, verbose, output_file):
    """Run health check against URL."""
    if verbose:
        click.echo(f"Checking {url} (timeout={timeout}s)")
    # ...

if __name__ == "__main__":
    cli()
```

### click extras

```python
# Pass context between commands
@click.pass_context
def cmd(ctx, ...):
    ctx.obj["config"] = load_config()

# Prompt user if not provided
@click.option("--password", prompt=True, hide_input=True)

# Path validation built-in
@click.argument("path", type=click.Path(exists=True))
```

---

## Logging setup

```python
import logging

# Basic setup — call once at entry point
logging.basicConfig(
    level=logging.DEBUG,  # or INFO, WARNING, ERROR
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)

log.debug("Connecting to %s", host)   # lazy formatting — avoids string build if level filtered
log.info("Request complete")
log.warning("Retrying in %ds", delay)
log.error("Failed: %s", e)
```

**Verbose flag pattern:**
```python
level = logging.DEBUG if args.verbose else logging.INFO
logging.getLogger().setLevel(level)
```

---

## Exit codes

```python
import sys

sys.exit(0)   # success
sys.exit(1)   # generic failure — caught by shell `if cmd; then ...`
sys.exit(2)   # misuse / bad args (argparse uses this automatically)

# Use sys.exit in CLI entry points, not raise — gives clean shell exit code
# Use raise inside library functions — callers handle exceptions
```

**Shell usage:**
```bash
python check.py --url http://example.com
echo $?   # 0 = ok, 1 = failed
```

---

## if __name__ == "__main__"

```python
# Prevents main() from running when file is imported as a module
if __name__ == "__main__":
    main()
```

Always wrap CLI entry point in this guard.
