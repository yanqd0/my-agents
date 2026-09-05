# Java 项目版本一致性检查

Java/Maven/Gradle 项目的版本号校验与修复规则。

## 项目识别

按优先级依次检测以下文件（命中即停）：

```bash
test -f pom.xml                        # Maven，优先
test -f build.gradle                   # Gradle (Groovy DSL)
test -f build.gradle.kts               # Gradle (Kotlin DSL)
```

## Maven（pom.xml）

### 版本号位置

`pom.xml` 中 `<project>` 根下的 `<version>` 元素：

```xml
<project xmlns="...">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>0.1.0</version>
    ...
</project>
```

- **注意区分**：`<parent>` 内也有 `<version>`，必须取 `<project>` 直系子节点中**不在** `<parent>` 内的 `<version>`。
- 若项目定义了 `<parent>` 且自身 `<version>` 省略（继承父 POM 版本）→ 跳过检查，记录"跳过：版本号继承自父 POM"。

### 版本号格式

- Maven 使用 `MAJOR.MINOR.PATCH[-qualifier]` 格式。
- 直接去掉 git tag 的 `v` 前缀后比较即可（Maven 的 `-SNAPSHOT` 等限定符会在比较时处理）。
- 若 `<version>` 以 `-SNAPSHOT` 结尾，tag 版本通常不带后缀。比较时忽略 `-SNAPSHOT` 后缀（`0.1.0-SNAPSHOT` ↔ tag `v0.1.0` 视为一致）。

### 动态版本检测

以下特征表明版本号由 git tag 动态管理，**跳过检查**：
- `<scm>` section 存在且 `<connection>` 或 `<developerConnection>` 包含 `scm:git:`。
- `pom.xml` 中引用了 `git-commit-id-plugin`、`flatten-maven-plugin`（带 `revision` 属性，版本号引用了 `${revision}`）、`maven-release-plugin`。
- `<version>` 值为 `${revision}` 或 `${project.version}` 等属性引用（而非硬编码字符串）。
- 若存在 `.mvn/maven.config` 且引用了 `-Drevision=` 或类似的 tag 驱动版本号 → 也是动态方案。

### 修复方法

若版本号是硬编码且不一致，且用户选择"更新项目配置文件"：

1. `Grep` `^[[:space:]]*<version>` 定位 `<project>` 下的版本行，排除 `<parent>` 块内的 `<version>`：先 `Grep` `^[[:space:]]*<parent>` 取 `<parent>` 块起止行号，再在其余 `[[:space:]]*<version>` 匹配中取第一个。
2. 若 `<version>` 以 `-SNAPSHOT` 结尾，保留 `-SNAPSHOT` 后缀，仅替换版本数字部分。
3. 用 `Edit` 替换为 target version。

修复后**不提交**——由调用方（my-git-tag）统一处理后续流程。

## Gradle（build.gradle / build.gradle.kts）

### 版本号位置

Gradle Groovy DSL：

```groovy
version = '0.1.0'
```

Gradle Kotlin DSL：

```kotlin
version = "0.1.0"
```

也可能从 `gradle.properties` 读取属性：

```properties
# gradle.properties
version=0.1.0
```

- 检查优先级：`build.gradle[.kts]` 中的 `version =` → `gradle.properties` 中的 `version=`。
- 若 `build.gradle[.kts]` 中写的是 `version = project.findProperty("version") ?: "0.0.0"` 等间接引用，去 `gradle.properties` 中找实际值。

### 版本号格式

- Gradle 使用标准 semver 或 Maven 兼容格式。
- 直接去掉 git tag 的 `v` 前缀后比较。
- 若版本以 `-SNAPSHOT` 结尾，比较时忽略（同 Maven 规则）。

### 动态版本检测

以下特征表明动态版本，**跳过检查**：
- 引用了 `com.gorylenko.gradle-git-properties` plugin。
- `version` 由 git 命令动态赋值（如 `version = 'git describe --tags'.execute().text.trim()`）。
- 使用了 `nebula.release`、`axion-release-plugin`、`researchgate/gradle-release` 等 release plugin。
- `gradle.properties` 中的 `version` 由 CI/CD 环境变量注入（若调用方上下文能获取 CI 信息则判断，否则以配置文件实际内容为准）。

### 修复方法

若版本号是硬编码且不一致，且用户选择"更新项目配置文件"：

1. `Grep` `^version\s*=` 在 `build.gradle[.kts]` 中定位版本行。
2. 若版本在 `gradle.properties` 中定义，则定位 `^version=` 行。
3. 用 `Edit` 替换为 target version。
4. 若 `-SNAPSHOT` 后缀存在，保留后缀，仅替换数字部分。

修复后**不提交**——由调用方（my-git-tag）统一处理后续流程。

## 多模块项目

若 Maven 多模块（aggregator pom）或 Gradle 多项目（`settings.gradle` 中定义了 `include`）：
- 优先检查根项目/aggregator 的版本号。
- 若各子模块有独立版本号 → 记录"多模块项目，仅检查根模块版本。子模块请单独确认。"
