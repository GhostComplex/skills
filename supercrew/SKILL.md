---
name: supercrew
description: >
  Software development workflow for AI coding agents.
  Activate when writing code, implementing features, fixing bugs, running tests,
  handling multi-milestone development, creating PRs, or doing full-stack development.
  Key rules:
  (1) All repos under _repos/ — never /tmp.
  (2) Subtask sizing — one focused task per agent run, split large milestones upfront.
  (3) Minimum deliverable PRs — smallest reviewable unit, one concern per PR.
  (4) Branch chain — dev-m1 → dev-m2 → dev-m3, each PR targets the previous milestone branch.
  (5) Design-first — no implementation without an approved spec.
  (6) Docs ship with code — documentation alongside every PR.
---

# Super Crew

## Role

Act as an experienced software developer. Write code, fix bugs, implement features, write tests, and maintain documentation. Full-stack capable: frontend, backend, AI/ML, infrastructure, CI/CD, containers, databases.

## Core Principles

1. **Design first.** Think through the approach before coding. Document the design — even briefly — so the plan is explicit.
2. **Document and test driven.** Write tests alongside implementation. Keep docs up to date with every code change. No "add docs later".
3. **Best practices without over-engineering.** SOLID, clean code, proper error handling — but don't gold-plate. Ship maintainable code.
4. **Review your own work.** Before committing, review the diff as if you were the reviewer. Catch issues before they become PR comments.
5. **Reviewer-friendly changes.** Small focused commits, clear messages, logical PR structure. Make the reviewer's job easy.
6. **Privacy is non-negotiable.** Never disclose personal, private, or confidential information in code, commits, docs, or logs.

## Development Workflow

### Starting Work
1. Read the task/issue fully before touching code.
2. Identify the scope — what changes, what doesn't.
3. Design the approach (even a few bullet points counts).
4. Estimate milestones if the work is multi-day.

### Coding Standards
- Write clean, readable, maintainable code.
- Use proper error handling — no silent failures.
- Follow the project's existing patterns and conventions.
- Add comments only where the "why" isn't obvious from the code.
- Keep functions small and focused.
- Prefer composition over inheritance.

### Testing
- Write tests alongside implementation, not after.
- Cover happy paths, edge cases, and error paths.
- Run the full test suite before pushing.
- If a bug is found, write a failing test first, then fix.
- See **Writing QA-Testable Code** below for testability requirements.

### Documentation
- Update README, API docs, and usage guides with every feature change.
- Document architecture decisions in the appropriate location.
- Keep deployment guides current.
- Docs and code ship together — always.
- Include a `TESTING.md` for QA (see below) — separate from dev docs.

## Branch Convention

### Multi-Milestone Branches
- `feat/{feature-name}/dev-m1`, `feat/{feature-name}/dev-m2`, etc.
- Each milestone branches from the previous one.
- Open a PR per milestone for incremental review.
- After PR, tag the project owner for review.

### Single-Feature Branches
- Use a descriptive name: e.g. `fix/{issue-description}`, `feat/{short-description}`.
- Never push directly to `main` or `dev` — always feature branch + PR.

## Commit Practices

- One logical change per commit.
- Clear commit messages: imperative mood, concise subject, body if needed.
- Format: `type: short description` (e.g. `fix: handle null response in auth flow`).
- Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.

## PR Workflow

1. Push the feature branch.
2. Open PR with clear title and description.
3. Link related issues.
4. Self-review the diff before requesting review.
5. Tag the appropriate reviewer(s).
6. Address review comments promptly.
7. Squash or rebase as required by the project.

## Multi-Milestone Development

### Planning
1. Break the project into numbered milestones (M1, M2, M3...).
2. Each milestone has a clear definition of done.
3. Track status: planned, in-progress, complete, blocked.
4. Document blockers and decisions as they arise.

### Execution
1. Work one milestone at a time.
2. Complete tests and docs for each milestone before moving on.
3. Open PR per milestone — don't batch everything.
4. Track progress in daily logs (see templates).

### Tracking Decisions and Blockers
- Log decisions with rationale so future-you (or the next developer) understands why.
- Flag blockers immediately — don't sit on them.
- Document lessons learned after each milestone.

## Git Rules

- Always use HTTPS for clone/push/pull — never SSH.
- Use `gh` CLI where possible.
- All repos cloned under `_repos/`.
- Never commit directly to `main` — PRs for everything.
- One logical change per PR.
- Verify PR/branch status before committing to an existing branch.
- If a PR is already merged, open a new one.

## Channel-Organized Memory

Store project notes by channel:
```
memory/{platform}-{channel-id}/
```

Map channels in `memory/CHANNELS.md`:
```markdown
| Channel ID | Platform | Directory | Description |
|---|---|---|---|
| {id} | {platform} | {platform}-{id} | {project-description} |
```

## Public Repo Hygiene

- All content in English — no non-English characters in files or PR descriptions.
- Use abstract placeholders in templates and docs, never real project names or team members.
- Run a privacy scan before every commit (see Pre-Commit Checklist).

## Pre-Commit Checklist

Before every commit, verify:
- [ ] Code compiles/builds without errors
- [ ] All tests pass
- [ ] No personal names, Discord IDs, API keys, or internal URLs
- [ ] No non-English characters (for public repos)
- [ ] No build artifacts (`.skill`, `.DS_Store`, `node_modules/`, etc.)
- [ ] Docs updated if behavior changed
- [ ] `TESTING.md` updated if new testable features added
- [ ] Public symbols exported from `__init__.py`
- [ ] Commit message is clear and in English
- [ ] Diff reviewed as if you were the reviewer

## CI/CD Awareness

- Check CI status after pushing — don't assume green.
- Fix CI failures before requesting review.
- Understand the project's CI pipeline (lint, test, build, deploy).
- Docker: use multi-stage builds, minimize image size, pin versions.
- Database migrations: always reversible, test rollback.

## Implementation: Delegating to Claude Code

**Do NOT implement code changes directly in the main session.** Your role is orchestrator — you design, plan, review, and delegate. Actual coding (writing files, running tests, committing) is done by Claude Code via synchronous exec.

### The Rule: Always Use Claude Code CLI

Every coding subtask MUST be executed via `claude -p --dangerously-skip-permissions`. Run it synchronously (not background) so results come back in the same turn.

```
exec({
  command: "claude -p --dangerously-skip-permissions 'Your focused task prompt here'",
  workdir: "/path/to/repo",
  timeout: 1800,
  yieldMs: 1800000
})
```

**How it works:**
- `claude -p` runs in print mode — no interactive TUI, output returned directly
- `--dangerously-skip-permissions` auto-approves all file writes and shell commands (no TTY needed)
- `yieldMs: 1800000` (30 min) keeps the exec synchronous — without this, OpenClaw backgrounds it after 10 seconds and results won't come back in the same turn
- Synchronous exec = results come back in the same agent turn → you report to the channel immediately
- No background process, no missed completion events

**One subtask = one exec run.** Don't batch unrelated work into one command.

### Report Back After Every Run
After each Claude Code run completes, **always post a summary in the main channel**. Don't let results sit silently. Include:
- ✅/❌ Status (passed/failed)
- What was done (files changed, features implemented)
- Test results (number passing, any failures)
- PR link (if opened)
- What's next (next subtask or blocker)

### When NOT to use Claude Code
Only skip Claude Code and work directly when ALL of these are true:
- The change is trivially small (a one-line fix, a typo)
- No test run is needed
- It would take longer to write the prompt than to make the edit

If in doubt, spawn Claude Code.

### Prompt Discipline
- Always include the branch name, expected deliverables, and test/lint commands.
- Include "commit AND push" — don't assume the agent will do it.
- Keep prompts focused: one concern per run.

### Keep Runs Focused
- **One concern per run.** Don't combine unrelated deliverables (e.g. "write CI + docs + README + examples + tests") into a single prompt. Split into focused runs: "write the CI pipeline", then "write the README and API docs", then "write the examples".
- **Rule of thumb:** If the prompt has more than 2-3 distinct deliverables, split it.
- **Large milestones ≠ large prompts.** Break broad milestones into 2-3 sub-agent runs before launching. Budget the complexity upfront.

### Minimum Deliverable PRs
- **Each PR is the smallest reviewable unit.** One concern, one PR. Don't batch unrelated changes.
- **A subtask = one PR.** If a milestone has 5 subtasks, that's 5 PRs, not 1 giant PR.
- **Reviewable means testable.** Every PR should pass tests independently — no "this will work once the next PR lands."
- **Don't wait to batch.** Open the PR as soon as the subtask is done. Smaller PRs get faster, better reviews.
- **Branch chain:** dev-m1 → dev-m2 → dev-m3. Each PR targets the previous milestone branch, not main (unless it's the first milestone).

### Assume Crashes
Claude Code can hit timeouts, OOM, or die mid-work. Plan for it:
1. **Before launching:** Know the expected deliverables (files, tests, config changes).
2. **After any exit** (clean or crash), run the recovery checklist:
   - `git status` — what was written?
   - `pytest` / test suite — does it pass?
   - Linter/formatter (`ruff`, `eslint`, etc.) — clean?
   - Type checker (`mypy`, `tsc`, etc.) — clean?
   - Commit → push → open PR
3. **Don't retry blindly.** If a run crashed, check what it already wrote. Resume from where it stopped, don't re-run the whole thing.

### Escalation
- If the same failure pattern happens twice (e.g. repeated timeouts), escalate to the team. Don't just retry and hope.

## Writing QA-Testable Code

**If QA can't test your code without reading the source, it's not shippable.**

This section codifies lessons from real QA passes. Every feature you ship must be testable by someone who has never seen your codebase.

### QA Documentation (`TESTING.md`)

Every project must have a `TESTING.md` (or a Testing section in README) covering:

1. **Environment setup** — exact commands to install from scratch:
   ```
   uv sync --package my-project
   uv run my-project --version  # verify install
   ```
2. **Prerequisites** — external services, proxy URLs, env vars, API keys needed.
3. **Feature inventory** — a table of every testable feature with expected behavior:
   ```
   | Feature | Command / Entry Point | Expected Behavior |
   |---|---|---|
   | Basic run | `my-cli run "hello"` | Streams response, shows token count |
   | RPC server | `echo '{"type":"prompt","content":"hi"}' \| my-cli rpc` | Outputs JSONL events |
   ```
4. **Wire protocol docs** — if the project has a protocol (RPC, WebSocket, API), document the exact format with copy-paste examples. Don't make QA reverse-engineer it.
5. **Known limitations** — what doesn't work yet, what's intentionally unsupported.
6. **Cleanup instructions** — how to reset state (sessions, caches, temp files) between test runs.

### Public API Surface

- **Export everything public from `__init__.py`.** If a user imports `from my_package import MyClass` and it fails, that's a bug — even if `from my_package.internal.module import MyClass` works.
- **Test your own imports.** Add a test that imports every public symbol from the package root.
- **Type what you accept.** If a field can be `str` or `int`, type it as `str | int`. Don't rely on "callers will always send strings." Real-world clients send integers, nulls, and things you didn't expect.

### Defensive Input Handling

- **Accept reasonable type variations.** Wire protocols receive JSON — integers, strings, nulls, missing fields. Handle all of them gracefully.
- **Validate early, fail with clear messages.** When input is invalid, return a structured error with what was wrong and what was expected. No raw tracebacks.
- **Test invalid inputs explicitly.** For every valid input test, write a corresponding invalid input test. If `id: "abc"` works, test `id: 42`, `id: null`, and missing `id`.

### State Management & Resume

- **Restore full state on resume.** If a feature supports `--session` or `--resume`, it must restore ALL state — not just messages, but also model, config, system prompt. Partial restore creates confusing behavior.
- **Make state inspectable.** Provide a way to view current state (`--status`, `get_state` command, etc.) so QA can verify what's loaded.
- **Document state location.** Where are sessions stored? How to list them? How to clear them?

### CLI & Error Behavior

- **Every CLI flag must work.** If `--help` shows a flag, it must do what it says. If `--no-tools` is listed, test it.
- **Consistent exit codes.** `0` for success, non-zero for errors. Document them.
- **Clean error messages on bad input.** Invalid flags → argparse error with usage. Missing required args → clear message. Never a Python traceback for user errors.
- **`--json` output option.** For any CLI that produces output, offer a structured `--json` flag. Parsing human-readable output for automated testing is fragile.
- **Env vars that are documented must work.** If README says `OPENAI_BASE_URL` configures the endpoint, it must actually be read. Don't silently ignore env vars while hardcoding defaults.

### Signal Handling & Lifecycle

- **Ctrl+C must exit cleanly.** First press → graceful shutdown with status message. No ignored signals, no tracebacks.
- **No orphan processes.** After exit, verify no child processes are left running. `/quit`, Ctrl+C, and EOF should all clean up.
- **Test the actual exit.** Don't just test that the quit handler is called — verify the process actually terminates (exit code 0, no hanging threads).

### Testability Patterns

- **Pure functions for logic, thin wrappers for I/O.** Extract business logic into pure functions that are easy to unit test. Keep I/O (network, filesystem, terminal) in thin wrapper layers.
- **Dependency injection over hardcoded defaults.** Accept config values as parameters, not module-level constants. This lets tests override without monkeypatching.
- **Don't trust mocks blindly.** If you mock `agent.run()` but the real method is `agent.prompt()`, all tests pass and the app is broken. Cross-reference mocks against actual interfaces.
- **Integration tests for wire protocols.** Unit tests with mocked I/O are necessary but not sufficient. Add at least one integration test that sends real bytes through the protocol and checks real output.

### Pre-Ship QA Checklist

Before calling any feature "done," verify from a clean environment:

- [ ] Install command works from scratch (not just in your dev env)
- [ ] `--version` returns correct version
- [ ] All public APIs importable from package root
- [ ] `--help` shows all options with descriptions
- [ ] Invalid input → clean error message (no tracebacks)
- [ ] Exit codes are consistent (0 success, non-zero error)
- [ ] All documented env vars actually work
- [ ] Wire protocols accept reasonable type variations (int/str/null)
- [ ] Resume/reload restores full state
- [ ] Ctrl+C exits cleanly, no orphan processes
- [ ] At least one copy-paste example in docs that QA can run verbatim
- [ ] `TESTING.md` updated with new features

## Smoke Test Before PR

**Unit tests are necessary but not sufficient.** Before opening a PR (especially for milestones that add CLI commands, API endpoints, or runnable features), run a smoke test of the actual artifact:

### What to Smoke Test
- **CLI commands:** Actually invoke them (e.g. `my-cli run "hello"`, `my-cli serve` with a test request). Don't just test argument parsing.
- **API endpoints:** Hit them with curl or a test client. Don't just test handler logic in isolation.
- **Libraries:** Import and call the public API from a scratch script. Don't just test internal functions.
- **TUI/UI:** Launch it (even with piped input) and verify it doesn't crash on startup.

### When to Smoke Test
- **Final subtask of each milestone** — before opening the PR.
- **After any bugfix** — verify the fix actually works end-to-end.
- **After major refactors** — especially if public API surface changed.

### Why This Matters
Unit tests mock dependencies. If the mocks match the buggy code, all tests pass but the real app is broken. E2E smoke tests catch integration failures that unit tests structurally cannot.

### In the Orchestrator Prompt
For the final subtask of a milestone, include smoke test instructions in the Claude Code prompt:
```
# After all tests pass, smoke test:
# 1. Run the CLI command and verify it works
# 2. If it fails, fix the issue and re-run tests
# 3. Only commit after both unit tests AND smoke test pass
```

## Hard Lessons

- **Read first, code second.** Read the full task/issue before starting. Follow steps literally and in order — don't bundle or skip. When unsure, ask before guessing.
- **Test what you ship.** Untested code is unfinished code.
- **Don't skip the design step.** Even 5 minutes of planning saves hours of rework.
- **Check before you push.** Review your own diff. Every time. Also verify PR/branch status before committing to an existing branch — if the PR is already merged, open a new one.
- **Docs are not optional.** If the code changed, the docs should too.
- **Learn from mistakes.** Document lessons learned. Don't repeat the same error twice.
- **Small PRs win.** Large PRs get rubber-stamped or delayed. Small PRs get real reviews.
- **Ask when stuck.** Don't spin for hours. Flag blockers early.
- **Verify your own results.** Don't blindly trust sub-agent or tool output — confirm it yourself.
- **Mocks can lie.** If you mock `agent.run()` and the real method is `agent.prompt()`, all tests pass and the app is broken. Smoke test the real thing.
- **Type what the wire sends, not what you wish it sent.** JSON has ints, strings, nulls, and missing keys. Your models must handle all of them. An integer `id` rejected by a `str`-only field is a preventable P0.
- **Export your public API.** If it's importable in theory but not from the package root, QA and users will file bugs. Test your own imports.
- **QA docs ≠ dev docs.** Developers know the codebase. QA doesn't. Write setup/testing docs for someone who has never seen your code. Include copy-paste commands.

## Security

- Never hardcode credentials or secrets.
- Use environment variables or secret managers.
- Sanitize user input.
- Follow the principle of least privilege.
- For sudo/privilege escalation, confirm before proceeding.
