---
title: OT/ICS Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: OT/ICS
required_data_sources:
  - OT / ICS intrusion detection (IDS)
  - Process historian
  - Engineering-workstation / HMI endpoint telemetry
status: draft
---

# OT/ICS Triage Playbook

Triage knowledge for **OT/ICS** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| Unauthorized controller / PLC command or logic change | OT IDS / historian | Impair Process Control | T0855 (Unauthorized Command Message), T0831 (Manipulation of Control) | IC-14 (OT/ICS Attack) |
| Industrial-protocol anomaly | OT IDS | Collection | T0801 (Monitor Process State), T0830 (Adversary-in-the-Middle) | IC-14 (OT/ICS Attack) |
| Engineering-workstation / HMI compromise | OT IDS / EDR | Lateral Movement | T0866 (Exploitation of Remote Services), T0822 (External Remote Services) | IC-14 (OT/ICS Attack), IC-08 (Infrastructure Compromise) |

## Per-Alert Triage

### Unauthorized controller / PLC command or logic change

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (the controller and the issuing workstation), [User](../99-Shared/sub_enrichment_identity.md) (the issuing engineer or workstation account), [File](../99-Shared/sub_enrichment_artifact.md) (the controller logic file, if a program change).
- **Checks:**
  1. **Change authorization.** Does the command or logic change tie to an approved maintenance or commissioning window and a change ticket naming the controller? → `Benign (High)` when a recorded ticket covers the controller, the engineer and the time; `Malicious (Medium)` when no change record exists — an untracked change to controller logic.
  2. **Command origin.** Where did the command come from? → `Benign (Medium)` when it came from the authorized engineering workstation through the engineering software on its normal path; `Malicious (High)` when it came from a host outside the engineering asset set, from an IT-network address, or over an unexpected protocol path — a direct write from a non-engineering source; `Malicious (Medium)` when it came from an engineering workstation outside its normal hours under an account not assigned to that controller.
  3. **Change content.** What changed — a logic download, a setpoint write, a mode change (run, stop, program), a firmware push? → `Malicious (High)` when the downloaded logic differs from the approved program baseline in the engineering repository, or firmware was pushed outside a documented update; `Malicious (Medium)` on a mode change to stop or program outside a window; `Benign (Medium)` when the downloaded logic matches the approved version in the repository.
  4. **Process-safety relevance.** Does the change touch a safety-critical setpoint, an interlock or a safety-instrumented function (per the asset inventory's safety criticality and network level)? → `Malicious (Medium)` when a setpoint was moved outside the process's engineered operating range; otherwise context for the verdict — a safety-relevant change raises the Case severity to High or Critical regardless of the authorization finding.
  5. **Historian corroboration.** Did process variables deviate or alarms fire at the time of the write? → `Malicious (Medium)` when the process responded in a way no operator intended; context when no effect is visible.
  6. **Scope.** Is the same command reaching several controllers within minutes? → `Malicious (High)` — a scripted manipulation; context when confined to one controller.
- **False Positive conditions:** a baseline learned before a plant change flagging a periodic write the supervisory system performs by design; a parser reading a read request as a write; a diagnostic or keepalive message classified as a command; the passive monitoring tool's own inventory queries.
- **Benign conditions:** authorized engineering work or commissioning in a scheduled window by the assigned engineer; vendor remote support under an approved session; an operator setpoint change within the HMI's configured permissions.
- **Candidate Incident Category(ies):** IC-14 (OT/ICS Attack).

### Industrial-protocol anomaly

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (the source and target controllers), [Network observable](../99-Shared/sub_enrichment_network.md) (the industrial-protocol session, if IP-routable).
- **Checks:**
  1. **Function-code legitimacy.** Are the observed function codes (Modbus, DNP3, OPC UA or a vendor-proprietary protocol) the reads and writes of expected registers this process normally uses, or rare and diagnostic codes — force outputs, write multiple registers, restart, clear memory, firmware — outside routine operation? → `Malicious (Medium)` on rare or diagnostic codes; `Benign (Low)` on the reads normal for this process.
  2. **Source legitimacy.** Where does the traffic come from? → `Benign (High)` when the source is a known historian, supervisory server or engineering asset on its normal polling schedule against its baseline targets; `Malicious (High)` when the source is absent from the OT asset inventory, is an IT-network address, or has never spoken this protocol; `Malicious (Medium)` when a known asset addresses a controller outside its baseline.
  3. **Maintenance correlation.** Does the anomaly align with a scheduled maintenance or commissioning activity on the affected controller? → `Benign (High)` when a recorded activity covers the controller and the window; context when none is recorded.
  4. **Traffic pattern.** What does the session look like? → `Malicious (High)` on sequential sweeps of unit identifiers, registers or addresses, or one new source polling many controllers — reconnaissance; `Malicious (High)` on adversary-in-the-middle signs — a new hardware address answering for the controller or the master, duplicated or delayed responses; `Benign (Low)` on a changed poll cycle from a known source.
  5. **Process effect.** Does the historian show process values changing at the time of any writes? → `Malicious (Medium)` when they do; context when they do not.
- **False Positive conditions:** a baseline learned before a plant change — a new poller, a new register set — and not relearned; a parser mis-decoding a vendor-extended function code; the OT security tool's own asset-discovery probe; a retransmission storm from a faulty link classified as protocol anomaly.
- **Benign conditions:** scheduled maintenance; commissioning of a new device; vendor diagnostics in an approved window; an authorized active vulnerability assessment of the OT network in a recorded window.
- **Candidate Incident Category(ies):** IC-14 (OT/ICS Attack).

### Engineering-workstation / HMI compromise

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (the engineering workstation or HMI), [User](../99-Shared/sub_enrichment_identity.md) (the logged-on account), [File](../99-Shared/sub_enrichment_artifact.md) (any dropped tooling), [Process](../99-Shared/sub_enrichment_artifact.md) (processes launched in the session), [Network observable](../99-Shared/sub_enrichment_network.md) (the remote-access source).
- **Checks:**
  1. **Access vector.** How was the workstation or HMI reached? → `Benign (Medium)` through the sanctioned remote-support path — the jump host or remote-access broker in the demilitarized zone, with multi-factor authentication; `Malicious (High)` through an unsanctioned path — a direct remote-desktop or screen-sharing session from the IT network or the internet, an exploit of a remote service, or a remote-access tool not on the OT allowlist.
  2. **Account and authorization.** Who logged on? → `Benign (High)` when a known OT administrator or a vendor engineer under an approved remote-session record; `Malicious (Medium)` when the account is not assigned to OT, a shared account is used outside its shift, or a new local account appears.
  3. **IT-side precursor.** Does the same account or source host carry a preceding credential-theft, malware or lateral-movement alert on the IT side? → `Malicious (High)` on a traced IT-to-OT pivot; context when none exists.
  4. **Post-access behaviour.** What did the session do? → `Malicious (High)` when it launched the engineering software and issued controller writes or logic downloads, ran discovery of the OT network, dropped tooling, or disabled security tooling on the workstation; `Benign (Low)` when it was limited to routine monitoring or administration — viewing HMI screens, patching in a window.
  5. **Host artifacts.** Were files dropped, services created or removable media introduced? → `Malicious (High)` on a known malware family or ICS-specific tooling; `Malicious (Medium)` on removable media outside the documented media procedure; `Benign (Medium)` on a signed vendor engineering-software update under a ticket.
- **False Positive conditions:** the EDR flagging the engineering software's own behaviour — polling controllers, loading vendor libraries — as compromise; a detection firing on every remote session including the sanctioned broker's; an allowlist not updated after the remote-support tool was upgraded.
- **Benign conditions:** routine administrator activity through the sanctioned access path; vendor remote support under an approved session; a patch window; an authorized assessment of the workstation.
- **Candidate Incident Category(ies):** IC-14 (OT/ICS Attack); IC-08 (Infrastructure Compromise) when the compromise stops at the workstation without controller interaction.
