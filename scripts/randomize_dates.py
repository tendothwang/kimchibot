"""Randomize post publish times to look like a human publishing pattern.

For each post:
- Keep the existing calendar date.
- Generate a deterministic-but-natural KST time between 07:30 and 23:45,
  derived from the filename so re-runs are idempotent.
- When multiple posts share a date, space them out and stagger minutes/seconds
  so they don't all sit at round-hour boundaries.
- Write back as RFC3339 with +09:00 so Hugo treats them as KST without UTC drift.
"""

from __future__ import annotations
import hashlib
import os
import random
import re
from collections import defaultdict

POSTS_DIR = r"D:\workspace\kimchibot\content\posts"
DATE_RE = re.compile(r"^date:\s*(\S+)\s*$", re.MULTILINE)


def seeded_rng(name: str, salt: int = 0) -> random.Random:
    h = hashlib.md5(f"{name}:{salt}".encode()).hexdigest()
    return random.Random(int(h, 16))


def collect():
    posts = []
    for fname in sorted(os.listdir(POSTS_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(POSTS_DIR, fname)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        m = DATE_RE.search(content)
        if not m:
            continue
        raw = m.group(1)
        cal = raw.split("T")[0]
        posts.append({
            "file": fname,
            "path": path,
            "content": content,
            "raw_date": raw,
            "cal_date": cal,
        })
    return posts


def assign_times(posts):
    """Assign a single new HH:MM:SS per post, spaced inside the same day."""
    START = 7 * 60 + 30   # 07:30
    END = 23 * 60 + 45    # 23:45

    by_date = defaultdict(list)
    for p in posts:
        by_date[p["cal_date"]].append(p)

    for cal_date, group in by_date.items():
        # Deterministic ordering inside a day, hash-based so it's not alphabetical
        group.sort(key=lambda p: hashlib.md5(p["file"].encode()).hexdigest())
        n = len(group)
        span = END - START
        slot = span // max(n, 1)

        for i, p in enumerate(group):
            rng = seeded_rng(p["file"])
            base = START + i * slot
            if n == 1:
                total_min = rng.randint(START, END)
            else:
                jitter_max = max(min(slot // 3, 45), 5)
                total_min = base + rng.randint(-jitter_max, jitter_max)
                total_min = max(START, min(END, total_min))
            secs = rng.randint(0, 59)
            hh = total_min // 60
            mm = total_min % 60
            p["new_date"] = f"{cal_date}T{hh:02d}:{mm:02d}:{secs:02d}+09:00"


def apply(posts):
    changed = 0
    for p in posts:
        new_line = f"date: {p['new_date']}"
        new_content = DATE_RE.sub(new_line, p["content"], count=1)
        if new_content != p["content"]:
            with open(p["path"], "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new_content)
            changed += 1
        print(f"{p['file']:75s}  {p['raw_date']:30s} -> {p['new_date']}")
    print(f"\nupdated {changed}/{len(posts)} files")


if __name__ == "__main__":
    posts = collect()
    assign_times(posts)
    apply(posts)
