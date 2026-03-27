# MiniTeam

MiniTeam is a source repository for reusable coding agents and shared guidance that can be exported into plugin packages for:

- Cursor
- Claude Code

The repository keeps one canonical source of truth under `src/`, then generates tool-specific plugin layouts under `dist/`.

## Repository layout

```text
src/
  agents.json          # Shared agent metadata
  prompts/             # Agent prompt bodies
  skills/              # Shared skills
  rules/               # Shared rules, currently exported for Cursor and bundled for Claude Code
tools/
  export_plugins.py    # Exporter entrypoint
dist/                  # Generated output (gitignored)
```

## How it works

`src/agents.json` stores the descriptive metadata for each agent:

- `id`
- `name`
- `model`
- `description`
- `readonly`
- `prompt_file`

The actual prompt content lives in `src/prompts/*.md`.

When you run the exporter, it reads the shared source files and builds:

- `dist/cursor/<package-id>/...`
- `dist/claude-code/<package-id>/...`

## Local usage

Export both plugin targets:

```bash
python tools/export_plugins.py
```

Export only one target:

```bash
python tools/export_plugins.py --target cursor
python tools/export_plugins.py --target claude-code
```

Generated output:

- Cursor plugin: `dist/cursor/`
- Claude Code plugin: `dist/claude-code/`

## Install the generated plugins

### Cursor

After export, the Cursor plugin is available under:

```text
dist/cursor/miniteam
```

That folder contains:

- `.cursor-plugin/plugin.json`
- `agents/`
- `skills/`
- `rules/`

You can use this generated plugin folder as the distributable plugin package for Cursor.

### Claude Code

After export, the Claude Code plugin is available under:

```text
dist/claude-code/miniteam
```

That folder contains:

- `.claude-plugin/plugin.json`
- `agents/`
- `skills/`
- `rules/`

You can use this generated plugin folder as the distributable plugin package for Claude Code.

## GitHub Actions and releases

The workflow file is:

```text
.github/workflows/export-plugins.yml
```

It does two things:

1. On normal pushes, it exports the plugins and uploads workflow artifacts for Cursor and Claude Code.
2. On pushes to `master` and on manual workflow runs, it also creates or updates a GitHub Release for the current package version and uploads two zip files:
   - `miniteam-cursor-v<version>.zip`
   - `miniteam-claude-code-v<version>.zip`
   - each zip contains the plugin root folder `miniteam/`, ready to install or distribute

Example release flow:

```bash
git push origin master
```

The release version comes from `src/agents.json`.
For example, if `src/agents.json` says `"version": "0.1.0"`, the workflow publishes release assets named:

```text
miniteam-cursor-v0.1.0.zip
miniteam-claude-code-v0.1.0.zip
```

You do not need to create a git tag manually. The workflow handles the GitHub Release versioning from the package metadata.

## How to update the package

1. Edit agent metadata in `src/agents.json`.
2. Edit prompt bodies in `src/prompts/`.
3. Edit shared skills in `src/skills/`.
4. Edit shared rules in `src/rules/`.
5. Run `python tools/export_plugins.py`.
6. Commit the source changes.
7. Push to `master`, or run the workflow manually, when you want the release assets refreshed.

## How to use the release packages

1. Open the repository Releases page on GitHub.
2. Download either `miniteam-cursor-v<version>.zip` or `miniteam-claude-code-v<version>.zip`.
3. Unzip the archive.
4. Use the extracted `miniteam/` folder as the plugin package for the target tool.

## Notes

- `dist/` is generated output and is ignored by git.
- Cursor and Claude Code do not consume exactly the same plugin model, so the exporter maps the shared source into each tool's expected layout.
- Codex export was intentionally removed because its plugin, custom agent, and rules systems differ too much from the Cursor/Claude source model in this repository.
