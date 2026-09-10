---
title: SOC Operational Metrics
type: concept
status: draft
last_updated: 2026-09-10
license: Apache-2.0
description: Process-anchored volume, speed, quality, autonomy and token-economics metrics for the detection and response pipeline
---

# SOC Operational Metrics

> **Draft.** This module defines the small set of metrics the operating loop can compute from its own records. Metrics that need a program the Roadmap stages later — adversary emulation, hunting, coverage economics — are listed in the Roadmap's backlog, not here. Expect the reference bands to change as adopters report their baselines.

Every metric in this module is anchored to a defined state transition in the [Detection & Response Lifecycle](../03-Processes/00-detection_and_response_lifecycle.md): if a metric's start and stop cannot be pointed to as a field change on the [Case](../02-Taxonomy/case_schema.md), the metric is not conformant. Speed alone does not measure security, and in an autonomous SOC **automation volume alone measures nothing**: "95% of alerts closed automatically" describes equally a world-class autonomous SOC and a noisy detection stack flushing its own garbage. The metrics below make those two worlds distinguishable: they measure noise at each pipeline stage, pair every autonomy metric with a quality counterweight, and price the compute that autonomous operations consume.

**Terminology** (canonical definitions in [Definitions §5](../01-Foundation/definitions.md#5-measurement--performance-terminology)). A **metric** is a measure defined below with a formula and a gate (§2); it is descriptive and carries no target. A **KPI** is a metric an organization elevates to steer Security Operations: tracked over time, sliced by executor, reviewed at a governance cadence. The framework marks its recommended candidates; the selection is the organization's. A **KPO** is the target value or band an organization commits to for a KPI, calibrated to its own baseline; the framework sets none, and the reference bands of §8 are inputs for setting them.

## 1. Measurement Principles

1. **Process-anchored.** Each metric starts and stops at a measurement gate (§2), a defined state transition on the Case. No gate, no metric.
2. **Precise.** A conformant metric states its numerator, its denominator and its boundary rules: what is included, what is excluded, where the edge cases fall.
3. **Vendor-agnostic.** Metrics are computed from Case fields and framework deliverables — Cases, Notes, attributed action logs — never from a product's built-in dashboard definitions, which are neither portable nor comparable.
4. **Executor-neutral.** A metric's definition is identical whether the work was performed by a human, automation or an agent, or a blend. The **Provenance** element of the [Triage Note and Investigation Note](../03-Processes/02-detection_and_analysis.md) records the executor, so every metric can be *sliced* by executor; the definition never changes.
5. **Computable from the audit trail.** Every input already exists as an artifact the framework mandates elsewhere: Note provenance, Case-attributed actions ([Agentic Guardrails](../07-Governance/agentic_guardrails.md)), QA sampling records ([Agentic Supervision](../07-Governance/agentic_supervision.md)). Measurement is a by-product of auditability, never a parallel bookkeeping.
6. **Paired reporting.** When a measure becomes a target it stops measuring: optimizing a speed or automation metric alone degrades the quality it was meant to serve. Efficiency metrics are non-conformant unless reported with their quality counterweight (§6.4).
7. **Distributions, not averages.** A 20-minute average is compatible with "everything takes 20 minutes" and with "everything takes 5 minutes except one six-hour outlier". Time metrics are reported as **median and 95th percentile**, per severity band. The "Mean Time To" names are kept for interoperability; the mean alone is never a conformant report.
8. **Bands, not extremes.** Most quality metrics have a healthy *band*: a 100% Promotion Precision means triage closes too aggressively and breeds false negatives; a 0% noise share means detections are tuned so tightly they detect nothing new.
9. **Few metrics.** Publish the handful that are acted on; keep the rest as diagnostics.

## 2. Measurement Gates

All metrics reference the five gates below. Objects and verdicts are as defined in [Definitions](../01-Foundation/definitions.md) and the [Case Schema](../02-Taxonomy/case_schema.md); the pipeline is Telemetry → Events → Signals → **Alerts → Cases → Incidents**.

| Gate | State transition | Process anchor |
|---|---|---|
| **G1 — Alert raised** | `Detection Finding [2004]` created with `severity_id ≥ Low (2)` | [Phase 1](../03-Processes/01-preparation_and_engineering.md) output |
| **G2 — Triage decision** | Case closed (`verdict_id` False Positive `1`, Benign `5`, Duplicate `10`) **or** promoted to Investigation | [Detection & Analysis §1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision) |
| **G3 — Investigation verdict** | Case closed (`verdict_id` `1`, `5`, `10`, Insufficient Data `7`) **or** confirmed Incident (`verdict_id = 2`) | [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence) |
| **G4 — Containment** | A containment action applied and confirmed | [Incident Response §2](../03-Processes/03-response.md#2-containment) |
| **G5 — Review** | A verdict re-examined: an approval rejected or a containment rolled back, [QA sampling](../07-Governance/agentic_supervision.md), or the [Post-Incident Review](../03-Processes/04-post_incident_activity.md) | Governance and Phase 4 |

**Denominator discipline.** Alerts consolidated by the deduplication, throttling and aggregation rules applied at reception ([Detection & Analysis §1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment)) never enter triage and are excluded from every triage denominator and from every *automation* numerator: consolidation is plumbing, not a verdict. A Case closed as **Duplicate** is merged into its master Case and leaves every denominator the same way. A Case closed as **Insufficient Data** is a disposition — it counts in the denominators — but it is neither noise nor an Incident; the Disposition Mix (§5.2) reports it on its own.

## 3. Volume Metrics

Context metrics: they size the pipeline so that the rates and costs downstream are interpretable. Reported per telemetry domain and per [Alert Type](../02-Taxonomy/alert_types.md).

*   **Alert Volume:** G1 alerts per window. The capacity-planning input, never a performance metric: a SOC "improving" by alerting less may just be seeing less.
*   **Consolidation Rate:** alerts consolidated at reception (deduplicated, throttled, aggregated into an existing Case) ÷ alerts generated. Reported separately from every verdict metric per the denominator discipline; in practice most of a headline "auto-close" number is consolidation, not verdicts. A rising rate is better correlation *or* a campaign in progress: the Campaign Check of [Detection & Analysis §1.3](../03-Processes/02-detection_and_analysis.md#13-scope--correlation-analysis) tells the two apart.

## 4. Speed Metrics

**T0** is the anchor of every speed metric: the timestamp of the *earliest confirmed malicious* event in the Case Timeline, established during Investigation ([Detection & Analysis §2.5](../03-Processes/02-detection_and_analysis.md#25-investigation-note-verdict-evidence-record)) and refined in the Post-Incident Review. A Case closed without the Malicious hypothesis proven carries no T0, so T0-anchored metrics exist only for confirmed Incidents. All speed metrics: median and p95, per severity band.

### Mean Time To Detect (MTTD)
*   **KPI candidate.**
*   **Start:** T0. **Stop:** the originating Alert raised (G1).
*   **Two populations, never blended:** Incidents whose originating Alert was produced by Phase 1 detection content, and Incidents discovered by threat hunting or out-of-band intake ([Detection & Analysis §4.3 and §5](../03-Processes/02-detection_and_analysis.md)), for which the stop is the registration of the Alert by that step. The second population is the cost of a miss expressed in time; averaging it into the first hides it.

### Mean Time To Investigate (MTTI)
*   **KPI candidate.**
*   **Start:** the originating Alert raised (G1). **Stop:** the Case's disposition — closed at G2, or closed or confirmed at G3.
*   **Purpose:** the end-to-end throughput of Detection & Analysis. It stops at a *verdict*, not at queue removal, which is what makes it the honest replacement for "we close alerts fast". Sliced by the gate at which the Case was dispositioned, since triage-stage and investigation-stage verdicts run on different clocks.

### Mean Time To Contain (MTTC)
*   **KPI candidate.**
*   **Start:** T0. **Stop:** the first containment action applied and confirmed (G4).
*   **Boundary rule:** MTTC **excludes HITL Dwell Time**. If an executor proposes containment and waits four hours for approval, those hours measure the organization's approval loop, not the operation's capability; mixing them makes fast executors look slow and hides slow approvers.

### HITL Dwell Time
*   **KPI candidate.**
*   **Start:** an action enters `Pending HITL`, or a Case is handed over ([Agentic Supervision §1](../07-Governance/agentic_supervision.md)). **Stop:** the approver decides, or the human assignee takes the Case.
*   **Purpose:** the human-side target, tracked per class: approval requests and handovers. The number to fix when MTTC is excellent but Incidents still run long.

### Mean Time To Recover (MTTR)
*   **Start:** T0. **Stop:** recovery complete — services restored and containment lifted ([Incident Response §4](../03-Processes/03-response.md#4-recovery)).
*   **Purpose:** the full duration of the Incident as the organization experienced it. Where MTTC measures how fast the threat was stopped, MTTR measures how long it cost.

## 5. Disposition Quality

A single "false positive rate" is not a metric; it is an ambiguity. The term conflates detection failures with correctly detected but benign activity, and the famous "99% false positive rate" is mostly benign triggers, not a measure of the technology (§10). The framework measures noise **per verdict and per gate**: noise caught at triage costs triage capacity, while a wrongly confirmed Incident costs the trust of asset owners and leadership, and those are different failures with different owners.

**Verdict split.** False Positive (`verdict_id 1`, detection failure → tuning ticket) and Benign (`verdict_id 5`, context gap → Knowledge Base entry) are tracked separately at every gate; their remediation paths differ ([Definitions §3](../01-Foundation/definitions.md#3-case-dispositions-verdicts)). "Noise" below means the two together.

### 5.1 Detection Precision
*   **KPI candidate.**
*   **Definition:** alerts whose Case was confirmed True Positive ÷ all alerts whose Case reached a verdict, per detection rule and per [Alert Type](../02-Taxonomy/alert_types.md). Alerts inherit their Case's verdict; alerts of Cases closed as Insufficient Data are excluded.
*   **Purpose:** drives the retirement or refinement of detection content through the Phase 1 tuning loop. The upstream number every automation claim is read against (§6.4).

### 5.2 Disposition Mix
*   **KPI candidate.**
*   **Definition:** the share of Cases dispositioned in the window by verdict — False Positive, Benign, Insufficient Data, True Positive — and, at G2, promoted; reported per gate, with Duplicates counted separately as a volume.
*   **Purpose:** one distribution answers the questions a SOC asks about its noise: how much of the pipeline is noise (False Positive plus Benign share), how much is caught at triage versus after an investigation (the G2 versus G3 split), how much triage promotes, and how much ends undecided (the Insufficient Data share, the signal of investigative thrash or missing telemetry). A high noise share is acceptable only while Detection Precision (§5.1) shows the detection layer is being tuned in response; a stable high noise share with no rising precision means the tuning loop is broken, and Tuning Loop Latency (§5.6) proves it.

### 5.3 Promotion Precision
*   **KPI candidate.**
*   **Definition:** promoted Cases confirmed as Incidents ÷ promoted Cases.
*   **A band, not a maximum:** triage promotes a Case whenever the Benign findings do not cover its alerts ([Detection & Analysis §1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision)), so promoting an unexplained Case is correct triage. A value near 100% signals over-closing at triage, a false-negative risk; a very low value signals promotion out of fear.

### 5.4 Verdict Overturn Rate
*   **KPI candidate.**
*   **Definition:** verdicts overturned at G5 ÷ verdicts examined, in two directions that are never summed:
    *   **Confirmed Incident overturned** (True Positive → noise): measured on *all* confirmed Incidents — an approval rejected, a containment rolled back, a Post-Incident re-classification. An efficiency finding: every wrongly confirmed Incident mobilizes asset owners and leadership and may start a regulatory deadline.
    *   **Close overturned** (noise → True Positive): measured on the QA sample of autonomous closes ([Agentic Supervision §2](../07-Governance/agentic_supervision.md)), with its confidence interval. A missed threat: each occurrence is a critical finding, and this direction is the recall of triage and investigation, the number that decides whether an executor keeps its autonomy grant ([Agentic Supervision §4](../07-Governance/agentic_supervision.md)).
*   **Slices:** by executor, and by the Case **confidence** at the verdict. Low-confidence verdicts are expected to overturn more often than High ones; a High-confidence verdict overturned is a finding against the playbook, and equal overturn rates across confidence levels mean the evidence model is not calibrated.
*   **Reopen Rate** (auxiliary): closed Cases reopened within 30 days ÷ Cases closed — the passive complement to QA sampling, including Insufficient Data closes whose monitoring watch fired.

### 5.5 False Negatives & Recall

False negatives never appear in a queue, but they are measurable. Precision asks: of what was flagged, how much was real? **Recall** asks: of what was real, how much was flagged? For an autonomous SOC recall is the safety metric — an executor that closes everything scores perfect efficiency and zero recall. A miss occurs at one of two places: a **detection miss** (malicious activity raised no Alert) or a **verdict miss** (an Alert fired but its Case was wrongly closed).

**Observation channels.** Recall is reportable only when the channels through which misses surface are operated as process steps with countable outputs. A conformant SOC operates all of the following:

| Channel | Surfaces | Process anchor |
|---|---|---|
| Threat hunting | Detection misses in production | [Detection & Analysis §4](../03-Processes/02-detection_and_analysis.md#4-threat-hunting) |
| Out-of-band intake (user and IT reports, partner and authority notifications, disclosures) | Detection misses | [Detection & Analysis §5](../03-Processes/02-detection_and_analysis.md#5-out-of-band-incident-intake) |
| Retrospective entity sweep at confirmation | Verdict misses: prior Cases on the same entities wrongly closed | [Detection & Analysis §3.1](../03-Processes/02-detection_and_analysis.md#31-incident-promotion) |
| QA sampling, oversampled on Low-confidence closes and Duplicates | Verdict misses, statistically estimable | [Agentic Supervision §2](../07-Governance/agentic_supervision.md); §5.4 |
| Post-Incident missed-detection walk | Detection misses *within* a confirmed Incident: actions that should have alerted and did not | [Phase 4 §3](../03-Processes/04-post_incident_activity.md#3-review-agenda) |

An Alert produced by Phase 1 detection content carries its producing analytic (the `analytic` object of the Detection Finding); an Alert registered by hunting or intake is created by that process step and carries none. That is how the discovery channel is known without a new field.

#### Observed Detection Recall
*   **KPI candidate.**
*   **Definition:** confirmed Incidents whose originating Alert was produced by Phase 1 detection content ÷ all confirmed Incidents, in the window.
*   **Boundary rule:** an optimistic estimate — misses no channel surfaced are absent from the denominator, so the figure can only overstate recall. It is conformant only when reported with the activity of the channels that bound it: hunts executed, intake reports received, QA sample size (§6.4). Recall measured against a known denominator, through adversary emulation, is staged on the [Roadmap](../01-Foundation/roadmap.md).

### 5.6 Tuning Loop Latency
*   **KPI candidate.**
*   **Definition:** time from a False Positive or Benign disposition emitting a tuning ticket ([Preparation & Engineering §1.2](../03-Processes/01-preparation_and_engineering.md)) to the corresponding detection change deployed ([Preparation & Engineering §1.1](../03-Processes/01-preparation_and_engineering.md)); median and p95 per ticket.
*   **Boundary rule:** a sample exists only for a ticket that *reached* deployment. Reported with the count and age of open tuning tickets: a flattering median next to a growing, aging backlog is the gamed state.

### 5.7 Visibility-Gap Rate
*   **KPI candidate.**
*   **Definition:** Cases whose Triage or Investigation Note records at least one Visibility Gap — a required data source unavailable ([Playbook Architecture §7](../04-Playbooks/playbook_architecture.md#7-dynamic-agentic-execution)) — ÷ Cases dispositioned.
*   **Purpose:** the telemetry-investment signal for SOC leadership and Phase 1 log-source health. A persistent gap is a telemetry problem, never an executor problem.

## 6. Autonomy Metrics

"How automated is our SOC?" is meaningful only as "what share of the defined decisions were made autonomously, and were they right?". All autonomy metrics are computed from the **Provenance** element of the Notes (executor: human, automation, agent, blends listed); no new instrumentation is required.

### 6.1 Autonomous Disposition Rate (ADR)
*   **KPI candidate.**
*   **Definition:** Cases dispositioned at G2 (and, separately, at G3) by automation or an agent with **zero human touch** ÷ all Cases dispositioned at that gate. Zero human touch means no handover, no approval, no human edit of the verdict; a Case an executor investigated and a human approved is supervised, not autonomous.
*   **Boundary rules:** consolidated alerts and Duplicates are excluded (§2). Always sliceable into an automation share and an agent share, never reported only as a blended total.

### 6.2 Handover Rate
*   **Definition:** Cases handed over to a human ÷ Cases automation or an agent was assigned, sliced by the recorded reason (`handover_reason`: crown-jewel, privileged-identity, manual — [Agentic Guardrails §3](../07-Governance/agentic_guardrails.md#3-human-assignee-conditions)).
*   **Purpose:** the reason mix is the diagnostic. A rising share of manual takeovers means humans do not trust the autonomous verdicts on the Cases they watch; read it with the Verdict Overturn Rate, which says whether they are right.

### 6.3 HITL Modification Rate
*   **KPI candidate.**
*   **Definition:** of the actions automation or agents submit for approval: share approved as proposed, modified, rejected.
*   **Purpose:** consistent modification is the playbook-drift signal of [Agentic Supervision §3](../07-Governance/agentic_supervision.md); a rising rejection share is the early warning of confirmed Incidents being overturned (§5.4).

### 6.4 Paired Reporting

Reporting the left column without the right column is non-conformant:

| Efficiency claim | Mandatory quality pair |
|---|---|
| Autonomous Disposition Rate | Detection Precision (§5.1) and Verdict Overturn Rate (§5.4) |
| "X% of alerts closed automatically" | Disposition Mix (§5.2) — closing 95% automatically while 90% of alerts are noise is automated waste, not capability |
| Alert-volume reduction | Consolidation Rate (§3) and autonomous verdicts (§6.1), split |
| Any speed metric (§4) | Verdict Overturn Rate, confirmed Incident direction (§5.4) |
| Recall claims (§5.5) | The activity of the observation channels: hunts executed, intake reports, QA sample size |
| Token cost per Case (§7) | Noise Tax (§7.3) |

## 7. Economic Metrics — Token Economics

Autonomous SecOps converts what used to be headcount into **inference spend that scales per Case**. That makes the economics measurable — with the same numerator and denominator rigor as everything above. Published production figures (§10) put triage-stage inference at low single-digit dollars per investigated alert, with token consumption rising by roughly an order of magnitude per stage: thousands of tokens for a triage classification, tens of thousands for a scoped investigation, unbounded for an open agentic loop.

### 7.1 Attribution and capture
*   **Every model invocation is attributed to a Case.** Already mandated by [Agentic Guardrails §5](../07-Governance/agentic_guardrails.md#5-resource--token-metering); token accounting is a by-product of auditability, not new plumbing.
*   **Input and output token counts are captured for every invocation**, named per the OpenTelemetry GenAI semantic conventions, adopted provisionally per [Design Decisions](../01-Foundation/design_decisions.md).
*   **Reported in tokens first, currency second.** Token counts are stable; prices are not. A currency figure states the model mix and the price date.

### 7.2 Boundary rules
*   **Include:** all inference attributed to the Case across triage, investigation and response, including retries, abandoned reasoning paths and guardrail checks the Case triggered. Failure costs are real costs.
*   **Exclude, tracked separately as standing compute:** telemetry embedding and indexing, model training and fine-tuning, hunts (attributed to the hunt, not a Case), QA sampling reviews.
*   **Deterministic work costs zero tokens.** A check resolvable by a query is a query, not a model call — the token-cost expression of the manifest's [deterministic-first principle](../01-Foundation/framework_manifest.md#executor-neutrality-and-human-readability). Work automation can do at zero token cost is not agent work.

### 7.3 The metrics
*   **Token Cost per Case (TCpC).** *KPI candidate.* Tokens of the invocations attributed to a Case, over Cases dispositioned in the window, **sliced by outcome**: closed at triage, investigated and closed, confirmed Incident. The order-of-magnitude difference between the slices makes a blended average meaningless; the closed-at-triage slice is the cost of an alert.
*   **Noise Tax.** *KPI candidate, the pair of TCpC.* Share of Case-attributed tokens spent on Cases dispositioned as noise. §5 expressed in compute: a high ADR with a high Noise Tax means the organization pays, per token, to automate waste. The cheapest token is the alert Phase 1 never generated.

Coverage economics — token cost per protected endpoint or identity, the figure an adopter compares against managed-detection market norms — is staged on the [Roadmap](../01-Foundation/roadmap.md) until enough baselines exist to make it comparable.

## 8. Reference Bands for Setting KPOs

The bands below are **illustrative**, synthesized from industry practice and the sources of §10. They are inputs for setting a [KPO](../01-Foundation/definitions.md#5-measurement--performance-terminology), not targets: alert mix, telemetry coverage and risk tolerance vary enough that an imported number misleads as easily as it guides. Establish the organization's own baseline in the first 90 days, then manage the trend.

| Metric | Human-led | Automation | Agent-led | Notes |
|---|---|---|---|---|
| MTTI (§4) | 15–60 min per Case closed at triage | Instant, only for fully specifiable False Positive classes | ≤ 10 min per Case closed at triage | Investigation-stage verdicts run longer; slice by gate. |
| MTTD (§4) | Executor-independent: a detection-content property | Executor-independent | Executor-independent | Minutes to hours for actively tuned techniques; track the trend. |
| MTTC (§4) | 4–24 h typical | Minutes, for pre-authorized actions | ≤ 30 min, excluding HITL Dwell Time, for pre-authorized actions | Approval-loop time is never counted as containment time. |
| HITL Dwell Time (§4) | Critical ≤ 30 min · High ≤ 2 h | n/a: automation requests approval, it does not grant it | n/a: agents request approval, they do not grant it | — |
| Detection Precision (§5.1) | Executor-independent | Executor-independent | Executor-independent | ≥ 80–90% per active rule, after tuning. |
| Disposition Mix (§5.2) | Noise share ≤ 30% and falling | same | same | Legacy human-run SOCs commonly run 30–70% noise. An Insufficient Data share above 10% is a telemetry or playbook signal. |
| Promotion Precision (§5.3) | 50–90% | 50–90% | 50–90% | Below 50%, triage over-promotes; above 90%, it over-closes. Parity across executors on the same alert mix. |
| Verdict Overturn Rate (§5.4) | Confirmed Incidents overturned ≤ 2–5% · closes overturned ≈ 0%, each occurrence a critical finding | same, ≤ the human baseline | same, ≤ the human baseline | Never summed. |
| HITL Modification Rate (§6.3) | n/a: humans are the reviewers here | ≤ 10% of proposed actions modified or rejected | ≤ 10% | A higher share means the playbooks or the autonomy matrix need work. |
| Autonomous Disposition Rate (§6.1) | n/a by definition | Maturity-staged: initial < 20% → operating 20–60% → mature > 80% of G2 dispositions | same | The binding constraint at every stage is the Verdict Overturn Rate, not this band. |
| Tuning Loop Latency (§5.6) | Executor-independent: a Phase 1 property | Executor-independent | Executor-independent | ≤ 14 days median, matching the High risk band of the Phase 4 [remediation deadlines](../03-Processes/04-post_incident_activity.md#5-remediation-deadlines). |
| Visibility-Gap Rate (§5.7) | Trending to < 5% of Cases | same | same | A persistent gap is a telemetry-investment signal. |
| TCpC and Noise Tax (§7) | Organization-specific by design | same | same | No industry reference exists: baseline in the first 90 days, then manage the trend, Noise Tax down. |

## 9. Metric → Process Traceability

| Metric | Gate | Process anchor | Primary consumer |
|---|---|---|---|
| Alert Volume, Consolidation Rate | G1 | [Phase 1](../03-Processes/01-preparation_and_engineering.md) output; [Detection & Analysis §1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment) | Capacity planning |
| MTTD — *KPI candidate* | T0 → G1 | Phase 1; [Detection & Analysis §4, §5](../03-Processes/02-detection_and_analysis.md) | Detection Engineer |
| MTTI — *KPI candidate* | G1 → G2/G3 | [Detection & Analysis §1.5, §2.4](../03-Processes/02-detection_and_analysis.md) | SOC Manager |
| MTTC — *KPI candidate*, MTTR | T0 → G4; T0 → recovery | [Incident Response §2, §4](../03-Processes/03-response.md) | SOC Manager, leadership |
| HITL Dwell Time — *KPI candidate* | `Pending HITL`, handover | [Agentic Supervision §1](../07-Governance/agentic_supervision.md) | SOC Manager |
| Detection Precision — *KPI candidate* | G1, judged at G2/G3 | Phase 1 tuning loop | Detection Engineer |
| Disposition Mix — *KPI candidate* | G2, G3 | [Detection & Analysis §1.5, §2.4](../03-Processes/02-detection_and_analysis.md) | SOC Manager, Detection Engineer |
| Promotion Precision — *KPI candidate* | G3 | [Detection & Analysis §1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision) | SOC Manager |
| Verdict Overturn Rate — *KPI candidate*, Reopen Rate | G5 | [Agentic Supervision §2](../07-Governance/agentic_supervision.md); [Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment); [Phase 4 §3](../03-Processes/04-post_incident_activity.md#3-review-agenda) | SOC Manager |
| Observed Detection Recall — *KPI candidate* | G3 / G5 | [Detection & Analysis §3.1, §4, §5](../03-Processes/02-detection_and_analysis.md); [Phase 4 §3](../03-Processes/04-post_incident_activity.md#3-review-agenda) | Leadership, Detection Engineer |
| Tuning Loop Latency — *KPI candidate* | G2/G3 → Phase 1 | [Phase 1 §1.1, §1.2](../03-Processes/01-preparation_and_engineering.md) | Detection Engineer |
| Visibility-Gap Rate — *KPI candidate* | G2/G3 | Note Visibility Gaps; [Playbook Architecture §7](../04-Playbooks/playbook_architecture.md#7-dynamic-agentic-execution) | SOC leadership, Security Platform Engineer |
| ADR — *KPI candidate*, Handover Rate, HITL Modification Rate — *KPI candidate* | G2–G4 | Note Provenance; [Agentic Guardrails §3](../07-Governance/agentic_guardrails.md#3-human-assignee-conditions); [Agentic Supervision](../07-Governance/agentic_supervision.md) | SOC Manager |
| TCpC, Noise Tax — *KPI candidates* | G1–G4 | [Agentic Guardrails §5](../07-Governance/agentic_guardrails.md#5-resource--token-metering) | Leadership, FinOps |

## 10. Sources & Prior Art

Foundations this module builds on rather than reinvents; credited here once, per the sourcing rule of the [Design Decisions](../01-Foundation/design_decisions.md).

*   **Standards and schemas:** [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) (lifecycle), [OCSF v1.8.0](https://schema.ocsf.io/1.8.0/categories) (state fields), SOC-CMM (maturity alignment), [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai) (token-capture naming, provisional), [FinOps FOCUS 1.2](https://www.finops.org/insights/focus-1-2-available/) (cost data normalization).
*   **Research and practitioner:** [Alahmadi et al., USENIX Security 2022](https://www.usenix.org/system/files/sec22summer_alahmadi.pdf) (false-positive ambiguity; benign triggers), [SpecterOps, Funnel of Fidelity](https://specterops.io/blog/2019/11/20/introducing-the-funnel-of-fidelity/) (stage model), MITRE, *11 Strategies of a World-Class Cybersecurity SOC* (measurement strategy), SANS SOC Surveys (noise burden, adoption data), [Bono et al., arXiv:2511.13860](https://arxiv.org/abs/2511.13860) (randomized controlled trial of AI-assisted phishing triage: human reviewers under-catch the assistant's false negatives — the basis of the oversampling rule), Gartner's evaluation guidance on investigation quality over alert volume.
*   **Empirical anchors, vendor-published and indicative only:** [RunReveal](https://blog.runreveal.com/ai-soc-investigation-cost-token-pricing/) (per-alert token cost), [Elastic Security Labs](https://www.elastic.co/security-labs/alert-triage-agentic-soc-elastic-workflows) (deterministic-first cost architecture), [SecurityWeek](https://www.securityweek.com/the-ai-token-costs-that-can-break-cybersecurity/) (token tiering), managed-detection per-endpoint pricing aggregates.

Where this module names metrics no standards body has defined — **Disposition Mix, Verdict Overturn Rate, Noise Tax, Token Cost per Case** — the definitions above are offered as the vendor-neutral standard, anchored to the precedent cited.
