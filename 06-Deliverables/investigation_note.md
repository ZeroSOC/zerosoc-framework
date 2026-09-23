---
title: Investigation Note Template
type: template
last_updated: 2026-09-23
license: Apache-2.0
status: draft
---

# Investigation Note

Fill-in template and worked example for the **Investigation Note**, the verdict evidence record produced when Investigation closes a Case or confirms an Incident. The canonical element list is [Detection & Analysis §2.5](../03-Processes/02-detection_and_analysis.md#25-investigation-note-verdict-evidence-record); this page is the practitioner-facing form. Naming convention: `investigation_note_<case-id>_<YYYYMMDD-HHMM>`.

It has the **same element structure as the [Triage Note](triage_note.md)**, with one element more, and the same rendering contract: it holds no state of its own, and renders the Case at this gate. It **extends and updates** the Triage Note rather than mirroring it — the same Case further along, with the Findings triage made now verified or retracted.

## Template

### Summary

*A factual account, current as at this gate, on the same terms as the Triage Note: what happened and when, which entities were involved and who acted on whom, and the root cause where discovered, how it is known and how confident you are of it. That confidence is prose and is not `confidence_id`.*

### Classification

*The confirmed (or, on close, the last candidate) Incident Category, the assessed `severity_id`, `confidence_id` and `impact_id`, and for a confirmed Incident whether it is significant and whether it is cross-border ([§3.1](../03-Processes/02-detection_and_analysis.md#31-incident-promotion)); and the decision: the `verdict_id` the resolution rule produced, with the master Case identifier where that verdict is Duplicate.*

### Rationale

*The [§2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence) resolution applied: the score of each side, the side proven and the Findings that carry it, and the Findings retracted and why. The confidence is in Classification; the Rationale says **how it was reached**, not what it is. What the close *emitted* is an action of the Case, not reasoning: it is a ticket the Case raised and renders in the Case Timeline.*

### Findings

*Every Finding the Case holds: the Alerts; the Findings triage made, each now **verified or retracted** with the reason; and the result of each validation query run. Each renders with its side and confidence or with neither, with **what produced it** — the validation query being the Finding's `analytic` — and with the events it rests on, cited by identifier.*

*The Alerts render what their detection asserted ([§1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment)), as in the Triage Note, with the **remediation state of each entity as it stands at this gate**. A remediation the source performed is an action the Case records and never a Benign finding. Any recommended action run at this gate renders as the Finding it produced.*

| # | Finding | Tag | Produced by | Event ref |
|---|---|---|---|---|
| T`<n>` | `<the triage Finding>` — **verified** or **retracted**, with the reason | `<tag>` or removed on a retraction | `<the query that settled it>` | `<event ref>` |
| `<n>` | `<what the validation query established>` | `<Malicious/Benign (confidence)>` or context | `<the question the query asked>` | `<event ref>` |

### Re-classification Pivots

*Any candidate `incident_category` change ([§2.2](../03-Processes/02-detection_and_analysis.md#22-playbook-execution)), with the reason and the evidence that triggered it; "None." otherwise.*

### Case Timeline

*A chronological reconstruction of the Case: **the course of the attack** (initial access → progression → objective, where established) interleaved with the detection and the response actions taken, each entry timestamped (UTC) and citing its supporting event reference. The earliest **confirmed malicious** event is the Case's **T0**. A Case closed without the Malicious hypothesis proven still carries a timeline — it documents the Case, not only the attack — and has no T0.*

| UTC timestamp | Actor / executor | Action / observation | Event ref |
|---|---|---|---|
| `<timestamp>` | `<actor/executor>` | `<action/observation — T0 if earliest confirmed malicious event>` | `<OCSF finding UID / event link>` |

### Visibility Gaps

*Every required data source unavailable during investigation, and every required input of [§1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment) the source did not supply, each paired with the check it prevented; write "None." when no gap occurred.*

### Provenance

*The playbook(s) used (path plus `last_updated` as version), the executor (human / automation / agent — all classes that contributed), the capability classes invoked, the Case identifier, and — once evidence has been preserved — the pointer to it ([§3.3](../03-Processes/02-detection_and_analysis.md#33-evidence-preservation--chain-of-custody)).*

---

## Worked Example

`investigation_note_CASE-4711_20260914-1640` — continues the Triage Note example of [triage_note.md](triage_note.md).

### Summary

At 14:58 UTC on 2026-09-14 `j.doe`, a standard-privilege Marketing user, posted content from a managed corporate laptop to an unsanctioned AI assistant. Content inspection at this gate establishes the root cause: the material was a product description draft, holding no regulated, proprietary or personal data, and the use was a single first occurrence with no concealment. What triage could not see, this gate saw, and the account is now complete — the unsanctioned tool was used for ordinary non-sensitive work.

### Classification

Last candidate Incident Category: **IC-09** (Insider Threat & Privilege Misuse). `severity_id`: **2 (Low)**. `confidence_id`: **3 (High)**. `impact_id`: **0 (Unknown)** — no Incident, so impact is not assessed. Decision: **Close**, `verdict_id` **5 (Benign)**.

### Rationale

Malicious side: the alert alone, `Malicious (Low)`, weight 1; no Finding stands beyond it. Benign side: T3, 1, 2 and 5 at Low (1 each) and Finding 4 at High (3), weight 7. The **Benign hypothesis is proven**: Finding 4 explains the alert, so the only Malicious Finding is accounted for and leaves no residual observation, and there is no Medium or High Malicious Finding to cover. No Finding was retracted.

### Findings

| # | Finding | Tag | Produced by | Event ref |
|---|---|---|---|---|
| T1 | The alert, **verified** — unchanged at this gate; no entity was remediated, the session having been recorded rather than blocked. | `Malicious (Low)` | SaaS discovery control | `DF-4711-001` |
| T3 | Access over the normal corporate network path, **verified** — unchanged. | `Benign (Low)` | Session detail on the alert record | `DF-4711-001` |
| 1 | Drafting marketing copy with a general-purpose AI assistant is plausible for the role. | `Benign (Low)` | Does the use fit `j.doe`'s role? | `EVT-4711-006` |
| 2 | Single, first occurrence; no recurring or bulk pattern. | `Benign (Low)` | Does the usage deviate from the user's 30-day baseline? | `EVT-4711-007` |
| 3 | No resignation, performance process or offboarding on record. | context | Is there HR risk context? | `EVT-4711-008` |
| 4 | The posted content is a product description draft: no regulated, proprietary or personal data. This **explains the alert** — an unsanctioned tool used for non-sensitive work. | `Benign (High)` | Was regulated or sensitive data posted? (tests `T1567 (Exfiltration Over Web Service)`) | `DF-4711-009` |
| 5 | No VPN bypass, private browsing or log deletion. | `Benign (Low)` | Any concealment? | `EVT-4711-010` |

### Re-classification Pivots

None. Candidate categories IC-09 and IC-11 stand; the Case closes without a category change.

### Case Timeline

*No T0: the Malicious hypothesis was not proven. The timeline documents the Case from detection to closure.*

| UTC timestamp | Actor / executor | Action / observation | Event ref |
|---|---|---|---|
| 2026-09-14 14:58 | Human (`j.doe`) | Posts content to the AI assistant from the managed laptop — the observed action. | `DF-4711-001` |
| 2026-09-14 14:59 | Automation (SaaS discovery) | Detection Finding raised; Case `CASE-4711` opened. | `DF-4711-001` |
| 2026-09-14 15:02 | Agent (Triage) | Case acknowledged, `status_id` → In Progress. | `EVT-4711-CASE-OPEN` |
| 2026-09-14 15:06–15:08 | Agent (Triage) | Enrichment: reputation, CMDB, identity directory, Knowledge Base, active Cases. | `DF-4711-002`, `EVT-4711-003`…`005` |
| 2026-09-14 15:12 | Agent (Triage) | Promote to Investigation: the alert is not covered (content exposure unverified). | `triage_note_CASE-4711_20260914-1512` |
| 2026-09-14 15:20–16:25 | Agent (Investigation) | Queries 1–5: role fit, baseline, HR context, content inspection, concealment. | `EVT-4711-006`…`010` |
| 2026-09-14 16:35 | Agent (Investigation) | Benign hypothesis proven at High confidence; Case closed Benign (`verdict_id: 5`). Knowledge Base entry emitted recording the use of AI assistants for non-sensitive drafting in Marketing, with a request for a sanctioning decision on the application so that a recurrence closes at triage. | `EVT-4711-011` |

### Visibility Gaps

None. The content inspection triage could not run in-band was available at this gate, which closed the gap the promotion rested on.

### Provenance

*   **Playbook:** [`04-Playbooks/02-Investigation-Response/09-insider_threat.md`](../04-Playbooks/02-Investigation-Response/09-insider_threat.md) (`last_updated: 2026-09-10`).
*   **Executor:** Agent.
*   **Capability classes:** Validation query; enrichment (identity directory, content inspection).
*   **Case:** `CASE-4711`.
