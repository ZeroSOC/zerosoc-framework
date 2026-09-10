<!-- Thanks for contributing! See CONTRIBUTING.md for the full workflow. -->

## What & why

<!-- Scope of the change. Link the issue it implements (issue-first rule for substantive changes): -->
Closes #

## Checklist

- [ ] An issue was opened and discussed before this PR (except editorial fixes)
- [ ] All commits carry a DCO `Signed-off-by` line (`git commit -s`)
- [ ] YAML frontmatter is valid on every touched document (`title`, `type`, `status`, `last_updated`, `license`; `status` exempt for `type: index`/`type: log`)
- [ ] All cross-document links and anchors resolve
- [ ] Executor and vendor neutrality respected (no brand names in normative text; every step is an action any executor performs)
- [ ] Structural or schema changes include a Design Decision entry in `01-Foundation/design_decisions.md`
- [ ] An entry was added to `CHANGELOG.md` under *Unreleased*
- [ ] **Playbook changes only:** the playbook follows the Architecture templates (tagged checks, False Positive and Benign conditions, both-outcome queries) and a tabletop walkthrough was performed
- [ ] No proprietary, commercial or customer-sensitive details anywhere in the change
