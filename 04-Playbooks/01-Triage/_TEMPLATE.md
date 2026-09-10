---
title: <Domain> Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: <Endpoint | Identity | Network | Cloud | Email | Data | Application | OT/ICS>
required_data_sources:
  - <telemetry source>
status: draft
---

# <Domain> Triage Playbook

Triage knowledge for **<Domain>** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| <alert type> | <log source> | <tactic(s)> | TXXXX (Name) | IC-NN (Name)[, IC-MM (Name)] |

## Per-Alert Triage

### <alert type>

- **Enrich entities:** <the entities in scope, each linked to its enrichment sub-playbook in [99-Shared/](../99-Shared/)>.
- **Checks:** <numbered; each states the question and what its result is evidence of — `Malicious (Low|Medium|High)` when ..., `Benign (Low|Medium|High)` when ...; a result that bears on neither side is context>.
- **False Positive conditions:** <activity that is not what the detection looks for, yet triggers it — a heuristic misfire, a parser artifact, a stale rule. Close as False Positive (`verdict_id` 1) with a tuning ticket to Phase 1.>
- **Benign conditions:** <authorized activity that legitimately matches the detection — an approved change, a sanctioned tool, a documented exception. Close as Benign (`verdict_id` 5) with a Knowledge Base entry when the exception is not yet recorded.>
- **Candidate Incident Category(ies):** <IC-NN[, IC-MM]>
