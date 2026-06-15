# Streams, Pipes & Redirection

> Covers lessons 5 (completed) and 15 (coming up)

---

## Table of Contents

1. [The Three Streams](#1-the-three-streams)
2. [Pipes — |](#2-pipes--)
3. [Useful Filter Commands](#3-useful-filter-commands)
4. [Redirection](#4-redirection)
5. [Combining Pipes and Redirection](#5-combining-pipes-and-redirection)
6. [Common Patterns](#6-common-patterns)

---

## 1. The Three Streams

Every Linux process has three standard streams open by default:

```
stdin  (fd 0) ← input  — keyboard by default
stdout (fd 1) → output — terminal by default
stderr (fd 2) → errors — terminal by default
```

```
                ┌─────────────┐
   stdin (0) →  │   command   │ → stdout (1)
                │             │ → stderr (2)
                └─────────────┘
```

**Why it matters:** You can redirect any of these streams — send output to a file,
read input from a file, hide errors, or chain commands together.

---

## 2. Pipes — |

The pipe `|` connects the **stdout** of one command to the **stdin** of the next.

```bash
command1 | command2 | command3
```

```
stdout of cmd1 → stdin of cmd2 → stdin of cmd3 → terminal
```

**The key insight:** neither command knows about the other. `ls` doesn't know
`grep` is filtering its output. `grep` doesn't know it came from `ls`.
Pipes are how you build powerful tools from simple ones.

### Examples

```bash
ls -la | grep ".txt"          # list files, filter for .txt
cat /etc/passwd | wc -l       # count lines in a file
ps aux | grep nginx           # find nginx process
cat access.log | sort | uniq  # sort and deduplicate log entries
history | grep "git"          # search your command history
ls -lS | head -5              # 5 largest files
cat file.txt | grep "error" | wc -l   # count lines containing "error"
```

---

## 3. Useful Filter Commands

These are the commands you pipe into most often:

### grep — search for a pattern

```bash
grep "pattern" file          # lines that match pattern
grep -i "error" file         # case insensitive
grep -n "error" file         # show line numbers
grep -v "error" file         # lines that do NOT match (invert)
grep -r "TODO" ./src/        # recursive search in directory
grep -c "error" file         # count matching lines (not printing them)
grep "^Error" file           # lines starting with "Error" (regex)
grep "error$" file           # lines ending with "error" (regex)
```

### wc — word/line/byte count

```bash
wc file.txt            # lines  words  bytes
wc -l file.txt         # line count only
wc -w file.txt         # word count only
wc -c file.txt         # byte count only
ls | wc -l             # how many files in current dir
```

### sort — sort lines

```bash
sort file.txt          # alphabetical
sort -r file.txt       # reverse
sort -n file.txt       # numeric sort
sort -u file.txt       # sort and remove duplicates
sort -k2 file.txt      # sort by second column
```

### uniq — remove duplicate lines

```bash
uniq file.txt              # remove consecutive duplicates
sort file.txt | uniq       # remove ALL duplicates (sort first!)
sort file.txt | uniq -c    # count occurrences of each line
sort file.txt | uniq -d    # show only duplicate lines
```

### head & tail

```bash
head file.txt          # first 10 lines
head -n 20 file.txt    # first 20 lines
tail file.txt          # last 10 lines
tail -n 20 file.txt    # last 20 lines
tail -f file.txt       # follow — stream new lines as they're written
```

### cut — extract columns

```bash
cut -d: -f1 /etc/passwd     # delimiter=:, get field 1 (usernames)
cut -d, -f2,4 data.csv      # get columns 2 and 4 from CSV
cut -c1-5 file.txt           # get characters 1 through 5 of each line
```

### tr — translate/replace characters

```bash
echo "hello" | tr 'a-z' 'A-Z'    # uppercase
echo "a:b:c" | tr ':' ','         # replace colon with comma
cat file | tr -d '\n'              # delete newlines
```

---

## 4. Redirection

Redirection changes where a stream goes — to/from a file instead of terminal/keyboard.

### stdout redirection

```bash
command > file.txt        # write stdout to file (OVERWRITES)
command >> file.txt       # append stdout to file (KEEPS existing content)

ls -la > filelist.txt     # save ls output to a file
echo "hello" > out.txt    # write "hello" to out.txt
echo "world" >> out.txt   # append "world" to out.txt
```

**`>` vs `>>`:**
```
> overwrites the file completely
>> adds to the end of the file
```

### stderr redirection

```bash
command 2> errors.txt     # redirect stderr to file
command 2>/dev/null       # discard errors (send to trash)
```

`/dev/null` is a special file that discards everything written to it.
Use it when you want to silence errors.

### redirect both stdout and stderr

```bash
command > out.txt 2>&1    # stdout to file, stderr to same place as stdout
command &> out.txt        # shorthand (bash only)
command > out.txt 2>/dev/null   # stdout to file, discard errors
```

`2>&1` means: "send file descriptor 2 (stderr) to the same place as file descriptor 1 (stdout)."

### stdin redirection

```bash
command < file.txt        # use file as input instead of keyboard
sort < unsorted.txt       # sort reads from the file
```

### Here-string and Here-doc

```bash
grep "error" <<< "some error text"    # pass string as stdin

cat << EOF
line one
line two
EOF
```

---

## 5. Combining Pipes and Redirection

Pipes and redirection can be combined:

```bash
# Filter errors from a log, save results to a file
grep "ERROR" /var/log/app.log > errors.txt

# Count errors and append count to a report
grep -c "ERROR" /var/log/app.log >> report.txt

# Process a file and discard errors
sort huge_file.txt 2>/dev/null > sorted.txt

# Chain multiple filters, save output
cat access.log | grep "404" | sort | uniq -c | sort -rn > 404_report.txt
```

---

## 6. Common Patterns

```bash
# Count occurrences of a pattern
grep -c "pattern" file

# Find the most frequent lines
sort file | uniq -c | sort -rn | head -10

# Search running processes
ps aux | grep "processname" | grep -v grep

# Watch a log file, filter for errors
tail -f /var/log/app.log | grep "ERROR"

# Count files in a directory
ls | wc -l

# Find and count unique IPs in a log
cut -d' ' -f1 access.log | sort | uniq -c | sort -rn

# Suppress all output (stdout and stderr)
command > /dev/null 2>&1

# Run command, save output, still see it in terminal
command | tee output.txt     # writes to file AND shows in terminal
```

### tee — split output to file and terminal

```bash
ls -la | tee filelist.txt      # shows output AND saves to file
command | tee -a log.txt       # append to file instead of overwrite
```
