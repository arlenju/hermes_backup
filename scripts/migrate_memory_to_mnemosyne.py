#!/usr/bin/env python3
"""Migrate old MEMORY.md and USER.md entries to Mnemosyne database."""
import os
import sys

# Add venv site-packages to path
venv_path = os.path.expanduser("~/.hermes/hermes-agent/venv/lib/python3.11/site-packages")
sys.path.insert(0, venv_path)

from mnemosyne import remember

# Read old memory files
hermes_home = os.path.expanduser("~/.hermes")
memories_file = os.path.join(hermes_home, "memories", "MEMORY.md")
user_file = os.path.join(hermes_home, "memories", "USER.md")

# Trigger DB creation by calling remember once
remember("__init__", importance=0.1)

# Find DB path
from mnemosyne.core.memory import _default_db_path
db_path = _default_db_path()
print(f"✅ Mnemosyne initialized")
print(f"📁 DB location: {db_path}")

def parse_entries(filepath):
    """Parse entries separated by §"""
    with open(filepath, 'r') as f:
        content = f.read().strip()
    entries = [e.strip() for e in content.split('§') if e.strip()]
    return entries

# Migrate MEMORY.md entries
print("\n--- Migrating MEMORY.md ---")
memory_entries = parse_entries(memories_file)
for i, entry in enumerate(memory_entries):
    remember(entry, importance=0.8, scope="hermes_memory")
    print(f"  [{i+1}/{len(memory_entries)}] ✅ {entry[:60]}...")

# Migrate USER.md entries
print("\n--- Migrating USER.md ---")
user_entries = parse_entries(user_file)
for i, entry in enumerate(user_entries):
    remember(entry, importance=0.9, scope="hermes_user_profile")
    print(f"  [{i+1}/{len(user_entries)}] ✅ {entry[:60]}...")

# Verify
print(f"\n--- Verification ---")
from mnemosyne import recall
all_results = recall("hermes_memory")
print(f"📊 Episodic memory entries: {len(all_results) if isinstance(all_results, list) else all_results}")

print(f"\n✅ Migration complete!")
print(f"💾 DB: {db_path}")
print(f"📏 Size: {os.path.getsize(db_path)} bytes")
