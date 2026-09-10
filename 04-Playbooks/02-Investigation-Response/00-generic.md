---
title: 00-Generic Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: ANY
mitre_ttps: ANY
default_severity: Medium
required_data_sources:
  - Depends on the triggering alert (endpoint, identity, network, cloud, email, data, application, or OT/ICS telemetry)
status: draft
---

# 00-Generic Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category maps to no specialized playbook (catch-all, `incident_category: ANY`) — activity that is suspicious but has not yet clustered into one of the [Incident Categories](../../02-Taxonomy/incident_categories.md). Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

The catch-all has two jobs: resolve the Case, and recognize as early as possible the category the evidence is trending toward, so that the specialized playbook takes over with the evidence carried forward. Its queries are the ones that apply to any category; the executor adds the category-specific ones the Case calls for.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** given this telemetry, the actor is malicious — the worst-case tactics and techniques the activity is consistent with, and the Incident Category (foothold or objective) it is trending toward.
   * **Benign:** a business operation, a misconfiguration, or an authorized test legitimately generated this telemetry.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Does the SOC Knowledge Base, the change calendar or the test schedule record an approved change window, vulnerability scan, sanctioned test or authorized automation covering the exact entities, action and time? → `Benign (High)` when the record covers the entity, the action and the time — the explanation of the alerts; `Benign (Medium)` when a window or automation exists but does not cover every alerted entity or action; `Malicious (Low)` when the activity presents itself as a change or a test and no record exists.
   * *Query 2:* Is the activity a known recurrence for these entities — the same process, source, schedule and parameters seen in their history before the alert window ([Asset](../99-Shared/sub_enrichment_asset.md), [Identity](../99-Shared/sub_enrichment_identity.md))? → `Benign (Medium)` when the same parameters recur with no incident behind the earlier occurrences; `Malicious (Medium)` when the activity is first-seen for the entity, or its parameters changed with the alert.
   * *Query 3:* What is the reputation of the external indicators in scope — file hash, source and destination IP addresses, domains ([Artifact](../99-Shared/sub_enrichment_artifact.md), [Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (High)` when an indicator is known command-and-control or a known malware family; `Malicious (Medium)` when it is newly registered or flagged by a single source; `Benign (Low)` when every indicator is clean with an established, widely seen reputation — a clean lookup is evidence, not silence.
   * *Query 4:* Are there signs of lateral movement, evasion tooling, or privilege escalation from the entities in scope in the surrounding window? → `Malicious (Medium)` when any is present; `Benign (Low)` when the entities show nothing beyond the alerted activity in the window before and after it.
   * *Query 5:* Do the observed techniques cluster into a specific Incident Category — a foothold (a person, an endpoint, an identity, an application, infrastructure, a supplier) or an objective (fraud, extortion, denial of service, exfiltration, resource theft, destruction)? → `Malicious (High)` when they cluster into a recognizable category — and the re-classification trigger below; context when they do not — an isolated technique is not less suspicious for lacking a category.

**Re-classification pivots:** the category the evidence clusters into, per the shape and precedence of the [Incident Categories](../../02-Taxonomy/incident_categories.md): a payload executed → [IC-05 (Commodity Malware / Loader)](05-commodity_malware.md); an identity taken over → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md); a server, network device or domain controller used as a foothold or pivot → [IC-08 (Infrastructure Compromise)](08-infrastructure_compromise.md); bulk data leaving the organization → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md); and any other category as its objective becomes visible. Where no specialized playbook exists for the category the evidence establishes, the Investigation Note records the novel category and this playbook continues.

## Incident Response

Once the Malicious hypothesis is proven, the Case is an Incident of the category the evidence established; where a specialized playbook exists, re-classify and apply its actions. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Determine the blast radius — every entity the confirmed activity touched — then apply the least-disruptive isolating control on the confirmed entities: revoke the sessions and tokens of the identities involved (reversed by signing in again), isolate the affected workstations (reversed by reconnecting them), block the external IP addresses and domains at the perimeter (reversed by removing the rules).
*   Isolating a production server, a database, a domain controller or any other Crown Jewel, or an entire subnet, VLAN or cloud network — **requires approval**.
*   Disabling an identity a critical service runs under, or blocklisting a partner or customer network — **requires approval**.

### Eradication
*   Identify all malicious artifacts — files, scheduled tasks, registry keys, services, backdoors, added credentials, grants or rules — from the Case timeline, remove them, and patch or close the initial vector.
*   Rotate the credentials of the identities confirmed compromised and of the secrets they could reach. A reset broader than the confirmed scope — **requires approval**.
*   Wiping or re-imaging an affected system — **requires approval**.

### Recovery
*   Verify the integrity of the affected systems, restore services to normal operation, and lift containment gradually only after eradication is confirmed complete and the monitoring window of [Incident Response §4](../../03-Processes/03-response.md#4-recovery) shows no indicator of compromise.
*   Feed the technique and indicators to Phase 1 as a detection-tuning signal; where the category was novel, record it for the taxonomy.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for the catch-all, every query added beyond the listed ones is recorded with its tag, and where the techniques cluster into a specialized Incident Category, the Note records the re-classification target and the evidence that triggered it.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 1 executed, or with Query 3 unanswered for any external indicator in scope.
*   Techniques that cluster into a category with a specialized playbook not re-classified when the pivot applies.
*   Eradicating or remediating an affected system before its malicious artifacts and initial vector are identified and recorded.
*   Lifting containment before eradication is confirmed complete — closure leaving a confirmed foothold.
*   Isolation of a Crown Jewel or a network segment, a reset beyond the confirmed identities, or a wipe or re-image applied without approval.

## Hunting Pivots

*   Sweep the fleet for the same indicators — hash, destination, source, command line — on entities outside the Case scope: an unclassified technique seen once is often seen elsewhere.
*   Sweep the retention window for the same technique on the same entity class (the same alert type across all hosts or identities), to recover the earlier occurrences that never alerted.

## References

*   NIST SP 800-61 Rev. 3; MITRE ATT&CK; OCSF.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); the [shared enrichment sub-playbooks](../99-Shared/).
