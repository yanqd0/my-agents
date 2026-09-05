#!/usr/bin/env python3
"""Install this project's content to a target agent host.

Multi-host source project. Currently pi is the supported target; dsh and other
hosts (codex/opencode) are added later behind the same --target contract.

For each host this project provides two kinds of installable content:
  - skills : 通用 Agent Skills，软链到该宿主共享的 skills 目录
              (pi 读 ~/.agents/skills，递归发现含 SKILL.md 的目录)
  - settings: settings/<host>/*.json deep-merge 到该宿主的 settings 文件
              (pi -> ~/.pi/agent/settings.json)

`_` 前缀的 settings 文件默认跳过安装，可用 --force 显式启用。
"""

import argparse
import json
import os
import sys
from pathlib import Path

HOME = Path.home()

# ── per-host layout ──────────────────────────────────────────────────────
# src 目录相对本文件；dest 为安装目标（可为 None=该 host 不装此项）
HOSTS = {
    "pi": {
        "name": "pi",
        # skills: 软链 skills/* -> <shared skills dir>
        "skills_src": "skills",
        "skills_dest": HOME / ".agents" / "skills",
        # settings: deep-merge settings/pi/*.json -> settings file
        "settings_src": "settings/pi",
        "settings_dest": HOME / ".pi" / "agent" / "settings.json",
    },
    # dsh/codex/opencode: 0.2.0+ 在此补宿主布局
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent


# ── skills（软链目录） ───────────────────────────────────────────────────
def _symlink_items(src_dir: Path, dst_dir: Path, dry_run: bool) -> int:
    """软链 src_dir 下的顶层项（目录/SKILL 目录）到 dst_dir。

    清理失效软链；跳过点前缀。返回安装/修复计数。
    """
    if not src_dir.is_dir():
        print(f"  warn: 源目录不存在: {src_dir}")
        return 0
    dst_dir.mkdir(parents=True, exist_ok=True)

    installed = 0
    for src in sorted(p for p in src_dir.iterdir() if p.name != ".gitkeep"):
        if src.name.startswith("."):
            continue
        dst = dst_dir / src.name
        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                print(f"  skip   : {dst.name} (correct)")
                continue
            print(f"{'[dry]  fix   : ' if dry_run else '  fix   : '}{dst.name} -> {src}")
            if not dry_run:
                dst.unlink()
        elif dst.exists():
            print(f"  skip   : {dst.name} (existing non-link file)")
            continue
        else:
            print(f"{'[dry]  install: ' if dry_run else '  install: '}{dst.name}")
        if not dry_run:
            dst.symlink_to(src)
        installed += 1

    # 清理失效软链（源被删除）
    for dst in sorted(dst_dir.iterdir()):
        if dst.is_symlink() and not dst.exists():
            print(f"{'[dry]  cleanup: ' if dry_run else '  cleanup: '}{dst.name} (broken)")
            if not dry_run:
                dst.unlink()
    return installed


def _unlink_items(src_dir: Path, dst_dir: Path, dry_run: bool) -> int:
    """移除指向 src_dir 下本项目的软链。"""
    if not dst_dir.is_dir():
        return 0
    removed = 0
    for dst in sorted(dst_dir.iterdir()):
        if dst.is_symlink() and dst.resolve().is_relative_to(repo_root()):
            print(f"{'[dry]  remove : ' if dry_run else '  remove : '}{dst.name}")
            if not dry_run:
                dst.unlink()
            removed += 1
    return removed


# ── settings（deep-merge） ───────────────────────────────────────────────
def _deep_merge(base: dict, overlay: dict, force: bool = False) -> None:
    """把 overlay 合入 base。标量仅当 base 缺失才写入，除非 force。"""
    for key, value in overlay.items():
        if key in base:
            if isinstance(base[key], dict) and isinstance(value, dict):
                _deep_merge(base[key], value, force)
            elif force:
                base[key] = value
            # else: 保留用户已有值（默认不覆盖）
        else:
            base[key] = value


def _deep_revert(base: dict, overlay: dict) -> None:
    """移除 base 中与 overlay 匹配的键（递归 dict）。"""
    for key, value in overlay.items():
        if key not in base:
            continue
        if isinstance(base[key], dict) and isinstance(value, dict):
            _deep_revert(base[key], value)
            if not base[key]:
                del base[key]
        elif base[key] == value:
            del base[key]


def _install_settings(settings_dir: Path, dst_path: Path,
                      force: bool, dry_run: bool) -> int:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    base = json.loads(dst_path.read_text()) if dst_path.exists() else {}

    installed = 0
    for src in sorted(settings_dir.glob("*.json")):
        if src.name.startswith("_") and not force:
            print(f"  skip   : {src.name} (internal, use --force)")
            continue
        overlay = json.loads(src.read_text())
        before = json.dumps(base, sort_keys=True, ensure_ascii=False)
        _deep_merge(base, overlay, force=force)
        after = json.dumps(base, sort_keys=True, ensure_ascii=False)
        tag = "force" if force else "install"
        if before != after:
            print(f"{'[dry]  ' if dry_run else '  '}{tag}: {src.name}")
            installed += 1
        else:
            print(f"  skip   : {src.name} (up to date)")

    if installed and not dry_run:
        dst_path.write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n")
    return installed


def _revert_settings(settings_dir: Path, dst_path: Path,
                     force: bool, dry_run: bool) -> int:
    if not dst_path.exists():
        print(f"  settings 文件不存在: {dst_path}")
        return 0
    base = json.loads(dst_path.read_text())
    reverted = 0
    for src in sorted(settings_dir.glob("*.json")):
        if src.name.startswith("_") and not force:
            continue
        overlay = json.loads(src.read_text())
        before = json.dumps(base, sort_keys=True, ensure_ascii=False)
        _deep_revert(base, overlay)
        after = json.dumps(base, sort_keys=True, ensure_ascii=False)
        if before != after:
            print(f"{'[dry]  revert : ' if dry_run else '  revert : '}{src.name}")
            reverted += 1
        else:
            print(f"  skip   : {src.name} (no match)")
    if reverted and not dry_run:
        dst_path.write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n")
    return reverted


# ── actions ──────────────────────────────────────────────────────────────
def install(host: dict, dry_run: bool, force: bool) -> None:
    root = repo_root()
    print(f"[install] target={host['name']}")
    print("- skills:")
    _symlink_items(root / host["skills_src"], host["skills_dest"], dry_run)
    print("- settings:")
    _install_settings(root / host["settings_src"], host["settings_dest"], force, dry_run)


def uninstall(host: dict, dry_run: bool, force: bool) -> None:
    root = repo_root()
    print(f"[uninstall] target={host['name']}")
    print("- skills:")
    _unlink_items(root / host["skills_src"], host["skills_dest"], dry_run)
    print("- settings:")
    _revert_settings(root / host["settings_src"], host["settings_dest"], force, dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install my-agents content to an agent host.")
    parser.add_argument("--target", default="pi", choices=sorted(HOSTS),
                        help="安装目标宿主（默认 pi）")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不落盘")
    parser.add_argument("--force", action="store_true",
                        help="强制覆盖已有 settings 键并启用 `_` 前缀文件")
    parser.add_argument("action", nargs="?", default="install",
                        choices=["install", "uninstall"],
                        help="install（默认）或 uninstall")
    args = parser.parse_args()

    host = HOSTS[args.target]
    if args.action == "install":
        install(host, args.dry_run, args.force)
    else:
        uninstall(host, args.dry_run, args.force)


if __name__ == "__main__":
    main()
