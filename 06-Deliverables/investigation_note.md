---
title: Investigation Note Template
type: template
last_updated: 2026-09-10
license: Apache-2.0
status: development
---

# Investigation Note

Fill-in template and worked example for the **Investigation Note**, the verdict evidence record produced when Investigation closes a Case or confirms an Incident. The canonical element list is [Detection & Analysis §2.5](../03-Processes/02-detection_and_analysis.md#25-investigation-note-verdict-evidence-record); this page is the practitioner-facing form. Naming convention: `investigation_note_<case-id>_<YYYYMMDD-HHMM>`.

## Template

### Classification & Assessment

*The confirmed (or, on close, the last candidate) Incident Category; `severity_id`; `confidence_id` as resolved in §2.4; for a confirmed Incident, `impact_id` and the significance and cross-border flags ([§3.1](../03-Processes/02-detection_and_analysis.md#31-incident-promotion)).*

### Executed Queries

*The validation queries run, each with its outcome and the tag of the finding it produced — `Malicious (Low|Medium|High)`, `Benign (Low|Medium|High)`, or context — and its event reference. Triage findings verified or retracted are listed with their new state.*

| # | Query | Outcome | Tag | Event ref |
|---|---|---|---|---|
| 1 | `<question>` | `<what was found>` | `<tag>` | `<event ref>` |

### Resolution Rationale

*The resolution of [§2.4](../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence): the score of each side, the side proven and the findings that carry it (for Benign, which finding explains the alert and covers the Medium and High Malicious findings), the findings retracted and why, and the resulting confidence. The verdict and, on a close, the tuning ticket or Knowledge Base entry emitted.*

### Re-classification Pivots

*Any candidate `incident_category` change, with the reason and the evidence that triggered it; "None." otherwise.*

### Case Timeline

*Chronological reconstruction of the Case: the attacker's course of action (initial access → progression → objective, where established) interleaved with the detection and response actions taken. The earliest **confirmed malicious** event is marked T0; context rows before it (reconnaissance, benign activity later ruled out) are permitted. A Case closed without the Malicious hypothesis proven carries a timeline but no T0.*

| UTC timestamp | Actor / executor | Action / observation | Event ref |
|---|---|---|---|
| `<timestamp>` | `<actor/executor>` | `<action/observation — T0 if earliest confirmed malicious event>` | `<OCSF finding UID / event link>` |

### Evidence References

*Links to the preserved evidence, plus the underlying event(s) grounding each finding, cited by identifier or link.*

### Visibility Gaps

*Every required data source unavailable during investigation, each paired with the check it prevented; write "None." when no gap occurred.*

### Provenance

*The playbook(s) used (path plus `last_updated` as version), the executor (human / automation / agent — all classes that contributed), the capability classes invoked, and the Case identifier.*

---

## Worked Example

`investigation_note_CASE-4711_20260914-1640` — continues the Triage Note example of [triage_note.md](triage_note.md).

### Classification & Assessment

Last candidate Incident Category: **IC-09** (Insider Threat & Privilege Misuse). `severity_id`: **2 (Low)**. `confidence_id`: **3 (High)**. No Incident: impact not assessed.

### Executed Queries

| # | Query | Outcome | Tag | Event ref |
|---|---|---|---|---|
| T1 | Triage finding 1 (the alert), verified | Unchanged. | `Malicious (Low)` | `DF-4711-001` |
| T3 | Triage finding 3 (access path), verified | Unchanged. | `Benign (Low)` | `DF-4711-001` |
| 1 | Does the use fit `j.doe`'s role? | Drafting marketing copy with a general-purpose AI assistant is plausible for the role. | `Benign (Low)` | `EVT-4711-006` |
| 2 | Does the usage pattern deviate from the user's baseline? | Single, first occurrence; no recurring or bulk pattern. | `Benign (Low)` | `EVT-4711-007` |
| 3 | Is there HR risk context (resignation, performance process, offboarding)? | None. | context | `EVT-4711-008` |
| 4 | Was regulated or sensitive data posted? (content inspection; tests `T1567 (Exfiltration Over Web Service)`) | The posted content is a product description draft; no regulated, proprietary or personal data. This explains the alert: an unsanctioned tool used for non-sensitive work. | `Benign (High)` | `DF-4711-009` |
| 5 | Any concealment (VPN bypass, private browsing, log deletion)? | None. | `Benign (Low)` | `EVT-4711-010` |

### Resolution Rationale

Malicious side: the alert, `Malicious (Low)`, weight 1; no finding beyond it. Benign side: findings T3, 1, 2, 5 at Low (1 each) and finding 4 at High (3): weight 7. **Benign hypothesis proven**: the score reaches the bar and finding 4 explains the alert, so the alert — the only Malicious finding — is accounted for and leaves no residual observation; there is no Medium or High Malicious finding to cover. No finding retracted. `confidence_id`: **3 (High)** — the highest confidence on the proven side. `verdict_id`: **5 (Benign)**. No malicious event confirmed: no T0. Emitted: a Knowledge Base entry recording the use of AI assistants for non-sensitive drafting in Marketing, and a request for a sanctioning decision on the application, so that the recurrence closes at triage.

### Re-classification Pivots

None. Candidate categories IC-09 / IC-11 stand; the Case closes without a category change.

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
| 2026-09-14 16:35 | Agent (Investigation) | Benign hypothesis proven at High confidence; Case closed Benign (`verdict_id: 5`); Knowledge Base entry emitted. | `EVT-4711-011` |

### Evidence References

SaaS discovery alert record; content-inspection log for the session; identity directory role record; 30-day baseline query result for `j.doe`.

- `EVT-4711-006` (role assessment against the identity directory record, 15:20 UTC) — grounds query 1.
- `EVT-4711-007` (30-day baseline query for `j.doe`, 15:35 UTC) — grounds query 2.
- `EVT-4711-008` (HR risk context lookup, 15:50 UTC) — grounds query 3.
- `DF-4711-009` (content-inspection log for the session, 16:10 UTC) — grounds query 4, the finding that explains the alert.
- `EVT-4711-010` (endpoint and session concealment check, 16:20 UTC) — grounds query 5.

### Visibility Gaps

None.

### Provenance

*   **Playbook:** [`04-Playbooks/02-Investigation-Response/09-insider_threat.md`](../04-Playbooks/02-Investigation-Response/09-insider_threat.md) (`last_updated: 2026-09-10`).
*   **Executor:** Agent.
*   **Capability classes:** Validation query; enrichment (identity directory, content inspection).
*   **Case:** `CASE-4711`.
