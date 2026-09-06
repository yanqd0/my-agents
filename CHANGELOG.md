# Change Log

## 0.1.0

### Features

- 搭建跨宿主 agent 内容源骨架：`install.py` 多目标安装器（软链 `skills/` 到 `~/.agents/skills`、deep-merge `settings/*.json` 到宿主设置）、`skills/` 与 `settings/pi/` 目录。
  - 安装器收敛为扁平 CLI，以 `--revert` 卸载、配 `--dry-run`/`--yes`/`--force`；dsh 目标 0.2.0 补齐。
  - 增加去重守卫：审计实体副本本应软链/失效软链，并入安装 skills 步。
- 迁移并做 pi 适配的通用 skills（my-mermaid、my-code-io、my-git-commit、my-git-amend、my-changelog、my-git-tag、my-image-vision）：AskUserQuestion 交互改写为宿主 `question` tool、正文用统一交互动作名并适配 headless。
  - 中性 references/scripts 改经 `vendor/my-claude` submodule + 软链拼装去重，本地只维护 pi 差异 `SKILL.md`。
- settings 片段与模型定义：`settings/pi/model/*.json` 经安装器 deep-merge 进 `~/.pi/agent/models.json`（deepseek-v4-pro/flash 定义），新增 compaction/startup 片段。
- 官方 T1 扩展随安装动态软链（方案 B）：`tools/pi-examples.sh` 定位已装 pi 包的 examples/extensions，install 将白名单项（plan-mode/subagent/question/permission-gate/todo）软链到 `~/.pi/agent/extensions/`，升级 pi 后重跑即刷新。

### Bug Fixes

- deepseek 价格改用官方定价页人民币原值直接入库，移除汇率折算反推。
- settings/pi/default.json 开启 showHardwareCursor，修复 herdr 等终端光标无法显示。

### Others

- 建立 AGENTS.md 项目规范（目录结构/安装机制/复用原则/路线图）与 notes 项目记忆索引（`notes/MEMORY.md`）。
- 记录 pi 扩展与插件技术选型（T0/T1/T2 三档政策及安装方案决策）。
- 文档随结构与策略演进同步：settings 片段政策、宿主作用域标签规则、submodule+软链拼装语义、README 改为人向。
- 添加 MIT LICENSE，引入 my-claude 为 submodule（相对 URL）。
