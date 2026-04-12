---
name: ios-app-qa
description: iOS app QA verification using Xcode command-line tools, iOS Simulator, and XCUITest. Use when verifying iOS app builds, running UI tests, capturing simulator screenshots, filing GitHub issues with inline screenshots, or doing acceptance testing for iOS projects. Triggers on phrases like "verify iOS app", "run simulator", "QA test", "acceptance test", "iOS screenshots", "XCUITest".
---

# iOS App QA Skill

Universal iOS app QA verification via command-line Xcode builds, simulator management, XCUITest automation, and structured acceptance reporting.

Works with any iOS project: `.xcodeproj`, `.xcworkspace`, SPM-only, CocoaPods, Carthage.

---

## Prerequisites

- macOS with Xcode installed (`xcodebuild -version` to confirm)
- Xcode CLI tools: `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`
- License accepted: `sudo xcodebuild -license accept`
- First launch: `sudo xcodebuild -runFirstLaunch`
- iOS Simulator runtime: `xcodebuild -downloadPlatform iOS` (~8GB)

---

## 1. Project Discovery

Before building, discover the project structure. Never assume scheme/target names.

### Detect project type

```bash
cd <PROJECT_DIR>

# Priority: workspace > xcodeproj > Package.swift
if ls *.xcworkspace 1>/dev/null 2>&1; then
    echo "Workspace found: $(ls *.xcworkspace)"
    xcodebuild -list -workspace *.xcworkspace
elif ls *.xcodeproj 1>/dev/null 2>&1; then
    echo "Project found: $(ls *.xcodeproj)"
    xcodebuild -list -project *.xcodeproj
elif [ -f Package.swift ]; then
    echo "SPM-only project"
    swift package describe
fi
```

### What to look for in `-list` output

```
Schemes:
    MyApp              ← main app scheme (use for build + install)
    MyAppTests         ← unit test scheme
    MyAppUITests       ← UI test target (use for XCUITest)
```

**Key rules:**
- Use the **app scheme** (not test scheme) for `build` and `install`
- Use `-only-testing:<UITestTarget>` for XCUITest runs
- If no schemes show up → they're not marked "shared" in Xcode → ask dev to share them

### Detect bundle ID

```bash
# From Info.plist
/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" <PROJECT>/Info.plist 2>/dev/null

# Or from build settings
xcodebuild -showBuildSettings -scheme <SCHEME> 2>/dev/null | grep PRODUCT_BUNDLE_IDENTIFIER
```

---

## 2. Simulator Management

### List available simulators

```bash
xcrun simctl list runtimes available          # installed iOS versions
xcrun simctl list devicetypes | grep iPhone   # device types
xcrun simctl list devices available | grep iPhone  # existing devices
```

### Create a simulator

```bash
# Match device type to installed runtime
xcrun simctl create "QA Test" "iPhone 17 Pro" "com.apple.CoreSimulator.SimRuntime.iOS-26-4"
# Returns: <DEVICE_UUID>
```

### Boot / reset / shutdown

```bash
xcrun simctl boot <DEVICE_UUID>
xcrun simctl shutdown <DEVICE_UUID>
xcrun simctl erase <DEVICE_UUID>    # factory reset — use before each QA round
```

### Open Simulator app (for human viewing)

```bash
open -a Simulator
```

### Troubleshooting

If `list runtimes` is empty but `runtime list` shows "Ready":
```bash
xcrun simctl runtime scan-and-mount
```

If runtime shows "Duplicate" error: do NOT delete the "Ready" one. Delete only the duplicate UUID.

---

## 3. Build

### Build command by project type

**`.xcworkspace` (CocoaPods, multi-project):**
```bash
xcodebuild -workspace App.xcworkspace -scheme <SCHEME> \
  -destination 'platform=iOS Simulator,id=<DEVICE_UUID>' \
  -derivedDataPath build clean build 2>&1 | tail -10
```

**`.xcodeproj` (standalone):**
```bash
xcodebuild -project App.xcodeproj -scheme <SCHEME> \
  -destination 'platform=iOS Simulator,id=<DEVICE_UUID>' \
  -derivedDataPath build clean build 2>&1 | tail -10
```

**SPM-only (Package.swift, no .xcodeproj):**
```bash
xcodebuild -scheme <SCHEME> \
  -destination 'platform=iOS Simulator,id=<DEVICE_UUID>' \
  -derivedDataPath build clean build 2>&1 | tail -10
```

### Always clean build for QA

```bash
rm -rf build DerivedData
```

Incremental builds may use stale cached code. QA must always start from clean.

### Compile errors → report to dev

**PM does not fix project code.** Extract errors and report:

```bash
xcodebuild ... 2>&1 | grep "error:" | head -20
```

Report format: **file path + line number + error message**. Stop QA until fixed.

---

## 4. Install & Launch

```bash
# Find the .app bundle
APP_PATH=$(find build/Build/Products -name "*.app" -type d | head -1)

# Install and launch
xcrun simctl install <DEVICE_UUID> "$APP_PATH"
xcrun simctl launch <DEVICE_UUID> <BUNDLE_ID>
```

If using default DerivedData (no `-derivedDataPath`):
```bash
APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator -name "*.app" -type d | sort | tail -1)
```

---

## 5. Screenshots

### Static screenshot (headless)

```bash
xcrun simctl io <DEVICE_UUID> screenshot /path/to/output.png
```

**Limitation:** Cannot tap or swipe. Only captures current screen. Use XCUITest for interactive flows.

### Video recording

```bash
xcrun simctl io <DEVICE_UUID> recordVideo /path/to/output.mp4
# Press Ctrl+C to stop
```

### Screenshot file organization

Save all QA screenshots in a dedicated directory inside the repo:

```bash
mkdir -p qa-screenshots/<round-name>
# Example: qa-screenshots/copy-qa/, qa-screenshots/ui-fidelity-v2/
```

### Push screenshots to repo

Screenshots must be committed and pushed **before** they can be referenced in reports:

```bash
git add qa-screenshots/
git commit -m "QA: screenshots for <round>"
git push origin main
```

### Reference screenshots in markdown (repo files)

In repo markdown files (reports, issues, checklists), use **relative paths**:

```markdown
✅ ![description](./qa-screenshots/round/image.png)      ← same directory level
✅ ![description](/qa-screenshots/round/image.png)        ← repo root absolute

❌ https://github.com/OWNER/REPO/blob/main/path/image.png           ← shows code page, not image
❌ https://github.com/OWNER/REPO/blob/main/path/image.png?raw=true  ← unreliable in private repos
```

GitHub auto-resolves relative paths when rendering repo markdown. No need for absolute URLs.

---

## 6. XCUITest (Automated User Flow Testing)

XCUITest simulates real taps, swipes, and user interactions. It runs in the simulator (works headless for CI).

### Discover available tests

```bash
# List all test targets and methods
xcodebuild -list -project App.xcodeproj | grep -A 100 "Schemes:"

# Run all UI tests
xcodebuild test -project App.xcodeproj -scheme <SCHEME> \
  -destination 'platform=iOS Simulator,id=<DEVICE_UUID>' \
  -only-testing:<UITestTarget> \
  -resultBundlePath output/test.xcresult 2>&1 | tail -20
```

**Build flags by project type — same as Section 3** (use `-workspace` for .xcworkspace, etc.)

### Run specific tests

```bash
# Single test class
-only-testing:<UITestTarget>/<TestClass>

# Single test method
-only-testing:<UITestTarget>/<TestClass>/<testMethod>

# Skip specific tests
-skip-testing:<UITestTarget>/<TestClass>/<testMethod>
```

### Test result summary

```bash
RESULT=$(find build/Logs/Test -name "*.xcresult" -type d 2>/dev/null | sort | tail -1)
# Fallback: check default DerivedData
[ -z "$RESULT" ] && RESULT=$(find ~/Library/Developer/Xcode/DerivedData/*/Logs/Test -name "*.xcresult" -type d 2>/dev/null | sort | tail -1)

xcrun xcresulttool get test-results summary --path "$RESULT"
```

### Extract screenshots from xcresult

**Modern method (Xcode 16+):**
```bash
mkdir -p qa-screenshots
xcrun xcresulttool export attachments --path "$RESULT" --output-path qa-screenshots
```

**Fallback (older Xcode or if export fails):**
```bash
for f in "$RESULT"/Data/data.*; do
    if file -b "$f" | grep -qi "png"; then
        name=$(basename "$f")
        cp "$f" "qa-screenshots/${name}.png"
    fi
done
```

### Parallel testing (large suites)

```bash
xcodebuild test ... -parallel-testing-enabled YES
```

---

## 7. GitHub Issues with Screenshots

For issue body, use the same relative path format as reports (see Section 5).

### Issue workflow

```bash
# Create issue — screenshots referenced by relative path
gh issue create --repo OWNER/REPO --title "Bug title" --body '## Problem
![screenshot](./qa-screenshots/round/image.png)
## Expected behavior
...
## Priority
P0/P1/P2
## Source
QA checklist item #X.X'

# Comment with verification after fix
gh issue comment NUMBER --repo OWNER/REPO --body '## ✅ Verified
![fixed](./qa-screenshots/round/fixed.png)
Commit: `abc1234`'

# Close only after verified
gh issue close NUMBER --repo OWNER/REPO --reason completed
```

---

## 8. Acceptance Flow SOP

Every QA round follows this sequence. No skipping steps.

### Step 0: Write Test Cases FIRST

**Before touching the simulator, write the complete test case list.** Based on:
- PRD requirements (every feature → at least one test case)
- Design spec (every screen → visual verification case)
- User flows (every interaction chain → flow test case with screenshot sequence)
- Edge cases (empty states, boundary values, error states)

Output: a filled `references/qa-checklist-template.md` with all items listed, results column blank.

**No test cases = no acceptance.** Do not start building/installing until the checklist is complete and reviewed.

### Step 1: Sync & Clean Build

```bash
cd <PROJECT_DIR>
git pull origin main
rm -rf build DerivedData
```

Then build (see Section 3 for project-type-specific commands).

If build fails → extract `error:` lines, report to dev. **Stop here until fixed.**

### Step 2: Reset Simulator & Install

```bash
xcrun simctl shutdown <DEVICE_UUID>
xcrun simctl erase <DEVICE_UUID>         # Clean state every time
xcrun simctl boot <DEVICE_UUID>
xcrun simctl install <DEVICE_UUID> "$APP_PATH"
xcrun simctl launch <DEVICE_UUID> <BUNDLE_ID>
```

### Step 3: Screenshot Every Screen

Run XCUITest or manually navigate. **One screenshot per verification item.** Do not reuse one screenshot for multiple items.

Save to repo directory (see Section 5 for path convention):
```bash
mkdir -p qa-screenshots/<round-name>
xcrun simctl io <DEVICE_UUID> screenshot qa-screenshots/<round-name>/01-screen-name.png
```

Push screenshots to repo immediately so they can be referenced in the report:
```bash
git add qa-screenshots/ && git commit -m "QA: screenshots for <round>" && git push origin main
```

### Step 4: Open and Verify Every Screenshot

**Must open each screenshot image and check the actual content.** Rules:

- Do NOT trust file names — a file named `article-detail.png` might show a Kegel timer
- Describe what you **actually see**, not what you expect
- If screenshot content doesn't match the verification item → mark ❌

**Interactive flows need a screenshot sequence, not a single image.** For example, verifying "Kegel timer works" requires:
1. Before tap (start button visible)
2. Timer running (contraction phase)
3. Timer running (relaxation phase)
4. Completion state (Toast / done screen)

One screenshot only proves "this screen exists." A sequence proves "the interaction works end-to-end." If you can't show the full flow, mark it ⏳ not ✅.

### Step 5: Compare Against Design Spec

For each screen, open design spec side-by-side with the screenshot:

- Colors match? (check hex values, not "looks similar")
- Fonts correct? (size, weight, family)
- Spacing right? (padding, margins)
- Icons correct? (style, color, size)

Discrepancies fall into two categories:
- **Spec issue (PM responsibility):** spec was ambiguous/wrong → update spec first
- **Dev issue:** spec is clear but implementation differs → file issue

### Step 6: Write Acceptance Report

Output a report following `references/acceptance-report-template.md`. **The report is the final deliverable — no report = no acceptance.**

**Report formatting rules:**
- Each verification section must have its screenshot **directly above** the results table (not in a separate section at the bottom)
- Use `![description](./qa-screenshots/round/image.png)` relative paths
- Code-only verifications (e.g. push notification text) must note the source file and line number
- Push the report to repo and **always share the GitHub link** in chat:
  ```
  https://github.com/OWNER/REPO/blob/main/qa-report-name.md
  ```
  Never just say "report is done" without a link.

### Step 7: File Issues for Failures

Every ❌ item → GitHub issue with screenshot + expected behavior. Link back to the report.

---

## Templates

- **QA Checklist:** `references/qa-checklist-template.md`
- **Acceptance Report:** `references/acceptance-report-template.md`

---

## Key Lessons

- **PM does not debug project code** — report errors with file/line/message to developers
- **Never skip or work around issues** — fix problems properly
- **Every verification needs a screenshot** — no "verified by reading code"
- **Reset simulator between test runs** — `xcrun simctl erase` for clean state
- **XCUITest > URL schemes > launch args** — for testing, prefer real user interaction
- **Test passing ≠ QA passing** — test pass means logic didn't crash; QA pass means UI is visually correct
- **Open every screenshot and verify actual content** — never trust file names alone
- **Write descriptions based on what you see, not what you expect** — if a screenshot shows the wrong screen, that's a bug
- **Clean build before QA** — always `rm -rf DerivedData` before verification builds
- **Discover before assuming** — always run `xcodebuild -list` first; never hardcode scheme/target names
- **Use `xcresulttool export attachments`** — modern Xcode has a proper API; don't brute-force scan data files
