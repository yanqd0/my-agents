# dsh 0.1.1-rc.2 Attachment / File Reference / Workspace

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## Attachment

- 抽象：`dsh-attachment`（ctx.attachments）
- 本地实现：`dsh-attachment-local`
- 对象存储：`$DSH_HOME/attachments/v1/objects/<sha256-prefix>/<sha256>`
- session events 只保存 `sha256:` reference + 元数据，不保存 base64/浏览器路径
- 图片会标准化：EXIF 应用、元数据剥离、限制长边/像素/字节
- 限制：每消息最多 20 图、200MiB；单图最多 20MiB、64M 像素、8192px/边
- 保留策略暂为 indefinitely；GC deferred

### 对 mint

- mint 若展示截图/附件，应通过 attachment seam 持久化，不要往 session log 塞文件路径或 base64。

## File Reference

- 抽象：`dsh-file-reference`
- 本地实现：`dsh-file-reference-local`
- 为每个 agent 维护 bounded workspace file search（根为 session cwd）
- 默认 maxResults=20、maxEntries=10000、排除 `.git`/`node_modules`
- 不 follow directory symlink；无 .gitignore 语义
- 有 read 工具时贡献固定一句话 prompt，提示 `@` 路径需要用 read 读取

### 对 mint

- mint 的 `@issue`/文件引用若要出现在聊天，可参考此机制；但 mint 数据不是文件，走 RPC/projection 更合适。

## Workspace

- 包：`dsh-workspace`，ctx：`workspaceRegistry`
- durable workspace 记录 + 稳定顺序 + session 候选索引
- create 会 canonicalize realpath；同一 canonical path 只允许一个 workspace
- delete 只删注册与 session 账户，不删目录/日志
- session 与 workspace 的关系通过 header cwd 建立
- 支持 archive session：只隐藏分组，不删 log
- Workspace 本身不向 model 注入任何 prompt/token

### 对 mint

- 若 mint 需要“按项目/仓库”存状态，优先用 Workspace 作为项目维度，或把 mint db 路径记录在 workspace 相关配置中。
