---
title: 08-Infrastructure Compromise Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-08
mitre_ttps:
  - T1133        # External Remote Services
  - T1078        # Valid Accounts
  - T1190        # Exploit Public-Facing Application
  - T1601        # Modify System Image
  - T1556        # Modify Authentication Process
default_severity: High
required_data_sources:
  - Network-device AAA / admin logs
  - Configuration-management / backup diffs
  - VPN logs
  - Netflow to/from the device
  - Vendor advisories / threat intelligence
status: draft
---

# 08-Infrastructure Compromise Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-08 Infrastructure Compromise` — compromise of a system other systems depend on: an edge device (router, firewall, VPN concentrator, load balancer), a server or hypervisor, or identity and backup infrastructure such as a domain controller — used as a foothold, a pivot or relay infrastructure before a business-impact objective is established, as distinct from `IC-07 (Web App Exploitation)`, which targets application logic rather than the device or host itself. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

Infrastructure carries trust the adversary wants to inherit. Edge devices are both a persistence beachhead and relay infrastructure (ORB or botnet enrollment), and are often the environment's blind spot — most carry no EDR, so device-native and network-side evidence substitute for host telemetry. Core infrastructure — domain controllers, hypervisors, identity and backup servers — holds the credentials, images and copies of everything else: its compromise exposes every system that trusts it, and the investigation scopes that exposure, not only the host.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an adversary has compromised an edge device or a core infrastructure system — through vulnerability exploitation or stolen administrative credentials — for persistent access, to harvest the trust the system holds (credentials, directory data, virtual-machine images, backups) or to enroll it as relay infrastructure, and has modified its configuration, image or authentication process.
   * **Benign:** a sanctioned configuration change, a vendor maintenance operation, a scheduled infrastructure job, or an authorized administrator working from an unusual path.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Does the running configuration or system state, diffed against the golden or backup baseline, show unauthorized change — on an edge device, new tunnels, ACL or routing changes, new local administrator users; on core infrastructure, new members of privileged groups, new policies or scheduled tasks, altered authentication modules, new hypervisor administrators or host keys, changed backup jobs or retention ([Asset](../99-Shared/sub_enrichment_asset.md))? → `Malicious (Medium)` on any change no record accounts for; `Benign (Medium)` when no difference exists against a trusted baseline taken before the alert window.
   * *Query 2:* Does an approved change ticket or a scheduled maintenance window cover the exact change, on this system, at this time? → `Benign (High)` on a match — the explanation of the alert; `Malicious (Medium)` when the change was made outside any window, or the ticket names a different system or a different change.
   * *Query 3:* Does the system's integrity check pass — the firmware or image hash against the vendor-published known-good value, the boot and kernel attestation of a hypervisor or server, the signatures of the authentication modules on identity infrastructure? → `Malicious (High)` on a mismatch or a failed attestation; `Benign (Medium)` on a match — a memory-resident implant passes an image check.
   * *Query 4:* Is the system itself initiating sessions to unknown external infrastructure — an edge device originating traffic rather than relaying client traffic, a domain controller, hypervisor or backup server opening outbound connections it never made ([Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (High)` on system-initiated egress to a destination absent from its history; `Benign (Low)` when outbound traffic is confined to the vendor's update and telemetry endpoints on the allowlist.
   * *Query 5:* Does administrative-access provenance show sessions from outside the management jump host or the administrative tier — an unmanaged workstation, a VPN client, a service account used interactively — or does threat intelligence show the system's vulnerability under active exploitation ([Identity](../99-Shared/sub_enrichment_identity.md))? → `Malicious (Medium)` on either; `Benign (Medium)` when every administrative session came from the management tier under a named administrator.
   * *Query 6:* On core infrastructure, is the trust the system holds being harvested — a directory replication request or database extraction from a host that is not a domain controller, a new trust or a modified authentication process, a virtual-machine snapshot, export or datastore access from outside the management tier, a backup catalog read or a job or retention change? → `Malicious (High)` when any such action came from outside the management tier or under a principal that never performed it; `Benign (Medium)` when each action maps to a scheduled job that ran with the same parameters in prior cycles.

**Re-classification pivots:** bulk data moved off the system → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md); encryption or backup destruction staged from the hypervisor or the backup infrastructure → [IC-03 (Ransomware & Digital Extortion)](03-ransomware.md) or [IC-13 (Destructive / Wiper Attack)](13-destructive_wiper.md); the evidence points at accounts and credentials rather than the host → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md); the entry is application-layer exploitation of an internet-facing application on the host → [IC-07 (Web App Exploitation)](07-web_app_exploitation.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-08 (Infrastructure Compromise)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Cut the external management interfaces and restrict the management plane to the jump host or the management network (reversed by restoring the interfaces); the system keeps serving.
*   Block the attacker's source addresses at the perimeter (reversed by removing the rules).
*   Disable the personal administrative identities confirmed compromised and revoke their sessions (reversed by re-enabling them); rotate the device's AAA credentials. Disabling a service identity a critical service runs under — **requires approval**.
*   Take an edge device out of path or offline — an outage for everything behind it — **requires approval**.
*   Isolate a domain controller, hypervisor, identity or backup server, or the production servers hosted on a compromised hypervisor — **requires approval**.
*   Isolate the management subnet or VLAN, or change its routing — **requires approval**.

### Eradication
*   Edge device: reflash the vendor's known-good firmware and restore the golden configuration; patch the exploited vulnerability. Where an implanted or modified image is suspected, preserve the running image for forensic analysis per [Detection & Analysis §3.3](../../03-Processes/02-detection_and_analysis.md#33-evidence-preservation--chain-of-custody) before reflashing.
*   Core infrastructure: remove the persistence found — added privileged-group members, scheduled tasks, altered authentication modules, rogue trusts, host keys, hypervisor accounts, changed backup jobs — and patch the exploited vulnerability. Rebuilding a domain controller, hypervisor or server from a known-good image — **requires approval**.
*   Rotate every secret, key and certificate the system held. For identity infrastructure, rotate the directory's key material — the ticket-granting key twice, per its standard rotation — and the credentials of every identity the compromised infrastructure could have exposed; a reset of many identities at once — **requires approval**.

### Recovery
*   Reintroduce the system in stages, with monitoring at each step, and re-run the configuration diff and the integrity check of Query 3 before each stage.
*   Restore the management-plane hardening: out-of-band management only, administrative tiering enforced, external management interfaces closed.
*   Where the system was enrolled as relay infrastructure (ORB or botnet), notify the upstream provider and, where policy requires, law enforcement through the organization's external-communications channel ([Detection & Analysis §3.2](../../03-Processes/02-detection_and_analysis.md#32-stakeholder--regulatory-notification)).
*   Feed the exploited vulnerability and the configuration-drift indicators to [Phase 1](../../03-Processes/01-preparation_and_engineering.md) as a detection-tuning signal.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-08, the integrity check of Query 3 is recorded before closure even when the Case resolved on other queries, and, for core infrastructure, the trust exposed — which secrets, identities, images and backups the system held — is enumerated.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 2 executed, or with Query 3 unrecorded.
*   Taking an edge device out of path, isolating a domain controller, hypervisor, identity or backup server, isolating the management subnet, rebuilding from image, or a mass credential reset applied without approval.
*   Reflashing or rebuilding before the exploited vulnerability is patched and the compromised credentials rotated — the foothold returns through the same door.
*   Closure leaving a confirmed foothold: a modified image, a rogue account, trust or task, or an unrotated secret the compromised infrastructure held.
*   Data moved, encryption or backup destruction staged, and the Case not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep sibling edge devices fleet-wide for the same vulnerability exposure and configuration-drift indicators.
*   Sweep for system-initiated egress matching this Incident from every device and server that should only relay or serve.
*   Sweep the identity, hypervisor and backup infrastructure for administrative sessions from outside the management tier in the last 30 days.

## References

*   MITRE ATT&CK: T1133, T1078, T1190, T1601, T1556; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Asset enrichment](../99-Shared/sub_enrichment_asset.md); [Network enrichment](../99-Shared/sub_enrichment_network.md).
