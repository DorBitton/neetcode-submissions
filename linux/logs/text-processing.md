# Text Processing — grep, awk, sed, cut

> The SRE toolkit for extracting signal from log files, config files, and command output.

---

## grep — find lines matching a pattern

```bash
grep "error" app.log                    # lines containing "error"
grep -i "error" app.log                 # case-insensitive
grep -v "error" app.log                 # lines NOT containing "error" (invert)
grep -n "error" app.log                 # show line numbers
grep -c "error" app.log                 # count matching lines
grep -r "error" /var/log/               # search recursively through directory
grep -l "error" /var/log/*.log          # only filenames that match (not lines)
grep -E "error|warn|crit" app.log       # extended regex — match multiple patterns
grep -A 3 "error" app.log              # 3 lines After each match (context)
grep -B 3 "error" app.log              # 3 lines Before each match
grep -C 3 "error" app.log              # 3 lines before and after (Context)
grep "^ERROR" app.log                   # lines starting with ERROR
grep "\.log$" /etc/logrotate.d/*       # lines ending with .log
```

**Real-world log patterns:**
```bash
grep "500" /var/log/nginx/access.log              # all 500 errors
grep "POST /api" access.log | grep " 200 "        # successful POSTs
grep -E "ERROR|FATAL|CRITICAL" app.log            # any serious log level
grep "2024-01-15 14:" app.log                     # specific hour
grep -v "health_check" access.log | grep "500"    # 500s that aren't health checks
```

---

## awk — extract and manipulate columns

Think of awk as "process each line and do something with its fields."

```bash
# Fields are split by whitespace by default
# $1 = first field, $2 = second, $NF = last field

awk '{print $1}' access.log                 # print first column (IP addresses)
awk '{print $1, $7}' access.log             # print columns 1 and 7
awk '{print $NF}' access.log               # print last column
awk -F: '{print $1}' /etc/passwd           # use : as delimiter, print first field
awk -F, '{print $2}' data.csv              # CSV: print second column
```

**Filtering with awk:**
```bash
awk '$9 == "500"' access.log               # lines where 9th field is 500 (HTTP status)
awk '$9 >= 400' access.log                 # all 4xx and 5xx responses
awk 'NR > 10' file.txt                     # skip first 10 lines
awk 'NR >= 5 && NR <= 10' file.txt         # lines 5 through 10
awk '/ERROR/ {print $0}' app.log           # lines matching pattern
awk '/ERROR/ {print $1, $3}' app.log       # from matching lines, print fields 1 and 3
```

**Aggregation:**
```bash
awk '{sum += $10} END {print sum}' access.log       # sum of column 10 (bytes sent)
awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -rn
# count requests per IP, sort by most requests
```

**Nginx access log analysis:**
```bash
# access log format: IP - - [date] "METHOD /path HTTP/1.1" status bytes

awk '$9 == "500" {print $1, $7}' access.log    # IP + URL for all 500s
awk '{print $9}' access.log | sort | uniq -c | sort -rn  # count by status code
```

---

## sed — stream editor, find/replace

```bash
sed 's/old/new/' file.txt              # replace first occurrence per line
sed 's/old/new/g' file.txt             # replace all occurrences (global)
sed 's/old/new/gi' file.txt            # global, case-insensitive
sed -i 's/old/new/g' file.txt          # edit file in-place (modifies the file)
sed -i.bak 's/old/new/g' file.txt      # in-place with backup (.bak extension)

# Delete lines
sed '/pattern/d' file.txt              # delete lines matching pattern
sed '5d' file.txt                      # delete line 5
sed '5,10d' file.txt                   # delete lines 5-10

# Print specific lines
sed -n '5p' file.txt                   # print only line 5
sed -n '5,10p' file.txt               # print lines 5-10
sed -n '/ERROR/p' file.txt            # print only lines matching ERROR

# Insert/append
sed '5i\new line here' file.txt        # insert before line 5
sed '5a\new line here' file.txt        # append after line 5
```

**Real-world sed uses:**
```bash
# Update a config value
sed -i 's/^port = .*/port = 8080/' app.conf

# Remove comment lines and blank lines
sed '/^#/d; /^$/d' config.txt

# Remove trailing whitespace
sed -i 's/[[:space:]]*$//' file.txt

# Extract just the IP from "Connection from 192.168.1.5 port 22"
echo "Connection from 192.168.1.5 port 22" | sed 's/.*from \([0-9.]*\) .*/\1/'
```

---

## cut — extract columns by delimiter

Simpler than awk for straightforward column extraction:

```bash
cut -d: -f1 /etc/passwd                # delimiter :, print field 1 (usernames)
cut -d: -f1,3 /etc/passwd              # fields 1 and 3
cut -d, -f2 data.csv                   # CSV second column
cut -c1-10 file.txt                    # characters 1-10 of each line
```

---

## Combining tools — the SRE pipeline

The real power is piping these together:

```bash
# Top 10 IPs by request count
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# Count 500 errors per hour
grep " 500 " access.log | awk '{print $4}' | cut -d: -f2 | sort | uniq -c

# Find which URLs are throwing errors
grep " 500 " access.log | awk '{print $7}' | sort | uniq -c | sort -rn

# Extract all unique email addresses from a log file
grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' app.log | sort -u

# Watch errors appear in real time
tail -f app.log | grep --line-buffered "ERROR"
```

---

## Quick reference — when to use which

| Tool | Best for |
|---|---|
| `grep` | Finding lines that match a pattern |
| `awk` | Extracting columns, filtering by field value, counting/aggregating |
| `sed` | Find/replace text, delete lines, edit files in-place |
| `cut` | Simple column extraction by delimiter |
| `sort \| uniq -c` | Count occurrences of repeated lines |
| `split` | Break large files into uploadable chunks |

---

## split — file partitioning

```bash
# split breaks a large file into smaller chunks
# Useful for: uploading large files, parallel processing, staying under size limits

# Split by size:
split -b 100M largefile.tar.gz part_     # 100MB chunks named part_aa, part_ab, part_ac...
split -b 500M dump.sql part_             # 500MB chunks
split -b 1G backup.tar.gz chunk_         # 1GB chunks with prefix "chunk_"

# Split by number of pieces:
split -n 5 file.txt part_               # exactly 5 equal pieces

# Split by line count:
split -l 1000 access.log part_          # 1000 lines per file
split -l 10000 large.csv chunk_         # 10000 lines per chunk

# Add numeric suffix instead of alphabetic (part_00, part_01, ...):
split -b 100M -d largefile.tar.gz part_

# Reassemble:
cat part_* > reassembled.tar.gz         # concatenate all parts in alphabetical order
cat chunk_0* > reassembled.sql          # numeric suffix order

# Verify integrity after reassemble:
md5sum original.tar.gz reassembled.tar.gz   # should match
sha256sum original.tar.gz reassembled.tar.gz

# Practical pattern: split, upload, reassemble on remote:
split -b 100M bigfile.tar.gz part_
for f in part_*; do scp "$f" user@remote:/tmp/; done
# On remote:
cat /tmp/part_* > /tmp/bigfile.tar.gz
```
