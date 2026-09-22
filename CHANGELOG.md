---
title: Changelog
type: log
last_updated: 2026-09-22
license: Apache-2.0
---

# Changelog

All notable changes to the ZeroSOC Framework are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the framework versions per [Semantic Versioning](https://semver.org/spec/v2.0.0.html) as described in [GOVERNANCE.md](GOVERNANCE.md#5-releases). Each release entry credits the contributors whose work landed in it.

## [Unreleased]

### Changed

- **03-Processes:** a Note renders **the account before the measures**. The element order of §1.6
  and §2.5 becomes Summary, Classification, Rationale, Findings (then Re-classification Pivots in
  §2.5), Case Timeline, Visibility Gaps, Provenance — what happened, what was decided, why, then
  what it rests on. Classification led because it is the block a reader compares between the two
  Notes, which it still is, one element lower; a reader who opens a Note wants to know what
  happened before they are shown a row of identifiers. Observed on a Note rendered into a source's
  own console, where the first thing an analyst met was five `severity_id`-shaped facts about a
  Case they had not yet been told about. The elements and what each holds are unchanged, and an
  implementation that reads the order from this section follows it with no change of its own.

- **02-Taxonomy:** the Case Schema declares `ocsf_version`, the OCSF release the mapping follows
  (`1.9.0`). The release was stated in the document's prose and nowhere a program could read it, so
  a Case written into another system's record, exported or archived carried no statement of what it
  was written against. A consumer reading one out of band now has it on the object's own schema.

- **03-Processes, 06-Deliverables:** rendering a technique code as `ID (Name)` in a Note is a **SHOULD**, stated as one. It was written as a flat declarative — "they are written as `ID (Name)` … never bare codes" — with neither MUST nor SHOULD, and an implementation that read it as a conformance condition refused Notes that were correct in every way that bears on the verdict. How a Note spells an identifier is a readability property; whether it is traceable, tagged and decided is not.

- **02-Taxonomy:** the Case Schema states the **per-source extension convention** — one object per source, under the source's own key, its shape declared where that source is described and validated against it; anything the framework already carries is a mapping and not an extension — and **what each phase must leave on the Case**: every check and query as a Finding with its question, request and query, or as a visibility gap naming the check it prevented; the evidence each Finding rests on; every action with its Course of Action; every entity as an observable; the provenance. A question nobody answered is on the Case rather than in silence; reasoning that has no structured form is prose the Case carries — the Summary, a Finding's own description, the Note's rendering, which is a field of the Case and not a record beside it — and bulk telemetry, message bodies and result sets are on it in no form, under no key (DD-26).
- **02-Taxonomy, 03-Processes, 06-Deliverables:** what a detection asserts — techniques, threat name and family, detection source and detector, description, recommended actions, per-entity remediation state — is a required input of triage, mapped to native OCSF carriers and recorded on the Case (DD-24). A Finding's evidence is **kept with the Case** and cited by identifier rather than cited alone, with relevance as the bound: bulk telemetry, result sets, message bodies and file content stay out, and a citation whose referent has expired no longer leaves a Case that cannot show what its verdict rests on (DD-25).

### Added

- **01-Foundation:** Framework Manifest, Definitions (including the classification levels for severity, confidence and impact, the executors and functions of the tier-less model, and the SOC Knowledge Base), Design Decisions registry, Roadmap.
- **02-Taxonomy:** Incident Categories (IC-01 to IC-15), Alert Types by telemetry domain, the Case Schema with its JSON Schema.
- **03-Processes:** Detection & Response Lifecycle; Preparation & Engineering (draft); Detection & Analysis with the evidence model — findings tagged by side and confidence, triage close by coverage, verify-or-retract investigation, verdict and confidence by score; Incident Response with the containment autonomy matrix; Post-Incident Activity.
- **04-Playbooks (draft):** Playbook Architecture, Operating Guide, eight domain triage playbooks, sixteen Investigation & Response playbooks and a catch-all, five shared enrichment sub-playbooks.
- **05-Metrics (draft):** twenty-one process-anchored volume, speed, quality, autonomy and token-economics metrics with reference bands; disposition quality is expressed as precision and recall per gate (Detection, Triage, Verdict).
- **06-Deliverables:** Triage Note and Investigation Note templates with worked examples.
- **07-Governance (draft):** Agentic Guardrails and Agentic Supervision.
- Community and project files: Contributing guidelines, Governance, Security policy, Code of Conduct, Trademarks, continuous checks (markdownlint, link check, frontmatter validation, DCO).

[Unreleased]: https://github.com/ZeroSOC/zerosoc-framework/commits/main
