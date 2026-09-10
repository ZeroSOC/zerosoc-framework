---
title: ZeroSOC Framework Roadmap
type: strategy
status: development
last_updated: 2026-09-07
license: Apache-2.0
---

# ZeroSOC Framework Roadmap

This roadmap bridges where the ZeroSOC Framework is **today** and where the [Framework Manifest](framework_manifest.md) points it: a vendor-neutral, precise and measurable standard for autonomous **Security Operations** — the *operational plane* of security, which cuts across the NIST CSF 2.0 functions without owning any of them whole (see the manifest's [Scope & Boundaries](framework_manifest.md#scope--boundaries)).

Today the framework's normative modules concentrate on **Detect, Respond, and Recover** (plus Preparation & Engineering). This roadmap is the vehicle that carries the standard toward the rest of that operational scope — hardening and measuring that core, then extending into the **operational edges of Identify and Protect** (proactive hunting, threat intelligence, exposure discovery, vulnerability triage), while leaving safeguard engineering and governance to the functions that own them.

It is deliberately **not** a dated list of modules to ship. It is written as a set of **bets**: the critical problems we choose to solve, each framed as an outcome to reach rather than a feature to build. The [Ideas & Exploration Backlog](#ideas--exploration-backlog) below is where everything else lives — parked on purpose, because the essence of a roadmap is choosing what *not* to do next.

## How to read this

- **Objectives, not deliverables.** Each item states the *problem* and the *outcome* we want. The proposed module is a **candidate** — a bet on how to get there — not a locked commitment. Candidates must be validated before they become normative parts of the standard.
- **Outcomes are measurable.** Where an objective extends an existing document, it names the result expected there, so success is judged by whether the framework actually moved the needle, not by whether a file shipped.
- **Priorities are transparent.** You do not have to agree with the ordering, but the *why* is stated so the chosen path is legible. P1 is the most urgent; higher numbers are committed but later.
- **Sequencing follows dependencies.** The detection bets form a deliberate spine — **hunt → engineer → assure**: you cannot continuously validate detections you have not yet engineered, and engineering is best fed by what hunting surfaces.
- **Bets can be wrong.** Discovery is not an exact science. The ordering reflects current insight from adopters, the existing modules, and the SecOps landscape — and is expected to change as we learn.

---

## The Roadmap

### P1 — Metrics & Maturity

**Problem.** The metrics and maturity layer is at an early stage. [05-Metrics](../05-Metrics/operational_metrics.md) captures *speed* (MTTD/MTTI/MTTC/MTTR) and *detection quality* (FPR, precision, coverage), but the framework cannot yet answer two questions adopters keep asking: **"Is autonomous SecOps economically efficient?"** and **"How mature are we, and what should we build next?"** Measurement comes first because it is how every other bet on this roadmap is judged.

**Outcome we want.** Adopters can measure the *economics* of autonomous SecOps alongside its speed and quality, and can see a staged, benchmarkable path from their current state toward a mature target state.

**Key results.**
- Four new economic metrics are defined in [05-Metrics](../05-Metrics/operational_metrics.md) with the same numerator/denominator rigor as MTTC (including explicit boundary rules):
  - **Token cost per alert** and **token cost per case** — the compute economics of triage and investigation.
  - **Token cost per protected identity** and **token cost per protected endpoint** — the economics of coverage at scale.

**Candidate bets.** Extend 05-Metrics with the token-economics metrics above; add a self-assessment maturity layer sitting on top of the existing modules and playbooks.

### P2 — Proactive Threat Hunting

**Problem.** The Malicious/Benign hypothesis engine is a reactive, post-alert construct. There is no standardized way to hunt *before* an alert fires — to look for adversary activity that no rule caught — and the coverage gaps such hunting reveals are exactly what should drive detection engineering downstream.

**Outcome we want.** Hypothesis-driven hunting is a first-class, pre-alert workflow that both catches what detection missed and continuously feeds the detection pipeline with new requirements.

**Candidate bet.** A *Proactive Hunting* module that reuses the existing Malicious/Benign hypothesis engine (smallest lift of the proactive bets) and outputs structured coverage gaps.

### P3 — Detection Engineering & Detection-as-Code

**Problem.** The framework describes detection requirements in prose. There is no standardized way to express, source, and version detection logic — and *replicating* an existing detection library would be wasteful and would fight the open ecosystem instead of building on it.

**Outcome we want.** Detection requirements are codified and version-controlled (detection-as-code), and detection content is **sourced by reference** from existing open libraries rather than re-created inside the framework.

**Key results.**
- Detection logic is expressed as code and versioned, consistent with the "no rigid vendor queries" principle in [playbook_architecture §7](../04-Playbooks/playbook_architecture.md).
- Each [Alert Type](../02-Taxonomy/alert_types.md) references detection content in an external library — **[SIGMA](https://github.com/SigmaHQ/sigma)** and others — rather than a bespoke, framework-owned rule.
- The loop with Phase-2 false-positive tuning tickets (raised during Triage and Investigation in [Detection & Analysis](../03-Processes/02-detection_and_analysis.md)) is closed: tuning feedback, and the gaps surfaced by hunting (P2), flow back into catalog updates.

**Candidate bet.** A *Detection-Rule Catalog* layer — a Phase-1 companion to the Alert Type taxonomy that, per alert type, states vendor-neutral detection requirements and telemetry preconditions and links out to referenced SIGMA (and other) content, with detection-as-code conventions for versioning it.

### P4 — Threat-Intelligence Lifecycle

**Problem.** There is no standard for how threat intelligence enters, ages, and expires, nor for how it feeds the rest of the pipeline.

**Outcome we want.** A defined lifecycle for IOC intake, aging, and expiry, with clear paths into triage enrichment and hunt-hypothesis generation — governed by the boundaries the framework already sets.

**Key results.**
- Intelligence feeds both Triage enrichment ([Detection & Analysis §1.2](../03-Processes/02-detection_and_analysis.md)) and hunt-hypothesis generation ([§4.2](../03-Processes/02-detection_and_analysis.md)), reinforcing the Proactive Hunting bet (P2).
- Intake and use of external intelligence remains governed by the existing [Data-Handling & OSINT Egress Boundaries](../07-Governance/agentic_guardrails.md).

**Candidate bet.** A *Threat-Intelligence Lifecycle* module.

### P5 — Detection Assurance

**Problem.** The framework asserts "continuous validation" as an aspiration, but there is no repeatable, automatable way to prove that a playbook — whichever executor runs it — still triages, investigates and responds as it claims after a change. Detection efficacy drifts silently, and a change to one playbook can quietly break another. Assurance is fundamental — but it can only be built once there are engineered detections (P3) to validate and hunting (P2) to reveal what coverage should exist.

**Outcome we want.** Playbooks and agents are validated the same way software is — every change is gated by an executable test, and detection efficacy is *demonstrated* against real adversary behavior rather than mapped on paper.

**Key results.**
- Detection efficacy is proven continuously through adversary emulation, defining **Measured Recall** — techniques that raised an Alert over techniques exercised per emulation campaign, aggregated over a rolling 90-day window as demonstrated ATT&CK coverage — the known-denominator complement of the Observed Detection Recall in [05-Metrics](../05-Metrics/operational_metrics.md).

**Candidate bet.** A *Simulation & Validation* layer: standardized per-playbook test fixtures plus adversary-emulation hooks wired into **[Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)** (and Breach-and-Attack-Simulation tooling) so playbooks and agents are unit-tested on every change. This turns "continuous validation" from an aspiration into a check that runs against every playbook edit.

### P6 — Exposure Management (CTEM + Vulnerability Management)

**Problem.** With the detection core hardened, measured, and assured, the standard's biggest remaining gap is the **operational edge of Identify**: proactively mapping exposure and triaging the vulnerabilities that feed detection and response. The framework does the operational work — discover, prioritize, validate, hand off — while the actual remediation (patching, hardening) stays with the IT/Protect owners it mobilizes.

**Outcome we want.** The standard extends from reactive detection into proactive exposure reduction, so adopters can prioritize and mobilize remediation *before* an incident, using the same taxonomy and metrics that govern the reactive core — without taking ownership of the safeguard engineering itself.

**Key results.**
- A **Continuous Threat Exposure Management (CTEM)** module standardizes the operational exposure loop: scoping & discovery of the attack surface (external, internal, identity, SaaS), exposure-severity assessment beyond CVSS base scores, prioritization via the [Incident Taxonomy](../02-Taxonomy/incident_categories.md), Red Team / BAS validation of exploitability (reusing the P5 assurance hooks), and agentic **mobilization** — routing validated remediation tasks to the IT owners who execute them.

**Candidate bets.** A CTEM module and a Vulnerability Management standard, developed together as the framework's move into the operational edge of Identify. Their validation stage reuses the adversary-emulation hooks built in P5, and their remediation output hands off at the Protect boundary rather than crossing it.

---

## Ideas & Exploration Backlog

These are **ideas, not commitments** — deliberately *not* on the roadmap so the bets above keep our focus. They are recorded here so the thinking is not lost and so adopters understand the intended direction of travel. Any one of them may be promoted to a roadmap bet as insight and demand accumulate; several already have natural pull toward the objectives above.

- **Entity Risk Scoring:** a decaying, per-entity risk aggregate over Signals and Alerts, aligned to the OCSF `risk_score` object, feeding Triage prioritization alongside Severity and Confidence (hinted at in [Detection & Analysis §1.4](../03-Processes/02-detection_and_analysis.md)).
- **Cross-IC Campaign Scenarios:** thin scenario overlays chaining multiple Incident Category playbooks along common kill chains (e.g. phishing → BEC → exfiltration), referencing — never duplicating — the underlying playbooks.
- **Per-Playbook Efficacy Metrics:** per-playbook MTTC/MTTR, verdict-overturn rate at QA sampling, and HITL-modification rate — a natural feeder for the **Metrics & Maturity (P1)** objective once that work matures.
- **Machine-Readable Integration Contract:** JSON Schemas freezing playbook frontmatter, the [§5 Phase Transition Contracts](../04-Playbooks/playbook_architecture.md), and Triage/Investigation Note structures — versioning the "markdown-as-interface" promise under explicit control.
- **Deferred metrics:** the measures kept out of [05-Metrics](../05-Metrics/operational_metrics.md) until the program they need exists — Measured Recall and demonstrated ATT&CK coverage (adversary emulation, P5), Hunt Yield (P2), a Re-classification Rate as a taxonomy diagnostic, and coverage economics (token cost per protected endpoint or identity) once enough baselines exist to compare.
- **Phase 3 and Phase 4 deliverable templates:** an Incident Record (containment-verification evidence) and a Post-Incident Review report, alongside the Triage Note and Investigation Note in [06-Deliverables](../06-Deliverables/README.md). Deferred by decision: the first release standardizes the Phase 2 deliverables only.
- **Regulatory Communications playbooks:** notification decision trees and report skeletons keyed to the NIS2/DORA gates in [Incident Response §6](../03-Processes/03-response.md), extended to GDPR breach notification. The notification *triggers, timelines, and gates* already exist in the response process and Governance's Glass Box auditing; this idea would add only the human-owned communications templates on top.

---

## Governance of Extensions

Every roadmap bet and backlog idea, if promoted into the standard, adheres to the ZeroSOC core philosophy:

- **Vendor Agnostic:** focus on the process, not the tool.
- **Precise and Measurable:** define clear metrics and states.
- **Executor-Neutral:** every workflow is executable by a human analyst, deterministic automation, or an autonomous AI agent alike, per the [Framework Manifest](framework_manifest.md#executor-neutrality-and-human-readability).
