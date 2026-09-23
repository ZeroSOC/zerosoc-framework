---
title: Case Schema
type: concept
status: draft
last_updated: 2026-09-24
license: Apache-2.0
---

# Case Schema

The **Case** is the object the operating loop works on: opened when Alerts are aggregated (Phase 2.a), promoted to an **Incident** when its verdict becomes True Positive (Phase 2.b), responded to (Phase 3) and reviewed (Phase 4). This document defines the Case once — the OCSF fields the framework uses and the fields the framework adds — so that processes, playbooks, deliverables and metrics refer to the same names. A formal [JSON Schema](case_schema.json) accompanies this document (§7).

The release this mapping follows is declared on the schema itself, as `ocsf_version`: a consumer handed a Case out of band — written into another system's record, exported, archived — reads which OCSF release it was written against without being told.

## 1. Object Mapping

A Case maps to the OCSF [Incident Finding [2005]](https://schema.ocsf.io/1.9.0/classes/incident_finding) object; the Alerts it aggregates are [Detection Finding [2004]](https://schema.ocsf.io/1.9.0/classes/detection_finding) objects it references. Case and Incident are one object: the transition is `verdict_id` → True Positive (`2`) (see [Definitions — Security Cases](../01-Foundation/definitions.md#security-cases)).

**One object crosses every phase.** A phase does not copy the Case forward and does not carry a subset of it: the [phase transition contracts](../04-Playbooks/playbook_architecture.md#5-phase-transition-contracts) state which of these fields MUST be populated at each boundary, and nothing more. Values are refined as the Case advances; the object is the same one throughout.

**The Notes render the Case.** The Triage Note and the Investigation Note are readable renderings of this object at their gate, held in `notes` (§2). They are a field of the Case and not a record beside it: a fact that has a field of its own is recorded in the field, and a Note is never the only place it is kept. Prose that has no structured form — the Summary, the rationale, the root cause and how confident the executor is of it — lives in the rendering, and is on the Case because the rendering is.

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
| `desc` | string | 2.a; refreshed at each gate and while the response runs | The Case **Summary**: what happened and when, the entities involved and which acted on which, and — once established — the root cause, with the Observations that establish it |
| `notes` | list of note | 2.a / 2.b | The Triage Note and the Investigation Note, one `note` each: `title` the deliverable name, `comment` the rendering, `owner` the executor, `created_time` and `modified_time` its anchors |
| `finding_info_list` | list of finding_info | 2.a; appended while open | Every **Observation** of the Case: the Alerts first, then the result of every check and validation query (§3) |
| `attacks` | list of MITRE ATT&CK objects | 2.a, refined in 2.b | Observed tactics and techniques, written `ID (Name)` |
| `observables` | list of observables | 2.a, extended in 2.b | Normalized [entities](../01-Foundation/definitions.md#entity) — the join keys of the investigation |
| `start_time` / `end_time` | timestamp | 2.a, refined in 2.b | The earliest and the most recent event or observation that **contributed to** the Case. **`start_time` is required**: a Case always has an Alert, so from the moment it opens it has a time it began at. It opens at the earliest Alert's own `start_time` and only ever moves **earlier**, whenever a Malicious Observation cites evidence of an earlier event (§3) — never later, and never to a time of the investigation rather than of the attack. A benign precursor examined and ruled out contributed to the investigation and not to the Case, and never moves it. On a confirmed Incident `start_time` is the earliest confirmed malicious event — what the framework calls **T0**, the anchor of the speed metrics ([Operational Metrics §4](../05-Metrics/operational_metrics.md)). On a Case closed as a False Positive or a Benign Positive it is still the earliest Alert's own start and nothing more: nothing malicious was confirmed, so it is **not T0** and anchors no metric. `end_time` is set where the Case's span is known |
| `vendor_attributes` | the source's `severity` and `severity_id` | 2.a, when triage overrides them | What the source reported before triage assessed it ([§1.4](../03-Processes/02-detection_and_analysis.md#14-case-classification-severity-confidence--impact)); the override is auditable and countable |
| `is_suspected_breach` | boolean | 2.b | Set when data compromise is suspected; informs the significance test |
| `tickets` | list of ticket | 2.a / 2.b | Tickets the Case **raised**, which is not a ticket it consulted: a change ticket an enrichment check read is evidence, and belongs to the Observation that cites it. OCSF's `type_id` says which system holds the ticket — **Internal** (`1`) or **External** (`2`) — and not what it is for, which is `zerosoc.kind`: `tuning`, `visibility`, `containment`, `eradication`, `recovery`. The set is open while the response phase is still being designed |

**`start_time` rests on a reading OCSF does not spell out.** Release 1.9.0 reworded the field across every Observations class, from *"the least recent event **included in** the incident"* to *"the earliest event or observation that **contributed to** this incident"*. The framework reads "contributed to" as **causal**, which is what makes the field adversary-dependent: widening a Case with context does not move it, and an event examined and ruled out never moves it. OCSF does not say which reading it intends. Under the older, aggregative reading the field would be the earliest contributing event of any kind, so two conformant producers could emit different times for the same Case and a consumer comparing detection latency across them would mix them without noticing. The question is open upstream; an adopter should know which reading this framework assumes.

## 3. Observations

`finding_info_list` holds one `finding_info` object for every entry in the Case's record: each **Observation** — an Alert, the result of a triage check, the result of a validation query — and each **response action** taken on the Case (§5). One object per entry, so that one set of tags belongs to exactly one of them.

| Attribute | Carries |
|---|---|
| `title`, `desc` | The Observation, or the action taken, stated in accurate terms |
| `first_seen_time` | When the thing it reports was observed, which is not when the Observation was made. The Case Timeline orders on this, and `start_time` is the earliest of them |
| `analytic` | What produced the Observation — the question, what was asked, and the query the tool ran — below |
| `types` | `alert` for an aggregated Alert, `observation` for the result of a check or query, `action` for a response action |
| `zerosoc` | The side and the confidence, and whether the timeline renders it — below |
| `related_events` | The **evidence**: the events the Observation rests on — below |
| `attack_graph` | Which entity acted on which, below |

**What produced it.** An Observation and what produced it are never separated, and `analytic` carries all three parts of that:

- `name` — the question the check or the query answers, in the words a reader of the Case understands.
- `desc` — what was asked, as the executor asked it: the telemetry, the entities and the window, before any tool translated it.
- `algorithm` — the query the tool actually ran, in that tool's own language.

`name` is what makes the Observation legible and `algorithm` is what makes it reproducible: a reader holding neither the Case's executor nor its tool bindings can re-run the query and see what it saw. An executor that records only the question has recorded an assertion, not evidence.

OCSF requires `type_id` on the object. A triage check and a validation query are none of the types OCSF lists — they are not detection content that fires on its own — so they take Other (99) and `type` names the kind: `triage check`, `validation query`, `enrichment`. An Alert keeps whatever analytic its source reported.

**What the detection asserts.** An Alert carries the source's own statements about the threat, which triage reads before it enriches anything ([Detection & Analysis §1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment)). Each has a home on the Case:

| What the detection asserts | Where the Case carries it |
|---|---|
| The **technique identifiers** | `attacks` on the Alert's `finding_info`, and on the Case (§2) once they are the Case's |
| **What detected it**, and which detector | the Alert's `analytic`: `type_id` for the kind of detection — Rule, Behavioral, Statistical, Learning (ML/DL), Fingerprinting are the values a detection source maps onto — with `uid` and `name` for the detector itself. This is the one place `type_id` is not Other (99): an Alert keeps the analytic its source reported |
| The source's **description** of the detection | `desc` of the Alert's `finding_info` |
| The **threat name and family** | the `malware` object on the cited Detection Finding, which is where OCSF carries it. A deployment may also surface it on the Alert's `finding_info` as a `trait`; `traits` is OCSF's generic list of characteristics extracted from an observation, and the framework reserves it for no one purpose |
| The **recommended actions** | `remediation` on the cited Detection Finding, `desc` and `references`. They are indicative (§1.5): what the Case carries is what came of the ones the executor **ran** — each is the Observation it produced, naming the recommendation it came from. One it did not run leaves nothing on the Case |
| The **remediation state** of an entity | an `action` entry (§5). The source's own remediation is a [Remediation Activity](https://schema.ocsf.io/1.9.0/classes/remediation_activity) event that fired before any executor opened the Case: the entry cites it, `status_id` says whether it succeeded and `activity_id` what it did — Isolate, Evict, Restore. An entry typed `action` carries no side and no confidence, which is what the framework means by a remediation being recorded rather than weighed |

**Side and confidence.** Two framework attributes on the Observation, under its `zerosoc` object, with the values of [Definitions §7](../01-Foundation/definitions.md#7-classification-levels):

- `side` — `Malicious` or `Benign`
- `confidence_id` — `1`, `2` or `3`

An Observation that bears on no hypothesis carries **neither**: absence is how context is expressed, and context carries no weight in hypothesis resolution. An `action` entry carries neither either, since an action is not evidence for a hypothesis.

**The timeline.** A third attribute, `timeline`, marks the entries the Case Timeline renders (§5). The timeline is a reconstruction and not a listing: an entry is flagged because it belongs to the account of what happened, and most Observations do not.

All three are declared and validated in the [JSON Schema](case_schema.json), and `side` and `confidence_id` are required together or not at all. They were three `tags` until this release, which OCSF intends for categorising and searching and whose names and values it does not constrain, so nothing validated them and a misspelt tag passed silently.

**Evidence.** An Observation's evidence is its `related_events`: the events it rests on. This is the one place evidence is held — there is no second list beside the Observations, and a raw log is never an Observation's body.

The classes a Case's Observations cite are not only Alerts and Cases: a Detection Finding where the Observation is an Alert, a Remediation Activity on an `action` entry, the events of the telemetry a validation query returned. An event OCSF does not carry is named by `type` instead, which `related_event` exists to allow.

Each reference carries **when the event happened** — `first_seen_time` — not when the Observation was made. That is what lets the Case's `start_time` move: it is the earliest such time across the Case's Malicious Observations, so an adversary reaching back before the detection that caught them moves it, and a benign precursor does not.

**Relevance is the bound, and size is not.** A query that returned four hundred rows contributes the rows its Observation rests on; `count` says how many occurrences the reference stands for. What a Case excludes is not copies but irrelevance: bulk telemetry, result sets nobody reasoned from, message bodies, file content. The Note still summarizes rather than pastes — a dump is not an argument — and what an Observation rests on is the executor's judgment, stated on the record and reviewable as such. An executor may hold a limit against an answer that is a result set rather than evidence; where it applies, the reference keeps the whole answer's `count` and the query that produced it, and never an arbitrary part of the answer — a limit that selected the evidence would decide by accident which of the events a verdict rests on survives.

This is not the incident-grade record of [Detection & Analysis §3.3](../03-Processes/02-detection_and_analysis.md#33-evidence-preservation--chain-of-custody), and the difference is scope rather than kind: the Case keeps the evidence its Observations rest on, and that record adds custody, integrity and tamper-proofing once an Incident is declared.

**Directionality.** `attack_graph` SHOULD be populated where the executor can establish which entity acted on which. It is a directed graph (`is_directed` `true`) over the Case's entities, and it borrows its vocabulary rather than inventing one:

- `node.uid` is the entity's value as it appears in `observables`, and `node.type` is that observable's OCSF `type_id` — a node is an [Entity](../01-Foundation/definitions.md#entity), not a parallel concept.
- `edge.source` is the acting entity and `edge.target` the entity acted on.
- `edge.relation` is the ATT&CK technique identifier where the edge is an observed technique, and otherwise a STIX 2.1 relationship type.
- `edge.data` cites the events grounding the edge, on the same terms as an Observation.

OCSF constrains none of this and no published convention exists, so an implementation that populates the graph is stating one; the framework states this one so that two implementations agree.

## 4. Framework Fields

Concepts with no home in the current OCSF release. Each is declared under a single `zerosoc` extension object and validated in the [JSON Schema](case_schema.json).

| Field | Values | Set in | Meaning |
|---|---|---|---|
| `candidate_incident_categories` | list of `IC-##` | 2.a | Candidate categories proposed by the [alert types](alert_types.md) |
| `incident_category` | `IC-##` | 2.b | Confirmed category (provisional until `verdict_id = 2`) |
| `reclassification_pivots` | list of {from, to, reason, event_refs} | 2.b | Every change of candidate category, with the evidence that triggered it. OCSF records the new state of an observation but never what it was before, so a Case's classification history has no native form |
| `entry_path` | `alert` · `hunt` · `out-of-band` | 2.a | How the Case entered the loop; hunt and out-of-band Cases are detection false negatives by construction |
| `visibility_gaps` | list of required data sources unavailable | 2.a / 2.b | Recorded with the check each prevented ([Playbook Architecture §7](../04-Playbooks/playbook_architecture.md#7-execution)); counted by the Visibility-Gap Rate |
| `provenance` | playbooks used (path and version), executor classes, capability classes | every phase | Glass Box audit trail |
| `significant` | boolean | 2.b | NIS2 Article 23(3) significance test: severe operational disruption or financial loss, or considerable damage to other persons |
| `cross_border` | boolean | 2.b | Cross-border effect, required in the NIS2 early warning |
| `notifications` | list of {recipient, deadline, sent_at} | 3 | Stakeholder and regulatory notifications and their deadlines |
| `handover_reason` | `crown-jewel` · `privileged-identity` · `manual` | any | Why the assignee became a human |
| `watch_until` | timestamp | 2.a / 2.b close | Monitoring watch on the Case's entities after an Insufficient Data or Low-confidence close |
| `master_case_uid` | Case `uid` | 2.a / 2.b, on a Duplicate close | The open master Case that handles the activity |

### One source's own record: the per-source extension

A detection source states more than the framework has a home for — its own classification and determination, its tags, its links, the identifiers it uses for entities. Discarding them loses what an executor opening the source would see; inventing a field for each turns the framework into a second copy of every vendor's schema.

**One object per source, under the source's own key, declared where that source is described.** The key is the source's own identifier, as its description names it; the object's shape is declared by that same description — the profile or mapping document a deployment maintains for it — and validated against that declaration. A platform may not add a key that nothing declares, and a reader who has the declaration can read the object without the platform that wrote it.

What belongs there is **what the source states and the framework carries nowhere**. What does not:

- Anything the framework already carries. The severity, the status, the techniques, the entities and the evidence are mappings, not extensions, and a Case that carries them twice has two answers to the same question. Where a source's value differs from the framework's — its own severity against the one triage assessed — the native carrier for that difference is `vendor_attributes` (§2), not a second copy under the source's key.
- Anything an executor produced. The extension is the source's own record; what the work on the Case produced is the Case's own, below.
- Raw telemetry, message bodies, file content. The extension is not a loophole for the evidence rule of §3: relevance bounds what a Case holds, wherever it is held.

A framework field is what the **framework** needs and OCSF does not carry ([§4](#4-framework-fields), under `zerosoc`). A source extension is what **one source** states and nothing else has a home for. The two are not interchangeable: a concept every source has belongs in neither — it belongs in OCSF, or in a framework field once the search of §4 has been made.

## 5. Events the Case References

*   **Response actions** — a containment, eradication or recovery action is its own entry in `finding_info_list`, typed `action`. Its `related_events` **MUST** cite the OCSF [Remediation Activity [7001]](https://schema.ocsf.io/1.9.0/classes/remediation_activity) event the action produced: that event is the record of what the tool did and whether it worked, and the entry is the Case's record of it. The entry states **what was done and what decided it** in `desc` — including whether the action was pre-authorized or approved and by whom ([Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment)) — because the executor's [Course of Action](../01-Foundation/definitions.md#course-of-action-coa) is the actions taken *and the decisions that select them*, and an action nobody can account for is an action nobody authorized. `analytic` is not used here: it names what produced an Observation, and an action is not an Observation's result. An action is recorded against the Case and not against the Observation that prompted it: the reasoning may be retracted, and the action still happened. A tool-initiated action that fires before any executor opens the Case is an entry like any other, so that triage sees what has already been done — this is where the remediation state the source reports per entity is carried, one entry per remediation, and an entity the source left active has none. OCSF holds no reference in the other direction.
*   **Lifecycle** — acknowledgment, promotion, handover and closure are `activity_id` Create, Update and Close events on the Case. They are not stored in the object.
*   **The Case Timeline** is the entries whose `zerosoc.timeline` is set, in `first_seen_time` order — when the thing happened, rather than when it was recorded. It is a reconstruction of the Case, not a listing of it.

## 6. Where the Fields Are Populated

The Notes render the Case and are a field of it rather than a record beside it ([Detection & Analysis §1.6](../03-Processes/02-detection_and_analysis.md#16-triage-note)): a fact that has a field of its own is recorded in the field and not only in a Note's prose. Reasoning has no field, and the Case carries it as prose — the Summary, each Observation's own `desc`, the Note's rendering. What a phase must not do is end with its reasoning unwritten: a verdict nobody can read back is a verdict nobody can audit, whichever executor reached it.

**What was asked, and what came back, is reconstructable from the Case alone.** At the end of a phase the Case carries:

| What the phase produced | What the Case holds |
|---|---|
| Every check and every validation query | an Observation, with its `analytic` carrying the question, the request as the executor made it and the query the tool ran (§3) — or, where it could not be answered, a **visibility gap** naming the check it prevented (§4) |
| The evidence each Observation rests on | the events it rests on, in its `related_events` (§3) |
| Every action taken | an `action` entry citing its Remediation Activity, with the decision that selected it in `desc` (§5) |
| Every entity the Case is about | an observable (§2) |
| What executed it | the provenance: the playbooks and their versions, the executor classes, the capability classes (§4) |
| Why the executor concluded what it did | prose, which the Case carries: the Summary (`desc`), each Observation's own `desc`, and the Note's rendering in `notes` (§2). An alternative weighed and set aside is an Observation with no side where evidence bears on it, and the rationale of the Note where only judgment does |

A question that was asked and that nobody answered is on the Case: as a visibility gap where it prevented a check, and otherwise as an Observation that carries the question and no side, because silence about it reads exactly like a clean result.

**What must not be on the Case**: bulk telemetry, message bodies, file content, the result set a query returned beyond what its Observation rests on. The bound is relevance (§3), and it does not move because the data arrived under a source's key or in a provenance block rather than as an Observation.

**Per phase**, the fields each one sets:

*   **Phase 2.a Triage** ([Detection & Analysis §1](../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization)): aggregation, status and assignee (§1.1); observables and techniques (§1.2–1.3); severity and confidence (§1.4); Observations, verdict on close, candidate categories, visibility gaps and provenance (§1.5–1.6).
*   **Phase 2.b Investigation** ([§2](../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation)): Observations from the validation queries, confidence and verdict (§2.4); confirmed category, impact, significance and cross-border effect (§3.1); handover reason (§2.3).
*   **Phase 3 Incident Response** ([03-response.md](../03-Processes/03-response.md)): notifications; Remediation Activity events referenced from the Observations that motivated them.
*   **Phase 4 Post-Incident Activity** ([04-post_incident_activity.md](../03-Processes/04-post_incident_activity.md)): review outcomes reference the Case by `uid`.

## 7. JSON Schema

[`case_schema.json`](case_schema.json) is the formal, machine-readable version of this document (JSON Schema 2020-12). It declares the OCSF Incident Finding fields of §2 with their enum values, the Observation mapping of §3 including the tag names the framework reserves, and the framework fields of §4 under a single `zerosoc` extension object, following OCSF's extension convention of adding attributes rather than redefining classes. Where a framework field has a natural OCSF type it reuses it: provenance carries OCSF `product` objects, a ticket is an OCSF `ticket`. Object shapes borrowed from OCSF are marked `x-ocsf-object` and are intentionally open (`additionalProperties: true`) so that a platform's full OCSF object validates unchanged.
