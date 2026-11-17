# Plugin packaging for ChatGPT and Codex

Official references were reviewed on **2026-11-17**. Check the target importer's contract before building each release.

| Format | Manifest | Skill location | Display metadata |
|---|---|---|---|
| Agent Plugins, the recommended portable format for new packages | Root-level `plugin.json` with the format version's `$schema` | Discovered under `skills/<name>/SKILL.md` | `extensions.com.openai.interface` |
| Codex compatibility format, used in v0.1.2 | `.codex-plugin/plugin.json` | `skills: "./skills/"` points to the directory containing the Skills | `interface` at the manifest root |

The v0.1.2 package uses the same compatibility layout as Cortex AI Skills and Language Teacher. The **New Plugin** dialog recognized the v0.1.1 manifest path and reported that `interface.longDescription` was missing.

## Compatibility manifest checks

| Field | Project check |
|---|---|
| `name`, `version`, `description` | Technical identifier, release version, and a non-empty description |
| `author.name` | Non-empty author name matching the author identity used by Language Teacher |
| `interface.displayName`, `shortDescription`, `longDescription`, `developerName` | Non-whitespace text. The long description can contain line breaks and has a 4,000-character limit. |
| `interface.category`, `capabilities` | Recognized category and capability list within documented limits |
| `interface.logo`, `composerIcon` | Relative paths to files in the ZIP. This project uses the same square PNG for both fields. |
| `interface.defaultPrompt` | Optional. Up to three suggestions, each on a single line. |

Each Skill has its own directory and an `SKILL.md` file with YAML frontmatter containing `name` and `description`. The packager includes the manifest, icon, and Skill runtime files.

## Distribution checks

1. Check the required fields and limits for the target surface. The current display name exceeds 30 characters and fits the package validation limit. Shorten it before a public directory submission.
2. Check that each path referenced in the manifest exists in the ZIP. Use square icons of at least 48 px. The documented PNG limits are 4,096 px and 5 MiB.
3. Run `python3 tests/test_plugin_package.py -v` and `python3 tools/package.py --plugin --version 0.1.2` to check the manifest and assets.
4. Confirm import, installation, and `@` selection in the authorized host. Record that outcome separately from local validation.

This package contains one Skill. Server, app, credential, and MCP review fields apply to packages with those integrations.

- [Plugin structure, compatibility, and paths](https://developers.openai.com/plugins/build/plugins)
- [Manifest fields and submission requirements](https://developers.openai.com/plugins/deploy/submission#manifest-fields)
- [Validation errors and limits](https://developers.openai.com/plugins/deploy/submission-errors)
