---
title: ZeroSOC Project Governance
type: policy
status: draft
last_updated: 2026-11-05
license: Apache-2.0
---

# ZeroSOC Project Governance

This document defines **how decisions are made** in the ZeroSOC Framework project — who holds which role, how changes are accepted, and how releases are cut. It complements [CONTRIBUTING.md](CONTRIBUTING.md) (how to contribute), [TRADEMARKS.md](TRADEMARKS.md) (naming rights), and the [Framework Manifest](01-Foundation/framework_manifest.md) (versioning and document maturity).

## 1. Roles

| Role | Who | Rights | How you get there |
|---|---|---|---|
| **Contributor** | Anyone | Open issues and pull requests (DCO sign-off required), comment and review | Contribute |
| **Maintainer** | `G-and-alf`, `in-secure` | Merge rights; dispute resolution; release authority | Sustained contributions or relevant security operations experience, appointed by agreement of the existing Maintainers |

The project aims to have Maintainers from more than one organization.

### Project Sponsor

The **Project Sponsor** acts solely as the **Trademark Steward** described in [TRADEMARKS.md](TRADEMARKS.md), following the steward model of foundations such as the Python Software Foundation and the Rust Foundation. The Sponsor holds the "ZeroSOC" mark; it holds **no special technical veto**. Technical direction lives in the open [design-decision registry](01-Foundation/design_decisions.md) and follows the process below like any other change.

## 2. Decision process

Decisions scale with the weight of the change:

| Change | What it takes |
|---|---|
| **Everyday changes:** editorial fixes, changes to `draft` documents, and changes to `development` documents that need no Design Decision | Green checks, then a Maintainer merges. |
| **Decisions:** a Design Decision on a `development` or `stable` document, a substantive change to a `stable` document, and any change to this document | An issue first, where the decision is proposed, then a pull request open for at least 72 hours with every objection answered. |
| **Promotion to `stable`** | The requirements of §3, including a review by someone other than the author. |

A **structural change** (schema elements, ID schemes, module layout, terminology renames, governance itself) needs a **Design Decision (DD) entry**, included in the pull request that implements it. The DD registry is the project's change-control mechanism.

**Working Group.** The Working Group discusses the framework on its calls and on Slack. It holds no vote: a view counts once it is written on the issue or pull request, and a decision is final when the pull request carrying it merges. An objection to a merged change goes on its pull request or on a new issue.

**Disputes** are resolved by Maintainer decision after the discussion has had a fair hearing; the outcome and its rationale are recorded in the issue or pull request that decided it. If the Maintainers cannot agree, the change does not land, and the disagreement and its reasons are recorded there.

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
- **Promotion to `stable` requires, at minimum:** (a) validation by a flow-test, tabletop exercise or equivalent check against real material; (b) complete cross-links with no dangling references; (c) one review pass by an executor other than the author — human or agent, per Executor Neutrality; (d) all normative dependencies declared at `stable` status.
- **Demotion is legitimate.** A `stable` document invalidated by new insight returns to `development` with a changelog entry. Honesty over face-saving.

## 4. Releases

- The framework is released as tagged **Semantic Versioning (MAJOR.MINOR.PATCH)** snapshots (`v0.1.0`, `v1.0.0`, …). A release tag is the citable conformance target: adopters conform to "ZeroSOC vX.Y", or to an exact snapshot `vX.Y.Z`, never to the live repository.
- **MAJOR (`X.0.0`):** breaking changes to `stable` content — renumbered identifiers, removed sections, changed normative schemas or lifecycle requirements.
- **MINOR (`X.Y.0`):** additive, backwards-compatible extensions — new domain triage playbooks, additional Incident Categories, expanded metrics.
- **PATCH (`X.Y.Z`):** non-normative errata, typo corrections, link fixes and editorial clarifications.
- Until `v1.0.0` the framework is in the `0.x` series: stability guarantees are best-effort, and `development` is the default status for active normative content.
- [CHANGELOG.md](CHANGELOG.md) follows Keep a Changelog; every release entry summarizes what changed since the previous tag and **credits the contributors** whose work landed in it.
- **Cadence:** a MINOR release is cut when a meaningful batch of work lands — as an ambition, roughly quarterly. Releases are content-driven, never date-driven.
- **Release checklist:** milestone issues resolved → promotions completed per §3 → CHANGELOG.md release entry → annotated git tag → GitHub release.

## 5. Communication channels

- **GitHub Issues** — defects, proposals, and all actionable work.
- **GitHub Discussions** and **Slack** — questions, ideas and open-ended exchange before something becomes an issue, where enabled; otherwise an issue serves.
- **Working Group calls** — discussion of open proposals (§2).

## 6. Amendments

This document changes by pull request accompanied by a DD entry (it is a structural document), on the route for Decisions in §2.
