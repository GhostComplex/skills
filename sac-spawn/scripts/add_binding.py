#!/usr/bin/env python3
"""Add a peer binding for a new agent in openclaw.json.

Usage:
    python3 add_binding.py <agent-id> <discord-channel-id> [--account <account>] [--channel <channel>] [--config <path>]

Defaults:
    --account  laughingman
    --channel  discord
    --config   ~/.openclaw/openclaw.json
"""

import argparse
import json
import os
import sys


def add_peer_binding(config, agent_id, channel_id, account, channel):
    """Add peer binding to bindings array. Returns True if added, False if duplicate."""
    bindings = config.setdefault("bindings", [])

    # Check for duplicate
    for b in bindings:
        match = b.get("match", {})
        peer = match.get("peer", {})
        if (
            b.get("agentId") == agent_id
            and match.get("channel") == channel
            and match.get("accountId") == account
            and peer.get("id") == channel_id
        ):
            print(f"Binding already exists: {agent_id} -> {channel}:{account} peer {channel_id}")
            return False

    new_binding = {
        "agentId": agent_id,
        "match": {
            "channel": channel,
            "accountId": account,
            "peer": {
                "kind": "group",
                "id": channel_id,
            },
        },
    }

    # Insert peer bindings before any channel-wide fallback for the same account
    insert_idx = len(bindings)
    for i, b in enumerate(bindings):
        match = b.get("match", {})
        if (
            match.get("channel") == channel
            and match.get("accountId") == account
            and "peer" not in match
        ):
            insert_idx = i
            break

    bindings.insert(insert_idx, new_binding)
    print(f"Added binding: {agent_id} -> {channel}:{account} peer {channel_id} (index {insert_idx})")
    return True


def main():
    parser = argparse.ArgumentParser(description="Add peer binding to openclaw.json")
    parser.add_argument("agent_id", help="Agent ID to bind")
    parser.add_argument("channel_id", help="Discord channel ID to bind to")
    parser.add_argument("--account", default="laughingman", help="Channel account ID (default: laughingman)")
    parser.add_argument("--channel", default="discord", help="Channel type (default: discord)")
    parser.add_argument("--config", default=os.path.expanduser("~/.openclaw/openclaw.json"), help="Config file path")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Config file not found at {args.config}", file=sys.stderr)
        sys.exit(1)

    with open(args.config, "r") as f:
        config = json.load(f)

    if add_peer_binding(config, args.agent_id, args.channel_id, args.account, args.channel):
        with open(args.config, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Config updated: {args.config}")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()
