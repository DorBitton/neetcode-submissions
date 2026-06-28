# requests — Making HTTP Calls from Python

## What requests is

`requests` is the standard Python library for making HTTP calls. You use it whenever your script needs to talk to a REST API — sending an alert to Slack or PagerDuty, calling the Kubernetes API, checking if a URL is up, polling a monitoring endpoint, or querying any service that speaks HTTP.

Python has a built-in `urllib` module, but it's verbose and awkward. `requests` wraps it with a much cleaner API. It's so widely used it's effectively standard.

Install it with: `pip install requests`

---

## 1. Basic HTTP Methods

HTTP has several methods — GET, POST, PUT, DELETE are the ones you'll use most. Here's what each does and when to use it.

```python
import requests

# -------------------------------------------------------------------
# GET — retrieve data from a server, no body sent
# -------------------------------------------------------------------
r = requests.get(
    "https://api.example.com/pods",

    # params= is for query string parameters.
    # This automatically builds: ?namespace=prod&status=running
    # DO NOT manually concatenate URL strings like f"?namespace={ns}"
    # params= handles URL encoding for you (spaces, special chars, etc.)
    params={"namespace": "prod", "status": "running"},

    headers={"Accept": "application/json"},  # tell the server we want JSON back

    # timeout= is covered in depth in section 4.
    # Short version: ALWAYS set it — requests has no default timeout.
    timeout=(3, 10)   # (connect_timeout_seconds, read_timeout_seconds)
)

# -------------------------------------------------------------------
# POST — send data to create something or trigger an action
# -------------------------------------------------------------------
r = requests.post(
    "https://api.example.com/alerts",

    # json= does two things automatically:
    #   1. Serializes your dict to a JSON string
    #   2. Sets the Content-Type: application/json header
    # If you use data= instead of json=, it sends form-encoded data
    # (like an HTML form submission) — NOT what APIs expect.
    json={"severity": "critical", "host": "web01"},

    headers={"Authorization": "Bearer <token>"},
    timeout=(3, 10)
)

# -------------------------------------------------------------------
# PUT — replace an existing resource
# -------------------------------------------------------------------
requests.put(
    "https://api.example.com/config/1",
    json={"key": "val"},
    timeout=(3, 10)
)

# -------------------------------------------------------------------
# DELETE — remove a resource
# -------------------------------------------------------------------
requests.delete("https://api.example.com/resource/42", timeout=(3, 10))
```

---

## 2. The Response Object

Every `requests.get()`, `requests.post()`, etc. returns a `Response` object. Here's what you can read from it.

```python
r = requests.get("https://api.example.com/health", timeout=(3, 10))

r.status_code           # integer: 200, 404, 500, etc.
r.json()                # parse the response body as JSON → returns a dict or list
r.text                  # response body as a string (any content type)
r.content               # response body as raw bytes (for binary files, images, etc.)
r.headers               # dict of response headers (case-insensitive)
r.headers["Content-Type"]   # e.g., "application/json; charset=utf-8"
```

### raise_for_status() — call this before r.json()

```python
r = requests.get("https://api.example.com/pods", timeout=(3, 10))

# raise_for_status() raises an HTTPError if the status code is 4xx or 5xx.
# Call it BEFORE r.json(). Here's why:
#
# If the server returns a 500 error, the response body might be an HTML error page,
# not JSON. If you call r.json() first, you get a cryptic JSONDecodeError and lose
# the actual error message. raise_for_status() first means you get a clear
# HTTPError with the status code, and the actual response body is still accessible
# via the exception.
r.raise_for_status()

data = r.json()   # safe to call now — we know the request succeeded
```

---

## 3. Exception Handling

`requests` has its own exception hierarchy. All exceptions inherit from `requests.exceptions.RequestException`, so you can catch that as a fallback for anything you didn't anticipate.

```python
import requests

try:
    r = requests.get("https://api.example.com/health", timeout=(3, 10))
    r.raise_for_status()     # raises HTTPError for 4xx/5xx
    data = r.json()

except requests.exceptions.Timeout:
    # The request took too long — either connecting or waiting for the response.
    # The server might be down, overloaded, or unreachable.
    print("Connection or read timed out")

except requests.exceptions.ConnectionError:
    # Couldn't reach the server at all.
    # Possible causes: DNS failure, connection refused, network unreachable,
    # TLS handshake failure, proxy error.
    print("DNS failure / refused connection / network unreachable")

except requests.exceptions.HTTPError as e:
    # Server responded, but with a 4xx or 5xx status code.
    # This is only raised if you called raise_for_status().
    # e.response is the Response object — you can read the error body from it.
    print(f"HTTP {e.response.status_code}: {e.response.text}")

except requests.exceptions.RequestException as e:
    # Catch-all for anything else requests might raise.
    # Good to have as a final fallback.
    print(f"Request failed: {e}")
```

The key distinction between `Timeout` and `ConnectionError`: a `ConnectionError` means you never got a response at all (DNS failed, port refused, etc.). A `Timeout` means a connection was established (or attempted) but didn't complete in time.

---

## 4. Timeouts — The Single Most Important Thing

```python
# The single most common mistake with requests: forgetting timeout=.
#
# requests has NO default timeout. None. If the server stops responding
# mid-connection, your script will hang. Forever. Not for 30 seconds.
# Forever. This means the thread, process, or cron job that called it
# also hangs forever. In production this is a serious problem.
#
# ALWAYS set timeout=. In SRE scripts this should be non-negotiable.

# Two forms:
timeout=(3, 10)   # TUPLE: (connect_timeout, read_timeout)
                  #   connect_timeout: how long to wait for the TCP connection
                  #                    to be established (the initial handshake)
                  #   read_timeout:    how long to wait for the SERVER TO START
                  #                    SENDING DATA after the connection is open
                  #   These are different! A server can accept your connection
                  #   quickly and then take 60 seconds before it starts sending
                  #   a response. read_timeout catches that.

timeout=5         # SINGLE VALUE: same limit applies to both connect and read

# Never do this:
requests.get("https://api.example.com/data")   # no timeout — hangs indefinitely
```

---

## 5. Session — Reuse Connections and Headers

Without a `Session`, each `requests.get()` call opens a brand new TCP connection: 3-way handshake, TLS handshake (if HTTPS), send request, receive response, close connection. That overhead adds up fast if you're making many calls to the same server.

A `Session` keeps the underlying TCP connection alive and reuses it across requests (HTTP keep-alive). This is typically 5–10x faster for multiple calls to the same host.

Sessions also let you set headers once that apply to every request — no more repeating `Authorization` on every call.

```python
import requests

session = requests.Session()

# session.headers.update() merges these into the session's default headers.
# Every request made through this session will include these headers automatically.
# This is where you put Authorization so you only set it once.
session.headers.update({
    "Authorization": "Bearer my-token",
    "Accept": "application/json",
})

# Both calls share the same TCP connection pool + headers
r1 = session.get("https://api.example.com/nodes", timeout=(3, 10))
r2 = session.get("https://api.example.com/pods", timeout=(3, 10))

session.close()   # release the connection

# Better: use as a context manager — automatically closes on exit
with requests.Session() as s:
    s.headers.update({"Authorization": "Bearer my-token"})
    r = s.get("https://api.example.com/health", timeout=(3, 10))
    r.raise_for_status()
    print(r.json())
    # session closes here even if an exception is raised
```

---

## 6. Auth — Authenticating Requests

```python
from requests.auth import HTTPBasicAuth

# Basic auth — username:password encoded in base64 and sent in the Authorization header.
# Only use this over HTTPS — the credentials are trivially decodable otherwise.
r = requests.get("https://api.example.com", auth=HTTPBasicAuth("user", "pass"))

# Shorthand that does the same thing — requests recognizes a 2-tuple as Basic auth
r = requests.get("https://api.example.com", auth=("user", "pass"))


# Bearer token auth — the most common pattern for modern APIs (GitHub, Kubernetes, etc.)
# The token goes in the Authorization header exactly like this.
# The word "Bearer" is required, followed by exactly one space, then the token.
# This is case-sensitive — "bearer" (lowercase) may be rejected by some APIs.
token = "eyJhbGciOiJSUzI1..."
headers = {"Authorization": f"Bearer {token}"}
r = requests.get("https://api.example.com", headers=headers)


# In a session, set it once and it applies to all requests:
with requests.Session() as s:
    s.headers["Authorization"] = f"Bearer {token}"
    r1 = s.get("https://api.example.com/pods", timeout=(3, 10))
    r2 = s.get("https://api.example.com/nodes", timeout=(3, 10))
```

---

## 7. Retry with Backoff

Networks are unreliable. Servers restart. Temporary 502/503 errors happen. Rather than failing immediately, a well-written SRE script retries with increasing delays.

The `Retry` class from `urllib3` (which `requests` uses internally) handles this.

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

retry = Retry(
    total=3,                        # retry at most 3 times (4 total attempts)

    backoff_factor=1,               # controls how long to wait between retries.
                                    # Formula: backoff_factor * (2 ** (retry_number - 1))
                                    # With factor=1:
                                    #   retry 1: sleep 0s   (1 * 2^0 = 1, but first retry skips)
                                    #   retry 2: sleep 2s   (1 * 2^1)
                                    #   retry 3: sleep 4s   (1 * 2^2)

    status_forcelist=[500, 502, 503],  # only retry on these HTTP status codes.
                                        # 500 = Internal Server Error (transient server crash)
                                        # 502 = Bad Gateway (upstream down)
                                        # 503 = Service Unavailable (overloaded)
                                        #
                                        # 404 (Not Found) is NOT in the list — retrying won't
                                        # make a missing resource appear.
                                        # 401 (Unauthorized) is NOT in the list — retrying
                                        # with the same bad credentials won't help.
)

# mount() attaches this retry adapter to all URLs starting with "https://"
# This means every request through this session to an https:// URL will use the retry logic.
# Add a second mount for http:// if you also call non-TLS endpoints.
session.mount("https://", HTTPAdapter(max_retries=retry))
session.mount("http://", HTTPAdapter(max_retries=retry))   # for non-TLS endpoints

try:
    r = session.get("https://api.example.com/health", timeout=(3, 10))
    r.raise_for_status()
    data = r.json()
except requests.exceptions.Timeout:
    print("Timed out after retries")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error {e.response.status_code} after retries")
except requests.exceptions.RequestException as e:
    print(f"Failed: {e}")
```

---

## 8. Pagination

Most APIs don't return all results at once. If you ask for all pods in a large cluster, the API returns a page of, say, 500, and a token you use to fetch the next page. You keep requesting until there's no next token.

The exact field name varies by API — Kubernetes uses `metadata.continue`, GitHub uses `Link` headers, others use `next_cursor` or `next_page_token`. Always check the API docs.

```python
import requests

def get_all_pods(base_url: str, token: str) -> list:
    results = []
    url = f"{base_url}/pods"
    headers = {"Authorization": f"Bearer {token}"}

    while url:                              # loop until there's no next page
        r = requests.get(url, headers=headers, timeout=(3, 10))
        r.raise_for_status()
        body = r.json()

        results.extend(body["items"])       # add this page's items to our list

        # Check for a continuation token — specific to the Kubernetes API.
        # body.get("metadata", {}) safely handles the case where "metadata" is absent.
        # If "continue" is absent, next_token is None, and the while loop exits.
        next_token = body.get("metadata", {}).get("continue")
        url = f"{base_url}/pods?continue={next_token}" if next_token else None

    return results


# Alternative: page number-based pagination (common in GitHub, many other APIs)
def get_all_issues(base_url: str) -> list:
    results = []
    page = 1

    while True:
        r = requests.get(
            base_url,
            params={"page": page, "per_page": 100},   # params= builds the query string
            timeout=(3, 10)
        )
        r.raise_for_status()
        data = r.json()

        if not data:      # empty list means no more pages
            break

        results.extend(data)
        page += 1

    return results
```
