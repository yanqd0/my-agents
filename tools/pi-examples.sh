#!/usr/bin/env bash
# 定位"当前已装 pi 发行包"自带的官方 example extensions 目录（选项 B 方案运行时定位）。
#
# 背景：pi 的 plan-mode / subagent / question / permission-gate / todo 等 T1 官方 example
#       <不收编进本仓库>，而是由 install.py --target pi 在安装时**从已装的 pi 包动态软链**
#       到 ~/.pi/agent/extensions/。本脚本只负责输出该 examples/extensions 目录的绝对路径。
#       （见 notes/pi-extension-plugin-selection.md 安装方案 (B)：动态引用已装 pi，软链。）
#
# 选择策略：pnpm 安装时发行包落在 ~/.pnpm/store/v11/links/.../pi-coding-agent/<版本>/ 下，
#       一个 pi 版本一个目录，可能并存多个版本。默认取**语义版本最高**者（通常=运行中版本）。
#       若运行中的 pi 非最高版本，可自行调整本脚本或改用其它解析方式指向对应版本。
#
# 输出：最高版本 pi 的 examples/extensions 绝对路径；未找到时退出非零并提示。
set -euo pipefail

base="${HOME}/.pnpm/store/v11/links/@earendil-works/pi-coding-agent"
if [[ ! -d "$base" ]]; then
  echo "未定位到 pi（未在 pnpm store 找到 pi-coding-agent）。若以 npm -g/源码安装，请自行令本脚本指向其 examples/extensions。" >&2
  exit 1
fi

for vdir in $(ls -1 "$base" | sort -V -r); do
  found="$(find "${base}/${vdir}" -type d \
    -path '*/node_modules/@earendil-works/pi-coding-agent/examples/extensions' \
    2>/dev/null | head -n 1)"
  if [[ -n "$found" ]]; then
    echo "$found"
    exit 0
  fi
done

echo "未找到 pi 官方 example extensions（各版本下均无 examples/extensions）" >&2
exit 1
