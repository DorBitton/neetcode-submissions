# Scenario: EC2 Inventory

**Difficulty:** Medium
**Topics:** boto3, pagination, argparse, CSV output

---

## Problem Statement

> "Write a script that lists all running EC2 instances across all regions, showing instance ID, name tag, private IP, and instance type. Output as CSV."

---

## Clarifying Questions to Ask

- All regions, or a specific list? (some accounts have regions disabled)
- Single AWS account or cross-account (assume-role)?
- Include stopped/terminated instances or only running?
- What should I output if the Name tag is missing?
- Should the CSV go to stdout or a file?

---

## Worked Solution

```python
#!/usr/bin/env python3
import boto3, csv, sys

def get_name_tag(tags):
    # Name tag may not exist — always use .get() with a default, never index directly
    if not tags:
        return ""
    return next((t["Value"] for t in tags if t["Key"] == "Name"), "")

def list_instances_in_region(region):
    ec2 = boto3.client("ec2", region_name=region)
    # ALWAYS use a paginator for describe_instances — truncates at 1000 without it
    paginator = ec2.get_paginator("describe_instances")
    rows = []
    for page in paginator.paginate(Filters=[
        {"Name": "instance-state-name", "Values": ["running"]}
    ]):
        for r in page["Reservations"]:
            for i in r["Instances"]:
                rows.append({
                    "region": region,
                    "instance_id": i["InstanceId"],
                    "name": get_name_tag(i.get("Tags")),
                    "private_ip": i.get("PrivateIpAddress", ""),  # may be absent for terminated
                    "type": i["InstanceType"],
                })
    return rows

def main():
    # Use us-east-1 only to enumerate regions — not to list instances
    ec2 = boto3.client("ec2", region_name="us-east-1")
    regions = [r["RegionName"] for r in ec2.describe_regions()["Regions"]]

    writer = csv.DictWriter(sys.stdout,
        fieldnames=["region", "instance_id", "name", "private_ip", "type"])
    writer.writeheader()

    for region in regions:
        try:
            rows = list_instances_in_region(region)
            writer.writerows(rows)
        except Exception as e:
            # Don't abort the whole run if one region fails (permission, disabled, etc.)
            print(f"# ERROR in {region}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
```

---

## Follow-up Questions the Interviewer Will Ask

**"Why do you use a paginator?"**
`describe_instances` returns at most 1000 results per API call and silently truncates. Without a paginator you'll miss instances in large accounts and never know. The paginator handles `NextToken` automatically.

**"How would you add a --region flag?"**
```python
p.add_argument("--region", nargs="*", help="Regions to query (default: all)")
regions = args.region or [r["RegionName"] for r in ec2.describe_regions()["Regions"]]
```
`nargs="*"` allows zero or more values: `--region us-east-1 us-west-2` or omit for all regions.

**"How would you handle cross-account access?"**
Use STS AssumeRole and pass the temporary credentials to a new session:
```python
sts = boto3.client("sts")
creds = sts.assume_role(
    RoleArn="arn:aws:iam::123456789012:role/ReadOnlyRole",
    RoleSessionName="ec2-inventory"
)["Credentials"]

session = boto3.Session(
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)
ec2 = session.client("ec2", region_name=region)
```

**"How would you make this faster?"**
Parallelize region queries with `ThreadPoolExecutor` — each region is an independent API call.
```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as pool:
    results = list(pool.map(list_instances_in_region, regions))
```

**"How would you filter by a tag, e.g., Environment=prod?"**
Add it to the Filters list:
```python
paginator.paginate(Filters=[
    {"Name": "instance-state-name", "Values": ["running"]},
    {"Name": "tag:Environment", "Values": ["prod"]},
])
```
