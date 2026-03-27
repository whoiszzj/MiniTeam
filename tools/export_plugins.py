from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
MANIFEST_PATH = SRC_DIR / "agents.json"
SKILLS_DIR = SRC_DIR / "skills"
RULES_DIR = SRC_DIR / "rules"


class ValidationError(RuntimeError):
    pass


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"Missing manifest: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc


def validate_manifest(data: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    package = data.get("package")
    agents = data.get("agents")

    if not isinstance(package, dict):
        raise ValidationError("Manifest must contain a 'package' object.")
    if not isinstance(agents, list) or not agents:
        raise ValidationError("Manifest must contain a non-empty 'agents' array.")

    required_package_fields = ["id", "display_name", "version", "description"]
    missing_package = [field for field in required_package_fields if not package.get(field)]
    if missing_package:
        raise ValidationError(
            f"Package metadata is missing required fields: {', '.join(missing_package)}"
        )

    seen_ids: set[str] = set()
    seen_names: set[str] = set()

    for agent in agents:
        if not isinstance(agent, dict):
            raise ValidationError("Every agent entry must be an object.")

        required_fields = ["id", "name", "model", "description", "readonly", "prompt_file"]
        missing_fields = [field for field in required_fields if field not in agent]
        if missing_fields:
            raise ValidationError(
                f"Agent entry is missing required fields: {', '.join(missing_fields)}"
            )

        agent_id = agent["id"]
        agent_name = agent["name"]
        if agent_id in seen_ids:
            raise ValidationError(f"Duplicate agent id: {agent_id}")
        if agent_name in seen_names:
            raise ValidationError(f"Duplicate agent name: {agent_name}")

        seen_ids.add(agent_id)
        seen_names.add(agent_name)

        prompt_path = resolve_src_path(agent["prompt_file"])
        if not prompt_path.is_file():
            raise ValidationError(f"Prompt file not found for agent '{agent_id}': {prompt_path}")

        claude = agent.get("claude_code")
        if claude is not None:
            if not isinstance(claude, dict):
                raise ValidationError(f"Agent '{agent_id}' claude_code config must be an object.")
            for skill_name in claude.get("skills", []):
                skill_path = SKILLS_DIR / skill_name / "SKILL.md"
                if not skill_path.is_file():
                    raise ValidationError(
                        f"Claude skill '{skill_name}' referenced by '{agent_id}' was not found."
                    )

    return package, agents


def resolve_src_path(relative_path: str) -> Path:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    path = (SRC_DIR / Path(normalized)).resolve()
    if SRC_DIR.resolve() not in path.parents and path != SRC_DIR.resolve():
        raise ValidationError(f"Path escapes src/: {relative_path}")
    return path


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dump_yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or any(ch in text for ch in [":", "#", "[", "]", "{", "}", "\n", '"', "'"]):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def build_frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {dump_yaml_scalar(item)}")
            continue
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for child_key, child_value in value.items():
                lines.append(f"  {child_key}: {dump_yaml_scalar(child_value)}")
            continue
        lines.append(f"{key}: {dump_yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def render_agent_markdown(frontmatter: dict[str, Any], prompt_body: str) -> str:
    body = prompt_body.strip()
    return f"{build_frontmatter(frontmatter)}\n\n{body}\n"


def copy_shared_skills(target_root: Path) -> None:
    if not SKILLS_DIR.is_dir():
        return
    shutil.copytree(SKILLS_DIR, target_root / "skills", dirs_exist_ok=True)


def copy_shared_rules(target_root: Path) -> None:
    if not RULES_DIR.is_dir():
        return
    shutil.copytree(RULES_DIR, target_root / "rules", dirs_exist_ok=True)


def build_optional_metadata(package: dict[str, Any]) -> dict[str, Any]:
    author = package.get("author") or {}
    metadata: dict[str, Any] = {
        "version": package.get("version"),
        "description": package.get("description"),
        "license": package.get("license"),
        "keywords": package.get("keywords") or [],
    }

    if any(author.get(field) for field in ("name", "email", "url")):
        metadata["author"] = {key: value for key, value in author.items() if value}
    if package.get("homepage"):
        metadata["homepage"] = package["homepage"]
    if package.get("repository"):
        metadata["repository"] = package["repository"]
    return metadata


def export_cursor(package: dict[str, Any], agents: list[dict[str, Any]], output_dir: Path) -> None:
    reset_dir(output_dir)
    plugin_root = output_dir / package["id"]
    plugin_root.mkdir(parents=True, exist_ok=True)
    agents_dir = plugin_root / "agents"
    copy_shared_skills(plugin_root)
    copy_shared_rules(plugin_root)

    plugin_manifest: dict[str, Any] = {
        "name": package["display_name"],
        "version": package["version"],
        "description": package["description"],
    }

    author = package.get("author") or {}
    if any(author.get(field) for field in ("name", "email", "url")):
        plugin_manifest["author"] = {key: value for key, value in author.items() if value}

    keywords = package.get("keywords") or []
    if keywords:
        plugin_manifest["keywords"] = keywords

    for agent in agents:
        prompt_body = resolve_src_path(agent["prompt_file"]).read_text(encoding="utf-8").strip()
        frontmatter = {
            "name": agent["name"],
            "model": agent["model"],
            "description": agent["description"],
            "readonly": agent["readonly"],
        }
        target_path = agents_dir / f"{agent['id']}.md"
        write_text(target_path, render_agent_markdown(frontmatter, prompt_body))

    write_json(plugin_root / ".cursor-plugin" / "plugin.json", plugin_manifest)


def export_claude_code(package: dict[str, Any], agents: list[dict[str, Any]], output_dir: Path) -> None:
    plugin_root = output_dir / package["id"]
    reset_dir(plugin_root)
    copy_shared_skills(plugin_root)
    copy_shared_rules(plugin_root)

    manifest = {
        "name": package["id"],
        "agents": "./agents/",
        "skills": "./skills/",
        **build_optional_metadata(package),
    }
    write_json(plugin_root / ".claude-plugin" / "plugin.json", manifest)

    for agent in agents:
        prompt_body = resolve_src_path(agent["prompt_file"]).read_text(encoding="utf-8").strip()
        claude_cfg = agent.get("claude_code", {})
        frontmatter: dict[str, Any] = {
            "description": agent["description"],
        }
        for key in (
            "tools",
            "disallowedTools",
            "model",
            "maxTurns",
            "skills",
            "initialPrompt",
            "memory",
            "effort",
            "background",
            "isolation",
        ):
            if key in claude_cfg:
                frontmatter[key] = claude_cfg[key]

        write_text(
            plugin_root / "agents" / f"{agent['id']}.md",
            render_agent_markdown(frontmatter, prompt_body),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export unified plugin sources into Cursor and Claude Code package layouts."
    )
    parser.add_argument(
        "--target",
        choices=["all", "cursor", "claude-code"],
        default="all",
        help="Export only one target. Defaults to all.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DIST_DIR),
        help="Base output directory. Defaults to ./dist",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()

    manifest = load_manifest(MANIFEST_PATH)
    package, agents = validate_manifest(manifest)

    targets = [args.target] if args.target != "all" else ["cursor", "claude-code"]
    for target in targets:
        if target == "cursor":
            export_cursor(package, agents, output_dir / "cursor")
        elif target == "claude-code":
            export_claude_code(package, agents, output_dir / "claude-code")

    print(f"Exported targets: {', '.join(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
