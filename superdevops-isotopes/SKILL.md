---
name: superdevops-isotopes
description: "DevOps, QA, and rescue operations for Isotopes—a self-iterating AI agent framework. Activate when: (1) Isotopes breaks itself and needs recovery, (2) complex features stall and need dev assistance, (3) code review or QA is needed, (4) E2E testing or feature validation is required. Triggers on: 'isotopes is broken', 'help isotopes', 'review isotopes PR', 'test isotopes feature', 'isotopes logs', 'fix isotopes', 'restart isotopes'."
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

**Always use debug mode** — set `LOG_LEVEL=debug` for all daemon starts to get full debug payload logging.

```bash
cd ~/_basement/isotopes

# Daemon control (always with debug)
LOG_LEVEL=debug node dist/cli.js start    # Start as background daemon
node dist/cli.js stop                      # Stop daemon
LOG_LEVEL=debug node dist/cli.js restart   # Restart daemon
node dist/cli.js status                    # Show daemon status
node dist/cli.js reload [agentId]          # Hot-reload workspace (no restart needed)

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
  - `pi-mono` — Underlying agent SDK (pi-agent-core, pi-coding-agent, pi-ai, pi-tui)
  - `hermes-agent` — Alternative agent implementation
  - `nanobot` — Lightweight Python agent reference
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

## Project Management

### Two-Layer Management System

**Layer 1: GitHub Project Board** (human-facing)
- **Project:** `isotopes` (#11) in GhostComplex org
- **Board URL:** https://github.com/orgs/GhostComplex/projects/11
- **Status columns:** Backlog → Ready → In progress → In review (PR open) → Done (merged) → [HumanOnly] Archive (Steins verified)
- Issues = lightweight PRDs: describe what and why, acceptance criteria
- Must be **absolutely correct and real-time** — Steins checks frequently
- **Proactively notify** Steins when items are created, started, or completed
- **Steins** moves items from Backlog → Ready to approve
- Agents pick from **Ready** by priority order

**Layer 2: Repo Docs** (agent-facing)
- `docs/wip/` = active design docs, `docs/archive/` = completed
- Complex context persistence for agent-to-agent communication
- **Once development starts**, create/update the design doc **strictly and in real-time**
- Stale docs are worse than no docs

### Workflow
1. All development work **must** have a corresponding GitHub Issue
2. Issues start in **Backlog** — notify Steins when created
3. **Steins** moves to **Ready** when approved
4. Agent picks from **Ready** by priority → moves to **In progress** → creates design doc in `docs/wip/`
5. PR opened → moves to **In review**
6. PR merged → moves to **Done** → design doc to `docs/archive/` if complete. **Done = agent's work is finished.** Move on to next Ready item.
7. **[HumanOnly] Archive** — only Steins moves items here after verification. Agents **NEVER** touch this column. Not a blocker.

### Self-Iteration Loop
When Fairy uses `iterate_codebase`:
1. Check **Ready** column for approved work items
2. Pick highest priority item
3. Create/update design doc in `docs/wip/`
4. Execute via subagent → creates branch + PR
5. Report result back to channel

### Adding Issues to Project
```bash
gh issue create --title "feat: ..." --label "enhancement" --body "..."
gh project item-add 11 --owner GhostComplex --url "https://github.com/GhostComplex/isotopes/issues/N"
```

## Important Notes

- **Workspace path is fixed**: Main agent always uses `~/.isotopes/workspace/`, no customization
- **Log files are fixed names** (`isotopes.out.log`, `isotopes.err.log`), NOT date-based
- **Daemon cwd**: `process.ts` sets `cwd: HOME` when forking to prevent path contamination (PR #94)
- **workspaceOnly**: Controls whether file tools are constrained to workspace. Relative paths always resolve against workspace regardless of this setting.
- **Post-merge reset routine**: After merging any feature PR, Major must immediately: (1) `cd ~/_basement/isotopes && git checkout main && git pull origin main`, (2) `npm run build`, (3) kill + restart in debug mode: `kill $(cat ~/.isotopes/isotopes.pid); LOG_LEVEL=debug nohup node dist/cli.js > ~/.isotopes/logs/isotopes.log 2>&1 & echo $! > ~/.isotopes/isotopes.pid`. This keeps Fairy running on latest main and ready for next task.
- **GitHub Project as single source of truth**: All planned work lives in the GitHub Project board. No separate BACKLOG.md or ad-hoc issue tracking. When identifying new work, create an Issue and add it to the project.

## Development Workflow Rules

### Branch Hygiene
- **Clean branch before new work.** When starting a new task or rewriting a PR, ALWAYS: (1) checkout main, (2) pull latest, (3) create a fresh branch. Never build on top of a closed/rejected PR's branch.
- **Reset rejected code.** When a PR is closed without merge, `git reset --hard origin/main` before starting over. Don't leave rejected code in the working tree — subagents will build on top of it and produce garbage.
- **Verify Fairy's branch before she codes.** When Fairy starts work, verify she: (1) is on the correct branch, (2) has a clean working tree, (3) based on latest main. If not, intervene immediately — don't wait until the PR to discover she built on stale/rejected code.
- **Subagent ≠ fire-and-forget.** After Fairy spawns a subagent, check the repo state (branch, working tree) within a few minutes. Mid-run course corrections are cheap; post-run rewrites are expensive.

### Session Corruption Recovery
- Compaction can corrupt sessions by removing `tool_use` blocks while keeping orphaned `tool_result` blocks → 400 errors from the API.
- **Fix:** Kill Isotopes process, delete the corrupted `.jsonl` session file under `~/.isotopes/workspace/sessions/`, remove the entry from `sessions.json`, then restart. Check ALL session files with `grep` for the bad `tool_use_id`, not just the obvious one.

### Runtime Bug Priority
- **400 errors, crashes, and obvious runtime bugs are P0** — drop everything and fix immediately.
- When a bug surfaces in the channel (e.g. Fairy spitting 400 errors):
  1. Check logs immediately: `tail -50 ~/.isotopes/logs/isotopes.log`
  2. Identify root cause (not just symptoms)
  3. Fix it — either session cleanup, code fix, or config change
  4. If it's a code bug, open a PR with the fix
  5. Don't resume feature work until the bug is resolved

### Config Wire-Through Audit
When reviewing PRs that add or modify config fields:
1. `grep` the field name across the entire codebase — find ALL consumers
2. Verify the value is passed from config parsing → every runtime consumer
3. If a config field only reaches some consumers but should affect all, that's a bug
4. After merging config-related fixes, run an E2E smoke test (not just tsc/unit tests)
5. Example: `allowedWorkspaces` was parsed and passed to subagent tool but NOT to file tools — caught late because we only verified the code logic, never tested Fairy actually reading an allowed path
