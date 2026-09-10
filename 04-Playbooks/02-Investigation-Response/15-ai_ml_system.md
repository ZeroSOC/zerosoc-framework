---
title: 15-AI/ML System Attack Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-15
mitre_ttps:
  - AML.T0051   # LLM Prompt Injection
  - AML.T0020   # Poison Training Data
  - AML.T0043   # Craft Adversarial Data
  - AML.T0024   # Exfiltration via ML Inference API
  - AML.T0040   # ML Model Inference API Access
default_severity: High
required_data_sources:
  - LLM / inference API logs (prompts + completions)
  - Model registry & ML-pipeline audit logs
  - Training-data lineage
  - GPU / compute telemetry
  - Host-application logs for AI features
status: draft
---

# 15-AI/ML System Attack Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-15 AI/ML System Attack` — attacks targeting AI systems: model evasion, poisoning, extraction, prompt injection and AI-infrastructure exploitation. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

Three attack surfaces share this category: the model's inputs (prompt injection, evasion), its supply chain (data or model poisoning) and its API (extraction, inversion). The first queries discriminate which surface is under attack. When the target is an agentic system, the blast radius is whatever tools the agent can call.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an adversary is attacking an AI system — injecting prompts into an LLM or agent to obtain unintended actions or disclosures, poisoning training data or model artifacts, or systematically extracting the model or its data through the inference API.
   * **Benign:** unusual but legitimate prompting, scheduled red-team or evaluation traffic, or normal retraining-pipeline churn.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Does prompt-log inspection show instruction-override or jailbreak patterns, encoded payloads, system-prompt-leak attempts, or injected instructions carried in retrieved documents or tool outputs — and did the input guardrails fire? → `Malicious (Medium)` on override patterns, encoded payloads or injected instructions in retrieved content; `Benign (Low)` when the prompts are unusual but within the application's purpose and the guardrails passed them.
   * *Query 2:* Following the suspicious input, did the model or agent perform an unintended tool call or action, or disclose the system prompt, another user's data or a secret (agent trace, tool-call and host-application logs)? → `Malicious (High)` on a tool call outside its intended scope, an action on a system the requester had no right to, or a disclosure — and, for data disclosed at scale, the re-classification trigger below; `Benign (Low)` when the model refused and nothing followed — an unsuccessful attempt is still an attempt.
   * *Query 3:* Does the API usage shape show high-volume, systematic query patterns — grid or near-duplicate inputs, confidence-score harvesting, membership probing — consistent with model extraction or inversion, against the normal client mix? → `Malicious (Medium)` on a systematic pattern from one client or key; `Benign (Low)` when the volume and shape match a known client's baseline.
   * *Query 4:* Are there unauthorized changes to the training data, the feature store or the model artifacts — a registry hash mismatch, a pipeline run outside its schedule, an artifact written by a principal that is not the pipeline (model registry, pipeline audit logs, training-data lineage)? → `Malicious (High)` on a hash mismatch or an artifact changed outside the pipeline; `Benign (Medium)` when every artifact matches the registry and every run traces to a scheduled job.
   * *Query 5:* Does the activity correlate with a scheduled red-team or evaluation window, a known client identifier, or an approved experiment? → `Benign (High)` on a match — the explanation of the alert; `Malicious (Low)` when the traffic claims to be a test and is not on the schedule.
   * *Query 6:* Whose credential is behind the traffic — the application's own key from its own infrastructure, a key issued to a different application, a key used from unfamiliar infrastructure, or an unauthenticated path ([Identity](../99-Shared/sub_enrichment_identity.md))? → `Malicious (High)` when the key belongs to another application, is used from unfamiliar infrastructure, or the path bypasses authentication — and the IC-06 pivot below; `Benign (Low)` when the key is the application's own, from its usual infrastructure.

**Re-classification pivots:** model or data theft at scale → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md); the platform credentials themselves are compromised → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md); the poisoned model or dataset came from a third-party source → [IC-10 (Supply-Chain Compromise)](10-supply_chain.md); the serving host or its application is exploited rather than the model → [IC-07 (Web App Exploitation)](07-web_app_exploitation.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-15 (AI/ML System Attack)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Revoke the offending API keys and suspend the offending clients (reversed by issuing new keys or re-enabling the client). Suspending a key or identity the production application runs under — **requires approval**.
*   Rate-limit the inference API for the offending clients (reversed by lifting the limit).
*   Tighten the input and output filters at the model gateway, and constrain or suspend the agent's tool permissions (reversed by restoring them). Removing a tool a critical production workflow depends on — **requires approval**.
*   Quarantine the documents or retrieval sources carrying the injected content (reversed by releasing them).
*   Taking the AI service or the model endpoint offline, or disabling the agent — **requires approval**.

### Eradication
*   Enumerate every tool call and action of the manipulated session and reverse each one — messages sent, records changed, transactions submitted. A reversal that is itself irreversible or touches many records — **requires approval**.
*   Roll back the production model to a known-good version from the registry — **requires approval**.
*   Identify the poisoned records or artifacts by lineage, then purge them and retrain — **requires approval**; never roll back or retrain before they are identified.
*   Remove the injected content from the retrieval corpus and close the injection path — sanitize retrieved content and tool outputs before they reach the model.
*   Rotate any secrets exposed through prompts, context or outputs. A rotation beyond the confirmed scope — **requires approval**.

### Recovery
*   Verify the restored model against the evaluation suite before serving, then re-enable in stages — rate limits, tool permissions, endpoint — with enhanced monitoring, each step recorded in the Case timeline.
*   Add the observed adversarial inputs to the evaluation suite.
*   Notify the users whose data the outputs disclosed of what was disclosed and of the actions taken.
*   Feed the observed patterns — injection strings, query shapes, client fingerprints — to Phase 1 as a detection-tuning signal.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-15, the attack surface — input, supply chain or API — is identified and recorded, every tool call of a manipulated agent is enumerated with its reversal status, and the data disclosed through outputs and the parties affected are enumerated before closure.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 5 executed, or with Query 2 unanswered for a session that carried an injection pattern.
*   A model endpoint taken offline, a production model rolled back, training data purged or a production key suspended without approval.
*   A rollback or a retrain performed before the poisoned data or artifacts are identified and purged.
*   Closure with a manipulated agent's actions not enumerated and reversed, or leaving injected content in the retrieval corpus — a confirmed foothold.
*   Data theft at scale or a compromised platform credential not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep the prompt logs of every AI-enabled application for the observed injection pattern — an injection that worked once is re-used against every model behind the gateway.
*   Sweep the model registry for artifacts whose hash differs from the pipeline's recorded output, and the lineage for records added outside a scheduled run.
*   Sweep the inference-API logs for keys with systematic query shapes or first use in the last 30 days.

## References

*   MITRE ATLAS: AML.T0051 (LLM Prompt Injection), AML.T0020 (Poison Training Data), AML.T0043 (Craft Adversarial Data), AML.T0024 (Exfiltration via ML Inference API), AML.T0040 (ML Model Inference API Access); NIST SP 800-61 Rev. 3; NIST AI 100-2 (Adversarial Machine Learning taxonomy); OWASP Top 10 for LLM Applications.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Identity enrichment](../99-Shared/sub_enrichment_identity.md).
