---
title: NN-<Incident Category Name> Investigation & Response
type: playbook
last_updated: 2026-11-13
license: Apache-2.0
incident_category: IC-NN
mitre_ttps:
  - TXXXX   # <technique name>
default_severity: Medium
required_data_sources:
  - <telemetry source>
status: draft
---

# NN-<Incident Category Name> Investigation & Response

> **Draft.** This template has not been verified in detail. Treat it as a proposal open to review rather than as a settled structure, and expect it to change.

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-NN <name>`. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage observations, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** <the adversary narrative this category represents>
   * **Benign:** <the authorized or mistaken activity that produces the same alerts>
2. **Validation queries** — each stated as a question; the executor translates it to its query language. Each query names what its outcomes are evidence of, in the tags of [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence); at least one query yields the `Benign (High)` observation that explains the alerts when the Benign hypothesis is true.
   * *Query 1:* <question> → `Malicious (High)` if <result>; `Benign (Low)` if <result>.
   * *Query 2:* <question> → `Benign (High)` if <result — the explanation of the alerts>; `Malicious (Medium)` if <result>.
   * *Query 3:* <question> → `Malicious (Medium)` if <result>; context otherwise.

**Re-classification pivots:** <adjacent categories this investigation commonly re-classifies to, per [Detection & Analysis §2.2](../../03-Processes/02-detection_and_analysis.md)>.

## Incident Response

Once the Malicious hypothesis is proven and the activity reached the environment ([Detection & Analysis §2.5](../../03-Processes/02-detection_and_analysis.md#25-incident-confirmation)), the Case is an `IC-NN` Incident. Containment actions are applied under the autonomy matrix of Incident Response §2.1, which decides from the Case's confidence, the Incident's Impact and the action's own impact whether each requires approval; an eradication or recovery action marked **requires approval** destroys what the organization holds, or resets credentials beyond the confirmed scope.

### Containment
*   <containment action; where its class is not plain, what decides its impact: what depends on the entity, what runs over the connection>

### Eradication
*   <remove what the threat actor added; close the entry point; rotate the credentials confirmed compromised>
*   <action that destroys what the organization holds: purge, wipe, re-image> — **requires approval**.

### Recovery
*   <verify eradication; restore; lift containment>

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced, and the phase transition contract (or the closure verdict) is emitted<; plus category-specific conditions>.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   <a verdict or response outcome that voids the run regardless of any other quality>

## Hunting Pivots

*   <one to three hunt hypotheses linking this category to a fleet-wide sweep, per [Threat Hunting](../../03-Processes/02-detection_and_analysis.md#4-threat-hunting)>

## References

*   <technique references; related playbooks; source standards>
