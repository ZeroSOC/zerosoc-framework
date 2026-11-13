---
title: Agentic Supervision
type: process
status: draft
last_updated: 2026-11-13
license: Apache-2.0
---

# Agentic Supervision Process

> **Draft.** This document states the minimum supervision of autonomous executors the operating loop depends on — approval reviews, quality-assurance sampling, playbook drift and the autonomy grant. Expect it to change in a later release.

Automation and agents close Cases and apply containment without a human in the loop. Supervision is the process by which the [SOC Manager](../01-Foundation/definitions.md#6-executors-and-functions) keeps that autonomy under control: reviews what the autonomous executors ask, samples what they decided alone, and withdraws autonomy when the quality drops. It applies to automation and agents alike; the [Agentic Guardrails](agentic_guardrails.md) set the boundaries, this process checks them.

## 1. Human-in-the-Loop (HITL) Reviews

A human is brought into an autonomous Case in three situations:

*   **Approval request:** an action that requires approval under the containment autonomy matrix ([Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment)) enters the `Pending HITL` state; the approver approves, modifies or rejects it, and the decision is recorded in the Case timeline.
*   **Proposed closure:** automation or an agent proposes a closure outside its autonomy grant (§4). A person decides on the Case's Note, and the Case is On Hold until then.
*   **Question:** a held Case asks for the evidence it lacks ([Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence)).

The human-side target is the HITL Dwell Time of [Operational Metrics §4](../05-Metrics/operational_metrics.md).

## 2. Quality Assurance Sampling

A Case closed by automation or an agent with no human touch is reviewed after the fact by sampling. Every week (a reference cadence) a random sample of the autonomous closes — False Positive, Benign, Duplicate and Insufficient Data — is reviewed by a Security Analyst under the SOC Manager's supervision, **oversampling** the closes where a wrong verdict costs most: closes at Low confidence, Duplicates (a wrong Duplicate is a missed threat) and Insufficient Data closes whose monitoring watch expired without a recurrence. The sample rate is an organization policy knob; 5% of closes is a reference value.

*   **Objective:** find wrong verdicts — the verdict misses of [Operational Metrics §5.5](../05-Metrics/operational_metrics.md) — and the drift, hallucination or confirmation bias behind them, before an Incident does.
*   **Review basis:** the Triage Note and the Investigation Note ([Detection & Analysis §1.6 and §2.6](../03-Processes/02-detection_and_analysis.md)) — the observations, their tags and the resolution — not raw execution transcripts.
*   **Outcome:** an overturned verdict reopens the Case and counts against Verdict Precision when a confirmed Incident is overturned ([Operational Metrics §5.4](../05-Metrics/operational_metrics.md)) or as a triage or investigation miss in Observed Triage Recall or Observed Verdict Recall when a close is overturned ([Operational Metrics §5.5](../05-Metrics/operational_metrics.md)); a wrong verdict traced to a playbook query or a missing organizational context becomes a playbook update or a [SOC Knowledge Base](../01-Foundation/definitions.md#soc-knowledge-base-soc-kb) entry.
*   **Standing input:** Cases that exhausted their budget and per-action ceiling trips ([Agentic Guardrails §4](agentic_guardrails.md#4-resource--token-metering)) are always in the sample: they indicate playbook inefficiency or runaway behavior, a failure mode distinct from verdict quality.

## 3. Playbook Drift Monitoring

Two signals show that a playbook no longer fits the environment: approvers consistently modifying the queries or containment actions an executor proposes (Approval Override Rate, [Operational Metrics §6.3](../05-Metrics/operational_metrics.md)), and observations retracted during investigation or in the evidence review of the Post-Incident Review ([Phase 4 §3](../03-Processes/04-post_incident_activity.md#3-review-agenda)). Either triggers a playbook update.

## 4. Autonomy Grant

Automation and agents close Cases and apply containment without approval only under a grant the SOC Manager gives and keeps under review with the sampling of §2. A grant to apply containment may be limited to actions up to a given impact, by action or by time window ([Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment)). A grant is withdrawn whole or for part of its scope.

*   **Scope.** The grant to close Cases **SHOULD** cover a Case whose scope includes a [critical entity](../01-Foundation/definitions.md#critical-entity) only when its closing verdict, a near miss included, is at High confidence (the key word as [Playbook Architecture §1](../04-Playbooks/playbook_architecture.md#1-conformance--normative-keywords) defines it). Outside the grant the executor proposes the closure and a person decides. An organization may narrow the grant further, by entity class (for example the entities its access control depends on) as by alert type.
*   **Entry: shadow mode.** Before the grant, the executor runs against live traffic without acting — its verdicts are recorded and compared with the human verdicts on the same Cases over a defined sample. The agreement rate is the entry bar; it measures conformity to human judgment, not ground truth, so the sampling of §2 remains the standing control after the grant. Agreement rates published by vendors are measured on their own baselines; they count only once reproduced on the organization's alert mix.
*   **Withdrawal.** The grant is withdrawn, for the executor or for an alert type, when its Observed Triage Recall or Observed Verdict Recall for that executor or alert type ([Operational Metrics §5.5](../05-Metrics/operational_metrics.md)) falls below the organization's threshold; the executor then proposes, and a human decides, until the grant is restored through shadow mode.
