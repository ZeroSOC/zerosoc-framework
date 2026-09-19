---
title: Case Schema
type: concept
status: draft
last_updated: 2026-09-20
license: Apache-2.0
---

# Case Schema

The **Case** is the object the operating loop works on: opened when Alerts are aggregated (Phase 2.a), promoted to an **Incident** when its verdict becomes True Positive (Phase 2.b), responded to (Phase 3) and reviewed (Phase 4). This document defines the Case once — the OCSF fields the framework uses and the fields the framework adds — so that processes, playbooks, deliverables and metrics refer to the same names. A formal [JSON Schema](case_schema.json) accompanies this document (§7).

## 1. Object Mapping

A Case maps to the OCSF [Incident Finding [2005]](https://schema.ocsf.io/1.9.0/classes/incident_finding) object; the Alerts it aggregates are [Detection Finding [2004]](https://schema.ocsf.io/1.9.0/classes/detection_finding) objects it references. Case and Incident are one object: the transition is `verdict_id` → True Positive (`2`) (see [Definitions — Security Cases](../01-Foundation/definitions.md#security-cases)).

**One object crosses every phase.** A phase does not copy the Case forward and does not carry a subset of it: the [phase transition contracts](../04-Playbooks/playbook_architecture.md#5-phase-transition-contracts) state which of these fields MUST be populated at each boundary, and nothing more. Values are refined as the Case advances; the object is the same one throughout.

**The Notes render the Case.** The Triage Note and the Investigation Note are readable renderings of this object at their gate, held in `notes` (§2). They hold no state of their own, so whatever a platform cannot carry here is not recoverable from them either. Prose that has no structured form — the Summary, the rationale, the root cause and how confident the executor is of it — is the exception, and lives in the rendering.

**Where OCSF carries a concept, the framework maps to it** and adds no field of its own. The fields in §4 are the concepts looked for in the current OCSF release and not found, or found in a form that loses what the framework needs.

## 2. OCSF Fields Used by the Framework

| Field | Values | Set in | Meaning in the framework |
|---|---|---|---|
| `uid` | string | 2.a | Case identifier, cited by the Notes, tuning tickets and metrics |
| `status_id` | 1 New · 2 In Progress · 3 On Hold · 4 Resolved · 5 Closed | 2.a → 4 | Workflow state; `In Progress` is set at acknowledgment |
| `severity_id` | 1 Informational · 2 Low · 3 Medium · 4 High · 5 Critical | 2.a, refined in 2.b | "How bad" — potential harm; drives urgency and internal notification |
| `confidence_id` | 1 Low · 2 Medium · 3 High | 2.a, resolved in 2.b | "How sure" — set by hypothesis resolution ([Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence)). A source's own `confidence_id` and `likelihood_id` are inputs triage validates, never accepted at face value |
| `impact_id` | 1 Low · 2 Medium · 3 High · 4 Critical | 2.a when already known; 2.b at incident confirmation | Realized or expected harm; drives regulatory notification ([§3.1](../03-Processes/02-detection_and_analysis.md#31-incident-promotion)) |
| `verdict_id` | 0 Unknown · 1 False Positive · 2 True Positive · 5 Benign · 7 Insufficient Data · 10 Duplicate | 2.a / 2.b | Open (`0`) until resolved; `2` promotes the Case to an Incident; levels in [Definitions §3](../01-Foundation/definitions.md#3-case-dispositions-verdicts) |
| `assignee` | user | 2.a; changes at handover | The Case **assignee**: the executor responsible for advancing it and for its verdict ([§2.3](../03-Processes/02-detection_and_analysis.md#23-case-assignment)) |
| `desc` | string | 2.a; refreshed at each gate and while the response runs | The Case **Summary**: what happened and when, the entities involved and which acted on which, and — once established — the root cause, with the Findings that establish it |
| `notes` | list of note | 2.a / 2.b | The Triage Note and the Investigation Note, one `note` each: `title` the deliverable name, `comment` the rendering, `owner` the executor, `created_time` and `modified_time` its anchors |
| `finding_info_list` | list of finding_info | 2.a; appended while open | Every **Finding** of the Case: the Alerts first, then the result of every check and validation query (§3) |
| `attacks` | list of MITRE ATT&CK objects | 2.a, refined in 2.b | Observed tactics and techniques, written `ID (Name)` |
| `observables` | list of observables | 2.a, extended in 2.b | Normalized [entities](../01-Foundation/definitions.md#entity) — the join keys of the investigation |
| `start_time` / `end_time` | timestamp | 2.a, refined in 2.b | The earliest and the most recent event or finding that **contributed to** the Case. **`start_time` is required**: a Case always has an Alert, so from the moment it opens it has a time it began at. It opens at the earliest Alert's own `start_time` and only ever moves **earlier**, whenever a Malicious Finding cites evidence of an earlier event (§3) — never later, and never to a time of the investigation rather than of the attack. A benign precursor examined and ruled out contributed to the investigation and not to the Case, and never moves it. On a confirmed Incident `start_time` is the earliest confirmed malicious event — what the framework calls **T0**, the anchor of the speed metrics ([Operational Metrics §4](../05-Metrics/operational_metrics.md)). On a Case closed as a False Positive or a Benign Positive it is still the earliest Alert's own start and nothing more: nothing malicious was confirmed, so it is **not T0** and anchors no metric. `end_time` is set where the Case's span is known |
| `vendor_attributes` | the source's `severity` and `severity_id` | 2.a, when triage overrides them | What the source reported before triage assessed it ([§1.4](../03-Processes/02-detection_and_analysis.md#14-case-classification-severity-confidence--impact)); the override is auditable and countable |
| `is_suspected_breach` | boolean | 2.b | Set when data compromise is suspected; informs the significance test |
| `tickets` | list of ticket | 2.a / 2.b, on a False Positive close | Tickets the Case raised; the Phase 1 tuning ticket carries `type` `tuning` |

## 3. Findings

`finding_info_list` holds one `finding_info` object for every entry in the Case's record: each **Finding** — an Alert, the result of a triage check, the result of a validation query — and each **response action** taken on the Case (§5). One object per entry, so that one set of tags belongs to exactly one of them.

| Attribute | Carries |
|---|---|
| `title`, `desc` | The Finding, or the action taken, stated in accurate terms |
| `first_seen_time` | When the thing it reports was observed, which is not when the Finding was made. The Case Timeline orders on this, and `start_time` is the earliest of them |
| `analytic` | What produced the Finding — the question, what was asked, and the query the tool ran — below |
| `types` | `alert` for an aggregated Alert, `finding` for the result of a check or query, `action` for a response action |
| `tags` | The side and the confidence, and whether the timeline renders it — below |
| `related_events` | The **evidence**: the events the Finding rests on, cited rather than copied — below |
| `attack_graph` | Which entity acted on which, below |

**What produced it.** A Finding and what produced it are never separated, and `analytic` carries all three parts of that:

- `name` — the question the check or the query answers, in the words a reader of the Case understands.
- `desc` — what was asked, as the executor asked it: the telemetry, the entities and the window, before any tool translated it.
- `algorithm` — the query the tool actually ran, in that tool's own language.

`name` is what makes the Finding legible and `algorithm` is what makes it reproducible: a reader holding neither the Case's executor nor its tool bindings can re-run the query and see what it saw. An executor that records only the question has recorded an assertion, not evidence.

OCSF requires `type_id` on the object. A triage check and a validation query are none of the types OCSF lists — they are not detection content that fires on its own — so they take Other (99) and `type` names the kind: `triage check`, `validation query`, `enrichment`. An Alert keeps whatever analytic its source reported.

**Side and confidence.** Two tags, with the values of [Definitions §7](../01-Foundation/definitions.md#7-classification-levels):

- `zerosoc:side` — `Malicious` or `Benign`
- `zerosoc:confidence_id` — `1`, `2` or `3`

A Finding that bears on no hypothesis carries **neither tag**: absence is how context is expressed, and context carries no weight in hypothesis resolution. An `action` entry carries neither either, since an action is not evidence for a hypothesis.

**The timeline.** A third tag, `zerosoc:timeline`, marks the entries the Case Timeline renders (§5). The timeline is a reconstruction and not a listing: an entry is flagged because it belongs to the account of what happened, and most Findings do not.

All three tags are declared and validated in the [JSON Schema](case_schema.json); OCSF does not constrain tag names or values, so nothing upstream validates them.

**Evidence.** A Finding's evidence is its `related_events`: the events it rests on, each cited by identifier and never copied in. This is the one place evidence is held — there is no second list beside the Findings, and a raw log is never a Finding's body.

An event OCSF carries is cited by its `uid` and its class `type_uid`, and OCSF's classes are not only Alerts and Cases: a Detection Finding where the Finding is an Alert, a Remediation Activity on an `action` entry, the events of the telemetry a validation query returned. An event OCSF does not carry is named by `type` instead, which `related_event` exists to allow.

Each reference carries **when the event happened** — `first_seen_time` — not when the Finding was made. That is what lets the Case's `start_time` move: it is the earliest such time across the Case's Malicious Findings, so an adversary reaching back before the detection that caught them moves it, and a benign precursor does not.

**Directionality.** `attack_graph` SHOULD be populated where the executor can establish which entity acted on which. It is a directed graph (`is_directed` `true`) over the Case's entities, and it borrows its vocabulary rather than inventing one:

- `node.uid` is the entity's value as it appears in `observables`, and `node.type` is that observable's OCSF `type_id` — a node is an [Entity](../01-Foundation/definitions.md#entity), not a parallel concept.
- `edge.source` is the acting entity and `edge.target` the entity acted on.
- `edge.relation` is the ATT&CK technique identifier where the edge is an observed technique, and otherwise a STIX 2.1 relationship type.
- `edge.data` cites the events grounding the edge, on the same terms as a Finding.

OCSF constrains none of this and no published convention exists, so an implementation that populates the graph is stating one; the framework states this one so that two implementations agree.

## 4. Framework Fields

Concepts with no home in the current OCSF release. Each is declared under a single `zerosoc` extension object and validated in the [JSON Schema](case_schema.json).

| Field | Values | Set in | Meaning |
|---|---|---|---|
| `candidate_incident_categories` | list of `IC-##` | 2.a | Candidate categories proposed by the [alert types](alert_types.md) |
| `incident_category` | `IC-##` | 2.b | Confirmed category (provisional until `verdict_id = 2`) |
| `reclassification_pivots` | list of {from, to, reason, event_refs} | 2.b | Every change of candidate category, with the evidence that triggered it. OCSF records the new state of a finding but never what it was before, so a Case's classification history has no native form |
| `entry_path` | `alert` · `hunt` · `out-of-band` | 2.a | How the Case entered the loop; hunt and out-of-band Cases are detection false negatives by construction |
| `visibility_gaps` | list of required data sources unavailable | 2.a / 2.b | Recorded with the check each prevented ([Playbook Architecture §7](../04-Playbooks/playbook_architecture.md#7-execution)); counted by the Visibility-Gap Rate |
| `provenance` | playbooks used (path and version), executor classes, capability classes | every phase | Glass Box audit trail |
| `significant` | boolean | 2.b | NIS2 Article 23(3) significance test: severe operational disruption or financial loss, or considerable damage to other persons |
| `cross_border` | boolean | 2.b | Cross-border effect, required in the NIS2 early warning |
| `notifications` | list of {recipient, deadline, sent_at} | 3 | Stakeholder and regulatory notifications and their deadlines |
| `handover_reason` | `crown-jewel` · `privileged-identity` · `manual` | any | Why the assignee became a human |
| `watch_until` | timestamp | 2.a / 2.b close | Monitoring watch on the Case's entities after an Insufficient Data or Low-confidence close |
| `master_case_uid` | Case `uid` | 2.a / 2.b, on a Duplicate close | The open master Case that handles the activity |

## 5. Events the Case References

The Case is the current state; what happened to it is a sequence of events it references, never an array it stores.

*   **Response actions** — a containment, eradication or recovery action is its own entry in `finding_info_list`, typed `action`, carrying the OCSF [Remediation Activity](https://schema.ocsf.io/1.9.0/classes/remediation_activity) event in its `related_events` by that event's `uid` and its class `type_uid`. An action is recorded against the Case and not against the Finding that prompted it: the reasoning may be retracted, and the action still happened. A tool-initiated action that fires before any executor opens the Case is an entry like any other, so that triage sees what has already been done. OCSF holds no reference in the other direction.
*   **Lifecycle** — acknowledgment, promotion, handover and closure are `activity_id` Create, Update and Close events on the Case. They are not stored in the object.
*   **The Case Timeline** is the entries tagged `zerosoc:timeline`, in `first_seen_time` order — when the thing happened, rather than when it was recorded. It is a reconstruction of the Case, not a listing of it.

## 6. Where the Fields Are Populated

*   **Phase 2.a Triage** ([Detection & Analysis §1](../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization)): aggregation, status and assignee (§1.1); observables and techniques (§1.2–1.3); severity and confidence (§1.4); Findings, verdict on close, candidate categories, visibility gaps and provenance (§1.5–1.6).
*   **Phase 2.b Investigation** ([§2](../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation)): Findings from the validation queries, confidence and verdict (§2.4); confirmed category, impact, significance and cross-border effect (§3.1); handover reason (§2.3).
*   **Phase 3 Incident Response** ([03-response.md](../03-Processes/03-response.md)): notifications; Remediation Activity events referenced from the Findings that motivated them.
*   **Phase 4 Post-Incident Activity** ([04-post_incident_activity.md](../03-Processes/04-post_incident_activity.md)): review outcomes reference the Case by `uid`.

## 7. JSON Schema

[`case_schema.json`](case_schema.json) is the formal, machine-readable version of this document (JSON Schema 2020-12). It declares the OCSF Incident Finding fields of §2 with their enum values, the Finding mapping of §3 including the tag names the framework reserves, and the framework fields of §4 under a single `zerosoc` extension object, following OCSF's extension convention of adding attributes rather than redefining classes. Where a framework field has a natural OCSF type it reuses it: provenance carries OCSF `product` objects, a ticket is an OCSF `ticket`. Object shapes borrowed from OCSF are marked `x-ocsf-object` and are intentionally open (`additionalProperties: true`) so that a platform's full OCSF object validates unchanged.
