# QA Checklist Template

Copy and adapt for each iOS app project.

---

## Verification Method

- Device: iPhone XX Pro / iOS XX.X (Simulator)
- Method: XCUITest automated flow (`testFullUserFlow`)
- Screenshots: extracted from `.xcresult`, stored in `qa-screenshots/`

## Checklist Format

```markdown
| # | Verification Item | Result | Screenshot | Notes |
|---|-------------------|--------|------------|-------|
| 1.1 | Description | ✅/❌/⏳ | `filename.png` | Details |
```

**Result values:**
- ✅ Pass (with screenshot evidence)
- ❌ Fail (open GitHub issue with screenshot)
- ⏳ Pending (blocked, describe why)

## Recommended Categories

1. **First Launch** — onboarding, permissions, initial setup
2. **Main Screens** — each tab/page renders correctly
3. **Core Interactions** — buttons, forms, navigation
4. **Data** — persistence, state management
5. **Design Fidelity** — colors, fonts, spacing vs design spec
6. **Notifications** — push, local
7. **Edge Cases** — empty states, boundary values, kill/restart

## Pass Criteria

- Pass rate ≥ 90%
- Zero P0 issues (crashes, data loss, core flow broken)
- All failed items tracked as GitHub issues with inline screenshots

## Issue Template

```markdown
## Problem
[one sentence]

## Screenshot
![screenshot](https://github.com/OWNER/REPO/blob/main/qa-screenshots/FILE.png?raw=true)

## Expected Behavior
[what should happen]

## Priority
P0/P1/P2

## Source
QA checklist item #X.X
```
