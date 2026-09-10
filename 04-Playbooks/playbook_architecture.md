---
title: Playbook Architecture
type: concept
status: draft
last_updated: 2026-09-10
license: Apache-2.0
---

# Playbook Architecture

> **Draft.** The playbook module is published for review with the structure below and the first set of triage and Investigation & Response playbooks. The checks, hypotheses and queries in the playbooks are indicative and will grow with adopters' contributions; the structure is what this document fixes.

Traditional SOC playbooks are monolithic per-incident documents that repeat the generic method in every one of them and assume malicious intent the moment an alert fires. The framework separates the two: the **method** is written once in the processes, and the playbooks hold only the **knowledge** specific to an alert type or an Incident Category — what to look at, what each observation is evidence of, what to do once the Incident is confirmed.

This document is the **normative standard** every playbook in this directory MUST follow.

## 1. Conformance & Normative Keywords

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be interpreted as described in RFC 2119. A playbook is **conformant** when it satisfies every MUST for its playbook type (§4) and is executable alike by a human analyst, deterministic automation or an agent ([Executor Neutrality](../01-Foundation/framework_manifest.md#executor-neutrality-and-human-readability)).

## 2. Two-Layer Architecture

**Layer 1 — the method ("how"), authored once in [03-Processes](../03-Processes/00-detection_and_response_lifecycle.md).** Alert-type-independent. Playbooks reference it and never restate it:

*   **Phase 2 Detection & Analysis** — Triage (object: the Alerts) and Investigation (object: the hypotheses): [Detection & Analysis](../03-Processes/02-detection_and_analysis.md).
*   **Phase 3 Incident Response** — containment, eradication, recovery, and the containment autonomy matrix: [Incident Response](../03-Processes/03-response.md).
*   **Phase 4 Post-Incident Activity** — generic, at the process level: [Post-Incident Activity](../03-Processes/04-post_incident_activity.md); no per-category playbook.

**Layer 2 — the knowledge ("what"), in this directory**, split by the object each phase works on:

*   **Triage playbooks, by telemetry domain** ([`01-Triage/`](01-Triage/)): Endpoint, Identity, Network, Cloud, Email, Data, Application, OT/ICS. They index the [Alert Type taxonomy](../02-Taxonomy/alert_types.md) and say, per alert type, which entities to enrich, what to check and what each result is evidence of.
*   **Investigation & Response playbooks, by Incident Category** ([`02-Investigation-Response/`](02-Investigation-Response/)): one per category, plus a catch-all. They hold the Malicious and Benign hypotheses, the validation queries, and the category-specific containment, eradication and recovery actions.
*   **Shared sub-playbooks** ([`99-Shared/`](99-Shared/)): per-entity enrichment content — identity, asset, network, artifact, email message — that both layers reference rather than duplicate. They are phase-neutral and named with a `sub_` prefix. Every shared sub-playbook MUST end with a **Produces** block naming its outputs, so that the Notes cite enrichment results by a stable name.

The **domain → Incident Category pivot** connects the two: triage proposes candidate categories, and the Investigation & Response playbook of the candidate takes over through the Triage → Investigation phase transition contract (§5).

## 3. Canonical Homes

Each concept has one home; everything else links to it.

| Concept | Canonical home |
|---|---|
| Triage method: enrichment, scope, the coverage rule that closes or promotes; Investigation method: verify or retract, score, coverage, verdict and confidence | [Detection & Analysis](../03-Processes/02-detection_and_analysis.md) §1 and §2 |
| Finding tags — `Malicious (Low\|Medium\|High)`, `Benign (Low\|Medium\|High)` | [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence) |
| Classification: severity, confidence, impact | [Detection & Analysis §1.4](../03-Processes/02-detection_and_analysis.md#14-case-classification-severity-confidence--impact); levels in [Definitions §7](../01-Foundation/definitions.md#7-classification-levels) |
| Containment autonomy: which actions require approval | [Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment) |
| Human assignee conditions, approval payload, egress and metering | [Agentic Guardrails](../07-Governance/agentic_guardrails.md) |
| The Case and its fields | [Case Schema](../02-Taxonomy/case_schema.md) |
| Playbook structure, routing and the phase transition contracts | this document |
| Practitioner entry point | [Playbook Operating Guide](README.md) |

Playbooks therefore contain no handover conditions, no autonomy boundaries and no restatement of the resolution rule. Where a playbook's response action falls in the approval tier of the autonomy matrix, the action is marked **requires approval** in place.

## 4. Playbook Templates (mandatory sections)

### 4.1 Triage playbook (`01-Triage/`, see [_TEMPLATE](01-Triage/_TEMPLATE.md))

Front matter MUST include `title`, `type: playbook`, `last_updated`, `license`, `domain`, `required_data_sources` and `status` (release status per the [Framework Manifest](../01-Foundation/framework_manifest.md#versioning--document-release-status); a playbook copied from the template starts as `draft`). Body MUST contain, in order:

1. **Alert Catalog** (MUST) — the domain's alert types drawn from the [Alert Type taxonomy](../02-Taxonomy/alert_types.md), as a table `Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories`, indexing the Per-Alert Triage subsections. Tactics and techniques are the candidates an alert type *may* map to, from which the executor selects those matching the observation; they are not a conjunction and not exhaustive.
2. **Per-Alert Triage** (MUST) — one `###` subsection per catalog row, with exactly these labeled elements:
   - **Enrich entities:** the entities in scope, each linked to its enrichment sub-playbook in [`99-Shared/`](99-Shared/).
   - **Checks:** the observations specific to this alert type, numbered. Each check states the question and **what its result is evidence of**, in the tags of Detection & Analysis §2.4: `Malicious (Low|Medium|High)` when ..., `Benign (Low|Medium|High)` when .... A result that bears on neither hypothesis is context. The levels follow the confidence table of Definitions §7: High when the observation alone establishes the side, Medium when it is a strong signal that needs a second, Low when it is consistent with the side but common in normal operation.
   - **False Positive conditions:** activity that is *not* what the detection looks for, yet triggers it — a heuristic misfire, a parser artifact, a stale rule. When such a condition explains the alert, the Case closes as **False Positive** (`verdict_id` 1) and emits a tuning ticket to Phase 1.
   - **Benign conditions:** authorized activity that *legitimately* matches the detection — an approved change, a sanctioned tool, a documented exception. When such a condition explains the alert, the Case closes as **Benign** (`verdict_id` 5) and, if the exception was not recorded, emits a Knowledge Base entry. The two lists are kept apart because their remediation differs: a False Positive fixes the detection, a Benign fixes the organization's knowledge of itself.
   - **Candidate Incident Category(ies):** the categories this alert type promotes to.

   Checks and conditions are indicative. The decision — close or promote — is the coverage rule of [Detection & Analysis §1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision) applied to the tagged findings; the playbook never restates it.

### 4.2 Investigation & Response playbook (`02-Investigation-Response/`, see [_TEMPLATE](02-Investigation-Response/_TEMPLATE.md))

Front matter MUST include `incident_category`, `mitre_ttps` (indicative), `default_severity`, `required_data_sources` and `status`. Body MUST contain, in order:

1. **Investigation** (MUST) — the **Malicious** and **Benign** hypotheses for the category, and the **validation queries**. Each query is stated as a question the executor translates to its own query language, and names what its outcomes are evidence of, in the tags of Detection & Analysis §2.4: `→ Malicious (High) if <result>; Benign (Low) if <result>`. A query MAY yield context for one of its outcomes. At least one query MUST yield the **`Benign (High)`** finding that explains the alerts when the Benign hypothesis is true: without it the Benign side can never be proven, and the playbook is biased toward promotion. Hypotheses and queries are indicative, not exhaustive; the executor adds the queries the Case calls for and tags them the same way.
2. **Re-classification pivots** (SHOULD) — the adjacent categories an investigation commonly re-classifies to, per [Detection & Analysis §2.2](../03-Processes/02-detection_and_analysis.md).
3. **Incident Response** (MUST) — Containment, Eradication, Recovery for the category. Actions in the approval tier of the [autonomy matrix](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment) — stopping a critical service, irreversible, affecting many entities at once — are marked **requires approval**; every other action is pre-authorized, subject to the Case confidence.
4. **Completion Criteria & Critical Failures** (MUST) — *Complete when:* the Case is resolved per Detection & Analysis §2.4, the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted, plus category-specific conditions. *Critical failures:* the category-specific outcomes that void a run regardless of any other quality — a verdict reached without a required query, an approval-tier action applied without approval, a closure that leaves a confirmed foothold — consumed by [QA sampling](../07-Governance/agentic_supervision.md) as auto-fail conditions. Numeric scoring is out of scope; scoring harnesses are a platform concern.
5. **Hunting Pivots** (SHOULD) — one to three hunt hypotheses linking the category to the fleet-wide sweeps it suggests, per [Threat Hunting](../03-Processes/02-detection_and_analysis.md#4-threat-hunting).
6. **References** (SHOULD).

## 5. Phase Transition Contracts

A [phase transition contract](../01-Foundation/definitions.md#phase-transition-contract) is the set of [Case Schema](../02-Taxonomy/case_schema.md) fields a Case carries when it moves forward. Both contracts are subsets of the schema; no field is defined here.

*   **Triage → Investigation** (promoted Cases only; a closed Case carries no contract): `uid`, `status_id` (In Progress), `severity_id`, `confidence_id`, `impact_id` when already known, `observables` (the normalized entities), `finding_info_list` (the alerts), `attacks` (candidate techniques), `candidate_incident_categories`, `entry_path`, `master_case_uid` when correlated to an open Case, `visibility_gaps`, `provenance`, and a reference to the **Triage Note**. `verdict_id` stays `0`: the promoted Case carries no verdict.
*   **Investigation → Response** (confirmed Incidents only): the fields above, refined, plus `verdict_id` (2), `incident_category` (confirmed), `t0` and `timeline`, `impact_id`, `significant`, `cross_border`, `is_suspected_breach`, `handover_reason` when a handover occurred, and the recommended containment, eradication and recovery actions from the playbook, together with a reference to the **Investigation Note**.

Verdict values: `1` False Positive, `2` True Positive, `5` Benign, `7` Insufficient Data, `10` Duplicate ([Definitions §3](../01-Foundation/definitions.md#3-case-dispositions-verdicts)).

## 6. Coverage Matrix

The playbooks cover the eight telemetry domains and the fifteen Incident Categories; new categories or domains are added here as the taxonomies grow. The Status column mirrors each playbook's frontmatter, which is authoritative.

| Layer | Unit | Playbook(s) | Status |
|---|---|---|---|
| Triage | Endpoint, Identity, Network, Cloud, Email, Data, Application, OT/ICS | `01-Triage/` | draft |
| Investigation & Response | IC-01 Phishing / Social Engineering | `02-Investigation-Response/01-phishing.md` | draft |
| Investigation & Response | IC-02 Business Email Compromise | `02-Investigation-Response/02-bec.md` | draft |
| Investigation & Response | IC-03 Ransomware & Digital Extortion | `02-Investigation-Response/03-ransomware.md` | draft |
| Investigation & Response | IC-04 Denial of Service | `02-Investigation-Response/04-dos.md` | draft |
| Investigation & Response | IC-05 Commodity Malware / Loader | `02-Investigation-Response/05-commodity_malware.md` | draft |
| Investigation & Response | IC-06 Identity & Credential Attack | `02-Investigation-Response/06-identity_credential_attack.md` | draft |
| Investigation & Response | IC-07 Web App Exploitation | `02-Investigation-Response/07-web_app_exploitation.md` | draft |
| Investigation & Response | IC-08 Infrastructure Compromise | `02-Investigation-Response/08-infrastructure_compromise.md` | draft |
| Investigation & Response | IC-09 Insider Threat & Privilege Misuse | `02-Investigation-Response/09-insider_threat.md` | draft |
| Investigation & Response | IC-10 Supply-Chain Compromise | `02-Investigation-Response/10-supply_chain.md` | draft |
| Investigation & Response | IC-11 Data Breach / Exfiltration | `02-Investigation-Response/11-data_breach_exfiltration.md` | draft |
| Investigation & Response | IC-12 Resource Hijacking / Cryptojacking | `02-Investigation-Response/12-resource_hijacking.md` | draft |
| Investigation & Response | IC-13 Destructive / Wiper Attack | `02-Investigation-Response/13-destructive_wiper.md` | draft |
| Investigation & Response | IC-14 OT/ICS Attack | `02-Investigation-Response/14-ot_ics.md` | draft |
| Investigation & Response | IC-15 AI/ML System Attack | `02-Investigation-Response/15-ai_ml_system.md` | draft |
| Investigation & Response | Catch-all (any category) | `02-Investigation-Response/00-generic.md` | draft |

## 7. Execution by Any Executor

The playbooks are Markdown read by whoever executes them: a human analyst opens them, automation and agents load them at runtime. The triage playbook classifies the alert and proposes the candidate categories; the front matter of the Investigation & Response playbook (`incident_category`, `mitre_ttps`) is the deterministic selection key; `required_data_sources` lets the executor detect a **visibility gap** before running. When a required data source is unavailable, the executor MUST record the gap in the Note's Visibility Gaps element ([Detection & Analysis §1.6](../03-Processes/02-detection_and_analysis.md#16-triage-note), [§2.5](../03-Processes/02-detection_and_analysis.md#25-investigation-note-verdict-evidence-record)) and MUST cap `confidence_id` at Medium (2): a verdict reached without the telemetry the playbook requires is never High. Queries are stated as questions; the executor translates them to the query language of its tools, so no playbook carries product-specific query code. Response actions run under the autonomy matrix and the [Agentic Guardrails](../07-Governance/agentic_guardrails.md).

## 8. References

*   NIST SP 800-61 Rev. 3; MITRE ATT&CK and ATLAS; OCSF.
*   [Alert Type taxonomy](../02-Taxonomy/alert_types.md), [Incident Categories](../02-Taxonomy/incident_categories.md), [Case Schema](../02-Taxonomy/case_schema.md), [Detection & Analysis](../03-Processes/02-detection_and_analysis.md), [Incident Response](../03-Processes/03-response.md), [Agentic Guardrails](../07-Governance/agentic_guardrails.md).
