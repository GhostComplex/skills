# RCA Template

Use this template when documenting manual bug fixes. Each RCA feeds future automated QA cycles.

## Header

```markdown
# <Title> RCA

**Date:** YYYY-MM-DD
**Commits:** `<hash1>`, `<hash2>`, ...
**Branch:** `<branch-name>`
**Files changed:** N (X insertions, Y deletions)
```

## Per-Issue Section

```markdown
## Issue N: <Short description>

**Symptom:** What the user saw or experienced.

**Root Cause:** Why it happened — trace from symptom to code.

**Fix (commit `<hash>`):**
- Bullet list of changes made
- Include file names and specific lines/patterns changed

**Files affected:** List all files touched

**Test points:**
- [ ] Specific test case 1 — what to verify
- [ ] Specific test case 2 — what to verify
- [ ] ...
```

## Guidelines

1. **Symptom first** — describe what the user actually experienced, not the code bug
2. **Root cause must explain WHY** — "the border was too thick" is a symptom, "Theme.border applied at full opacity with lineWidth: 1" is a root cause
3. **Fix should be reproducible** — someone reading this should be able to re-apply the same fix
4. **Test points become QA checklist items** — write them as concrete, verifiable checks
5. **Pattern extraction** — after writing the RCA, identify the general anti-pattern (e.g., "hardcoded colors instead of design tokens") that can be grep-detected in future code audits
