---
title: ZeroSOC Project Governance
type: policy
status: draft
last_updated: 2026-09-19
license: Apache-2.0
---

# ZeroSOC Project Governance

This document defines **how decisions are made** in the ZeroSOC Framework project — who holds which role, how changes are accepted, and how releases are cut. It complements [CONTRIBUTING.md](CONTRIBUTING.md) (how to contribute), [TRADEMARKS.md](TRADEMARKS.md) (naming rights), and the [Framework Manifest](01-Foundation/framework_manifest.md) (versioning and document maturity).

## 1. Roles

| Role | Who | Rights | How you get there |
|---|---|---|---|
| **Contributor** | Anyone | Open issues and pull requests (DCO sign-off required) | Contribute |
| **Reviewer** | Recognized contributors | Provide the **non-author review** the maturity model requires for promotion to `stable`; triage issues | Sustained quality contributions — as a guideline, ~5 merged substantive PRs and ~3 useful reviews — confirmed by maintainer consensus |
| **Maintainer** | Project stewards | Merge rights; dispute resolution; release authority | Reviewer + ~3 months of sustained engagement, appointed by consensus of existing maintainers |

### Project Sponsor

The **Project Sponsor** acts solely as the **Trademark Steward** described in [TRADEMARKS.md](TRADEMARKS.md), following the steward model of foundations such as the Python Software Foundation and the Rust Foundation. The Sponsor holds the "ZeroSOC" mark; it holds **no special technical veto**. Technical direction lives in the open [design-decision registry](01-Foundation/design_decisions.md) and follows the process below like any other change.

## 2. Decision process

Decisions scale with the weight of the change:

1. **Editorial changes** (typos, broken links, formatting, clarifications that don't alter meaning): **lazy consensus** — a PR that passes CI and review merges without prior discussion.
2. **Substantive changes** (new or changed normative content — playbooks, taxonomy entries, metrics, process steps): **issue first**, per CONTRIBUTING §4. The issue is where scope is agreed before writing begins.
3. **Structural changes** (schema elements, ID schemes, module layout, terminology renames, governance itself): require a **Design Decision (DD) entry**, proposed in the issue and included in the PR that implements the change. The DD registry is the project's change-control mechanism.

**Disputes** are resolved by maintainer decision after the discussion has had a fair hearing; the outcome and its rationale are recorded in the issue or pull request that decided it.

## 3. Document maturity

Every framework document declares a `status` field in its YAML frontmatter, alongside `title`, `type`, `last_updated` and `license`. Documents of `type: index` and `type: log` are exempt: navigational and ledger artifacts have no release maturity. `last_updated` is the per-document **revision** identifier — the version recorded in Note provenance — while `status` states **maturity**, not revision.

| Status | Meaning | Guarantees |
|---|---|---|
| `draft` | Exploratory: an initial proposal, a placeholder, or a first pass that has not been verified in detail. Shape, scope and existence may change without notice, and parts of it may simply be wrong. | None. MUST NOT be cited as a conformance target; RFC-2119 keywords carry no obligation. |
| `development` | Content-complete candidate undergoing validation (flow-tests, tabletop exercises, adopter feedback). The default state for new normative content. | Structure and intent are settled; details may change between MINOR releases. Feedback is explicitly invited. |
| `stable` | Normative. Validated, cross-linked, part of the conformance surface. | RFC-2119 keywords are binding. Identifiers, section anchors and normative requirements change only at a MAJOR release. |
| `deprecated` | Superseded or withdrawn; retained for the record. | The frontmatter MUST name the successor document, or state that none exists. New content never cites a deprecated document. |

### Promotion and demotion

- **Transitions are governance events.** Every status change is recorded in [CHANGELOG.md](CHANGELOG.md) with its rationale; a promotion that settles a contested design choice also warrants a [design decision](01-Foundation/design_decisions.md) entry.
- **Promotion to `stable` requires, at minimum:** (a) validation by a flow-test, tabletop exercise or equivalent check against real material; (b) complete cross-links with no dangling references; (c) one review pass by an executor other than the author — human or agent, per Executor Neutrality, and Reviewers or Maintainers may provide it; (d) all normative dependencies declared at `stable` status.
- **Demotion is legitimate.** A `stable` document invalidated by new insight returns to `development` with a changelog entry. Honesty over face-saving.

## 4. Rules while the roster is small

Honest governance beats aspirational governance. A two-maintainer roster can meet the review requirements in full, and does:

- **Every substantive pull request is reviewed by someone other than its author**, including a maintainer's own. CI must be green. No change merges on its author's approval alone.
- **Maintainer PRs** with substantive changes also stay open for a **72-hour comment window** before merging, so that contributors outside the roster have time to object (editorial changes exempt).
- **Promotion to `stable`** uses the non-author review of §3. The self-review substitute this section previously allowed no longer applies and is not available.
- **Appointments** to Reviewer or Maintainer are by consensus of the existing maintainers, which at this size means both must agree.
- **A deadlock between the two maintainers is not resolved by merging.** Where §2 leaves a dispute undecided, the change does not land, and the disagreement and its reasons are recorded in the issue or pull request. The project would rather carry an open question than a decision one steward does not stand behind.

These rules describe the current roster. As it grows they are revisited by amendment under §7, not by silent lapse.

## 5. Releases

- The framework is released as tagged **Semantic Versioning (MAJOR.MINOR.PATCH)** snapshots (`v0.1.0`, `v1.0.0`, …). A release tag is the citable conformance target: adopters conform to "ZeroSOC vX.Y", or to an exact snapshot `vX.Y.Z`, never to the live repository.
- **MAJOR (`X.0.0`):** breaking changes to `stable` content — renumbered identifiers, removed sections, changed normative schemas or lifecycle requirements.
- **MINOR (`X.Y.0`):** additive, backwards-compatible extensions — new domain triage playbooks, additional Incident Categories, expanded metrics.
- **PATCH (`X.Y.Z`):** non-normative errata, typo corrections, link fixes and editorial clarifications.
- Until `v1.0.0` the framework is in the `0.x` series: stability guarantees are best-effort, and `development` is the default status for active normative content.
- [CHANGELOG.md](CHANGELOG.md) follows Keep a Changelog; every release entry summarizes what changed since the previous tag and **credits the contributors** whose work landed in it.
- **Cadence:** a MINOR release is cut when a meaningful batch of work lands — as an ambition, roughly quarterly. Releases are content-driven, never date-driven.
- **Release checklist:** milestone issues resolved → promotions completed per §3 → CHANGELOG.md release entry → annotated git tag → GitHub release.

## 6. Communication channels

- **GitHub Issues** — defects, proposals, and all actionable work (issue-first rule).
- **GitHub Discussions** and **Slack** — questions, ideas and open-ended exchange before something becomes an issue, where enabled; otherwise an issue serves.

## 7. Amendments

This document changes by pull request accompanied by a DD entry (it is a structural document). Amendments follow the review and comment-window rules of §4.
