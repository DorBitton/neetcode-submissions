# Scenario: Terraform Drift Detection

## Problem Statement (as interviewer would say it)

> "Your Terraform plan shows no changes. But your deployment is behaving differently than yesterday. Walk me through how you'd find what changed in AWS."

---

## Clarifying Questions to Ask

- Which resource types should we focus on — security groups, IAM roles, route tables?
- Do you have access to the Terraform state file (local or remote in S3)?
- Is AWS access read-only, or do we have full permissions?

---

## Core Concept

The **Terraform state file** is a receipt of what Terraform created. This script reads that receipt, calls the AWS API for the live state of the same resources, and diffs the two.

`terraform plan` shows what Terraform *would* change — this script shows what *already* changed without Terraform knowing.

**The blind spot:** resources created manually outside Terraform have no receipt. They are invisible to this check. You need both drift detection (this script) and a separate resource inventory check to cover that gap.

---

## Worked Solution

```python
#!/usr/bin/env python3
"""Compare Terraform state against live AWS state to detect manual changes."""
import boto3, json, sys

def load_tfstate(path):
    with open(path) as f:
        return json.load(f)

def get_security_groups_from_state(tfstate):
    """Extract security group IDs and their ingress rules from state file."""
    sgs = {}
    for r in tfstate.get("resources", []):
        if r["type"] == "aws_security_group":
            for inst in r.get("instances", []):
                sg_id = inst["attributes"]["id"]
                sgs[sg_id] = inst["attributes"].get("ingress", [])
    return sgs

def normalize_state_rules(rules):
    """Convert Terraform state ingress format to a comparable set of tuples."""
    out = set()
    for r in rules:
        for cidr in r.get("cidr_blocks", []):
            out.add((r.get("from_port", 0), r.get("to_port", 0), r.get("protocol", "-1"), cidr))
    return out

def normalize_aws_rules(rules):
    """Convert AWS API IpPermissions format to the same tuple shape."""
    out = set()
    for r in rules:
        proto = r.get("IpProtocol", "-1")
        for ip in r.get("IpRanges", []):
            out.add((r.get("FromPort", 0), r.get("ToPort", 0), proto, ip["CidrIp"]))
    return out

def detect_drift(tfstate_path):
    tfstate = load_tfstate(tfstate_path)
    state_sgs = get_security_groups_from_state(tfstate)

    if not state_sgs:
        print("No security groups in state file.")
        return

    ec2 = boto3.client("ec2")
    drift_found = False

    for sg_id, state_ingress in state_sgs.items():
        print(f"\nChecking {sg_id}...")
        try:
            r = ec2.describe_security_groups(GroupIds=[sg_id])
            aws_ingress = r["SecurityGroups"][0].get("IpPermissions", [])
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        state_rules = normalize_state_rules(state_ingress)
        aws_rules = normalize_aws_rules(aws_ingress)

        added = aws_rules - state_rules      # in AWS but not in state = manual addition
        removed = state_rules - aws_rules    # in state but not in AWS = manual deletion

        if added:
            drift_found = True
            print("  DRIFT — added in AWS (not in state):")
            for rule in added:
                print(f"    port {rule[0]}-{rule[1]} {rule[2]} {rule[3]}")
        if removed:
            drift_found = True
            print("  DRIFT — removed from AWS (still in state):")
            for rule in removed:
                print(f"    port {rule[0]}-{rule[1]} {rule[2]} {rule[3]}")
        if not added and not removed:
            print("  OK")

    print("\n" + "="*50)
    if drift_found:
        print("Drift detected.")
        print("IMPORTANT: This only checks resources tracked in the state file.")
        print("Resources created manually outside Terraform are NOT visible here.")
    else:
        print("No drift detected in tracked resources.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "terraform.tfstate"
    detect_drift(path)
```

---

## The Two Types of Drift to Explain

1. **Known resource modified manually** — this script catches it. Security group rule added via console? Diff shows it.
2. **New resource created outside Terraform** — this script returns clean even though the account has an extra security group. No state entry = invisible to this check.

Mention both. Interviewers want to see you know the limits of the tool.

---

## Key Insight to Say in the Interview

> "A clean `terraform plan` only means the resources Terraform tracks match its state file. A colleague can create a security group in the console and this script will never know. That's the blind spot — you need both drift detection and resource inventory to cover it fully."

---

## Follow-Up Q&A

**"Why not just run terraform plan?"**
`plan` shows what Terraform *would* change next time it runs. This script shows what *already* changed outside Terraform's knowledge. Also faster — no Terraform binary, provider downloads, or state lock needed.

**"How would you automate this?"**
Daily cron, compare output, alert (Slack/PagerDuty) if any `DRIFT` lines appear. Or run it on-demand as a pre-deploy gate.

**"How would you catch resources created outside Terraform?"**
AWS Config rules (e.g., flag untagged security groups with no matching Terraform tag), or a separate inventory script: list all SGs in the account, compare against every SG ID in the state file — different check, complementary coverage.

**"What about remote Terraform state in S3?"**
Download state first, then run the same script:
```bash
aws s3 cp s3://my-tfstate-bucket/env/prod/terraform.tfstate ./terraform.tfstate
python3 drift_detect.py terraform.tfstate
```

**"What other resource types would you extend this to?"**
IAM role trust policies and inline policies are high-value — those are common manual edits with security implications. Route table entries and NACLs are also worth checking in network-sensitive environments.
