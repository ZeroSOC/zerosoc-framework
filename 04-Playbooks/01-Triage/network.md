---
title: Network Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: Network
required_data_sources:
  - Network flow / NDR
  - Proxy / web gateway logs
  - Firewall logs
  - DNS logs
status: draft
---

# Network Triage Playbook

Triage knowledge for **Network** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| C2 beaconing / known-bad destination | Network / proxy / firewall | Command and Control | T1071 (Application Layer Protocol), T1571 (Non-Standard Port) | IC-05 (Commodity Malware / Loader) |
| Download from known-malicious / newly-registered domain | Proxy / DNS / firewall | Command and Control | T1105 (Ingress Tool Transfer) | IC-05 (Commodity Malware / Loader) |
| Outbound data spike | Network / CASB / firewall | Exfiltration | T1567 (Exfiltration Over Web Service), T1048 (Exfiltration Over Alternative Protocol) | IC-11 (Data Breach / Exfiltration), IC-03 (Ransomware & Digital Extortion) |
| DoS / DDoS pattern | Network / DDoS appliance | Impact | T1498 (Network Denial of Service), T1499 (Endpoint Denial of Service) | IC-04 (Denial of Service) |
| Internal scan / lateral movement | Network / NDR | Discovery | T1046 (Network Service Discovery), T1021 (Remote Services) | IC-06 (Identity & Credential Attack), IC-08 (Infrastructure Compromise) |
| DNS tunneling / suspicious DNS | DNS / NDR | Command and Control | T1071.004 (DNS), T1572 (Protocol Tunneling) | IC-11 (Data Breach / Exfiltration), IC-05 (Commodity Malware / Loader) |
| Anomalous access / change on network-edge device | Network device logs | Persistence | T1133 (External Remote Services) | IC-08 (Infrastructure Compromise) |

## Per-Alert Triage

### C2 beaconing / known-bad destination

- **Enrich entities:** [Network observable](../99-Shared/sub_enrichment_network.md) (destination IP/domain), [Device](../99-Shared/sub_enrichment_asset.md) (source host), [User](../99-Shared/sub_enrichment_identity.md) (host owner).
- **Checks:**
  1. **Periodicity and jitter.** Is the connection interval tightly regular, or does it match a known software-update or telemetry schedule? → `Malicious (Low)` on a rigid, low-jitter interval to an unrecognized destination — the beacon signature, but update and telemetry traffic is regular too; `Benign (Medium)` when the interval matches a known update or telemetry schedule.
  2. **Destination reputation.** Is the destination threat-intelligence-flagged, newly registered, or hosted on infrastructure with no legitimate business purpose? → `Malicious (High)` when a threat-intelligence feed lists it as active command-and-control; `Malicious (Medium)` when it is newly registered or on hosting with no explainable purpose; `Benign (High)` when it is a baselined vendor update or telemetry endpoint recorded in the SOC Knowledge Base — the periodicity is explained; `Benign (Medium)` when it is a well-known vendor's infrastructure not yet baselined.
  3. **Port/protocol mismatch.** Is the traffic using a non-standard port for its apparent protocol, or tunneling inside an allowed protocol? → `Malicious (Medium)` on a mismatch or tunneling — a common evasion trait; `Benign (Low)` when protocol and port agree.
  4. **Originating process.** Where host telemetry is available, which process opened the connections? → `Benign (Medium)` when a signed updater or management agent did; `Malicious (Medium)` when an unsigned or unknown process did.
- **False Positive conditions:** software-update or telemetry traffic with beacon-like periodicity to a known-good vendor endpoint absent from the detection's allowlist; a stale reputation entry on a sinkholed, reassigned or shared-hosting address.
- **Benign conditions:** a sanctioned monitoring agent or security sensor polling its own cloud service on a fixed interval; an authorized red-team exercise whose infrastructure and window are recorded.
- **Candidate Incident Category(ies):** IC-05 (Commodity Malware / Loader).

### Download from known-malicious / newly-registered domain

- **Enrich entities:** [Network observable](../99-Shared/sub_enrichment_network.md) (source domain/URL), [Device](../99-Shared/sub_enrichment_asset.md) (requesting host).
- **Checks:**
  1. **Domain age and reputation.** Is the source domain newly registered, threat-intelligence-flagged, or otherwise reputation-poor? → `Malicious (High)` when threat intelligence flags it as a malware-distribution or phishing host; `Malicious (Low)` when it is merely newly registered — young domains are common among legitimate new sites; `Benign (Medium)` when the domain clears reputation checks and has an established, identifiable owner.
  2. **Content retrieved.** Does the response deliver an executable, script or archive rather than ordinary web content? → `Malicious (Medium)` on a binary, script or archive from a low-reputation source; `Benign (Low)` on ordinary web content.
  3. **Host follow-through.** Did the requesting host write and execute the downloaded content? → `Malicious (High)` when execution followed the download — delivery succeeded, and the Endpoint "Ingress tool transfer to host" subsection applies; context when the content was blocked at the perimeter or never executed — delivery was attempted but did not land.
  4. **Business purpose.** Is the domain a vendor's new product site, a partner's new domain, or otherwise recorded as legitimate, and does the content match that purpose? → `Benign (High)` when it is — the download is explained; context when the domain is unknown to the organization.
- **False Positive conditions:** a reputation entry on a shared-hosting address or a CDN edge that serves many unrelated sites; a rule keyed on domain age alone.
- **Benign conditions:** a legitimate newly-registered site (a new vendor product launch, a start-up, a rebranded partner) with no other risk indicators; a security team fetching a sample from a flagged domain in an authorized analysis session.
- **Candidate Incident Category(ies):** IC-05 (Commodity Malware / Loader).

### Outbound data spike

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (source host), [User](../99-Shared/sub_enrichment_identity.md), [Network observable](../99-Shared/sub_enrichment_network.md) (destination).
- **Checks:**
  1. **Destination and schedule fit.** Does the transfer go to a sanctioned backup or cloud-storage endpoint on a known schedule, or to an unrecognized external destination outside any schedule? → `Benign (High)` when it matches a sanctioned destination on its schedule — the volume is explained; `Malicious (Medium)` when the destination is unrecognized and the transfer fits no schedule; `Malicious (High)` when the destination is threat-intelligence-flagged or an anonymous file-drop service.
  2. **Volume vs. baseline.** Is the volume a genuine outlier against this host's or user's historical egress, or within normal variance for a bulk business process? → `Malicious (Low)` on a genuine outlier — deviation from the baseline, not raw volume, is what matters; `Benign (Medium)` when it sits within the normal variance of a known process.
  3. **Transfer mechanics.** Which protocol or channel carried the data? → `Malicious (Medium)` when it went over an alternative protocol (DNS, ICMP, raw TCP to an unusual port) or to a personal cloud or file-sharing service; `Benign (Low)` when it went over a sanctioned sync or backup client's channel.
  4. **Preceding activity.** Did the spike follow a mass file-access or staging alert on the same host or user, or a ransom-note alert? → `Malicious (High)` when preceded by collection or staging — exfiltration — or by a ransom note — extortion with data theft; context when nothing preceded it.
- **False Positive conditions:** a threshold on raw volume with no baseline, firing on a routine bulk process; a NAT egress aggregating many hosts counted as one source; a parser double-counting bidirectional flows.
- **Benign conditions:** a legitimate bulk transfer recorded as approved (a dataset delivered to a partner, a migration); a scheduled backup job to its sanctioned destination.
- **Candidate Incident Category(ies):** IC-11 (Data Breach / Exfiltration); IC-03 (Ransomware & Digital Extortion) when the spike follows extortion indicators.

### DoS / DDoS pattern

- **Enrich entities:** [Network observable](../99-Shared/sub_enrichment_network.md) (source IPs), [Device](../99-Shared/sub_enrichment_asset.md) (targeted service).
- **Checks:**
  1. **Source distribution.** Is traffic distributed across many disparate, often spoofed or botnet-associated sources, or concentrated from a few legitimate-looking clients? → `Malicious (High)` when the sources are on a botnet or booter threat-intelligence feed; `Malicious (Medium)` on a wide distribution of spoofed or disparate sources; `Benign (Low)` when concentrated from a few identifiable clients — the shape of a misconfiguration.
  2. **Traffic shape.** Does the flood match a known denial-of-service vector (SYN flood, UDP amplification, application-layer flood with no valid sessions) rather than an organic usage pattern? → `Malicious (High)` on a vector fingerprint; `Benign (Medium)` when sessions complete, the request mix is normal and the geography matches real users.
  3. **Correlated event.** Does the surge coincide with a business event (product launch, marketing campaign, failover) or an identified internal retry or failover loop that would explain the volume? → `Benign (High)` when a recorded event or an identified loop explains it; `Malicious (Low)` when no cause is found.
  4. **Extortion or claim.** Has a ransom demand been received, or has a group claimed the attack against the organization? → `Malicious (High)`; context when none.
- **False Positive conditions:** a threshold set below the service's normal peak; a detection counting a load balancer's or a CDN's health checks as a flood; a monitoring system's synthetic traffic.
- **Benign conditions:** a legitimate traffic surge from a marketing event, product launch or failover; an authorized load test or resilience test with a documented window; an internal misconfiguration (a retry or failover loop) generating the flood — not an attack, recorded until fixed.
- **Candidate Incident Category(ies):** IC-04 (Denial of Service).

### Internal scan / lateral movement

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (source and target hosts), [User](../99-Shared/sub_enrichment_identity.md) (source-host owner).
- **Checks:**
  1. **Scope and pattern.** Is the source touching many hosts and ports in a systematic sweep, or making targeted connections to specific hosts with valid credentials? → `Malicious (Medium)` on a sweep from a host with no scanning role, or on targeted credentialed connections — lateral movement proper; `Benign (Low)` when the connections are few and consistent with the source's role (a monitoring server polling its targets).
  2. **Source authorization.** Does the source IP or host match the approved vulnerability-scanner or asset-discovery inventory? → `Benign (High)` when it does and the sweep falls in its schedule — the fastest clearing signal; `Malicious (Medium)` when the source is a workstation or a server with no scanning role.
  3. **Credential and protocol used.** For host-to-host connections, are remote-administration protocols (RDP, SMB, WinRM, SSH) used with credentials not normally used by that source? → `Malicious (High)` on anomalous credential use over an administration protocol, or on a credential seen in a credential-dumping alert; `Benign (Low)` when protocol and credential match the source's normal administrative pattern.
  4. **Target outcome.** Were authenticated sessions established on the targets? → `Malicious (Medium)` when sessions were established on several targets; context when every connection was refused.
- **False Positive conditions:** a threshold that makes a monitoring system's routine polling look like a sweep; a rule not updated after a scanner's address changed; a discovery-protocol broadcast counted as a scan.
- **Benign conditions:** an authorized vulnerability scanner or asset-discovery sweep; an approved penetration test whose scope covers the source and the window; a sanctioned bulk remote-administration task.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack) when the movement rides on stolen credentials; IC-08 (Infrastructure Compromise).

### DNS tunneling / suspicious DNS

- **Enrich entities:** [Network observable](../99-Shared/sub_enrichment_network.md) (queried domain), [Device](../99-Shared/sub_enrichment_asset.md) (querying host).
- **Checks:**
  1. **Query characteristics.** Are query names abnormally long, high-entropy, or high-frequency to a single parent domain? → `Malicious (Medium)` on those encoding artifacts of a tunneled channel; `Benign (Low)` when length and rate are ordinary.
  2. **Record-type anomalies.** Is the traffic dominated by TXT, NULL or CNAME queries rather than the A/AAAA mix a resolver produces? → `Malicious (Medium)` on an unusual record-type distribution; `Benign (Low)` on the typical mix.
  3. **Destination control.** Does the parent domain resolve to infrastructure the organization does not control, with no known legitimate service? → `Malicious (High)` when a threat-intelligence feed lists it as a tunnel endpoint; `Malicious (Medium)` when it has no explainable business purpose; `Benign (High)` when it belongs to a known service that uses DNS as a transport by design (security telemetry, anti-spam lookups, a CDN) and is recorded as such — the pattern is explained.
  4. **Querying process.** Where host telemetry is available, which process issued the queries? → `Benign (Medium)` when a known agent did; `Malicious (Medium)` when an unknown or unsigned process did.
- **False Positive conditions:** a detection scoring the long, encoded-looking hostnames of a CDN or a cloud provider's service discovery as tunneling; an entropy or length threshold too low for the organization's normal resolver traffic.
- **Benign conditions:** a chatty but legitimate resolver or security-telemetry product using DNS as a transport (reputation lookups, anti-spam checks, endpoint agents); an authorized red-team exercise with a recorded window.
- **Candidate Incident Category(ies):** IC-11 (Data Breach / Exfiltration); IC-05 (Commodity Malware / Loader).

### Anomalous access / change on network-edge device

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (edge device), [User](../99-Shared/sub_enrichment_identity.md) (administrator account), [Network observable](../99-Shared/sub_enrichment_network.md) (source IP of the administrative session).
- **Checks:**
  1. **Change-control correlation.** Does the configuration change or administrative access tie to an approved maintenance window or change ticket? → `Benign (High)` when a ticket names the device and the change — the access is explained; `Malicious (Medium)` when it is untracked.
  2. **Access origin.** Was the session initiated from a recognized management network or jump host, or from an unfamiliar external IP? → `Malicious (High)` on external-origin administrative access to an edge device; `Benign (Low)` when it comes from the management network.
  3. **Change content.** Does the change add remote-access paths (a new VPN user, an opened port, an added static route, disabled logging) rather than routine tuning? → `Malicious (Medium)` when it expands external reachability or reduces visibility; `Benign (Low)` for routine tuning.
  4. **Firmware modification.** Was device firmware or a configuration file replaced outside the vendor's update process? → `Malicious (High)` when the image does not match a published release or was installed outside any update process — persistence on the device; `Benign (Medium)` when it matches a published release installed under change control.
  5. **Exposure to known exploitation.** Is the device running a version with a known exploited vulnerability, and was the access preceded by exploit attempts against it? → `Malicious (Medium)`; context when the device is patched.
- **False Positive conditions:** a configuration-backup or compliance-audit tool's read-only sessions flagged as administrative access; a monitoring system's polling; a high-availability pair's automatic configuration sync counted as a change.
- **Benign conditions:** a sanctioned configuration change during an approved maintenance window; a vendor-support session under a recorded ticket.
- **Candidate Incident Category(ies):** IC-08 (Infrastructure Compromise).
