---
title: 09-Insider Threat & Privilege Misuse Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-09
mitre_ttps:
  - T1078        # Valid Accounts
  - T1074         # Data Staged
  - T1560         # Archive Collected Data
  - T1567         # Exfiltration Over Web Service
  - T1052.001     # Exfiltration Over Physical Medium: Exfiltration over USB
  - T1531         # Account Access Removal
default_severity: Medium
required_data_sources:
  - DLP / file-access audit logs
  - Identity Provider / directory audit logs
  - CASB
  - Endpoint telemetry
  - HR context (joiner-mover-leaver)
status: draft
---

# 09-Insider Threat & Privilege Misuse Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-09 Insider Threat & Privilege Misuse` — an authorized user abusing access, whether malicious, negligent or a compromised insider. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

The actor here is *authorized*: technical evidence alone rarely resolves intent, and the investigation is legally sensitive from the first query. Evidence handling meets the chain-of-custody standard of [Detection & Analysis §3.3](../../03-Processes/02-detection_and_analysis.md#33-evidence-preservation--chain-of-custody) from the outset, not only after an Incident is declared, and every action visible to the subject is sequenced with HR and Legal, who own interviews, suspension and the use of evidence under employee-privacy, works-council and data-protection constraints.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an authorized user is deliberately collecting or exfiltrating data, or abusing privileges beyond their job function — a malicious or departing insider.
   * **Benign:** a legitimate bulk business task (migration, backup, e-discovery) or role-appropriate access that tripped a volume threshold.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Does the accessed data map to the user's role, department and current projects ([Identity](../99-Shared/sub_enrichment_identity.md))? → `Benign (Medium)` when it fits; `Malicious (Medium)` when the data belongs to a function the user has no business reason to touch.
   * *Query 2:* Does the access volume, time-of-day pattern or repository deviate from the user's own baseline and from their peer group's? → `Malicious (Medium)` on a deviation from both; `Benign (Low)` when the activity sits within both baselines.
   * *Query 3:* Is there HR risk context — a resignation notice, an active performance process, or imminent offboarding? → `Malicious (Low)` when present — sensitive context, corroborating only, never sufficient alone; context when absent.
   * *Query 4:* Is the sensitive-data access followed by an upload to a personal cloud account, a write to removable media, or a send to a personal email address (DLP, CASB, endpoint telemetry)? → `Malicious (High)` on any of these; `Benign (Medium)` when the data went only to sanctioned repositories and recipients.
   * *Query 5:* Is there concealment behavior — renamed or encrypted archives, log deletion, off-hours staging? → `Malicious (High)` on any of these; `Benign (Low)` when the data was handled in the open, under its original names, in working hours.
   * *Query 6:* Does an approved business task cover the access — a migration, backup, e-discovery or audit request, a ticket or a manager's attestation naming the data set and the time window? → `Benign (High)` on a match — the explanation of the alert; `Malicious (Medium)` when the user cites a task the record does not support.
   * *Query 7:* Is the account acting from the user's usual device and location, with no sign-in anomaly, so that the actor is the person and not a stolen session? → `Malicious (Medium)` when sign-in anomalies show the account, not the employee, is acting — and the re-classification trigger below; context when the sessions are the user's own.

**Re-classification pivots:** the account, not the employee, is acting → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md); confirmed large-scale data theft → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-09 (Insider Threat & Privilege Misuse)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Snapshot and preserve the evidence per [Detection & Analysis §3.3](../../03-Processes/02-detection_and_analysis.md#33-evidence-preservation--chain-of-custody) before any action visible to the subject; where the subject holds administrative access, preserve first the logs and audit trails the subject could alter.
*   Quietly restrict the specific access paths and egress channels involved — block the personal-cloud destination, disable writes to removable media, hold outbound mail to the personal address (reversed by removing the rules); prefer controls the subject does not see.
*   Suspending the subject's sessions or disabling the identity is reversible and stops no service, but it is visible to the subject: apply it when data is leaving at that moment; otherwise sequence it with HR and Legal. Disabling a service identity the subject administers and a critical service runs under — **requires approval**.

### Eradication
*   Eradication here is actor-centric, not artifact-centric: access revocation, device recovery and every employee-facing action — interview, suspension, notification — are executed per HR and Legal direction; the executor supplies the evidence record and does not initiate them.
*   Recover the exfiltrated data where possible — deletion from the personal cloud account, retrieval of removable media — through HR and Legal.

### Recovery
*   Conduct an entitlement review of the affected data stores.
*   Tune the DLP rules against the concealment and egress pattern observed, as a [Phase 1](../../03-Processes/01-preparation_and_engineering.md) signal.
*   Fix the underlying process — entitlement, joiner-mover-leaver, offboarding — that allowed the privilege misuse.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-09, chain-of-custody evidence handling is confirmed from the first query onward, and every employee-facing action is recorded with the HR and Legal direction it was taken under.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   Any employee-facing action — interview, suspension, visible access change — taken without HR and Legal direction.
*   A record naming the employee as a malicious insider before the Malicious hypothesis is proven, or produced outside HR and Legal direction.
*   The Malicious hypothesis resolved on HR context (Query 3) without a converging query.
*   A Benign close without Query 6 executed, or with Query 4 unanswered.
*   Evidence gathered without the §3.3 chain-of-custody standard before a subject-visible action.
*   Sign-in anomalies or large-scale data theft confirmed and the Case not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep for the same egress channel — the personal-cloud service, removable-media writes, sends to personal addresses — following sensitive-data access, across the department and its peer groups.
*   Sweep the sensitive repositories touched for reads by users outside their owning role in the last 30 days.

## References

*   MITRE ATT&CK: T1078, T1074, T1560, T1567, T1052.001, T1531; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Identity enrichment](../99-Shared/sub_enrichment_identity.md).
