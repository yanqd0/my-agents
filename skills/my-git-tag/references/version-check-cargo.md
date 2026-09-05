# Cargo 项目版本一致性检查

Rust/Cargo 项目的版本号校验与修复规则。

## 项目识别

项目根目录存在 `Cargo.toml` 文件：

```bash
test -f Cargo.toml
```

## 版本号位置

`Cargo.toml` 中 `[package]` section 下的 `version` 字段：

```toml
[package]
name = "my-crate"
version = "0.1.0"
```

- `version` 字段在 `[package]` 与下一个 `[` section 之间出现。
- 格式为 `version = "MAJOR.MINOR.PATCH[-prerelease]"`，遵循语义化版本。
- 注意 workspace 成员：若存在 `[workspace]` 且当前 crate 在 `[workspace.members]` 中，则版本号可能在 workspace 级别的 `Cargo.toml` 中统一管理。此时需先确认版本号实际定义位置。

## 版本号格式

- Cargo 使用标准 semver，与 git tag 格式一致（仅无 `v` 前缀）。
- **无需格式转换**：去掉 tag 的 `v` 前缀后直接比较即可。

## 比较方法

1. 从 `<version>`（git tag 版本号）中去掉 `v` 前缀等到 `<stripped_version>`。
2. `Grep`（pattern `^version\s*=`）在 `Cargo.toml` 的 `[package]` 区域内定位版本行。
3. 提取 `version = "..."` 中的版本字符串，与 `<stripped_version>` 精确比较（大小写敏感）。

## 动态版本检测

Cargo 通常要求显式声明版本号，**极少使用 git-tag 动态版本**。以下情况跳过检查：
- `Cargo.toml` 的 `[package]` 下不存在 `version` 字段。
- 这通常意味着版本号在 workspace 根 `Cargo.toml` 中或由构建脚本动态注入——此时记录"跳过：版本字段缺失"。

## 修复方法

若项目配置版本与 tag 不一致，且用户选择"更新项目配置文件"：

1. `Read` `Cargo.toml`，定位 `[package]` 与 `version = "..."` 行号。
2. 用 `Edit` 将 `version` 值替换为 `<stripped_version>`（去 `v` 前缀的 tag 版本号）。
3. 可选替代方案：若 `cargo set-version` 可用（`cargo install cargo-edit` 后），优先使用 `Bash cargo set-version <stripped_version>`，它自动处理 Cargo.toml 格式。
4. 修复后**不提交**——由调用方（my-git-tag）统一处理后续流程。
