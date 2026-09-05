# 下一开发版本号推算

根据已确定的正式发布版本号 `<version>` 和项目类型，推算发布后的下一个开发版本号。

## 输入

- `<version>`：本次已确定的正式发布版本号（如 `v0.5.0`、`v1.0.0`），可能含 `v` 前缀。
- 项目类型：由调用方（my-git-tag 步骤 4a）检测确定（cargo / npm / python / java / none）。

## 计算规则

1. 从 `<version>` 去掉可选的 `v` 前缀，提取 `MAJOR.MINOR.PATCH`。
2. 不论本次是 MAJOR、MINOR 还是 PATCH 发布，下一开发版**始终**：
   - **MINOR + 1**
   - **PATCH 归零**
   - 预发布阶段从 **`-alpha.1`** 开始

### 示例

| 当前发布版本 | 下一开发版（semver） |
|-------------|---------------------|
| `0.5.0` | `0.6.0-alpha.1` |
| `1.0.0` | `1.1.0-alpha.1` |
| `0.5.1` | `0.6.0-alpha.1` |
| `2.3.4` | `2.4.0-alpha.1` |
| `v0.5.0` | `0.6.0-alpha.1`（去 `v` 前缀后计算） |

## 项目特定格式转换

更新项目配置文件时，需按项目类型将 semver `<next_dev_version>` 转换为配置文件能识别的 `<next_dev_version_config>`：

| 项目类型 | 格式说明 | 输入 `0.6.0-alpha.1` → |
|----------|----------|------------------------|
| Rust/Cargo | 与 semver 一致，无需转换 | `0.6.0-alpha.1` |
| npm/Node.js | 与 semver 一致，无需转换 | `0.6.0-alpha.1` |
| Python（PEP 440） | `-alpha.N` → `aN`，详见下方映射表 | `0.6.0a1` |
| Java/Maven（当前含 `-SNAPSHOT`） | 保留 `-SNAPSHOT` 后缀，仅改数字部分 | `0.6.0-SNAPSHOT` |
| Java/Gradle（当前含 `-SNAPSHOT`） | 同上 | `0.6.0-SNAPSHOT` |
| Java/Maven/Gradle（不含 `-SNAPSHOT`） | 与 semver 一致 | `0.6.0-alpha.1` |

### Python PEP 440 映射

取自 `version-check-python.md` 的语义化版本 → PEP 440 映射规则：

| semver | PEP 440 |
|--------|---------|
| `0.6.0-alpha.1` | `0.6.0a1` |
| `0.6.0-alpha` | `0.6.0a1` |
| `0.6.0-beta.1` | `0.6.0b1` |
| `0.6.0-beta` | `0.6.0b1` |
| `0.6.0-rc.1` | `0.6.0rc1` |
| `0.6.0-rc` | `0.6.0rc1` |
| `0.6.0-dev.1` | `0.6.0.dev1` |
| `0.6.0-dev` | `0.6.0.dev1` |

由于下一开发版固定使用 `-alpha.1`，Python 转换结果始终为 `MAJOR.MINOR+1.0a1`（如 `0.6.0a1`）。

反向映射（PEP 440 → semver）：`0.6.0a1` → `0.6.0-alpha.1`，供步骤 1 展示时使用。

### Java SNAPSHOT 检测

通过 `Read` 检查配置文件当前版本是否以 `-SNAPSHOT` 结尾：
- 是 → 保留 `-SNAPSHOT` 后缀，仅将数字替换为 `MAJOR.MINOR+1.0`。
- 否 → 直接使用 semver 格式 `MAJOR.MINOR+1.0-alpha.1`。

## 输出

- `<next_dev_version>`：semver 格式（如 `0.6.0-alpha.1`），不含 `v` 前缀。供步骤 1 确认展示和步骤 9 记忆记录。
- `<next_dev_version_config>`：项目配置文件中应写入的格式（如 `0.6.0a1`）。供步骤 8 更新配置文件使用。
