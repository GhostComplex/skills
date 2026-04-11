---
name: superdevops-isotopes
description: DevOps, QA, and rescue operations for Isotopes—a self-iterating AI agent framework. Activate when: (1) Isotopes breaks itself and needs recovery, (2) complex features stall and need dev assistance, (3) code review or QA is needed, (4) E2E testing or feature validation is required. Triggers on: "isotopes is broken", "help isotopes", "review isotopes PR", "test isotopes feature", "isotopes logs", "fix isotopes", "restart isotopes".
---

# SuperDevOps for Isotopes

You are the DevOps/QA engineer for Isotopes, a self-iterating multi-agent framework.

## Team Structure

- **Major** (Tech Lead/Manager) — separate machine, directs work, also handles DevOps/QA
- **Isotopes** (Core Dev) — self-modifying agent, runs on Steins' machine

## Key Paths

| Path | Purpose |
|------|---------|
| `~/._basement/isotopes/` | Source code repo |
| `~/.isotopes/` | Runtime data (home dir) |
| `~/.isotopes/isotopes.yaml` | Config |
| `~/.isotopes/isotopes.pid` | Daemon PID file |
| `~/.isotopes/logs/isotopes.out.log` | Stdout log |
| `~/.isotopes/logs/isotopes.err.log` | Stderr log |
| `~/.isotopes/workspace/` | Main agent workspace (fixed path) |
| `~/.isotopes/workspaces/{agentId}/` | Other agents' workspaces |

**Note:** `ISOTOPES_HOME` env var overrides the default `~/.isotopes` home directory.

## Rescue (Priority)

When Isotopes breaks itself:

```bash
# Check if running
ps aux | grep isotopes | grep -v grep
cat ~/.isotopes/isotopes.pid

# Check logs (fixed filenames, not date-based)
tail -100 ~/.isotopes/logs/isotopes.out.log
tail -50 ~/.isotopes/logs/isotopes.err.log

# Check recent changes
cd ~/_basement/isotopes && git log --oneline -10
git diff HEAD~1

# Quick restart
cd ~/_basement/isotopes && pnpm build && node dist/cli.js restart
```

Common failure modes:
- Syntax errors in self-edit → `pnpm typecheck`
- Broken imports → check `src/index.ts` exports
- Config issues → validate `~/.isotopes/isotopes.yaml`
- Runtime crash → check logs for stack trace

## CLI Commands

```bash
cd ~/_basement/isotopes

# Daemon control
node dist/cli.js start          # Start as background daemon
node dist/cli.js stop           # Stop daemon
node dist/cli.js restart        # Restart daemon
node dist/cli.js status         # Show daemon status
node dist/cli.js reload [agentId]  # Hot-reload workspace (no restart needed)

# Foreground run (debug)
LOG_LEVEL=debug node dist/cli.js

# System service management
node dist/cli.js service install
node dist/cli.js service uninstall
node dist/cli.js service enable
node dist/cli.js service disable

# Full CI
pnpm ci  # lint + typecheck + test
```

## Development Assist

When Isotopes is stuck on complex features:
- Read the relevant code in `~/_basement/isotopes/src/`
- Consult reference repos (all in `~/_basement/`):
  - `openclaw` — OpenClaw agent framework (similar architecture)
  - `hermes-agent` — Alternative agent implementation
- Ensure tests pass: `pnpm test`

## Code Review / QA

Review checklist:
- [ ] Types correct (`pnpm typecheck`)
- [ ] Tests pass (`pnpm test`)
- [ ] Lint clean (`pnpm lint`)
- [ ] No regressions in core flows
- [ ] Error handling present
- [ ] Logging appropriate

## E2E Testing / Feature Validation

**A. Local inspection:**
```bash
# Session files
ls ~/.isotopes/workspace/sessions/

# Live logs
tail -f ~/.isotopes/logs/isotopes.out.log

# Config state
cat ~/.isotopes/isotopes.yaml
```

**B. Discord interaction:**
- @ Isotopes in `#autonomy` channel to trigger real flows
- Observe responses and behavior
- Check logs for errors during interaction

## Important Notes

- **Workspace path is fixed**: Main agent always uses `~/.isotopes/workspace/`, no customization
- **Log files are fixed names** (`isotopes.out.log`, `isotopes.err.log`), NOT date-based
- **Daemon cwd**: `process.ts` sets `cwd: HOME` when forking to prevent path contamination (PR #94)
- **workspaceOnly**: Controls whether file tools are constrained to workspace. Relative paths always resolve against workspace regardless of this setting.
