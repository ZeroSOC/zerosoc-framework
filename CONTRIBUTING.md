---
title: ZeroSOC Framework Contributing Guidelines
type: policy
status: development
last_updated: 2026-09-10
license: Apache-2.0
---

# Contributing to the ZeroSOC Framework

Thank you for your interest in contributing. The ZeroSOC Framework is an open standard for security operations, maintained by practitioners: analysts, detection engineers, threat hunters, platform engineers and the people who build automation and agents for the SOC. Contributions keep its taxonomies, processes, playbooks and metrics accurate and usable.

## 1. Principles every contribution follows

The [Framework Manifest](01-Foundation/framework_manifest.md) states the principles; the three that shape most reviews are:

1. **Executor neutrality.** Every process step and playbook action is performed the same way by a human analyst, deterministic automation or an agent. A rule that ends in "escalate to a human when in doubt" is not a rule: name the action.
2. **Human readability.** Field names, enumerations and tags are additive; the prose stays clear enough for an analyst to execute the document on a bad night.
3. **Vendor neutrality.** No product or vendor names in normative text; no product-specific query code. Queries are questions; the executor translates them. External standards and sources are credited once, in the [Design Decisions](01-Foundation/design_decisions.md) registry or a document's sources section.

## 2. What the framework builds on

*   **Schema.** Cases, Alerts and their fields are the OCSF classes and attributes recorded in the [Case Schema](02-Taxonomy/case_schema.md); new fields are proposed there, never defined in a process or playbook.
*   **Vocabulary.** Terms are defined once in [Definitions](01-Foundation/definitions.md). Alerts are organized by **Alert Type** and telemetry domain; Incidents by **Incident Category** (`IC-##`). Findings carry a side and a confidence — `Malicious (Low|Medium|High)` or `Benign (Low|Medium|High)` — as defined in [Detection & Analysis §2.4](03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence).
*   **Techniques.** ATT&CK and ATLAS techniques are written `ID (Name)`, e.g. `T1566.001 (Spearphishing Attachment)`, and are indicative: an Incident Category is decided by the adversary's objective, not by technique lookup.
*   **Evidence.** Like ATT&CK, the framework documents behaviors observed in the wild. A new Alert Type, Incident Category or playbook cites public reporting that shows the behavior.
*   **Standards.** The exact versions of the standards the framework aligns to are registered in the [README](README.md#standard-alignment).

## 3. Contribution areas

1. **Playbooks** ([Playbook Architecture](04-Playbooks/playbook_architecture.md) is the normative structure):
   *   **Triage playbooks** (`04-Playbooks/01-Triage/`), by telemetry domain: per alert type, the entities to enrich, the **checks** and what each result is evidence of (tagged), the **False Positive conditions** (the detection misfires) kept apart from the **Benign conditions** (authorized activity), and the candidate categories.
   *   **Investigation & Response playbooks** (`04-Playbooks/02-Investigation-Response/`), by Incident Category: the Malicious and Benign hypotheses; validation queries that state **both outcomes** in the finding tags, including at least one query that yields the `Benign (High)` finding explaining the alerts; containment, eradication and recovery with approval-tier actions marked per [Incident Response §2.1](03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment); completion criteria and critical failures.
   *   **Shared enrichment** (`04-Playbooks/99-Shared/`): per-entity enrichment content with a Produces block.
2. **Taxonomies and vocabulary:** new Alert Types, refinements to Incident Categories, terms in Definitions.
3. **Processes and metrics:** the lifecycle phases, the evidence model, the [Operational Metrics](05-Metrics/operational_metrics.md).
4. **Governance:** the [Agentic Guardrails](07-Governance/agentic_guardrails.md) and [Agentic Supervision](07-Governance/agentic_supervision.md).
5. **Deliverables:** the Note templates and their worked examples in [06-Deliverables](06-Deliverables/README.md).

## 4. How to contribute

### Step 1 — Open an issue (substantive changes)

Open an issue in this repository before writing a substantive change (new or changed normative content), so that scope is agreed first; editorial fixes go straight to a pull request. Questions and ideas that are not yet actionable go to GitHub Discussions where enabled, otherwise to an issue.

> **Public repository.** Never include proprietary, commercial or customer-sensitive details in issues, discussions or pull requests.

### Step 2 — Write

*   Clone the repository and create a branch.
*   Every Markdown document starts with YAML frontmatter: `title`, `type`, `status`, `last_updated`, `license` (`status` is exempt for `type: index` and `type: log`). A new document starts as `draft`.
*   Playbooks are copied from the templates (`_TEMPLATE.md` in each playbook directory) and keep their mandatory sections in order.
*   Structural changes — schema elements, identifiers, module layout, terminology — include a Design Decision entry in the [registry](01-Foundation/design_decisions.md); identifiers are never reused.
*   Add an entry to [CHANGELOG.md](CHANGELOG.md) under *Unreleased*.

### Step 3 — Verify

*   Walk the change through as an executor would: a tabletop run of a playbook, an end-to-end read of a process change. Outputs of a playbook map to the [Triage Note and Investigation Note](06-Deliverables/README.md).
*   Check that every cross-document link and anchor resolves and that the frontmatter validates; the repository checks (markdownlint, link check, frontmatter validation) run on every pull request.

### Step 4 — Sign off your commits (DCO)

There is no Contributor License Agreement. Contributions are certified under the [Developer Certificate of Origin](https://developercertificate.org/): every commit carries a `Signed-off-by` line, added with `git commit -s`, stating that you have the right to submit the work under the Apache License 2.0.

```bash
git commit -s -m "docs: add the consent-grant check to the identity triage playbook"
```

### Step 5 — Open a pull request

*   Open the pull request against `main`, describe the change and link the issue it implements.
*   The pull request template lists the checks a reviewer expects; the repository checks must pass.
*   Decisions on merging follow [GOVERNANCE.md](GOVERNANCE.md).

## 5. Licensing and trademarks

*   **License.** The framework is licensed under the [Apache License 2.0](LICENSE); inbound contributions are outbound under the same terms (Apache License §5).
*   **Trademarks.** The "ZeroSOC" name and logos are governed by [TRADEMARKS.md](TRADEMARKS.md); contributing content does not grant rights to the mark.
