---
title: Changelog
type: log
last_updated: 2026-09-10
license: Apache-2.0
---

# Changelog

All notable changes to the ZeroSOC Framework are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the framework versions per [Semantic Versioning](https://semver.org/spec/v2.0.0.html) as described in the [Framework Manifest](01-Foundation/framework_manifest.md#versioning--document-release-status). Each release entry credits the contributors whose work landed in it.

## [Unreleased]

### Added

- **01-Foundation:** Framework Manifest, Definitions (including the classification levels for severity, confidence and impact, the executors and functions of the tier-less model, and the SOC Knowledge Base), Design Decisions registry, Roadmap.
- **02-Taxonomy:** Incident Categories (IC-01 to IC-15), Alert Types by telemetry domain, the Case Schema with its JSON Schema.
- **03-Processes:** Detection & Response Lifecycle; Preparation & Engineering (draft); Detection & Analysis with the evidence model — findings tagged by side and confidence, triage close by coverage, verify-or-retract investigation, verdict and confidence by score; Incident Response with the containment autonomy matrix; Post-Incident Activity.
- **04-Playbooks (draft):** Playbook Architecture, Operating Guide, eight domain triage playbooks, sixteen Investigation & Response playbooks and a catch-all, five shared enrichment sub-playbooks.
- **05-Metrics (draft):** nineteen process-anchored volume, speed, quality, autonomy and token-economics metrics with reference bands.
- **06-Deliverables:** Triage Note and Investigation Note templates with worked examples.
- **07-Governance (draft):** Agentic Guardrails and Agentic Supervision.
- Community and project files: Contributing guidelines, Governance, Security policy, Code of Conduct, Trademarks, continuous checks (markdownlint, link check, frontmatter validation, DCO).

[Unreleased]: https://github.com/ZeroSOC/zerosoc-framework/commits/main
