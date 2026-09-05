# 默认提交前缀

本文件仅在规范识别流程判定"仓库无历史规范"时读取。若仓库已有规范（Angular、Conventional Commits 变体等），遵守仓库规范，不读此文件。

## 前缀表（Conventional Commits）

| type | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能/特性 | `feat: 新增 mermaid 图类型选择指南` |
| `fix` | Bug 修复 | `fix: 修复 settings 数组合并重复` |
| `chore` | 杂务、维护、工具 | `chore: 清理失效软链接` |
| `docs` | 文档 | `docs: 更新 README 安装说明` |
| `refactor` | 重构（非功能非修复） | `refactor: 提取公共 deep merge 逻辑` |
| `style` | 代码格式（不影响逻辑） | `style: 统一缩进` |
| `perf` | 性能优化 | `perf: 减少文件遍历次数` |
| `test` | 测试 | `test: 补充 revert 边界用例` |
| `build` | 构建系统、依赖 | `build: 升级 pyyaml 到 6.x` |
| `ci` | CI/CD 配置 | `ci: 添加 pre-commit 检查` |

> `git revert` 自动生成 `Revert "xxx"`，不提供 `revert` type。

- type 全小写，后跟 `: `，再接中文描述。
- 标题总长（含 type 和 `: `）≤ 40 字符。
