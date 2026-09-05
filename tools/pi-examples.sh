#!/usr/bin/env bash
# 定位已安装 pi 自带的官方 example extensions 目录（跨环境通用，不含本机私密/配置）。
#
# 用途：收编官方 example（见 notes/pi-extension-plugin-selection.md 安装方案 (a)）时，
#       从 pi 发行包读取 plan-mode / subagent / question / permission-gate 等源文件。
#
# 输出：第一个匹配的 examples/extensions 目录绝对路径；未找到时退出非零。
#
# 说明：pi 经 pnpm 安装时发行包落在 ~/.pnpm/store 下的版本哈希路径，故用 find 探测。
#       其它安装方式（npm -g / 源码）下可自行指向 pi-coding-agent/examples/extensions。
set -euo pipefail

found="$(find "${HOME}/.pnpm/store" -type d \
  -path '*/node_modules/@earendil-works/pi-coding-agent/examples/extensions' \
  2>/dev/null | head -n 1)"

if [[ -z "$found" ]]; then
  echo "未找到 pi example extensions（尝试定位 pi-coding-agent/examples/extensions）" >&2
  exit 1
fi
echo "$found"
