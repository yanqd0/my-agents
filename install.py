#!/usr/bin/env python3
"""Install this project's content to a target agent host.

Multi-host source project. Targets pi (default) and dsh behind the same --target
contract; codex/opencode are added later.

For each host this project provides several kinds of installable content:
  - skills : 通用 Agent Skills，软链到该宿主共享的 skills 目录
              (pi/dsh 均读 ~/.agents/skills；dsh-skill-filesystem 默认直接发现，无需插件)
  - settings: settings/<host>/*.json deep-merge 到该宿主的 settings 文件
              (pi -> ~/.pi/agent/settings.json；dsh 无对应 JSON 文件 → 不装)
  - models: settings/<host>/model/*.json deep-merge 到该宿主的模型定义文件
              (pi -> ~/.pi/agent/models.json，含各模型 cost 价格；dsh 的模型/cost 由
              provider 插件管理，无 pi models.json 对应物 → 不装)
  - plugins (dsh): 按 DSH_PLUGINS_BY_PROFILE 把插件装进指定 dsh profile，经
              `dsh plugin --profile <p> add/remove` 安装/卸载。已装项在每次重跑时做
              **更新检查**（npm registry 版本对比 / GitHub HEAD 版本对比），发现新版本
              默认仅报告，加 `--update` 才实际升级（registry 走 `pnpm update --latest`、
              github spec 走 `pnpm update`）。缺装项始终 add，故重跑幂等且可检更新。
  - extensions (pi): T1 必要官方 example <不本仓库收编>，改由 <tools/pi-examples.sh> 定位
              **已装 pi 包**自带的 examples/extensions，将白名单条目软链到
              ~/.pi/agent/extensions/。扩展含完整系统权限 → 分发需确认/--yes；升级 pi 后
              重跑即刷新（软链指向的 store 路径可能随版本/prune 漂移，重跑会 re-link）。

`src == None` 表示该 host 不装该项（install/uninstall 跳过）。dsh 的 skills/settings 加载
机制调研见 notes/dsh/skills-settings-loading.md。

`_` 前缀文件默认跳过安装，可用 --force 显式启用。模型定义/价格更新需 --force
（models 数组为既有键，默认 merge 不覆盖）。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HOME = Path.home()

# ── per-host layout ──────────────────────────────────────────────────────
# src 目录相对本文件；dest 为安装目标（可为 None=该 host 不装此项）
# T1 必要官方 example 白名单：仅软链这些进 ~/.pi/agent/extensions。pi 的 examples 目录含几十个
# 示例，全软链会让 pi 自动加载大量非必要扩展（命令/UI/工具冲突）。来源随已装 pi 版本漂移，
# 升级 pi 后重跑 install.py 即刷新到新版本源。
PI_T1_EXTENSIONS = ["permission-gate.ts", "plan-mode", "question.ts", "subagent", "todo.ts"]


HOSTS = {
    "pi": {
        "name": "pi",
        # skills: 软链 skills/* -> <shared skills dir>
        "skills_src": "skills",
        "skills_dest": HOME / ".agents" / "skills",
        # settings: deep-merge settings/pi/*.json -> settings file
        "settings_src": "settings/pi",
        "settings_dest": HOME / ".pi" / "agent" / "settings.json",
        # models: deep-merge settings/pi/model/*.json -> model definitions file
        "model_src": "settings/pi/model",
        "model_dest": HOME / ".pi" / "agent" / "models.json",
    },
    "dsh": {
        "name": "dsh",
        # skills: 软链 skills/* -> <shared skills dir>。dsh-skill-filesystem 默认把
        #         ~/.agents/skills 作 user-agents 根直接发现（rank500，无需插件）——与 pi 同源。
        "skills_src": "skills",
        "skills_dest": HOME / ".agents" / "skills",
        # settings: dsh 无 pi 式 models.json/settings.json 深合并对象。其配置是
        #         ~/.dsh/settings.yaml 的 YAML namespace 文档（个人 harness 配置）、模型/cost
        #         由 provider 插件管理（见 notes/dsh/skills-settings-loading.md）→ 0.2.0 不装。
        #         置 None 表示该 host 不装此项（install/uninstall 会跳过）。
        "settings_src": None,
        "settings_dest": None,
        "model_src": None,
        "model_dest": None,
    },
    # codex/opencode: 后续在此补宿主布局
}


# ── dsh plugins（web profile 第三方插件清单） ─────────────────────────────
# dsh 的「插件」是 cordis/npm 包，需经 dsh 官方封装 `dsh plugin --profile <p>
# <pnpm add/remove/update>` 装进某个 profile（web/headless/tui/自定义名）。本清单是
# 单一真源：dict: profile -> [(声明名, pnpm spec), ...]。
#   - 声明名 = 装进 profile package.json 的依赖键（= 插件包 package.json 的 name；
#     github spec 装完后 pnpm 仍以该名记依赖），用于幂等/回滚判定与更新报告。
#   - spec = 传给 `dsh plugin … add` 的原样 spec：registry 名走 npm（国内镜像友好、
#     更新检查走 registry）；GitHub 专发（作者未发 npm / npm 包缺 dsh.bundle）用
#     `github:owner/repo`（装 repo 默认分支 HEAD，需仓库自带构建产物或 prepare 脚本；
#     更新检查走 GitHub API 的 HEAD 版本）。
# 更新语义：registry spec → pnpm view 对比最新；github spec → GitHub HEAD package.json
# 版本对比。重复执行 install.py 只报告；`--update` 才升级。
# 注意：graph-memory 的依赖含原生模块（@photostructure/sqlite），首次 add 若被 pnpm
# 阻断构建脚本，需在 profile pnpm-workspace.yaml 的 allowBuilds 放行后重跑（dsh 会在
# 失败信息中提示 exact key）。目标若是正运行的 GUI profile（web），建议非活跃时执行。
DSH_PLUGINS_BY_PROFILE = {
    "web": [
        ("dshmarket", "dshmarket"),                            # dsh-market/dsh-market：设置内插件市场（浏览/一键装/更新/备份）
        ("dsh-whale-widget", "dsh-whale-widget"),              # MeteorNOX/DeepSeek-Balance-Whale-Widget：余额鲸鱼挂件（npm 已发）
        ("graph-memory", "github:adoresever/graph-memory"),    # adoresever/graph-memory：知识图谱记忆（dsh 支持仅 GitHub main，npm 未发）
        ("dsh-calculator", "github:bobcat848/dsh-calculator"), # bobcat848/dsh-calculator：DeepSeek 费用/余额右上角卡片（无 npm 发布）
    ],
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


def _verify_nested_links(src_dir: Path) -> int:
    """校验 skills 源内指向 submodule 的嵌套软链可解析。

    软链进整目录后，skill 内部 references/scripts 若为指向 vendor/my-claude 的
    软链，需子模块已 checkout 才可达；失效即提示用户 init 子模块。返回失效数。
    """
    broken = 0
    for dp, dn, fn in os.walk(src_dir):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            p = Path(dp) / f
            if p.is_symlink() and not p.exists():
                print(f"  warn   : 嵌套软链失效 {p.relative_to(repo_root())}"
                      f"  (子模块未 checkout？跑 git submodule update --init)")
                broken += 1
    if broken:
        print(f"  warn   : {broken} 处嵌套软链失效，请先初始化子模块 vendor/my-claude")
    return broken


def _audit_dedup(src_dir: Path) -> int:
    """去重守卫：skills 源内实体文件若与 submodule 对应文件字节一致，本应软链而非实体副本。

    防止共享文件被改成实体副本后静默分叉（打破去重/单源）。返回冗余实体副本数。
    """
    redun = 0
    sub = repo_root() / "vendor" / "my-claude" / "skills"
    for dp, dn, fn in os.walk(src_dir):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            p = Path(dp) / f
            if p.is_symlink():
                continue
            relp = p.relative_to(src_dir)
            vfile = sub / relp
            if vfile.is_file() and p.read_bytes() == vfile.read_bytes():
                print(f"  warn   : {p.relative_to(repo_root())} 与上游一致，建议改软链去重")
                redun += 1
    return redun


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


# ── extensions（pi: 软链已装 pi 包官方 example 白名单，需确认） ─────────
def _pi_examples_dir():
    """经 tools/pi-examples.sh 定位当前(最高)已装 pi 的 examples/extensions 目录。
    未定位成功返回 None。"""
    sh = repo_root() / "tools" / "pi-examples.sh"
    try:
        out = subprocess.run(["bash", str(sh)], capture_output=True, text=True,
                             check=True, timeout=20).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None
    p = Path(out)
    return p if p.is_dir() else None


def _confirm(prompt: str) -> bool:
    try:
        return input(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def _pending_ext_names(names: list, src_dir: Path, dst_dir: Path) -> list:
    """列出白名单中需要 install/relink 的项（已正确指向当前源则过滤）。
    返回 [(name, 动作)]。当前 pi 无此 example（版本差异）不列入。"""
    pending = []
    for name in names:
        src, dst = src_dir / name, dst_dir / name
        if not src.exists():
            continue
        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                continue
            pending.append((name, "relink"))
        elif dst.exists():
            pending.append((name, "exists(non-link 保留)"))
        else:
            pending.append((name, "install"))
    return pending


def _cleanup_broken_ext(names: list, dst_dir: Path, dry_run: bool) -> None:
    for name in names:
        dst = dst_dir / name
        if dst.is_symlink() and not dst.exists():
            print(f"{'[dry]  ' if dry_run else '  '}cleanup: {name} (broken link)")
            if not dry_run:
                dst.unlink()


def _install_extensions(dry_run: bool, assume_yes: bool) -> None:
    print("- extensions:")
    src_dir = _pi_examples_dir()
    if src_dir is None:
        print("  warn   : 未定位到已装 pi 的官方 examples（tools/pi-examples.sh）→ 跳过扩展")
        return
    dst_dir = HOME / ".pi" / "agent" / "extensions"
    dst_dir.mkdir(parents=True, exist_ok=True)

    pending = _pending_ext_names(PI_T1_EXTENSIONS, src_dir, dst_dir)
    if not pending:
        print("  skip   : T1 扩展已全部指向当前 pi 包（升级 pi 后重跑即可刷新）")
        _cleanup_broken_ext(PI_T1_EXTENSIONS, dst_dir, dry_run)
        return

    print(f"  T1 必要官方 example 将软链到 {dst_dir}:")
    for name, act in pending:
        print(f"    - {name}  ({act})")
    print("  源     : 已装 pi 包自带 examples/extensions（升级 pi 后重跑即刷新；T2 第三方不默认装）")
    if dry_run:
        return
    if not (assume_yes or (sys.stdin.isatty() and _confirm("  确认软链以上扩展？"))):
        print("  取消   : 扩展未链接（headless 需显式 --yes；可先 --dry-run 预览）")
        return
    for name in PI_T1_EXTENSIONS:
        src, dst = src_dir / name, dst_dir / name
        if not src.exists():
            print(f"  warn   : 当前 pi 无 example {name}（版本差异，跳过）")
            continue
        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                print(f"  skip   : {name} (correct)")
                continue
            print(f"  relink : {name}")
            dst.unlink()
        elif dst.exists():
            print(f"  skip   : {name} (existing non-link，保留)")
            continue
        else:
            print(f"  install: {name}")
        dst.symlink_to(src)
    _cleanup_broken_ext(PI_T1_EXTENSIONS, dst_dir, dry_run)


def _uninstall_extensions(dry_run: bool) -> None:
    print("- extensions:")
    dst_dir = HOME / ".pi" / "agent" / "extensions"
    if not dst_dir.is_dir():
        print("  skip   : 扩展目录不存在")
        return
    removed = 0
    for name in PI_T1_EXTENSIONS:
        dst = dst_dir / name
        if dst.is_symlink():
            print(f"{'[dry]  ' if dry_run else '  '}remove : {name}")
            if not dry_run:
                dst.unlink()
            removed += 1
    if not removed:
        print("  skip   : 无 T1 扩展软链")


# ── dsh plugins（经 `dsh plugin` 封装；清单见 DSH_PLUGINS_BY_PROFILE） ───
def _dsh_home() -> Path:
    """dsh harness 配置根：$DSH_HOME 或 ~/.dsh。"""
    return Path(os.environ.get("DSH_HOME") or HOME / ".dsh")


def _dsh_profile_deps(profile: str) -> set:
    """读某 dsh profile 的 package.json dependencies 键集合（幂等/回滚判定）。"""
    pkg = _dsh_home() / "profiles" / profile / "package.json"
    try:
        return set(json.loads(pkg.read_text()).get("dependencies", {}))
    except (OSError, json.JSONDecodeError):
        return set()


def _spec_is_registry(spec: str) -> bool:
    """registry 名（裸包名）vs git/path/url spec 判定。registry 走 npm 源更新检查。"""
    return not spec.startswith(("github:", "git+", "https:", "http:", "file:", "link:", "."))


def _spec_repo(spec: str) -> str | None:
    """从 github:owner/repo spec 提取 owner/repo；非 github spec 返回 None。"""
    if spec.startswith("github:"):
        return spec[len("github:"):].split("#")[0]
    return None


def _installed_version(profile: str, name: str) -> str | None:
    """读某 profile 内已装插件包的实际版本（nodeLinker hoisted → profile/node_modules）。"""
    pkg = _dsh_home() / "profiles" / profile / "node_modules" / name / "package.json"
    try:
        return json.loads(pkg.read_text()).get("version")
    except (OSError, json.JSONDecodeError):
        return None


def _registry_latest(name: str) -> str | None:
    """registry 最新版本：`pnpm view <name> version`（pnpm 自管 store，不依赖 npm cache）。"""
    try:
        proc = subprocess.run(["pnpm", "view", name, "version"],
                              capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            return None
        return proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else None
    except (OSError, subprocess.SubprocessError):
        return None


def _github_head_version(repo: str) -> str | None:
    """GitHub 默认分支 HEAD 的 package.json version（github spec 更新检查用）。

    raw.githubusercontent 在国内网络常被墙/超时，故走 api.github.com（contents raw）。
    """
    try:
        def get(url: str, accept_raw: bool) -> str:
            req = urllib.request.Request(url, headers={
                "User-Agent": "my-agents-install",
                "Accept": "application/vnd.github.raw" if accept_raw
                          else "application/vnd.github+json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8")

        meta = json.loads(get(f"https://api.github.com/repos/{repo}", False))
        branch = meta.get("default_branch")
        if not branch:
            return None
        return json.loads(get(
            f"https://api.github.com/repos/{repo}/contents/package.json?ref={branch}",
            True)).get("version")
    except Exception:
        return None


def _version_key(version: str) -> tuple:
    """粗粒度版本序键：取第一个连字符/加号前的数字段（如 1.6.0-beta.14 -> (1,6,0)）。"""
    nums = re.findall(r"\d+", (version or "").split("-")[0].split("+")[0])
    return tuple(int(n) for n in nums) or (0,)


def _run_dsh_plugin(profile: str, args: list, dry_run: bool) -> None:
    """执行 `dsh plugin --profile <p> <args…>`（add/remove/update 等，原样转发 pnpm）。"""
    cmd = ["dsh", "plugin", "--profile", profile] + args
    label = " ".join(cmd)
    print(f"{'[dry]  ' if dry_run else '  '}dsh-plugin {profile} {' '.join(args)}")
    if dry_run:
        return
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:
        print(f"  error : 执行失败 {label}: {exc}")
        return
    if proc.stdout:
        print("  " + proc.stdout.strip().replace("\n", "\n  "))
    if proc.returncode != 0:
        print(f"  error : {label} 退出码 {proc.returncode}: {proc.stderr.strip()}")


def _dsh_plugin_available(profile: str, name: str, spec: str) -> str | None:
    """某插件「上游最新可装版本」：registry spec 查 npm；github spec 查 GitHub HEAD。"""
    if _spec_is_registry(spec):
        return _registry_latest(name)
    repo = _spec_repo(spec)
    return _github_head_version(repo) if repo else None


def _update_dsh_plugin(profile: str, name: str, spec: str, dry_run: bool) -> None:
    """把已装插件升到上游最新。registry → pnpm update --latest；github → pnpm update。"""
    if _spec_is_registry(spec):
        _run_dsh_plugin(profile, ["update", "--latest", name], dry_run)
    else:
        _run_dsh_plugin(profile, ["update", name], dry_run)


def _dsh_plugins(dry_run: bool, update: bool) -> int:
    """dsh 目标：按 DSH_PLUGINS_BY_PROFILE 装齐插件并做更新检查。

    缺装项 → add（幂等）；已装项 → 对比上游版本：可更新时默认只报告，`update=True`
    时执行升级。返回「存在更新」计数（含已升级），供概要提示。
    """
    print("- plugins:")
    if not DSH_PLUGINS_BY_PROFILE:
        print("  skip   : 未声明 dsh 插件（DSH_PLUGINS_BY_PROFILE 为空）")
        return 0
    if shutil.which("dsh") is None or shutil.which("pnpm") is None:
        print("  warn   : 需要 dsh 与 pnpm 在 PATH（dsh 用于 profile 插件管理）")
        return 0
    outdated = 0
    for profile, entries in sorted(DSH_PLUGINS_BY_PROFILE.items()):
        installed = _dsh_profile_deps(profile)
        for name, spec in entries:
            if name not in installed:
                _run_dsh_plugin(profile, ["add", spec], dry_run)
                continue
            print(f"  skip   : {name} (profile={profile} 已装)")
            installed_ver = _installed_version(profile, name)
            if installed_ver is None:
                continue
            available = _dsh_plugin_available(profile, name, spec)
            if available is None:
                print(f"  warn   : {name} 版本核对不可达（registry/GitHub？），已装 {installed_ver}")
                continue
            if _version_key(available) > _version_key(installed_ver):
                outdated += 1
                verb = "upgrade" if (update and not dry_run) else "update-avail"
                print(f"  {verb} : {name} {installed_ver} -> {available} "
                      f"(spec={spec}{', dry-run' if dry_run and update else ''})")
                if update and not dry_run:
                    _update_dsh_plugin(profile, name, spec, dry_run)
    if outdated:
        if update and dry_run:
            how = "（--update + --dry-run：仅预览，未实际升级）"
        elif update:
            how = "（已按 --update 升级）"
        else:
            how = "（重跑加 --update 升级）"
        print(f"  note   : {outdated} 个插件有可用更新{how}")
    return outdated


def _uninstall_dsh_plugins(dry_run: bool) -> None:
    """dsh 目标：卸载 DSH_PLUGINS_BY_PROFILE 里的插件（remove）。"""
    print("- plugins:")
    if not DSH_PLUGINS_BY_PROFILE:
        print("  skip   : 未声明 dsh 插件（DSH_PLUGINS_BY_PROFILE 为空）")
        return
    for profile, entries in sorted(DSH_PLUGINS_BY_PROFILE.items()):
        installed = _dsh_profile_deps(profile)
        for name, _spec in entries:
            if name not in installed:
                print(f"  skip   : {name} (profile={profile} 未装)")
                continue
            _run_dsh_plugin(profile, ["remove", name], dry_run)


# ── actions ──────────────────────────────────────────────────────────────
def install(host: dict, dry_run: bool, force: bool, assume_yes: bool,
            update_plugins: bool = False) -> None:
    root = repo_root()
    print(f"[install] target={host['name']}")
    print("- skills:")
    _symlink_items(root / host["skills_src"], host["skills_dest"], dry_run)
    _verify_nested_links(root / host["skills_src"])
    _audit_dedup(root / host["skills_src"])
    settings_src = host["settings_src"]
    if settings_src is None:
        print("- settings:（该 host 无此项，跳过）")
    else:
        print("- settings:")
        _install_settings(root / settings_src, host["settings_dest"], force, dry_run)
    model_src = host["model_src"]
    if model_src is None:
        print("- models:（该 host 无此项，跳过）")
    else:
        print("- models:")
        _install_settings(root / model_src, host["model_dest"], force, dry_run)
    if host["name"] == "pi":
        _install_extensions(dry_run, assume_yes)
    elif host["name"] == "dsh":
        _dsh_plugins(dry_run, update_plugins)


def uninstall(host: dict, dry_run: bool, force: bool) -> None:
    root = repo_root()
    print(f"[uninstall] target={host['name']}")
    print("- skills:")
    _unlink_items(root / host["skills_src"], host["skills_dest"], dry_run)
    settings_src = host["settings_src"]
    if settings_src is None:
        print("- settings:（该 host 无此项，跳过）")
    else:
        print("- settings:")
        _revert_settings(root / settings_src, host["settings_dest"], force, dry_run)
    model_src = host["model_src"]
    if model_src is None:
        print("- models:（该 host 无此项，跳过）")
    else:
        print("- models:")
        _revert_settings(root / model_src, host["model_dest"], force, dry_run)
    if host["name"] == "pi":
        _uninstall_extensions(dry_run)
    elif host["name"] == "dsh":
        _uninstall_dsh_plugins(dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install my-agents content to an agent host.")
    parser.add_argument("--target", default="pi", choices=sorted(HOSTS),
                        help="安装目标宿主（默认 pi）")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不落盘")
    parser.add_argument("--force", action="store_true",
                        help="强制覆盖已有 settings 键并启用 `_` 前缀文件")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="扩展软链免交互确认（headless 下必须）")
    parser.add_argument("--update", action="store_true",
                        help="dsh：把已装插件升级到上游最新（缺省只检查并报告可用更新）")
    parser.add_argument("--revert", action="store_true",
                        help="卸载：移除本项目装入的 skills/settings/models/extensions/插件")
    args = parser.parse_args()

    host = HOSTS[args.target]
    if args.revert:
        uninstall(host, args.dry_run, args.force)
    else:
        install(host, args.dry_run, args.force, args.yes, args.update)


if __name__ == "__main__":
    main()
