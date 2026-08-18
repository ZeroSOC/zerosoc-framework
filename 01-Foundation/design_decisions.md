---
title: Design Decisions
type: concept
status: development
last_updated: 2026-08-17
license: Apache-2.0
---

# Design Decisions

A durable, append-only record of the key design decisions behind the ZeroSOC Framework, with the rationale and the alternatives that were weighed. New significant decisions should be appended here.

### Entry Schema
Every entry in this registry follows this structure:
- **`DD-##: <title>`**: Identifier and concise statement of the decision.
- **Decision:** The normative choice made.
- **Rationale:** Technical, operational, or architectural reasoning supporting the decision.
- **Alternatives:** Competing options evaluated and specific reasons for rejection.
- **Cross-links / Revisit trigger:** Connections to affected framework documents and conditions under which the decision should be re-evaluated.

## DD-01: "Alert Type" vs "Incident Category" (intentional terminology asymmetry)
- **Decision:** Alerts are classified by **Alert Type**; incidents are classified by **Incident Category** (`IC-##`). The two use different nouns on purpose.
- **Rationale:** They sit at different altitudes. *Alert types* are granular detection patterns (a data-source-level "type"); *incident categories* are higher-level **business-impact** groupings. Different words signal the different level. "Incident category" is also the established industry term (NIST, CISA, ENISA, FIRST), and "type" is the natural word for detection-level patterns — which is why "Alert **Type**" fits.
- **Alternatives:** Rename to "Incident Type" for surface symmetry with "Alert Type" — rejected: it hides the altitude difference, departs from industry usage, and carries high churn (`IC-##`, `incident_categories.md`, "candidate Incident Categories" are threaded through the framework).

## DD-02: Two-layer playbook architecture (method vs. knowledge)
- **Decision:** Separate the generic phase **methods** (how to triage/investigate/respond — in `03-Processes`) from the specialized **knowledge playbooks** (what — in `04-Playbooks`). Playbooks reference the methods; they do not duplicate them.
- **Rationale:** Avoids duplicating the method across every incident type and the "duplicated logic across type playbooks" anti-pattern. Matches mainstream practice: CISA ships generic process playbooks with specialized ones on top; Elastic attaches per-detection investigation guides; SOAR platforms (XSOAR/Splunk) compose generic sub-playbooks into type-specific parents.
- **Alternatives:** Monolithic per-incident playbooks (duplicative, unmaintainable); a per-phase × per-type file matrix (~45 files — over-fragmentation).

## DD-03: Triage by domain, Investigation & Response by Incident Category
- **Decision:** Triage playbooks are organized by telemetry **domain**; Investigation & Response playbooks are organized by **Incident Category**.
- **Rationale:** Alerts are raised by domain tooling (EDR, IdP, firewall, CASB, email, DLP), so triage enrichment and known-FP conditions are domain-specific. Incidents are the unit of investigation and response. The **domain → Incident Category pivot** happens at the Triage → Investigation handoff.
- **Alternatives:** Everything by Incident Category (forces alerts into IC buckets before classification is known); everything by domain (misfits the response phase, which is incident-centric).

## DD-04: Domain-assignment principle for alert types
- **Decision:** An alert type's **home domain** is the domain of the primary telemetry that raises it and the entity it is about. The Detection Source column lists only sources native to that domain; cross-domain corroboration is enrichment. The same behavior seen from two domains is modeled as two alert types.
- **Rationale:** Keeps the taxonomy unambiguous and prevents a single behavior from sprawling detection sources across domains (e.g., a host tool download is Endpoint/EDR; the perimeter view is a separate Network alert).
- **Alternatives:** List every possible sensor per alert (ambiguous home domain, duplicated rows).

## DD-05: Prioritization = Severity + Confidence
- **Decision:** Prioritize on two orthogonal axes — **Severity** (Informational…Critical, OCSF `severity_id`) and **Confidence** (Low/Medium/High, OCSF `confidence_id`). No separate "priority" axis.
- **Rationale:** Matches leading MDR practice (CrowdStrike, Microsoft, Red Canary, SentinelOne, Expel lead with severity + confidence). "Severity = how bad, Confidence = how sure." An ITIL Impact×Urgency "priority" is redundant because urgency in security is largely intrinsic to the threat/impact.
- **Alternatives:** NIST SP 800-61 three-factor (functional/information/recoverability) — kept only as *inputs* to Severity; ITIL Impact×Urgency priority — redundant with Severity.

## DD-06: Phase model aligned to the incident lifecycle
- **Decision:** Phase 2 is **Detection & Analysis** with **Triage** and **Investigation** sub-phases; Phase 3 is **Incident Response** (Containment/Eradication/Recovery); Post-Incident Activity is process-level (Phase 4), not a per-incident playbook. Phase titles drop the "(NIST 800-61 r3)" suffix (NIST remains cited in body/references).
- **Rationale:** Aligns playbook phase names with the `03-Processes` lifecycle and industry usage (Assign→Triage→Investigate→Respond). "Incident Response" (vs. "Response") emphasizes that only confirmed incidents enter Phase 3.
- **Alternatives:** Keep the legacy "Observation & Triage" / "Response" names — inconsistent with the process module.

## DD-07: OCSF-aligned handoff contract between phases
- **Decision:** Phase boundaries are defined by case/finding fields named per OCSF (Detection Finding / Incident Finding): `severity_id`, `confidence_id`, entities, candidate `incident_category`, `status_id`. A promoted Case carries no verdict at handoff — `verdict_id` remains open until Investigation resolves it (False Positive/Benign on close, True Positive at incident promotion).
- **Rationale:** An explicit handoff contract is the #1 defense against lost context when phases are separated; OCSF is the rapidly-adopted, vendor-neutral interchange schema.
- **Alternatives:** Implicit/prose handoffs (break silently); a bespoke schema (reinvents OCSF).

## DD-08: Concurrent A/B Hypothesis Engine
- **Decision:** Investigation tests two competing hypotheses (A = malicious/TP, B = benign/FP) and seeks evidence that invalidates the competitor, rather than linear if/then branching.
- **Rationale:** Reduces confirmation bias and false positives; mirrors analysis-of-competing-hypotheses and vendor "exploration query" scaffolding.
- **Alternatives:** Linear conditional playbooks (assume malice on alert, drive alert fatigue).

## DD-09: Eight telemetry domains
- **Decision:** Endpoint, Identity, Network, Cloud, Email, Data, Application, OT/ICS. SaaS alerts map to Identity and/or Cloud; Container/Kubernetes maps to Cloud.
- **Rationale:** Mirrors how detection libraries (Elastic, Sentinel, Sigma) organize by data source. Application aligns 1:1 with `IC-07`; OT/ICS with `IC-14`. SaaS/Container are covered by existing domains rather than proliferating domains.
- **Alternatives:** Six domains (undersells the web/app and OT detection classes); a separate SaaS domain (overlaps Identity/Cloud).

## DD-10: `ID (Name)` notation and sub-techniques where precise
- **Decision:** All MITRE and Incident Category references use `ID (Name)` form. Alert types map to a **sub-technique** when specific enough to warrant one (e.g., `T1566.001` Spearphishing Attachment, `T1685.002` Disable or Modify Cloud Log), and to the **parent technique** for deliberately aggregated types. The framework tracks the current MITRE ATT&CK release (v19, April 2026 — which introduced the **Defense Impairment** tactic and technique `T1685`, superseding the former `T1562` Impair Defenses family).
- **Rationale:** Readability and precision without over-fragmenting aggregated alert types.
- **Alternatives:** Bare ids (less readable); always sub-techniques (spurious precision on generic types).

## DD-11: Aggregation level of the alert-type taxonomy
- **Decision:** Keep the alert-type list at a high level of abstraction (~40 aggregated types), not hundreds of near-duplicate detections.
- **Rationale:** The taxonomy is a triage vocabulary, not a detection-rule catalog; excessive granularity would duplicate vendor rule libraries and be unmaintainable.
- **Alternatives:** Exhaustive per-rule enumeration (unmaintainable, low value at the taxonomy layer).

## DD-12: Adopt ideas, not niche standards, as dependencies
- **Decision:** The framework draws on broadly-adopted standards (NIST, MITRE ATT&CK, OCSF, SANS, ISO/IEC 27035) and treats niche frameworks (OASIS CACAO, RE&CT, Atomic Threat Coverage) as sources of ideas only — not tooling dependencies.
- **Rationale:** Longevity and interoperability; avoids betting the standard on low-adoption ecosystems.
- **Alternatives:** Build on CACAO/RE&CT directly — rejected due to low real-world adoption.

## DD-13: Executor neutrality and de-emphasis of branded philosophies
- **Decision:** The framework names **Executor Neutrality** as a manifest principle (processes and playbooks are executable by human, automation, or agent alike) and describes operating-model substance — tier-less peer roles, the even operations/engineering balance, SRE-style toil eradication — without leaning on branded or niche terms such as "Autonomic Security Operations (ASO)" in normative text. Informal sources are credited once, in [Intellectual Influences](#intellectual-influences).
- **Rationale:** An application of DD-12 at the level of concepts: the ideas are load-bearing, the brand names are not; normative text should survive terminology churn.
- **Alternatives:** Keep ASO as the named philosophy (couples the standard to a vendor-coined term); name no principle (leaves executor neutrality implicit and unenforceable).

## DD-14: Cost-telemetry alignment — FOCUS adopted, OTel GenAI provisional
- **Decision:** For the token-economics metrics ([Operational Metrics §7](../05-Metrics/operational_metrics.md)), the normative requirement is stated framework-natively: capture **input and output token counts per model invocation, attributed to the Security Case ID**. The FinOps Foundation **FOCUS v1.2** specification (ratified 2025) is adopted for cost/billing normalization. The **OpenTelemetry GenAI semantic conventions** are adopted **provisionally**, as a SHOULD-level attribute-naming recommendation (`gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`) — not as a conformance dependency — because the spec is formally in *Development* status.
- **Rationale:** DD-12 applied to telemetry, with the two candidates passing the adoption bar differently. FOCUS passes in full: the only open cross-vendor billing-data schema, ratified by the FinOps Foundation, with first-party support in the major cloud billing exports. The OTel GenAI conventions are the only vendor-neutral LLM-telemetry vocabulary and are widely implemented by observability tooling, but the spec is experimental and has already renamed attributes once — hard-coupling conformance to it would import churn. Stating the requirement natively keeps conformance stable while the ecosystem's names converge.
- **Alternatives:** Proprietary telemetry schemas (vendor lock — violates the technology axis of Executor Neutrality); framework-invented attribute names (reinvents the wheel and guarantees divergence from where the ecosystem is converging); waiting for OTel GenAI to stabilize (leaves the four token-economics metrics without a capture recommendation in the interim).
- **Revisit trigger:** when the OTel GenAI semantic conventions reach *Stable*, promote the naming recommendation from SHOULD to MUST and pin the version in the [Standard Alignment registry](../README.md#standard-alignment).

## DD-15: Apache 2.0 licensing and contribution governance
- **Decision:** The entire framework repository is licensed under the **Apache License 2.0** (single license — [LICENSE](../LICENSE), [NOTICE](../NOTICE)). Inbound contributions follow **inbound=outbound** under License §5, with a lightweight **DCO** (`Signed-off-by`) rather than a CLA. Trademark use of the "ZeroSOC" name is governed separately by [TRADEMARKS.md](../TRADEMARKS.md) (License §6 grants no trademark rights). A machine-readable **`license: Apache-2.0`** key is added to the standard YAML front-matter schema so downstream engines and pipelines can parse licensing per file.
- **Rationale:** Although the framework is documentation, Executor Neutrality makes its playbooks *implementable specifications*: agents execute the files verbatim and products redistribute derivatives — the licensing posture of implementable specs (OpenAPI, CloudEvents, OCSF, the OTel specification), which is Apache 2.0, not the CC BY 4.0 of narrative docs. Apache 2.0 uniquely provides: an express **patent grant + retaliation** (§3) covering contributed response *methods* that are performed when a playbook is executed; automatic **inbound=outbound contribution licensing** (§5); mandatory **change-marking on forks** (§4(b)), which protects conformance integrity — divergence cannot masquerade as canonical ZeroSOC; and an explicit **trademark exclusion** (§6) reinforcing the steward policy. It is also congruent with the framework's adopted ecosystems (OCSF per DD-05/DD-07, OTel per DD-14) and allowlisted by default in enterprise legal review.
- **Alternatives:** **CC BY 4.0** (the narrative-docs convention) — explicitly excludes patent rights (§2(b)(2)), awkward to embed in code repositories, and gains nothing over Apache §4's equally mandatory attribution; **MIT** — no patent language, no contribution clause, silent on trademarks and change-marking, and its real advantages (GPLv2 compatibility, brevity) do not apply to a playbook corpus; **dual MIT OR Apache-2.0** — complexity that lets recipients opt out of the patent grant to solve a GPLv2-linking problem this corpus does not have; **CLA** — unnecessary under a permissive outbound license (Apache 2.0 already permits commercial embedding of contributions) and higher-friction than a DCO.

## DD-16: Three-class executor model, canonical order, no "hybrid" class
- **Decision:** Executors are **human / automation / agent**, in that canonical, historical order — automation predates agents as a SOC executor, so the enumeration lists it second, immediately after human and before agent, everywhere in the framework. Automation — deterministic, rule- and script-based execution (SOAR playbook automation, scheduled jobs, dedup/allowlist logic) — is a first-class executor with its own [Provenance](../03-Processes/02-detection_and_analysis.md#16-triage-note) representation, not undifferentiated tooling or plumbing behind "agent." Assignment across the three follows a **deterministic-first** principle, echoed in the [Framework Manifest's Executor Neutrality subsection](framework_manifest.md#executor-neutrality-and-human-readability): simple, repetitive, fully-specifiable activities SHOULD be delivered by deterministic automation, not by agents — agents are reserved for work requiring judgment under uncertainty, and humans for accountability, ambiguity, and safety gates. **There is no enumerated "hybrid" executor class.** Real SOC operation is always a blend of the three, at varying degrees — the target autonomous-SOC model is **automation + agents + human supervision**, not a discrete fourth state. Where a single record spans executors (e.g. a Case automation pre-processed and an agent then dispositioned), the Provenance executor field lists the component classes that materially contributed, in canonical order (e.g. `automation + agent`), never `hybrid`.
- **Rationale:** A two-class (human/agent) model mis-attributes rule-based dispositions to "agent," inflating agent-autonomy metrics with work no model ever reasoned about, and gives a rule-auto-closed alert no home in Provenance. Naming automation as a peer executor lets [Operational Metrics Principle 4](../05-Metrics/operational_metrics.md#1-measurement-principles) and the [Autonomy Distribution metric (§6.5)](../05-Metrics/operational_metrics.md#65-autonomy-distribution-informative) slice honestly between "an agent reasoned about this" and "a deterministic rule fired," which is the difference the deterministic-first principle depends on being measurable. The human/automation/agent ordering is fixed as historical, not alphabetical or importance-ranked: automation (rule- and script-based execution) has been a SOC executor since long before AI agents existed, so it is listed immediately after the human executor it was originally built to relieve, and before the agent class that came later. A fourth, enumerated "hybrid" value was rejected because it collapses exactly the distinction DD-16 exists to make: a blend is not a class of executor, it is a composition of the other three, and naming it as a peer class would let mixed-provenance work hide from the automation/agent split the same way an undifferentiated "agent" bucket used to hide automation.
- **Alternatives:** A two-class executor model (human/agent only) — rejected: mis-attributes rule-based dispositions to agents and inflates agent-autonomy metrics. Treating automation as a technology-axis tooling concern only (SOAR as "just a tool," not an executor) — rejected: an auto-closed Case had no executor of record in Provenance, breaking Glass Box auditability for the single most common disposition path in a mature SOC. Enumerating **hybrid** as a fourth executor value (the framework's initial adoption) — rejected: since mature autonomous operation is *always* some blend of automation, agents, and human supervision, a "hybrid" bucket would absorb the majority of real dispositions without saying which classes were actually involved, defeating the auditability DD-16 was adopted to provide.
- **Cross-links:** [Framework Manifest — Executor Neutrality and Human Readability](framework_manifest.md#executor-neutrality-and-human-readability); [Operational Metrics — Principle 4 and §6.5 Autonomy Distribution](../05-Metrics/operational_metrics.md).

## DD-17: Community infrastructure and automated status checks
- **Decision:** Adopt an automated CI status-check suite for pull requests and main branch integration, comprising: (1) **markdownlint** (configured via `.markdownlint.yml`), (2) **lychee** offline internal link and anchor validation on PRs (with scheduled external checks), (3) a **frontmatter schema validator** (enforcing `title`, `type`, `status`, `last_updated`, `license`), and (4) **DCO (`Signed-off-by`)** verification. Maintainer commits adopt `git commit -s`.
- **Rationale:** CONTRIBUTING §4 promises automated repository status checks; implementing and specifying them in CI guarantees link integrity, frontmatter schema compliance, and intellectual property hygiene without manual gatekeeping overhead.
- **Alternatives:** Purely manual maintainer review (error-prone, fails to catch anchor rot); heavy multi-linter frameworks (adds excessive build friction).
- **Cross-links:** [CONTRIBUTING.md](../CONTRIBUTING.md); [Framework Manifest — Versioning & Document Release Status](framework_manifest.md#versioning--document-release-status).

## DD-18: Bifurcated Phase 2 (Triage vs. Investigation) and Triage-level Case Closure
- **Decision:** Phase 2 (Detection & Analysis) maintains two distinct operational sub-phases: **Triage (Phase 2.1)** and **Investigation (Phase 2.2)**. Triage is explicitly authorized to close cases with a definitive verdict (Gate G2: False Positive / Benign Positive) and emit detection-tuning feedback, rather than mandating that every alert progress to deep investigation.
- **Rationale & Architectural Context:**
  Although we acknowledge that in future Autonomous SecOps the separation between triage and investigation may appear less distinct—because the traditional "Tier 1 vs. Tier 2" split was historically built around human staffing bottlenecks (where junior analysts performed superficial filtering to protect expensive senior investigators), and in hospital emergency care triage is strictly a rapid acuity/routing assessment where all cases are ultimately examined by a physician rather than discharged at the door—the ZeroSOC Framework deliberately retains a bifurcated Phase 2 structure with triage-level closure for three fundamental reasons:
  1. *Cognitive & Computational Economics (System 1 vs. System 2):* Even in a fully autonomous agentic SOC, reasoning compute is not free. Triage represents high-velocity, low-cost **System 1 (fast thinking)**: enriching entities, matching historical baselines, recalibrating true operational priority, and immediately suppressing obvious benign noise. Launching an expensive **System 2 (slow thinking)** multi-agent forensic graph traversal or concurrent A/B hypothesis test on every routine backup script or informational anomaly is computationally and financially wasteful (violating DD-14 and DD-16).
  2. *Stage-Differentiated Diagnostic Feedback:* Separating the triage decision gate (Gate G2) from the investigation verdict (Gate G3) is critical for driving continuous improvement in [Preparation & Engineering (Phase 1)](../03-Processes/01-preparation_and_engineering.md). A high volume of False Positives closed at triage points to simple detection rule misconfigurations or missing allow-lists that can be easily suppressed upstream. Conversely, False Positives identified only during deep investigation represent complex behavioral ambiguities requiring playbook refinement, deeper telemetry, or model tuning.
  3. *Executor Neutrality & Blended Workforces:* As an executor-neutral standard, ZeroSOC must govern human analysts, deterministic automation, and AI agents under a unified, auditable lifecycle. Preserving explicit measurement gates (G1 Alert Raised $\rightarrow$ G2 Triage Decision $\rightarrow$ G3 Investigation Verdict) ensures consistent performance tracking, QA supervision, and capacity planning regardless of which executor fulfills the role.
- **Cross-links:** [Definitions — Triage and Investigation](definitions.md); [Detection & Analysis](../03-Processes/02-detection_and_analysis.md); [Operational Metrics — §5 Disposition Quality](../05-Metrics/operational_metrics.md).

## Intellectual Influences

Concepts the framework draws on that are not formal standards. They are credited here once; normative text describes their substance without relying on the names (per DD-12/DD-13).

- **Autonomic Security Operations (ASO)** (Google Cloud): the tier-less operating model, the even operations/engineering balance, and SRE principles applied to SecOps. Adopted as substance in [Roles & Responsibilities](roles_and_responsibilities.md); the term is not used normatively.
- **The tier-less SOC practitioner movement:** handoff-free case ownership, skill-based routing, and the retention effects of flat models; ingested research in `raw/roles-and-responsibilities.md`.
- **SOC Capability Maturity Model (SOC-CMM)** (Rob van Os): The concept of domain-level capability and maturity scoring across Business, People, Process, and Technology. ZeroSOC's role profiles and continuous-improvement metric loops are designed to provide compatible quantitative evidence for CMM-style assessments; the model itself is not a normative dependency (per DD-12).
- **SANS SEC450:** triage-method grounding for the Detection & Analysis phase (already cited in playbook references).
- **dandye/ai-runbooks:** per-runbook completion rubrics (adopted as Completion Criteria & Critical Failures), typed common-step outputs (adopted as sub-playbook Produces blocks), report provenance conventions (adopted in the Triage/Investigation Note schemas), and persona-to-permission matrices (adopted as the Role → Capability matrix).
