---
name: ios-e2e-qa
description: "Automated E2E QA for iOS apps on Simulator: screenshot every screen, evaluate against a design system, find UX/visual bugs, and open GitHub issues. Use when: (1) running E2E visual QA on an iOS app, (2) setting up automated QA cron jobs for iOS projects, (3) evaluating screenshots against design standards (Liquid Glass, Material Design, HIG, custom), (4) discovering UX and design smells via simulator testing. Triggers: 'E2E QA', 'visual QA', 'screenshot QA', 'design review', 'iOS QA', 'simulator QA', 'automated QA cron'. NOT for: unit testing, CI pipeline setup, Android apps, or web apps."
---

# iOS E2E QA Skill

Automated visual QA for iOS apps: build → deploy to Simulator → screenshot every screen → evaluate against design standards → open issues for failures.

## Workflow

### 1. Gather Project Config

Before running QA, collect these from the user or project files:

```
REPO            # GitHub repo (owner/repo)
XCODE_PROJECT   # path to .xcodeproj
SCHEME          # Xcode scheme name
BUNDLE_ID       # app bundle identifier
SIMULATOR       # Simulator UDID (from `xcrun simctl list devices`)
SIMULATOR_NAME  # e.g. "iPhone 17 Pro"
DERIVED_DATA    # build output path (default: build/)
DESIGN_SYSTEM   # design standard to evaluate against
```

Optional (for issue/board management):
```
GH_PROJECT_NUM  # GitHub project board number
STATUS_FIELD_ID # project Status field ID
READY_OPTION_ID # "Ready" status option ID
DONE_OPTION_ID  # "Done" status option ID
DISPATCH_TO     # Discord @mention for issue assignment
```

### 2. Build & Deploy

```bash
# Build
xcodebuild build \
  -project "$XCODE_PROJECT" -scheme "$SCHEME" \
  -destination "platform=iOS Simulator,name=$SIMULATOR_NAME,OS=latest" \
  -derivedDataPath "$DERIVED_DATA" -quiet 2>&1

# Deploy
xcrun simctl terminate "$SIMULATOR" "$BUNDLE_ID" 2>/dev/null
xcrun simctl install "$SIMULATOR" "$DERIVED_DATA/Build/Products/Debug-iphonesimulator/$SCHEME.app"
xcrun simctl launch "$SIMULATOR" "$BUNDLE_ID"
```

### 3. Screenshot Every Screen

For each reachable screen state:

```bash
# Navigate to state (simctl openurl, push notifications, or natural app flow)
xcrun simctl io "$SIMULATOR" screenshot "/tmp/qa-<screen-name>.png"
```

Read each screenshot image to visually inspect it. **Headless simulators** cannot receive tap events — if a screen requires tap navigation and no display is attached, do a **code audit** instead: read the SwiftUI view file and evaluate the design tokens directly.

### 4. Evaluate Against Design System

Read `references/design-systems.md` for evaluation criteria per design system. Every screenshot or code audit must be checked against:

1. **Visual consistency** — borders, shadows, colors, spacing uniform across views
2. **Design system compliance** — materials, corner radii, typography match the spec
3. **UX smells** — see smell checklist below
4. **Interaction correctness** — error states, loading states, empty states all handled

### 5. UX Smell Checklist (Universal)

These are design smells regardless of design system:

- Boxy hard-bordered cards with no depth
- Custom overlays fighting OS native chrome (nav bar, tab bar, status bar)
- Errors displayed as regular content (not visually distinct)
- Input controls active on broken/error states
- Duplicate content on view re-entry
- Hard color transitions without blur/gradient/animation
- Inconsistent corner radii across similar components
- Shadow values that differ between cards of the same type
- Auto-scroll failure during streaming/live content
- Stale data after navigation (list not refreshing)
- Missing loading/empty/error states
- Text truncation hiding critical info
- Locale-sensitive formatting bugs (numbers, dates)

### 6. Issue Creation

For each problem found, open a GitHub issue:

```bash
gh issue create --repo "$REPO" \
  --title "iOS: <concise description>" \
  --body "<description>

**Expected:** <what should happen>
**Actual:** <what happens>
**Screenshot:** <reference /tmp/qa-*.png>
**Design system:** <which standard is violated>"
```

If a project board is configured:
```bash
gh project item-add "$GH_PROJECT_NUM" --owner "$OWNER" --url "$ISSUE_URL"
# Move to Ready using field/option IDs
```

### 7. Cleanup

```bash
xcrun simctl terminate "$SIMULATOR" "$BUNDLE_ID"
# Kill any background processes (daemons, servers) started for testing
```

### 8. Report

Post a summary with:
- Build status (pass/fail)
- Screens tested (screenshot vs code audit)
- Pass/fail per screen with brief reason
- Issues opened (with links)
- Overall assessment (🟢/🟡/🔴)

## Cron Job Setup

To run QA on a recurring schedule, create a cron job with these guidelines:

1. **Idle check** — only run full E2E when the channel has been idle (no substantive messages in last N minutes). Otherwise, post a brief status check only.
2. **Dispatch rule** — when issues are found and added to the board, immediately dispatch to the assigned developer by @-mention. Never leave issues in Ready without assignment.
3. **Code review** — use `claude --print --permission-mode bypassPermissions` for PR review and code audits.
4. **Dedup** — if no code has changed since last QA run, skip the build/screenshot cycle. Report "no changes" instead.
5. **Always post** — never reply NO_REPLY from a cron. Always post at least a brief status.

## RCA-Driven QA

When fixing bugs manually, write a Root Cause Analysis doc (see `references/rca-template.md`). The RCA feeds future QA cycles:

1. Each RCA **test point** becomes a permanent item in the QA checklist
2. Each RCA **root cause** becomes a pattern to grep for in code audits
3. Each RCA **fix pattern** becomes a "known good" reference for reviewing similar code

This creates a feedback loop: manual fixes → RCA → automated QA catches regressions.
