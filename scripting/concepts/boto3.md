# boto3 — AWS SDK for Python

## What boto3 is

boto3 is Amazon's official Python SDK for AWS. Every AWS service — EC2, S3, SSM, IAM, EKS, Route53 — has a boto3 client. Instead of writing raw HTTP requests to the AWS API yourself, you call Python functions. boto3 handles all of the low-level work: authentication, request signing (AWS Signature V4), automatic retries on transient failures, and parsing the JSON response into a Python dict.

Without boto3:
- You'd need to manually sign every HTTP request with your credentials using AWS's signature algorithm
- You'd parse raw HTTP JSON yourself
- You'd implement retry logic yourself

With boto3, you just call `ec2.describe_instances(...)` and get back a Python dict.

---

## 1. client vs resource vs session

These three concepts confuse almost everyone at first. Here's what each one is.

### boto3.client — the one you'll use most

```python
import boto3

# Create a low-level client for EC2 in us-east-1
ec2 = boto3.client("ec2", region_name="us-east-1")
```

A client is a **direct mapping to the AWS API**. Every method on a client corresponds 1:1 to one AWS API call. The response is always a raw Python dict — whatever AWS returned, parsed from JSON.

Why use it:
- It works for every AWS service
- It gives you full control over every parameter
- It supports **paginators** (explained in section 5)
- When you look up AWS documentation, the API call names match the client method names exactly (`describe_instances` → `ec2.describe_instances(...)`)

### boto3.resource — the higher-level wrapper

```python
# Create a higher-level resource interface for S3
s3 = boto3.resource("s3")

# Instead of a dict, you get a Bucket object with methods on it
bucket = s3.Bucket("my-bucket")
bucket.download_file("key/file.txt", "/local/path/file.txt")
```

A resource is an **object-oriented wrapper** around the client. Instead of getting a dict back, you get an object with methods. `s3.Bucket("name")` returns a Bucket object; `ec2.Instance("i-1234")` returns an Instance object.

Why it exists: some people find the OO style easier to read.

Why you'll mostly use client instead:
- Resources are only available for **some** services (S3, EC2, DynamoDB, SQS — not SSM, EKS, Route53, etc.)
- Resources have **no paginators** — you can hit the 1000-result truncation silently
- Clients are what every AWS tutorial, Stack Overflow answer, and colleague example uses

### boto3.Session — how you pick which credentials to use

```python
# Use the "prod" profile from ~/.aws/credentials
session = boto3.Session(profile_name="prod", region_name="us-west-2")

# Now create a client from that session — it uses prod credentials
ec2 = session.client("ec2")
```

A Session is how you specify **which AWS account or credentials** to use. When you have multiple AWS accounts (dev, staging, prod), they each have a named profile in `~/.aws/credentials`. A Session lets you pick which profile to use.

You also create a Session when you need to **assume a role** in another account:

```python
# First, get temporary credentials for a role in another account
sts = boto3.client("sts")
assumed = sts.assume_role(
    RoleArn="arn:aws:iam::123456789012:role/DeployRole",
    RoleSessionName="my-deploy-session",
)
creds = assumed["Credentials"]

# Create a session with those temporary credentials
session = boto3.Session(
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)
ec2 = session.client("ec2")
```

### Environment variables

boto3 reads credentials automatically from environment variables. You don't need to pass them in code.

```bash
# Use a named profile from ~/.aws/credentials
export AWS_PROFILE=prod

# Set the default region (overrides what's in the profile)
export AWS_DEFAULT_REGION=us-east-1

# Direct credentials — fine for local testing, NEVER commit these to git
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

The credential search order boto3 uses (it tries these in order until one works):
1. Explicitly passed in code (Session/client constructor)
2. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
3. `AWS_PROFILE` environment variable → named profile in `~/.aws/credentials`
4. Default profile in `~/.aws/credentials`
5. EC2 instance role / ECS task role / Lambda execution role (when running in AWS)

In production, never use hardcoded credentials. The instance/task/Lambda role is the correct approach — AWS gives the running process temporary credentials automatically.

---

## 2. EC2 — describe_instances

### Understanding the response structure first

Before writing any code, you need to understand how AWS structures the `describe_instances` response — because it confuses everyone.

The top level is `Reservations`. This is a historical AWS concept from the early days when a "reservation" meant a block of capacity you purchased. Today it has no practical meaning, but the data structure is still nested inside it.

The hierarchy is:
```
Response
└── Reservations (list)
    └── each Reservation
        └── Instances (list)
            └── each Instance (dict with all instance details)
```

This means you always need **two nested loops**: one to iterate over Reservations, one to iterate over Instances inside each Reservation.

### Filters

Instead of fetching all instances and filtering in Python, use Filters to ask AWS to return only matching resources. This is faster and reduces the data transferred.

The filter format is always a list of dicts, each with `Name` and `Values`:
```python
Filters=[
    {"Name": "filter-name", "Values": ["value1", "value2"]},
]
```

Multiple filters in the list are **ANDed** together (instance must match all filters). Multiple values inside one filter's `Values` list are **ORed** (instance can match any value).

Common filter names for EC2:
- `instance-state-name` — "running", "stopped", "terminated"
- `tag:KeyName` — filter by a tag, e.g. `tag:Env` matches the Env tag

### Paginators for describe_instances

AWS caps `describe_instances` at 1000 results per call. If you have 1001 instances, a raw call silently returns 1000 — you have no idea you're missing one.

A paginator handles this automatically. Under the hood it reads the `NextToken` from each response and makes another API call with that token until there are no more pages. From your code's perspective, you just iterate pages.

```python
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2", region_name="us-east-1")

# get_paginator returns a Paginator object for the named API call
paginator = ec2.get_paginator("describe_instances")

# paginate() accepts the same arguments as describe_instances()
# It returns an iterator — each iteration gives you one page (up to 1000 instances)
for page in paginator.paginate(
    Filters=[
        # Only return instances that are currently running
        {"Name": "instance-state-name", "Values": ["running"]},
        # AND have the tag Env=prod
        {"Name": "tag:Env", "Values": ["prod"]},
    ]
):
    # Each page has the same structure as a raw describe_instances response
    for reservation in page["Reservations"]:       # outer loop: Reservations
        for instance in reservation["Instances"]:   # inner loop: Instances inside each Reservation
            print(instance["InstanceId"], instance.get("PrivateIpAddress", "no-ip"))
            # .get() with a default is safer than direct key access —
            # PrivateIpAddress may be missing on instances in certain states
```

---

## 3. S3

### list_buckets vs list_objects_v2

These two calls behave differently with pagination:

**`list_buckets`** — an account has at most a few hundred buckets. AWS returns all of them in one call. No pagination needed.

**`list_objects_v2`** — a single bucket can have millions of objects. AWS truncates at 1000 per call. Always use a paginator.

```python
s3 = boto3.client("s3")

# list_buckets — no pagination, returns all buckets in your account
response = s3.list_buckets()
for bucket in response["Buckets"]:   # "Buckets" is the key in the response dict
    print(bucket["Name"])

# list_objects_v2 — always paginate
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket", Prefix="logs/2024/"):
    # Why .get("Contents", []) instead of page["Contents"]?
    # If the bucket is empty OR the Prefix matches nothing, AWS omits the "Contents"
    # key entirely from the response — it's not an empty list, it's just missing.
    # Accessing page["Contents"] would raise a KeyError. .get() with [] as default is safe.
    for obj in page.get("Contents", []):
        print(obj["Key"], obj["Size"])

# Read an object's content
resp = s3.get_object(Bucket="my-bucket", Key="config/app.json")
# resp["Body"] is a streaming object — call .read() to get bytes, then decode to string
data = resp["Body"].read().decode("utf-8")

# Upload content (Body can be bytes or a file-like object)
s3.put_object(Bucket="my-bucket", Key="output/result.txt", Body=b"hello world")

# Delete a single object
s3.delete_object(Bucket="my-bucket", Key="old/file.txt")
```

---

## 4. SSM Parameter Store

### What SSM Parameter Store is

SSM Parameter Store is AWS's service for storing configuration values and secrets. Think of it as a key-value store in the cloud where your applications can look up their own config at startup instead of having it baked into environment variables or config files.

Common uses:
- Database hostnames, ports, usernames
- Feature flag values
- Environment names ("prod", "us-east-1")
- API keys and passwords (using SecureString type)

There are two parameter types that matter:
- **String** — plain text, stored and returned as-is
- **SecureString** — encrypted with a KMS key before storage

SSM Parameter Store vs Secrets Manager:
- Parameter Store is **cheaper** (free tier for standard parameters)
- Secrets Manager has automatic secret rotation built in — for database passwords that rotate, use Secrets Manager
- For non-rotating secrets and config values, Parameter Store with SecureString is common

### Reading a parameter

```python
import boto3
from botocore.exceptions import ClientError

ssm = boto3.client("ssm")

try:
    response = ssm.get_parameter(
        Name="/myapp/prod/db_password",   # parameter names use slash-separated paths by convention
        WithDecryption=True,              # IMPORTANT: for SecureString parameters, this decrypts
                                          # the value before returning it. Without this flag,
                                          # you'd get the raw KMS ciphertext — useless.
                                          # For plain String parameters, this flag is ignored.
    )
    # The value is nested under "Parameter" -> "Value"
    password = response["Parameter"]["Value"]

except ClientError as e:
    if e.response["Error"]["Code"] == "ParameterNotFound":
        # The parameter doesn't exist — raise a clear error
        raise ValueError(f"SSM parameter not found: /myapp/prod/db_password")
    raise   # unexpected error — re-raise it
```

---

## 5. Paginators — the full explanation

### Why this matters (a concrete failure scenario)

You have 1500 objects in an S3 bucket. You write this code:

```python
resp = s3.list_objects_v2(Bucket="my-bucket")
keys = [obj["Key"] for obj in resp.get("Contents", [])]
```

What happens:
1. AWS returns 1000 objects and sets `IsTruncated: True` in the response
2. AWS also returns a `NextContinuationToken` value in the response
3. Your code iterates those 1000 objects, does its work, and exits
4. You never processed 500 objects
5. You got **no error, no warning, no exception** — the script exits with code 0

This is a silent data loss bug. It's especially dangerous in scripts that process logs, send alerts, clean up old files, or sync data — you might be systematically missing records for months before anyone notices.

### How paginators fix it

A paginator reads `IsTruncated` and `NextContinuationToken` from each response automatically and makes another API call until `IsTruncated` is `False`. You just iterate pages.

```python
# WRONG — silently misses results past 1000
resp = s3.list_objects_v2(Bucket="big-bucket")
keys = [obj["Key"] for obj in resp.get("Contents", [])]
# If there are 1500 objects, this list only has 1000 entries. No error.

# RIGHT — paginator handles all pages automatically
paginator = s3.get_paginator("list_objects_v2")
keys = []
for page in paginator.paginate(Bucket="big-bucket"):
    # Each page is a dict just like the raw API response
    # .extend() appends all items from the list to keys
    keys.extend(obj["Key"] for obj in page.get("Contents", []))
# Now keys contains all 1500 objects
```

### Which API calls need paginators

Almost any "list" or "describe" call that could return many results needs a paginator. Common ones:

| Service | Call | Limit |
|---|---|---|
| S3 | `list_objects_v2` | 1000 objects |
| EC2 | `describe_instances` | 1000 instances |
| EC2 | `describe_security_groups` | 1000 groups |
| IAM | `list_users` | 1000 users |
| CloudWatch Logs | `describe_log_groups` | 50 groups |

boto3 itself knows which calls support pagination. If you try `get_paginator("some_call")` on a call that doesn't support it, boto3 raises `OperationNotPageableError`. For non-pageable calls (like `s3.list_buckets()`), just use the raw call — those always return everything.

---

## 6. Error handling — ClientError

### What ClientError is

When an AWS API call fails — the resource doesn't exist, you don't have permission, you're being rate-limited — boto3 raises a `ClientError`. The error details are in `e.response["Error"]`, which is a dict with two keys:

- `"Code"` — a machine-readable string identifying the error type (e.g. `"NoSuchKey"`, `"AccessDenied"`)
- `"Message"` — a human-readable description of what went wrong

You check `Code` to decide what to do. Different codes mean different things and require different handling.

### The pattern

```python
from botocore.exceptions import ClientError

try:
    s3.get_object(Bucket="my-bucket", Key="maybe-missing.txt")
except ClientError as e:
    # Extract the error code — this is always a string
    code = e.response["Error"]["Code"]
    msg  = e.response["Error"]["Message"]

    if code == "NoSuchKey":
        # The object doesn't exist — this is expected, handle gracefully
        print("Object not found, skipping")
    elif code == "AccessDenied":
        # IAM permissions are wrong — this is a configuration problem
        print(f"Permission denied: {msg}")
        sys.exit(1)
    elif code == "ThrottlingException":
        # We're making too many requests — back off and retry
        time.sleep(5)
        # (in a real script, use exponential backoff or let boto3's retry config handle it)
    else:
        # An error we didn't anticipate — don't silently swallow it.
        # A bare `raise` re-raises the current exception with its original traceback.
        # Never do `raise e` — that resets the traceback to this line.
        raise
```

### Why `raise` not `raise e`

In Python, `raise` (with no argument) re-raises the current exception including the full original traceback. `raise e` creates a new exception chained from the current one — the traceback shows the `raise e` line, which makes debugging harder. Always use bare `raise` to re-raise.

### Why you should always re-raise unexpected errors

It's tempting to wrap everything in `except ClientError: pass` to avoid crashes. Don't. If an API call fails for a reason you didn't anticipate — a new error code you haven't seen, a permissions regression, a service outage — you want the script to crash loudly rather than silently succeed while doing nothing. Silent failures are the hardest bugs to find.

### Common error codes

| Code | Trigger | What to do |
|---|---|---|
| `NoSuchKey` | S3 object doesn't exist | Handle gracefully or return None |
| `NoSuchBucket` | S3 bucket doesn't exist | Check bucket name, fail with clear message |
| `ParameterNotFound` | SSM parameter missing | Check parameter name, fail with clear message |
| `InvalidInstanceID.NotFound` | EC2 instance ID doesn't exist | Check ID, fail with clear message |
| `AccessDenied` | IAM permission missing | Check the role/policy, fail — don't retry |
| `ThrottlingException` | Too many API calls per second | Add backoff/retry logic |
| `RequestExpired` | System clock is wrong | Fix system clock (NTP issue) |
| `InvalidClientTokenId` | Credentials are invalid or expired | Check credential setup |
