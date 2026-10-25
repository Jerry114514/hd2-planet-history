# -*- coding: utf-8 -*-
"""星球历史记录器：抓主站 data.json → 追加每颗星球的人数/血量/归属快照

数据文件：
  history.json  — 全部星球的滚动窗口（7 天），紧凑数组格式
  格式：{"_meta": {...}, "planets": {"<idx>": [[ms, players, health, owner_id], ...], ...}}

去重：与该星球最后一条快照的 (players, health, owner) 完全相同则跳过（不产生空转 commit）。
"""
import json, os, time, urllib.request

DATA_URL = "https://jerry114514.github.io/HD2-Galatic_war-Map/data.json"
HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history.json")
RETENTION_MS = 7 * 86400 * 1000  # 7 天
OWNER_ID = {"Humans": 1, "Terminids": 2, "Automaton": 3, "Automatons": 3, "Illuminate": 4}

def fetch(url):
    with urllib.request.urlopen(url, timeout=45) as r:
        return json.load(r)

def main():
    now_ms = int(time.time() * 1000)
    data = fetch(DATA_URL)
    fetched_at = data.get("fetchedAt") or ""
    planets = data.get("planets") or []

    hist = {}
    if os.path.exists(HISTORY_FILE):
        try:
            hist = json.load(open(HISTORY_FILE, encoding="utf-8"))
        except Exception:
            hist = {}
    snapshots = hist.get("planets") or {}
    changed = False

    for p in planets:
        idx = str(p.get("index"))
        if not idx:
            continue
        players = int(p.get("players") or 0)
        health = int(p.get("health") or 0)
        owner = OWNER_ID.get(str(p.get("currentOwner") or ""), 0)
        entries = snapshots.get(idx) or []
        # 去重：与最后一条相同则跳过
        if entries and entries[-1][1] == players and entries[-1][2] == health and entries[-1][3] == owner:
            continue
        entries.append([now_ms, players, health, owner])
        # 截断到保留窗口
        cutoff = now_ms - RETENTION_MS
        entries = [e for e in entries if e[0] >= cutoff]
        snapshots[idx] = entries
        changed = True

    if changed:
        hist["_meta"] = {
            "desc": "每颗星球的人数/血量/归属历史（5 分钟采样，7 天滚动窗口，无变化不记录）",
            "source": DATA_URL,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "fetched_at": fetched_at,
            "format": "[epoch_ms, players, health, owner_id(1=SE 2=虫 3=机 4=光)]",
            "retention_days": 7,
            "planets_count": len(snapshots),
        }
        hist["planets"] = snapshots
        tmp = HISTORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, HISTORY_FILE)
        print(f"recorded {len(snapshots)} planets, file size: {os.path.getsize(HISTORY_FILE)}")
    else:
        print("no changes, skip commit")

if __name__ == "__main__":
    main()
