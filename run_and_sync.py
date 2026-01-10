#!/usr/bin/env python3
"""
同步 result/nodetotal.txt 到 github.com/yafeisun/v2ray-nodes 的 files/node.txt

说明：
- 从 ./result/nodetotal.txt 读取
- 使用环境变量 TARGET_PAT（在 Actions secrets 中设置）来推送目标仓库
- 如果没有设置 TARGET_PAT，仅做本地检查并退出

注意：脚本会尽量避免把 PAT 原文打印到日志中（会把 PAT 用 *** 掩码）。
"""
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# -------- configuration --------
SRC_PATH = Path("result") / "nodetotal.txt"
TARGET_REPO = "yafeisun/v2ray-nodes"
TARGET_REL_PATH = "files/node.txt"
TARGET_BRANCH = "main"    # 如果目标分支不是 main，请改为实际分支名
GIT_USER_NAME = "github-actions[bot]"
GIT_USER_EMAIL = "github-actions[bot]@users.noreply.github.com"
# --------------------------------

def run(cmd, cwd=None, check=True):
    # 安全打印：如果命令中包含 PAT，则用 *** 掩码
    pat = os.environ.get("TARGET_PAT")
    safe_cmd = []
    for part in cmd:
        if pat and pat in part:
            safe_cmd.append(part.replace(pat, "***"))
        else:
            safe_cmd.append(part)
    print("+", " ".join(safe_cmd))
    res = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if res.stdout:
        print(res.stdout, end="")
    if res.stderr:
        print(res.stderr, end="", file=sys.stderr)
    if check and res.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(safe_cmd)} (code={res.returncode})")
    return res

def push_to_target(nodetotal_path: Path):
    if not nodetotal_path.exists():
        print(f"Source file not found: {nodetotal_path}", file=sys.stderr)
        return 1

    pat = os.environ.get("TARGET_PAT")
    if not pat:
        print("Environment variable TARGET_PAT not set — skipping remote push.")
        print("If you want automatic push, set TARGET_PAT (PAT with repo/public_repo permissions).")
        return 0

    tmpdir = tempfile.mkdtemp(prefix="v2raynodes_sync_")
    try:
        clone_url = f"https://{pat}@github.com/{TARGET_REPO}.git"
        print("Cloning target repo (PAT will be masked in logs)...")
        res = subprocess.run(["git", "clone", "--depth", "1", "--branch", TARGET_BRANCH, clone_url, tmpdir],
                             text=True, capture_output=True)
        if res.stdout:
            print(res.stdout, end="")
        if res.stderr:
            print(res.stderr, end="", file=sys.stderr)
        if res.returncode != 0:
            raise RuntimeError("git clone failed")

        target_file = Path(tmpdir) / TARGET_REL_PATH
        target_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(nodetotal_path, target_file)
        print(f"Copied {nodetotal_path} -> {target_file}")

        run(["git", "config", "user.name", GIT_USER_NAME], cwd=tmpdir)
        run(["git", "config", "user.email", GIT_USER_EMAIL], cwd=tmpdir)

        run(["git", "add", TARGET_REL_PATH], cwd=tmpdir)
        status = run(["git", "status", "--porcelain"], cwd=tmpdir, check=False)
        if not status.stdout.strip():
            print("No changes to commit in target repo.")
            return 0

        run(["git", "commit", "-m", "Update node.txt from v2raynode [skip ci]"], cwd=tmpdir)
        run(["git", "push", "origin", f"HEAD:{TARGET_BRANCH}"], cwd=tmpdir)
        print("Pushed changes to target repository.")
        return 0
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

def main():
    exit_code = push_to_target(SRC_PATH)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()