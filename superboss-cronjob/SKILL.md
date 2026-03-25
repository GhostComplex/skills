---
name: superboss-cronjob
description: Project progress monitor for Discord channels. Creates, enables, and disables a recurring cron job that reads recent channel messages via sessions_history, evaluates project status, and pings the right people when things are blocked. Use when user asks to monitor a project channel, set up project tracking, enable/disable project monitoring, or mentions "superboss-cronjob".
---

# Project Monitor

Per-channel cron job that reads recent Discord messages, evaluates project progress, and reports idle or blocked (with @-mentions).

## Create

Resolve from context:
- `CHANNEL_ID` — from current chat (`channel:<id>`) or user-specified
- `AGENT` — agent id that owns the channel session AND runs the cron
- `ACCOUNT` — from inbound context `account_id`

Session key pattern: `agent:AGENT:discord:channel:CHANNEL_ID`

Cron message template (substitute values):

```
You are monitoring project progress.

Step 1: Call sessions_history with sessionKey="agent:AGENT:discord:channel:CHANNEL_ID" and limit=25 to read the latest messages.

Step 2: ALWAYS reply with a status report. Do NOT reply NO_REPLY.
- Current status (idle/blocked)
- If blocked: who needs to act and on what (use <@DISCORD_ID> mention format)
- If idle: brief summary of recent progress

Be concise and actionable.
```

```bash
openclaw cron add \
  --name "superboss-CHANNEL_ID" \
  --description "Project monitor for channel:CHANNEL_ID" \
  --agent AGENT \
  --every 20m \
  --tz Asia/Shanghai \
  --announce \
  --channel discord \
  --to "channel:CHANNEL_ID" \
  --account ACCOUNT \
  --timeout 60000 \
  --message '<substituted cron message>'
```

Always include `--channel discord` — omitting it causes delivery failures.

## Enable / Disable / Remove

Look up `JOB_ID` via `openclaw cron list --json`, match by name `superboss-CHANNEL_ID`.

```bash
openclaw cron enable "JOB_ID"
openclaw cron disable "JOB_ID"
openclaw cron run "JOB_ID"       # immediate trigger
openclaw cron rm "JOB_ID"
```

## Conventions

- One monitor per channel, named `superboss-<CHANNEL_ID>`.
- Runs in isolated session. Reads messages via `sessions_history` — not `openclaw message read` or Discord API (those don't work in isolated sessions).
