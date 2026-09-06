# dsh 0.1.1-rc.2 Agent Presets Authoring 与 Trust

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## Root / Trust

- shipped root：位于部署/安装目录的 `config/agent-presets/`，trust=`system`
- user root：`$DSH_HOME/.agent-presets`，trust=`user`
- user root 在 roster 中最后 append；earlier root wins duplicate id
- 复制 shipped preset 到 user root 是官方 authoring 路径

## Authoring 规则

- 创建/编辑发生在文件系统：一个 preset = 一个目录 + `agent.cordis.yml` + 可选 `preset.yml`
- `agentPresets.copy(from, to, name?)`：复制整个目录到 user root
- copy 会：
  - 拒绝非法 id（`[a-z0-9][a-z0-9-]*`）
  - 拒绝覆盖已存在 id
  - dereference symlink，做 self-contained 副本
  - 收紧权限：文件 `0600`、目录 `0700`
  - 改写 `preset.yml`：保留 description，去掉 name/order（复制品不能冒充原预设）
- `remove()` 拒绝删除 shipped preset

## preset.yml

- 只承载显示信息：`name`、`description`、`order`
- `id` 来自目录名，`trust` 来自所在 root，不能写在文件里

## 默认选择

- 组合默认由 web-app 的 `agent-presets` 行 `default: standard` 决定
- settings.yaml 可写：
  ```yaml
  agent-presets:
    default: minimal
  ```
- 用户设置只在下次创建会话时生效；运行中的会话保持创建/切换时使用的预设

## 加载失败

- 不可读/不可解析的目录会被列成 `broken`，而不是直接跳过
- `mount/resolve/recompose` 会拒绝 broken preset
- 这样 UI/删除入口仍能看到坏预设

## 对 dsh-mint

- 若 mint 想“一键生成 mint preset”，应 copy shipped standard/code 到 user root 后修改文件。
- 不要改 shipped install：升级会被覆盖。
- 想给 preset 加 mint 上下文，可以把 mint host 插件行作为普通工具/context 放进 preset，也可以只保留 host 全局挂载。
