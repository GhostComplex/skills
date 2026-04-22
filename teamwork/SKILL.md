---
name: teamwork
description: "Local feature lifecycle: requirements → PRD → implement in worktree → PR → CI → multi-perspective code review → fix loop. /teamwork [feature description or issue#]"
argument-hint: "[feature description to discuss, or issue# to resume]"
---

# Teamwork — Local Feature Lifecycle

You are the **orchestrator**. You drive a feature from idea to merge-ready PR in a single session. You handle requirements, design, implementation, and PR creation yourself. Only code review is delegated — to parallel review agents with distinct perspectives.

Each `/teamwork` session runs in its own terminal process (tmux window or separate terminal) with its own worktree. Tmux panes within a window are reserved for agent teams — use separate windows or terminal processes for parallel features.

## Session Isolation

Multiple `/teamwork` sessions can work on the same repo simultaneously without interfering, as long as they run in **separate tmux windows or terminal processes** (not panes — panes are used by agent teams). The **feature-slug** is the isolation key (analogous to Discord's channel ID in superboss).

### How Isolation Works

| Layer | Isolation mechanism |
|-------|-------------------|
| **Git** | Each session gets its own worktree (`EnterWorktree` with unique feature-slug) → separate branch, separate working directory. Commits and pushes never collide. |
| **PRD** | Each feature writes to `docs/prd/<feature-slug>.md` — unique path per feature. |
| **Issues/PRs** | Each feature creates its own issue and PR — no shared state. |
| **Tracking** | `.teamwork/<feature-slug>/` — each feature gets its own directory (not a shared JSON file). |
| **Reviews** | `.teamwork/<feature-slug>/reviews/round-N.md` — scoped to the feature. |

### Avoiding Conflicts

- **Never share a feature-slug across sessions.** Each session = unique feature-slug = unique worktree.
- **PRDs are committed on the feature branch**, not on main — so parallel PRD commits don't conflict.
- **`.teamwork/` uses per-feature directories**, not a single shared JSON file — no concurrent write risk.
- If the user asks to resume an in-progress feature, it should be in the **same session** that started it (same worktree context).

### Feature-Slug as Session ID

The feature-slug serves the same purpose as Discord's channel ID in superboss/supercrew:
- It's chosen at Step 1 during brainstorming (derived from the feature description)
- It must be unique within the repo — check for collisions before creating
- All artifacts (PRD, branch, worktree, tracking, reviews) are namespaced under it

## Step 0 — Detect Platform & Parse Input

### 0.1 Platform Detection

```bash
git remote get-url origin 2>/dev/null
```

| Remote URL contains | Platform | Mode |
|---------------------|----------|------|
| `github.com` | GitHub | Use `gh` CLI for issues, PRs, CI, and reviews |
| Anything else (ADO, GitLab, etc.) or no remote | Non-GitHub | **Local mode** — `.teamwork/` folder for tracking |

**Local mode** setup — create `.teamwork/` at repo root (add to `.gitignore`):

```
.teamwork/
└── <feature-slug>/
    ├── status.json      # this feature's tracking
    └── reviews/
        ├── round-1.md
        └── round-2.md
```

Each feature gets its own directory — no shared state across sessions.

`status.json` (per-feature):
```json
{
  "feature_slug": "<feature-slug>",
  "status": "Backlog|Ready|In progress|In review|Done",
  "prd": "docs/prd/<feature-slug>.md",
  "branch": "<feature-slug>",
  "review_round": 0,
  "created_at": "<ISO timestamp>",
  "updated_at": "<ISO timestamp>"
}
```

### 0.2 Parse Input

| Input | Action |
|-------|--------|
| Feature description (text) | Start from Step 1 |
| Issue number (`#12`, `12`) or feature slug | Resume — find status and jump to the right step |
| Blank | Ask the user what they want to build |

**Collision check:** Before creating a new feature-slug, verify no existing worktree or `.teamwork/<slug>/` directory uses the same name. If collision detected, append a short suffix (e.g., `-v2`).

## Issue Lifecycle

All issues (parent features and subtasks) follow the same 5-status lifecycle:

| Status | Meaning | Who moves here |
|--------|---------|----------------|
| **Backlog** | Proposed work — created by agent, awaiting human approval | Agent creates issue → lands here |
| **Ready** | Approved for development | **Human only** — agent NEVER self-approves |
| **In Progress** | Agent is actively working on it | Agent moves when starting work |
| **In Review** | PR open, awaiting review | Agent moves when PR is ready |
| **Done** | PR merged, work complete | Agent moves on merge |

**Critical rule: Agents only pick work from Ready.** Never scan Backlog for work. The human gates what gets built by promoting items from Backlog → Ready. This is the same workflow as superboss on Discord.

**GitHub mode:** Use a GitHub Project board with these 5 columns. Move items via `gh project item-edit`.

**Local mode:** Track status in `.teamwork/<feature-slug>/status.json` (parent) and `subtasks.json` (subtasks) using the same 5 statuses.

**After creating issues, notify the user** that items are in Backlog and need approval to proceed. Wait for the user to confirm which items should move to Ready before starting any implementation.

## Step 1 — Requirements & Design (DDD)

Follow the Document-Driven Development flow. No code without an approved spec.

```
Idea → Brainstorming → Design Doc → Review Gate → Task Breakdown → Implementation
```

### 1.1 Brainstorming

Engage the user in a focused requirements conversation:

1. Summarize your understanding of the feature
2. Ask clarifying questions — **one at a time**, not a wall of 10. Prefer multiple-choice.
3. Propose 2-3 approaches with trade-offs and your recommendation
4. Challenge scope creep — apply YAGNI. "Do we need this for v1?"
5. Iterate until the user confirms

**Do NOT proceed to PRD until the user explicitly approves the requirements.**

### 1.2 Write PRD

Create `docs/prd/<feature-slug>.md`:

```markdown
# <Feature Title>

## Overview
<!-- 1-2 sentence summary -->

## Motivation
<!-- Why this feature is needed -->

## Requirements
<!-- Numbered list of functional requirements -->

## Acceptance Criteria
<!-- Testable criteria that define "done" -->

## Technical Approach
<!-- Architecture, components, data flow, error handling -->

## Testing Strategy
<!-- What to test and how -->

## Out of Scope
<!-- What this feature intentionally does NOT cover -->
```

Scale each section to complexity — a few sentences if straightforward, detailed if nuanced.

### 1.3 Review Gate

Present the written PRD to the user for review. Do NOT proceed until explicitly approved. If changes requested, revise and re-present.

### 1.4 Task Breakdown

Break the approved PRD into subtasks. Each subtask must be:

- **Completable in one focused run** — if you can't estimate it fitting in one run, split further
- **Sized** — S (< 200 LOC), M (200-500 LOC), L (500+ LOC, consider splitting)
- **Defined** — what files it touches, what the deliverable is
- **Dependency-mapped** — mark which subtasks depend on others, which are independent

Example:
```
1. Router interface + round-robin strategy (S) [independent]
   - New: router.py, strategies/round_robin.py
   - Tests: test_router.py

2. Fallback chains + circuit breaker (M) [depends on 1]
   - New: strategies/fallback.py, circuit_breaker.py
   - Tests: test_fallback.py

3. Config schema + validation (S) [independent]
   - New: config/schema.py, config/validator.py
   - Tests: test_config.py
```

### 1.5 Choose Execution Mode

Based on the task breakdown, choose how to execute:

| Condition | Mode | How |
|-----------|------|-----|
| ≤ 3 subtasks, all sequential | **Solo** | Orchestrator implements everything in one worktree |
| Multiple independent subtasks that can run in parallel | **Parallel** | Orchestrator spawns dev agents, each in its own worktree |

**The user can override this decision.** Always present your recommendation and let the user confirm.

### 1.6 Create Issues / Register Feature

#### Parent Issue

Commit the PRD:

```bash
git add docs/prd/<feature-slug>.md
git commit -m "docs: add PRD for <feature-slug>"
```

**GitHub mode:**
```bash
gh issue create --title "<title>" --body "$(cat docs/prd/<feature-slug>.md)"
```
Add the issue to the GitHub Project — it lands in **Backlog** by default. Record the parent issue number.

**Local mode:** Register in `.teamwork/<feature-slug>/status.json` with status `Backlog`.

#### Subtask Issues

Create a tracked issue for **every subtask** from the breakdown (both solo and parallel modes):

**GitHub mode:**

For each subtask:
```bash
gh issue create --title "<parent-title>: <subtask-title>" \
  --body "$(cat <<'EOF'
Parent: #<parent_issue_number>

## Scope
<subtask spec — files, deliverables, acceptance criteria>

## Size: S|M|L
EOF
)"
```

Then add a checklist to the parent issue body linking all subtasks:
```bash
gh issue edit <parent_issue_number> --body "$(cat <<'EOF'
<original PRD content>

## Subtasks
- [ ] #<subtask_1> — <title>
- [ ] #<subtask_2> — <title>
- [ ] #<subtask_3> — <title>
EOF
)"
```

As each subtask completes, update the parent checklist:
```bash
# Close the subtask issue
gh issue close <subtask_number>
# The checkbox in the parent body auto-tracks via issue state
```

**Local mode:**

Create `.teamwork/<feature-slug>/subtasks.json`:
```json
[
  {
    "id": 1,
    "title": "<subtask title>",
    "status": "Backlog",
    "size": "S|M|L",
    "spec": "<subtask spec>",
    "depends_on": [],
    "branch": null
  }
]
```

Update this file as subtasks progress through the lifecycle (Backlog → Ready → In Progress → In Review → Done).

#### Wait for Human Approval

After creating all issues (parent + subtasks), **notify the user** with a summary:

```
Created parent issue #N and M subtask issues — all in Backlog.
Please review and move the items you'd like me to work on to Ready.
```

**Do NOT start implementation until the user promotes items to Ready** (or explicitly tells you to proceed). This is the human gate — it ensures the user controls what gets built and in what order.

In practice, for a single `/teamwork` session, the user will often approve all subtasks at once. But the gate must exist.

## Step 2 — Implementation

### 2.0 Pick from Ready

Before starting any implementation, check which items are in **Ready** status:

**GitHub mode:** Scan the project board for Ready items.
**Local mode:** Check `subtasks.json` for items with `"status": "Ready"`.

Only work on Ready items. If no items are Ready, wait for the user to promote them.

### 2.1 Execution Mode Branch

Based on the mode chosen in Step 1.5:

- **Solo mode** → proceed to Step 2A
- **Parallel mode** → proceed to Step 2B

---

### Step 2A — Solo Implementation

For small/sequential features. The orchestrator does everything in one worktree.

#### 2A.1 Enter Worktree

Use the `EnterWorktree` tool with `name: "<feature-slug>"`. All work happens in this worktree.

Update status to **In progress**.

#### 2A.2 Implement

Work through Ready subtasks sequentially:

1. Move subtask to **In Progress** (GitHub Project or `subtasks.json`)
2. Read the PRD for context
3. Implement the subtask
4. Run tests, linting, type checking (check CLAUDE.md for commands)
5. Commit with conventional style: `feat(<scope>): <description> (#<subtask_issue>)`
6. Move subtask to **Done**: `gh issue close <subtask_number>` (GitHub mode) or update `subtasks.json` (local mode)
7. Move to next Ready subtask

#### 2A.3 Self-Simplification Pass

Before creating the PR, review every file you changed:

- Can anything be deleted, inlined, or simplified?
- Are there abstractions that earn their complexity?
- Any AI-typical over-engineering? (unnecessary wrappers, premature abstractions, gold-plating)
- Three similar lines is better than a premature abstraction.

Fix anything you find, commit as `refactor: simplify <description>`.

#### 2A.4 Pre-Commit Checklist

Before pushing, verify:
- [ ] Code builds without errors
- [ ] All tests pass
- [ ] No secrets, personal info, or API keys
- [ ] Docs updated if behavior changed
- [ ] Diff self-reviewed as if you were the reviewer

#### 2A.5 Open PR

**GitHub mode:**

```bash
git push -u origin <feature-slug>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<bullet points>

Closes #<issue_number>

## Test Plan
<how to verify>

## PRD
See [docs/prd/<feature-slug>.md](docs/prd/<feature-slug>.md)
EOF
)"
```

**Local mode:**
```bash
git push -u origin <feature-slug>
```
Update `.teamwork/<feature-slug>/status.json` to **In review**.

Then proceed to **Step 3** (CI monitoring).

---

### Step 2B — Parallel Implementation

For large features with independent subtasks. The orchestrator manages, dev agents implement.

#### 2B.1 Setup

1. Use `TaskCreate` to create a task for each subtask from the breakdown. Include the subtask spec, files to touch, and acceptance criteria in the description.
2. Set up dependencies with `TaskUpdate` (`addBlockedBy`) for subtasks that depend on others.
3. Enter a worktree for the main feature branch: `EnterWorktree` with `name: "<feature-slug>"`.
4. Update status to **In progress**.

#### 2B.2 Dispatch Dev Agents

Spawn dev agents using the `Agent` tool with `isolation: "worktree"`. Each agent gets its own isolated worktree — no conflicts between agents.

**Dispatch rules:**
- Launch all independent (unblocked) subtasks in parallel in a **single message**
- When a blocked subtask's dependency completes, dispatch it in the next wave
- One subtask per agent. Don't combine unrelated work.

**Agent prompt template:**
```
You are a dev agent implementing one subtask of a larger feature.

## Your Subtask
{subtask spec from task breakdown}

## Overall Feature Context
{PRD content}

## Project Conventions
{CLAUDE.md contents, if available}

## Deliverables
1. Implement the subtask
2. Write tests
3. Run: {test/lint/type-check commands from CLAUDE.md}
4. Commit with conventional style: feat(<scope>): <description>
5. Run a self-simplification pass before final commit

## Rules
- Do NOT touch files outside your subtask scope
- If you discover a dependency on another subtask, report it — don't implement it
- Commit only your subtask's changes
```

#### 2B.3 Track Progress

As agents complete:

1. Update tasks via `TaskUpdate` to `completed`
2. Close the corresponding subtask issue: `gh issue close <subtask_number>` (GitHub mode) or update `subtasks.json` (local mode)
3. Review each agent's output — check what was committed, whether tests pass
4. Dispatch the next wave of unblocked subtasks
5. If an agent fails or hits a blocker, reassess and either retry or reassign

Use `TaskList` to monitor overall progress.

#### 2B.4 Integrate

Once all subtasks are complete, in the main worktree (`<feature-slug>`):

1. Merge each agent's worktree branch:
   ```bash
   git merge <agent-worktree-branch> --no-ff -m "feat: integrate <subtask>"
   ```
2. Run the full test suite to catch integration issues
3. Fix any merge conflicts or integration bugs
4. Run the self-simplification pass (same as 2A.3)
5. Run the pre-commit checklist (same as 2A.4)

#### 2B.5 Open PR

Same as Step 2A.5. Then proceed to **Step 3** (CI monitoring).

## Step 3 — CI Monitoring (GitHub mode)

After PR creation, monitor CI:

```bash
gh pr checks <pr_number> --watch
```

If CI fails:
1. Read the failure logs: `gh pr checks <pr_number> --json name,state,description`
2. Fix the issue in the worktree
3. Commit and push
4. Re-monitor

Max 3 CI fix attempts. After 3 failures, escalate to the user with the error details.

## Step 4 — Multi-Perspective Code Review

Spawn review agents **in parallel** using the Agent tool. Each agent reviews the PR diff with a specific lens. The diff, the PRD, and the role definition are provided to each agent.

### 4.1 Prepare Review Context

Collect the review material:

```bash
# GitHub mode
gh pr diff <pr_number>

# Local mode
git diff main...<feature-slug>
```

Read the PRD from `docs/prd/<feature-slug>.md`.

### 4.2 Spawn Review Agents

Launch all review agents in a **single message** (parallel execution):

| Agent Name | Role File | Priority |
|-----------|-----------|----------|
| `review-simplicity` | `references/simplicity.md` | **Highest — veto power** |
| `review-engineer` | `references/engineer.md` | High |
| `review-architect` | `references/architect.md` | High |
| `review-product` | `references/product.md` | High |
| `review-tester` | `references/tester.md` | Medium |
| `review-security` | `references/security.md` | Medium |
| `review-syntax` | `references/syntax.md` | Low |

Each agent prompt must include:
1. The full diff
2. The PRD content
3. The role definition from the corresponding reference file
4. Instruction to produce structured findings in the role's output format
5. Instruction to produce a final verdict: `APPROVE` or `REQUEST_CHANGES`

### 4.3 Synthesize Review

Collect all agent findings and synthesize:

1. **Simplicity findings are mandatory fixes** — the simplicity reviewer has veto power
2. Deduplicate findings across reviewers
3. Rank by severity: critical > important > suggestion
4. Drop suggestions that contradict each other (use judgment)

**Verdict rules:**
- Any `critical` finding from any reviewer → `REQUEST_CHANGES`
- Any simplicity `REQUEST_CHANGES` → `REQUEST_CHANGES`
- Otherwise, if majority approves → `APPROVE`

### 4.4 Post Review

**GitHub mode:** Post the synthesized review as a PR review:

```bash
jq -n '{
  body: "<synthesized review>",
  event: "REQUEST_CHANGES|APPROVE"
}' | gh api repos/{owner}/{repo}/pulls/<pr_number>/reviews --method POST --input -
```

**Local mode:** Write to `.teamwork/<feature-slug>/reviews/round-N.md`.

## Step 5 — Review-Fix Loop (Max 3 Rounds)

If the review verdict is `REQUEST_CHANGES`:

1. Fix all findings in the worktree, starting with simplicity and critical items
2. Commit: `fix: address review round N feedback`
3. Push to the PR branch
4. Wait for CI to pass (Step 3)
5. Re-run the multi-perspective review (Step 4)

**Round 3 rule:** If still not approved after round 3, produce a summary of all remaining issues and escalate to the user for a decision. Do NOT continue beyond round 3.

Each review must state: `Review round N/3`.

## Step 6 — Approved & Merge

When the review passes:

1. Post the `APPROVE` review (GitHub mode) or write the final review file (local mode)

### 6.1 Detect Merge Policy

**GitHub mode:** Check if the repo requires human review for merging:

```bash
gh api repos/{owner}/{repo}/branches/main/protection --jq '.required_pull_request_reviews.required_approving_review_count // 0'
```

| Result | Merge policy |
|--------|-------------|
| `0` or API returns 404 (no protection) | **Auto-merge** — orchestrator can merge directly |
| `≥ 1` | **Human review required** — notify user to review and merge |

**Local mode:** Always treat as human-merge (no way to detect protection rules).

### 6.2a Auto-Merge (no human review required)

The orchestrator merges the PR and completes the lifecycle:

```bash
gh pr merge <pr_number> --squash --delete-branch
```

Move all related issues to **Done**. Proceed to Step 7 (cleanup).

### 6.2b Human Review Required

Notify the user:

```
PR #N has passed all automated reviews (3 rounds) and CI is green.
This repo requires human review — please review and merge when ready.
```

Wait for the user to merge. Detect merge via polling or user confirmation:

```bash
gh pr view <pr_number> --json state --jq '.state'
```

Once merged, move all related issues to **Done**. Proceed to Step 7 (cleanup).

## Step 7 — Cleanup

After the PR is merged (auto-merged in 6.2a, or detected/confirmed in 6.2b):

1. Update status to **Done**
2. Use `ExitWorktree` with `action: "remove"` to clean up
3. Report completion

## Rules

- **Merge policy is repo-dependent.** If the repo has no required reviewers, the orchestrator auto-merges after passing review and CI. If the repo requires human review, notify the user and wait.
- **Never commit to main.** All work goes through worktree + PR.
- **Never pick from Backlog.** Only work on items the human has moved to Ready. Agent creates issues in Backlog, human promotes to Ready.
- **Design before code.** No implementation without an approved PRD.
- **Simplicity is mandatory.** Simplicity reviewer has veto power. AI-generated code trends toward over-engineering — actively fight this.
- **Max 3 review rounds.** Escalate to human after round 3.
- **Max 3 CI fix attempts.** Escalate to human after 3 failures.
- **User approval gates:** Requirements approved → PRD approved → issues in Backlog → human promotes to Ready → implementation starts.
- **Handle failures gracefully.** If any `gh` command fails, report the error to the user instead of proceeding blindly.
- **One session, one task.** Each `/teamwork` session handles one feature in one worktree. Parallel features = separate tmux windows or terminal processes (not panes — those are used by agent teams).
- **Notify proactively.** When you create issues, change status, or complete work — tell the user. Don't make them discover state changes by checking the board.
