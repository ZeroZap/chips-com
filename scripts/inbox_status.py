#!/usr/bin/env python3
"""Report the _Inbox backlog: pending candidates, age, protocol and status."""

import argparse
import collections
import datetime
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
INBOX = ROOT / "_Inbox"
PROCESSED = INBOX / "已处理"
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---", re.S)
STATUS_RE = re.compile(r"^status:\s*([A-Za-z_-]+)", re.M)


def read_meta(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    created = None
    match = DATE_RE.search(path.stem)
    if match:
        try:
            created = datetime.date.fromisoformat(match.group(1))
        except ValueError:
            pass
    status = "pending"
    frontmatter = FM_RE.match(text)
    if frontmatter:
        status_match = STATUS_RE.search(frontmatter.group(1))
        if status_match:
            status = status_match.group(1).lower()
    protocol = DATE_RE.sub("", path.stem)
    protocol = re.sub(r"-*candidates$", "", protocol).strip("-") or path.stem
    return {"path": path, "created": created, "status": status, "protocol": protocol}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        help="age threshold for stale candidates (default: 30)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help="number of stale candidates to list (default: 15)",
    )
    args = parser.parse_args()

    today = datetime.date.today()
    pending = [
        read_meta(p) for p in sorted(INBOX.glob("*.md")) if p.name != "README.md"
    ]
    archived = [read_meta(p) for p in sorted(PROCESSED.glob("*.md"))]

    stale = [
        x
        for x in pending
        if x["created"] and (today - x["created"]).days > args.stale_days
    ]
    unmarked = [x for x in pending if x["status"] == "pending"]
    undated = [x for x in pending if not x["created"]]

    by_protocol = collections.defaultdict(list)
    for item in pending:
        by_protocol[item["protocol"]].append(item)

    print("inbox status @ %s" % today.isoformat())
    print(
        "pending: %d | stale >%dd: %d | unmarked: %d | undated: %d"
        % (len(pending), args.stale_days, len(stale), len(unmarked), len(undated))
    )
    print("archived: %d" % len(archived))
    print("\nby protocol:")
    for protocol, items in sorted(
        by_protocol.items(), key=lambda kv: (-len(kv[1]), kv[0])
    ):
        dates = [x["created"] for x in items if x["created"]]
        oldest = min(dates).isoformat() if dates else "?"
        print("  %-24s %2d  oldest %s" % (protocol, len(items), oldest))

    if stale:
        print("\nstale candidates (oldest first):")
        for item in sorted(stale, key=lambda x: x["created"])[: args.limit]:
            age = (today - item["created"]).days
            print(
                "  %3dd  %-28s %s  [%s]"
                % (age, item["path"].name, item["created"], item["status"])
            )
        if len(stale) > args.limit:
            print("  ... %d more" % (len(stale) - args.limit))

    if undated:
        print("\nundated candidates:")
        for item in undated[: args.limit]:
            print("  " + item["path"].name)


if __name__ == "__main__":
    main()
