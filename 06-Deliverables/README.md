---
title: Deliverables Module
type: index
last_updated: 2026-09-23
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
- **Event references are mandatory:** every finding cites the specific supporting event(s) — an OCSF finding or event identifier, or a platform event link — never a raw-log dump. The Case keeps those events, not only the reference to them ([Case Schema §3](../02-Taxonomy/case_schema.md#3-findings)); the deliverable cites them and does not reproduce them.
- **The Alerts carry what their detection asserted** ([Detection & Analysis §1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment)): the technique identifiers, the threat name and family, the detection source and detector, and the remediation state of each entity the Alert names. The source's **recommended actions** are indicative: one the executor ran renders as the Finding it produced, naming the recommendation it came from, and one it did not run renders nowhere. An assertion the source did not supply is a Visibility Gap like any other.
- **Technique notation:** ATT&CK and ATLAS codes SHOULD be written as `ID (Name)` (e.g. `T1567 (Exfiltration Over Web Service)`).
- Notes are specific and concise: findings in accurate terms, evidence summarized — summarized in the deliverable, kept on the Case.
