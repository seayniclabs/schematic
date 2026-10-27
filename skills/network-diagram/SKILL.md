---
name: network-diagram
description: Draw a network topology diagram (L1 physical, L2 VLAN, or L3 IP subnets) as an editable draw.io file from a device inventory the user supplies. Groups devices into subnets and zones, and adds a device table. Use when the user asks for a network map, topology, rack or subnet layout, or a diagram of their home or office network.
license: MIT
source: https://github.com/seayniclabs/schematic
author: Seaynic Labs
---

# Network diagram

Turn a device list into a topology diagram the user can edit. This skill works from an inventory the user gives you. It does not scan the network.

## 1. Get the inventory

Ask for one of these, whichever the user has:

- A list in chat: device name, role (router, switch, server, NAS, workstation, IoT, access point), IP address, subnet or VLAN, and what it connects to.
- A CSV or JSON file they point to. Read it and check the columns before you draw anything.
- Output they pasted from a tool they already ran, such as `ip -br addr`, `arp -a`, or a router's client table.

Do not run network scans, port scans or discovery commands. Do not contact devices. Work only with what the user supplied.

If a link is missing (for example, which switch a server plugs into), ask once. If the user does not know, draw it as "unknown" with a dashed edge and say so in your report.

## 2. Choose the layer

| Layer | Shows | Use when |
|---|---|---|
| L1 physical | Cables and which port each device uses | Rack or cabling plans |
| L2 | VLANs and broadcast domains, with switches and access ports | Segmentation questions |
| L3 | IP subnets, routers and routes | Addressing and routing questions |

If the user does not say, draw L3, and label each subnet container with its CIDR. Draw one layer per diagram. For more than one, make one file per layer.

## 3. Lay out the diagram

- Top row: the internet or WAN edge, then the gateway or firewall.
- Next row: core and distribution switches, and routers.
- Next rows: servers, storage, access points.
- Bottom row: endpoints and IoT devices.
- Put each subnet or VLAN in a container (a swimlane or a dashed frame) labelled with its name and CIDR. Devices inside it use the container as `parent`.
- Use orthogonal edges. Label each edge with its link speed or VLAN tag when the user gave one.

Write the file with the diagram skill's rules: the `.drawio` format, descriptive ids, and cells 0 and 1 present. For a diagram that lives in a repo, write `.drawio.svg` (see the diagram skill). Use the draw.io network shapes:

| Device | Style |
|---|---|
| Router | `shape=mxgraph.cisco.routers.router;whiteSpace=wrap;html=1;` |
| Firewall | `shape=mxgraph.cisco.firewalls.firewall;whiteSpace=wrap;html=1;` |
| Switch | `shape=mxgraph.cisco.switches.workgroup_switch;whiteSpace=wrap;html=1;` |
| Server | `shape=mxgraph.cisco.servers.standard_server;whiteSpace=wrap;html=1;` |
| Laptop | `shape=mxgraph.cisco.computers_and_peripherals.laptop;whiteSpace=wrap;html=1;` |
| Wireless access point | `shape=mxgraph.cisco.wireless.wireless_access_point;whiteSpace=wrap;html=1;` |
| Cloud (internet) | `shape=cloud;whiteSpace=wrap;html=1;` |

Use a plain rounded rectangle when a device type has no shape here. Color by role or by status, never by both: one palette for the whole diagram.

## 4. Add a device table

Give the user a Markdown table next to the diagram, one row per device: name, role, address, subnet, connects to. Put it in the chat, or in a `.md` file only if the user asks for a file.

## 5. Protect private details

Diagrams get shared. Before you write the file:

- Use the addresses the user gave, but if the diagram is going into a public repo or a document, replace real addresses and hostnames with example values (`10.0.10.0/24`, `router-1`) and say that you did.
- Leave out MAC addresses, serial numbers, usernames and Wi-Fi passwords, even if the inventory contains them.
- Show a public IP only if the user asks for it.

## 6. Check and report

If the diagram skill is installed alongside this one, run its checker on the file:

```bash
python3 <skills-folder>/diagram/scripts/check_drawio.py <file>
```

Fix every problem it reports. Then report the file path as a link, the layer drawn, the number of devices and subnets, and anything marked unknown.

## Notes

- Cisco Network Sketcher (cisco-open/network-sketcher, Apache-2.0) is a separate MCP server that generates network diagrams. You can install it yourself. This skill does not depend on it.
- The diagram is a snapshot of the inventory you were given. Redraw it when the network changes.
