---
title: 11-Data Breach / Exfiltration Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-11
mitre_ttps:
  - T1048   # Exfiltration Over Alternative Protocol
  - T1567   # Exfiltration Over Web Service
  - T1041   # Exfiltration Over C2 Channel
  - T1530   # Data from Cloud Storage
  - T1074   # Data Staged
  - T1560   # Archive Collected Data
  - T1020   # Automated Exfiltration
default_severity: High
required_data_sources:
  - DLP
  - Netflow / proxy / CASB egress logs
  - Cloud-storage audit logs
  - File audit + classification labels
  - EDR
status: draft
---

# 11-Data Breach / Exfiltration Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-11 Data Breach / Exfiltration` — unauthorized access to and removal of confidential data as the defining act. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

Exfiltration is defined by the *act of removal*, regardless of actor: the same playbook serves external adversaries, compromised accounts and, through the pivot, insiders. Whether the removed data is regulated is what starts the notification clock, not who moved it.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an adversary — or a compromised or insider account — has staged and moved confidential data to external infrastructure under their control.
   * **Benign:** a sanctioned bulk transfer — backup, migration, partner exchange, content-delivery or analytics sync — or a volume anomaly misread as exfiltration.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Is the destination a sanctioned backup or partner endpoint, or a personal cloud account, an anonymous file-sharing service or an unknown rented server ([Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (Medium)` for a personal, anonymous or unknown destination; `Benign (Medium)` when the destination is a sanctioned endpoint on the organization's allowlist.
   * *Query 2:* Which objects moved — do the classification labels show regulated or confidential data, and does the storage-read volume correlate with the egress bytes observed? → `Malicious (High)` when regulated or confidential data is confirmed leaving; `Malicious (Medium)` when the read volume correlates with the egress but the objects carry no label; `Benign (Medium)` when the objects moved are public or carry no confidential classification.
   * *Query 3:* Does a preceding compromise exist on the source identity or host — malware, an anomalous sign-in, a new access key — or is this a clean, authorized principal acting alone ([Identity](../99-Shared/sub_enrichment_identity.md), [Asset](../99-Shared/sub_enrichment_asset.md))? → `Malicious (Medium)` on a preceding compromise; context when the principal is clean and authorized — with the re-classification trigger below once the transfer proves unauthorized.
   * *Query 4:* Were archives created shortly before the egress, and is the outbound stream encrypted or high-entropy in a way inconsistent with the sanctioned transfer method? → `Malicious (Medium)` on staging or an inconsistent stream; `Benign (Low)` when the transfer uses the sanctioned tool and protocol without staging.
   * *Query 5:* Does an approved migration or transfer ticket, or a recorded workflow, cover this transfer — the data set, the destination and the time window? → `Benign (High)` on a match — the explanation of the alert; `Malicious (Low)` when the transfer claims a ticket that does not cover its destination, data set or time.

**Re-classification pivots:** the source principal is a clean, authorized insider acting alone → [IC-09 (Insider Threat & Privilege Misuse)](09-insider_threat.md); an extortion contact or a leak-site threat is received → [IC-03 (Ransomware & Digital Extortion)](03-ransomware.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-11 (Data Breach / Exfiltration)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Block the destination and the egress channel at the perimeter, the proxy and the DLP (reversed by removing the rules).
*   Suspend the sessions of the involved identity and disable it, and isolate the involved host when it is an end-user workstation (reversed by re-enabling and reconnecting). Isolating a production server or database from which the data is leaving — **requires approval**.
*   Revoke the storage credentials in use — the specific API keys, signed storage URLs and other live grants (reversed by issuing new ones). Revoking the grants of many principals at once, or the service identity a production application uses to reach the store — **requires approval**.

### Eradication
*   Close the access path: rotate the credentials involved and fix the misconfiguration or public exposure that allowed the transfer.
*   Preserve the staging artifacts (archives) and any attacker tooling on the source systems per [Detection & Analysis §3.3](../../03-Processes/02-detection_and_analysis.md#33-evidence-preservation--chain-of-custody), then quarantine them (reversed by releasing them). Deleting them — **requires approval**.

### Recovery
*   Scope the exposed data set precisely enough to support the notification decision; where regulated data (personal, health or payment-card data) is confirmed exfiltrated, the regulatory notification of [Detection & Analysis §3.2](../../03-Processes/02-detection_and_analysis.md#32-stakeholder--regulatory-notification) is triggered through its Critical-severity path, with Legal and the data-protection officer.
*   Restore hardened access controls on the source and destination paths.
*   Monitor for publication of the data on leak sites and in dark-web markets; an extortion contact re-classifies the Case to IC-03.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-11, the exposed data set is scoped and its classification — regulated or not — is recorded before closure, since it drives the notification clock.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 5 executed, or with Query 2 unanswered.
*   Regulated data confirmed exfiltrated and the Case closed, or the response continued, without the §3.2 regulatory notification triggered through the Critical-severity path.
*   Isolating a production server or database, a mass revocation, or deleting data applied without approval.
*   The exposed data set scoped so imprecisely that a notification decision is made without it.
*   Closure leaving a confirmed foothold: the credential, misconfiguration or public exposure that allowed the transfer still open.
*   An extortion contact received, or a clean insider principal confirmed, and the Case not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep the egress logs for the same destination, hosting network or protocol from every other host and identity in the last 30 days.
*   Sweep the storage audit logs for bulk reads by principals that never read those stores before, and for archives created in staging paths shortly before outbound transfers.

## References

*   MITRE ATT&CK: T1048, T1567, T1041, T1530, T1074, T1560, T1020; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Network enrichment](../99-Shared/sub_enrichment_network.md).
