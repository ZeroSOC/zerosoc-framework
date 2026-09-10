---
title: Triage Note Template
type: template
last_updated: 2026-09-10
license: Apache-2.0
status: development
---

# Triage Note

Fill-in template and worked example for the **Triage Note**, the decision record every triage — human, automation or agent — produces. The canonical element list is [Detection & Analysis §1.6](../03-Processes/02-detection_and_analysis.md#16-triage-note); this page is the practitioner-facing form. Naming convention: `triage_note_<case-id>_<YYYYMMDD-HHMM>`.

## Template

### Summary

*The alert(s), the entities involved and the behavior that triggered them.*

### Actions Taken

*The logs and systems reviewed, the enrichment capabilities queried, the Knowledge Base and prior Cases consulted.*

### Findings

*The alerts first, each tagged `Malicious (Low|Medium|High)` at the confidence the tool reports (or derived from its severity). Then every enrichment, scope and correlation result, each tagged with its side and confidence or marked context. Each finding cites its event reference.*

| # | Finding | Tag | Event ref |
|---|---|---|---|
| 1 | `<alert>` | `Malicious (<confidence>)` | `<finding UID>` |
| 2 | `<enrichment or correlation result>` | `<Malicious/Benign (confidence)>` or context | `<event ref>` |

### Decision & Justification

*The decision — **Close** (False Positive, Benign, or Duplicate with the master Case identifier) or **Promote** — with the coverage rule of [§1.5](../03-Processes/02-detection_and_analysis.md#15-triage-decision) applied in one or two sentences: which Benign findings cover which alerts, or why they do not. For a promoted Case: `severity_id`, `confidence_id` leaving triage, `impact_id` when already known, and the candidate Incident Categories.*

### References

*Links to the queries, indicators and internal records used, plus a resolvable reference for each event cited in the Findings — an OCSF finding or event identifier, or a platform event link. A finding without a traceable event reference is not conformant.*

### Visibility Gaps

*Every required data source unavailable during triage, each paired with the check it prevented; write "None." when no gap occurred.*

### Provenance

*The playbook(s) used (path plus `last_updated` as version), the executor (human / automation / agent — all classes that contributed, e.g. `automation + agent`), the capability classes invoked, and the Case identifier.*

---

## Worked Example

`triage_note_CASE-4711_20260914-1512`

### Summary

The SaaS discovery control raised **Unsanctioned SaaS app usage (Shadow IT / Shadow AI discovery)**, severity Low: user `j.doe` posted content to an AI assistant not on the sanctioned list, from a managed corporate laptop.

### Actions Taken

Queried the reputation of the destination domain; the CMDB for the endpoint; the identity directory for the user's role and privilege; the SOC Knowledge Base for an approved exception; the active-Cases store for prior Cases on the user, the endpoint and the alert type.

### Findings

| # | Finding | Tag | Event ref |
|---|---|---|---|
| 1 | Unsanctioned SaaS app usage: `j.doe` → AI assistant, content posted over the corporate network path. Tool reports no confidence; severity Low → Low. | `Malicious (Low)` | `DF-4711-001` |
| 2 | `j.doe` is a standard-privilege user in Marketing, within normal working hours; the endpoint is a managed laptop, not a Crown Jewel. | context | `EVT-4711-003`, `EVT-4711-004` |
| 3 | Access over the normal corporate network path: no VPN bypass, no private browsing session. | `Benign (Low)` | `DF-4711-001` |
| 4 | Destination is a well-known AI assistant with a non-malicious reputation. Reputation does not bear on the hypothesis: the concern is the data posted, not the destination. | context | `DF-4711-002` |
| 5 | No approved exception in the Knowledge Base for this user or application; no prior Cases for the user, the endpoint or the alert type. | context | `EVT-4711-005` |

### Decision & Justification

**Promote** to Investigation. The only Benign finding (3) weighs 1 and does not exceed the alert's weight of 1, so the alert is not covered: whether sensitive content was posted cannot be verified at triage, since no content-inspection result is available in-band. If content exposure is confirmed, the behavior maps to `T1567 (Exfiltration Over Web Service)`. `severity_id`: **2 (Low)**. `confidence_id` leaving triage: **1 (Low)** — the alert's confidence; the Benign finding exists but does not close the Case. Impact: not assessable at triage. Candidate Incident Categories: **IC-09** (Insider Threat & Privilege Misuse), **IC-11** (Data Breach / Exfiltration).

### References

SaaS discovery alert; reputation lookup result; CMDB asset record; identity directory record; Knowledge Base and active-Cases queries.

- `DF-4711-001` (Detection Finding [2004], SaaS discovery: `j.doe` → AI assistant, POST over the corporate network path, 2026-09-14 14:58 UTC) — the alert; grounds findings 1 and 3.
- `DF-4711-002` (reputation lookup on the destination domain, 15:06 UTC) — grounds finding 4.
- `EVT-4711-003` (CMDB asset record for the endpoint, queried 15:07 UTC) — grounds finding 2.
- `EVT-4711-004` (identity directory record for `j.doe`, queried 15:07 UTC) — grounds finding 2.
- `EVT-4711-005` (Knowledge Base and active-Cases queries, 15:08 UTC) — grounds finding 5.

### Visibility Gaps

None.

### Provenance

*   **Playbook:** [`04-Playbooks/01-Triage/cloud.md`](../04-Playbooks/01-Triage/cloud.md) (`last_updated: 2026-09-10`).
*   **Executor:** Agent.
*   **Capability classes:** Enrichment (reputation, CMDB, identity directory, Knowledge Base); read-only telemetry query.
*   **Case:** `CASE-4711`.
