---
title: 13-Destructive / Wiper Attack Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-13
mitre_ttps:
  - T1485   # Data Destruction
  - T1561   # Disk Wipe
  - T1490   # Inhibit System Recovery
  - T1486   # Data Encrypted for Impact
  - T1531   # Account Access Removal
default_severity: Critical
required_data_sources:
  - EDR
  - Backup-system logs
  - Storage / hypervisor audit logs
  - AD/GPO & deployment-infrastructure logs
  - Netflow
status: draft
---

# 13-Destructive / Wiper Attack Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-13 Destructive / Wiper Attack` — intent to destroy, corrupt or render systems and data permanently unavailable, so that recovery requires rebuild or restore. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

Wipers often masquerade as ransomware; the discriminator matters because communications, negotiation and recovery differ. Recovery is the dominant phase, and the playbook protects the backups first: a destructive actor who reaches them leaves nothing to restore from.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** a destructive attack — a wiper, a raw-disk overwrite, or the mass deletion of systems, volumes or backups — intends to render systems and data unrecoverable, possibly disguised as ransomware, and may be propagating through central deployment infrastructure.
   * **Benign:** a failed patch or storage-firmware rollout, an administrator's script error, an approved decommissioning, or a hardware or filesystem failure on a single host.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* What do the destruction mechanics show — raw-disk or partition-table overwrites, deletion with no ransom note, or a note whose payment or contact path does not work — and does threat intelligence match the artifact to a known destructive campaign ([Artifact](../99-Shared/sub_enrichment_artifact.md))? → `Malicious (High)` on a raw-disk overwrite, a non-functional demand or a campaign match — the wiper-vs-ransomware discriminator; a functional demand with recoverable encryption is the IC-03 pivot below; `Benign (Low)` when the corruption pattern matches a hardware or filesystem fault and no process wrote to the raw disk.
   * *Query 2:* Was the destructive binary pushed through group policy, the software deployment platform, the hypervisor management plane or another domain-wide mechanism? → `Malicious (High)` on a central push — and the deployment infrastructure and the domain enter the scope as compromised; `Benign (Low)` when the binary arrived through no central channel and only one host is affected.
   * *Query 3:* Does the timing correlate with a patch window, a storage-firmware update, or an approved decommissioning or change ticket covering the affected hosts? → `Benign (High)` when a change record covers the exact hosts and time and the change's own artifact is what wrote the damage — the explanation of the alert; `Malicious (Medium)` when the activity falls outside every window or the change owner disowns it.
   * *Query 4:* Did deliberate backup deletion or tampering precede the destruction — snapshots or backup jobs deleted, retention shortened, replication severed, shadow copies removed, immutable-storage locks changed (backup-system and storage audit logs)? → `Malicious (High)` on any of these; `Benign (Low)` when the backups and shadow copies are intact and untouched since before the first damage.
   * *Query 5:* How many hosts are affected and over what interval — many hosts near-simultaneously, or one host degrading over time? → `Malicious (Medium)` when many hosts fail within minutes of each other; `Benign (Medium)` when a single host degrades over hours with storage or hardware errors in its own logs.
   * *Query 6:* Were accounts disabled, passwords changed en masse, or administrators locked out around the destruction (identity-provider and directory audit logs)? → `Malicious (High)` on mass lockout coinciding with the damage; context when the identity plane shows no change.

**Re-classification pivots:** a functional ransom demand exists and the encryption is recoverable → [IC-03 (Ransomware & Digital Extortion)](03-ransomware.md); availability is lost but systems and data are intact and return when the activity stops → [IC-04 (Denial of Service)](04-dos.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-13 (Destructive / Wiper Attack)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence. The order matters: the backups are protected before anything else.

### Containment
*   Protect the backup infrastructure first: sever replication from the affected zones and revoke the credentials and sessions that reach the backup system (reversed by re-enabling replication and issuing new credentials). Isolating the backup servers themselves from the network — **requires approval**, requested before any other approval-tier action.
*   Disable the abused deployment mechanism: unlink the group policy object, pause the deployment jobs, revoke the management-plane session (reversed by re-linking or resuming). Disabling the service identity the deployment platform runs under — **requires approval**.
*   Disable the identities that pushed the destructive binary and revoke their sessions (reversed by re-enabling). A reset or disablement of many identities at once — **requires approval**.
*   Isolate the affected end-user workstations (reversed by reconnecting). Isolating a production server, hypervisor or domain controller — **requires approval**. Isolating an entire segment, VLAN or cloud network — **requires approval**.
*   Block the staging and command-and-control destinations at egress (reversed by removing the rule) and quarantine the destructive binary wherever it is staged but not yet triggered (reversed by releasing it).

### Eradication
*   Rebuild the wiped hosts from clean media; do not attempt in-place cleanup of a wiped host. Re-imaging — **requires approval**.
*   Assume domain compromise: rotate every domain credential, including the Kerberos service account (`krbtgt`, twice) — **requires approval**.
*   Eradicate the access vector used to reach the deployment infrastructure, and remove the deployment objects — policies, packages, jobs, scheduled tasks — the attacker created.
*   Remove staged-but-untriggered payloads and their scheduled tasks across the fleet.

### Recovery
*   Restore in priority tiers from offline or immutable backups taken before T0, under the organization's business-continuity and disaster-recovery plan.
*   Verify the integrity of every restored system — image hashes against known-good, a scan for the destructive artifact and its persistence — before reconnecting it.
*   Extend monitoring across the previously affected fleet and lift segment isolation gradually, each removal recorded in the Case timeline.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-13, the wiper-vs-ransomware discriminator (Query 1) is recorded even when resolution comes from other queries — communications and recovery depend on it — and the state of the backups (Query 4) and the propagation mechanism (Query 2) are recorded before the contract is emitted.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 3 executed, or with Query 4 unanswered for the backup infrastructure.
*   A verdict emitted without the wiper-vs-ransomware discriminator recorded, or not re-classified to IC-03 when the pivot applies.
*   Segment isolation, the isolation of a domain controller, deployment server, hypervisor or backup server, a domain-wide credential reset or a re-image applied without approval.
*   Segment isolation applied before the backup infrastructure is protected (replication severed, access revoked).
*   A system restored or reconnected before its integrity and the backup's integrity are verified, or closure leaving a staged payload or the deployment-infrastructure access in place — a confirmed foothold.

## Hunting Pivots

*   Hunt fleet-wide for staged-but-untriggered destructive payloads and the scheduled tasks or deployment jobs that would trigger them.
*   Sweep the backup-infrastructure access logs for reconnaissance preceding the attack — enumeration of backup sets, retention policies and immutable-storage settings.
*   Sweep the deployment platform and group policy for objects created or modified in the last 30 days by principals that never did so before.

## References

*   MITRE ATT&CK: T1485, T1561, T1490, T1486, T1531; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Artifact enrichment](../99-Shared/sub_enrichment_artifact.md); [Asset enrichment](../99-Shared/sub_enrichment_asset.md).
