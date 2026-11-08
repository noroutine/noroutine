#!/usr/bin/env python3
"""Sync ohmycv_data.json markdown fields with plain .md files in cv/.

    cv/sync.py extract   # json -> cv/*.md  (edit these normally)
    cv/sync.py pack      # cv/*.md -> json  (before importing back into ohmycv)

Only the `markdown` field of each entry is touched; css/styles/ids are left alone.
"""
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "ohmycv_data.json"
CV_DIR = ROOT / "cv"


def slug(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def extract():
    data = json.loads(JSON_PATH.read_text())["data"]
    for entry_id, entry in data.items():
        path = CV_DIR / f"{slug(entry['name'])}.md"
        path.write_text(entry["markdown"])
        print(f"wrote {path.relative_to(ROOT)} <- {entry['name']} ({entry_id})")


def pack():
    doc = json.loads(JSON_PATH.read_text())
    data = doc["data"]
    by_slug = {slug(e["name"]): entry_id for entry_id, e in data.items()}

    changed = False
    for path in sorted(CV_DIR.glob("*.md")):
        key = path.stem
        entry_id = by_slug.get(key)
        if entry_id is None:
            print(f"skip {path.name}: no matching entry (slug {key!r} not found)")
            continue
        new_markdown = path.read_text()
        if data[entry_id]["markdown"] != new_markdown:
            data[entry_id]["markdown"] = new_markdown
            data[entry_id]["updated_at"] = str(int(time.time() * 1000))
            changed = True
            print(f"updated {data[entry_id]['name']} ({entry_id}) <- {path.relative_to(ROOT)}")

    if changed:
        JSON_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        print("ohmycv_data.json updated")
    else:
        print("no changes")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("extract", "pack"):
        print(__doc__)
        sys.exit(1)
    {"extract": extract, "pack": pack}[sys.argv[1]]()


if __name__ == "__main__":
    main()
