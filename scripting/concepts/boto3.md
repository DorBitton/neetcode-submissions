# boto3 — AWS SDK for Python

## Client vs Resource vs Session

```python
import boto3

# client — low-level, maps 1:1 to AWS API, always use for pagination
ec2 = boto3.client("ec2", region_name="us-east-1")

# resource — higher-level OO wrapper; limited service support, no paginators
s3 = boto3.resource("s3")

# session — explicit credentials/profile; use in scripts that switch roles
session = boto3.Session(profile_name="prod", region_name="us-west-2")
ec2 = session.client("ec2")
```

**Env vars** (picked up automatically by boto3):
```
AWS_PROFILE=prod
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY  # avoid; prefer instance role or SSO
```

---

## EC2 — describe_instances

```python
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2", region_name="us-east-1")

# List running instances with tag — must use paginator for >1000 results
paginator = ec2.get_paginator("describe_instances")
for page in paginator.paginate(Filters=[
    {"Name": "instance-state-name", "Values": ["running"]},
    {"Name": "tag:Env", "Values": ["prod"]},
]):
    for r in page["Reservations"]:
        for i in r["Instances"]:
            print(i["InstanceId"], i["PrivateIpAddress"])
```

---

## S3

```python
s3 = boto3.client("s3")

# List buckets (no pagination needed — returns all)
buckets = s3.list_buckets()["Buckets"]

# list_objects_v2 truncates at 1000 — always paginate
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket", Prefix="logs/"):
    for obj in page.get("Contents", []):
        print(obj["Key"])

# Get object body
resp = s3.get_object(Bucket="my-bucket", Key="config/app.json")
data = resp["Body"].read().decode("utf-8")

# Upload
s3.put_object(Bucket="my-bucket", Key="output/result.txt", Body=b"hello")

# Delete
s3.delete_object(Bucket="my-bucket", Key="old/file.txt")
```

---

## SSM Parameter Store

```python
# SSM secret read
try:
    ssm = boto3.client("ssm")
    val = ssm.get_parameter(Name="/app/db_password", WithDecryption=True)
    password = val["Parameter"]["Value"]
except ClientError as e:
    if e.response["Error"]["Code"] == "ParameterNotFound":
        raise ValueError("SSM param missing")
    raise
```

---

## Paginators — why they matter

AWS truncates responses at **1000 items** by default (EC2 instances, S3 objects, etc.).  
Raw API calls return a `NextToken`/`NextMarker` — paginators handle this automatically.

```python
# WRONG — silently misses results past 1000
resp = s3.list_objects_v2(Bucket="big-bucket")
keys = [o["Key"] for o in resp.get("Contents", [])]

# RIGHT
paginator = s3.get_paginator("list_objects_v2")
keys = []
for page in paginator.paginate(Bucket="big-bucket"):
    keys.extend(o["Key"] for o in page.get("Contents", []))
```

Check paginator availability: `s3.get_paginator("list_objects_v2")` — raises `OperationNotPageableError` if the API doesn't support it.

---

## Error handling — ClientError

```python
from botocore.exceptions import ClientError

try:
    s3.get_object(Bucket="my-bucket", Key="missing.txt")
except ClientError as e:
    code = e.response["Error"]["Code"]
    msg  = e.response["Error"]["Message"]
    if code == "NoSuchKey":
        print("Object not found")
    elif code == "AccessDenied":
        print("Permission denied")
    else:
        raise  # re-raise unexpected errors
```

**Common error codes:**
| Code | Trigger |
|---|---|
| `NoSuchKey` | S3 object missing |
| `NoSuchBucket` | S3 bucket missing |
| `ParameterNotFound` | SSM param missing |
| `InvalidInstanceID.NotFound` | EC2 instance ID bad |
| `AccessDenied` | IAM permission missing |
| `ThrottlingException` | Rate limited — add retry/backoff |
