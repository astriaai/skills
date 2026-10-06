#!/usr/bin/env python3
"""Validate manifests and prove the generated plugin matches its sources."""

import argparse
import hashlib
import json
import re
import runpy
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "astria"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition, message):
    if not condition:
        raise SystemExit(f"validate-plugin: {message}")


def file_map(directory):
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def validate_tool_examples(sources):
    # Offline: schemas come from the bundled shared CLI, not a second tool list.
    core = runpy.run_path(str(ROOT / "bin" / "astria"), run_name="astria_plugin_validation")
    schemas = {tool["name"]: tool["inputSchema"] for tool in core["operation_catalog"]()}
    for source in sources.values():
        for path in source.rglob("*.md"):
            for block in re.findall(r"```json\s*\n(.*?)\n```", path.read_text(encoding="utf-8"), re.DOTALL):
                example = json.loads(block)
                if not isinstance(example, dict) or "tool" not in example:
                    continue
                name = example["tool"]
                require(name in schemas, f"unknown tool in {path}: {name}")
                schema = schemas[name]
                arguments = example["arguments"]
                require(isinstance(arguments, dict), f"non-object arguments in {path}")
                require(not set(arguments) - schema["properties"].keys(), f"unknown arguments in {path}: {name}")
                require(set(schema["required"]) <= arguments.keys(), f"missing arguments in {path}: {name}")
                for key, value in arguments.items():
                    field = schema["properties"][key]
                    valid = {
                        "string": isinstance(value, str),
                        "boolean": isinstance(value, bool),
                        "array": isinstance(value, list) and all(isinstance(item, str) for item in value),
                    }[field["type"]]
                    require(valid, f"invalid {name}.{key} type in {path}")
                    if "enum" in field:
                        require(value in field["enum"], f"invalid {name}.{key} choice in {path}")
                    if field["type"] == "array" and "enum" in field["items"]:
                        require(all(item in field["items"]["enum"] for item in value), f"invalid {name}.{key} choices in {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-version")
    args = parser.parse_args()

    portable = read_json(PLUGIN_ROOT / "plugin.json")
    codex = read_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
    claude = read_json(ROOT / ".claude-plugin" / "plugin.json")
    generated_claude = read_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json")
    claude_marketplace = read_json(ROOT / ".claude-plugin" / "marketplace.json")
    codex_marketplace = read_json(ROOT / ".agents" / "plugins" / "marketplace.json")

    versions = {
        portable["version"],
        codex["version"],
        claude["version"],
        generated_claude["version"],
        claude_marketplace["metadata"]["version"],
        claude_marketplace["plugins"][0]["version"],
    }
    require(len(versions) == 1, f"version mismatch: {sorted(versions)}")
    version = versions.pop()
    require(SEMVER.fullmatch(version), f"invalid semantic version: {version}")
    if args.expected_version:
        require(version == args.expected_version, f"expected {args.expected_version}, found {version}")

    require(portable["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "invalid portable schema")
    require({portable["name"], codex["name"], claude["name"]} == {"astria"}, "plugin names must all be astria")
    require(codex["skills"] == "./skills/", "Codex manifest must load ./skills/")
    interface = portable["extensions"]["com.openai"]["interface"]
    require(interface == codex["interface"], "portable and Codex interface metadata differ")
    require(len(interface["defaultPrompt"]) <= 3, "at most three default prompts are allowed")
    require(all(len(prompt) <= 128 for prompt in interface["defaultPrompt"]), "default prompt exceeds 128 characters")
    for field in ("composerIcon", "logo", "logoDark"):
        require(field in interface, f"interface.{field} is required")
        asset = PLUGIN_ROOT / interface[field].removeprefix("./")
        require(asset.is_file(), f"interface.{field} does not exist: {interface[field]}")
        contents = asset.read_bytes()
        require(contents.startswith(b"\x89PNG\r\n\x1a\n"), f"interface.{field} must be a PNG")
        width, height = struct.unpack(">II", contents[16:24])
        require(width == height, f"interface.{field} must be square, found {width}x{height}")

    marketplace_entry = codex_marketplace["plugins"][0]
    require(codex_marketplace["name"] == "astria", "Codex marketplace name must be astria")
    require(marketplace_entry["name"] == "astria", "Codex marketplace plugin must be astria")
    require(marketplace_entry["source"] == {"source": "local", "path": "./plugins/astria"}, "Codex marketplace source is incorrect")
    require(marketplace_entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "Codex marketplace policy is incorrect")

    sources = {
        Path(entry).name: ROOT / entry
        for entry in claude_marketplace["plugins"][0]["skills"]
    }
    generated = {path.name: path for path in (PLUGIN_ROOT / "skills").iterdir() if path.is_dir()}
    require(sources.keys() == generated.keys(), "generated skill names do not match the source marketplace")
    for name, source in sources.items():
        require(file_map(source) == file_map(generated[name]), f"generated skill differs from source: {name}")

    validate_tool_examples(sources)

    require((ROOT / "bin" / "astria").read_bytes() == (PLUGIN_ROOT / "bin" / "astria").read_bytes(), "generated CLI is stale")
    require((ROOT / "mcp.json").read_bytes() == (PLUGIN_ROOT / "mcp.json").read_bytes(), "generated MCP config is stale")
    mcp = read_json(PLUGIN_ROOT / "mcp.json")
    require(mcp["$schema"] == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "invalid MCP schema")
    require(mcp["mcpServers"] == {"astria": {"type": "streamable-http", "url": "https://api.astria.ai/mcp"}}, "incorrect Astria MCP endpoint")
    require(codex["mcpServers"] == "./.mcp.json", "Codex MCP wiring is missing")
    require(read_json(PLUGIN_ROOT / ".mcp.json") == {"mcpServers": {"astria": {"type": "http", "url": "https://api.astria.ai/mcp"}}}, "incorrect compatibility MCP config")
    require((ROOT / ".mcp.json").read_bytes() == (PLUGIN_ROOT / ".mcp.json").read_bytes(), "Claude and native MCP configs differ")
    require(not (ROOT / "hooks" / "hooks.json").exists(), "CLI login hook must not run in MCP plugins")
    require(not (PLUGIN_ROOT / "hooks").exists(), "OpenAI directory packages cannot contain hooks")
    require(not list(PLUGIN_ROOT.rglob("*.pyc")), "generated plugin contains .pyc files")
    require(not list(PLUGIN_ROOT.rglob("__pycache__")), "generated plugin contains __pycache__")

    print(f"Astria plugin {version} is valid ({len(sources)} skills)")


if __name__ == "__main__":
    main()
