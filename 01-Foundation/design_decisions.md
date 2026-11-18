---
title: Design Decisions
type: concept
status: development
last_updated: 2026-11-18
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

## DD-07: Phase Transition Contracts

- **Decision:** A phase boundary is crossed by an explicit, machine-readable **phase transition contract** stated in OCSF terms. A contract is a data boundary and never a transfer of control: a change of assignee is an event of its own. A promoted Case carries no verdict: `verdict_id` stays open until Investigation resolves it. Contract fields in [Playbook Architecture §5](../04-Playbooks/playbook_architecture.md).
- **Rationale:** An explicit contract stops context being lost between stages. Contract and handover had been used interchangeably, which confused a data artifact with a transfer of accountability.
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

- **Decision:** Containment autonomy is specified once, in [Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment), keyed on three things: the Case's confidence, the Incident's Impact, and the action's own impact. The playbooks list the actions of each Incident Category and do not restate the matrix.
- **Rationale:** The boundaries had been stated in three places with drifting lists, all keyed on the asset alone — so disabling a compromised administrator account was blocked for touching a domain controller, while the same action was pre-authorized on a workstation. Keying on what the action does to the entity's service lets fast, reversible actions run everywhere and reserves approval for the disruptive ones.
- **Discarded alternatives:** asset-only boundaries (block reversible actions on the assets that most need them); a matrix per Incident Category in the playbooks (duplication and drift); autonomy by executor class (breaks executor neutrality — a human needs the same approval to shut down a production database).
- **Revisit:** when OCSF standardizes a containment-action vocabulary.

## DD-22: Disposition Quality as Precision and Recall per Gate

- **Decision:** Disposition quality is two questions asked at each decision gate — **precision** (of what the gate flagged, how much was real) and **recall** (of what was real, how much the gate flagged) — named per gate at G1, G2 and G3. Every recall is reported as *Observed*, an estimate bounded by the channels that surface misses. The two are reported together and never averaged into a single accuracy. The former Verdict Overturn Rate is retired. Implemented in [Operational Metrics §5](../05-Metrics/operational_metrics.md).
- **Rationale:** One vocabulary for the whole quality section. The overturn rate mixed a precision figure and a recall component under one name with two denominators, which invited summing them. Accuracy is rejected because most Cases are noise: a single figure is dominated by correct closes and hides missed threats, the failure the autonomy grant exists to catch.
- **Discarded alternatives:** keeping the overturn rate as the observable and layering the new names on top (two names for one number); one accuracy or F-score per executor (hides that the two errors cost differently and have different owners).
- **Revisit:** when recall can be measured against a known denominator through adversary emulation.

## DD-23: Native OCSF Mapping Preferred Over Framework Extensions

- **Decision:** Where OCSF carries a concept, the framework maps to it and defines no field of its own. A field under the `zerosoc` extension is added only where the concept was looked for in the current OCSF release and found absent, or present in a form that loses what the framework needs, and it is declared in the [JSON Schema](../02-Taxonomy/case_schema.json). The framework states a mapping only where OCSF is ambiguous, where the framework requires the attribute, or where it extends OCSF. A source's own record goes under `unmapped`, keyed by the source's identifier.
- **Rationale:** An adopter maps their platform to OCSF once, and every field the framework invents is one they must then carry privately. Recording what was searched for tells an extension that was checked from one that was convenient.
- **Discarded alternatives:** extension-first, mapping to OCSF only where convenient (every adopter carries private fields, and the mapping stops being reviewable); deciding case by case (what produced the drift).
- **Revisit:** at every OCSF minor release: an extension whose concept OCSF has since adopted natively is migrated.

## DD-24: Response Actions Are Their Own Note Element

- **Decision:** A Triage Note and an Investigation Note render **Response Actions** as an element of their own. It holds the observed remediation, mapped to the [Remediation Activity [7001]](https://schema.ocsf.io/1.9.0/classes/remediation_activity) events the Case references, and the planned remediation, mapped to the tickets the Case raised. Every ticket says which kind it is, such as `tuning`, `visibility`, `containment`, `eradication` or `recovery`. Implemented in [Detection & Analysis §1.6 and §2.6](../03-Processes/02-detection_and_analysis.md) and the [Case Schema](../02-Taxonomy/case_schema.md).
- **Rationale:** A reader of a Note needs one place that says what was done and what is about to be done. In OCSF a Remediation Activity records an attempt that was made, with a time and an outcome, so a planned action is a ticket, and its kind tells a tuning request from a containment step. The element takes a framework name because it holds more than the OCSF class.
- **Discarded alternatives:** actions only among the Observations (an action waiting for approval has nowhere to go); naming the element Remediation Activity (a reader would expect every entry to be one); a planned state on a Remediation Activity (its status values are outcomes of an attempt).
- **Revisit:** when OCSF can represent a remediation that has not been attempted.

## DD-25: The Framework's Entry Is an Observation, Not a Finding

- **Decision:** One entry in a Case's record is an **Observation**: a tagged assertion carrying a side and a confidence, or neither where it is pure context. *Finding* is left to OCSF, where it names a class of event. A Case ([Incident Finding [2005]](https://schema.ocsf.io/1.9.0/classes/incident_finding)) holds Observations in `finding_info[]`, and each Observation's `related_events[]` cite what it rests on: an Alert ([Detection Finding [2004]](https://schema.ocsf.io/1.9.0/classes/detection_finding)), an observed remediation or another event. Defined in [Definitions](definitions.md#observation), mapped in the [Case Schema](../02-Taxonomy/case_schema.md).
- **Rationale:** In OCSF a Detection Finding is the framework's Alert and an Incident Finding its Case, so a framework Finding, one entry in the record, gave the word two meanings. The collision pushed the side and the confidence into `tags`, response actions into a list of findings, and the reason for an action into `analytic`. `finding_info` stays the carrier because it is the only link OCSF gives between an Incident Finding and what it aggregates.
- **Discarded alternatives:** keeping the collision with a warning in the glossary (the warning prevented none of those stretches); renaming OCSF's sense (OCSF is the dependency).

## DD-26: The Case Takes Its Title From the Source

- **Decision:** A Case's title is OCSF `message` on the Incident Finding: the source's own title for the Case, kept in step with the source while the Case is open, or the first Alert's title where the source gives none. Mapped in the [Case Schema](../02-Taxonomy/case_schema.md).
- **Rationale:** A source that groups alerts retitles the group as alerts join, and a Case named after its first Alert drifts from what a reader opens in the source. OCSF has no `title` on Incident Finding, and `message` is the source's concise, human-readable description, which is what a title is.
- **Discarded alternatives:** the first Alert's title (stale once the source retitles the Case); a `title` under the `zerosoc` extension (OCSF already carries the concept).
- **Revisit:** if OCSF adds a title to Incident Finding.

## DD-27: Techniques Belong to the Observations, and the Incident's Are Assessed From Them

- **Decision:** Each Observation carries in its `attacks` the tactics and techniques it shows: an Alert those its detection asserted, and a Malicious Observation SHOULD carry those it establishes. The Case's `attacks` holds the Incident's, empty until the Incident is confirmed, then assessed from the Observations that stand and kept current through the response. Implemented in [Detection & Analysis §2.4–2.6](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), [Incident Response §1](../03-Processes/03-response.md#1-scope-confirmation) and the [Case Schema](../02-Taxonomy/case_schema.md).
- **Rationale:** The mapping a detection asserts is a first reading of one alert, often wrong or too broad. Left on the Alert, it can be checked there, and the Case's list keeps one meaning: what the Incident is known to have done. Each technique the Case names traces to the Observation that showed it, so a retraction takes the technique with it.
- **Discarded alternatives:** copying the Alerts' techniques to the Case at triage (gives a guess the standing of an assessment); assessing them once, at confirmation (the response reveals techniques the investigation did not see); techniques on the Case only (a retraction cannot remove one); a MUST on every Malicious Observation (some corroborate without showing a technique, such as a threat-intelligence match); the technique as a node of the attack graph, as Attack Flow models it (the graph's nodes are the Case's entities).
- **Revisit:** if the framework adopts Attack Flow, or OCSF gives a graph edge an attack object.

## DD-28: The Alert Carries Its Alert Type

- **Decision:** An Alert records the [alert type](../02-Taxonomy/alert_types.md) it is triaged under, as `alert_type` on its Observation. A source that writes its detections for the framework's alert types declares it; for any other Alert the executor identifies it at reception. Mapped in the [Case Schema](../02-Taxonomy/case_schema.md).
- **Rationale:** The alert type selects the triage playbook's section, proposes the candidate Incident Categories and decides which Alerts count once, yet the Case did not carry it, so a reviewer or another executor could not tell which section an Alert was triaged under. In OCSF, `finding_info.types` says what an entry rests on and `analytic` describes the detector in the source's own terms; neither carries a taxonomy the framework defines.
- **Discarded alternatives:** the analytic's `category` (a framework value would overwrite the source's own text); identifying the type again for every Alert, declared or not (it can contradict the rule the detection was written for).
- **Revisit:** if OCSF adds a classification of a finding against an external taxonomy.

## DD-29: One Extension Object, and a Case Identified by Its Correlation UID

- **Decision:** The framework's fields are the OCSF extension `zerosoc`, with the uid 984 requested in OCSF's extensions registry, declared in [ocsf_extension](../02-Taxonomy/ocsf_extension/extension.json). It adds one attribute, `zerosoc`, to the Incident Finding class and to the `finding_info` and `ticket` objects, and that attribute holds one object. A Case is identified by `metadata.correlation_uid`, the same on every event of the Case.
- **Rationale:** OCSF types an attribute once, in its dictionary, so one name holds one object wherever it appears. OCSF 1.9 gives an Incident Finding no identifier of its own across its Create, Update and Close events, and documents `correlation_uid` as the key that ties the events of one incident together.
- **Discarded alternatives:** three attribute names, one per place (renames keys every implementation writes); a root `uid` added to the class by the extension (an identifier of the framework's own beside the one OCSF documents); `metadata.uid` (since OCSF 1.7 it identifies each single event).
- **Revisit:** when OCSF gives the Incident Finding an identifier of its own, or lets an object's attribute hold another type than its dictionary's.

## DD-30: An Observation Cites Its Events, Kept With the Case as OCSF Events

- **Decision:** An Observation cites the events it rests on in its `related_events`, each citation's `uid` the cited event's `metadata.uid`. The events are kept with the Case as OCSF events of their own class, such as a Detection Finding for an Alert or a Process Activity for a process launched. Mapped in the [Case Schema](../02-Taxonomy/case_schema.md).
- **Rationale:** OCSF's related event is a citation. A process, its parentage and the script it ran belong to the event's own class, where OCSF's tools read them.
- **Discarded alternatives:** adding `process` and `script` to the related event through the extension (puts on a citation the objects OCSF keeps on events); the events embedded in the Case under `zerosoc` (a second copy of OCSF's event classes).
- **Revisit:** if OCSF gives the related event the objects of the event it cites, or a class that holds a finding with its evidence.

## DD-31: Governance Sized to a Small Team

- **Decision:** The project has two roles, Contributor and Maintainer. Everyday changes merge on green checks. A Design Decision on a `development` or `stable` document, a substantive change to a `stable` document and a governance change start with an issue and stay open for at least 72 hours with every objection answered. Promotion to `stable` keeps its non-author review. The Working Group discusses and does not vote. Implemented in [GOVERNANCE.md](../GOVERNANCE.md#2-decision-process).
- **Rationale:** A non-author review and 72 hours on every substantive pull request assumed more active reviewers than the project has, and those rules were not kept. The wait stays where a decision is hard to undo, and the review where a document becomes binding.
- **Discarded alternatives:** a review or 72 hours on every substantive change (holds up routine work when reviewers are few); a Working Group vote (membership is open and attendance varies, so a count would mean little).
- **Revisit:** when there are enough active Maintainers to review routine changes, and at the latest before `v1.0.0`.

## DD-32: An Incident Is Malicious Activity That Reached the Environment

- **Decision:** A Case is an Incident when its verdict is Malicious and its activity reached the environment: something landed on a device, ran, persisted, was delivered to a person, or was gained. Malicious activity that did not reach it is a **near miss**, closed without response. Every closing verdict other than an Incident sets `severity_id` to 1 (Informational). Defined in [Definitions](definitions.md#security-incident).
- **Rationale:** ISO/IEC 27035-1:2023 defines an incident as an event that "can harm an organization's assets or compromise its operations", and reach makes "can harm" something the evidence settles. OCSF has no value that tells a stopped attack from one that reached the environment, so severity carries it, and one severity for every non-incident close keeps automated triage from reading a closed Case as a live one. "Near miss" is the NIS2 term.
- **Discarded alternatives:** NIST SP 800-61r3's occurrences that "imminently" jeopardize an asset (a blocked attempt would be an Incident, and "imminent" has no test); `verdict_id` 8, Security Risk, for exposure without an attack (a further verdict and branch, which OCSF does not define).
- **Revisit:** if OCSF adds a value that tells a stopped attack from one that reached the environment, or if adopters' Cases show the reach test misclassifies.

## DD-33: Seven Gates From the Alert to the Closed Case

- **Decision:** The measurement gates follow a Case in order: G1 Alert(s) received, G2 triage disposition, G3 Incident declaration, G4 containment completed, G5 eradication verified, G6 recovery complete, G7 Case closed. The verdict review is an event outside that order, and the Case's status follows the gates. MTTC runs from G1 to G4. MTTR is Mean Time To Respond and starts at G1. Defined in [Operational Metrics §2](../05-Metrics/operational_metrics.md#2-measurement-gates).
- **Rationale:** The five earlier gates stopped at containment and counted a verdict review as G5, so nothing marked the end of response, and an implementation could resolve a source's incident while containment still waited for approval. MTTC from G1 measures response speed alone and stays put when the review moves T0 earlier.
- **Discarded alternatives:** G5 kept as the review, with the new gates after it (mixes positions in the order with a re-examination that can happen at any point); MTTC from T0 (repeats MTTD and changes after the fact); MTTR as Mean Time To Recover (in security operations MTTR most often means Respond).
- **Revisit:** where MTTR stops, still open on #85: containment completed (G4) or eradication verified (G5).

## DD-34: An Undecided Case Is Held, Never Closed by a Clock

- **Decision:** A Case whose Observations prove neither side goes On Hold with verdict Unknown once no discriminating query is left to run, and the questions whose answers could prove a side are asked. It closes as Insufficient Data only when no such evidence can be obtained. No clock closes a Case. Defined in [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence).
- **Rationale:** Closing at a timebox reported as closed a Case nobody had decided, and a source's console could show it as a False Positive. The verdict rests on the evidence, so the missing evidence is what to ask for. On Hold is OCSF's status for an incident waiting on information from a person or a third party.
- **Discarded alternatives:** Insufficient Data at timebox or budget expiry (a closed Case nobody decided); a watch window ending in a Benign close at Low confidence (weak against low-and-slow activity, and nobody is asked); assigning the Case to a person at expiry (the person faces the same evidence).
- **Revisit:** if adopters report Cases held without end because nobody answers.

## DD-35: Containment Autonomy Weighs the Risk of Waiting Against the Risk of Acting

- **Decision:** An executor applies a containment action without approval when the risk of waiting for a person is higher than the risk of acting, and the action's impact is not above the Incident's Impact. The risk of waiting combines the likelihood that the Incident is real with its Impact. The risk of acting combines the likelihood that it is false with the action's impact: what the organization cannot use while the action holds. Implemented in [Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment) and [Agentic Supervision §4](../07-Governance/agentic_supervision.md#4-autonomy-grant).
- **Rationale:** If the Incident is real, a person approves the containment anyway and waiting only adds the harm done meanwhile; if it is false, the disruption is paid only because the executor acted alone. The comparison holds only for an action that does no more harm than the Incident, hence the second condition. Impact is the input because severity already counts the criticality of the entities. Both risks come from one lookup. High, Medium and Low confidence give a High, Moderate and Low likelihood that the Incident is real, and the likelihood that it is false is the complement. An action of no impact has no risk of acting, and equal risks require approval:

  | Likelihood ↓ / impact → | Low | Medium | High | Critical |
  |---|---|---|---|---|
  | **High** | Low | Moderate | High | Very High |
  | **Moderate** | Low | Moderate | Moderate | High |
  | **Low** | Low | Low | Low | Moderate |

  Sources: NIST SP 800-30 Rev. 1 (the lookup, Table I-2); FIPS 199 (requirements per property); NIST SP 800-39; NIST CSF 2.0, GV.RM; NIST SP 800-34 Rev. 1; J. Wright, *Dynamic Incident Response*, 2026.
- **Discarded alternatives:** charging the action's full impact whatever the confidence (it needed a cap on large actions and then an exception to the cap); a fixed rule that Low confidence always requires approval (the comparison already yields it, except where being wrong costs nothing); a weighted numeric score (false precision on inputs that are judgments); a matrix that also rates eradication and recovery (their cost is not availability alone; open on #124).
- **Revisit:** when supervision data (the Approval Override Rate, rolled-back actions, approval dwell time) shows a cell set wrong.

## DD-36: The Scope of the Autonomy Grant Replaces the Handover

- **Decision:** The grant to close Cases should cover a Case whose scope includes a critical entity only when its closing verdict is at High confidence. Outside the grant the executor proposes the closure and a person decides. This replaces the handover, with its `handover_reason` field and the rule that made a Case's assignee a human. Implemented in [Agentic Supervision §4](../07-Governance/agentic_supervision.md#4-autonomy-grant) and [Operational Metrics §6.2](../05-Metrics/operational_metrics.md).
- **Rationale:** The handover was a rule on the executor's class, placed inside the process. Scoping the trust placed in an automated executor's verdict is what the grant exists for, so the limit belongs there and the process stays the same for every executor.
- **Discarded alternatives:** a closure-approval rule in the process for every executor (a person's close would wait for a second signature); no statement at all (leaves an automated wrong closure on a critical entity unguarded); a requirement in place of a recommendation (how far an organization trusts an executor's verdict is its own risk decision).
- **Revisit:** if QA sampling or the observed recall figures show wrong closures on critical entities at High confidence.
