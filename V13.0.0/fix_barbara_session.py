"""
Fix the current session to include Barbara in the preview
"""
import json
import sys
from pathlib import Path

sys.path.append('app')

from api.server import _build_preview_single_file

# Find latest session
sessions = list(Path('out/sessions').glob('*/meta.json'))
if not sessions:
    print("❌ No sessions found")
    sys.exit(1)

latest_session = max(sessions, key=lambda p: p.stat().st_mtime)
session_dir = latest_session.parent
session_id = session_dir.name

print(f"📁 Latest session: {session_id}")

# Load meta.json
meta = json.loads(latest_session.read_text(encoding='utf-8'))
print(f"📄 Current ABZ file: {meta.get('abz')}")
print(f"📊 Current preview has {len(meta.get('preview', {}))} employees")

# Get ABZ file path
abz_filename = meta.get('abz')
if not abz_filename:
    print("❌ No ABZ file in session")
    sys.exit(1)

abz_path = session_dir / abz_filename
if not abz_path.exists():
    print(f"❌ ABZ file not found: {abz_path}")
    sys.exit(1)

print(f"\n🔄 Rebuilding preview from: {abz_path}")

# Rebuild preview
anfin_filename = meta.get('anfin')
anfin_path = session_dir / anfin_filename if anfin_filename else None

preview = _build_preview_single_file(abz_path, anfin_path)

print(f"\n✅ New preview has {len(preview)} employees")
print(f"📋 Employees: {list(preview.keys())}")

# Check if Barbara is in the new preview
if 'Bárbara Chapeta Mattoso Franco' in preview:
    barbara = preview['Bárbara Chapeta Mattoso Franco']
    print(f"\n✅ Barbara found in preview!")
    print(f"   Items: {barbara.get('items', [])}")
else:
    print(f"\n❌ Barbara NOT in preview")

# Update meta.json
meta['preview'] = preview
latest_session.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')

print(f"\n💾 Session updated: {session_id}")
print(f"🌐 Refresh the browser to see the changes")

