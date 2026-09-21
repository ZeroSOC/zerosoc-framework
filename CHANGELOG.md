---
title: Changelog
type: log
last_updated: 2026-09-20
license: Apache-2.0
---

# Changelog

All notable changes to the ZeroSOC Framework are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the framework versions per [Semantic Versioning](https://semver.org/spec/v2.0.0.html) as described in [GOVERNANCE.md](GOVERNANCE.md#5-releases). Each release entry credits the contributors whose work landed in it.

## [Unreleased]

### Changed

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
