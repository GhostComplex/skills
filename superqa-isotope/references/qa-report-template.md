# QA Report Template

Copy this template for each QA pass. Save reports to `reports/` (gitignored).

```markdown
# QA Report: Isotope — <Epoch/Version> (<Date>)

## Environment
- **Commit:** `<hash>` (<branch>)
- **Install:** `<install command>`
- **Platform:** <os/arch>, Python <version>
- **Proxy:** `<url>`

## Results

| Test | Status | Notes |
|------|--------|-------|
| Install | ✅/❌ | |
| `--version` | ✅/❌ | |
| `--help` | ✅/❌ | |
| `run` (basic) | ✅/❌ | |
| `run --preset` | ✅/❌ | |
| `run --no-tools` | ✅/❌ | |
| `run --model` | ✅/❌ | |
| `sessions` | ✅/❌ | |
| TUI: launch | ✅/❌ | |
| TUI: chat | ✅/❌ | |
| TUI: tool calls | ✅/❌ | |
| TUI: /help | ✅/❌ | |
| TUI: /quit | ✅/❌ | |
| TUI: Ctrl+C | ✅/❌ | |
| RPC: string id | ✅/❌ | |
| RPC: integer id | ✅/❌ | |
| `--session` resume | ✅/❌ | |
| Error: bad model | ✅/❌ | |
| Error: no proxy | ✅/❌ | |

## Bugs Found

1. **[P0/P1/P2]** Description — command run, expected behavior, actual behavior

## Regressions

- (any previously-fixed bugs that reappeared)

## Notes

- (observations, recommendations, follow-ups)
```
