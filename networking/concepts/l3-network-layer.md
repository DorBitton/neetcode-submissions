# L3 — Network Layer

> IP addressing, routing, subnetting. The foundation everything else runs on.

---

## Table of Contents

1. [What L3 Does](#1-what-l3-does)
2. [IP Addresses](#2-ip-addresses)
3. [CIDR and Subnetting](#3-cidr-and-subnetting)
4. [Routing](#4-routing)
5. [BGP Basics](#5-bgp-basics)
6. [On-prem: How Routing Works in a Data Center](#6-on-prem-how-routing-works-in-a-data-center)
7. [AWS: VPC and Route Tables](#7-aws-vpc-and-route-tables)

---

## 1. What L3 Does

L3 is responsible for **getting a packet from source to destination across networks**.

- Assigns logical addresses (IP addresses) to devices
- Decides the path a packet takes (routing)
- Does not care about reliability or ordering — that's L4's job

Key protocol: **IP (Internet Protocol)**

---

## 2. IP Addresses

Every device on a network has an IP address — a 32-bit number (IPv4) written as four octets.

```
192.168.1.10
│   │   │ │
│   │   │ └── host part
│   │   └──── host part
│   └──────── network part
└──────────── network part
```

**Private IP ranges** (not routable on the internet):
```
10.0.0.0/8          10.x.x.x          large private networks
172.16.0.0/12       172.16-31.x.x     medium private networks
192.168.0.0/16      192.168.x.x       home/office networks
```

**Special addresses:**
```
127.0.0.1           loopback (yourself)
0.0.0.0             "any address" / default route
255.255.255.255     broadcast to all hosts on local network
```

---

## 3. CIDR and Subnetting

CIDR (Classless Inter-Domain Routing) notation: `IP/prefix`

The prefix length tells you how many bits are the **network part**.
The rest are the **host part**.

```
192.168.1.0/24
             ↑
             24 bits = network, 8 bits = hosts
             2^8 = 256 addresses (254 usable, minus network + broadcast)
```

**Common subnet sizes:**
| CIDR | Hosts | Use case |
|---|---|---|
| `/32` | 1 | single IP (loopback, host route) |
| `/30` | 2 usable | point-to-point links |
| `/29` | 6 usable | small subnet |
| `/28` | 14 usable | small subnet |
| `/24` | 254 usable | typical subnet |
| `/22` | 1022 usable | larger subnet |
| `/16` | 65534 usable | VPC / large network |
| `/8` | 16M usable | huge block (10.x.x.x) |

**Quick calculation:**
- Hosts = 2^(32 - prefix) − 2
- `/24` → 2^8 − 2 = 254 hosts
- `/28` → 2^4 − 2 = 14 hosts

**Why subnetting matters for SRE:** When you design a VPC or on-prem network, you allocate CIDR blocks for each subnet, region, or environment. Getting this wrong is expensive to fix later.

---

## 4. Routing

A **routing table** is a list of rules: "to reach network X, send packets to Y."

```
Destination       Gateway         Interface
0.0.0.0/0         10.0.0.1        eth0      ← default route (everything else)
10.0.0.0/8        direct          eth0      ← local network
192.168.1.0/24    10.0.0.254      eth1      ← specific subnet via gateway
```

**Longest prefix match:** when multiple routes match, the router picks the most specific one.
```
Packet to 192.168.1.5:
  matches 0.0.0.0/0       → 0 bits matched
  matches 192.168.1.0/24  → 24 bits matched ← wins (most specific)
```

**Useful commands:**
```bash
ip route show              # show routing table (Linux)
ip route get 8.8.8.8       # which route would be used for this IP
route -n                   # older alternative
traceroute 8.8.8.8         # show each hop a packet takes
ping 8.8.8.8               # test basic connectivity
```

---

## 5. BGP Basics

**BGP (Border Gateway Protocol)** is how the internet (and large on-prem networks) exchange routing information between autonomous systems.

You don't need to configure BGP as an SRE, but you need to understand:

- **AS (Autonomous System):** a network under one organization's control with a unique AS number
- **eBGP:** BGP between different organizations (internet routing)
- **iBGP:** BGP within the same organization (internal routing)
- **BGP advertises prefixes:** "I can reach 203.0.113.0/24, send those packets to me"

**Why SREs care about BGP:**
- Multi-datacenter failover often uses BGP to advertise the same IP from multiple locations
- AWS Direct Connect uses BGP to connect on-prem to AWS
- BGP route leaks or misconfiguration can cause major outages (this comes up in incident postmortems)

---

## 6. On-prem: How Routing Works in a Data Center

```
Internet
   │
   ▼
[Edge Router]          ← BGP with upstream ISPs, announces your IP blocks
   │
   ▼
[Core Switch/Router]   ← routes between internal subnets and VLANs
   │
   ├── [Server VLAN]   10.0.1.0/24
   ├── [DB VLAN]       10.0.2.0/24
   └── [Mgmt VLAN]     10.0.3.0/24
```

**VLANs (Virtual LANs):** logical separation of networks on the same physical switches. Each VLAN is a broadcast domain. Routing between VLANs requires a router or L3 switch.

**Common on-prem routing scenario:**
- Each rack has a top-of-rack (ToR) switch
- ToR switches connect to spine/leaf switches
- Routing between subnets happens at the leaf or core layer
- BGP or OSPF used for dynamic routing updates

---

## 7. AWS: VPC and Route Tables

AWS VPC (Virtual Private Cloud) is AWS's version of a private network. Same concepts, different terminology.

### VPC structure
```
VPC: 10.0.0.0/16
├── Subnet A (public)  10.0.1.0/24   us-east-1a
├── Subnet B (public)  10.0.2.0/24   us-east-1b
├── Subnet C (private) 10.0.3.0/24   us-east-1a
└── Subnet D (private) 10.0.4.0/24   us-east-1b
```

**Public vs private subnet:** the difference is whether the route table has a route to an Internet Gateway.

### AWS Route Tables

Every subnet has a route table. Same concept as on-prem routing tables.

```
VPC Main Route Table:
Destination     Target
10.0.0.0/16     local              ← traffic within VPC stays local
0.0.0.0/0       igw-xxxxx          ← everything else → Internet Gateway
```

```
Private Subnet Route Table:
Destination     Target
10.0.0.0/16     local
0.0.0.0/0       nat-xxxxx          ← outbound via NAT Gateway (no inbound)
```

### On-prem ↔ AWS mapping

| On-prem concept | AWS equivalent |
|---|---|
| Data center network | VPC |
| VLAN / subnet | Subnet |
| Router + routing table | Route Table |
| Firewall ACL | Security Group + NACL |
| BGP to ISP | Internet Gateway |
| MPLS / leased line to DC | Direct Connect |
| VPN to branch office | Site-to-Site VPN |
| Multiple DCs routing together | Transit Gateway |

### VPC connectivity options

```
VPC Peering          ← connect two VPCs directly (same or different accounts)
Transit Gateway      ← hub-and-spoke: connect many VPCs + on-prem
Direct Connect       ← dedicated physical line from on-prem to AWS (like MPLS)
Site-to-Site VPN     ← encrypted tunnel from on-prem to AWS over internet
```
