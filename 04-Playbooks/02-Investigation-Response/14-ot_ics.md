---
title: 14-OT/ICS Attack Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-14
mitre_ttps:
  - T0855   # Unauthorized Command Message
  - T0831   # Manipulation of Control
  - T0866   # Exploitation of Remote Services
  - T0822   # External Remote Services
  - T0801   # Monitor Process State
default_severity: Critical
required_data_sources:
  - OT IDS
  - Process historian
  - Engineering-workstation / HMI endpoint telemetry
  - Control-network flows
  - Change / maintenance schedule
status: draft
---

# 14-OT/ICS Attack Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-14 OT/ICS Attack` — manipulation or disruption of physical or industrial processes through control systems. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

OT incidents carry physical-safety consequences. The investigation works from the IT side — the engineering workstation, the HMI, the IT→OT conduit — and any action that stops or changes a physical process, a controller, a safety system or an OT network segment is in the approval tier of the autonomy matrix. A deviation toward a safety limit is passed to plant operations on the plant's life-safety channel the moment it is observed, whatever the state of the hypotheses: the life-safety path does not wait for a verdict.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an adversary is manipulating controllers or the physical process — through a compromised engineering workstation or HMI, or by direct industrial-protocol access (write, mode-change or command messages over Modbus, DNP3, OPC UA, IEC 61850 or a proprietary protocol) — threatening process integrity and safety.
   * **Benign:** authorized engineering, commissioning or maintenance activity producing controller changes and protocol anomalies, or a monitoring baseline that has not caught up with a legitimate change.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Does the change correlate with an open maintenance window, a work order or a commissioning plan that names the controller, the change and the engineer (change and maintenance schedule)? → `Benign (High)` when the work order covers the exact controller, change and time and the activity matches it — the explanation of the alert; `Malicious (Medium)` when no work order exists or the named engineer disowns the change.
   * *Query 2:* Was the command issued from a sanctioned engineering workstation at the expected network level, or from the IT network, a remote-access path or an unknown device ([Asset](../99-Shared/sub_enrichment_asset.md), [Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (High)` from the IT network, a remote source or an unknown device; `Malicious (Medium)` from a sanctioned workstation outside its normal hours or under an unfamiliar user; `Benign (Low)` from the sanctioned workstation, the usual engineer and the usual hours — a compromised workstation issues the same commands.
   * *Query 3:* Does the controller logic, configuration or firmware differ from the last-known-good project file (program upload and hash comparison)? → `Malicious (High)` when the difference disables alarms or interlocks, or alters safety logic; `Malicious (Medium)` on any undocumented difference; `Benign (Medium)` when the logic matches the last-known-good file or the version the work order names.
   * *Query 4:* Do historian values deviate toward or violate safety setpoints, or does the physical process behave inconsistently with what the HMI displays? → `Malicious (High)` on a deviation with no process cause and command messages preceding it; `Benign (Low)` when values are within their normal band and agree with the HMI. On any deviation toward a safety limit, notify plant operations on the life-safety channel immediately, before the hypotheses are resolved, and record the time in the Case timeline.
   * *Query 5:* Are there IT-side compromise indicators on the engineering workstation or HMI that bridges IT to OT — unsanctioned remote-access tools, credential dumping, unknown engineering software, unsigned binaries, command-and-control traffic (EDR)? → `Malicious (High)` on any of these; `Benign (Low)` when the host is clean — where the host carries no endpoint telemetry, that is a visibility gap, not a Benign finding.
   * *Query 6:* Which protocol operations reached which controllers — writes, mode changes (program/run/stop), firmware uploads, or polling of process state from a source that never polled before — across the control network, not only the alerted controller (OT IDS, control-network flows)? → `Malicious (High)` on writes, mode changes or uploads from an unsanctioned source; `Malicious (Medium)` on new polling of process state from an unfamiliar source — reconnaissance precedes manipulation; `Benign (Low)` when only reads from the usual sources are seen. The controllers reached scope the response.

**Re-classification pivots:** the compromise is limited to the IT-side edge or bridge and has not reached the control network → [IC-08 (Infrastructure Compromise)](08-infrastructure_compromise.md); OT hosts are encrypted or wiped with no manipulation of the process → [IC-03 (Ransomware & Digital Extortion)](03-ransomware.md) or [IC-13 (Destructive / Wiper Attack)](13-destructive_wiper.md); the change was made by an authorized engineer abusing access → [IC-09 (Insider Threat & Privilege Misuse)](09-insider_threat.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-14 (OT/ICS Attack)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence. Every approval-tier action on the control side is applied per the plant's operating procedures, with the process engineer.

### Containment
*   IT-side first: isolate the engineering workstation on its IT interface (reversed by reconnecting). Isolating an HMI, or any host whose loss removes the operators' view of or control over the process — **requires approval**.
*   Revoke the remote-access sessions and disable the identities that issued the commands (reversed by re-enabling), and block the external source at the IT→OT boundary (reversed by removing the rule). Closing the IT→OT conduit entirely, or isolating an OT segment — **requires approval**.
*   Controller-side actions — placing a controller in manual mode, disconnecting engineering access to it, stopping a PLC, or any action on a safety-instrumented system — **requires approval**.

### Eradication
*   Restore validated controller logic, configuration and firmware from the known-good project files, under engineering supervision — **requires approval**.
*   Rebuild the engineering workstation or HMI from clean media — **requires approval**.
*   Close the remote-access vector: remove the unsanctioned remote-access tools and engineering software, patch the exploited service, and rotate the credentials confirmed to have OT reach. A rotation of all credentials with OT reach — **requires approval**.

### Recovery
*   Perform a staged restart of the process per plant procedures — **requires approval**.
*   Validate process values against the historian baselines before resuming normal operation, and lift the IT-side isolation gradually, each removal recorded in the Case timeline.
*   Conduct a joint post-incident safety review with plant operations as input to Phase 4.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-14, every controller reached (Query 6) is enumerated with its logic verified against the known-good project file, and any safety-setpoint deviation (Query 4) carries the time plant operations were notified.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   Any controller, safety-system, OT-segment or process-state action — manual mode, stop, restart, logic restore, isolation — applied without approval.
*   A safety-setpoint deviation observed and plant operations not notified on the life-safety channel at that moment, or the notification deferred until resolution.
*   A Benign close without Query 1 executed, or with Query 3 unanswered for the alerted controller.
*   Controller logic restored or a rebuilt workstation reconnected without verification against the known-good project file, or closure leaving modified logic in any controller — a confirmed foothold.
*   A compromise confined to the IT-side bridge not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep the OT monitoring platform for write, mode-change and firmware-upload operations from non-engineering sources in the last 30 days, across every controller.
*   Sweep the IT side for remote-access tools and engineering software on hosts with a route into the control network.
*   Compare every controller's running program against its project file — a modified controller nobody alerted on is the one to find.

## References

*   MITRE ATT&CK for ICS: T0855, T0831, T0866, T0822, T0801; NIST SP 800-61 Rev. 3; NIST SP 800-82; ISA/IEC 62443.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Asset enrichment](../99-Shared/sub_enrichment_asset.md); [Network enrichment](../99-Shared/sub_enrichment_network.md).
