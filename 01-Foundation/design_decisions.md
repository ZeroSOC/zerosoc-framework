---
title: Design Decisions
type: concept
status: development
last_updated: 2026-09-23
license: Apache-2.0
---

# Design Decisions

The strategic and architectural decisions behind the ZeroSOC Framework, each with the reasoning that produced it. Entries record *what was decided and why*; **how** it works is in the document that implements it, linked from the entry and never restated here.

## Entry Schema

- **`DD-##: <title>`** — the identifier and the decision in a phrase. Numbers are never reused: a consolidated decision keeps the earliest, a retired one leaves its number skipped, so a reference made once stays valid.
- **Decision:** the choice, and where it is implemented.
- **Rationale:** why it was chosen.
- **Discarded alternatives:** options that were genuinely weighed, and why they lost. Omitted where there were none — an entry with no real alternative is a definition, not a decision, and says so by leaving the field out.
- **Revisit:** the concrete condition that would reopen the decision. Omitted where none is known.

**Documents do not cite this registry.** A framework document states its own rule and is the source of truth for it. This registry records *why* that rule was chosen, so that a settled decision is not reopened from memory — it is read by someone proposing a change, not by an executor following the method. A reference therefore runs one way: from an entry here to the document that implements it, never the reverse.

External standards and sources are credited in this registry once, per DD-12.

## DD-01: Alert Type vs Incident Category

- **Decision:** Alerts are classified by **Alert Type**, incidents by **Incident Category** (`IC-##`). The different nouns are deliberate.
- **Rationale:** The two sit at different altitudes. An alert type describes a detection pattern in one telemetry source; an incident category describes business impact. "Incident category" is also the established term (NIST, CISA, ENISA, FIRST).
- **Discarded alternatives:** "Incident Type" for surface symmetry — it hides the altitude difference and departs from industry usage.

## DD-02: Two-Layer Playbook Architecture

- **Decision:** Generic phase **methods** live in [`03-Processes`](../03-Processes/); specialized **knowledge playbooks** live in [`04-Playbooks`](../04-Playbooks/). A playbook references a method and does not restate its execution logic.
- **Rationale:** One copy of the workflow logic rather than one per playbook.
- **Discarded alternatives:** monolithic per-incident playbooks (the same workflow duplicated in every file); a per-phase × per-type matrix (~45 fragmented files).

## DD-03: Domain-Oriented Triage, Category-Oriented Investigation

- **Decision:** Triage playbooks are organized by **telemetry domain**, Investigation & Response playbooks by **Incident Category**. An alert type has exactly one home domain, set by the sensor that raises it and the entity it is about; corroboration from another domain is enrichment. The pivot from domain to category happens at the Triage → Investigation transition. *(Consolidates the former DD-03 and DD-04.)*
- **Rationale:** Alerts arrive from domain-specific sensors, where the enrichment and the known false-positive heuristics are domain-native. Incidents are defined by business impact instead. One home domain per alert type keeps taxonomy ownership unambiguous.
- **Discarded alternatives:** every phase by Incident Category (forces a category before classification is established); every phase by domain (misfits response, which is impact-centric); several home domains per alert type (redundant rows, ambiguous ownership).

## DD-05: Severity and Confidence as the Prioritization Axes

- **Decision:** Alerts and Cases are prioritized on two orthogonal axes, **Severity** (`severity_id`) and **Confidence** (`confidence_id`). **Impact** (`impact_id`) is a third measure recorded only once known — at triage where the harm is already evident, otherwise at incident confirmation — and drives regulatory notification. Implemented in [Detection & Analysis §1.4](../03-Processes/02-detection_and_analysis.md).
- **Rationale:** Severity is how bad, Confidence is how sure, and in security operations urgency follows from the two together. Impact is kept separate because it records realized harm, which regulators ask for (NIS2 Article 23) and severity does not answer.
- **Discarded alternatives:** an ITIL Impact × Urgency priority matrix (a third number that does not change the order of work); NIST SP 800-61 three-factor scoring (kept as an input to Severity, not as an axis of its own).

## DD-06: Four Phases Aligned to the Incident Lifecycle

- **Decision:** Phase 1 **Preparation & Engineering**, Phase 2 **Detection & Analysis** (Triage 2.a, Investigation 2.b), Phase 3 **Incident Response**, Phase 4 **Post-Incident Activity**.
- **Rationale:** Matches the standard handling lifecycle. "Incident Response" rather than a generic "Response" marks that only confirmed True Positives enter Phase 3.
- **Discarded alternatives:** the earlier "Observation & Triage" and "Response" labels, which do not line up with the process lifecycle.

## DD-07: Phase Transition Contracts, Distinct from Handover

- **Decision:** A phase boundary is crossed by an explicit, machine-readable **phase transition contract** stated in OCSF terms. **Handover** means an operational control transfer only — escalation, shift change, agent to human — and never a data boundary. A promoted Case carries no verdict: `verdict_id` stays open until Investigation resolves it. Contract fields in [Playbook Architecture §5](../04-Playbooks/playbook_architecture.md).
- **Rationale:** An explicit contract stops context being lost between stages. The two words had been used interchangeably, which confused a data artifact with a transfer of accountability.
- **Discarded alternatives:** a bespoke interchange schema (reinvents OCSF and breaks vendor neutrality).

## DD-08: Concurrent Malicious and Benign Hypotheses

- **Decision:** Investigation tests a **Malicious** and a **Benign** hypothesis concurrently, seeking discriminating evidence for both, and resolves them by the additive score of [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md).
- **Rationale:** A sequential investigation starts from the alert and looks for what confirms it. Testing the benign explanation with equal rigour is what surfaces authorized activity — maintenance, admin scripts, sanctioned testing, user travel — before a verdict rather than after it.
- **Discarded alternatives:** linear conditional playbooks, which assume malicious intent from the alert onward and raise the false-positive rate.

## DD-09: Eight Telemetry Domains and an Aggregated Alert Taxonomy

- **Decision:** Eight domains — **Endpoint, Identity, Network, Cloud, Email, Data, Application, OT/ICS**. SaaS detections map to Identity or Cloud, containers to Cloud. Alert types stay aggregated (around 40) rather than enumerating vendor detection rules. *(Consolidates the former DD-09 and DD-11.)*
- **Rationale:** Mirrors how detection content is already categorized, and gives triage a shared vocabulary without the framework becoming a second rule catalog to maintain.
- **Discarded alternatives:** six domains (drops dedicated Application and OT/ICS coverage); rule-level alert enumeration (unmaintainable and vendor-coupled).

## DD-12: Open Standards as Dependencies, Niche Frameworks as Influences

- **Decision:** Formal dependencies are widely implemented, vendor-neutral standards: NIST SP 800-61 and CSF, MITRE ATT&CK, OCSF, ISO/IEC 27035, FinOps FOCUS. OASIS CACAO, RE&CT and SOC-CMM are conceptual influences, not normative dependencies. Standards and sources are credited in this registry once; normative text describes the substance without relying on brand names.
- **Rationale:** Longevity and vendor independence. A conformance dependency on a low-adoption framework binds this one to a tooling ecosystem that may not outlast it.
- **Discarded alternatives:** conformance dependencies on CACAO or RE&CT.

## DD-14: FOCUS Adopted, OpenTelemetry GenAI Provisional

- **Decision:** Cost and billing normalization follows FinOps **FOCUS v1.2**. **OpenTelemetry GenAI** attribute naming (`gen_ai.usage.*`) is adopted provisionally, as a `SHOULD`. Token counts are captured per model invocation and attributed to the Case.
- **Rationale:** FOCUS is a ratified cross-cloud billing standard. OTel GenAI is still in Development status, so requiring it would import upstream specification churn.
- **Revisit:** promote the OTel GenAI naming to `MUST` once the upstream specification reaches Stable.

## DD-15: Apache 2.0 Licensing and DCO Contribution

- **Decision:** The repository is licensed **Apache 2.0**, with a Developer Certificate of Origin (`Signed-off-by`) contribution model. The "ZeroSOC" mark is reserved separately under [TRADEMARKS.md](../TRADEMARKS.md). Frontmatter carries `license: Apache-2.0`.
- **Rationale:** These playbooks and schemas are implementable specifications executed by engines and agents, so the patent grant and retaliation clause, the automatic inbound=outbound terms and the fork change-marking all apply — the same choice OpenAPI, CloudEvents and OCSF made.
- **Discarded alternatives:** CC BY 4.0 (a narrative license, no patent protection); MIT (no patent language, no fork change-marking).

## DD-16: Three Executor Classes — Human, Automation, Agent

- **Decision:** Work is executed by **human**, **automation** (deterministic rules, scripts) or **agent** (probabilistic reasoning systems), assigned deterministic-first. An action more than one class contributed to records the composite, such as `automation + agent`.
- **Rationale:** Naming automation as a peer executor keeps rule-based work out of the agent's autonomy figures, so those figures stay honest.
- **Discarded alternatives:** a fourth "hybrid" class for an action more than one class contributed to (hides the breakdown an audit needs, which the composite records instead); a two-class human/agent model (erases deterministic automation from the record and inflates agent autonomy).

## DD-18: Two Sub-Phases in Phase 2, and Case Closure at Triage

- **Decision:** Phase 2 has **Triage (2.a)** and **Investigation (2.b)**. Triage may close a Case with a verdict at Gate G2 — False Positive, Benign, or Duplicate under the criteria of [Detection & Analysis §1.5](../03-Processes/02-detection_and_analysis.md) — and emit tuning feedback upstream. Not every alert reaches investigation.
- **Rationale:** Triage is the cheap filter and investigation the expensive one; routing every alert through investigation exhausts both analyst attention and token budget. The two gates also fail differently — a false positive closed at G2 is usually a rule or allowlist fix, while one found at G3 is a behavioural ambiguity needing the playbook or the model changed — and separating them keeps the measurement gates (G1 → G2 → G3) comparable across executors.
- **Discarded alternatives:** a single undifferentiated detection phase, which blurs the gates and the metrics taken at them.

## DD-19: A Single Case Schema

- **Decision:** The Case is defined once, in the [Case Schema](../02-Taxonomy/case_schema.md) and its [JSON Schema](../02-Taxonomy/case_schema.json). Processes, playbooks, deliverables, metrics and the phase transition contracts use those field names and define none of their own.
- **Rationale:** Field names had drifted across documents — `confidence` against `confidence_id` — with no single answer to which fields a Case carries. One definition removes the drift, lets the contracts be stated as subsets of it, and gives an adopter one mapping target.
- **Discarded alternatives:** per-document field lists (the drift itself); a bespoke schema in place of OCSF (reinvents it and breaks vendor neutrality).
- **Revisit:** when OCSF adds native equivalents of the framework's extension fields.

## DD-20: The SOC Knowledge Base as a Foundational Component

- **Decision:** The [SOC Knowledge Base](definitions.md#soc-knowledge-base-soc-kb) — what the organization knows about its own environment — is a named component: an enrichment source at triage, an output of Post-Incident Activity, and a maintenance responsibility of Preparation & Engineering.
- **Rationale:** This is the context that separates a benign recurrence from a new intrusion, and it usually lives in documentation of varying maturity or in analysts' heads. Naming it makes it a required input that an automated or agentic executor can actually read, instead of knowledge lost with staff turnover.
- **Discarded alternatives:** relying on the CMDB and the directory alone, which are incomplete in practice.
- **Revisit:** if a structured schema for this knowledge is standardized.

## DD-21: One Containment Autonomy Matrix

- **Decision:** Containment autonomy is specified once, in [Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment), keyed on three things: the reversibility of the action, the criticality of the entity it acts on, and the Case's confidence and severity. The Guardrails govern how approval is requested and granted; the playbooks list the actions of each Incident Category; neither restates the matrix.
- **Rationale:** The boundaries had been stated in three places with drifting lists, all keyed on the asset alone — so disabling a compromised administrator account was blocked for touching a domain controller, while the same action was pre-authorized on a workstation. Keying on what the action does to the entity's service lets fast, reversible actions run everywhere and reserves approval for the disruptive ones.
- **Discarded alternatives:** asset-only boundaries (block reversible actions on the assets that most need them); a matrix per Incident Category in the playbooks (duplication and drift); autonomy by executor class (breaks executor neutrality — a human needs the same approval to shut down a production database).
- **Revisit:** if the reversibility test proves insufficient to classify an action, or when OCSF standardizes a containment-action vocabulary.

## DD-22: Disposition Quality as Precision and Recall per Gate

- **Decision:** Disposition quality is two questions asked at each decision gate — **precision** (of what the gate flagged, how much was real) and **recall** (of what was real, how much the gate flagged) — named per gate at G1, G2 and G3. Every recall is reported as *Observed*, an estimate bounded by the channels that surface misses. The two are reported together and never averaged into a single accuracy. The former Verdict Overturn Rate is retired. Implemented in [Operational Metrics §5](../05-Metrics/operational_metrics.md).
- **Rationale:** One vocabulary for the whole quality section. The overturn rate mixed a precision figure and a recall component under one name with two denominators, which invited summing them. Accuracy is rejected because most Cases are noise: a single figure is dominated by correct closes and hides missed threats, the failure the autonomy grant exists to catch.
- **Discarded alternatives:** keeping the overturn rate as the observable and layering the new names on top (two names for one number); one accuracy or F-score per executor (hides that the two errors cost differently and have different owners).
- **Revisit:** when recall can be measured against a known denominator through adversary emulation.

## DD-23: Native OCSF Mapping Preferred Over Framework Extensions

- **Decision:** Where OCSF carries a concept, the framework maps to it and defines no field of its own. A field under the `zerosoc` extension is added only where the concept was looked for in the current OCSF release and found absent, or present in a form that loses what the framework needs; it is then declared and validated in the [JSON Schema](../02-Taxonomy/case_schema.json), which is what makes it checkable. Three concepts qualify today, each recorded with what was searched for: a finding's **side and confidence**, the link from a **response action back to the finding that motivated it**, and **re-classification history**.
- **Rationale:** An adopter maps their platform to OCSF once, and every field the framework invents is one they must then carry privately; a framework that invents freely stops being a mapping target and becomes a second schema to implement. Recording what was searched for is what keeps the exception list honest — a reader can tell an extension that was checked from one that was convenient.
- **Discarded alternatives:** extension-first, mapping to OCSF only where convenient (more expressive per Case, but every adopter carries private fields and the mapping stops being reviewable); no rule, deciding case by case (what produced the drift, and leaves no record of what was searched for).
- **Revisit:** at every OCSF minor release — an extension whose concept the release has since adopted natively is migrated, and the list is re-tested rather than assumed.
