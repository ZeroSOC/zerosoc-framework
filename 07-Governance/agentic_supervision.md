---
title: Agentic Supervision
type: process
status: draft
last_updated: 2026-09-10
license: Apache-2.0
---

# Agentic Supervision Process

> **Draft.** This document states the minimum supervision of autonomous executors the operating loop depends on — approval and handover reviews, quality-assurance sampling, playbook drift and the autonomy grant. Expect it to change in a later release.

Automation and agents close Cases and apply containment without a human in the loop. Supervision is the process by which the [SOC Manager](../01-Foundation/definitions.md#6-executors-and-functions) keeps that autonomy under control: reviews what the autonomous executors ask, samples what they decided alone, and withdraws autonomy when the quality drops. It applies to automation and agents alike; the [Agentic Guardrails](agentic_guardrails.md) set the boundaries, this process checks them.

## 1. Human-in-the-Loop (HITL) Reviews

A human is brought into an autonomous Case in two situations:

*   **Approval request:** an action that requires approval under the containment autonomy matrix ([Incident Response §2.1](../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment)) is requested with the payload of [Agentic Guardrails §2](agentic_guardrails.md#2-the-human-in-the-loop-hitl-presentation-payload). The action enters the `Pending HITL` state; the approver approves, modifies or rejects it, and the decision is recorded in the Case timeline.
*   **Handover:** the Case scope includes a Crown Jewel asset or a privileged identity ([Agentic Guardrails §3](agentic_guardrails.md#3-human-assignee-conditions)); the human becomes the assignee and decides on the findings and actions the previous executor keeps producing.

An executor never stops for doubt: when the evidence is insufficient it applies the resolution rule of [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence). The human-side target for both situations is the HITL Dwell Time of [Operational Metrics §4](../05-Metrics/operational_metrics.md): the time an action or a Case waits for the human, which is never counted as containment time.

## 2. Quality Assurance Sampling

A Case closed by automation or an agent with no human touch is reviewed after the fact by sampling. Every week (a reference cadence) a random sample of the autonomous closes — False Positive, Benign, Duplicate and Insufficient Data — is reviewed by a Security Analyst under the SOC Manager's supervision, **oversampling** the closes where a wrong verdict costs most: closes at Low confidence, Duplicates (a wrong Duplicate is a missed threat) and Insufficient Data closes whose monitoring watch expired without a recurrence. The sample rate is an organization policy knob; 5% of closes is a reference value.

*   **Objective:** find wrong verdicts — the verdict false negatives of [Operational Metrics §5.7](../05-Metrics/operational_metrics.md) — and the drift, hallucination or confirmation bias behind them, before an Incident does.
*   **Review basis:** the Triage Note and the Investigation Note ([Detection & Analysis §1.6 and §2.5](../03-Processes/02-detection_and_analysis.md)) — the findings, their tags and the resolution — not raw execution transcripts.
*   **Outcome:** an overturned verdict reopens the Case and counts in the Verdict Overturn Rate ([Operational Metrics §5.4](../05-Metrics/operational_metrics.md)); a wrong verdict traced to a playbook query or a missing organizational context becomes a playbook update or a [SOC Knowledge Base](../01-Foundation/definitions.md#soc-knowledge-base-soc-kb) entry.
*   **Standing input:** budget-exhaustion closes and per-action ceiling trips ([Agentic Guardrails §5](agentic_guardrails.md#5-resource--token-metering)) are always in the sample: they indicate playbook inefficiency or runaway behavior, a failure mode distinct from verdict quality.

## 3. Playbook Drift Monitoring

Two signals show that a playbook no longer fits the environment: approvers consistently modifying the queries or containment actions an executor proposes (HITL Modification Rate, [Operational Metrics §6.3](../05-Metrics/operational_metrics.md)), and findings retracted during investigation or in the evidence review of the Post-Incident Review ([Phase 4 §3](../03-Processes/04-post_incident_activity.md#3-review-agenda)). Either triggers a playbook update.

## 4. Autonomy Grant

An executor closes Cases or applies pre-authorized containment autonomously only under a grant the SOC Manager gives and keeps under review with the sampling of §2.

*   **Entry: shadow mode.** Before the grant, the executor runs against live traffic without acting — its verdicts are recorded and compared with the human verdicts on the same Cases over a defined sample. The agreement rate is the entry bar; it measures conformity to human judgment, not ground truth, so the sampling of §2 remains the standing control after the grant. Agreement rates published by vendors are measured on their own baselines; they count only once reproduced on the organization's alert mix.
*   **Withdrawal.** The grant is withdrawn, for the executor or for an alert type, when the close-overturned direction of the Verdict Overturn Rate ([Operational Metrics §5.4](../05-Metrics/operational_metrics.md)) exceeds the organization's threshold; the executor then proposes, and a human decides, until the grant is restored through shadow mode.
