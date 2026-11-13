---
title: Agentic Governance & Guardrail Protocols
type: policy
status: draft
last_updated: 2026-11-13
license: Apache-2.0
---

# Agentic Governance & Guardrail Protocols

> **Draft.** This document states the controls the operating loop depends on — least access, the autonomy grant, data egress and metering — and no more. Its expansion, including the per-function capability matrix, is tracked on the [Roadmap](../01-Foundation/roadmap.md). Expect it to change in a later release.

Automation and agents act in the environment with real privileges. This document sets the boundaries within which they act, so that every action is attributable, reversible where it can be, approved where it must be, and under human accountability for what matters most.

## 1. Least Access Identity Plane

Automation and agents do not operate with standing, highly privileged accounts.

*   **Just-in-time scoping:** an executor requests permissions scoped to the query, enrichment or containment action it is about to perform on the Case at hand.
*   **Token lifetime:** the credential expires when the action completes or the Case leaves the executor.
*   **Auditability:** every API call is logged centrally and attributed to the Case that drove it.

## 2. The Autonomy Grant

Automation and agents close Cases and apply containment without approval only within an autonomy grant, whose entry, scope and withdrawal are specified in [Agentic Supervision §4](agentic_supervision.md#4-autonomy-grant). Outside the grant they propose, and a person decides.

## 3. Data-Handling & OSINT Egress Boundaries

Enrichment frequently sends data to public or third-party analysis services. To prevent data leakage and preserve operational security, the framework constrains what may leave the environment during triage, investigation and response — an **indicators-only** principle.

*   **Never submit organizational content or sensitive indicators** to public or third-party services: files, scripts and documents; **full URLs**, which may embed session tokens, personal data or internal hostnames; email or message bodies.
*   **Permitted:** querying non-attributable, pre-computed indicators — file hashes, and IP addresses or domains that are already public external infrastructure.
*   **Dynamic or behavioral analysis** of a suspected sample uses a private, isolated sandbox, never a public one.

**Rationale:** uploading organizational data to a public service risks a reportable data leak under NIS2 and DORA; submitting an attacker's implant or infrastructure to a public service tells the attacker the campaign is detected and prompts a change of infrastructure.

## 4. Resource & Token Metering

Inference spend is an operational resource like privilege or egress, and it is governed the same way: metered, budgeted and bounded. Agents are the metered executor class; deterministic automation reports zero token cost by definition ([Operational Metrics §7.2](../05-Metrics/operational_metrics.md)).

*   **Metering:** every model invocation records its input and output token counts, the model identifier and the Case that drove it — the §1 auditability rule extended from API calls to inference spend. Attribute names follow the OpenTelemetry GenAI semantic conventions, adopted provisionally while that specification remains in Development status.
*   **Per-Case budget:** every Case carries a token budget scaled by severity; the values are an organization policy knob — the framework fixes the mechanism, not the numbers. Budget exhaustion is not a failure, and the Case stays with its assignee: the executor applies the resolution rule of [Detection & Analysis §2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence) to the evidence at hand — at Triage, the decision of [§1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision) — and records the spend and the state reached in the Note.
*   **Per-action runaway ceiling:** independent of the Case budget, a per-action token ceiling bounds any single reasoning loop. Repeated identical tool calls or self-invocations trip the ceiling early: a runaway loop is recognized by its shape, not only by its cumulative bill. The value is an organization policy knob.
*   **Deterministic first:** a check resolvable by a query or a rule is executed as a query or rule, never as a model call — the enforcement of the manifest's [deterministic-first principle](../01-Foundation/framework_manifest.md#executor-neutrality-and-human-readability) and of the zero-token boundary rule in [Operational Metrics §7.2](../05-Metrics/operational_metrics.md).
*   **Feed to metrics:** these metering records are the sole input to the Token Economics metrics ([Operational Metrics §7](../05-Metrics/operational_metrics.md)). Estimated or sampled spend is not conformant: measurement is a by-product of this guardrail, never a parallel bookkeeping.
