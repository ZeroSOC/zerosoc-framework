---
title: Framework Manifest
type: concept
status: development
last_updated: 2026-08-17
license: Apache-2.0
---

# ZeroSOC Framework Manifest

## Strategic Mandate

The ZeroSOC Framework is an authoritative, vendor-independent body of knowledge defining security operations standards for the era of autonomous security operations — where human analysts, deterministic automation, and AI agents share the same processes. It explicitly separates abstract standard definitions from platform-specific reference runtimes, providing a highly technical architectural standard for modern SOC environments. 

Indeed, a core objective of this framework is to provide a solid foundation for trustworthy and grounded autonomous SecOps models.

## The Concept

The ZeroSOC Framework ambitionally aims to become the definitive standard for Security Operations. Instead of relying on disparate, vendor-specific playbooks and siloed definitions, ZeroSOC provides an open, extensible baseline for reasoning, investigating, and responding to cyber threats. 

This framework is built to guide **human analysts**, **deterministic automation**, and **autonomous AI agents** alike, ensuring consistent, mathematically precise, and auditable outcomes regardless of the underlying detection tooling, automation platform or AI model.

### Executor Neutrality and Human Readability

The Framework is independent along **two axes**:
*   **Technology Neutrality:** No process or playbook depends on a specific vendor, product, or query language.
*   **Executor Neutrality:** Every process and playbook is authored to be executable by any qualified executor — a human analyst, deterministic automation (such as SOAR scripts), an autonomous AI agent, or any blend of the three — demanding the same analytical rigor, evidence standards, and deliverables regardless of who or what performs the work.

While the framework's **specifications are executor-neutral**, its **operational guidance recognizes executor fitness**:
*   **Deterministic Automation:** Best suited for high-volume, repetitive, fully-specifiable tasks (lowest cost, predictable latency).
*   **AI Agents:** Best suited for contextual correlation, hypothesis testing, and reasoning under uncertainty.
*   **Human Analysts:** Essential for handling ambiguity, high-blast-radius decisions, and ultimate accountability.

Human readability and actionability are therefore **conformance properties**, not documentation courtesies. They are necessary for transparency, auditability, and to guarantee that a human always understands exactly what an autonomous agent will do. As Andrej Karpathy noted, *"You can outsource thinking, but you cannot outsource understanding."* Enforcing human-readable playbooks ensures that even as execution is automated, the human retainers of the system retain full comprehension and governance over the agent's behavior. Consequently, agent-facing affordances — front-matter selection keys, OCSF enum anchors, machine-readable handoff contracts — are additive and MUST NOT make the prose less readable or less actionable for a human executor. Where a capability is impractical for a human executor (e.g. bulk parallel queries), the documents state the *what* and the *why* so a human achieves the same outcome sequentially.

### Scope & Boundaries

ZeroSOC's scope is the **operational plane** of security — the run-time work of detecting, triaging, investigating, hunting, responding, recovering, validating controls, and monitoring and enforcing safeguards. This plane cuts *across* the NIST CSF 2.0 functions (see [Standard Alignment](#standard-alignment) below) rather than owning any of them whole:

*   **Identify:** the operational slice only — exposure discovery, vulnerability *triage* and prioritization, threat intelligence, and asset context. The strategic risk-assessment program sits outside.
*   **Protect:** the operational slice only — control monitoring, control validation, log-management operations, and identity threat detection and enforcement. **Building or deploying** safeguards (IAM architecture, network segmentation, encryption, awareness training) sits outside.
*   **Detect, Respond, Recover:** owned nearly in full — these functions are inherently operational.
*   **Govern:** a thin operational thread only — operational roles and the metrics that feed oversight. Setting risk appetite, policy, and strategy sits outside.

The dividing line is **operate (in scope) vs. build and govern (out of scope)**. The framework *interfaces* with the excluded work — handing validated remediation tasks to the IT owners who execute them, consuming risk strategy from governance — but does not define it. Even at full maturity, ZeroSOC is a **Security Operations** standard, not an enterprise security-program standard.

Coverage is built in deliberate order. Today the normative modules concentrate on **Detect, Respond, and Recover** (grounded by the Preparation & Engineering process and the Governance module); extension into the operational edges of **Identify** and **Protect** — proactive hunting, threat intelligence, exposure management, and vulnerability triage — is committed but staged on the [Roadmap](roadmap.md), which sequences and prioritizes it. The manifest states the scope; the roadmap is the vehicle that reaches it.

## Versioning & Document Release Status

Adopters cannot claim conformance against a moving repository, and readers cannot tell a settled standard from a working candidate unless the document says so. ZeroSOC therefore versions at two levels — a pattern common to mature open standards (OWASP ASVS, OCSF, OpenTelemetry semantic conventions): **framework releases** for the standard as a whole, and a **release status** on every document.

### Framework Releases

*   The framework is released as tagged **Semantic Versioning (MAJOR.MINOR.PATCH)** snapshots (e.g. `v0.1.0`, `v1.0.0`). A release tag is the citable conformance target: adopters conform to "ZeroSOC vX.Y" (or an exact snapshot `vX.Y.Z`), never to the live repository.
*   **MAJOR (`X.0.0`)**: Breaking changes to `stable` content — renumbered identifiers, removed sections, changed normative schemas or lifecycle requirements.
*   **MINOR (`X.Y.0`)**: Additive, backwards-compatible extensions — new domain triage playbooks, additional Incident Categories, or expanded metrics.
*   **PATCH (`X.Y.Z`)**: Non-normative errata, typo corrections, link fixes, and editorial clarifications.
*   The chronological ledger ([log.md](../log.md)) doubles as the changelog; each release adds a release entry summarizing changes since the previous tag.
*   Until `v1.0.0` the framework is in the `0.x` series: stability guarantees are best-effort, and `development` is the default status for active normative content.

### Document Release Status

Every framework document declares a `status` field in its YAML frontmatter, alongside `title`, `type`, `last_updated`, and `license` (per [DD-15](design_decisions.md#dd-15-apache-20-licensing-and-contribution-governance)). Exceptions: documents of `type: index` or `type: log`, and everything under `raw/` — navigational and ledger artifacts have no release maturity. `last_updated` remains the per-document **revision** identifier (it is the version recorded in Note provenance); `status` states **maturity**, not revision.

| Status | Meaning | Guarantees |
|---|---|---|
| `draft` | Exploratory. Shape, scope, or existence may change without notice. | None. MUST NOT be cited as a conformance target; RFC-2119 keywords carry no obligation. |
| `development` | Content-complete candidate undergoing validation (flow-tests, tabletop exercises, adopter feedback). The default state for new normative content. | Structure and intent are settled; details may change between MINOR releases. Feedback is explicitly invited. |
| `stable` | Normative. Validated, cross-linked, part of the conformance surface. | RFC-2119 keywords are binding. Identifiers, section anchors, and normative requirements change only at a MAJOR release. |
| `deprecated` | Superseded or withdrawn; retained for the record. | The frontmatter MUST name the successor document (or state that none exists). New content never cites a deprecated document. |

### Promotion & Demotion

*   **Transitions are governance events.** Every status change is recorded in [log.md](../log.md) with its rationale; a promotion that settles a contested design choice also warrants a [design decision](design_decisions.md) entry.
*   **Promotion to `stable` requires, at minimum:** (a) validation by a flow-test, tabletop exercise, or equivalent check against real material; (b) complete cross-links with no dangling references; (c) one review pass by an executor other than the author — human or agent, per Executor Neutrality; (d) all normative dependencies declared at `stable` status.
*   **Demotion is legitimate.** A `stable` document invalidated by new insight returns to `development` with a log entry. Honesty over face-saving.

## Standard Alignment

The ZeroSOC Framework doesn't reinvent the wheel. It acts as an integration and orchestration layer on top of the industry's most trusted standards. The exact versions ZeroSOC is currently built upon are recorded in the [Standard Alignment registry](../README.md#standard-alignment) in the framework README.

### 1. Strategic Governance (NIST CSF)
NIST CSF 2.0 provides the strategic foundation (Govern, Identify, Protect, Detect, Respond, Recover). ZeroSOC aligns its operational phases directly to these functions to ensure that security operations are treated as an integrated component of corporate risk management.

### 2. Tactical Incident Handling (NIST SP 800-61)
NIST SP 800-61 Rev. 3 acts as the operational profile for the framework. Instead of a standalone lifecycle, it serves as a CSF 2.0 Community Profile. ZeroSOC’s containment, eradication, recovery, and post-incident playbooks are mapped directly to the tactical recommendations of SP 800-61 Rev. 3.

### 3. International Process Governance (ISO/IEC 27035 & ISO/IEC 27001)
To ensure alignment with global enterprise environments, ZeroSOC maps its operational processes to the five-phase model of ISO/IEC 27035 (Plan/Prepare, Detect/Report, Assess/Decide, Respond, Learn). This mapping serves as the authoritative incident management baseline supporting the broader Information Security Management System (ISMS) controls defined in ISO/IEC 27001:2022 (specifically control A.5.24 - A.5.28).

### 4. Data Schema (OCSF)
To govern autonomous agents, a mathematically precise lexicon is required. The framework mandates adherence to the Open Cybersecurity Schema Framework (OCSF) for state normalization, ensuring that "Alerts" (Detection Findings) and "Incidents" (Incident Findings) are universally understood.

### 5. Threat Tactics & Techniques (MITRE ATT&CK®)
While the ZeroSOC Taxonomy abstracts incidents based on simplified categories, MITRE ATT&CK remains the foundational framework for mapping specific adversary behaviours and exploitation vectors and executing hypothesis validation queries during triage.

### 6. Regulatory Auditing (NIS2 & DORA)
With the rise of Agentic MDR platforms, autonomous actions must be transparent, auditable, and compliant with European reporting timelines:
*   **Early Warning (24 Hours):** Automated flagging of potential systemic or cross-border impact to trigger the initial 24-hour notification gate under NIS2 (Article 23) or DORA.
*   **Incident Notification (72 Hours):** Verification workflows to populate and submit detailed incident reports within the 72-hour window.
*   **"Glass Box" Auditing:** The framework's Governance module mandates "Glass Box" design patterns to satisfy the strict reporting and auditing requirements of EU directives like NIS2 and DORA.
