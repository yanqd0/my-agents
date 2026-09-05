# npm 项目版本一致性检查

npm/Node.js 项目的版本号校验与修复规则。

## 项目识别

项目根目录存在 `package.json` 文件：

```bash
test -f package.json
```

## 版本号位置

`package.json` 顶层 `"version"` 字段：

```json
{
  "name": "my-package",
  "version": "0.1.0",
  ...
}
```

- `"version"` 通常在文件开头（`"name"` 之后）。
- 格式为 `"MAJOR.MINOR.PATCH[-prerelease]"`，遵循语义化版本。

### 特殊情况

- **Monorepo workspace**：若存在 `pnpm-workspace.yaml`、`lerna.json`、`nx.json` 或 `workspaces` 字段，根 `package.json` 的 `version` 可能为 `"0.0.0"` 或无意义值。此时需要定位到**具体子包**的 `package.json`。
  - 若项目只有一个子包存在 `"version"` 且值不为 `"0.0.0"` → 检查该子包。
  - 若多个子包各有独立版本 → 用 `question` 让用户选择检查哪个。
- **`"private": true`**：若 `package.json` 标记为 private 且 `"version"` 缺失，这是合法的（private packages 不需版本号）→ 跳过检查。

## 版本号格式

- npm 使用标准 semver，与 git tag 格式一致（仅无 `v` 前缀）。
- **无需格式转换**：去掉 tag 的 `v` 前缀后直接比较。

## 比较方法

1. 从 `<version>`（git tag 版本号）中去掉 `v` 前缀得到 `<stripped_version>`。
2. `Read` `package.json`，解析 `"version"` 字段值 `<pkg_version>`。
3. 比较 `<stripped_version>` 与 `<pkg_version>`（字符串精确比较）。

## 动态版本检测

npm 生态极少使用 git-tag 动态版本。以下情况跳过检查：
- `package.json` 中不存在 `"version"` 字段（且 `"private": true`）。
- `"version"` 值为 `"0.0.0-semantically-released"` 或类似占位符（常见于 semantic-release 项目）→ 跳过检查，记录"跳过：版本号由 semantic-release 管理"。

## 修复方法

若项目配置版本与 tag 不一致，且用户选择"更新项目配置文件"：

1. `Read` `package.json`，定位 `"version"` 行号。
2. 用 `Edit` 将版本值替换为 `<stripped_version>`。

**备选方案**：若 `npm` CLI 可用，也可使用：

```bash
npm version <stripped_version> --no-git-tag-version --allow-same-version
```

`--no-git-tag-version` 阻止 npm 自动创建 git tag（我们手动打 tag），`--allow-same-version` 允许版本号不变（万一已经是目标版本则不报错）。

修复后**不提交**——由调用方（my-git-tag）统一处理后续流程。
