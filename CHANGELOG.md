---
title: Changelog
type: log
last_updated: 2026-10-25
license: Apache-2.0
---

# Changelog

All notable changes to the ZeroSOC Framework are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the framework versions per [Semantic Versioning](https://semver.org/spec/v2.0.0.html) as described in [GOVERNANCE.md](GOVERNANCE.md#5-releases). Each release entry credits the contributors whose work landed in it.

## [Unreleased]

### Added

- **02-Taxonomy:** the Case Schema says how a Case carries process lineage and decoded commands, with
  OCSF's own objects: a process's parentage in `parent_process` and `ancestry`, a decoded command in
  a `script` (`script_content`), and a parent the evidence does not show as a process entity with
  what is known of it. The JSON Schema declares both on a related event (`process`, `script`).

- **02-Taxonomy:** an Alert carries its alert type, as `alert_type` on its Observation (DD-28). A
  source that writes its detections for the framework's alert types declares it and the Alert keeps
  it; for any other Alert the executor identifies it at reception.

### Changed

- **01-Foundation, 02-Taxonomy:** the framework states a mapping only where OCSF is ambiguous, where
  it requires the attribute, or where it extends OCSF (DD-23). Any other attribute of the OCSF class
  is used as OCSF defines it, such as the analysts' `notes` beside the two Notes, an Incident
  Finding's closing `comment`, its `src_url` and its `metadata.labels`, and the JSON Schema no longer
  rejects one that is not an object. A source's tags and links leave the per-source extension:
  OCSF carries both.

- **02-Taxonomy, 03-Processes:** tactics and techniques are carried at two levels. Each
  Observation's `attacks` holds the ones it shows: an Alert the ones its detection asserted, and a
  Malicious Observation SHOULD carry the ones it establishes. The Case's `attacks` holds the
  Incident's tactics and techniques: empty until incident confirmation (§2.5), assessed then from
  the Observations that stand before the Investigation Note is written, and kept current as the
  response reveals more. The Alerts' mappings are provisional: one no Observation shows is left
  out, and a broad one is narrowed. A technique edge of an Observation's `attack_graph` names the
  most specific identifier the Observation's `attacks` carries, whose entry gives it its tactic, and
  the Case's graph is the union of the graphs of the Observations that stand. The Triage →
  Investigation contract no longer carries the Case's `attacks`; the Investigation → Response
  contract does. The Investigation Note's Classification renders the Incident's techniques, and both
  Notes render the techniques on Malicious Observations.

- **02-Taxonomy:** `vendor_attributes` on the Case is the Case's severity as the source reports it,
  kept current while the Case is open: the highest of its alerts' where the source reports none,
  and never a value the executor wrote back. It is no longer set only when
  triage overrides the severity, which left a Case with nothing to compare `severity_id` against
  and missed the severity Investigation now re-assesses.

- **03-Processes:** Investigation gains §2.5, *Incident Confirmation*, between the resolution of
  §2.4 and the Investigation Note, which is now §2.6. When the Malicious hypothesis is proven the
  executor re-assesses severity, confidence and Incident Category, estimates the impact, and plans
  the initial response actions from the source's recommendations, the category's playbook and its
  own judgment, dropping redundant ones. Setting `verdict_id = 2` and recording the category,
  techniques and T0 move here from §3.1, which keeps significance, the retrospective sweep and the
  hand-off to Response. Response starts from the planned actions, and the Investigation → Response
  contract carries them in place of the playbook's list. The Case's confidence is re-assessed at
  confirmation instead of staying the highest on the proven side.

- **03-Processes:** checking whether the Case changed while it was being worked on, before a gate
  decision, is a MUST. Before resolving, Investigation checks for alerts that joined the Case after
  promotion and investigates them without returning the Case to triage: each is scored as an Alert
  Observation, and the executor assesses whether it changes the verdict. A new technique or a new
  targeted entity weighs more than a repeat of what the Case already holds.

- **02-Taxonomy:** the Case's title is OCSF `message`, the source's own title for the Case, which
  follows the source as it retitles the Case; the first Alert's title where the source gives none.

- **04-Playbooks:** *Malware / loader execution* check 2, *Payload location*, applies only to a file
  that ran: `Malicious (Medium)` when an unknown or unsigned binary ran from a temporary or shared
  folder, context when the file was not run. A user's Downloads folder is no longer in the list.

- **04-Playbooks:** *Ingress tool transfer to host* check 3 decides on what the file was run to do,
  as *Malware / loader execution* check 7 does: a downloaded file written to a user's folder and run
  shortly after is no longer `Malicious (High)` by itself. Where it landed and how soon it ran are
  context.

- **04-Playbooks:** discovery is `Malicious (Medium)` in the Endpoint triage playbook, in *Malware /
  loader execution* check 4, *Suspicious script / interpreter execution* check 3 and *Remote
  execution / lateral movement* check 5. Administrators and their scripts run the same commands
  every day, so discovery alone corroborates the Malicious side without settling it; credential
  access, recovery sabotage, a tunnel or a further transfer stay `Malicious (High)`.

- **04-Playbooks:** the Endpoint triage playbook reads what a legitimate tool was asked to do.
  *Malware / loader execution* gains check 7, *What the tool was asked to do*: a signed tool's
  command and arguments are Malicious when they open a tunnel, read credentials, stage files or
  disable a defence, and Benign (Medium) when they are clearly benign. *Remote execution / lateral
  movement* check 5 no longer reads every discovery command as Malicious (High): account, group and
  domain discovery is, read-only status and health checks are Benign (Medium). *Malware / loader
  execution* and *Ingress tool transfer to host* name a False Positive condition for a
  threat-intelligence indicator that lists a legitimate, signed tool which was not run, or ran only
  clearly benign commands.

- **03-Processes, 06-Deliverables:** an input of Detection & Analysis §1.1 that the source did not
  supply is no longer a Visibility Gap by itself. A visibility gap is a question the executor needed
  answered and could not get (§1.2). §1.1 and the *Before deciding* list of §1.2 are shorter.

### Removed

- **03-Processes:** the two "former elements" paragraphs of the Triage Note and the Investigation
  Note, which described an earlier version of the Notes.

## [0.1.0] - 2026-10-13

The first tagged release: a baseline of the framework as it stands, for adopters and implementations
to cite and to migrate from. Most modules are still `development` or draft.

Contributors: @G-and-alf.

### Changed

- **03-Processes, 04-Playbooks:** a search that finds no approval carries no weight
  (Detection & Analysis §2.4). The cloud triage check *Change-control correlation* and IC-05
  Query 6 no longer tag a missing approval `Malicious`.
- **03-Processes, 06-Deliverables:** Observations are numbered O1, O2, … across the Case;
  investigation keeps the triage numbers and continues from the next. The `T` that marked a
  triage Observation read like T0 and like an ATT&CK technique.
- **02-Taxonomy:** an Observation names alerts by title, entity and time; identifiers stay in
  `related_events` (Case Schema §3).
- **03-Processes, 01-Foundation:** the alerts alone do not prove Malicious at investigation unless
  one of them is at High confidence (#88, item 7). Detection & Analysis §2.4: Malicious is proven
  at a score of 3 or more only when at least one of its observations is an alert at High
  confidence or an observation beyond the alerts (§1.5); a restatement of an alert counts as the
  alert. Alerts at Medium or Low confidence that the investigation could not check leave the Case
  *neither proven*, and at the timebox it closes as Insufficient Data naming the gaps. Definitions
  §7 points to these conditions. Found in live runs: two Medium audit alerts on a cloud provider's
  own job, which triage could not cover and the investigation could not check, were proven
  Malicious by their own 4 points before any query ran.

- **04-Playbooks, 03-Processes:** the cloud provider's own operations on the organization's tenant.
  A detection firing on the provider's provisioning or maintenance of the tenant is a False Positive
  condition, established by the source's records, never by the actor's name alone (Playbook
  Architecture §4.1, the cloud triage playbook's *Logging / guardrail disabled* and the identity
  triage playbook's *Privileged role / group grant*). In those sections the change-control, scope
  and actor checks no longer tag such a change Malicious, and *Logging / guardrail disabled* gains
  the False Positive condition of an update that enabled or strengthened logging and disabled
  nothing. Detection & Analysis §1.1: Active Case Correlation also appends alerts of the same
  operation, and a shared service identity (built-in principals, the provider's own service
  identities, a service account the SOC Knowledge Base records as shared) is on its own no key for
  correlation or throttling; it stays an entity of the Case. Found in a live run: a provider's
  provisioning job of 70 operations matched two audit alert policies, a literal reading of the
  checks promoted both as undocumented changes by a workload identity, and each run of the job
  opened its own Cases (#90).

- **03-Processes:** Detection & Analysis §1.1 notes that what the executor itself wrote into a
  source's record (its Note, its verdict, the Case) is not one of the inputs the source asserts.
- **03-Processes, 07-Governance:** an identity action targets a person's account or a service
  identity. Incident Response §1 names three kinds of identity it reads in the scope: a person's
  account, a service identity, and a host's own identity (the computer account a directory gives a
  joined device, and the operating system's built-in principals, which OCSF types as a User of type
  System), and it selects an identity action (suspending sessions, disabling the account, resetting its
  credentials) only for a person's account or a service identity the Case shows was used or exposed;
  a host's own identity is contained through its host. §2.1 says a host's own identity is never "an
  identity no critical service runs under", since every service of the host runs under it. The
  Guardrails request an action only on an entity of the kind it acts on, and the payload says what
  the entity is. Found in a live run: a confirmed Incident whose evidence named the computer account
  a scheduled task ran under asked a person to approve disabling that account, which contains no
  one; the scope listed it among the affected identities and nothing in the framework said otherwise.
  Incident Response §2 also says where an identity is contained: an account held by a cloud identity
  provider, an on-premises directory, both (synchronized) or a single host is acted on where each copy
  is held, since disabling or ending the sessions of one copy leaves the others signing in; and an
  action no means of the executor reaches is handed to a person as a task with its steps, keeps its
  place in the matrix, and is recorded under the name of whoever applied it. Found in a live run: a
  local account of a host, which no directory holds, was proposed for disabling through the cloud
  identity provider, and the approved action failed because the provider holds no such account.

- **03-Processes, 04-Playbooks:** the triage close is decided by the rule, not by a label the
  executor chooses. Two things the coverage rule of §1.5 left to the reader are now said. An
  observation stands *beyond the alerts* when it adds to what the detections asserted: a result a
  check or a query returned, a reading of an alert's own evidence the detection did not state, or a
  relation between alerts no single alert states — and it cites what that reading rests on; one
  that says of a single alert only what its detection asserted restates it and is not a Malicious
  observation beyond them, however it is tagged. And the verdict a Close carries follows
  the playbook condition the covering observation *names*, by its place in one of the two lists,
  never a kind it labels on its own: Benign (`5`) when the highest-confidence covering observation
  names a Benign condition, False Positive (`1`) otherwise — including when observations of both
  kinds cover at the same confidence, and when the alerts are explained but no condition of either
  list was named. Measured on one recorded false positive replayed against a live model: the same
  evidence closed as False Positive three times and was promoted once, because one run tagged a
  restatement of the alert as Malicious; the same scenario had earlier closed as `1` and as `5` on
  the same evidence because the model labelled the kind itself. Both readings are now the rule's. A Benign condition is one a **statement** establishes — a change
  ticket, a deployment record, an inventory designation, a written authorization — never what the
  file or the actor is on its own: the endpoint playbook's malware conditions say so, because a
  live executor named "an authorized deployment by the endpoint management platform" for a signed
  internal binary that no deployment record covered, and closed as Benign what was a False Positive.
  An antivirus test file or test detection — the EICAR file, a vendor's test string for the
  anti-malware interface — is a Benign condition the repository or the threat name itself
  records, and the hash-reputation check says so: on ten live Cases the same test-file detection
  was read as malware once and as an authorized test once.
- **03-Processes:** a Note that fails its conformance check is corrected and rendered again from
  the Case; it is never discarded, never a reason to re-decide, never a handover. The check tests
  what §1.6 requires — the elements and their order, side and confidence, event references, a
  check named per gap — and never wording or notation.
- **03-Processes, 06-Deliverables, 02-Taxonomy, CONTRIBUTING:** the four flat statements of the
  `ID (Name)` form that survived the last release now say what §1.6 says: the name is the
  catalogue's own, which an executor knows or looks up — the framework's tables do not replicate
  it — and a bare identifier is never a conformance failure.

- **01-Foundation, 02-Taxonomy:** what an Observation rests on is an event or a **statement** —
  what a system of record or a person states: a Knowledge Base object, a change ticket, a confirmed
  answer — cited by identifier and version with the system or person that holds it; the Observation
  that consulted it is typed `event`. The three kinds of entry are unchanged. A Benign close raises
  an **`exception` ticket** — the Knowledge Base entry it proposes, for a person to confirm — the
  pair of the `tuning` ticket a False Positive raises; the executor proposes and never confirms its
  own, and "emits a Knowledge Base entry" is gone from the six places it stood.

### Fixed

- **02-Taxonomy, 03-Processes, 06-Deliverables:** the Case Timeline answers *what happened*: the
  Alerts, the actions the Observations establish (the adversary's, where there is one) and the
  response actions that ran. The Case Schema already said the timeline is a reconstruction and not
  a listing, but the Notes let the work on the Case into it: the Investigation Note's worked example
  listed the acknowledgment, the enrichment, the promotion and each validation query, and the Triage
  Note said the timeline is usually empty at triage. Triage now compiles the timeline, a Case closed
  at triage keeps it, and investigation extends it; a check or a query is the Observation it
  produced, and an acknowledgment, a promotion or a handover is a lifecycle event. Incident
  Response records an approval, a schedule and a scope change on the Case rather than in the
  timeline, and the Post-Incident Review reads the acknowledgment and the verdict from the
  lifecycle events. The lifecycle's alignment notes map the three records to CSF 2.0:
  the timeline to RS.AN-03, the record of the work to RS.AN-06, chain of custody to RS.AN-07.
- **01-Foundation:** `types` on an Observation is `alert`, `event` or `action`, as the Case Schema
  has it; the definition still said `observation`. `verdict_id` open states no longer list a
  `Suspicious (4)` that is in no enum of the framework.
- **02-Taxonomy, 04-Playbooks:** `T1685` and `T1685.002` are not ATT&CK identifiers; the
  security-tool tampering and cloud-logging alert types now cite `T1562.001 (Disable or Modify
  Tools)` and `T1562.008 (Disable or Modify Cloud Logs)` under the tactic that holds them, Defense
  Evasion.

- **03-Processes, 02-Taxonomy:** a source's **recommended actions are indicative**, as the
  playbook's own checks (§1.2), its queries (§2.2) and the hypotheses (§2.1) already were. The rule
  required each to be "followed, or set aside with a stated reason", and said that an unread
  recommendation is an unexamined step. That sentence is gone. A procedure written for an alert
  type, before anything was known about the Case, does not get to decide what an executor that
  knows the Case spends its attention on. What the executor **ran** is recorded, as the Finding it
  produced; what it did not run is recorded nowhere, because an entry saying a recommendation was
  considered and found irrelevant is not evidence. Measured on a 59-alert Case: 684 published
  actions, 107 distinct instructions, and a three-alert Case whose Note carried 67 findings of
  which six decided it.

- **03-Processes:** §1.2 and §1.3 say what they always meant — the enrichment and the scope
  analysis are **indicative**, what is usually worth knowing rather than a list to be discharged,
  and an executor that queries every capability on every Case spends its budget proving that a
  printer is a printer. In their place, a short floor: what triage does not decide without is what
  the detection asserted, the role of every entity the decision rests on, and the prior Cases on
  the same entities or alert type. A question the executor **chose not to ask** is not a visibility
  gap; a gap is one it needed answered and could not get.

- **03-Processes:** before a gate decision the executor **checks whether the Case changed while it
  was being worked on**. It previously re-read "at each step and before the decision", which asked
  for both more often and more than the point required: a source may append alerts after a Case was
  opened, and a decision must be taken on what the Case holds when it is taken.

- **03-Processes:** a Note renders **the account before the measures**. The element order of §1.6
  and §2.5 becomes Summary, Classification, Rationale, Findings (then Re-classification Pivots in
  §2.5), Case Timeline, Visibility Gaps, Provenance — what happened, what was decided, why, then
  what it rests on. Classification led because it is the block a reader compares between the two
  Notes, which it still is, one element lower; a reader who opens a Note wants to know what
  happened before they are shown a row of identifiers. Observed on a Note rendered into a source's
  own console, where the first thing an analyst met was five `severity_id`-shaped facts about a
  Case they had not yet been told about. The elements and what each holds are unchanged, and an
  implementation that reads the order from this section follows it with no change of its own.

- **02-Taxonomy:** the Case Schema declares `ocsf_version`, the OCSF release the mapping follows
  (`1.9.0`). The release was stated in the document's prose and nowhere a program could read it, so
  a Case written into another system's record, exported or archived carried no statement of what it
  was written against. A consumer reading one out of band now has it on the object's own schema.

- **03-Processes, 06-Deliverables:** rendering a technique code as `ID (Name)` in a Note is a **SHOULD**, stated as one. It was written as a flat declarative — "they are written as `ID (Name)` … never bare codes" — with neither MUST nor SHOULD, and an implementation that read it as a conformance condition refused Notes that were correct in every way that bears on the verdict. How a Note spells an identifier is a readability property; whether it is traceable, tagged and decided is not.

- **02-Taxonomy:** the Case Schema states the **per-source extension convention** — one object per source, under the source's own key, its shape declared where that source is described and validated against it; anything the framework already carries is a mapping and not an extension — and **what each phase must leave on the Case**: every check and query as a Finding with its question, request and query, or as a visibility gap naming the check it prevented; the evidence each Finding rests on; every action with its Course of Action; every entity as an observable; the provenance. A question nobody answered is on the Case rather than in silence; reasoning that has no structured form is prose the Case carries — the Summary, a Finding's own description, the Note's rendering, which is a field of the Case and not a record beside it — and bulk telemetry, message bodies and result sets are on it in no form, under no key.
- **02-Taxonomy, 03-Processes, 06-Deliverables:** what a detection asserts — techniques, threat name and family, detection source and detector, description, recommended actions, per-entity remediation state — is a required input of triage, mapped to native OCSF carriers and recorded on the Case. A Finding's evidence is **kept with the Case** and cited by identifier rather than cited alone, with relevance as the bound: bulk telemetry, result sets, message bodies and file content stay out, and a citation whose referent has expired no longer leaves a Case that cannot show what its verdict rests on.

### Added

- **01-Foundation:** Framework Manifest, Definitions (including the classification levels for severity, confidence and impact, the executors and functions of the tier-less model, and the SOC Knowledge Base), Design Decisions registry, Roadmap.
- **02-Taxonomy:** Incident Categories (IC-01 to IC-15), Alert Types by telemetry domain, the Case Schema with its JSON Schema.
- **03-Processes:** Detection & Response Lifecycle; Preparation & Engineering (draft); Detection & Analysis with the evidence model — findings tagged by side and confidence, triage close by coverage, verify-or-retract investigation, verdict and confidence by score; Incident Response with the containment autonomy matrix; Post-Incident Activity.
- **04-Playbooks (draft):** Playbook Architecture, Operating Guide, eight domain triage playbooks, sixteen Investigation & Response playbooks and a catch-all, five shared enrichment sub-playbooks.
- **05-Metrics (draft):** twenty-one process-anchored volume, speed, quality, autonomy and token-economics metrics with reference bands; disposition quality is expressed as precision and recall per gate (Detection, Triage, Verdict).
- **06-Deliverables:** Triage Note and Investigation Note templates with worked examples.
- **07-Governance (draft):** Agentic Guardrails and Agentic Supervision.
- Community and project files: Contributing guidelines, Governance, Security policy, Code of Conduct, Trademarks, continuous checks (markdownlint, link check, frontmatter validation, DCO).

[Unreleased]: https://github.com/ZeroSOC/zerosoc-framework/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ZeroSOC/zerosoc-framework/releases/tag/v0.1.0
