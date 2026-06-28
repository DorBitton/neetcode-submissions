# requests / HTTP — SRE Reference

## 1. Basic HTTP Methods

```python
import requests

# GET with query params
r = requests.get(
    "https://api.example.com/pods",
    params={"namespace": "prod", "status": "running"},  # ?namespace=prod&status=running
    headers={"Accept": "application/json"},
    timeout=(3, 10)     # (connect_timeout, read_timeout) — ALWAYS set this
)

# POST with JSON body
r = requests.post(
    "https://api.example.com/alerts",
    json={"severity": "critical", "host": "web01"},     # sets Content-Type: application/json
    headers={"Authorization": "Bearer <token>"},
    timeout=(3, 10)
)

# PUT / DELETE
requests.put("https://api.example.com/config/1", json={"key": "val"}, timeout=(3, 10))
requests.delete("https://api.example.com/resource/42", timeout=(3, 10))
```

---

## 2. Response Object

```python
r.status_code           # 200, 404, 500 ...
r.json()                # parse JSON body → dict/list
r.text                  # raw body as string
r.content               # raw bytes (for binary)
r.headers               # dict of response headers
r.headers["Content-Type"]

# Raise on 4xx/5xx — raises HTTPError
r.raise_for_status()    # call before r.json() — prevents parsing error bodies
```

---

## 3. Exception Handling

```python
import requests

try:
    r = requests.get("https://api.example.com/health", timeout=(3, 10))
    r.raise_for_status()
    data = r.json()
except requests.exceptions.Timeout:
    print("Connection or read timed out")
except requests.exceptions.ConnectionError:
    print("DNS failure / refused connection / network unreachable")
except requests.exceptions.HTTPError as e:
    print(f"HTTP {e.response.status_code}: {e.response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")   # catch-all base class
```

---

## 4. Timeouts

```python
# INTERVIEW GOTCHA: always set timeout — default is None (hangs forever)
timeout=(3, 10)     # 3s to connect, 10s to read response
timeout=5           # same value for both connect and read

# Never:
requests.get("https://api.example.com/data")   # no timeout — hangs indefinitely
```

---

## 5. Session — Reuse Connections + Headers

```python
import requests

session = requests.Session()
session.headers.update({
    "Authorization": "Bearer my-token",
    "Accept": "application/json",
})

# All calls share the TCP connection pool + headers
r1 = session.get("https://api.example.com/nodes", timeout=(3, 10))
r2 = session.get("https://api.example.com/pods", timeout=(3, 10))
session.close()

# Or use as context manager
with requests.Session() as s:
    s.headers.update({"Authorization": "Bearer my-token"})
    r = s.get("https://api.example.com/health", timeout=(3, 10))
```

---

## 6. Auth

```python
from requests.auth import HTTPBasicAuth

# Basic auth
r = requests.get("https://api.example.com", auth=HTTPBasicAuth("user", "pass"))
r = requests.get("https://api.example.com", auth=("user", "pass"))   # shorthand

# Bearer token
headers = {"Authorization": f"Bearer {token}"}
r = requests.get("https://api.example.com", headers=headers)

# Token in session
session.headers["Authorization"] = f"Bearer {token}"
```

---

## 7. Retry with Backoff

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503])
session.mount("https://", HTTPAdapter(max_retries=retry))

try:
    r = session.get("https://api.example.com/health", timeout=(3, 10))
    r.raise_for_status()
    data = r.json()
except requests.exceptions.Timeout:
    print("timed out")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error {e.response.status_code}")
```

```python
# backoff_factor=1 means:
#   retry 1: sleep 0s
#   retry 2: sleep 2s   (1 * 2^1)
#   retry 3: sleep 4s   (1 * 2^2)
# status_forcelist=[500,502,503] — retry on these codes; 404/401 are NOT retried
```

---

## 8. Pagination

```python
import requests

def get_all_pods(base_url: str, token: str) -> list:
    results = []
    url = f"{base_url}/pods"
    headers = {"Authorization": f"Bearer {token}"}

    while url:
        r = requests.get(url, headers=headers, timeout=(3, 10))
        r.raise_for_status()
        body = r.json()
        results.extend(body["items"])

        # next page token (varies by API)
        next_token = body.get("metadata", {}).get("continue")
        url = f"{base_url}/pods?continue={next_token}" if next_token else None

    return results

# Alternative — cursor/page-based
page = 1
while True:
    r = requests.get(url, params={"page": page, "per_page": 100}, timeout=(3, 10))
    r.raise_for_status()
    data = r.json()
    if not data:
        break
    results.extend(data)
    page += 1
```
