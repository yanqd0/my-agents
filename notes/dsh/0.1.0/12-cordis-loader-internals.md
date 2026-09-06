# dsh 0.1.1-rc.2 Cordis Loader 内部机制

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## Loader 是什么

`@deepseek-ai/cordis-plugin-loader` 管理运行时插件 EntryTree：

- `create/update/remove`：增减或修改 entry
- `resolve(id)`：按 id 解析 entry，支持嵌套 `a:b`
- `await()`：等待 pending import/fiber reload
- entry 变更后同步启动/停止对应 plugin fiber

## Entry 字段

| 字段 | 含义 |
|---|---|
| `id` | 稳定 id |
| `name` | 模块 specifier |
| `config` | 插件 config |
| `group` | 若 true，config 是子 entry 列表 |
| `disabled` | 停止且不启动 |
| `inject` | 声明依赖或给依赖加 intercept config |

## Include 文件层

`@deepseek-ai/cordis-plugin-include`：

- 读 YAML/JSON `cordis.yml`
- 把文件内容转成 Loader entries
- 可写回文件
- 支持 `patches`：按 id 覆盖或 insert

### Patch 规则

- 覆盖行是整行 config 替换
- `insert` 增加新行
- 新插件必须 insert，不能用裸 `- id/name` 覆盖不存在的行

## dsh boot 如何用它

- `mountRootInclude(ctx, configPath, patches, bareModuleBaseUrl)` 注册内置 `cordis:include` / `cordis:group`，再挂 include 根。
- `boot()` 挂完整棵树并 `assertEntriesLoaded/Activated`，把“启用了但没 fiber/启动失败”变成启动错误。
- 裸包名解析从 host 安装树；相对/绝对路径按各自 base 解析。

## 与 HMR

- Loader 保留运行图与 entry 更新同步。
- 用户 patch HMR 通过事务重算完整 patch list，然后 Loader 对增删改行做热更新。

## 对插件作者

- 运行时动态加载插件可用 `loader.create()` 或 `tool-cordis` / `cordis-host-runner` 体系。
- 普通自定义插件不需要直接使用 Loader；写在 profile patch 里即可。
