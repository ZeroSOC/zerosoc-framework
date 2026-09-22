---
title: Phase 2 - Detection & Analysis
type: process
status: development
last_updated: 2026-09-22
license: Apache-2.0
---

# Phase 2: Detection & Analysis

Once telemetry is flowing and detection logic is active (Phase 1), the Security Operations Center (SOC) must identify and analyze security-relevant events. This phase governs the process of moving from raw alerts to validated, scoped, and prioritized incidents.

The objective of this phase is to rapidly determine whether the activity is a genuine threat (True Positive), a detection error (False Positive) or authorized activity (Benign Positive), assess the scope of any malicious activity, and pass confirmed Incidents to Response for containment. Root cause analysis is explicitly excluded from the critical path of this phase to avoid delaying containment.

## Process Flowchart

```mermaid
graph TD
    Start([Alert ingested]) --> Agg[Aggregate related Alerts into a Case]
    OOB[Out-of-band report: user, IT, partner, authority, disclosure] --> Agg
    Agg --> Ack[Acknowledge the Case: assignee set]
    Ack --> Cart[Open the domain Triage playbook]
    Cart --> Enrich[Enrich: threat intelligence, asset, identity, SOC Knowledge Base]
    Enrich --> Scope[Scope and correlate: prior Cases, history, lateral scope, campaign]
    Scope --> Prioritize[Assess Severity and Confidence, and Impact where already known]
    Prioritize --> TriageDecision{Triage decision}
    TriageDecision -->|"Close: False Positive / Benign / Duplicate"| CloseT[Close the Case; tuning signal on a False Positive]
    TriageDecision -->|Promote| Hyp[Formulate the Malicious and the Benign hypotheses]
    Hunt[Threat hunt finding] --> Hyp
    Hyp --> Playbooks[Open the Investigation & Response playbook of the candidate category; run discriminating queries]
    Playbooks --> Resolve{Resolve: score both sides}
    Resolve -->|"Benign proven, or duplicate of an open Case"| CloseI[Close the Case: False Positive / Benign / Duplicate]
    Resolve -->|"Insufficient data: remaining queries; at expiry close with a watch"| Playbooks
    Resolve -->|"Malicious proven"| Reclass{Objective exceeds the candidate category?}
    Reclass -->|"Yes: re-classify"| Playbooks
    Reclass -->|No| Decl[Confirm the Incident: verdict True Positive, category, severity, impact]
    Decl --> Notify[Stakeholder and regulatory notification]
    Decl --> Evid[Evidence preservation and chain of custody]
    Decl --> Pass[Pass scope to Phase 3 Incident Response]
```

---

## Phase 2 sub-phases

Phase 2 (Detection & Analysis) is executed in two sub-phases: **Phase 2.a — Triage** (alert-centric, low-effort, fast) and **Phase 2.b — Investigation** (hypothesis-centric, deep). The object of Triage is **Alerts**; the object of Investigation is the **hypothesis**. The split mirrors the two modes of human reasoning: Triage is **System 1** thinking — fast, pattern-based, low-cost, good at recognizing the familiar and discarding the obvious — and Investigation is **System 2** thinking — slow, deliberate, hypothesis-driven, reserved for what System 1 could not settle. Keeping them distinct keeps the fast path fast and gives the slow path only the Cases that deserve it.

## 1. Phase 2.a — Triage (Verification, Enrichment & Prioritization)

The triage process begins as soon as an Alert is triggered and a Case is opened. The goal is to quickly enrich the context and assign a severity score.

**Domain playbook selection.** Identify the alert's **telemetry domain** (Endpoint, Identity, Network, Cloud, Email, Data, Application, OT/ICS) and open the corresponding **triage playbook** under [`04-Playbooks/01-Triage/`](../04-Playbooks/01-Triage/). That playbook supplies the domain alert catalog, entity normalization & enrichment, and known false-positive conditions used in the steps below, and defines the Triage → Investigation phase transition contract it must populate (see [Playbook Architecture §5](../04-Playbooks/playbook_architecture.md)). The two-layer playbook model and the domain → Incident Category pivot are defined in [Playbook Architecture](../04-Playbooks/playbook_architecture.md).

### Inputs & Outputs

| | |
|---|---|
| **Consumes** | One or more **Security Alerts** (`Detection Finding [2004]`, `severity_id ≥ Low`) aggregated into a **Case** (`Incident Finding [2005]`), each with what it asserts about the threat — technique identifiers, threat name and family, detection source, per-entity remediation state, description and recommended actions (§1.1); enrichment sources (threat intelligence, CMDB, identity directory, SOC knowledge base); the active-Cases store. **Signals** (Informational Detection Findings) do not trigger triage; they are consulted during it. |
| **Produces (exactly one)** | (a) a **Closed Case** — `verdict_id` False Positive (`1`), Benign (`5`) or Duplicate (`10`, §1.5); a False Positive additionally emits a tuning signal to [Phase 1](01-preparation_and_engineering.md); or (b) a **Case promoted to Investigation**, carrying the Triage → Investigation phase transition contract (field schema in [Playbook Architecture §5](../04-Playbooks/playbook_architecture.md)) and the Triage Note (§1.6). Triage does **not** confirm an Incident. |

### 1.1 Reception, Aggregation, and Assignment
1.  **Alert Registration & Aggregation:** An incoming Alert is registered in the queue. To reduce alert fatigue and provide broader visibility of the potential incident, SIEM, SOAR, or XDR tools may aggregate multiple related alerts (e.g., sharing common attributes like host, user, or threat actor) into a consolidated **Security Case**.
2.  **Deduplication & Throttling Rules:**
    *   *Active Case Correlation:* The triage system queries the active Cases database. If an open, unresolved Case exists for the same host, identity, or IP address, incoming alerts are automatically appended to that existing Case instead of spawning a new one.
    *   *Rate Throttling:* If the same alert type repeatedly triggers from a single source within a sliding window (e.g., 1 hour), the system consolidates them into a single summary signal and suppresses duplicate alerts.
3.  **Acknowledgment:** The Analyst (human, automation, or agent — see [Definitions §6](../01-Foundation/definitions.md#6-executors-and-functions)) acknowledges the Case (and its constituent alerts) and shifts its state to `In Progress`.
4.  **Review the Alert(s):** Read the detection logic and key fields and form a first impression before enrichment — do not skim. Identify what behavior triggered the alert and whether it plainly warrants deeper work, so the steps that follow are directed rather than exploratory. In case multiple alerts are aggregated in a Case by the SecOps tools try to understand the relationships between the alerts and the related entities. A case with multiple alerts of different types and mapping to multiple techniques has a higher probability of representing an incident compared to an alert with a single Low / Medium severity alert.
5.  **Read what the detection asserts:** an Alert carries more than its entities and its type. Each of the inputs below is **required** at triage — read before enrichment and recorded on the Case ([Case Schema §3](../02-Taxonomy/case_schema.md#3-findings)) — because a method that ignores them re-derives by enquiry what the source already stated, and can decide a Case without noticing that the object of it was blocked at execution. They are the source's assertions, validated like the source's severity (§1.4) and never taken as a verdict.

    | Input | What it is | What triage does with it |
    |---|---|---|
    | **Technique identifiers** | the ATT&CK / ATLAS techniques the detection maps the behavior to | narrow the candidate Incident Categories (§1.4) and select the per-alert section of the triage playbook; a technique the detection names and the alert type's catalog row does not **widens** the candidates rather than being dropped |
    | **Threat name and family** | the malware, tool or activity-group name the detection assigns | seeds the Malicious hypothesis (§2.1) and directs enrichment: a named family has documented behavior, persistence and follow-on activity to look for |
    | **Detection source and detector identity** | what detected it — a signature, a behavioral rule, a learned model, a custom rule — and which detector | weighs the Alert: a signature match on a known sample and a first-of-its-kind model score are not the same evidence, and the detector is what a tuning ticket has to name |
    | **Remediation state, per entity** | whether the source blocked, quarantined, removed or left active each entity it names | recorded with the Findings on that entity (§1.6) and applied in the decision (§1.5): what was already neutralized changes what remains to be proven, and what was not is the live part of the Case |
    | **The source's description of the detection** | the source's own account of what the detection fires on | read before the checks: it states what behavior the Alert is evidence of, and it is what a False Positive condition is judged against |
    | **Recommended actions** | the procedure the source publishes for this detection | each is **followed, or set aside with a stated reason**, and the disposition is recorded (§1.5, §1.6). Silence is not an option: an unread recommendation is an unexamined step |

    An input the source does not supply is a **Visibility Gap** (§1.6), recorded with the check it prevented. A Case whose Alerts carry none of them still runs; no value for them is assumed, and none is inferred from the alert title.
6.  **Watch the Case while it is open:** while triage and investigation are in progress, the SecOps tooling may append new alerts to the Case and, in some cases, change its severity or its affected assets. The executor re-reads the Case at each step and before the decision, so that no newly added activity is overlooked.

### 1.2 Multi-Vector Context Enrichment
Before performing deep-dive analysis, the alert must be enriched with critical business and environmental context. Enrichment starts from what the detection already asserted (§1.1) and does not repeat it: a family the detection names is looked up for its behavior rather than re-attributed, and a question the detection has already answered is recorded with the detection as its source and asked again only where the decision turns on it and the answer can be checked independently.
*   **Threat Intelligence & Enrichment Capabilities:** Query indicators of compromise (IOCs) — public IPs, file hashes, domains, and URLs — against threat-intelligence and enrichment services to check reputation and known threat-actor affiliations. Use these capability classes, subject to the [Data-Handling & OSINT Egress Boundaries](../07-Governance/agentic_guardrails.md):
    *   **Multi-engine reputation lookup** for hashes, IPs, domains, and URLs — interpret the *number* of engines flagging an indicator, not a single verdict.
    *   **URL detonation / rendering** to inspect a suspicious link's behavior and content without visiting it directly. Detonation is a risky activity: perform it only in a controlled fashion on hardened, isolated sandbox systems, never from an analyst workstation or a production network.
    *   **Malware-sample / behavioral repository** lookup (by indicator) for family attribution and observed behavior.
    *   **Domain registration-age / WHOIS** — a newly-registered domain carries elevated risk.
    *   **Decoding / deobfuscation** of encoded command lines and payloads to reveal the underlying action.
*   **Asset Context:** Query the CMDB or asset inventory to retrieve:
    *   Asset business criticality (e.g., Crown Jewels, production system, dev/test).
    *   Network segment (e.g., external-facing DMZ, internal database zone).
    *   Operating system, patch level, and installed software.
*   **Identity Context:** Query directory services (e.g., Active Directory, LDAP, cloud IAM) to retrieve:
    *   User role, department, and geographic location.
    *   Privilege levels (e.g., Domain Admin, Billing Admin, standard employee).
    *   Active sessions and standard access hours.
*   **Organizational Context (SOC Knowledge Base):** Query the [SOC Knowledge Base](../01-Foundation/definitions.md#soc-knowledge-base-soc-kb) for what the CMDB and the directory do not know: VIP or high-risk status of the user, approved exceptions and known-benign activity for the entity, naming conventions that reveal an asset's role, network ranges, vulnerability scans or maintenance windows covering the alert time, and lessons learned from prior Incidents on the same entities.

### 1.3 Scope & Correlation Analysis
To understand if an alert is an isolated event or part of a wider campaign, the executor conducts:
*   **Prior Cases:** Query prior Cases for this alert type, host, or identity — the activity may already have been investigated and dispositioned, and a prior verdict with its documented reasons is valuable context. It is context, not a verdict: a Case is never closed because similar Cases were closed before. Read the prior Case's reasoning and verify that it applies to the details of this one; "similar" alerts differ in exactly the attributes that separate a benign recurrence from a new intrusion.
*   **Historical Correlation:** Query system execution, authentication, and network flow logs (typically the last 30 days) to determine if this specific asset or identity has exhibited similar anomalous patterns.
*   **Lateral Scope Analysis:** Pivot on shared parameters (such as source IP, admin credentials used, or file hashes) to check adjacent systems and shared cloud services for related activity, defining the initial blast radius.
*   **Campaign Check:** Query whether the same alert type or indicator cluster is firing across many entities in the current window. If so, aggregate the alerts into a single campaign-level Case and set `severity_id` for the campaign scope, not the single alert.

### 1.4 Case Classification: Severity, Confidence & Impact

Every Case carries three measures, defined level by level in [Definitions §7](../01-Foundation/definitions.md#7-classification-levels) and recorded in the [Case Schema](../02-Taxonomy/case_schema.md). Triage assigns them; Investigation refines them. Triage does not accept the alert's source `severity_id` at face value: it validates it and overrides it where context (asset criticality, identity privilege, blast radius) warrants.

#### A. Severity — "how bad" (OCSF `severity_id`)
**Informational (1) · Low (2) · Medium (3) · High (4) · Critical (5)**. Potential harm: the threat severity of the observed behavior combined with the criticality of what it touches. Sets the response deadlines.

#### B. Confidence — "how sure" (OCSF `confidence_id`)
**Low (1) · Medium (2) · High (3)**. The likelihood that the Malicious hypothesis is true. The same scale tags every finding (§1.6): the Case's confidence starts from its strongest alert's — or, when the tool gives none, from its severity (Informational/Low → Low, Medium → Medium, High/Critical → High) — and is set by the triage rule (§1.5) and the resolution rule (§2.4). Sets what may be acted on autonomously.

#### C. Impact — "how much harm" (OCSF `impact_id`)
**Low (1) · Medium (2) · High (3) · Critical (4)**. Realized or expected harm. Assessed at triage when already known — an external report stating the harm, or affected entities classified as critical assets or VIP users — and otherwise at incident confirmation (§3.1); **unknown** until then, never guessed. Sets what must be reported (§3.2).

#### D. Candidate Incident Categories

Triage proposes the **candidate Incident Categories** the Case may belong to, and the technique identifiers the detection supplies (§1.1) are their first input: the triage playbook's alert catalog maps each alert type to its techniques and to the categories it promotes to ([Playbook Architecture §4.1](../04-Playbooks/playbook_architecture.md#4-playbook-templates-mandatory-sections)), so a technique the detection names is looked up there and the categories it points at are added to the candidates. A technique that matches no catalog row is still recorded on the Case and named in the Note; it is a signal the catalog is incomplete, not a value to discard. The threat name and family do the same work for the hypotheses (§2.1).

None of this decides the category. Techniques describe *how*, and an Incident Category is decided by the adversary's **objective and impact** (§2.2): the candidates are where Investigation starts, and Investigation confirms or re-classifies them.

There is no separate "priority" axis. Organizations running risk-based alerting MAY add an entity **risk score** as an extension.

### 1.5 Triage Decision

Triage ends in a decision: **Close** the Case (False Positive, Benign, or Duplicate) or **Promote** it to Investigation. There is no "escalate" outcome: stakeholder notification (§3.2) happens only after Investigation confirms an Incident, and a change of assignee (§2.3) is not a triage outcome.

**Evidence at triage.** Every finding is tagged with a **side** and a **confidence** — `Malicious (High)`, `Benign (Medium)`, … — or left untagged as context (§1.6). The alerts themselves are the first Malicious findings: each independent alert in the Case is tagged `Malicious` at the confidence its tool assigned, or at the level its severity maps to when the tool gives none. Alerts of the same type on the same entity count once. A `Benign (High)` finding is one that **explains** an alert on its own: an approved exception or documented change in the SOC Knowledge Base, an authorized test window covering the host and the time, a known-benign recurrence with the same parameters.

**What the source already did.** An entity the source blocked, quarantined or removed (§1.1) is **not** an explanation of the Alert. The behavior happened; the source responded to it. So the remediation state never retracts a Finding and never lowers its confidence — it changes what remains to be proven, and it is recorded with every Finding on that entity:

*   A remediated entity leaves the questions the block does not answer: **how it arrived**, **what ran before it was stopped**, and **whether the same thing is elsewhere**. Those questions are the triage checks that remain.
*   An entity the source left **active** is the live part of the Case and is where the checks go first.
*   A Case is never closed because everything in it was blocked. A blocked payload whose delivery is unexplained is an unexplained Case, and the rule below promotes it.
*   The source's remediation is an action the Case records, not evidence for a hypothesis, so it carries no side and no confidence ([Case Schema §3](../02-Taxonomy/case_schema.md#3-findings), [§5](../02-Taxonomy/case_schema.md#5-events-the-case-references)). Recording it is what lets Response see what has already been done, and what has not.

**Recommended actions.** Each action the source recommends (§1.1) is **followed, or set aside with a stated reason** — it does not apply to this environment, the evidence contradicts it, it is already done, or it is a response action the autonomy matrix reserves for approval ([Incident Response §2.1](03-response.md#21-risk-based-autonomy-matrix-for-containment)). A recommendation followed produces a Finding like any other check, tagged on the evidence it returns; a recommendation set aside is recorded with its reason. The decision is not taken while a recommendation is unread.

**The rule.** Close as False Positive or Benign only when both hold:

1. no Malicious finding exists beyond the alerts themselves;
2. the Benign findings **cover every alert** in the Case: an alert at High confidence is covered only by a `Benign (High)` finding; an alert at Low or Medium confidence by Benign findings whose weights (Low 1, Medium 2, High 3) sum to more than its own.

Otherwise promote — including when there is no finding at all: an alert that enrichment could neither explain nor corroborate is an unexplained alert, and Investigation, not Triage, resolves ambiguity. If a required data source was unavailable, that is a Visibility Gap (§1.6), recorded as such.

**Confidence leaving triage.** Start from the strongest alert's confidence; raise one level when the Case aggregates independent alerts of different types or techniques, or holds two or more independent Malicious findings beyond them; lower one level when Benign findings exist but do not close the Case. High at triage is legitimate and authorizes nothing by itself: autonomous action keys on the confidence Investigation resolves.

*   **Checklist — can I explain *why* this is suspicious?** If you cannot articulate, in one sentence and with evidence, why the activity is suspicious, you are missing context: gather more. Do not promote out of fear, and do not close prematurely to clear the queue.

> **Example — a Case that closes at triage.** Identity alert "OAuth app consent / token-session theft", tool confidence Medium → `Malicious (Medium)`, weight 2. Findings: the user is in Marketing (context); the consented app is on the sanctioned list in the SOC Knowledge Base, onboarded last week → `Benign (High)`, 3; the same consent is seen for six colleagues the same morning → `Benign (Medium)`, 2; the publisher domain is four years old with a clean reputation → `Benign (Low)`, 1. No Malicious finding beyond the alert; the Benign findings covering it sum to 6 > 2 (and one of them explains it outright). **Close as Benign Positive**, confidence High.
>
> **Example — the source blocked it, and the Case still promotes.** Endpoint alert "Malware / loader execution", tool confidence High → `Malicious (High)`, 3. The detection asserts `T1204 (User Execution)` and `T1059 (Command and Scripting Interpreter)`, names the threat as a known loader family, was raised by a signature rather than a behavioral rule, and reports the file **quarantined** and the process **terminated**. Its recommended actions are a full scan of the device and a check for the same file elsewhere. Triage runs both, and neither bears on the side: a clean scan says no *other* malware is on the device and the file being on no other device bounds the blast radius — both are **context**, because neither is consistent with the activity having been authorized or the detection having misfired (§2.4). Two checks the block does not answer remain: the file was written by the mail client twenty minutes earlier, from an attachment no email alert fired on → `Malicious (Medium)`, 2, and the user opened it. Nothing weighs on the Benign side at all, and a Malicious finding stands beyond the Alert. **Promote** — quarantining the payload closed the execution, not the delivery, and the unexamined mail path is the Case. The quarantine and the termination are recorded as actions of the Case, so Response is not asked to contain what is already contained.
>
> **Example — a Case that promotes.** Endpoint alerts "Credential dumping" (tool confidence High → `Malicious (High)`, 3) and "Remote execution / lateral movement" (no confidence field, severity Medium → `Malicious (Medium)`, 2) on the same host. Findings: the host is a jump server used by administrators → `Benign (Low)`, 1; the knowledge base records an authorized penetration test this week whose scope does not include this host (context); the dumping process was launched from a scheduled task created two hours earlier → `Malicious (Medium)`, 2; the task creator is a service account that never created tasks before → `Malicious (Low)`, 1. A Malicious finding exists beyond the alerts and neither alert is covered. **Promote**; two independent techniques raise the confidence to High.

**Closing as Duplicate.** A Case is closed as Duplicate (`verdict_id` 10) — at triage or during investigation — when its activity, root cause and threat vector are already being handled by an open **master Case** (a tuning ticket submitted, an investigation or a response in progress) and the recurrence adds neither risk nor evidence to it. Because a wrongly closed duplicate is a missed threat, all of the following are validated first:

*   **Matching core entities:** the same primary identifiers — host, user, file hash, process, command line — as the master Case, not merely the same detection rule name.
*   **Overlapping timeline:** the activity falls in the master Case's time window and is a known step of the attack it is tracking (e.g., further beacons during an intrusion already under investigation).
*   **Active assignment:** the master Case has an assignee and is In Progress, or its tuning ticket is open.
*   **Evidence merged:** every new timestamp, event reference or indicator from the recurrence is linked or merged into the master Case before the duplicate is closed.

Do **not** close as Duplicate when the identical alert fires on a *different* host or user — that is scope expansion (possible lateral movement): add the entity to the master Case instead; when the recurrence comes long after the prior Case was resolved — treat it as possible re-infection, incomplete eradication or new compromise; or when the only similarity is the rule name. The Triage Note (§1.6) of a duplicate records the master Case identifier and the parameters that matched (e.g., "same host, user and file hash; part of the containment in progress"), so the lineage survives audit and post-incident review.

### 1.6 Triage Note

Every triage — whether performed by a human, automation, or an agent — produces a **Triage Note**, the decision record that travels with the Case and its phase transition contract. It is distinct from, and lighter than, the forensic **Evidence Preservation & Chain of Custody** record (§3.3), which is incident-grade and tamper-proof.

**The Note holds no state of its own.** Everything it shows is already on the Case, sampled at this gate: the Note is one `note` on the Case — `title` the deliverable name, `comment` the rendering, `owner` the executor, `created_time` and `modified_time` its anchors ([Case Schema](../02-Taxonomy/case_schema.md)). What follows is therefore what the rendering MUST contain, and in what order; it is not a second place the same facts are kept. What has no field of its own — the reasoning — is what the rendering carries, and it is on the Case because the Note is.

A conformant Triage Note renders, in this order:

1.  **Classification** — the Case's `severity_id`, `confidence_id` and `impact_id` (§1.4, `impact_id` **Unknown** until it is known), the candidate Incident Categories, and the decision: **Close** or **Promote** (§1.5), with the `verdict_id` on a Close and the master Case identifier where that verdict is Duplicate. It comes first because it is the part a reader compares directly against the Investigation Note's.
2.  **Summary** — a factual account, current as at this gate: **what happened and when**, which entities were involved and **who acted on whom**, and **the root cause** where it was discovered — how it is known, and how confident the executor is of it. That last confidence is prose and is **not** `confidence_id`, which is confidence in the Malicious/Benign verdict alone.
3.  **Findings** — every Finding the Case holds: the Alerts, and the result of each check run — entity context, entity and process analysis, threat-intelligence results, and the historical baseline (was this seen before, and how many of the prior Cases on the same entities or alert type were confirmed True Positive?). Each Finding renders with its **side and confidence** — `Malicious (High)`, `Benign (Medium)`, … — or with neither where it is pure context — asset role, user department (§1.5, §2.4); with **what produced it**, the check or query being the Finding's `analytic`; and with **the events it rests on**, cited by OCSF identifier or platform event link. A Finding without a traceable event reference is not conformant, and a raw-log dump is not an event reference. The Note cites what the Case keeps: the events a Finding rests on are preserved on the Case with what the Finding reasoned from ([Case Schema §3](../02-Taxonomy/case_schema.md#3-findings)), so a Note read after the source's retention window has closed still rests on something.
    Each **Alert** Finding also renders what its detection asserted (§1.1): the technique identifiers as `ID (Name)`, the threat name and family where one was assigned, the detection source and the detector, and the remediation state of each entity the Alert names — blocked, quarantined, removed or active. The **disposition of the recommended actions** renders with the Findings: one followed renders as the Finding it produced, naming the recommendation it came from; one set aside renders with the reason it was set aside.
4.  **Rationale** — one to two sentences, citing the Findings, saying why the decision follows: which alerts the Benign findings cover, or which Malicious finding stands beyond them (§1.5).
5.  **Case Timeline** — the Findings the Case flags for the narrative, in `first_seen_time` order ([Case Schema §5](../02-Taxonomy/case_schema.md)). Early in a Case usually nothing is flagged; the element then renders "None."
6.  **Visibility Gaps** — every `required_data_sources` entry ([Playbook Architecture §7](../04-Playbooks/playbook_architecture.md#7-execution)) unavailable during triage, and every required input of §1.1 the source did not supply, each paired with the check it prevented; write "None." when no gap occurred. The countable source for [Visibility-Gap Rate](../05-Metrics/operational_metrics.md).
7.  **Provenance** — the playbook(s) used (path plus its `last_updated` date as version), the executor (human / automation / agent — list all classes that materially contributed, e.g. `automation + agent`), the capability classes invoked, and the case/incident ID(s). Required for Glass Box auditability ([Agentic Guardrails](../07-Governance/agentic_guardrails.md)).

**Two former elements are gone, not lost.** *Actions Taken* was a prose restatement of work each Finding already accounts for: the check that produced a Finding is that Finding's `analytic`, rendered beside it. *References* was a second list of the same event identifiers the Findings cite; per-Finding evidence stays with the Finding, and the preserved-evidence pointer belongs with Provenance, where it appears only once preservation has happened (§3.3).

Notes must be specific and concise: state findings in accurate terms rather than vague language, and summarize evidence rather than pasting raw logs — what the Note summarizes, the Case keeps, and neither holds what no Finding rested on. Whenever ATT&CK/ATLAS technique codes appear in a Note, they SHOULD be written as `ID (Name)` (e.g. `T1114.003 (Email Forwarding Rule)`).

---

## 2. Phase 2.b — Investigation

Investigation is driven by testing competing hypotheses rather than unstructured searching. It executes the Investigation & Response playbooks under [`04-Playbooks/02-Investigation-Response/`](../04-Playbooks/02-Investigation-Response/), selected by candidate Incident Category (the domain → Incident Category pivot of the [Playbook Architecture](../04-Playbooks/playbook_architecture.md)).

### Inputs & Outputs

| | |
|---|---|
| **Consumes** | The promoted Case, its Triage → Investigation phase transition contract, and its Triage Note (§1.6). The Note's tagged Findings — the enrichment of §1.2 and the scope and correlation results of §1.3 — are the starting evidence of the investigation and seed its score (§2.4); they are verified and extended, not re-collected. The Note also carries the reason the Case could not close: the Malicious findings beyond the alerts, and the Benign findings they were weighed against — the conflict Investigation starts from. |
| **Produces (exactly one)** | (a) a **Closed Case** — Benign hypothesis proven, `verdict_id` False Positive (`1`) or Benign (`5`) (a False Positive emits a tuning ticket to [Phase 1](01-preparation_and_engineering.md)); or (b) a **Confirmed Incident** — Malicious hypothesis proven — by setting `verdict_id = 2` (True Positive), assigning the definitive Incident Category, severity and impact, and the timeline, and emitting the Investigation → Response phase transition contract (field schema in [Playbook Architecture §5](../04-Playbooks/playbook_architecture.md)). Stakeholder and regulatory notification (§3.2) is triggered after confirmation; a change of assignee (§2.3) is a within-phase control. |

### 2.1 Concurrent Malicious/Benign Hypothesis Formulation
The executor formulates two competing narratives based on the observed behaviors and MITRE ATT&CK techniques:
*   **Malicious hypothesis (True Positive):** The telemetry indicates a threat actor performing unauthorized, malicious actions.
*   **Benign hypothesis (False Positive or Benign Positive):** The telemetry is explained by standard IT administration, developer testing, scheduled tasks, or expected user activities.

Where the detection named a **threat or family** (§1.1), that name is where the Malicious hypothesis starts: a named family has documented behavior, persistence and follow-on activity, and the investigation asks whether *those* are present rather than whether the activity is malicious in general. A name is a lead and not a verdict — an attribution the evidence does not support is retracted like any finding (§2.4), and its absence narrows nothing.

There are always exactly two sides. Competing explanations within a side — which Incident Category on the malicious side, which authorized activity on the benign side — are sub-hypotheses; the evidence they gather scores for their side (§2.4). The hypotheses as worded in the playbooks are indicative: the executor refines them to the Case.

### 2.2 Playbook Execution
1. **Verify the triage findings, starting from the conflict** that promoted the Case: confirm each tagged Finding (§1.6) or **retract** it when it does not hold or does not apply to this Case, and aim the first discriminating queries at the findings that conflict.
2. Apply the **domain → Incident Category pivot**: using the candidate `incident_category` from the Triage → Investigation phase transition contract, open the matching Investigation & Response playbook in [`04-Playbooks/02-Investigation-Response/`](../04-Playbooks/02-Investigation-Response/); if no specialized playbook exists, use the catch-all `00-generic.md`. (Contract fields per [Playbook Architecture §5](../04-Playbooks/playbook_architecture.md).) The technique lists in the playbooks and alert types are indicative, not exhaustive: the relation between techniques and Incident Categories is intentionally loose, and a category is decided by the adversary's objective and impact, not by technique lookup.
3. Execute the validation queries. The playbook's queries are **indicative, non-exhaustive examples** of the discriminating evidence that has worked for that category: the executor chooses the applicable ones and adds any step their experience warrants; every query run, listed or added, is recorded in the Investigation Note with its tag (§2.5). Queries must be **discriminating** and state the reading of both outcomes. Seek evidence against the favoured hypothesis, not only for it.
4. Resolve per §2.4, then act on the outcome: a proven Malicious hypothesis promotes the Case to a confirmed Incident (§3.1); a proven Benign hypothesis closes the Case (a False Positive submits a tuning ticket to [Phase 1: Preparation & Engineering](01-preparation_and_engineering.md)).
5. **Re-classify on evidence drift:** if evidence reveals the activity's objective differs from, or exceeds, the current candidate Incident Category (e.g. a commodity loader staging ransomware, or phishing that yielded credentials), update the candidate `incident_category`, switch to the matching Investigation & Response playbook, and carry all accumulated evidence forward. Record the pivot, and its reason, in the Investigation Note (§2.5). The classification remains provisional until `verdict_id = 2` is set at incident promotion (§3.1).

### 2.3 Case Assignment
Every Case has one **assignee** (OCSF `assignee`): the executor responsible for advancing it and for its verdict. A change of assignee is a [handover](../01-Foundation/definitions.md#handover). The conditions under which the assignee must be a human — accountability for Crown Jewel assets and privileged identities — and the metering of automation and agents (investigation timebox, token budget) are specified in [Agentic Guardrails](../07-Governance/agentic_guardrails.md); this process applies the same resolution rule (§2.4) whoever the assignee is. A handover does not block the containment actions that [Incident Response §2.1](03-response.md#21-risk-based-autonomy-matrix-for-containment) pre-authorizes.

### 2.4 Hypothesis Resolution, Verdict and Confidence

Every finding — an alert, a tagged Triage Note Finding (§1.6) or a query result — carries a **side** and a **confidence**: `Malicious (Low | Medium | High)` or `Benign (Low | Medium | High)`. Playbook query tags MUST use exactly this vocabulary. The levels are the framework's confidence levels ([Definitions §7](../01-Foundation/definitions.md#7-classification-levels)): **Low** (weight 1) — consistent with the side, explainable otherwise; **Medium** (2) — corroborates the side, not conclusive alone; **High** (3) — sufficient on its own; on the Benign side, a finding that explains the alert.

**What carries no weight.** A result that yields no information carries neither side: an indicator no source holds a record of is **context**. This is narrower than "found nothing" — a covered host showing no child process in the window is a scoped negative observation and a real `Benign` finding, because something was learned; a threat-intelligence lookup that knows nothing is not. A check that could not be run at all is a **visibility gap** (§1.6), not a finding. A **remediation the source performed** carries neither side either, at this gate as at triage (§1.5): it is an action the Case records, and the questions it leaves open — how the entity arrived, what ran before it was stopped, whether the same thing is elsewhere — are the ones the validation queries answer.

**Score and retraction.** Each side scores the sum of its findings' weights, triage and investigation together. Findings derived from the same underlying telemetry artifact count once — a triage lookup and an investigation lookup on the same indicator are one finding. A query result that refutes a finding **retracts** it: its tag is removed, the score recomputed, and the retraction with its reason recorded in the Note. A result that indicates the other side is tagged on that side at the confidence it deserves.

**Resolution.**

1. **Malicious is proven** when its score, after retractions, is **3 or more**.
2. **Benign is proven** when its score is **3 or more** *and* its explanation **covers every Medium and High confidence Malicious finding** — each is either retracted or accounted for by the explanation. Uncovered Low-confidence Malicious findings never block a Benign verdict; they lower its confidence one level and are listed in the Note as residual observations, which the monitoring watch covers.
3. **Verdict and confidence:**

| Outcome | Verdict (`verdict_id`) | Confidence (`confidence_id`) | Next step |
|---|---|---|---|
| Benign proven | False Positive (`1`) if the detection was wrong; Benign Positive (`5`) if the activity was authorized | the highest confidence on the Benign side, minus one level for residual Low-confidence Malicious findings | Close; a False Positive emits a tuning ticket to Phase 1; a Low-confidence close carries a monitoring watch and is flagged for QA sampling |
| Malicious proven (and Benign not) | True Positive (`2`) | the highest confidence on the Malicious side | Promote to Incident (§3.1); response autonomy keys on this confidence — at Low, every containment action requires approval per [Incident Response §2.1](03-response.md#21-risk-based-autonomy-matrix-for-containment) |
| The activity is already handled by an open master Case (§1.5 duplicate criteria met) | Duplicate (`10`) | — | Close; evidence merged into the master Case |
| Neither proven | none — **insufficient data** | — | Run the remaining discriminating queries, listed or added; when the investigation timebox or budget expires ([Agentic Guardrails](../07-Governance/agentic_guardrails.md)), apply this rule to the evidence at hand and, if still neither, close as Insufficient Data (`7`) with a monitoring watch (re-open on recurrence of the entities; active monitoring for the retention window at High/Critical severity) and a visibility or tuning ticket |

Because Benign proof requires coverage, the two sides cannot both be proven: an explanation that leaves a Medium or High Malicious finding standing is incomplete, and the Malicious verdict holds until a query retracts that finding or the explanation grows to cover it.

> **Example — retraction flips the verdict.** A user-reported phishing alert, tool confidence Medium → `Malicious (Medium)`, 2. Triage found: sender domain registered three days ago → `Malicious (Medium)`, 2; the link is a credential-harvesting page per detonation → `Malicious (High)`, 3; the SOC Knowledge Base lists a running phishing-awareness campaign by the training vendor → `Benign (High)`, 3. Malicious 7, Benign 3 — promoted, because Malicious findings exist beyond the alert. Investigation starts from the conflict: the vendor confirms the message is theirs and the harvesting page is their mock-up. That **retracts** the harvesting-page and young-domain findings, which belong to the simulation. Malicious is back to the alert alone, 2; Benign 3 covers it (the only remaining Medium/High Malicious finding is the alert, explained by the campaign). **Benign proven → Benign Positive, confidence High.**
>
> **Example — coverage decides, no arbitration needed.** Credential-dumping alert, tool confidence High → `Malicious (High)`, 3. Investigation: the credential was used from a new host forty minutes later → `Malicious (High)`, 3; the process that read LSASS is the backup agent's signed binary, which does so by design on every host → `Benign (High)`, 3. Malicious 6, Benign 3, but the Benign explanation covers only the alert, not the later credential use: **Benign is not proven; Malicious is** — True Positive, High. The playbook's next query asks whether that use was the agent's own authentication to the backup target. If it was, the finding is retracted, the explanation now covers everything, and the verdict is **Benign Positive, High**. If it was not, the Incident stands.
>
> **Example — confidence is the strongest finding, not an average.** C2-beaconing alert, Medium → `Malicious (Medium)`, 2. Investigation: the destination is an active C2 server on a threat-intelligence feed → `Malicious (High)`, 3; the beacon interval is regular to the second → `Malicious (Low)`, 1; the process is unsigned → `Malicious (Low)`, 1; first contact at 02:14 → `Malicious (Low)`, 1. Malicious 8, Benign 0: **True Positive, confidence High** — the feed hit is sufficient on its own. An average (1.6) would have said Medium and denied the pre-authorized containment a confirmed C2 destination warrants; the three Low findings describe the intrusion, they do not dilute it.
>
> **Example — a Low-confidence verdict is acted on, not escalated.** New cloud access key, tool confidence Low → `Malicious (Low)`, 1. Investigation adds: created outside change windows → `Malicious (Low)`, 1; by a principal that never created keys → `Malicious (Low)`, 1; used from a region the account never used → `Malicious (Low)`, 1. Malicious 4, Benign 0: **True Positive at Low confidence.** The Incident is declared and passed to Response, where at Low confidence every containment action — even revoking the key — requires approval under the autonomy matrix. The remaining queries, or the response itself, raise the confidence or retract the findings.

### 2.5 Investigation Note (Verdict Evidence Record)

Every Investigation — whether performed by a human, automation, or an agent — produces an **Investigation Note** on Investigation close or incident promotion. It has the **same element structure as the Triage Note** (§1.6), and the same rendering contract: it holds no state of its own, and renders the Case at this gate. It **extends and updates** the Triage Note rather than mirroring it — the same Case further along, with the Findings triage made now verified or retracted.

A conformant Investigation Note renders, in this order:

1.  **Classification** — the confirmed (or, on close, the last candidate) Incident Category, the assessed `severity_id`, `confidence_id` and `impact_id`, and for a confirmed Incident whether it is significant and whether it is cross-border (§3.1); and the decision: the `verdict_id` the resolution rule produced (§2.4), with the master Case identifier where that verdict is Duplicate.
2.  **Summary** — a factual account, current as at this gate, on the same terms as §1.6: what happened and when, which entities were involved and who acted on whom, and the root cause where discovered, how it is known and how confident the executor is of it. That confidence is prose and is not `confidence_id`.
3.  **Findings** — every Finding the Case holds: the Alerts; the Findings triage made, each now **verified or retracted** with the reason; and the result of each validation query run. Each renders with its side and confidence or with neither, with what produced it — the validation query being the Finding's `analytic` — and with the events it rests on, cited by identifier. The Alerts render what their detection asserted, as in §1.6, with the remediation state of each entity **as it stands at this gate** and the disposition of the recommended actions.
4.  **Rationale** — the §2.4 resolution applied: the score of each side, the side proven and the Findings that carry it, and the Findings retracted and why. The confidence is in Classification; the Rationale says **how it was reached**, not what it is.
5.  **Re-classification Pivots** — any candidate `incident_category` change (§2.2), with the reason and the evidence that triggered it.
6.  **Case Timeline** — a chronological reconstruction of the Case: **the course of the attack** (initial access → progression → objective, where established) interleaved with the detection and the response actions taken, each entry timestamped (UTC) and citing its supporting event reference. The timeline is the entries the Case flags for it, in `first_seen_time` order ([Case Schema §5](../02-Taxonomy/case_schema.md)), not a field the Case stores. The Case's `start_time` opens at its earliest Alert and moves earlier whenever a Malicious Finding cites an earlier event; on a **confirmed Incident** it is the earliest confirmed malicious event — the Case's **T0**, the anchor for MTTD/MTTC/MTTR ([Operational Metrics §4](../05-Metrics/operational_metrics.md)) and for the Phase 4 reconstruction ([Post-Incident Activity](04-post_incident_activity.md)). A Case that closes without the Malicious hypothesis being proven still carries a Case Timeline — it documents the Case, not only the attack — and its `start_time` is its earliest Alert's own start, which is not a T0 and anchors no metric.
7.  **Visibility Gaps** — every `required_data_sources` entry ([Playbook Architecture §7](../04-Playbooks/playbook_architecture.md#7-execution)) unavailable during investigation, and every required input of §1.1 the source did not supply, each paired with the check it prevented; write "None." when no gap occurred. The countable source for [Visibility-Gap Rate](../05-Metrics/operational_metrics.md).
8.  **Provenance** — the playbook(s) used (path plus its `last_updated` date as version), the executor (human / automation / agent — list all classes that materially contributed, e.g. `automation + agent`), the capability classes invoked, the case/incident ID(s), and — once evidence has been preserved — the pointer to it (§3.3). Required for Glass Box auditability ([Agentic Guardrails](../07-Governance/agentic_guardrails.md)).

**Two former elements are gone, not lost.** *Executed Queries* named a table that never held only queries: a query that produced a Finding is that Finding's `analytic`, and the triage Findings carried forward are Findings, so both belong in the Findings element. *Evidence References* was the same second list of identifiers §1.6 dropped, with the preserved-evidence pointer moved to Provenance.

The Investigation Note is the machine-reviewable record consumed by QA sampling ([Agentic Supervision](../07-Governance/agentic_supervision.md)) and by post-incident review (Phase 4). As in the Triage Note, ATT&CK/ATLAS technique codes SHOULD be written as `ID (Name)` (e.g. `T1114.003 (Email Forwarding Rule)`).

---

## 3. Incident Declaration & Notification

The promotion of a Case to an Incident is a formal event that triggers technical, management, and regulatory communication channels.

### 3.1 Incident Promotion
The moment Malicious hypothesis is proven:
1. Promote the Case to an active **Incident** by setting its `Incident Finding` **`verdict_id = 2` (True Positive)** — the confirmation step that distinguishes an Incident from a Case (see [Definitions](../01-Foundation/definitions.md)).
2. Assign the definitive [Incident Category](../02-Taxonomy/incident_categories.md), record the observed MITRE ATT&CK tactics and techniques, and carry forward the timeline: promotion's `scope/impact/timeline` output (§2, Inputs & Outputs) *is* the Investigation Note's **Case Timeline** (§2.5); its earliest **confirmed malicious** event is recorded as **T0**, the anchor for MTTD/MTTC/MTTR ([Operational Metrics §4](../05-Metrics/operational_metrics.md)).
3. **Confirm or assess Impact and regulatory significance:** confirm the Impact recorded at triage, or assess it now — `impact_id` (Low / Medium / High / Critical) as the realized or expected harm to operations, data and third parties; determine whether the Incident is **significant** under NIS2 Article 23(3) — it caused or can cause severe operational disruption or financial loss, or considerable material or non-material damage to other persons — and whether it has **cross-border** effect. For financial entities, DORA's classification criteria (clients and counterparts affected, duration, geographic spread, data losses, criticality of the services, economic impact) inform the same assessment. These are fields of the [Case Schema](../02-Taxonomy/case_schema.md) and drive §3.2.
4. **Retrospective entity sweep:** query Cases closed as False Positive or Benign within the lookback window (default 90 days) that share the incident's entities. Every match is a candidate **verdict false negative** — flag it for mandatory QA review ([Agentic Supervision §2](../07-Governance/agentic_supervision.md)); confirmed misses are adjudicated in the Post-Incident Review ([Phase 4 §3](04-post_incident_activity.md)). Candidate matches are never silently dismissed.
5. Pass the initial scope (blast radius) directly to [Phase 3: Incident Response](03-response.md) for immediate containment.

### 3.2 Stakeholder & Regulatory Notification
Notification is the responsibility of the [SOC Manager](../01-Foundation/definitions.md#6-executors-and-functions) and keyed on the Incident's severity and impact (§3.1).

**Internal notification, by severity** (reference response times; the values are an organization policy knob):
*   **Low / Medium:** incident ticket to the affected asset owners; no out-of-hours notification.
*   **High:** notify the affected asset owners and the security lead within 30 minutes.
*   **Critical:** notify the CISO, legal counsel, risk management and executive leadership within 15 minutes.

**Regulatory notification** applies when the Incident is **significant** (§3.1) and the organization is in scope of the regulation. Deadlines run from awareness of the Incident; the reporting procedure and the content of each report are specified in [Incident Response §6](03-response.md#6-regulatory-reporting-nis2--dora):
*   **NIS2 (Article 23):** early warning within **24 hours** (whether the Incident is suspected to be malicious or unlawful, and whether it has cross-border effect); incident notification within **72 hours** with the initial assessment of severity and impact and the indicators of compromise; final report within **one month**.
*   **DORA (Article 19):** initial notification, intermediate report and final report on the deadlines of the regulation, with the classification of the Incident as major.

The recipient of these notifications is the national CSIRT or the competent authority designated by the regulation; the framework uses the term CSIRT in that sense only.

### 3.3 Evidence Preservation & Chain of Custody
All data collected during triage and investigation must be preserved to support subsequent forensics, root cause analysis, or legal prosecution:
*   Maintain a timestamped audit trail of all commands run, scripts executed, and queries submitted.
*   Preserve volatile evidence (e.g., memory captures, active network sessions, process lists) using non-destructive gathering scripts.
*   Store all evidence, screenshots, and logs in a secure, write-once, tamper-proof incident ledger.

---

## 4. Threat Hunting

Threat Hunting is a proactive sub-process that runs in parallel with continuous monitoring to detect adversaries that have bypassed automated rules.

### 4.1 Sprint-Based Cadence
Threat hunting is conducted in structured sprints at a cadence defined by the organization (bi-weekly recommended). Each hunt must target a specific hypothesis rather than generalized log parsing.

### 4.2 Hypothesis Generation
Hunt hypotheses are generated from:
*   **Threat Intelligence:** Newly published MITRE ATT&CK TTPs or threat group profiles.
*   **Vulnerability Disclosures:** Supply chain concerns or newly discovered software flaws.
*   **Crown Jewels Review:** Proactive baselining and verification of access logs to the company's most critical assets.

### 4.3 Pipeline Integration
If a threat hunt uncovers signs of malicious activity:
1. Immediately generate a high-priority Alert.
2. Formulate a Case and ingest it directly into **Investigation** (§2) for immediate validation, prioritization, and response. A hunt-found incident is, by definition, a detection false negative — its Alert was registered by the hunt, not produced by Phase-1 detection content — and feeds the recall metrics in [Operational Metrics §5.5](../05-Metrics/operational_metrics.md).

---

## 5. Out-of-Band Incident Intake

Detection does not only fail loudly; it also fails silently. Suspected incidents surface outside the alert pipeline: a user report, an IT anomaly ticket, a partner / CERT / law-enforcement notification, a vendor breach disclosure, or activity stumbled upon during an unrelated investigation. Each of these is a potential **detection false negative**. The framework treats their intake as a first-class Phase 2 entry point — not an ad-hoc side channel — so that misses are investigated with the same rigor as alerts and measured honestly ([Operational Metrics §5.5](../05-Metrics/operational_metrics.md)).

1. **Register:** create an Alert (`Detection Finding [2004]`, severity per initial assessment) and aggregate it into a Case per §1.1. Out-of-band reports run the standard triage → investigation pipeline and produce the same Notes and deliverables — no shadow process. Because the Alert is registered by this intake step rather than produced by Phase-1 detection content, the discovery channel is evident from the Case itself; no additional marking is required ([Operational Metrics §5.5](../05-Metrics/operational_metrics.md)).
2. **Evaluate & attribute:** triage and investigate per §1–§2. If the Case is confirmed as an Incident, it is a **confirmed detection false negative**: the Post-Incident Review MUST perform the missed-detection analysis ([Phase 4 §3](04-post_incident_activity.md)), converting the miss into detection requirements rather than just a closed ticket.
