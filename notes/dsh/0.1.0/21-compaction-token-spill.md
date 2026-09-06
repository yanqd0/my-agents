# dsh 0.1.1-rc.2 Compaction / Token Meter / Spill / Surface 重写

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 分层

| 包 | 角色 |
|---|---|
| `dsh-compaction` | 抽象 CompactionEngine（ctx.compaction） |
| `dsh-compaction-basic` | 具体后端：token 压力 + 保留尾部 + LLM summary |
| `dsh-compaction-tool-result-pruner` | 压缩前裁剪超大 tool result |
| `dsh-token-meter` | replay-aware token 计量 |
| `dsh-spill` | 超大文本 spill 抽象 |
| `dsh-spill-policy` | >50KB tool result 转成文件引用 |
| `dsh-output-retention` | 通用保留/截断提示工具 |

## Surface 重写模型

- 只有 `user/message`、`assistant/message`、`tool/result` 可以出现在 model surface。
- compaction 不直接在 surface 上写 summary event。
- 成功压缩流程：
  1. append `compaction/start`（log-only，拿锁）
  2. LLM 总结被 shadow 范围
  3. append `compaction/summary`（log-only）
  4. append 一个 `user/message` + `surfaceOp: replace` 作为 checkpoint
  5. append `compaction/end`（log-only，放锁）
- 被 shadow 的旧事件仍留在 raw log，只是不再进入 derived model history。

## Token Meter

- `ctx.tokenMeter` 计量当前 canonical envelope 与 surface 总 token。
- 压力触发在 `agent/pre-step` 检查；canonical overflow 在 `agent/request-error` 进入。
- compaction summary 是一次直接 `ctx.llm.stream()` 调用，不在 loop step 内。
- summary 调用重放已有 system prompt/tools/messages，以复用 KV cache。

## Tool Result Pruner / Spill

- pruner：对超过阈值的 tool result 做 head/middle/tail 保留，可减少 surface 体积。
- spill：把超长结果存入 private file，给模型一个简短 preview + path。
- pruner 和 spill 都“不能减少 system prompt / tools / session prefix”，只处理结果文本。

## 对插件作者

- 如果 mint 会给 model 注入长 issue/context，应做成“按需读取/工具返回”，不要写死进每轮 system/context。
- 如果 mint 工具返回很长，可考虑给 dsh spill/pruner 适配，而不是直接拼长文本。
- 会话压缩会 shadow 旧消息；如果 mint 有需要长期保留的“事实”，应写入独立 projection/storage，而不是依赖对话历史。
