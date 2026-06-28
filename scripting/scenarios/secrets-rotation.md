# Scenario: Secrets Rotation

## Problem Statement (verbatim)

> "You rotate a database password. `kubectl get pods` shows Running. Ten minutes later users can't log in. What happened, and how do you prevent it?"

---

## Clarifying Questions to Ask

1. How is the secret injected — env var or mounted volume?
2. Does the app expose a `/healthz/db` endpoint (or similar DB connectivity check)?
3. Is this a rolling restart or recreate strategy on the deployment?
4. What's the readiness probe configured to check?

---

## Core Concept

- Kubernetes **readiness probe** checks `/healthz` (HTTP server alive) — not database connectivity.
- Pods hold a **connection pool authenticated before rotation** — those long-lived connections stay alive briefly after the password changes.
- **New connections** use the env var (stale old password) and fail immediately.
- Pod stays `Running` and `Ready` while DB auth is broken for new connections.
- `kubectl get pods` shows green. Users get login failures. The two things are unrelated — Kubernetes never checked DB auth.

---

## Worked Solution

```python
#!/usr/bin/env python3
"""
Rotate a DB credential safely:
1. Update AWS Secrets Manager
2. ALTER USER in the database
3. Patch the Kubernetes Secret
4. Rolling restart (preserves availability)
5. Verify /healthz/db — the check Kubernetes never runs
"""
import boto3, base64, json, secrets, subprocess, sys
from botocore.exceptions import ClientError

SECRET_NAME = "myapp/db-credentials"
K8S_SECRET_NAME = "db-credentials"
DEPLOYMENT = "myapp"
NAMESPACE = "default"

def get_current_secret():
    sm = boto3.client("secretsmanager")
    r = sm.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(r["SecretString"])

def update_secrets_manager(username, new_password):
    sm = boto3.client("secretsmanager")
    # put_secret_value creates a new version — previous version retained briefly for rollback
    sm.put_secret_value(
        SecretId=SECRET_NAME,
        SecretString=json.dumps({"username": username, "password": new_password})
    )
    print("  [AWS] Secrets Manager updated")

def alter_db_password(new_password):
    """Run ALTER USER directly on the running postgres pod."""
    # Must change DB-side password BEFORE restarting pods
    # otherwise new pods start with new env var but DB still expects old password
    result = subprocess.run(
        ["kubectl", "exec", "-n", NAMESPACE,
         "deployment/postgres", "--",
         "psql", "-U", "postgres", "-c",
         f"ALTER USER appuser PASSWORD '{new_password}'"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ALTER USER failed: {result.stderr}")
    print("  [DB] Password changed at database level")

def patch_k8s_secret(username, new_password):
    from kubernetes import client, config
    config.load_kube_config()
    v1 = client.CoreV1Api()
    # K8s secrets are base64-encoded (not encrypted) — encrypt etcd separately
    v1.patch_namespaced_secret(
        name=K8S_SECRET_NAME, namespace=NAMESPACE,
        body={"data": {
            "username": base64.b64encode(username.encode()).decode(),
            "password": base64.b64encode(new_password.encode()).decode(),
        }}
    )
    print("  [K8s] Secret object updated")

def rolling_restart():
    """Rolling restart: new pod up + healthy before old pod terminates. Zero downtime."""
    subprocess.run(
        ["kubectl", "rollout", "restart", f"deployment/{DEPLOYMENT}", "-n", NAMESPACE],
        check=True
    )
    subprocess.run(
        ["kubectl", "rollout", "status", f"deployment/{DEPLOYMENT}",
         "-n", NAMESPACE, "--timeout=120s"],
        check=True
    )
    print("  [K8s] Rolling restart complete — all pods Ready")

def verify_db_auth():
    """
    The check Kubernetes never runs.
    /healthz returns 200 if HTTP server is alive.
    /healthz/db opens a fresh DB connection and runs SELECT 1.
    If this fails after rollout: pod is Running but can't serve DB requests.
    """
    result = subprocess.run(
        ["kubectl", "exec", "-n", NAMESPACE,
         f"deployment/{DEPLOYMENT}", "--",
         "curl", "-sf", "http://localhost:8000/healthz/db"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("  [VERIFY] FAILED — pod Running but DB auth failed")
        print("  Readiness probe passed /healthz. /healthz/db failed.")
        print("  These are different contracts. Kubernetes only checked the first.")
        return False
    print("  [VERIFY] PASSED — app can authenticate with new credential")
    return True

def rotate():
    print("[1/5] Reading current secret...")
    current = get_current_secret()
    username = current["username"]
    new_password = secrets.token_urlsafe(16)

    print("[2/5] Updating Secrets Manager...")
    update_secrets_manager(username, new_password)

    print("[3/5] Changing password at database level...")
    alter_db_password(new_password)

    print("[4/5] Patching Kubernetes Secret + rolling restart...")
    patch_k8s_secret(username, new_password)
    rolling_restart()

    print("[5/5] Verifying credential at application level...")
    if not verify_db_auth():
        sys.exit(1)

    print("\nRotation complete.")

if __name__ == "__main__":
    rotate()
```

---

## Key Insight / Phrase to Say in the Interview

> "`kubectl` shows Running — but Running only means the HTTP server responded to `/healthz`. That's a different contract from 'the app can authenticate to the database.' Kubernetes never checks the second thing. The script adds that check at the end of every rotation."

---

## Follow-Up Q&A

**"Why rolling restart instead of delete all pods?"**
Rolling restart creates one new pod, waits for readiness, then removes one old pod. Availability is maintained throughout. Deleting all pods at once causes downtime equal to cold-start time.

**"What if step 5 fails?"**
Previous Secrets Manager version still exists. Re-run `ALTER USER` with the old password. Re-patch the K8s secret with the old value. Trigger another rolling restart. The script exits non-zero so CI/CD pipelines halt on failure.

**"What's the difference between readiness and liveness probes?"**
Readiness: is the pod ready to receive traffic? Kubernetes removes it from the Service endpoints if not. Liveness: is the pod alive at all? Kubernetes restarts it if not. Neither checks DB auth by default — that's an application-level contract, not a Kubernetes contract.

**"How would you rotate a secret with zero downtime if no rolling restart?"**
Use a brief dual-password window: configure the DB to accept both old and new passwords simultaneously for ~60 seconds, allow all pods to restart and pick up the new credential, then revoke the old password. Some databases (PostgreSQL with `pg_hba.conf` tricks, or connection poolers like PgBouncer) support this pattern cleanly.

**"Why base64 in Kubernetes Secrets if it's not encryption?"**
Base64 is encoding, not encryption. K8s Secrets are stored as base64 in etcd by default. For real security: enable etcd encryption at rest, use an external secrets manager (AWS Secrets Manager + External Secrets Operator), or use Sealed Secrets. Never commit a Secret manifest to git.
