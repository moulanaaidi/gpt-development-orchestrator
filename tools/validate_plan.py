#!/usr/bin/env python3
"""Validate an orchestrator plan using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


PLAN_FIELDS = {"schema_version", "plan", "model_registry", "tasks"}
METADATA_FIELDS = {"id", "title", "objective", "status"}
TASK_FIELDS = {
    "id",
    "title",
    "readiness",
    "role",
    "model",
    "dependencies",
    "write_set",
    "mutates",
    "acceptance_criteria",
    "validation_commands",
    "risk",
    "parallel_group",
}
PLAN_STATUSES = {"draft", "ready", "in_progress", "blocked", "complete"}
RISKS = {"low", "medium", "high", "critical"}
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r} is not allowed")


def load_plan(path: Path) -> tuple[Any | None, list[str]]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            value = json.load(
                stream,
                object_pairs_hook=_object_without_duplicate_keys,
                parse_constant=_reject_non_json_constant,
            )
    except FileNotFoundError:
        return None, [f"$: file not found: {path}"]
    except UnicodeDecodeError as exc:
        return None, [f"$: file is not valid UTF-8: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"$: malformed JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"]
    except (DuplicateKeyError, ValueError) as exc:
        return None, [f"$: {exc}"]
    except OSError as exc:
        return None, [f"$: could not read file: {exc}"]
    return value, []


def _check_object(
    value: Any, path: str, required: set[str], allowed: set[str], errors: list[str]
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected an object")
        return False
    for field in sorted(required - value.keys()):
        errors.append(f"{path}.{field}: required field is missing")
    for field in sorted(value.keys() - allowed):
        errors.append(f"{path}.{field}: unknown field")
    return True


def _non_empty_string(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected a non-empty string")
        return False
    return True


def _string_list(value: Any, path: str, errors: list[str], *, non_empty: bool = False) -> bool:
    if not isinstance(value, list):
        errors.append(f"{path}: expected an array of strings")
        return False
    if non_empty and not value:
        errors.append(f"{path}: must contain at least one item")
    valid = True
    for index, item in enumerate(value):
        valid = _non_empty_string(item, f"{path}[{index}]", errors) and valid
    return valid


def _repo_scope(value: str) -> str | None:
    """Normalize a repo-relative scope; a terminal '/**' owns a directory tree."""
    candidate = value.replace("\\", "/")
    if candidate.endswith("/**"):
        candidate = candidate[:-3]
    if any(character in candidate for character in "*?[]"):
        return None
    if candidate.startswith("/") or re.match(r"^[A-Za-z]:", candidate):
        return None
    parts = candidate.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    if "\x00" in candidate:
        return None
    return str(PurePosixPath(*parts)).casefold()


def _scopes_overlap(first: str, second: str) -> bool:
    return first == second or first.startswith(second + "/") or second.startswith(first + "/")


def _validate_metadata(metadata: Any, errors: list[str]) -> None:
    path = "$.plan"
    if not _check_object(metadata, path, METADATA_FIELDS, METADATA_FIELDS, errors):
        return
    for field in ("id", "title", "objective"):
        if field in metadata:
            _non_empty_string(metadata[field], f"{path}.{field}", errors)
    if "status" in metadata and (
        not isinstance(metadata["status"], str) or metadata["status"] not in PLAN_STATUSES
    ):
        errors.append(f"{path}.status: expected one of {', '.join(sorted(PLAN_STATUSES))}")


def _validate_registry(registry: Any, errors: list[str]) -> dict[str, set[str]]:
    path = "$.model_registry"
    if not isinstance(registry, dict):
        errors.append(f"{path}: expected an object mapping roles to model arrays")
        return {}
    if not registry:
        errors.append(f"{path}: must declare at least one role")
    result: dict[str, set[str]] = {}
    for role, models in registry.items():
        role_path = f"{path}.{role}"
        if not IDENTIFIER.fullmatch(role):
            errors.append(f"{path}: role name {role!r} must match {IDENTIFIER.pattern}")
        if not isinstance(models, list):
            errors.append(f"{role_path}: expected an array of model identifiers")
            continue
        if not models:
            errors.append(f"{role_path}: must declare at least one model")
        result[role] = set()
        for index, model in enumerate(models):
            if _non_empty_string(model, f"{role_path}[{index}]", errors):
                if model in result[role]:
                    errors.append(f"{role_path}[{index}]: duplicate model {model!r}")
                result[role].add(model)
    return result


def _validate_tasks(tasks: Any, registry: dict[str, set[str]], errors: list[str]) -> None:
    if not isinstance(tasks, list):
        errors.append("$.tasks: expected an array")
        return
    if not tasks:
        errors.append("$.tasks: must contain at least one task")

    task_ids: dict[str, int] = {}
    task_values: list[dict[str, Any]] = []
    for index, task in enumerate(tasks):
        path = f"$.tasks[{index}]"
        if not _check_object(task, path, TASK_FIELDS - {"parallel_group"}, TASK_FIELDS, errors):
            task_values.append({})
            continue
        task_values.append(task)

        for field in ("id", "title", "role", "model"):
            if field in task and _non_empty_string(task[field], f"{path}.{field}", errors):
                if field == "id":
                    task_id = task[field]
                    if task_id in task_ids:
                        errors.append(
                            f"{path}.id: duplicate task ID {task_id!r}; first declared at $.tasks[{task_ids[task_id]}].id"
                        )
                    else:
                        task_ids[task_id] = index

        if "readiness" in task and (
            not isinstance(task["readiness"], str) or task["readiness"] not in PLAN_STATUSES
        ):
            errors.append(f"{path}.readiness: expected one of {', '.join(sorted(PLAN_STATUSES))}")
        if "risk" in task and (
            not isinstance(task["risk"], str) or task["risk"] not in RISKS
        ):
            errors.append(f"{path}.risk: expected one of {', '.join(sorted(RISKS))}")

        role = task.get("role")
        model = task.get("model")
        if isinstance(role, str) and isinstance(model, str):
            if role not in registry:
                errors.append(f"{path}.role: undeclared role {role!r} in $.model_registry")
            elif model not in registry[role]:
                errors.append(f"{path}.model: model {model!r} is not declared for role {role!r}")

        dependencies = task.get("dependencies")
        if _string_list(dependencies, f"{path}.dependencies", errors):
            seen_dependencies: set[str] = set()
            for dep_index, dependency in enumerate(dependencies):
                if dependency in seen_dependencies:
                    errors.append(f"{path}.dependencies[{dep_index}]: duplicate dependency {dependency!r}")
                seen_dependencies.add(dependency)

        write_set = task.get("write_set")
        if _string_list(write_set, f"{path}.write_set", errors):
            normalized_scopes: set[str] = set()
            for scope_index, scope in enumerate(write_set):
                normalized = _repo_scope(scope)
                if normalized is None:
                    errors.append(
                        f"{path}.write_set[{scope_index}]: expected a repository-relative path without '.' or '..' segments; only a terminal '/**' wildcard is allowed"
                    )
                elif normalized in normalized_scopes:
                    errors.append(f"{path}.write_set[{scope_index}]: duplicate path scope {scope!r}")
                else:
                    normalized_scopes.add(normalized)

        if "mutates" in task and not isinstance(task["mutates"], bool):
            errors.append(f"{path}.mutates: expected a boolean")
        elif task.get("mutates") is True and isinstance(write_set, list) and not write_set:
            errors.append(f"{path}.write_set: mutating tasks must declare at least one path scope")

        if "acceptance_criteria" in task:
            _string_list(task["acceptance_criteria"], f"{path}.acceptance_criteria", errors, non_empty=True)
        if "validation_commands" in task:
            _string_list(task["validation_commands"], f"{path}.validation_commands", errors)
            if task.get("mutates") is True and isinstance(task["validation_commands"], list) and not task["validation_commands"]:
                errors.append(f"{path}.validation_commands: mutating tasks must declare at least one validation command")

        if "parallel_group" in task:
            group = task["parallel_group"]
            if group is not None:
                _non_empty_string(group, f"{path}.parallel_group", errors)

    declared_ids = set(task_ids)
    for index, task in enumerate(task_values):
        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list):
            continue
        for dep_index, dependency in enumerate(dependencies):
            if isinstance(dependency, str) and dependency not in declared_ids:
                errors.append(f"$.tasks[{index}].dependencies[{dep_index}]: undeclared task ID {dependency!r}")

    _validate_dependency_cycles(task_values, task_ids, errors)
    _validate_parallel_scopes(task_values, errors)


def _validate_dependency_cycles(
    tasks: list[dict[str, Any]], task_ids: dict[str, int], errors: list[str]
) -> None:
    graph: dict[str, list[str]] = {}
    for task_id, index in task_ids.items():
        deps = tasks[index].get("dependencies", [])
        graph[task_id] = [dep for dep in deps if isinstance(dep, str) and dep in task_ids]

    state: dict[str, int] = {}
    stack: list[str] = []
    reported: set[tuple[str, ...]] = set()

    def visit(task_id: str) -> None:
        state[task_id] = 1
        stack.append(task_id)
        for dependency in graph.get(task_id, []):
            if state.get(dependency, 0) == 0:
                visit(dependency)
            elif state.get(dependency) == 1:
                cycle_start = stack.index(dependency)
                cycle = tuple(stack[cycle_start:] + [dependency])
                if cycle not in reported:
                    errors.append("$.tasks: dependency cycle: " + " -> ".join(cycle))
                    reported.add(cycle)
        stack.pop()
        state[task_id] = 2

    for task_id in graph:
        if state.get(task_id, 0) == 0:
            visit(task_id)


def _validate_parallel_scopes(tasks: list[dict[str, Any]], errors: list[str]) -> None:
    groups: dict[str, list[tuple[int, str, str]]] = {}
    for index, task in enumerate(tasks):
        group = task.get("parallel_group")
        scopes = task.get("write_set")
        task_id = task.get("id", f"index-{index}")
        if not isinstance(group, str) or not isinstance(scopes, list):
            continue
        for scope in scopes:
            if isinstance(scope, str):
                normalized = _repo_scope(scope)
                if normalized is not None:
                    groups.setdefault(group, []).append((index, str(task_id), normalized))

    for group, entries in groups.items():
        for position, (first_index, first_id, first_scope) in enumerate(entries):
            for second_index, second_id, second_scope in entries[position + 1 :]:
                if first_index != second_index and _scopes_overlap(first_scope, second_scope):
                    errors.append(
                        f"$.tasks[{second_index}].write_set: overlaps task {first_id!r} in parallel group {group!r} ({first_scope!r})"
                    )


def validate_plan(value: Any) -> list[str]:
    errors: list[str] = []
    if not _check_object(value, "$", PLAN_FIELDS, PLAN_FIELDS, errors):
        return errors

    if "schema_version" in value and value["schema_version"] != "1.0":
        errors.append("$.schema_version: expected '1.0'")
    if "plan" in value:
        _validate_metadata(value["plan"], errors)
    registry = _validate_registry(value.get("model_registry"), errors) if "model_registry" in value else {}
    if "tasks" in value:
        _validate_tasks(value["tasks"], registry, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="path to a JSON plan document")
    args = parser.parse_args(argv)

    value, errors = load_plan(args.plan)
    if not errors:
        errors = validate_plan(value)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Valid plan: {args.plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
