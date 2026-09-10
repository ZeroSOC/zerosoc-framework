---
title: Case Schema
type: concept
status: draft
last_updated: 2026-09-10
license: Apache-2.0
---

# Case Schema

The **Case** is the object the operating loop works on: opened when Alerts are aggregated (Phase 2.a), promoted to an **Incident** when its verdict becomes True Positive (Phase 2.b), responded to (Phase 3) and reviewed (Phase 4). This document defines the Case once — the OCSF fields the framework uses and the fields the framework adds — so that processes, playbooks, deliverables and metrics refer to the same names. A formal [JSON Schema](case_schema.json) accompanies this document (§5). The [phase transition contracts](../04-Playbooks/playbook_architecture.md#5-phase-transition-contracts-ocsf-aligned) are subsets of this model.

## 1. Object Mapping

A Case maps to the OCSF [Incident Finding [2005]](https://schema.ocsf.io/1.8.0/classes/incident_finding) object; its Alerts are [Detection Finding [2004]](https://schema.ocsf.io/1.8.0/classes/detection_finding) objects referenced from it. Case and Incident are one object: the transition is `verdict_id` → True Positive (`2`) (see [Definitions — Security Cases](../01-Foundation/definitions.md#security-cases)). A platform that cannot carry one of the framework's own fields (§3) as an extension attribute records it in the Case's notes or ticket; the field still exists, and the Triage Note and Investigation Note always carry it.

## 2. OCSF Fields Used by the Framework

| Field | Values | Set in | Meaning in the framework |
|---|---|---|---|
| `uid` | string | 2.a | Case identifier, cited by the Notes, tuning tickets and metrics |
| `status_id` | 1 New · 2 In Progress · 3 On Hold · 4 Resolved · 5 Closed | 2.a → 4 | Workflow state; `In Progress` is set at acknowledgment (MTTA) |
| `severity_id` | 1 Informational · 2 Low · 3 Medium · 4 High · 5 Critical | 2.a, refined in 2.b | "How bad" — potential harm; drives urgency and internal notification |
| `confidence_id` | 1 Low · 2 Medium · 3 High | 2.a, resolved in 2.b | "How sure" — set by hypothesis resolution ([Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence)); capped by visibility gaps |
| `impact_id` | 1 Low · 2 Medium · 3 High · 4 Critical | 2.a when already known; 2.b at incident confirmation | Realized or expected harm; drives regulatory notification ([§3.1](../03-Processes/02-detection_and_analysis.md#31-incident-promotion)) |
| `verdict_id` | 0 Unknown · 1 False Positive · 2 True Positive · 5 Benign · 7 Insufficient Data · 10 Duplicate | 2.a / 2.b | Open (`0`) until resolved; `2` promotes the Case to an Incident; levels in [Definitions §3](../01-Foundation/definitions.md#3-case-dispositions-verdicts) |
| `assignee` | user | 2.a; changes at handover | The Case **owner**: the executor responsible for advancing it and for its verdict ([§2.3](../03-Processes/02-detection_and_analysis.md#23-case-ownership)) |
| `finding_info_list` | list of finding_info | 2.a; appended while open | The aggregated Alerts |
| `attacks` | list of MITRE ATT&CK objects | 2.a, refined in 2.b | Observed tactics and techniques, written `ID (Name)` |
| `observables` | list of observables | 2.a, extended in 2.b | Normalized [entities](../01-Foundation/definitions.md#entity) — the join keys of the investigation |
| `start_time` / `end_time` | timestamp | 2.a / close | Case lifetime; measurement anchors together with T0 |
| `is_suspected_breach` | boolean | 2.b | Set when data compromise is suspected; informs the significance test |

## 3. Framework Fields

| Field | Values | Set in | Meaning |
|---|---|---|---|
| `candidate_incident_categories` | list of `IC-##` | 2.a | Candidate categories proposed by the [alert types](alert_types.md) |
| `incident_category` | `IC-##` | 2.b | Confirmed category (provisional until `verdict_id = 2`) |
| `entry_path` | `alert` · `hunt` · `out-of-band` | 2.a | How the Case entered the loop; hunt and out-of-band Cases are detection false negatives by construction |
| `t0` | timestamp | 2.b | Earliest confirmed malicious event; anchor for MTTD / MTTC / MTTR |
| `timeline` | ordered entries with event references | 2.b → 3 | The Case Timeline of the Investigation Note, extended with response actions |
| `visibility_gaps` | list of required data sources unavailable | 2.a / 2.b | Caps confidence ([Playbook Architecture §7](../04-Playbooks/playbook_architecture.md#7-dynamic-agentic-execution)); counted by the Visibility-Gap Rate |
| `provenance` | playbooks used (path and version), executor classes, capability classes | every phase | Glass Box audit trail |
| `significant` | boolean | 2.b | NIS2 Article 23(3) significance test: severe operational disruption or financial loss, or considerable damage to other persons |
| `cross_border` | boolean | 2.b | Cross-border effect, required in the NIS2 early warning |
| `notifications` | list of {recipient, deadline, sent_at} | 3 | Stakeholder and regulatory notifications and their deadlines |
| `tuning_ticket` | reference | 2.a / 2.b, on a False Positive close | The Phase 1 ticket that closes the tuning loop |
| `handover_reason` | `crown-jewel` · `privileged-identity` · `manual` | any | Why ownership moved to a human |
| `watch_until` | timestamp | 2.a / 2.b close | Monitoring watch on the Case's entities after an Insufficient Data or Low-confidence close |
| `master_case_uid` | Case `uid` | 2.a / 2.b, on a Duplicate close | The open master Case that handles the activity |

## 4. Where the Fields Are Populated

*   **Phase 2.a Triage** ([Detection & Analysis §1](../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization)): aggregation, status and owner (§1.1); observables and techniques (§1.2–1.3); severity and confidence (§1.4); verdict on close, candidate categories, visibility gaps and provenance (§1.5–1.6).
*   **Phase 2.b Investigation** ([§2](../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation)): confidence and verdict (§2.4); timeline and T0 (§2.5); confirmed category, impact, significance and cross-border effect (§3.1); handover reason (§2.3).
*   **Phase 3 Incident Response** ([03-response.md](../03-Processes/03-response.md)): notifications; containment actions appended to the timeline.
*   **Phase 4 Post-Incident Activity** ([04-post_incident_activity.md](../03-Processes/04-post_incident_activity.md)): review outcomes reference the Case by `uid`.

## 5. JSON Schema

[`case_schema.json`](case_schema.json) is the formal, machine-readable version of this document (JSON Schema 2020-12). It declares the OCSF Incident Finding fields of §2 with their enum values, and the framework fields of §3 under a single `zerosoc` extension object, following OCSF's extension convention of adding attributes rather than redefining classes. Where a framework field has a natural OCSF type it reuses it: timeline entries carry OCSF `finding_info` and `related_event` objects, provenance carries OCSF `product` objects, the tuning ticket is an OCSF `ticket`. Object shapes borrowed from OCSF are marked `x-ocsf-object` and are intentionally open (`additionalProperties: true`) so that a platform's full OCSF object validates unchanged.
