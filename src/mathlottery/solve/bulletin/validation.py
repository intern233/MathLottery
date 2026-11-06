"""Stdlib preflight for the schemas copied to native workspaces.

This catches common envelope mistakes before queueing. The controller's Pydantic
models and live dependency/identity checks remain authoritative.
"""

import re


def errors(value, schema):
    def check(item, rule, path):
        if "$ref" in rule:
            target = schema
            for key in rule["$ref"].removeprefix("#/").split("/"):
                target = target[key]
            return check(item, target, path)
        if "anyOf" in rule:
            choices = [check(item, option, path) for option in rule["anyOf"]]
            return [] if any(not result for result in choices) else [f"{path}: does not match an allowed type"]
        kind = rule.get("type")
        valid = {"object": isinstance(item, dict), "array": isinstance(item, list),
                 "string": isinstance(item, str), "integer": type(item) is int,
                 "number": type(item) in {int, float}, "boolean": type(item) is bool,
                 "null": item is None}
        if kind in valid and not valid[kind]:
            return [f"{path}: expected {kind}"]
        result = []
        if "enum" in rule and item not in rule["enum"]:
            result.append(f"{path}: choose one of {rule['enum']}")
        if "const" in rule and item != rule["const"]:
            result.append(f"{path}: expected {rule['const']}")
        if kind == "object":
            fields = rule.get("properties", {})
            result += [f"{path}.{key}: required" for key in rule.get("required", []) if key not in item]
            if rule.get("additionalProperties") is False:
                result += [f"{path}.{key}: unknown field" for key in item if key not in fields]
            for key, content in item.items():
                if key in fields:
                    result.extend(check(content, fields[key], f"{path}.{key}"))
        elif kind == "array":
            if not rule.get("minItems", 0) <= len(item) <= rule.get("maxItems", float("inf")):
                result.append(f"{path}: invalid number of items")
            for index, content in enumerate(item):
                result.extend(check(content, rule.get("items", {}), f"{path}[{index}]"))
        elif kind == "string":
            if not rule.get("minLength", 0) <= len(item) <= rule.get("maxLength", float("inf")):
                result.append(f"{path}: invalid string length")
            if "pattern" in rule and not re.search(rule["pattern"], item):
                result.append(f"{path}: invalid format")
        elif kind in {"integer", "number"}:
            if not rule.get("minimum", float("-inf")) <= item <= rule.get("maximum", float("inf")):
                result.append(f"{path}: outside allowed range")
        return result

    return check(value, schema, "input")
