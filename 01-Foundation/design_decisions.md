---
title: Design Decisions
type: concept
status: development
last_updated: 2026-09-10
license: Apache-2.0
---

# Design Decisions

A durable, stable-identifier record of the key strategic and architectural design decisions behind the ZeroSOC Framework, with the rationale and the alternatives that were weighed.

### Entry Schema
Every entry in this registry follows this structure:
- **`DD-##: <title>`**: Persistent identifier and concise statement of the decision. When decisions are consolidated, the earliest ID is retained; when decisions are retired, IDs are skipped to maintain immutable cross-references.
- **Decision:** The normative choice made.
- **Rationale:** Technical, operational, or architectural reasoning supporting the decision.
- **Alternatives:** Competing options evaluated and specific reasons for rejection.
- **Cross-links / Revisit trigger:** Connections to affected framework documents and conditions under which the decision should be re-evaluated.

## DD-01: "Alert Type" vs "Incident Category" (Intentional Taxonomy Altitude Asymmetry)
- **Decision:** Alerts are classified by **Alert Type**; incidents are classified by **Incident Category** (`IC-##`). The two use different nouns intentionally.
- **Rationale:** Alert Types and Incident Categories operate at fundamentally different operational altitudes. *Alert types* describe granular detection patterns from specific telemetry sources; *incident categories* represent higher-level **business-impact** groupings. "Incident category" is the established industry standard (NIST, CISA, ENISA, FIRST), while "type" naturally fits detection patterns.
- **Alternatives:** Renaming to "Incident Type" for surface symmetry was rejected because it hides the altitude difference, departs from industry usage, and carries high churn across the framework.

## DD-02: Two-Layer Playbook Architecture (Generic Methods vs. Specialized Knowledge)
- **Decision:** Separate generic phase **methods** (how to triage, investigate, and respond — in `03-Processes`) from specialized **knowledge playbooks** (what telemetry and indicators to evaluate — in `04-Playbooks`). Playbooks reference methods without duplicating execution logic.
- **Rationale:** Prevents duplicating workflow logic across dozens of playbook files, eliminating maintenance sprawl. Matches leading practice (CISA process playbooks, Elastic detection guides, SOAR sub-playbook composition).
- **Alternatives:** Monolithic per-incident playbooks (unmaintainable duplication); full per-phase × per-type matrix (~45 fragmented files).

## DD-03: Domain-Oriented Triage vs. Incident-Category Investigation & Domain Assignment
- **Decision:** Triage playbooks are organized by **telemetry domain** (Endpoint, Identity, Network, Cloud, Email, Data, Application, OT/ICS), while Investigation & Response playbooks are organized by **Incident Category**. An alert type's **home domain** is strictly defined by the primary telemetry source that raises it and the entity it is about; cross-domain corroboration is treated as enrichment. The operational pivot from domain to Incident Category occurs at the Triage → Investigation phase transition.
- **Rationale:** Alerts originate from domain-specific sensors (EDR, IdP, firewall, CASB) where enrichment and known false-positive heuristics are domain-native. Conversely, incidents and investigations are defined by business impact. Enforcing strict home domains prevents telemetry sprawl and keeps taxonomy ownership unambiguous. *(Consolidates former DD-03 and DD-04).*
- **Alternatives:** Organizing all phases by Incident Category (forces alerts into impact categories before classification is established); organizing all phases by domain (misfits response, which is incident- and impact-centric); assigning multiple home domains per alert type (causes redundant rows and ambiguous ownership).

## DD-05: Prioritization via Severity and Confidence (No Redundant Priority Axis)
- **Decision:** Prioritize alerts and cases along two orthogonal axes: **Severity** (Informational to Critical, OCSF `severity_id`) and **Confidence** (Low/Medium/High, OCSF `confidence_id`), without a separate ITIL "priority" matrix. A third measure, **Impact** (OCSF `impact_id`), is assessed only when a Case is confirmed as an Incident: it records realized or expected harm and drives regulatory notification (NIS2 Article 23 requires both severity and impact), whereas Severity estimates potential harm to drive urgency. Impact is assessed at triage when it is already known (an external report stating the harm, or entities classified as critical assets or VIP users) and otherwise at incident confirmation; it is recorded as unknown until assessed.
- **Rationale:** Matches modern SecOps and MDR practice. Severity represents potential business impact ("how bad"), while Confidence represents certainty and fidelity ("how sure"). In security operations, urgency is intrinsic to the threat severity and confidence; adding an ITIL Impact × Urgency matrix creates redundant complexity without improving operational triage.
- **Alternatives:** NIST SP 800-61 three-factor scoring (retained purely as inputs to Severity); ITIL Impact × Urgency priority matrices (redundant with Severity).

## DD-06: Phase Model Aligned to the Incident Lifecycle
- **Decision:** The operational lifecycle follows four macro phases: Phase 1 is **Preparation & Engineering**, Phase 2 is **Detection & Analysis** (with **Triage** and **Investigation** sub-phases), Phase 3 is **Incident Response** (Containment, Eradication, Recovery), and Phase 4 is **Post-Incident Activity**.
- **Rationale:** Aligns playbook phase names with the `03-Processes` lifecycle and standard SecOps handling (Assign → Triage → Investigate → Respond → Review). Using "Incident Response" (rather than generic "Response") emphasizes that only confirmed True Positive incidents enter Phase 3.
- **Alternatives:** Keep legacy "Observation & Triage" / "Response" labels (inconsistent with modern process lifecycles).

## DD-07: OCSF-Aligned Phase Transition Contracts (Disambiguated from HITL Handover)
- **Decision:** Phase boundaries are governed by explicit, machine-readable **phase transition contracts** using OCSF field semantics (`severity_id`, `confidence_id`, entities/observables, candidate `incident_category`, `status_id`). A promoted Case carries no conclusive verdict across the transition (`verdict_id` remains open until Investigation resolves it). The term **phase transition contract** (or *phase contract*) is used for data boundaries, reserving **handover** strictly for operational control transfers (human-in-the-loop escalation, shift changes, agent-to-human control transfer).
- **Rationale:** Explicit data contracts prevent context loss between operational stages and enforce vendor-neutral interoperability via OCSF. Disambiguating phase transition contracts from operational handovers resolves terminology confusion between data interchange and operational accountability transfer.
- **Alternatives:** Implicit prose descriptions at stage boundaries (silent context loss); bespoke data interchange schemas (reinvents OCSF); using "handoff/handover" interchangeably for both data artifacts and human escalation (creates operational ambiguity).

## DD-08: Concurrent Malicious/Benign Hypothesis Validation Engine
- **Decision:** Investigation systematically evaluates competing hypotheses (**Malicious hypothesis:** confirmed threat / True Positive activity vs. **Benign hypothesis:** authorized, expected, or benign activity) by seeking targeted corroborating and discriminant evidence for both possibilities concurrently, rather than following linear if-then branch trees or assuming malicious intent.
- **Rationale:** Sequential investigation often falls victim to confirmation bias (seeking only evidence that confirms initial alert alarms). Concurrent hypothesis validation ensures that evidence supporting benign explanations (e.g., scheduled maintenance, approved administrative scripts, authorized penetration testing, user travel) is tested with equal rigor alongside threat indicators before reaching a definitive Case Verdict (Gate G3). Every finding — alert, enrichment result or query result — is tagged with a side and a confidence level on the OCSF scale; hypotheses resolve by the additive score of [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), with the Benign side required to cover the Medium and High confidence Malicious findings, so that the rule is explainable and executor-neutral by design.
- **Alternatives:** Linear conditional playbooks (often assume malicious intent upon alert generation, leading to confirmation bias and elevated false positive rates); unstructured open-ended forensic queries (inconsistent, difficult to automate or audit).

## DD-09: Eight Telemetry Domains and Aggregated Alert Taxonomy
- **Decision:** Telemetry is classified into eight core domains: **Endpoint, Identity, Network, Cloud, Email, Data, Application, and OT/ICS**. SaaS detections map to Identity/Cloud; Containers/Kubernetes map to Cloud. Alert types are maintained at a high level of abstraction (~40 aggregated types) rather than enumerating hundreds of vendor-specific detection rules.
- **Rationale:** Mirrors how detection repositories (Elastic, Sigma, Sentinel) categorize telemetry while preventing domain proliferation. A high-level taxonomy serves as an operational triage vocabulary without duplicating vendor rule catalogs. *(Consolidates former DD-09 and DD-11).*
- **Alternatives:** Six domains (omits dedicated Application and OT/ICS coverage); unbounded domain expansion (e.g., separate SaaS, Container, Serverless domains); exhaustive rule-level alert enumeration (unmaintainable, vendor-coupled).

## DD-12: Adopt Open Standards, Treat Niche Frameworks as Conceptual Influences
- **Decision:** ZeroSOC adopts widely implemented, vendor-neutral standards as formal dependencies (NIST SP 800-61 / CSF, MITRE ATT&CK, OCSF, ISO/IEC 27035, FinOps FOCUS). Niche or emerging frameworks (OASIS CACAO, RE&CT, SOC-CMM) are treated as conceptual influences rather than normative dependencies.
- **Rationale:** Protects the framework's longevity, broad industry adoption, and vendor independence, avoiding tight coupling to nascent or low-adoption tooling ecosystems.
- **Alternatives:** Direct conformance dependencies on niche execution frameworks like CACAO or RE&CT (rejected due to low enterprise adoption).

## DD-14: Cost Telemetry Alignment — FOCUS Adopted, OTel GenAI Provisional
- **Decision:** Token economics metrics capture input/output token counts per model invocation attributed to the Security Case ID. The FinOps Foundation **FOCUS v1.2** specification is adopted for cost and billing normalization. **OpenTelemetry GenAI semantic conventions** are adopted provisionally as a recommended (`SHOULD`) attribute-naming standard (`gen_ai.usage.*`) pending specification stability.
- **Rationale:** FOCUS is a ratified cross-cloud billing standard. OTel GenAI provides vendor-neutral LLM telemetry conventions but remains in Development status; adopting it provisionally ensures alignment without importing breaking upstream specification churn.
- **Alternatives:** Proprietary LLM telemetry schemas (vendor lock-in); invented custom attribute names (inevitable divergence from OpenTelemetry).
- **Revisit trigger:** Promote OTel GenAI naming to normative requirement (`MUST`) once the upstream specification reaches Stable status.

## DD-15: Apache 2.0 Licensing and Contribution Governance
- **Decision:** The entire framework repository is licensed under the **Apache License 2.0** with a Developer Certificate of Origin (DCO / `Signed-off-by`) contribution model. Trademark rights for "ZeroSOC" are reserved separately under `TRADEMARKS.md`. Machine-readable `license: Apache-2.0` metadata is required in all frontmatter.
- **Rationale:** ZeroSOC playbooks and schemas function as implementable specifications executed by automated engines and AI agents. Apache 2.0 provides essential patent grants and retaliation clauses (§3), automatic inbound=outbound terms (§5), and mandatory change-marking on forks (§4(b)), matching standard practice for technical specifications (OpenAPI, CloudEvents, OCSF).
- **Alternatives:** Creative Commons CC BY 4.0 (narrative-only license lacking patent protections); MIT (lacks patent language and fork change-marking).

## DD-16: Three-Class Executor Model (Human / Automation / Agent) with No "Hybrid" Class
- **Decision:** SecOps activities are executed by three canonical classes in historical order: **human**, **automation** (deterministic rules, SOAR scripts), and **agent** (probabilistic LLM/reasoning systems). Real-world operation combines all three under a **deterministic-first** principle (simple tasks to automation, complex reasoning to agents, governance/oversight to humans). "Hybrid" is strictly rejected as a discrete fourth executor class; multi-executor actions record exact composite provenance (e.g., `automation + agent`).
- **Rationale:** Treating automation as an explicit peer executor prevents misattributing rule-based actions to AI agents and ensures honest autonomy metrics. Rejecting a vague "hybrid" class preserves Glass Box auditability for every operational action.
- **Alternatives:** Two-class human/agent model (erases deterministic automation from audit logs and inflates agent autonomy metrics); enumerated "hybrid" class (hides actual execution breakdown).

## DD-18: Bifurcated Phase 2 (Triage vs. Investigation) and Triage-Level Case Closure
- **Decision:** Phase 2 (Detection & Analysis) maintains two distinct operational sub-phases: **Triage (Phase 2.a)** and **Investigation (Phase 2.b)**. Triage is explicitly authorized to close cases definitively with a verdict (Gate G2: False Positive / Benign Positive / Duplicate, the last only under the validation criteria of Detection & Analysis §1.5) and emit upstream detection tuning feedback, rather than mandating that every alert progress to deep investigation.
- **Rationale:**
  1. *Cognitive & Computational Economics (System 1 vs. System 2):* Triage provides rapid, low-cost **System 1 (fast thinking)** filtering (enriching entities, baseline comparison, priority recalibration, obvious noise suppression). Deep multi-agent graph traversal and hypothesis testing (**System 2 slow thinking**) are reserved for ambiguous or high-risk cases to conserve analyst attention and LLM compute.
  2. *Stage-Differentiated Diagnostic Feedback:* Closing false positives at Gate G2 identifies simple rule misconfigurations and missing allowlists for immediate suppression, whereas false positives uncovered at Gate G3 highlight subtle behavioral ambiguities requiring playbook or model refinement.
  3. *Unified Measurement:* Provides consistent, auditable measurement gates (G1 Alert Raised → G2 Triage Decision → G3 Investigation Verdict) across human, automated, and agentic workflows.
- **Alternatives:** Single undifferentiated detection phase (forces all alerts through heavy investigation or blurs triage metrics); routing all alerts to investigation without triage closure (overwhelms senior responders and exhausts token budgets).
- **Cross-links:** [Definitions — Triage and Investigation](definitions.md); [Detection & Analysis](../03-Processes/02-detection_and_analysis.md); [Operational Metrics — §5 Disposition Quality](../05-Metrics/operational_metrics.md).

## DD-19: Single Case Schema
- **Decision:** The Case is defined once, in the [Case Schema](../02-Taxonomy/case_schema.md) and its JSON Schema: the OCSF Incident Finding fields the framework uses (status, severity, confidence, impact, verdict, owner, aggregated alerts, techniques, observables, times) and the framework's own fields (candidate and confirmed Incident Category, entry path, T0 and timeline, visibility gaps, provenance, regulatory significance and cross-border flags, notifications, tuning ticket, handover reason). Processes, playbooks, deliverables, metrics and the phase transition contracts refer to these names and do not define fields of their own.
- **Rationale:** Field names were scattered across the processes, the playbook architecture and the deliverables with drifting names (`confidence` vs `confidence_id`) and no single answer to "which fields does a Case carry". One model removes the drift, lets the phase transition contracts be stated as subsets, and gives adopters a mapping target for their platform.
- **Alternatives:** Keep per-document field lists (drift, no canonical source); adopt a bespoke schema instead of OCSF (reinvents OCSF, breaks vendor neutrality).
- **Cross-links / Revisit trigger:** [Case Schema](../02-Taxonomy/case_schema.md); [Playbook Architecture §5](../04-Playbooks/playbook_architecture.md); [Detection & Analysis](../03-Processes/02-detection_and_analysis.md); [Deliverables](../06-Deliverables/README.md). Revisit when OCSF adds native equivalents of the framework's extension fields.

## DD-20: SOC Knowledge Base as a Foundational Component
- **Decision:** The framework names the [SOC Knowledge Base](definitions.md#soc-knowledge-base-soc-kb) — the organization's institutional knowledge about its own environment — as a foundational component: an enrichment source in Triage (Organizational Context), an output of Post-Incident Activity (lessons learned), and a maintenance responsibility of Preparation & Engineering.
- **Rationale:** Most security teams hold this knowledge in internal documentation of varying maturity, often compensating an incomplete CMDB, and it is exactly the context that separates a benign recurrence from a new intrusion. Naming it makes it a required input that every executor reads — the mechanism by which institutional knowledge reaches automated and agentic execution instead of living only in analysts' heads.
- **Alternatives:** Rely on the CMDB and directory alone (incomplete in practice); leave the knowledge implicit (unavailable to automation and agents, lost with staff turnover).
- **Cross-links / Revisit trigger:** [Definitions](definitions.md#soc-knowledge-base-soc-kb); [Detection & Analysis §1.2](../03-Processes/02-detection_and_analysis.md#12-multi-vector-context-enrichment); [Preparation & Engineering](../03-Processes/01-preparation_and_engineering.md); [Post-Incident Activity](../03-Processes/04-post_incident_activity.md). Revisit if a structured schema for the knowledge base is standardized.

## DD-21: Single Target-Aware Containment Autonomy Matrix
- **Decision:** Containment autonomy is specified once, in [Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment), and keyed on three things: the reversibility of the action, the criticality of the entity it acts on, and the Case confidence and severity. Pre-authorized actions are reversible and leave the affected entity serving — any executor applies them without approval, on a Crown Jewel included. Actions that stop a critical service, are not reversible or affect many entities at once require approval, requested with the Guardrails payload whoever the executor is. At Low confidence every action requires approval. The Guardrails govern how approval is requested and granted and when the assignee must be human; the playbooks list the actions of each Incident Category; neither restates the matrix.
- **Rationale:** Autonomy boundaries were stated in three places (the Response process, the Guardrails, the playbook failure criteria) with drifting lists, and the lists keyed on the asset alone — so disabling a compromised administrator account was blocked because it touched a domain controller, while the same action was pre-authorized on a workstation. Keying on what the action does to the entity's service lets the fast, reversible actions run everywhere, and reserves approval for the disruptive ones. Keying on confidence connects the matrix to the evidence model: a verdict proven on Low-confidence findings is acted on, but under approval.
- **Alternatives:** Asset-only boundaries (blocks reversible actions on the assets that most need them); per-Incident-Category matrices in the playbooks (duplication and drift); autonomy by executor class (breaks executor neutrality — a human executor needs the same approval to shut down a production database).
- **Cross-links / Revisit trigger:** [Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment); [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence); [Agentic Guardrails](../07-Governance/agentic_guardrails.md); [Playbook Architecture](../04-Playbooks/playbook_architecture.md). Revisit if organizations report that the reversibility test is insufficient to classify an action, or when OCSF standardizes a containment-action vocabulary.
