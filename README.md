# Skills

A collection of custom skills for [OpenClaw](https://openclaw.ai) agents.

## Structure

Each skill is a self-contained directory at the repo root:

```
<skill-name>/
├── SKILL.md              # Required — YAML frontmatter + instructions
├── scripts/              # Optional — executable code
├── references/           # Optional — documentation loaded on demand
└── assets/               # Optional — files used in output
```

## Installation

### Option 1: Workspace (per-agent)

Copy or symlink a skill folder into `<workspace>/skills/`:

```bash
cp -r <skill-name> ~/.openclaw/workspace/skills/<skill-name>
```

### Option 2: Shared (all agents)

Copy a skill folder into `~/.openclaw/skills/`:

```bash
cp -r <skill-name> ~/.openclaw/skills/<skill-name>
```

### Option 3: Extra dirs (point at this repo)

Add this repo's path to `skills.load.extraDirs` in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["/path/to/this/repo"]
    }
  }
}
```

OpenClaw picks up new skills on the next session. No gateway restart needed.

## Skills

<!-- Update this table as skills are added -->
| Skill | Description |
|-------|-------------|
| [superboss](./superboss/) | Engineering management for multi-agent software teams |

## License

MIT
