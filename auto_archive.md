
1. Python 走 Focalboard **REST API**：`login → list teams → list boards → 按 title 找到 board_id → export board archive`
2. 在 **10.21.13.51** 上用 **cron** 定时跑脚本，把 `.boardarchive` 写到 `/home/uat/opt/archive_boards/`

这些 API 路径在 v2 里就是 `/api/v2/...`（standalone/personal server）。([Michał Karol][1])

---

## 1) Python 脚本：按 title 找 board 并导出 archive

保存为：`/home/uat/bin/export_board_by_title.py`

```python
#!/usr/bin/env python3
import os
import re
import sys
import datetime as dt
import requests

BASE_URL = os.environ.get("FOCALBOARD_BASE_URL", "").rstrip("/")
USERNAME = os.environ.get("FOCALBOARD_USERNAME", "")
PASSWORD = os.environ.get("FOCALBOARD_PASSWORD", "")
BOARD_TITLE = os.environ.get("FOCALBOARD_BOARD_TITLE", "")  
OUT_DIR = os.environ.get("FOCALBOARD_OUT_DIR", "/home/uat/opt/archive_boards")
TIMEOUT = int(os.environ.get("FOCALBOARD_TIMEOUT", "30"))

def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)

def safe_name(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\\/:\*\?\"<>\|\s]+", "_", s)  # 适配文件名
    return s[:120] if len(s) > 120 else s

def main():
    if not (BASE_URL and USERNAME and PASSWORD and BOARD_TITLE):
        die("Missing env vars: FOCALBOARD_BASE_URL/USERNAME/PASSWORD/BOARD_TITLE")

    os.makedirs(OUT_DIR, exist_ok=True)
    s = requests.Session()

    # 1) login -> token  (POST /api/v2/login) :contentReference[oaicite:1]{index=1}
    r = s.post(f"{BASE_URL}/api/v2/login",
               json={"username": USERNAME, "password": PASSWORD},
               timeout=TIMEOUT)
    if r.status_code != 200:
        die(f"Login failed: {r.status_code} {r.text}")

    token = r.json().get("token")
    if not token:
        die(f"No token in login response: keys={list(r.json().keys())}")

    s.headers.update({"Authorization": f"Bearer {token}"})

    # 2) list teams: GET /api/v2/teams :contentReference[oaicite:2]{index=2}
    r = s.get(f"{BASE_URL}/api/v2/teams", timeout=TIMEOUT)
    if r.status_code != 200:
        die(f"List teams failed: {r.status_code} {r.text}")
    teams = r.json()

    matches = []
    for t in teams:
        team_id = t.get("id") or t.get("ID")
        if not team_id:
            continue

        # 3) list boards in team: GET /api/v2/teams/{team_id}/boards :contentReference[oaicite:3]{index=3}
        rb = s.get(f"{BASE_URL}/api/v2/teams/{team_id}/boards", timeout=TIMEOUT)
        if rb.status_code != 200:
            continue
        boards = rb.json()

        for b in boards:
            title = (b.get("title") or b.get("Title") or "").strip()
            if title == BOARD_TITLE.strip():
                board_id = b.get("id") or b.get("ID")
                matches.append((team_id, board_id, title))

    if not matches:
        die(f'Board not found by title: "{BOARD_TITLE}" (searched all teams)')

    if len(matches) > 1:
        # 优先第一个
        print("WARNING: multiple boards with same title found, using the first one:", file=sys.stderr)
        for m in matches:
            print(f"  team_id={m[0]} board_id={m[1]} title={m[2]}", file=sys.stderr)

    team_id, board_id, title = matches[0]

    # 4) export board archive: GET /api/v2/boards/{board_id}/archive/export :contentReference[oaicite:4]{index=4}
    rexp = s.get(f"{BASE_URL}/api/v2/boards/{board_id}/archive/export", timeout=TIMEOUT)
    if rexp.status_code != 200:
        die(f"Export board failed: {rexp.status_code} {rexp.text}")

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    fn = f"{safe_name(title)}__board-{board_id}__{ts}.boardarchive"
    out_path = os.path.join(OUT_DIR, fn)
    with open(out_path, "wb") as f:
        f.write(rexp.content)

    print(f"OK: exported {title} (team={team_id}, board={board_id}) -> {out_path}")

if __name__ == "__main__":
    main()
```

给权限：

```bash
chmod +x /home/uat/bin/export_board_by_title.py
```

---

## 2) 环境变量文件（把你给的信息直接写进去）

`/home/uat/.focalboard_archive.env`

```bash
FOCALBOARD_BASE_URL=http://{}
FOCALBOARD_USERNAME=账号
FOCALBOARD_PASSWORD=密码
FOCALBOARD_BOARD_TITLE=看板
FOCALBOARD_OUT_DIR=/home/uat/opt/archive_boards
FOCALBOARD_TIMEOUT=30
```

权限（很重要）：

```bash
chmod 600 /home/uat/.focalboard_archive.env
mkdir -p /home/uat/opt/archive_boards
```

---

## 3) cron：每周二 17:00 自动导出

```bash
crontab -e
```

加入：

```cron
0 17 * * 2 . /home/uat/.focalboard_archive.env; /usr/bin/python3 /home/uat/bin/export_board_by_title.py >> /home/uat/opt/archive_boards/archive.log 2>&1
```

---

