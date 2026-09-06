# dsh 0.1.1-rc.2 Session Log 导出 / 冷读

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 持久化格式

- 包：`dsh-session-persistence-jsonl`
- 默认路径：`$DSH_HOME/sessions/<normalized-cwd>/<encoded-id>/`
- 文件：`session.jsonl.zstd`（默认 zstd；可 `compression:none` 改 `.jsonl`）
- 第一行 immutable `SessionHeader`；后续每行一个 storage record/event
- `packChunks:true` 时 assistant/chunk 会合并 packed row，文件更小
- `assistant/chunk` 不丢弃；logical seq 连续

## Session Query / 冷读

- 包：`dsh-session-query`，ctx：`sessionQuery`
- 功能：list/read/filter/trace、readSurface、readEvent
- 冷读不会把 session 放进 live store
- `readSession()` 返回完整 detached raw log，经过与 resume 相同的 replay validation
- `readSurface()` 返回 header + raw capture + 当前 surface（按 model-history 顺序）
- 默认不启 FTS：`searchSessions/searchEvents` 依赖具体后端（SQLite），当前 `openAt:never`
- exact/literal-text 过滤与 `filterSessions/filterEvents` 不依赖 SQLite

## Export

- 浏览器 `/export` 或 header 按钮 → `GET /api/session.export?sessionId=...`
- Host 会先 flush live session，再读取 raw artifact
- ZIP 包含当前 session + descendants（`subagents/<id>/`）+ 被引用图片
- 必须是 persistence backend 提供 per-session raw artifact；JSONL 支持
- 只下载到浏览器，不写 Host 路径

## 对 mint / 离线审计

- 若要做 issue↔session 关联，冷读比 resume 更安全：不会创建 live Agent/工具副作用。
- 导出格式是原始 JSONL/ZIP，不保证“模型可见摘要”；应自己 fold/parse events。
- 全文搜索未默认开；需要时把 `session-query-sqlite` 改成 `openAt:first-search|startup` 并给 durable path。
