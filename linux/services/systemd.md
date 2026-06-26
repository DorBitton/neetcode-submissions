# Systemd and Service Management

> How Linux starts and manages services. The replacement for init scripts.

---

## The mental model

Every background process (nginx, postgres, sshd, your app) is a **unit** managed by systemd. Systemd starts them in the right order at boot, restarts them if they crash, and collects their logs.

```
systemd (PID 1) → starts all services → monitors them → restarts on failure
```

---

## Core commands

```bash
# Status and control
systemctl status nginx          # is it running? last log lines, PID
systemctl start nginx           # start now
systemctl stop nginx            # stop now
systemctl restart nginx         # stop + start (brief downtime)
systemctl reload nginx          # reload config without stopping (if supported)
systemctl enable nginx          # start automatically at boot
systemctl disable nginx         # don't start at boot
systemctl is-active nginx       # just: active or inactive
systemctl is-enabled nginx      # just: enabled or disabled

# Listing units
systemctl list-units --type=service             # all running services
systemctl list-units --type=service --all       # including stopped/failed
systemctl list-units --state=failed             # only failed units
```

---

## Reading status output

```
● nginx.service - A high performance web server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled)
     Active: active (running) since Mon 2024-01-15 10:23:11 UTC; 2h ago
    Process: 1234 ExecStart=/usr/sbin/nginx (code=exited, status=0/SUCCESS)
   Main PID: 1235 (nginx)
      Tasks: 3
     Memory: 12.4M
        CPU: 234ms
     CGroup: /system.slice/nginx.service
             ├─1235 nginx: master process
             └─1236 nginx: worker process
```

**Active line is what you look at first:**
```
active (running)    → healthy
activating          → still starting
failed              → crashed or exited with error
inactive (dead)     → stopped, not failed
```

---

## Reading logs with journalctl

```bash
journalctl -u nginx                     # all logs for nginx
journalctl -u nginx -f                  # follow (live tail)
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx -n 50              # last 50 lines
journalctl -u nginx -p err             # errors only
journalctl -b -u nginx                 # since last boot only
journalctl -xe                         # recent logs, extra context (use after failed start)
```

**The debugging sequence when a service fails:**
```bash
systemctl status nginx          # 1. what's the current state?
journalctl -u nginx -n 50      # 2. what did it log right before failing?
journalctl -xe                  # 3. what did systemd itself report?
nginx -t                        # 4. (nginx-specific) is the config valid?
```

---

## Unit files

Unit files define how systemd manages a service. Stored in:
```
/lib/systemd/system/      ← package-installed (don't edit)
/etc/systemd/system/      ← your custom units and overrides (edit here)
```

**Basic service unit file:**
```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target          # start after networking is up
Requires=postgresql.service   # hard dependency

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/start.sh
Restart=on-failure            # restart if it crashes
RestartSec=5s
StandardOutput=journal        # logs go to journald
StandardError=journal

[Install]
WantedBy=multi-user.target    # start in normal (non-GUI) mode
```

**After editing a unit file:**
```bash
systemctl daemon-reload       # always run this after editing unit files
systemctl restart myapp
```

---

## Common Restart policies

```
no              → never restart (default)
on-failure      → restart only if exit code != 0
always          → restart always, even on clean exit
on-abnormal     → restart on signal/watchdog/timeout (not clean exit)
```

For production services: `Restart=on-failure` with `RestartSec=5s` is the standard.

---

## Troubleshooting scenarios

**Service fails to start — config error:**
```bash
systemctl status myapp          # shows: "code=exited, status=1/FAILURE"
journalctl -u myapp -n 20       # shows the actual error message
# Fix the config, then:
systemctl start myapp
```

**Service starts but keeps crashing:**
```bash
journalctl -u myapp -f          # follow — watch it crash in real time
# Look for: OOM killer? Missing file? Port already in use?
ss -tulpn | grep :8080          # is something else on the port?
```

**Service not starting at boot despite being enabled:**
```bash
systemctl is-enabled myapp      # confirm enabled
systemctl list-dependencies myapp  # check if a dependency is failing
journalctl -b -u myapp          # logs from last boot
```

**Port conflict (common):**
```bash
ss -tulpn | grep :80            # what's already on port 80?
systemctl status <that-service> # stop it or reconfigure
```
