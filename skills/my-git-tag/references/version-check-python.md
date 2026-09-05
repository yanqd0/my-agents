# Python 项目版本一致性检查

Python 项目的版本号校验与修复规则。Python 使用 **PEP 440** 版本格式，与 git tag 的 semver 格式不同，需要格式转换。

## 项目识别

按优先级依次检测以下文件（命中即停）：

```bash
test -f pyproject.toml   # 优先
test -f setup.cfg         # 次选
test -f setup.py          # 最后
```

## 版本号位置

### pyproject.toml

```toml
[project]
name = "my-package"
version = "0.1.0"
```

或 Poetry 格式：

```toml
[tool.poetry]
name = "my-package"
version = "0.1.0"
```

### setup.cfg

```ini
[metadata]
name = my-package
version = 0.1.0
```

### setup.py

```python
setup(
    name="my-package",
    version="0.1.0",
    ...
)
```

## PEP 440 与 Semver 映射

Git tag 使用 semver 格式（如 `v0.1.0-alpha.1`），Python 配置文件使用 PEP 440（如 `0.1.0a1`）。比较时需将 tag 转换为 PEP 440：

| Git Tag（semver，去 `v` 前缀） | PEP 440（pyproject.toml / setup.cfg / setup.py） |
|---|---|
| `0.1.0` | `0.1.0` |
| `0.1.0-alpha.1` | `0.1.0a1` |
| `0.1.0-alpha` | `0.1.0a1` |
| `0.1.0-beta.2` | `0.1.0b2` |
| `0.1.0-beta` | `0.1.0b1` |
| `0.1.0-rc.3` | `0.1.0rc3` |
| `0.1.0-rc` | `0.1.0rc1` |
| `0.1.0-dev.1` | `0.1.0.dev1` |
| `0.1.0-dev` | `0.1.0.dev1` |

**转换规则**：
1. 去掉 `v` 前缀（如有）。
2. 将 `-alpha.N`（或 `-alpha`）替换为 `aN`（省略 `.N` 时取 `1`）。
3. 将 `-beta.N`（或 `-beta`）替换为 `bN`。
4. 将 `-rc.N`（或 `-rc`）替换为 `rcN`。
5. 将 `-dev.N`（或 `-dev`）替换为 `.devN`。

### 反向映射：PEP 440 → Semver

当需要从 Python 配置文件版本号生成 tag 名称时（如用户选择"调整 tag 以匹配项目配置"），使用以下逆映射：

1. 将 `aN`（alpha 后跟数字）替换为 `-alpha.N`（`0.1.0a1` → `0.1.0-alpha.1`）。
2. 将 `bN`（beta 后跟数字）替换为 `-beta.N`（`0.1.0b2` → `0.1.0-beta.2`）。
3. 将 `rcN` 替换为 `-rc.N`（`0.1.0rc3` → `0.1.0-rc.3`）。
4. 将 `.devN` 替换为 `-dev.N`（`0.1.0.dev1` → `0.1.0-dev.1`）。
5. 无后缀的正式版本不变，直接加 `v` 前缀（`0.1.0` → `v0.1.0`）。
6. 根据 `<last_tag>` 的 `v` 前缀惯例决定是否添加 `v` 前缀。

## 动态版本检测

以下任一条件命中，说明项目使用动态版本（基于 git tag 自动确定），**跳过检查**：

### setuptools-scm

- `pyproject.toml` 中存在 `[tool.setuptools_scm]` section
- `pyproject.toml` 中 `[project] dynamic = ["version"]`
- `pyproject.toml` 中 `[build-system] requires` 包含 `"setuptools-scm"` 或 `"setuptools_scm"`
- `setup.py` 中 `setup()` 调用包含 `use_scm_version=True` 或 `use_scm_version={...}`
- `setup.cfg` 中存在 `[tool:setuptools_scm]` section

### hatch-vcs

- `pyproject.toml` 中 `[tool.hatch.version] source = "vcs"` 或类似 vcs 源配置
- `pyproject.toml` 中 `[build-system] requires` 包含 `"hatch-vcs"` 或 `"hatch_vcs"`

### dunce / versioningit / other

- `pyproject.toml` 的 `[build-system] requires` 中包含 `"dunce"`、`"versioningit"`、`"vcversioner"` 等基于 git 的版本工具
- `setup.py` 中 `setup(version=...)` 的值由 `subprocess` 调用 `git describe` 等动态获取

### 不确定时

若存在上述动态版本特征但不完全匹配（如自定义的 SCM 方案），**默认视为动态版本并跳过**，同时记录"跳过：疑似动态版本，无法自动校验"。

## 比较方法

1. 将 `<version>`（git tag 版本号）按上述 PEP 440 映射规则转换为 `<pep440_version>`。
2. 读配置文件中的版本字段，记为 `<config_version>`。
3. 将 `<pep440_version>` 与 `<config_version>` 精确比较（大小写不敏感：`A1` = `a1`）。
4. 若 `<config_version>` 的值由变量引用或函数调用构成（如 `version = __version__` 读取自 `__init__.py`），则沿引用路径找到实际值后比较。
   - 常见模式：`setup.py` 中 `version=__import__("my_package").__version__` → 去对应 `__init__.py` 中找 `__version__ = "0.1.0"`。
   - 若引用链太长无法可靠追踪，跳过检查并记录原因。

## 修复方法

若项目配置版本与 tag 不一致，且用户选择"更新项目配置文件"：

### pyproject.toml（PEP 621 标准 `[project]`）

1. `Read` `pyproject.toml`，定位 `[project]` 下 `version = "..."` 行。
2. 用 `Edit` 将值替换为 `<pep440_version>`。

### pyproject.toml（Poetry `[tool.poetry]`）

1. 定位 `[tool.poetry]` 下 `version = "..."` 行。
2. 用 `Edit` 将值替换为 `<pep440_version>`。

### setup.cfg

1. 定位 `[metadata]` 下 `version = ...` 行。
2. 用 `Edit` 替换值（注意 `setup.cfg` 中 version 值不带引号）。

### setup.py

1. `Grep` `version=` 定位 `setup()` 调用中的版本行。
2. 若为直接字符串 `version="0.1.0"` → `Edit` 替换。
3. 若为变量引用 `version=__version__` → 追踪到源文件（如 `src/my_package/__init__.py`）并 `Edit` 其中的 `__version__` 值。
4. 若引用链复杂 → 报告"无法自动修复：版本号来自变量引用，请手动更新"。

修复后**不提交**——由调用方（my-git-tag）统一处理后续流程。
