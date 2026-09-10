---
title: Deliverables Module
type: index
last_updated: 2026-09-10
license: Apache-2.0
---

# 06-Deliverables

Fill-in **templates** and **worked examples** for the framework's written deliverables. The element lists are canonical in [Detection & Analysis §1.6 and §2.5](../03-Processes/02-detection_and_analysis.md); this module holds the practitioner-facing forms and one worked example each. Per the [Executor Neutrality principle](../01-Foundation/framework_manifest.md#executor-neutrality-and-human-readability), the same template is used whether the deliverable is produced by a human analyst, automation or an agent.

The Notes are the records the framework reviews: QA sampling ([Agentic Supervision §2](../07-Governance/agentic_supervision.md)) and the Post-Incident Review ([Phase 4](../03-Processes/04-post_incident_activity.md)) read the Notes, not execution transcripts. Phase 3 and Phase 4 have no separate deliverable in this release: the [Case](../02-Taxonomy/case_schema.md), with its timeline and these Notes, is the record of an Incident ([Incident Response §5](../03-Processes/03-response.md#5-transition-to-phase-4)); an Incident Record and a Post-Incident Review report are staged on the [Roadmap](../01-Foundation/roadmap.md).

## Contents

- [Triage Note](triage_note.md) — template and worked example: the decision record of Triage.
- [Investigation Note](investigation_note.md) — template and worked example: the verdict evidence record of Investigation, including the **Case Timeline**, whose earliest confirmed malicious event is the Case's T0.

## Conventions

- **Naming:** `<type>_<case-id>_<YYYYMMDD-HHMM>` (e.g. `triage_note_CASE-4711_20260914-1512`).
- **Every finding carries its side and confidence** — `Malicious (Low|Medium|High)`, `Benign (Low|Medium|High)` — or is marked context ([Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence)). The alerts are the first findings.
- **Provenance is mandatory** in every deliverable: the playbook(s) used (path plus `last_updated` as version), the executor (human / automation / agent, all classes that contributed), the capability classes invoked, and the Case identifier — the audit trail the [Agentic Guardrails](../07-Governance/agentic_guardrails.md) require.
- **Event references are mandatory:** every finding cites the specific supporting event(s) — an OCSF finding or event identifier, or a platform event link — never a raw-log dump.
- **Technique notation:** ATT&CK and ATLAS codes are written as `ID (Name)` (e.g. `T1567 (Exfiltration Over Web Service)`), never bare codes.
- Notes are specific and concise: findings in accurate terms, evidence summarized.
