# Bash Essentials — SRE Tutor Reference

## What bash scripting is

A bash script is a text file containing shell commands. Instead of typing them one by one,
you run the file and they execute in sequence. Bash scripts are how SREs automate repetitive
tasks, run health checks, deploy applications, and process logs.

When you type commands at the terminal you're already using bash interactively. A script is
just those same commands saved to a file so they can be run again without retyping — and
without you watching.

---

## 1. Script header — the three magic lines

Every bash script should start with these three lines. Each one solves a real problem you
would eventually hit without it.

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

### `#!/usr/bin/env bash` — the shebang

This is called a **shebang** (hash + bang = `#!`). It tells the operating system which
program should be used to interpret the rest of the file.

Without it, the OS may run your script with `/bin/sh` — a minimal POSIX shell that doesn't
support many bash features (`[[ ]]`, arrays, `${VAR:-default}`, etc.). Your script would
fail with confusing errors.

Why `#!/usr/bin/env bash` instead of `#!/bin/bash`?

`/usr/bin/env bash` searches for bash in the system PATH. On macOS with Homebrew, the
newer bash you installed lives at `/opt/homebrew/bin/bash`, not `/bin/bash`. On NixOS, bash
lives somewhere else entirely. `env bash` finds it wherever it is. More portable.

### `set -euo pipefail` — safe mode for scripts

This single line turns on three critical safety behaviors. Each one prevents a whole class
of silent bugs.

**`-e` (errexit) — exit immediately on error**

Without `-e`, if a command in your script fails (returns a non-zero exit code), bash just
logs a note in `$?` and keeps going. Example: if `mkdir /no-permission` fails with
"Permission denied", your script continues running as if nothing happened — possibly
deploying to the wrong place or corrupting data.

With `-e`, any command failure immediately stops the script. You get a loud failure instead
of silent wrong behavior.

There's one exception: commands in an `if` condition are allowed to fail. `if ! some_cmd`
won't exit even if `some_cmd` fails — that's intentional.

**`-u` (nounset) — exit on unset variables**

Without `-u`, referencing a variable you never set silently expands to an empty string.
A typo like `$DATBASE_HOST` (missing letter) becomes `""` and your script runs with an
empty hostname. The error you get will be far from the typo.

With `-u`, bash exits with an error immediately when you reference an unset variable.
The error message points directly to the typo.

**`-o pipefail` — pipes fail if any stage fails**

Without `pipefail`, a pipe like `cmd1 | cmd2` only fails if `cmd2` fails. If `cmd1` fails
but `cmd2` succeeds (or receives empty input and exits 0), the entire pipeline returns
success. You'd never know `cmd1` broke.

```bash
cat /nonexistent-file | wc -l   # without pipefail: exits 0 (wc -l succeeds on empty input)
                                 # with pipefail: exits non-zero (cat failed)
```

`-o pipefail` makes the pipeline return the exit code of the rightmost failing command.

### `IFS=$'\n\t'` — safer word splitting

IFS is the **Internal Field Separator** — the characters bash uses to split strings into
separate words. The default IFS is space, tab, and newline.

The space in the default IFS is the problem. Consider this common pattern:

```bash
for f in $(ls /my/dir); do
    process "$f"
done
```

If a filename is `my log.txt`, bash splits it on the space into `my` and `log.txt` — two
separate items. Your loop processes them as two broken filenames instead of one real one.

Setting `IFS=$'\n\t'` removes space from the separator list. Now only newlines and tabs
split words. Filenames with spaces stay intact.

(Note: the `$'\n\t'` syntax is bash's way of writing literal newline + tab characters in
a string. You can't just write them directly.)

---

## 2. Variables

Variables in bash are just strings. There are no types — no integers, no booleans, no
lists (well, arrays exist, but everything else is a string). You set them without spaces
around `=`. You read them with `$`.

```bash
NAME="value"        # set — no spaces around =
echo "$NAME"        # read — the $ is how you expand it
echo "${NAME}"      # read with explicit braces — required when adjacent to other characters
```

### Why always double-quote variable expansions

This is one of the most important habits in bash. Always wrap `$VAR` in double quotes.

Without quotes, the value is **word-split and glob-expanded** after substitution. Consider:

```bash
FILE="my log.txt"

cat $FILE           # parsed as: cat my log.txt  (two arguments — fails)
cat "$FILE"         # parsed as: cat "my log.txt"  (one argument — works)
```

Or with a glob character in the value:

```bash
PATTERN="*.log"
ls $PATTERN         # bash expands *.log to actual filenames — maybe not what you want
ls "$PATTERN"       # passed literally as "*.log" — always what you want
```

Double-quoting prevents both word splitting and glob expansion. Default to quoting every
`$VAR` unless you have a specific reason not to.

### Default values and required variables

```bash
# The :- operator: if VAR is unset OR empty, use the default value.
# The variable itself is NOT changed — this is just for the expansion.
PORT="${PORT:-8080}"

# The :? operator: if VAR is unset or empty, print this message and EXIT.
# Use this for variables that your script absolutely requires.
# Better to fail loudly at startup than mysteriously in the middle of a run.
DB_HOST="${DB_HOST:?DB_HOST must be set before running this script}"
```

### Arrays

```bash
HOSTS=("web01" "web02" "db01")

echo "${HOSTS[0]}"              # first element (zero-indexed)
echo "${HOSTS[@]}"              # all elements — always quote this with @
echo "${#HOSTS[@]}"             # array length

# Iterate (use [@] not [*] — [*] joins all elements into one word)
for host in "${HOSTS[@]}"; do
    echo "$host"
done
```

---

## 3. Conditionals

### `[[ ]]` vs `[ ]` — always use `[[ ]]` in bash

`[[ ]]` is a **bash keyword** built into the shell. `[ ]` is actually a command — it's
an alias for `/usr/bin/[` (yes, there's a file called `[` on your system). Using `[[ ]]`
gives you several advantages:

- **Safe with empty variables:** `[ $VAR == 'x' ]` fails with a syntax error if `$VAR`
  is empty (the `[` command receives too few arguments). `[[ $VAR == 'x' ]]` handles
  empty values safely.
- **Regex support:** `[[ ]]` supports `=~` for pattern matching. `[ ]` does not.
- **No word splitting:** inside `[[ ]]`, variables are not word-split. You can write
  `[[ $VAR == "hello" ]]` without quotes and it won't break on spaces. (Quote anyway
  as a habit, but it's not the trap it is with `[ ]`.)

```bash
# String comparisons
if [[ "$ENV" == "prod" ]]; then
    echo "production"
fi

if [[ "$ENV" != "dev" ]]; then
    echo "not dev"
fi

# Numeric comparisons — use (( )) for arithmetic or -gt/-lt inside [[ ]]
if (( count > 10 )); then echo "high"; fi           # arithmetic context, no $ needed
if [[ $count -gt 10 ]]; then echo "high"; fi        # POSIX-style numeric comparison
```

### File test operators

These flags go inside `[[ ]]` and test properties of files:

| Flag | What it actually checks |
|------|------------------------|
| `-f` | is a **regular file** — not a directory, not a symlink, not a device |
| `-d` | is a **directory** |
| `-e` | **exists** at all — file, directory, symlink, device — anything |
| `-r` | you have **read permission** on this file |
| `-x` | you have **execute permission** — use this before running a binary |
| `-z` | the **string is zero length** (empty) — tests a string, not a file |
| `-n` | the **string is non-empty** — opposite of `-z` |

```bash
if [[ -f "/etc/hosts" ]]; then
    echo "hosts file exists and is a regular file"
fi

if [[ -d "/var/log" ]]; then
    echo "log directory exists"
fi

if [[ -z "$VAR" ]]; then
    echo "VAR is empty or unset"
fi

if [[ -n "$VAR" ]]; then
    echo "VAR has a value"
fi

# Check before executing
if [[ -x "/usr/local/bin/myapp" ]]; then
    /usr/local/bin/myapp
fi
```

### Regex matching with `=~`

The `=~` operator does regex matching inside `[[ ]]`. The regex does not need anchors —
it matches anywhere in the string. If you want to anchor to the start, use `^`.

Capture groups are stored in the `${BASH_REMATCH}` array:
- `${BASH_REMATCH[0]}` — the entire match
- `${BASH_REMATCH[1]}` — first capture group
- `${BASH_REMATCH[2]}` — second capture group, etc.

```bash
VERSION="2.14.3"

# Check if it looks like a semver
if [[ "$VERSION" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    echo "Major: ${BASH_REMATCH[1]}"   # 2
    echo "Minor: ${BASH_REMATCH[2]}"   # 14
    echo "Patch: ${BASH_REMATCH[3]}"   # 3
fi
```

---

## 4. Loops

Bash has three loop types. Pick the one that matches your use case.

### `for` — iterate over a list

```bash
# Over a literal list
for host in web01 web02 db01; do
    ssh "$host" "uptime"
done

# Over an array — use "${ARRAY[@]}" always
for host in "${HOSTS[@]}"; do
    echo "Checking $host"
done

# Over files matching a glob — safer than parsing ls output
for f in /var/log/*.log; do
    echo "Processing $f"
done

# Over a numeric range
for i in {1..5}; do
    echo "Step $i"
done
```

### `while` — repeat while a condition is true

```bash
# Classic countdown
count=5
while (( count > 0 )); do
    echo "$count"
    (( count-- ))
done

# Wait until a service is healthy
until curl -sf http://localhost/health; do
    echo "Waiting for service..."
    sleep 2
done
```

### Reading a file line by line — the correct pattern

This pattern confuses many people. Here's the full explanation:

```bash
while IFS= read -r line; do
    echo "$line"
done < /etc/hosts
```

Breaking it down piece by piece:

- **`IFS=`** (set to empty): by default, `read` strips leading and trailing whitespace from
  each line using IFS. Setting `IFS=` (empty string) before `read` prevents that stripping,
  so you get the line exactly as it appears in the file — spaces and all.

- **`-r` flag**: prevents backslash interpretation. Without `-r`, a line containing `\n`
  would be converted to a literal newline. With `-r`, `\n` stays as the two characters
  backslash and n. Use `-r` unless you specifically want backslash escapes processed.

- **`< filename`**: redirects the file as input to the entire `while` loop, not just one
  command. The `while` loop reads from the file until `read` hits EOF and returns non-zero.

Why not `for line in $(cat file)`? Because that splits on whitespace, not just newlines.
A line containing spaces becomes multiple loop iterations. The `while read` pattern is
the correct approach.

---

## 5. Functions

Functions in bash are reusable blocks of commands. Arguments are positional: `$1` is the
first argument, `$2` is the second, and so on. `$@` is all arguments as separate words.
`$#` is the count of arguments.

```bash
check_service() {
    local service="$1"          # $1 is the first argument passed to this function
    local timeout="${2:-10}"    # $2 is optional — default to 10 if not provided

    systemctl is-active --quiet "$service"
    return $?   # return $? passes through the exit code of the previous command
                # 0 = active, non-zero = not active
}

# Call it and act on the result
if check_service nginx; then
    echo "nginx is running"
else
    echo "nginx is down"
    exit 1
fi

# Or use || for inline error handling
check_service postgresql || { echo "postgres down — aborting"; exit 1; }
```

### `local` — scope variables to the function

Variables in bash are **global by default — even inside functions**. If you assign
`NAME="foo"` inside a function, it overwrites any outer variable called `NAME`.

`local var='value'` declares the variable with function scope. When the function returns,
the local variable disappears. Always use `local` for function variables to avoid
accidentally clobbering outer script variables.

```bash
greet() {
    local name="$1"        # local — this NAME only exists inside greet()
    echo "Hello, $name"
}

name="global"
greet "Alice"
echo "$name"              # still "global" — greet() didn't overwrite it
```

### Return codes vs output — two different channels

Functions can communicate in two ways. Don't confuse them.

**Return code:** the integer (0–255) a function exits with. `0` = success. Non-zero = error.
Checked with `$?` or used directly in `if` and `||`.

```bash
is_even() {
    local n="$1"
    (( n % 2 == 0 ))   # (( )) exits 0 if true, 1 if false
}

if is_even 4; then echo "even"; fi
```

**stdout output:** text the function prints. Captured with `$(function)`. This is how
you return a string value.

```bash
get_instance_id() {
    curl -s http://169.254.169.254/latest/meta-data/instance-id
    # curl prints the instance ID to stdout — caller captures it
}

ID=$(get_instance_id)    # captures the stdout of get_instance_id
echo "Running on: $ID"
```

These are separate channels. A function can return 0 (success) while printing an error
message, or return 1 (failure) while printing a result. Design your functions to use
return code for success/failure and stdout for the value.

---

## 6. String manipulation

Bash has built-in parameter expansion operators for string manipulation. They're cryptic
at first but extremely useful — no need to call `sed` or `awk` for simple cases.

The mental model: `#` and `##` work on the **front** (beginning) of the string. `%` and
`%%` work on the **back** (end). Single character = shortest match. Doubled = longest match.

```bash
FILE="deploy-2024-01-15.tar.gz"
PATH_EXAMPLE="/var/log/nginx/access.log"
```

**`${FILE#prefix}` — remove shortest match from the BEGINNING**

The `#` means "from the front." One `#` means shortest match (non-greedy).

```bash
echo "${FILE#deploy-}"         # → 2024-01-15.tar.gz
                               # removed "deploy-" from the front
```

**`${FILE##prefix}` — remove longest match from the BEGINNING (greedy)**

Two `##` means longest match. This is how you get just the filename from a path — it
removes everything up to and including the last `/`.

```bash
echo "${PATH_EXAMPLE##*/}"     # → access.log
                               # ## matches as much as possible, including all slashes
                               # equivalent to: basename "$PATH_EXAMPLE"
```

**`${FILE%suffix}` — remove shortest match from the END**

The `%` means "from the back." One `%` means shortest match.

```bash
echo "${FILE%.tar.gz}"         # → deploy-2024-01-15
                               # removed ".tar.gz" from the end

echo "${FILE%.*}"              # → deploy-2024-01-15.tar
                               # removed only the last extension (.gz)
                               # % is non-greedy — stops at first match from the end
```

**`${FILE%%suffix}` — remove longest match from the END (greedy)**

```bash
echo "${FILE%%.*}"             # → deploy-2024-01-15
                               # %% matches greedily from the end
                               # removes ".tar.gz" as one greedy match
```

**`${FILE//find/replace}` — replace ALL occurrences**

Single `/` replaces only the first match. Double `//` replaces all occurrences.

```bash
echo "${FILE//2024/2025}"      # → deploy-2025-01-15.tar.gz  (all "2024" → "2025")
echo "${FILE/deploy/release}"  # → release-2024-01-15.tar.gz  (only first match)
```

**Case conversion (bash 4+)**

```bash
echo "${FILE^^}"               # → DEPLOY-2024-01-15.TAR.GZ  (all uppercase)
echo "${FILE,,}"               # → deploy-2024-01-15.tar.gz  (all lowercase)
```

**String length**

```bash
echo "${#FILE}"                # → 22  (character count)
```

---

## 7. Error handling

### The `trap` command — guaranteed cleanup

`trap` registers a command to run when the script receives a signal or hits certain events.
The most useful trap is `EXIT` — it runs no matter how the script exits: normal completion,
a command failing with `-e`, or Ctrl+C.

```bash
cleanup() {
    rm -f /tmp/work.$$        # $$ is the current process ID — makes temp filenames unique
    echo "Cleanup done"
}
trap cleanup EXIT             # register cleanup to run on any exit
```

After this line, you never need to remember to clean up in every exit path. Whether the
script succeeds, fails, or gets interrupted, `cleanup` runs. This is the bash equivalent
of a `finally` block in Python or Java.

You can also trap specific signals:

```bash
trap 'echo "ERR at line $LINENO — exit code $?"' ERR   # runs on any command failure
trap 'echo "Interrupted"; exit 1' INT                   # runs on Ctrl+C (SIGINT)
```

### `||` for inline error handling

`cmd || fallback` means: run `cmd`. If it fails (non-zero exit), run `fallback`.
This is the bash logical OR — it short-circuits after the first success.

```bash
rm /tmp/old.lock || { echo "failed to remove lock file"; exit 1; }
```

The `{ }` braces group multiple commands into one unit. Two syntax requirements that
trip everyone up:

- There must be a **space after `{`** — `{echo` is a syntax error
- There must be a **`;` before `}`** — `}` must start a new statement

```bash
mkdir /output || { echo "Cannot create output dir"; exit 1; }

# Another common pattern — check for required tools at startup
command -v kubectl &>/dev/null || { echo "kubectl not found in PATH"; exit 1; }
# command -v checks if a command exists without running it
# &>/dev/null redirects both stdout and stderr to /dev/null (silence the output)
```

### A complete production-ready script template

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# --- Cleanup on exit ---
cleanup() {
    rm -f /tmp/work.$$
}
trap cleanup EXIT

# --- Required variables (fail fast if not set) ---
DB_HOST="${DB_HOST:?DB_HOST must be set}"
TIMEOUT="${TIMEOUT:-30}"          # optional with a sensible default

# --- Prerequisite check ---
command -v kubectl &>/dev/null || { echo "kubectl not found"; exit 1; }

# --- Main logic ---
echo "Connecting to $DB_HOST with timeout ${TIMEOUT}s"
```

---

## 8. SRE one-liners

These are the kind of commands you'll reach for during incidents or log analysis. Each
one chains multiple tools together using pipes — the output of one command becomes the
input of the next.

### Top 10 IPs hitting nginx

```bash
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10
```

Breaking down every stage:

- `awk '{print $1}'` — awk processes each line. `$1` is the first whitespace-separated
  field. In nginx's default log format, field 1 is the client IP address.
- `| sort` — sorts the IP addresses alphabetically. This groups identical IPs together,
  which is required for uniq to work correctly (uniq only counts *consecutive* duplicates).
- `| uniq -c` — counts consecutive identical lines. `-c` prepends the count to each line.
  Output looks like: `   142 192.168.1.50`
- `| sort -rn` — sorts numerically (`-n`) in reverse order (`-r`) so the highest
  counts appear first.
- `| head -10` — keeps only the first 10 lines (the top 10 IPs by request count).

### Replace a hostname across all nginx config files

```bash
grep -rl "old-hostname" /etc/nginx/ | xargs sed -i 's/old-hostname/new-hostname/g'
```

Breaking it down:

- `grep -r` — searches recursively through the directory tree
- `-l` — print only the **filenames** that contain a match, not the matching lines
  themselves. This is what makes the output useful to pipe to the next command.
- `| xargs sed -i` — xargs takes the list of filenames from stdin and passes them as
  arguments to `sed`. `-i` means edit files **in-place** (modify the actual files).
- `'s/old-hostname/new-hostname/g'` — sed substitution. `s` = substitute.
  `old-hostname` = find this. `new-hostname` = replace with this. `g` = global
  (replace all occurrences in each line, not just the first).

### Count HTTP status codes in nginx log

```bash
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
# field 9 in nginx combined log format is the HTTP status code
```

### Find large files

```bash
find /var -type f -size +100M -exec ls -lh {} \;
# -type f: only regular files (skip dirs and symlinks)
# -size +100M: larger than 100 megabytes
# -exec ls -lh {}: run ls -lh on each found file ({} is the placeholder)
# \; ends the -exec expression (the backslash escapes the ; from the shell)
```

### Watch a log file for errors in real time

```bash
tail -f /var/log/app.log | grep --line-buffered -i "error\|exception"
# tail -f: follows the file, printing new lines as they're written
# --line-buffered: flush grep's output after every line instead of waiting for a full buffer
#   (without this, you'd see no output until grep's internal buffer fills)
# -i: case-insensitive match
# "error\|exception": match either "error" or "exception" (\| is the OR operator in grep)
```

### Run the same command on multiple servers

```bash
for h in web01 web02 web03; do
    echo "=== $h ==="
    ssh "$h" "df -h /"
done
# Quick way to check disk on all web servers during an incident
```
