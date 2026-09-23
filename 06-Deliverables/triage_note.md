---
title: Triage Note Template
type: template
last_updated: 2026-09-24
license: Apache-2.0
status: draft
---

# Triage Note

Fill-in template and worked example for the **Triage Note**, the decision record every triage — human, automation or agent — produces. The canonical element list is [Detection & Analysis §1.6](../03-Processes/02-detection_and_analysis.md#16-triage-note); this page is the practitioner-facing form. Naming convention: `triage_note_<case-id>_<YYYYMMDD-HHMM>`.

The Note renders the account first, then what was decided, then why, then what it rests on, so that a reader reaches the substance before the apparatus. It holds no state of its own: everything it shows is already on the Case, sampled at this gate.

## Template

### Summary

*A factual account, current as at this gate: **what happened and when**, which entities were involved and **who acted on whom**, and **the root cause** where it was discovered — how it is known, and how confident you are of it. That confidence is prose and is **not** `confidence_id`, which is confidence in the Malicious/Benign verdict alone.*

### Classification

*`severity_id`, `confidence_id` and `impact_id` (**Unknown** until it is known), the candidate Incident Categories, and the decision: **Close** or **Promote** ([§1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision)), with the `verdict_id` on a Close and the master Case identifier where that verdict is Duplicate.*

### Rationale

*One to two sentences, citing the Observations, saying why the decision follows: which alerts the Benign observations cover, or which Malicious observation stands beyond them.*

### Observations

*Every Observation the Case holds: the Alerts first, then the result of each check run — entity context, entity and process analysis, threat-intelligence results, and the historical baseline. Each renders with its **side and confidence** — `Malicious (High)`, `Benign (Medium)`, … — or with neither where it is pure context; with **what produced it**, the check being the Observation's `analytic`; and with **the events it rests on**, cited by OCSF identifier or platform event link. An Observation without a traceable event reference is not conformant, and a raw-log dump is not an event reference.*

*Each **Alert** also renders what its detection asserted ([§1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment)): the technique identifiers as `ID (Name)`, the threat name and family where one was assigned, the detection source and the detector, and the remediation state of each entity it names — blocked, quarantined, removed or active.*

*The source's **recommended actions** are indicative ([§1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision)). One you ran renders as the Observation it produced, naming the recommendation it came from; one you did not run renders nowhere.*

| # | Observation | Tag | Produced by | Event ref |
|---|---|---|---|---|
| 1 | `<alert>` — `<T#### (Name), ...>`; threat `<name (family)>`; detected by `<detection source>`; `<entity>` `<remediation state>` | `Malicious (<confidence>)` | `<detector>` | `<observation UID>` |
| 2 | `<enrichment, scope or correlation result>` | `<Malicious/Benign (confidence)>` or context | `<the check that produced it>` | `<event ref>` |
| 3 | `<result of a recommended action you ran>` | `<tag>` or context | `<the recommendation it came from>` | `<event ref>` |

### Case Timeline

*The Observations the Case flags for the narrative, in `first_seen_time` order. Early in a Case usually nothing is flagged; write "None." then.*

### Response Actions

*The remediation the Case carries, in one place. The **observed remediation** — each Remediation Activity the Case references, the entity it acted on and whether it succeeded — and the **planned remediation** — each open ticket the Case raised, with its kind. A remediation the source performed before triage opened renders here too: it is recorded, never weighed as evidence. Write "None." when the Case carries neither.*

| What | State | Entity | Ref |
|---|---|---|---|
| `<the action>` | observed — `<succeeded / failed / partial>` | `<entity>` | `<Remediation Activity uid>` |
| `<the action asked for>` | planned — `<kind>` | `<entity>` | `<ticket uid>` |

### Visibility Gaps

*Every required data source unavailable during triage, and every required input of [§1.1](../03-Processes/02-detection_and_analysis.md#11-reception-aggregation-and-assignment) the source did not supply, each paired with the check it prevented; write "None." when no gap occurred.*

### Provenance

*The playbook(s) used (path plus `last_updated` as version), the executor (human / automation / agent — all classes that contributed, e.g. `automation + agent`), the capability classes invoked, and the Case identifier.*

---

## Worked Example

`triage_note_CASE-4711_20260914-1512`

### Summary

At 14:58 UTC on 2026-09-14 the SaaS discovery control recorded `j.doe` — a standard-privilege Marketing user, on a managed corporate laptop — posting content to an AI assistant that is not on the sanctioned list. The account of the session is certain: it rests on the detection's own record of the request. What it means is not, because the root cause turns on whether the content was sensitive, and nothing available at this gate inspects it.

### Classification

`severity_id`: **2 (Low)**. `confidence_id`: **1 (Low)** — the alert's own confidence; the Benign observation exists but does not close the Case. `impact_id`: **0 (Unknown)** — not assessable at triage. Candidate Incident Categories: **IC-09** (Insider Threat & Privilege Misuse), **IC-11** (Data Breach / Exfiltration). Decision: **Promote** to Investigation.

### Rationale

The one Benign observation (3) weighs 1 and does not exceed the alert's own weight of 1, so the alert is not covered: whether sensitive content was posted cannot be verified at triage, and the alert stands unexplained. If content exposure is confirmed, the behavior maps to `T1567 (Exfiltration Over Web Service)`.

### Observations

| # | Observation | Tag | Produced by | Event ref |
|---|---|---|---|---|
| 1 | Unsanctioned SaaS app usage: `j.doe` → AI assistant, content posted over the corporate network path. No technique asserted; no threat name; no entity remediated — the session was recorded, not blocked. Tool reports no confidence; severity Low → Low. | `Malicious (Low)` | SaaS discovery control | `DF-4711-001` |
| 2 | `j.doe` is a standard-privilege user in Marketing, within normal working hours; the endpoint is a managed laptop, not a Crown Jewel. | context | CMDB and identity directory lookup | `EVT-4711-003`, `EVT-4711-004` |
| 3 | Access over the normal corporate network path: no VPN bypass, no private browsing session. | `Benign (Low)` | Session detail on the alert record | `DF-4711-001` |
| 4 | Destination is a well-known AI assistant with a non-malicious reputation. Reputation does not bear on the hypothesis: the concern is the data posted, not the destination. | context | Multi-engine reputation lookup | `DF-4711-002` |
| 5 | No approved exception in the Knowledge Base for this user or application; no prior Cases for the user, the endpoint or the alert type. | context | Knowledge Base and active-Cases query | `EVT-4711-005` |

### Case Timeline

None. No Observation is flagged for the narrative at this gate.

### Response Actions

None. The source recorded the session and remediated nothing, and triage asked for nothing: the Case promotes for a check it could not run, not for an action it could not take.

### Visibility Gaps

Content inspection was not available in-band, which prevented the check on whether regulated or proprietary data was posted — the check the promotion turns on.

### Provenance

*   **Playbook:** [`04-Playbooks/01-Triage/cloud.md`](../04-Playbooks/01-Triage/cloud.md) (`last_updated: 2026-09-10`).
*   **Executor:** Agent.
*   **Capability classes:** Enrichment (reputation, CMDB, identity directory, Knowledge Base); read-only telemetry query.
*   **Case:** `CASE-4711`.
