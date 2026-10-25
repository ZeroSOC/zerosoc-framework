#!/usr/bin/env python3
"""The ZeroSOC extension to OCSF and the Case's JSON Schema declare the same framework fields.

`02-Taxonomy/case_schema.json` validates a Case. `02-Taxonomy/ocsf_extension/` declares the same
fields in OCSF's own form, for OCSF's tools: the `zerosoc` object the Case, its Observations and
its tickets carry, the objects it holds, and the patches that add it to the Incident Finding class
and to the `finding_info` and `ticket` objects. A field in one and not the other, or typed
differently, fails here; whether the extension compiles against OCSF is checked by OCSF's own
compiler and validator in CI.

Standard library only. Exit 1 on any difference.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "02-Taxonomy" / "case_schema.json"
EXTENSION = ROOT / "02-Taxonomy" / "ocsf_extension"
NAME, UID = "zerosoc", 984
CORE = {"confidence_id": "integer_t", "path": "string_t", "version": "string_t"}
"""OCSF's own dictionary attributes the extension uses as they are."""
CORE_OBJECTS = {"product": "ocsf_product"}
"""OCSF's own objects the extension's attributes hold, and the JSON Schema's definition of each."""
SCALARS = {"string_t": "string", "boolean_t": "boolean", "timestamp_t": "integer", "integer_t": "integer"}
PATCHES = {
    "events/findings/incident_finding.json": "incident_finding",
    "objects/finding_info.json": "finding_info",
    "objects/ticket.json": "ticket",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(node: dict[str, Any], defs: dict[str, Any]) -> dict[str, Any]:
    """The definition a node stands for: what it references, or the one branch of a value that
    may also be null, which OCSF writes by leaving the attribute out."""
    while "$ref" in node:
        node = defs[node["$ref"].split("/")[-1]]
    branches = [b for b in node.get("anyOf") or [] if b.get("type") != "null"]
    return _resolve(branches[0], defs) if len(branches) == 1 else node


def _same(
    name: str,
    schema: dict[str, Any],
    objects: dict[str, Any],
    dictionary: dict[str, Any],
    defs: dict[str, Any],
    where: str,
) -> list[str]:
    """The extension's object `name` declares exactly the properties `schema` declares, typed alike."""
    problems: list[str] = []
    held = objects.get(name)
    if held is None:
        return [f"{where}: the extension declares no object {name!r}"]
    ours, theirs = set(held.get("attributes") or {}), set(schema.get("properties") or {})
    for missing in sorted(theirs - ours):
        problems.append(f"{where}: {missing!r} is in the JSON Schema and not in the extension's {name!r}")
    for extra in sorted(ours - theirs):
        problems.append(f"{where}: {extra!r} is in the extension's {name!r} and not in the JSON Schema")
    for attribute in sorted(ours & theirs):
        here = f"{where}.{attribute}"
        declared = dictionary.get(attribute) or ({"type": CORE[attribute]} if attribute in CORE else None)
        if declared is None:
            problems.append(f"{here}: no dictionary declares it")
            continue
        node = _resolve(schema["properties"][attribute], defs)
        many = node.get("type") == "array"
        if many != bool(declared.get("is_array")):
            problems.append(f"{here}: an array in {'the JSON Schema' if many else 'the extension'} only")
            continue
        node = _resolve(node.get("items") or {}, defs) if many else node
        kind = declared["type"]
        if kind in SCALARS:
            if node.get("type") != SCALARS[kind]:
                problems.append(f"{here}: {kind} in the extension, {node.get('type')!r} in the JSON Schema")
        elif kind in CORE_OBJECTS:
            if node is not defs[CORE_OBJECTS[kind]]:
                problems.append(f"{here}: OCSF {kind} in the extension, not in the JSON Schema")
        else:
            problems += _same(kind, node, objects, dictionary, defs, here)
    return problems


def main() -> int:
    schema = _load(SCHEMA)
    defs = schema["$defs"]
    manifest = _load(EXTENSION / "extension.json")
    dictionary = _load(EXTENSION / "dictionary.json")["attributes"]
    objects = {
        held["name"]: held
        for held in (_load(p) for p in sorted((EXTENSION / "objects").glob("*.json")))
        if "name" in held
    }
    problems: list[str] = []
    if (manifest.get("name"), manifest.get("uid")) != (NAME, UID):
        problems.append(f"extension.json: name and uid are {NAME!r} and {UID}, as OCSF's registry has them")
    for rel, target in PATCHES.items():
        patch = _load(EXTENSION / rel)
        if patch.get("extends") != target or patch.get("name", target) != target:
            problems.append(f"{rel}: a patch of {target!r} extends it and has no other name")
        elif NAME not in (patch.get("attributes") or {}):
            problems.append(f"{rel}: the patch does not add {NAME!r} to {target!r}")
    # the Case, an Observation and a ticket carry one object: the union of what the JSON Schema
    # declares at each, each attribute applying to one of them
    places = {
        "the Case": _resolve(schema["properties"][NAME], defs),
        "an Observation": defs["ocsf_finding_info"]["properties"][NAME],
        "a ticket": defs["ocsf_ticket"]["properties"][NAME],
    }
    union: dict[str, Any] = {}
    for where, node in places.items():
        for attribute, held in node["properties"].items():
            if attribute in union:
                problems.append(f"{where}: {attribute!r} is declared at two places of the JSON Schema")
            union[attribute] = held
    problems += _same(NAME, {"properties": union}, objects, dictionary, defs, NAME)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(f"{len(problems)} difference(s) between the extension and the JSON Schema", file=sys.stderr)
        return 1
    print(f"ocsf extension: ok ({len(union)} zerosoc attributes, {len(objects)} objects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
