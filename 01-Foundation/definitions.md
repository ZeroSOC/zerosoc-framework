---
title: Definitions
type: concept
status: development
last_updated: 2026-09-09
license: Apache-2.0
---

# Standard SecOps Definitions

These definitions establish a clear, standardized vocabulary for Security Operations (SecOps) terminology, based on the most widely adopted industry conventions (e.g., NIST, SANS). Disambiguating these terms is critical for efficient triage, incident response, and tool alignment. Crucially, enforcing a standardized vocabulary is essential for maintaining a vendor-agnostic architecture, ensuring that core operations, taxonomies, and playbooks translate seamlessly across diverse security tools, cloud environments, telemetry sources, and agentic orchestration platforms without proprietary terminology lock-in.

Where applicable, each term is mapped to its corresponding entity in the [Open Cybersecurity Schema Framework (OCSF) v1.8.0](https://schema.ocsf.io/1.8.0/categories).

## 1. Foundational Data & Activity

### Log Sources (Telemetry Sources)
The originators, assets, applications, security controls, or infrastructure components that generate logs, measurements, and security-relevant activity records. 
*   **Context:** Log sources are the origin points of raw telemetry before collection, parsing, forwarding, or normalization. In the ZeroSOC Framework, log sources are categorized across eight core **telemetry domains** (Endpoint, Identity, Network, Cloud, Email, Data, Application, and OT/ICS). Disambiguating the log source from the telemetry it emits is critical: the log source is the generating entity or software system (e.g., a Domain Controller, an EDR sensor, a Kubernetes API server, or a firewall appliance), whereas telemetry is the actual data stream emitted by that source.
*   **Examples:** the event log service on a domain controller, an EDR sensor on an endpoint, a cloud provider's control-plane audit log, a network security monitor, an identity provider's audit log exporter, or a next-generation firewall.
*   **OCSF Mapping:** Corresponds to the generating device, agent, or service context, represented in OCSF objects such as [Metadata (`metadata.log_provider`, `metadata.product`, `metadata.version`)](https://schema.ocsf.io/1.8.0/objects/metadata), [Device](https://schema.ocsf.io/1.8.0/objects/device), [Agent](https://schema.ocsf.io/1.8.0/objects/agent), or [Cloud](https://schema.ocsf.io/1.8.0/objects/cloud).

### Telemetry (Raw Data)
The raw, unprocessed data streams continuously emitted by endpoints, network devices, cloud services, and applications. 
*   **Context:** Telemetry is the foundational layer of visibility—the "source of truth." It is high in volume, low in immediate context, and typically requires parsing before it can be actively used for detection or hunting. The primary difference from an Event is that Telemetry is a continuous state or measurement, whereas an Event is a discrete occurrence.
*   **Examples:** Raw packet captures (PCAP), unfiltered EDR activity traces, basic firewall connection logs.
*   **OCSF Mapping:** Corresponds to native, unparsed source payloads prior to schema transformation (represented conceptually in OCSF via raw payload structures or the `unmapped` attribute container). ZeroSOC strictly avoids normalizing raw telemetry into OCSF to drastically reduce compute costs. ZeroSOC uses such elements only during investigations.

### Events
Records of specific, defined actions or occurrences that happened within the IT infrastructure. Events are discrete, typically parsed and normalized extracts derived from raw telemetry.
*   **Context:** While an event indicates a significant change in state or an activity took place, it does not inherently imply malicious intent. It is just a record of "what happened" and "when."
*   **Examples:** A user successfully authenticating, a process starting, a file being modified, or a service shutting down.
*   **Reference:** [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) — Defines the foundational difference between an *Event* and a *Cybersecurity Incident*.
*   **OCSF Mapping:** Maps across OCSF's operational activity categories, primarily: **Category 1 (System Activity)** (e.g., [Process Activity [1007]](https://schema.ocsf.io/1.8.0/classes/process_activity), [File Activity [1001]](https://schema.ocsf.io/1.8.0/classes/file_activity), [Log Activity [1008]](https://schema.ocsf.io/1.8.0/classes/log_activity)), **Category 3 (IAM)** (e.g., [Authentication [3002]](https://schema.ocsf.io/1.8.0/classes/authentication)), **Category 4 (Network Activity)** (e.g., [Network Activity [4001]](https://schema.ocsf.io/1.8.0/classes/network_activity), [HTTP Activity [4002]](https://schema.ocsf.io/1.8.0/classes/http_activity), [DNS Activity [4003]](https://schema.ocsf.io/1.8.0/classes/dns_activity)), and **Category 6 (Application Activity)** (e.g., [API Activity [6003]](https://schema.ocsf.io/1.8.0/classes/api_activity)). Similar to Telemetry, ZeroSOC strictly avoids normalizing general events into OCSF to reduce compute costs, utilizing them only during investigations.

### Signals
Observable occurrences (often derived from events or groups of events) that have security relevance but are not immediately actionable or necessarily malicious on their own.
*   **Context:** Signals are structurally similar to Security Alerts, representing parsed and filtered security observations. However, they differ in operational intent: a single signal does not require immediate human triage or an active investigation (e.g., they are treated as *Informational*). Instead, they act as telemetry/contextual building blocks. When correlated or when a specific threshold of signals is met, they generate an actionable Security Alert.
*   **Examples:** An unusual spike in network traffic, a login from a new geographic location, or the execution of a rarely used administrative tool.
*   **OCSF Mapping:** Maps to [Detection Finding [2004]](https://schema.ocsf.io/1.8.0/classes/detection_finding) — the **same class as a Security Alert**, discriminated by **`severity_id`**. A Signal is *always* **Informational (`severity_id = 1`)** and therefore does **not** trigger the triage/investigation workflow; it is a correlation building block. A Detection Finding at `severity_id ≥ Low (2)` is a Security Alert, not a Signal.

### Entity
A discrete actor, asset, or artifact involved in security-relevant activity — the "who" and "what" that Telemetry, Events, and Alerts are *about*. Entities are the **nouns** of Detection & Response: extracted from raw data, normalized to a common schema, and enriched with context during Triage.
*   **Context:** Entities are the **join keys** of an investigation. Correlating on shared entities — the same user, host, or IP recurring across multiple alerts — is what bounds the scope of a Security Case and drives the domain → Incident Category pivot at the Triage → Investigation phase transition contract. **Entity enrichment** (adding Threat Intelligence, asset/CMDB, and identity context) turns a bare identifier into an actionable picture. Entities are commonly typed as **identity** (user, account, service principal), **asset** (host/device, cloud resource, application), **network** (IP address, domain, URL), and **artifact** (file, hash, process, registry key, email message).
*   **Examples:** A user `jdoe`, a host `FIN-LAPTOP-07`, the IP `203.0.113.10`, a SHA-256 file hash, a process `powershell.exe`, a sender domain.
*   **Entity vs. Observable/Indicator:** We define **entity** broadly as any typed, correlatable pivot (user, host, IP, file, process). An entity and its indicators represent the same concept at different granularities: a complex object (e.g., `User`, `File`) is the entity, while a scalar property of it (e.g., username, file hash, IP address) functions as its indicator.
*   **OCSF Mapping & Type ID Bands:** OCSF maps both entities and indicators to the [Observable](https://schema.ocsf.io/1.8.0/objects/observable) object, differentiating them using a `type_id` enum divided into two bands:
    *   **Scalar / Primitive Types (IDs < 20):** Represent basic properties or values (the indicator layer), such as `1` = Hostname, `2` = IP Address, `4` = User Name, `6` = URL String, or `8` = Hash.
    *   **Full Entity Objects (IDs ≥ 20):** Represent complete OCSF entity objects, such as `20` = Endpoint/Device, `21` = User, `24` = File, or `25` = Process.
    An observable with a `type_id` in the upper band (20+) maps directly to a full entity object, whereas a `type_id` in the lower band maps to a scalar property/indicator belonging to that entity. Every OCSF event surfaces these pivots in a top-level `observables[]` array of `{ name, type_id, value }` structures.

---

### SOC Knowledge Base (SOC KB)
The organization's institutional knowledge about its own environment, maintained by the SOC for use during triage, investigation and response: VIP and high-risk users, approved exceptions and known-benign activity, naming conventions, network ranges and diagrams, vulnerability-scan and maintenance schedules, business-critical (Crown Jewel) assets, and the lessons learned from past Incidents.
*   **Context:** Many security teams keep this knowledge in internal documentation of varying structure and maturity, often to compensate for an incomplete CMDB. The framework treats it as a foundational component: it is an enrichment source in Triage (Organizational Context, [Detection & Analysis §1.2](../03-Processes/02-detection_and_analysis.md#12-multi-vector-context-enrichment)), it receives the lessons learned of Post-Incident Activity, and it is maintained as part of Preparation & Engineering. Because every executor — human, automation or agent — reads the same knowledge base, it is the mechanism by which institutional knowledge reaches automated execution.
*   **OCSF Mapping:** None. The knowledge base is a source consulted during enrichment; the facts drawn from it are recorded in the Triage Note and Investigation Note as findings with references.

## 2. Detection & Investigation Entities

### Security Alerts
A high-priority notification generated by security tools (like SIEM, SOAR, or EDR) indicating a potential security threat that requires human or automated attention. Alerts are generated when events or signals match predefined conditions or correlation rules.
*   **Context:** This is the primary trigger for a SOC workflow. Alerts represent specific, point-in-time behaviors. 
*   **OCSF Mapping:** Maps directly to [Detection Finding [2004]](https://schema.ocsf.io/1.8.0/classes/detection_finding) in the Findings category. Key attributes include `confidence`, `severity_id`, `risk_level_id`, and `attacks` (for [MITRE ATT&CK®](https://schema.ocsf.io/1.8.0/objects/attack) mapping). An Alert is a Detection Finding with **`severity_id ≥ Low (2)`**; an Informational (`severity_id = 1`) Detection Finding is a **Signal**, not an Alert, and does not enter triage.
*   **Platform Nomenclature: (illustrative)** 
    *   **Splunk:** Often referred to as *Notable Events*. (See: [Splunk Notable Events Documentation](https://docs.splunk.com/Documentation/ES/latest/User/Workwithnotableevents))
    *   **Microsoft Sentinel:** Historically and confusingly referred to as *Incidents* (though standard industry parlance reserves "incident" for a confirmed breach). (See: [Sentinel Incidents Documentation](https://learn.microsoft.com/en-us/azure/sentinel/investigate-incidents))
    *   **CrowdStrike:** *Detections*.

### Security Cases
A broader, administrative workspace used to manage the investigative workflow. It is the logical container where analysts document activities, gather evidence, and track progress.
*   **Context:** A case can be opened as soon as an alert fires. A single case may group together multiple related Security Alerts, Signals, and Event Logs. It is the tactical "investigation folder." 
*   **Outcome:** A closed case will ultimately be dispositioned (e.g., as an Incident, a False Positive, or a Benign Positive).
*   **OCSF Mapping:** A Case maps to [Incident Finding [2005]](https://schema.ocsf.io/1.8.0/classes/incident_finding) — the aggregation object that groups the constituent [Detection Findings [2004]](https://schema.ocsf.io/1.8.0/classes/detection_finding) (Alerts) and carries the case verdict — in a **pre-confirmation** state: `verdict_id` still open (Unknown `0` / Suspicious `4` / Insufficient Data `7`) and `status_id` New (`1`) / In Progress (`2`). Workflow metadata can additionally be tracked via the [Ticket](https://schema.ocsf.io/1.8.0/objects/ticket) object. A Case becomes a **Security Incident** only when its verdict is confirmed (see below).

*   **Data model:** the fields a Case carries — OCSF fields and the framework's own — are defined once in the [Case Schema](../02-Taxonomy/case_schema.md).

### Security Incidents
An event (or series of events) that has been investigated through a case and **verified as a confirmed security threat** or a serious violation of security policies. 
*   **Context:** This represents an actual or imminent compromise of confidentiality, integrity, or availability. Escalating a case to an incident fundamentally shifts the workflow from *investigation* to *Incident Response (IR)* (containment, eradication, recovery).
*   **OCSF Mapping:** The **same class as a Case** — [Incident Finding [2005]](https://schema.ocsf.io/1.8.0/classes/incident_finding) — discriminated by **`verdict_id`**. A Case becomes a confirmed Security Incident when **`verdict_id = 2` (True Positive)** (optionally `is_suspected_breach = true`); this is the promotion gate into Phase 3. Other key attributes: `priority_id`, `impact_id`, `status_id`, and `assignee` / `src_url` (ticketing links). A closed non-incident Case carries `verdict_id` False Positive (`1`) or Benign (`5`).
*   **Reference:** [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) — Formal definition of a *Computer Security Incident*. See also ISO/IEC 27001 (Information security management).

### OCSF class-sharing note (Signal vs Alert, Case vs Incident)

Two ZeroSOC concept pairs share a single OCSF class and are told apart by one attribute:
*   **Signal vs Alert** — both are [Detection Finding [2004]](https://schema.ocsf.io/1.8.0/classes/detection_finding); discriminator `severity_id` (Signal = Informational `1`; Alert = `≥ Low 2`). Only Alerts trigger triage.
*   **Case vs Incident** — both are [Incident Finding [2005]](https://schema.ocsf.io/1.8.0/classes/incident_finding); discriminator `verdict_id` (Incident = confirmed True Positive `2`). The NIST/ISO "incident" is the confirmed sub-state of a Case, not a separate object. Reference: [OCSF discussion #1375](https://github.com/ocsf/ocsf-schema/discussions/1375).

---

## 3. Case Dispositions (Verdicts)

When a Security Case is investigated, a final determination or verdict is reached to disposition the case, track detection accuracy, and emit tuning feedback.

In OCSF, these dispositions are represented by the `verdict_id` enum on [Incident Finding [2005]](https://schema.ocsf.io/1.8.0/classes/incident_finding).

### True Positive (TP)
An alert that correctly identifies actual malicious activity or a genuine policy violation.
*   **Outcome:** Escalates to a Security Incident.
*   **OCSF `verdict_id`:** `2` (True Positive)
*   **Reference:** [MITRE ATT&CK & D3FEND](https://attack.mitre.org/) - Broadly useful for understanding the behavioral context of true positive signals.

### False Positive (FP) Cases
Cases where an alert was generated, but triage reveals the system misinterpreted benign or normal activity as malicious. 
*   **Context:** This represents a "technical error" by the detection logic. The activity did not pose a threat, and it shouldn't have been escalated as an incident.
*   **Outcome:** The case is closed, and the feedback must be used for detection or triage playbook tuning to reduce noise.
*   **OCSF `verdict_id`:** `1` (False Positive)

### Benign Positive (BP) Cases
Cases where the detection tool worked exactly as intended and correctly identified specific behavior, but triage determines the activity was authorized, expected, or harmless.
*   **Context:** This is a "contextual issue" rather than a technical misfiring. The rule accurately spotted an action (like a script running), but no breach occurred because the actor was legitimate. The activity looks malicious, but was specifically authorized.
*   **Examples:** Authorized penetration tests, scheduled vulnerability scans, or an IT administrator executing a remote administration script.
*   **Outcome:** The case is closed. Benign Positives typically require minor tuning such as whitelisting to reduce noise.
*   **OCSF `verdict_id`:** `5` (Benign)

### Duplicate
A Case closed because its activity, root cause and threat vector are already handled by an open master Case, and the recurrence adds neither risk nor evidence to it.
*   **Context:** Permitted at triage or during investigation only after the validation criteria of [Detection & Analysis §1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision) are met — matching core entities, overlapping timeline, active ownership of the master Case, evidence merged — and never on the strength of a shared rule name, a different affected entity, or a recurrence long after the prior Case was resolved.
*   **OCSF `verdict_id`:** `10` (Duplicate). The closing Note records the master Case identifier.

### False Negative (FN)
Malicious activity that occurred but failed to generate a Security Alert. (Not a direct case classification, but a critical metric for SOC health representing "missed detections").

### True Negative (TN)
Benign activity that correctly did *not* trigger any alarms. (The normal, silent operation of the environment).

---

## 4. Playbook & Response Terminology

### Playbook
A standardized, structured procedure detailing the analytical, investigative, and response actions for a specific domain or incident category. Playbooks define required telemetry inputs, hypothesis validation queries, containment/eradication procedures, completion criteria, and governance boundaries.
*   **Context:** ZeroSOC Framework adopts a modular two-layer playbook architecture: **Domain Triage Playbooks** (for front-line alert validation and prioritization) and **Incident Category (IC) Investigation & Response Playbooks** (for concurrent Malicious/Benign hypothesis testing and response).
*   **Terminology Note:** In the broader industry or depending on the specific SOAR vendor, these are often referred to as "Runbooks." To avoid ambiguity, the ZeroSOC Framework exclusively uses the term *Playbook* and intentionally omits the use of the term *Runbook*.

### Triage
The initial, high-velocity analytical phase (System 1 fast-thinking) of evaluating an Alert or Case to enrich context, validate technical authenticity, recalibrate operational priority (Severity and Confidence), and determine immediate disposition: either closing the case as a False Positive or Benign Positive (emitting tuning feedback) or promoting it to active investigation under a candidate Incident Category.
*   **Context:** In the ZeroSOC Framework, Triage acts as a rapid prioritization, scoping, and validation engine. It extracts entity context, correlates historical baselines, independently calculates true operational severity (never accepting raw vendor scores blindly), and executes the primary triage decision gate (Gate G2) to resolve obvious noise at high speed and route genuine potential threats into deep investigation.

### Investigation
The diagnostic analytical process of testing competing hypotheses, reconstructing adversary actions, determining attack scope and blast radius, and establishing a definitive case verdict.
*   **Context:** In the ZeroSOC Framework, Investigation is governed by the **Concurrent Malicious/Benign hypothesis Engine** ([Detection & Analysis §2](../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation)). It systematically executes deep-dive queries across endpoint, identity, network, and cloud telemetry to seek evidence that confirms or invalidates competing hypotheses (Malicious True Positive vs. Benign). The outcome of an investigation is a conclusive **Case Verdict** (documented in an Investigation Note), which either closes the case (False Positive / Benign) or promotes it to a confirmed **Security Incident** for immediate containment and eradication.

### Containment
Short-term, tactical actions taken to stop an active threat from spreading or causing further damage. Containment must happen *before* eradication.
*   **Context:** Per NIST SP 800-61 Rev. 3, containment is about risk mitigation. Examples include isolating a host from the network, disabling an account, or blocking an IP address at the firewall.

### Eradication
The process of permanently removing the threat actor's access and malicious artifacts from the environment.
*   **Context:** Eradication happens after successful containment. Examples include deleting malware, rebuilding an infected system from a known-good image, and rotating compromised credentials.

### Recovery
The steps taken to restore systems and data to their normal, pristine operational state.
*   **Context:** Examples include restoring data from offline backups, lifting containment controls (like network isolation), and verifying that systems are functioning correctly without reinfection.

### Post-Incident Activity (Lessons Learned & Root Cause Analysis)
The retrospective phase of evaluating confirmed incidents or major false-positive disruptions to identify root causes, extract lessons learned, and convert operational findings into engineering and detection improvements.
*   **Context:** Aligned with NIST SP 800-61 Rev. 3 (Post-Incident Activity) and ISO/IEC 27035 (Lessons Learned), this phase conducts a blameless Root Cause Analysis (RCA) categorizing failures across four systemic buckets (Telemetry Gaps, Software Flaws, Human/Configuration Errors, Policy/Process Deficiencies) and generating actionable tickets for detection tuning, playbook updates, and infrastructure hardening.

---

### Phase Transition Contract
The defined set of Case fields that a Case carries when it moves forward from one phase to the next — from Triage to Investigation on promotion, from Investigation to Response on confirmation. A data boundary, specified once in the [Playbook Architecture](../04-Playbooks/playbook_architecture.md#5-phase-transition-contracts-ocsf-aligned) as subsets of the [Case Schema](../02-Taxonomy/case_schema.md). A closed Case carries none.

## 5. Measurement & Performance Terminology

These three terms form a chain: the framework defines **metrics**; an organization elevates some of them to **KPIs**; and it calibrates a target **KPO** for each KPI it tracks. See [Operational Metrics](../05-Metrics/operational_metrics.md) for the operational detail — this is its canonical definitional home.

### Metric
A quantitative measure defined in [Operational Metrics](../05-Metrics/operational_metrics.md) with a mathematically precise formula, explicit numerator and denominator, and defined boundary rules (including duration metrics anchored to OCSF state transitions, as well as quality, cost, and coverage measures).
*   **Context:** A metric is descriptive — it carries no target. Detection Precision, MTTA, and Token Cost per Case are all metrics whether or not any organization tracks them as KPIs.

### Key Performance Indicator (KPI)
A metric an organization elevates to actively steer Security Operations: tracked over time, sliced by executor, and reviewed at a defined governance cadence.
*   **Context:** KPI selection is an organizational decision, not a framework mandate. The framework marks its recommended default KPI candidates — the metrics carrying [§9](../05-Metrics/operational_metrics.md#9-reference-bands-for-setting-kpos) reference bands — as **KPI candidate** in [Operational Metrics](../05-Metrics/operational_metrics.md); an organization may adopt, extend, or replace that set.

### Key Performance Objective (KPO)
The concrete target value or band an organization commits to for a KPI, calibrated to its own baseline (alert mix, telemetry coverage, risk tolerance).
*   **Context:** The framework itself sets no KPOs. [Operational Metrics §9](../05-Metrics/operational_metrics.md#9-reference-bands-for-setting-kpos) publishes illustrative reference bands — inputs for setting KPOs, not targets — which become KPOs only once an organization adopts and calibrates them to its own baseline.

## 6. Executors and Functions

The framework describes *who* performs work at two levels: the **executor** that carries out a step, and the **function** that step belongs to. Neither is a job title or a tier.

### Executor
The party that carries out a process step or playbook: a **human analyst**, **deterministic automation** (rule-based scripts and orchestration workflows), or an **autonomous AI agent** — or any blend of the three. Every process and playbook is executable by any executor class (Executor Neutrality, per the [Framework Manifest](framework_manifest.md#executor-neutrality-and-human-readability)). The **Provenance** field of a deliverable records which executor performed each step, so every metric can be sliced by executor without changing its definition.

### Function
A named area of responsibility that any executor class may fulfill. Functions are **peer functions in a tier-less model** (see the [Framework Manifest](framework_manifest.md#tier-less-operating-model)): work is routed by skill and by risk through explicit handover boundaries, never up a seniority ladder, and the executor that takes a Case owns it to conclusion — through investigation and response alike. Ownership changes only under the handover conditions the processes define; skill-based routing happens at intake, not mid-Case. The framework uses the following function names throughout; organizations map their own titles onto them.

| Function | Responsibility | Primary phases |
| :--- | :--- | :--- |
| **Security Analyst** | Own a Case end to end: acknowledge, enrich, scope, prioritize and decide Close-or-Promote; investigate to a verdict, producing the Triage Note and Investigation Note; then contain, eradicate and recover the Incident the Case becomes, and contribute its post-incident review. Referred to as *Analyst* in process and playbook text. | Phase 2, Phase 3, Phase 4 |
| **Detection Engineer** | Author, test, tune and version-control detection logic (Detection-as-Code), and act on the tuning signals that closed Cases emit. | Phase 1, Phase 4 |
| **Security Platform Engineer** | Deploy, integrate and maintain the security tooling and telemetry pipelines — SIEM, SOAR, EDR/XDR, log collection — including log-source onboarding and health. Often staffed by the same team as Detection Engineering, with distinct skills; commonly titled *SOC Engineer* or *SIEM Engineer*. | Phase 1 |
| **Threat Hunter** | Formulate and test hunt hypotheses against telemetry, operationalize threat intelligence, and open Cases for threats that bypassed detection logic. | Phase 2 |
| **SOC Manager** | Own the operating model and its oversight: capacity, quality-assurance supervision of autonomous dispositions, metrics review, and the interface to enterprise risk management. For declared Incidents, own the interface to enterprise incident management — regulatory notification timelines and stakeholder coordination (the *Incident Coordinator* of ISO/IEC 27035). | Phase 3, Phase 4, cross-phase |

### Handover
The transfer of a Case's **ownership** (OCSF `assignee`) from one executor to another — in the framework, from automation or an agent to a human — under the conditions that the processes define ([Detection & Analysis §2.3](../03-Processes/02-detection_and_analysis.md#23-conditions-requiring-human-ownership-handover)). A handover moves responsibility for the Case and its verdict; it is not a data boundary (that is the phase transition contract) and it does not by itself stop pre-authorized containment.

## 7. Classification Levels

Every Case carries three measures, defined in the [Case Schema](../02-Taxonomy/case_schema.md) and assessed in [Detection & Analysis](../03-Processes/02-detection_and_analysis.md#14-case-classification-severity-confidence--impact): **Severity** ("how bad"), **Confidence** ("how sure") and **Impact** ("how much harm"). The levels below are the framework's readable definitions; the numeric values are OCSF's.

### Severity (OCSF `severity_id`)
Severity estimates the *potential* harm of the observed activity and sets the urgency of the response. It combines the threat severity of the behavior with the criticality of what it touches.

| Level | OCSF meaning | Framework guidance | Example |
|---|---|---|---|
| **1 Informational** | Informational message; no action required. | A Signal, not an Alert. Consulted during triage, never triaged on its own. | A single failed login; a new process seen for the first time on a host. |
| **2 Low** | The user decides if action is needed. | Suspicious but contained in scope; routine triage, no deadline pressure. | A password spray blocked by lockout on standard accounts. |
| **3 Medium** | Action is required but the situation is not serious at this time. | Likely malicious or policy-relevant activity on non-critical entities; investigate within the shift. | Commodity malware detected and quarantined on a standard workstation. |
| **4 High** | Action is required immediately. | Malicious activity with a credible path to material harm, or touching a critical entity; investigate now, response likely. | Credential dumping on a server; a privileged role granted outside change control. |
| **5 Critical** | Action is required immediately and the scope is broad. | Active, spreading or Crown-Jewel-level threat; response and notification run in parallel with investigation. | Ransomware propagating; domain controller compromise; confirmed exfiltration of regulated data. |

### Confidence (OCSF `confidence_id`)
Confidence is the likelihood that the Malicious hypothesis is true. OCSF names the levels without defining them; the framework binds them to the evidence resolution rule of [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence).

| Level | Definition | Example |
|---|---|---|
| **1 Low** | The hypothesis is plausible but rests on a single supporting finding, on ambiguous evidence, or on findings with an unresolved contradiction. Not sufficient to act autonomously. | A reputation lookup flags a domain on one engine out of many; nothing else corroborates. |
| **2 Medium** | The hypothesis is proven by two or more independent, convergent supporting findings, with no strongly-supporting finding. Sufficient for a verdict; autonomous containment requires human review. | An unusual process plus an outbound connection to a newly registered domain, each explainable alone, together not. |
| **3 High** | The hypothesis is proven by at least one unrebutted strongly-supporting finding. Sufficient for a verdict and for pre-authorized autonomous containment. | Multi-engine hash consensus on a known malware family; a decoded command line that stages a payload. |

A visibility gap — a required data source unavailable during triage or investigation — caps Confidence at Medium regardless of the findings, because the missing source could have contradicted them.

### Impact (OCSF `impact_id`)
Impact records the *realized or expected* harm of a confirmed or suspected Incident. The framework assesses it on three effects, after NIST SP 800-61 — **functional** (services and operations), **informational** (confidentiality and integrity of data) and **recoverability** (time and effort to recover) — and binds the top level to the NIS2 significance test. Impact is assessed at triage when already known and otherwise at incident confirmation; until assessed it is recorded as unknown, never guessed.

| Level | OCSF meaning | Framework definition | Example |
|---|---|---|---|
| **1 Low** | The magnitude of harm is low. | Minimal or no effect on services; no data compromised; recovery within normal operations. | Malware quarantined before execution on one workstation. |
| **2 Medium** | The magnitude of harm is moderate. | A non-critical service degraded or one business unit affected; non-sensitive data accessed; recovery with supplemented resources within the day. | A compromised standard account used to read internal, non-regulated documents. |
| **3 High** | The magnitude of harm is high. | A critical service disrupted or a Crown Jewel affected; regulated or proprietary data breached; extended recovery. | Ransomware on a production file server with backups intact. |
| **4 Critical** | The magnitude of harm is high and the scope is widespread. | Severe operational disruption or financial loss, or considerable damage to other persons or organizations — the NIS2 Article 23 significance test — or harm that cannot be recovered. Triggers regulatory notification. | Enterprise-wide ransomware with backups destroyed; exfiltration of customer personal data at scale; a cross-border outage of a regulated service. |

The **significant** and **cross-border** flags of the Case Schema are set from this assessment; a Critical Impact is always significant, and a High Impact is significant when the NIS2 criteria are met.
