---
name: superqa-isotope
description: >
  QA testing for the Isotope agent framework (GhostComplex/isotope).
  Activate when: QA testing isotope CLI/TUI/RPC, smoke-testing isotope builds,
  verifying isotope bug fixes, running regression tests on isotope, or reviewing
  isotope PRs from a QA perspective.
  NOT for: other projects (use superqa), unit tests or code review (use superboss/supercrew),
  or writing isotope code (use supercrew).
---

# Isotope QA

Black-box QA for the [Isotope](https://github.com/GhostComplex/isotope) agent framework. Test the built artifact as a user would.

Inherits methodology from `superqa` (generic black-box testing). This skill adds Isotope-specific environment setup, test plans, known issues, and lessons learned.

## Reporting

Use `references/qa-report-template.md` for each QA pass. Save reports to `reports/` (gitignored — reports stay local, not checked in).

## Environment Setup

### Prerequisites

- **LLM proxy** at `localhost:4141` (OpenAI-compatible). Required for any test that sends prompts.
- **Python 3.12+** with `uv` installed.
- **tmux** for TUI testing.

### Install from Source

```bash
cd _repos/isotope
uv sync --package isotope-agents --extra tui
```

Verify:
```bash
uv run isotope --version          # → isotope-agents X.Y.Z
uv run isotope --help             # → shows subcommands
uv run python -c "from isotope_agents import IsotopeAgent; print('ok')"  # → ok (if exported)
```

### Install from PyPI

```bash
uvx --from 'isotope-agents[tui]' isotope --version
```

## Architecture

Monorepo with two packages:

| Package | Path | What it does |
|---|---|---|
| `isotope-core` | `packages/isotope-core/` | Agent loop, LLM providers, middleware, events, context |
| `isotope-agents` | `packages/isotope-agents/` | CLI, TUI, tools, sessions, RPC, presets, skills, MCP |

## Test Plan

### 1. Install Verification

```bash
uv sync --package isotope-agents --extra tui
uv run isotope --version
uv run isotope --help
uv run python -c "from isotope_core import Agent; print('ok')"
uv run python -c "from isotope_agents.agent import IsotopeAgent; print('ok')"
```

Check: all commands succeed, no tracebacks.

### 2. CLI: `isotope run`

```bash
# Basic prompt (needs proxy)
uv run isotope run "what is 2+2"

# With model override
uv run isotope run --model claude-sonnet-4-20250514 "say hello"

# With preset
uv run isotope run --preset minimal "list files in current dir"

# No tools
uv run isotope run --no-tools "what is 2+2"
```

Check: streams response, shows `[tokens: in=X, out=Y]`, exit code 0.

### 3. CLI: `isotope sessions`

```bash
uv run isotope sessions
```

Check: lists saved sessions with IDs, message counts, previews. No crash on empty list.

### 4. TUI: `isotope chat`

Use tmux with `remain-on-exit` for capture:

```bash
tmux kill-session -t qa 2>/dev/null
tmux new-session -d -s qa -x 120 -y 40 "uv run isotope chat"
tmux set-option -t qa remain-on-exit on
```

**Startup flow:**
1. System prompt selection (Enter to skip)
2. Model selection (Enter for default, or type model name)
3. Shows session ID + prompt

```bash
sleep 3
tmux capture-pane -t qa -p  # Should show prompt setup
tmux send-keys -t qa "" Enter  # Skip system prompt
sleep 1
tmux send-keys -t qa "" Enter  # Accept default model
sleep 2
tmux capture-pane -t qa -p  # Should show "Type your message" prompt
```

**Chat interaction:**
```bash
tmux send-keys -t qa "what is 2+2" Enter
sleep 8  # Wait for LLM response
tmux capture-pane -t qa -p  # Should show response
```

**Tool calling (coding preset):**
```bash
tmux send-keys -t qa "list files in this directory" Enter
sleep 10
tmux capture-pane -t qa -p  # Should show tool call + result
```

**Commands:**
```bash
tmux send-keys -t qa "/help" Enter
sleep 1
tmux capture-pane -t qa -p  # Should list available commands
```

**Clean exit (Ctrl+C):**
```bash
tmux send-keys -t qa C-c
sleep 2
tmux capture-pane -t qa -p  # Should show "Bye!"
tmux list-panes -t qa -F '#{pane_dead} #{pane_dead_status}'  # → 1 0
```

Check: `pane_dead=1`, `pane_dead_status=0`. Process fully terminated.

### 5. RPC: `isotope rpc`

Test JSONL-over-stdio protocol:

```bash
# Basic prompt
echo '{"type":"prompt","content":"say hello","id":"test-1"}' | uv run isotope rpc 2>/dev/null

# Integer ID (regression: was P0 crash)
echo '{"type":"prompt","content":"say hi","id":1}' | uv run isotope rpc 2>/dev/null

# get_state
echo '{"type":"get_state","id":"s1"}' | uv run isotope rpc 2>/dev/null

# abort (should not crash)
echo '{"type":"abort","id":"a1"}' | uv run isotope rpc 2>/dev/null
```

Check: JSONL events on stdout (`agent_start`, `text_delta`, `agent_end`). Integer `id` must not crash.

### 6. Presets

```bash
uv run isotope run --preset coding "what tools do you have"
uv run isotope run --preset assistant "what tools do you have"
uv run isotope run --preset minimal "what tools do you have"
```

Check: each preset loads different tool sets. `coding` has read/write/edit/bash/grep/glob. `minimal` has bash only.

### 7. Error Paths

```bash
# Bad model name
uv run isotope run --model nonexistent-model "hello"

# Invalid subcommand
uv run isotope badcmd

# No proxy running (kill proxy first, or use wrong port)
OPENAI_BASE_URL=http://localhost:9999 uv run isotope run "hello"
```

Check: clean error messages (not raw tracebacks), non-zero exit codes.

### 8. Session Resume

```bash
# Create a session
uv run isotope run "remember the number 42" 2>&1 | grep -i session

# Resume (use session ID from above)
uv run isotope chat --session <id>
```

Check: resumes with prior messages loaded. **Known P2:** Still prompts for model/system prompt on resume.

## Known Bugs (P2 — Open)

| Bug | Status | Description |
|---|---|---|
| `--session` re-prompts | Open | Resuming a session still asks for model and system prompt selection |
| `IsotopeAgent` not in `__init__` | Open | `from isotope_agents import IsotopeAgent` fails — must use full path |
| `OPENAI_BASE_URL` ignored | Open | Env var silently ignored; must use config file for `base_url` |

## Fixed Bugs (Reference)

| Bug | PR | Fix |
|---|---|---|
| P0: RPC crash on integer `id` | #24 | Widened `id` to `str \| int \| None`, stringify for `stream_id` |
| P1: TUI duplicate text on tool calls | #24 | `_streamed_text` flag skips `message_end` re-render |
| P1: Ctrl+C doesn't exit TUI | #24 | `os._exit(0)` after "Bye!" — prompt_toolkit stdin reader blocks normal exit |
| TUI: Rich bypasses patch_stdout | #26 | Plain `print()` when prompt_toolkit active, Rich when not |
| TUI: ANSI garbage in tool panels | #26 | `Text.from_ansi()` for tool output |
| TUI: Structured tool result as JSON dump | #26 | Extract text from `{"content": [{"type":"text",...}]}` |

## TUI Visual Testing Limitations

**What tmux capture can verify:**
- Text content is present and correct
- Tool calls fire and return output
- Commands work (`/help`, `/quit`)
- Clean exit (pane_dead + exit code)
- No Python tracebacks in output

**What tmux capture CANNOT verify:**
- Rich panel borders and styling
- Color rendering correctness
- ANSI escape code handling (content may look correct in capture but garbled on screen)
- Text overlap or positioning bugs
- prompt_toolkit input rendering

**Workaround:** For visual rendering bugs, the only reliable test is a human looking at the screen or screenshot-based regression testing (not currently available).

## Lessons Learned

- **`os._exit(0)` for prompt_toolkit apps.** `sys.exit()` and `SystemExit` don't work — prompt_toolkit's stdin reader thread keeps the process alive. `os._exit(0)` terminates immediately.
- **Rich Console and patch_stdout conflict.** Rich writes directly to the real stdout, bypassing prompt_toolkit's output intercept. Use plain `print()` for anything rendered while prompt_toolkit is active.
- **RPC protocols need type tolerance.** JSON sends ints, strings, nulls. Pydantic models must accept all reasonable variations. The P0 crash was caused by `str`-only typing on `id`.
- **Mocks matched the buggy code.** 883 unit tests passed while the app had broken method calls. Always smoke-test the actual binary.
- **Tool result structure varies at runtime.** Unit tests mock results as strings; real tools return `{"content": [{"type": "text", ...}]}`. Test with real response fixtures.
- **ANSI codes in tool output.** Bash tool output contains color codes from `ls`, `grep`, `ruff`, etc. Renderers must handle ANSI or strip it.

## Regression Checklist (Post-Merge)

After any merge to `main`, run this quick regression:

1. `uv sync --package isotope-agents --extra tui` — installs clean
2. `uv run isotope --version` — correct version
3. `uv run isotope run "say hello"` — streams response
4. `echo '{"type":"prompt","content":"hi","id":1}' | uv run isotope rpc 2>/dev/null` — JSONL output, no crash
5. TUI launch → send message → Ctrl+C → verify exit code 0
6. `uv run isotope sessions` — lists sessions

If all pass, the build is green.
