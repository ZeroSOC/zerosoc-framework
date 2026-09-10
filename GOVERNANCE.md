---
title: ZeroSOC Project Governance
type: policy
status: draft
last_updated: 2026-09-10
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

**Current roster:** the project is in its **bootstrap phase** with a single maintainer. The rules in §4 exist precisely for this phase and self-repeal as the roster grows.

### Project Sponsor

The **Project Sponsor** acts solely as the **Trademark Steward** described in [TRADEMARKS.md](TRADEMARKS.md), following the steward model of foundations such as the Python Software Foundation and the Rust Foundation. The Sponsor holds the "ZeroSOC" mark; it holds **no special technical veto**. Technical direction lives in the open [design-decision registry](01-Foundation/design_decisions.md) and follows the process below like any other change.

## 2. Decision process

Decisions scale with the weight of the change:

1. **Editorial changes** (typos, broken links, formatting, clarifications that don't alter meaning): **lazy consensus** — a PR that passes CI and review merges without prior discussion.
2. **Substantive changes** (new or changed normative content — playbooks, taxonomy entries, metrics, process steps): **issue first**, per CONTRIBUTING §4. The issue is where scope is agreed before writing begins.
3. **Structural changes** (schema elements, ID schemes, module layout, terminology renames, governance itself): require a **Design Decision (DD) entry**, proposed in the issue and included in the PR that implements the change. The DD registry is the project's change-control mechanism.

**Disputes** are resolved by maintainer decision after the discussion has had a fair hearing; the outcome and its rationale are recorded in the issue or pull request that decided it.

## 3. Document maturity and promotion

Per-document maturity (`draft` → `development` → `stable` → `deprecated`) and its promotion rules are defined in the [Framework Manifest](01-Foundation/framework_manifest.md#versioning--document-release-status). Promotion to `stable` is a governance event and requires validation, complete cross-links, and **one review pass by an executor other than the author**. Reviewers and maintainers may provide that pass.

## 4. Bootstrap rules (single-maintainer phase)

Honest governance beats aspirational governance. While the project has one maintainer:

- **Maintainer PRs** with substantive changes stay open for a **72-hour comment window** before merging (editorial changes exempt). CI must be green.
- **External PRs** require maintainer review, as usual.
- Where the maturity model requires a *non-author review* and no second Reviewer exists yet, the maintainer may substitute a **publicly logged self-review** (recorded in the pull request) with a **14-day post-hoc objection window**: any substantiated objection raised in that window reopens the promotion.

Each of these exceptions **self-repeals** the moment a second Reviewer or Maintainer joins the roster; §1's normal rules then apply without needing to amend this document.

## 5. Releases

- The framework versions as **tagged MAJOR.MINOR snapshots** (`v0.x`, `v1.0`, …) per the manifest; adopters conform to a tagged release, never the live repository.
- [CHANGELOG.md](CHANGELOG.md) follows Keep a Changelog; every release gets an entry summarizing what changed and **crediting the contributors** whose work landed in it.
- **Cadence:** a MINOR release is cut when a meaningful batch of work lands — as an ambition, roughly quarterly. Releases are content-driven, never date-driven.
- **Release checklist:** milestone issues resolved → promotions completed per §3 → CHANGELOG.md release entry → annotated git tag → GitHub release.
- Breaking changes to `stable` content ship only in MAJOR releases.

## 6. Communication channels

- **GitHub Issues** — defects, proposals, and all actionable work (issue-first rule).
- **GitHub Discussions** — questions, ideas and open-ended exchange before something becomes an issue, where enabled; otherwise an issue serves.

The channel set is deliberately minimal; new channels are added only when the community's volume demands them.

## 7. Amendments

This document changes by pull request accompanied by a DD entry (it is a structural document). During the bootstrap phase, amendments follow the §4 comment-window rule.
