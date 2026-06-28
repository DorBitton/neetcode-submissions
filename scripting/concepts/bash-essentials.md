# Bash Essentials — SRE Reference

## Script header

```bash
#!/usr/bin/env bash
set -euo pipefail   # -e exit on error, -u unbound vars, -o pipefail pipe errors
IFS=$'\n\t'         # safer word splitting — no space splitting
```

---

## Variables

```bash
NAME="value"
echo "$NAME"          # always double-quote to prevent word splitting
echo "${NAME}"        # explicit braces — required adjacent to other chars

# Defaults and guards
PORT="${PORT:-8080}"            # use default if unset or empty
DB_HOST="${DB_HOST:?DB_HOST must be set}"  # exit with error if unset

# Arrays
HOSTS=("web01" "web02" "db01")
echo "${HOSTS[0]}"              # first element
echo "${HOSTS[@]}"              # all elements
echo "${#HOSTS[@]}"             # array length
```

---

## Conditionals

```bash
# [[ ]] — bash built-in, preferred (no word splitting, supports =~)
# [ ]  — POSIX sh, portable but more footguns

if [[ -f "/etc/hosts" ]]; then echo "file exists"; fi
if [[ -d "/var/log" ]];  then echo "dir exists";  fi
if [[ -z "$VAR" ]];      then echo "empty";        fi
if [[ -n "$VAR" ]];      then echo "not empty";    fi

# String comparison
if [[ "$ENV" == "prod" ]]; then ...
if [[ "$ENV" != "dev"  ]]; then ...

# Regex match
if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+ ]]; then echo "valid semver"; fi

# Numeric comparison
if (( count > 10 )); then echo "high"; fi
if [[ $count -gt 10 ]]; then echo "high"; fi  # POSIX-style
```

**File tests:**
| Flag | Meaning |
|---|---|
| `-f` | is regular file |
| `-d` | is directory |
| `-e` | exists (any type) |
| `-r` | readable |
| `-x` | executable |
| `-z` | string is empty |
| `-n` | string is non-empty |

---

## Loops

```bash
# For over list
for host in web01 web02 db01; do
    ssh "$host" "uptime"
done

# For over array
for host in "${HOSTS[@]}"; do echo "$host"; done

# For over files
for f in /var/log/*.log; do
    echo "Processing $f"
done

# While — read file line by line (safe with IFS)
while IFS= read -r line; do
    echo "$line"
done < /etc/hosts

# Until — run until condition true
until curl -sf http://localhost/health; do
    echo "waiting..."
    sleep 2
done
```

---

## Functions

```bash
check_service() {
    local service="$1"          # local — scoped to function
    local timeout="${2:-10}"    # default 10s

    systemctl is-active --quiet "$service"
    return $?   # 0=active, non-zero=inactive
}

check_service nginx || { echo "nginx down"; exit 1; }

# Capture return value vs output
result=$(check_service nginx)   # captures stdout
check_service nginx             # just runs; use $? for status
```

---

## String manipulation

```bash
FILE="deploy-2024-01-15.tar.gz"

echo "${FILE#deploy-}"         # strip shortest prefix match → 2024-01-15.tar.gz
echo "${FILE##*/}"             # strip longest prefix → basename
echo "${FILE%.tar.gz}"         # strip shortest suffix → deploy-2024-01-15
echo "${FILE%.*}"              # strip extension

echo "${FILE//2024/2025}"      # replace all occurrences
echo "${FILE/deploy/release}"  # replace first occurrence

echo "${FILE^^}"               # uppercase (bash 4+)
echo "${FILE,,}"               # lowercase

# Length
echo "${#FILE}"
```

---

## Error handling

```bash
# Inline guard — short circuit on failure
rm /tmp/old.lock || { echo "failed to remove lock"; exit 1; }

# Trap — run cleanup on EXIT (always), ERR, or signals
cleanup() {
    rm -f /tmp/work.$$
    echo "Cleanup done"
}
trap cleanup EXIT          # runs on any exit (normal or error)
trap 'echo "ERR at line $LINENO"' ERR  # runs on any error

# Full example
#!/usr/bin/env bash
set -euo pipefail

cleanup() { rm -f /tmp/work.$$; }
trap cleanup EXIT

DB_HOST="${DB_HOST:?DB_HOST must be set}"
TIMEOUT="${TIMEOUT:-30}"

command -v kubectl &>/dev/null || { echo "kubectl not found"; exit 1; }

# Top 10 IPs from nginx log
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```

---

## SRE one-liners

```bash
# Top 10 IPs hitting nginx
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Count HTTP status codes
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Find large files
find /var -type f -size +100M -exec ls -lh {} \;

# Watch log for errors in real time
tail -f /var/log/app.log | grep --line-buffered -i "error\|exception"

# Replace string in many files
grep -rl "old-hostname" /etc/nginx/ | xargs sed -i 's/old-hostname/new-hostname/g'

# Kill processes matching name
pgrep -f "stale-worker" | xargs kill -9

# Disk usage top directories
du -sh /var/*  | sort -rh | head -10

# Count lines matching pattern
grep -c "ERROR" app.log

# Extract column N from CSV
cut -d',' -f3 data.csv | sort | uniq

# Run command on multiple hosts
for h in web01 web02 web03; do ssh "$h" "df -h /"; done
```
