# CLI Tools — argparse, click, logging, exit codes

## What this section covers

When you write a Python script that other people (or automation) will run, you need a way to pass in arguments — which server to check, which environment to target, what timeout to use. Without argument parsing, you'd have to hardcode those values and edit the file each time, or use fragile positional `sys.argv[1]` indexing.

`argparse` and `click` are the two standard ways to add a proper CLI to a Python script. You also need `logging` so the script communicates what it's doing without resorting to `print()` scattered everywhere.

---

## 1. argparse — the stdlib solution

`argparse` is built into Python's standard library — no `pip install` needed. It's the right choice for scripts where you want zero extra dependencies.

Here's a complete working example, explained line by line:

```python
import argparse   # stdlib — no install needed
import logging    # also stdlib
import sys        # for sys.exit()

def main():
    # ArgumentParser is the object that knows all your script's arguments.
    # description= is what shows up at the top of --help output. Always write one.
    # It helps future-you and teammates understand what the script does.
    parser = argparse.ArgumentParser(description="Health check script — hits a URL and reports status")

    # add_argument() defines one argument your script accepts.
    #
    # "--url" starts with double-dash, which means it's a "named" argument (has a flag).
    # Despite being called "optional arguments" in argparse docs, required=True makes it mandatory.
    # help= is what shows up next to this argument in --help output.
    parser.add_argument("--url", required=True, help="URL to check (e.g. https://example.com/health)")

    # type=int converts the string "10" to the integer 10 automatically.
    # All command-line arguments arrive as strings — type= does the conversion.
    # default=5 means if --timeout isn't provided, args.timeout will be 5.
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")

    # action="store_true" means: if the flag is present, set the value to True.
    # If the flag is absent, set it to False. No value is needed after the flag.
    # Usage: python check.py --url http://x --verbose
    # Without: python check.py --url http://x   (args.verbose is False)
    # "-v" and "--verbose" are aliases — either flag works
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug output")

    # parse_args() does the actual work: reads sys.argv (the real command line),
    # validates all arguments against what you defined, shows --help if requested,
    # and prints an error + exits if something is wrong (missing required arg, wrong type, etc.).
    # Returns a Namespace object — you access values with dot notation.
    args = parser.parse_args()
    # Now: args.url = "https://example.com/health"
    #      args.timeout = 5
    #      args.verbose = True or False

    # Configure logging based on the --verbose flag (explained in section 4)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    log = logging.getLogger(__name__)

    log.info("Checking %s with timeout=%ds", args.url, args.timeout)
    # ... do the actual work here ...
    sys.exit(0)   # 0 = success (explained in section 5)

# This guard prevents main() from running if this file is imported as a module.
# When Python runs a file directly, __name__ is "__main__".
# When it's imported, __name__ is the module name. The guard ensures only direct runs trigger main().
if __name__ == "__main__":
    main()
```

### Running it

```bash
python check.py --url https://example.com/health --timeout 10 --verbose
python check.py --url https://example.com/health   # timeout defaults to 5, verbose defaults to False
python check.py --help                              # argparse auto-generates help output
python check.py                                    # error: --url is required
```

---

## 2. argparse argument types — the full reference

```python
# Positional argument — no flag, required by position, no --name prefix
# Usage: python script.py myfile.txt
parser.add_argument("filename", help="File to process")
# Access: args.filename

# Optional named argument with a default value
# Usage: python script.py --retries 5
# If omitted: args.retries = 3
parser.add_argument("--retries", type=int, default=3, help="Number of retries")

# Boolean flag — presence = True, absence = False
# Usage: python script.py --dry-run
parser.add_argument("--dry-run", action="store_true", help="Print actions without executing them")
# Access: args.dry_run (argparse converts hyphens to underscores in attribute names)

# Restricted choices — argparse rejects any value not in the list
# and shows a clear error message automatically. No need to validate manually.
# Usage: python script.py --env prod
parser.add_argument("--env", choices=["dev", "staging", "prod"], required=True,
                    help="Target environment")

# nargs='+' — accept one or more values, collected into a list
# Usage: python script.py --hosts web1 web2 web3
# Result: args.hosts = ["web1", "web2", "web3"]
parser.add_argument("--hosts", nargs="+", help="One or more hostnames to check")

# nargs='*' — accept zero or more values (can be empty list)
parser.add_argument("--tags", nargs="*", help="Optional tags")

# nargs=2 — accept exactly 2 values
# Usage: python script.py --range 1 100
# Result: args.range = ["1", "100"] (strings — add type=int if you need ints)
parser.add_argument("--range", nargs=2, metavar=("START", "END"), help="Start and end values")

# type=float — same as type=int but for floating-point numbers
parser.add_argument("--threshold", type=float, default=0.95, help="Failure threshold (0.0–1.0)")
```

---

## 3. click — the decorator-based alternative

### Why click exists

click does the same job as argparse but with a **decorator syntax** that many people find cleaner, especially for scripts with subcommands. Think of commands like `git commit`, `git push`, `git log` — "git" is the main command, "commit"/"push"/"log" are subcommands. That structure is called a command group.

argparse can do subcommands too, but click's syntax is significantly less verbose for that use case.

### The decorator pattern

In click, you build your CLI by **stacking decorators** on a function. The decorators define the arguments; the function parameters receive the values. Each decorator you add corresponds to one argument — click wires them up automatically.

```python
import click

# @click.command() turns this function into a CLI command.
# When you run the script, click calls this function with the parsed argument values.
@click.command()
# @click.option() defines a named argument (same idea as argparse's add_argument("--flag")).
# required=True makes it mandatory. help= appears in --help output.
@click.option("--url", required=True, help="URL to check")
# default=5 sets a default. show_default=True prints "(default: 5)" in --help — very useful.
@click.option("--timeout", default=5, show_default=True, help="Timeout in seconds")
# is_flag=True is click's equivalent of action="store_true" — presence = True, absence = False.
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
def check(url, timeout, verbose):
    """Run a health check against URL.

    This docstring appears in --help output as the command description.
    """
    # The function parameters have the same names as the --option flags.
    # click passes the parsed values in automatically.
    if verbose:
        click.echo(f"Checking {url} with timeout={timeout}s")
    # click.echo() is click's replacement for print() — handles unicode and encoding edge cases.
    click.echo("Done")

if __name__ == "__main__":
    check()   # call the function — click intercepts and parses sys.argv first
```

### click.group — subcommands

A group is a **parent command that owns sub-commands**. This is how you build a CLI like `mytool check`, `mytool deploy`, `mytool status`.

```python
import click

# @click.group() creates a parent command that does nothing by itself —
# it just routes to the correct sub-command based on what the user types.
@click.group()
def cli():
    """SRE operations toolkit."""
    pass   # The group itself has no logic — subcommands do the work

# @cli.command() registers this function as a sub-command of cli (not of click).
# The function name becomes the sub-command name: "check"
@cli.command()
@click.option("--url", required=True, help="URL to check")
@click.option("--timeout", default=5, show_default=True)
def check(url, timeout):
    """Health check a URL."""
    click.echo(f"Checking {url}")

# Another sub-command: "deploy"
@cli.command()
@click.option("--env", required=True, type=click.Choice(["dev", "staging", "prod"]))
@click.argument("service")   # Positional argument — no flag, required by position
def deploy(env, service):
    """Deploy a service to an environment."""
    click.echo(f"Deploying {service} to {env}")

if __name__ == "__main__":
    cli()
```

Usage:
```bash
python tool.py check --url https://example.com
python tool.py deploy --env prod myservice
python tool.py --help          # shows group-level help
python tool.py check --help    # shows check sub-command help
```

### Useful click extras

```python
# Prompt the user interactively if the option is not passed on the command line.
# hide_input=True masks the input — good for passwords.
# confirmation_prompt=True asks them to type it twice.
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)

# Path validation — click checks that the path exists before calling your function.
# This saves you writing os.path.exists() checks manually.
@click.argument("config_file", type=click.Path(exists=True))

# Pass shared state between commands using a context object.
# ctx.obj is a dict (or any object) you can store data in.
# @click.pass_context injects the context as the first argument.
@click.pass_context
def cmd(ctx, **kwargs):
    ctx.obj = {}                    # initialize shared state
    ctx.obj["config"] = load_config()
```

---

## 4. logging

### Why print() isn't enough

In production scripts, `print()` has several problems:
- No timestamps — you can't tell when something happened
- No severity levels — a debug message and an error look identical
- Can't be filtered — you can't turn off verbose output without editing code
- Goes to stdout — errors mixed with normal output makes piping harder

`logging` fixes all of this.

```python
import logging

# basicConfig() configures the root logger. Call this once at the start of your script.
# Only the first call to basicConfig() takes effect — subsequent calls are ignored.
# This is why it must be called at the entry point (main()), not inside library functions.
logging.basicConfig(
    # The minimum level to display. Messages below this level are silently dropped.
    # DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50
    level=logging.INFO,

    # The format of each log line.
    # %(asctime)s    — timestamp: "2024-01-15 14:23:01,234"
    # %(levelname)-8s — level name, left-padded to 8 chars: "INFO    " "WARNING "
    # %(name)s       — logger name, usually the module: "myapp.checker"
    # %(message)s    — your message
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
)

# Get a logger for this module. Using __name__ gives the logger the module's full name,
# which lets you configure different log levels for different modules if needed.
# Avoid using the root logger directly (logging.info()) in real scripts.
log = logging.getLogger(__name__)

# Usage
log.debug("Connecting to host %s on port %d", host, port)   # very detailed, for troubleshooting
log.info("Starting health check for %s", url)               # normal operation
log.warning("Retry %d of %d for %s", attempt, max_retries, url)  # unexpected but not fatal
log.error("Request failed: %s", e)                          # something failed
log.critical("Configuration file missing — cannot continue") # catastrophic, about to exit
```

### Log levels — what each one means

| Level | When to use |
|---|---|
| `DEBUG` | Very detailed — connection params, every loop iteration, intermediate values. Off by default. Turn on with --verbose. |
| `INFO` | Normal operation — "starting X", "completed Y", "found N items". This is what you see in normal runs. |
| `WARNING` | Something unexpected happened but the script can continue — a retry, a missing optional config, a deprecated parameter. |
| `ERROR` | Something failed — a request failed, a file couldn't be written, an API call errored. Script may or may not continue. |
| `CRITICAL` | Catastrophic failure — the script cannot continue at all. Usually followed by `sys.exit(1)`. |

### Lazy formatting — why %s not f-strings

```python
# WRONG — always builds the string, even if the message won't be logged
log.debug(f"Processing item: {expensive_function()}")
# If log level is INFO, this debug message is dropped — but expensive_function() already ran
# and the f-string was already built. Wasted work.

# RIGHT — lazy formatting
log.debug("Processing item: %s", expensive_function())
# If log level is INFO, logging checks the level first.
# Since DEBUG < INFO, it drops the message WITHOUT calling expensive_function()
# and WITHOUT building the string. The %s substitution only happens if the message
# will actually be output.
```

For simple values it doesn't matter much. But in tight loops or when the formatting call itself is expensive, lazy formatting can meaningfully improve performance.

### The --verbose flag pattern

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    # Set log level based on the flag — all in one line
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    log = logging.getLogger(__name__)
    log.debug("Verbose mode enabled")   # only visible when --verbose is passed
```

---

## 5. Exit codes

### What exit codes are

When a script finishes, it returns an **exit code** to the shell. This is an integer in the range 0–255. The shell uses this to know whether the script succeeded.

- `0` — success
- non-zero — failure (any non-zero value means something went wrong)

This matters because shell scripts, CI systems, and automation tools check exit codes:

```bash
# Shell if-statement checks the exit code of the command
if python check.py --url https://example.com; then
    echo "Health check passed — proceeding with deploy"
else
    echo "Health check failed — aborting"
    exit 1
fi

# Check the exit code manually
python check.py --url https://example.com
echo $?   # 0 = success, 1 = failure
```

### How to set exit codes from Python

```python
import sys

# Success — script did its job
sys.exit(0)

# Generic failure — something went wrong
sys.exit(1)

# Argument/usage error — argparse uses exit code 2 automatically
# when the user passes bad arguments. You can also use it manually
# for "called incorrectly" situations.
sys.exit(2)
```

### sys.exit vs raise

Use `sys.exit()` in CLI entry points (your `main()` function). It sends a clean exit code to the shell.

Use `raise` inside library functions and helper functions — let the caller decide whether to exit or recover. This is important if someone ever imports your script as a module.

```python
def check_url(url, timeout):
    """Library function — raises on failure, doesn't call sys.exit()."""
    resp = requests.get(url, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Health check failed: {resp.status_code}")
    return resp

def main():
    """Entry point — catches exceptions and exits with the right code."""
    args = parse_args()
    try:
        check_url(args.url, args.timeout)
        log.info("Check passed")
        sys.exit(0)
    except RuntimeError as e:
        log.error("Check failed: %s", e)
        sys.exit(1)
    except Exception as e:
        log.critical("Unexpected error: %s", e)
        sys.exit(2)
```

### Exit codes in click

click handles `sys.exit()` for you if you raise `SystemExit` or use `ctx.exit()`:

```python
@click.command()
def check():
    if something_failed:
        raise SystemExit(1)   # click-idiomatic way
```
