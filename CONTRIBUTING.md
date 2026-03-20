# Contributing

## Adding a skill

1. Fork & clone this repo
2. Create a branch: `git checkout -b feat/add-<skill-name>`
3. Add your skill directory at the repo root:
   ```
   my-skill/
   ├── SKILL.md
   └── references/       # optional
   ```
4. Ensure `SKILL.md` has valid YAML frontmatter:
   ```yaml
   ---
   name: my-skill
   description: What this skill does and when to activate it.
   ---
   ```
5. Review for privacy — no personal names, IDs, API keys, or internal URLs
6. Open a PR against `main`

## Skill guidelines

- **Concise over verbose** — the context window is shared; only include what the model doesn't already know
- **No extra docs** — no README.md, CHANGELOG.md, or INSTALLATION_GUIDE.md inside skill folders
- **Use references/ for detail** — keep `SKILL.md` lean (<500 lines), split detailed content into `references/`
- **Use scripts/ for reliability** — if the same code gets rewritten every time, make it a script
- **Test scripts** — any added scripts must be verified to work before submitting
