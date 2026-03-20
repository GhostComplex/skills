# Skills

A collection of [AgentSkills](https://agentskills.io)-compatible skills for [OpenClaw](https://openclaw.ai) agents.

## Structure

Each skill is a self-contained directory with a `SKILL.md` and optional resources:

```
skill-name/
├── SKILL.md              # Required — frontmatter + instructions
├── scripts/              # Optional — executable code
├── references/           # Optional — documentation loaded on demand
└── assets/               # Optional — files used in output
```

## Usage

### Workspace install (per-agent)

Copy or symlink a skill folder into your agent's `<workspace>/skills/` directory. OpenClaw picks it up automatically.

### Shared install (all agents)

Copy a skill folder into `~/.openclaw/skills/`. Visible to all agents on the machine.

### Extra dirs

Add paths to `skills.load.extraDirs` in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["/path/to/this/repo"]
    }
  }
}
```

## Contributing

1. Create a new branch from `main`
2. Add your skill directory following the structure above
3. Ensure `SKILL.md` has valid YAML frontmatter with `name` and `description`
4. Open a PR for review

## License

MIT
