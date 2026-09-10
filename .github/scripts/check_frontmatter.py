#!/usr/bin/env python3
"""Frontmatter validator for the ZeroSOC Framework.

Enforces the document schema from 01-Foundation/framework_manifest.md
(§ Versioning & Document Release Status) and DD-15:

- Every tracked Markdown file outside the exempt directories has a YAML
  frontmatter block with `title`, `type`, `last_updated`, and `license`.
- `status` is required except for `type: index` and `type: log` documents
  (and the exempt directories, which are skipped entirely).
- `type`, `status`, and `license` values must come from the allowed sets.

Stdlib-only (no PyYAML): the frontmatter grammar used in this repo is flat
`key: value` pairs plus optional list values, which is all we parse.
"""

import re
import subprocess
import sys

EXEMPT_DIRS = ("raw/", "assets/", ".github/")
EXEMPT_FILES = {"LICENSE", "NOTICE"}

ALLOWED_TYPES = {
    "concept", "process", "policy", "strategy", "playbook",
    "reference", "template", "index", "log",
}
ALLOWED_STATUS = {"draft", "development", "stable", "deprecated"}
STATUS_EXEMPT_TYPES = {"index", "log"}
REQUIRED_KEYS = ("title", "type", "last_updated", "license")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def tracked_markdown_files():
    out = subprocess.run(
        ["git", "ls-files", "*.md"], capture_output=True, text=True, check=True
    ).stdout
    for path in out.splitlines():
        if path.startswith(EXEMPT_DIRS) or path in EXEMPT_FILES:
            continue
        yield path


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        first = fh.readline()
        if first.strip() != "---":
            return None
        fields = {}
        for line in fh:
            if line.strip() == "---":
                return fields
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
            if m:
                fields[m.group(1)] = m.group(2).strip().strip("\"'")
        return None  # unterminated block


def main():
    errors = []
    for path in tracked_markdown_files():
        fm = parse_frontmatter(path)
        if fm is None:
            errors.append(f"{path}: missing or unterminated YAML frontmatter block")
            continue
        for key in REQUIRED_KEYS:
            if not fm.get(key):
                errors.append(f"{path}: missing required frontmatter key `{key}`")
        doc_type = fm.get("type", "")
        if doc_type and doc_type not in ALLOWED_TYPES:
            errors.append(f"{path}: unknown `type: {doc_type}` (allowed: {sorted(ALLOWED_TYPES)})")
        if doc_type not in STATUS_EXEMPT_TYPES:
            status = fm.get("status", "")
            if not status:
                errors.append(f"{path}: missing `status` (required unless type is index/log)")
            elif status not in ALLOWED_STATUS:
                errors.append(f"{path}: unknown `status: {status}` (allowed: {sorted(ALLOWED_STATUS)})")
        last_updated = fm.get("last_updated", "")
        if last_updated and not DATE_RE.match(last_updated):
            errors.append(f"{path}: `last_updated` must be YYYY-MM-DD (got `{last_updated}`)")
        license_val = fm.get("license", "")
        if license_val and license_val != "Apache-2.0":
            errors.append(f"{path}: `license` must be `Apache-2.0` (got `{license_val}`)")

    if errors:
        print(f"Frontmatter validation failed ({len(errors)} error(s)):\n")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    print("Frontmatter validation passed.")


if __name__ == "__main__":
    main()
