# TLS / HTTPS — Certificates, Inspection, and Debugging

## 1. What a TLS certificate contains

- **CN** (Common Name) — legacy hostname field; modern clients ignore it for validation
- **SAN** (Subject Alternative Name) — the hostnames/IPs the cert is valid for (required by modern clients)
- **Issuer** — CA that signed the cert (or self for self-signed)
- **Valid dates** — `Not Before` / `Not After`
- **Chain** — server cert + intermediate CA(s) leading to a trusted root

---

## 2. Inspect a certificate file

```bash
openssl x509 -in cert.pem -text -noout          # full cert info
openssl x509 -in cert.pem -noout -dates         # expiry only (Not Before / Not After)
openssl x509 -in cert.pem -noout -subject       # CN and subject
openssl x509 -in cert.pem -noout -issuer        # issuing CA
```

---

## 3. Check a live server's certificate

```bash
openssl s_client -connect example.com:443                  # connect and show cert
openssl s_client -connect example.com:443 -showcerts       # full chain (server + intermediates)

# One-liner — check expiry without interactive mode
echo | openssl s_client -connect example.com:443 2>/dev/null \
  | openssl x509 -noout -dates

curl -vI https://example.com    # HTTPS headers + TLS handshake info in verbose output
```

---

## 4. Check SANs (Subject Alternative Names)

```bash
openssl x509 -in cert.pem -text -noout | grep -A 5 "Subject Alternative Name"
```

**Why SANs matter:** Modern browsers and clients (RFC 6125) require the hostname to appear in the SAN extension. A cert with only a CN match will be rejected — "CN alone is not enough."

**Fix missing SAN:** The cert must be regenerated. Add an `[alt_names]` section to `openssl.cnf`:

```ini
[req]
req_extensions = v3_req

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = example.com
DNS.2 = www.example.com
IP.1  = 192.168.1.10
```

Then regenerate the CSR with this config:

```bash
openssl req -new -key server.key -out server.csr -config openssl.cnf
```

---

## 5. Generate RSA key + CSR

```bash
openssl genrsa -out server.key 2048                        # generate 2048-bit RSA private key
openssl req -new -key server.key -out server.csr           # generate CSR (prompts for subject info)
openssl req -noout -text -in server.csr                    # verify CSR contents before submitting
```

Submit `server.csr` to a CA. Keep `server.key` private.

---

## 6. Self-signed certificate (dev/test only)

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

- `-x509` — output a self-signed cert instead of a CSR
- `-nodes` — no passphrase on the private key (required for nginx/apache to start without a prompt)

Self-signed certs are not trusted by browsers. Use only for internal dev/test. For staging/prod use Let's Encrypt or an internal CA.

---

## 7. Fix broken certificate chain

A complete chain = **server cert + intermediate CA(s)**. Browsers and curl verify the full chain up to a trusted root. If intermediates are missing, you get "certificate verify failed" even if the cert itself is valid.

```bash
# Concatenate server cert + intermediate(s) into a full chain file
cat server.crt intermediate.crt > fullchain.pem

# Verify the chain against a CA bundle
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt fullchain.pem

# Diagnose — see what the server is actually sending
openssl s_client -connect host:443 -showcerts
```

nginx config — point to the full chain file:

```nginx
ssl_certificate     /etc/ssl/certs/fullchain.pem;   # must include intermediates
ssl_certificate_key /etc/ssl/private/server.key;
```

---

## 8. mTLS — Mutual TLS

Standard TLS: only the client verifies the server's cert.
mTLS: **both sides present certificates** — the server also verifies the client's cert.

```bash
# Test mTLS as a client using openssl
openssl s_client -connect host:443 -cert client.crt -key client.key

# Test mTLS as a client using curl
curl --cert client.crt --key client.key https://host/endpoint
```

nginx server config to require client certs:

```nginx
server {
    listen 443 ssl;
    ssl_certificate     /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;
    ssl_client_certificate /etc/ssl/certs/client-ca.crt;  # CA that signed client certs
    ssl_verify_client on;                                   # reject requests without valid client cert
}
```

---

## 9. Private key permissions

```bash
chmod 600 server.key    # owner read/write only — required
```

nginx and Apache **refuse to start** if the private key is world-readable or group-readable. Symptom: `SSL_CTX_use_PrivateKey_file() failed`. Always set 600 on any `.key` or `.pem` private key file.

---

## 10. Debug TLS vs HTTP mismatch

**Symptom:** `wrong version number`, `SSL handshake failure`, or `ERR_SSL_PROTOCOL_ERROR`.

Root cause: client and server disagree on whether the port speaks TLS or plain HTTP.

```bash
# Client sending plain HTTP to a TLS port — server expects TLS handshake
curl -v http://host:443
# Response will show garbled data or "wrong version number"

# Client sending TLS to a plain HTTP port — server responds with HTTP
openssl s_client -connect host:80
# Response shows raw HTTP headers instead of a TLS handshake

# Correct usage — TLS on 443, plain HTTP on 80
curl -v https://host:443
openssl s_client -connect host:443
```

**Fix:** Ensure the client protocol matches the server listener. Check nginx/apache config — `listen 443 ssl` for TLS, `listen 80` for plain HTTP. Do not proxy TLS traffic to an HTTP backend without termination.
