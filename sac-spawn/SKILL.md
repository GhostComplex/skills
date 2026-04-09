---
name: sac-spawn
description: Spawn a new agent for the laughingman Discord bot and bind it to a specific channel. Maps the shared laughingman bot to different agent personas per channel. NOT for general agent creation — only for laughingman channel-specific agent mappings. Triggers ONLY on "sac-spawn", "sac spawn", or similar variations. Input format is agent name + channel ID.
---

# SAC Spawn

Spawn a new agent-channel binding for the `laughingman` Discord bot — maps a specific Discord channel to a dedicated agent persona.

## Required Inputs

- **Agent ID** — lowercase, hyphens allowed (e.g. `gtbc`, `ops-bot`)
- **Channel ID** — Discord channel ID (e.g. `1484372470306963547`)

## Workflow

### Step 1: Create the agent

```bash
openclaw agents add <agent-id> --workspace ~/.openclaw/workspace-<agent-id> --non-interactive
```

The `--non-interactive` flag is **required** — without it the CLI prompts for input and blocks in non-TTY contexts. `--workspace` is mandatory when using `--non-interactive`.

Creates the agent with workspace at `~/.openclaw/workspace-<agent-id>` and state at `~/.openclaw/agents/<agent-id>/`.

### Step 2: Remove .git from workspace

The agent workspace is part of a mono-repo backup. Remove the auto-generated `.git` directory to avoid nested repos:

```bash
rm -rf ~/.openclaw/workspace-<agent-id>/.git
```

### Step 3: Add peer binding

The CLI `openclaw agents bind` does not support peer-level bindings. Run the bundled script to edit `~/.openclaw/openclaw.json`:

```bash
python3 <skill-dir>/scripts/add_binding.py <agent-id> <discord-channel-id>
```

The script adds a peer binding to the `bindings` array:
```json
{
  "agentId": "<agent-id>",
  "match": {
    "channel": "discord",
    "accountId": "laughingman",
    "peer": { "kind": "group", "id": "<channel-id>" }
  }
}
```
Inserted before any channel-wide `laughingman` fallback (peer bindings must come first). Duplicates are detected and skipped.

Options:
- `--account <id>` — override account (default: `laughingman`)
- `--channel <type>` — override channel type (default: `discord`)
- `--config <path>` — override config path

### Step 4: Restart gateway

```bash
openclaw gateway restart
```

## Teardown

To remove an agent created by sac-spawn:

```bash
openclaw agents delete <agent-id> --force
openclaw gateway restart
```

This removes the agent config, bindings, workspace (`~/.openclaw/workspace-<agent-id>`), and state (`~/.openclaw/agents/<agent-id>/`).

## Notes

- Peer bindings are more specific than channel-wide bindings and always win in routing.
- The script detects duplicates and skips if the binding already exists.
- The agent workspace is created with default bootstrap files (AGENTS.md, SOUL.md, etc.) — customize after creation.
- To bind additional channels to the same agent, run the script again with a different channel ID.
