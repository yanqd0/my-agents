# dsh 0.1.1-rc.2 Telemetry / 审计钩子

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 现状

- 包：`dsh-session-telemetry-otel`
- 当前默认 `mode: DISABLED`
- 可通过 `DSH_TELEMETRY_MODE=FULL|FEEDBACK_ONLY` 开启
- `DSH_TELEMETRY_DISABLED` 任意非空值硬关
- 上传目标默认 `https://harness-telemetry.deepseeksvc.com/v1/logs`

## 模式

| 模式 | 行为 |
|---|---|
| `FULL` | 每个 session telemetry record 立即交给 OTel SDK |
| `FEEDBACK_ONLY` | 仅当用户产生 feedback 时重放/导出相关记录 |
| `DISABLED` | 默认；不构造 exporter/pipeline |

## 数据范围与隐私注意

- 开启后 record 携带完整 event.data：
  - 用户/助手消息、工具参数与结果、system prompt、tool schemas、todo、compaction summary、feedback
- 官方 seam **默认没有 redaction 规则**；需要自己挂 `sessionTelemetry/record` 监听器裁剪
- API key 不在 session events 中，结构性不会上传
- 匿名身份来自 `$DSH_HOME/.anonymous-user-id`，删除可重置

## 对插件开发 / 审计

- 若要审计 dsh-mint 自身行为，不依赖 telemetry；直接读 session log / projection 更可控。
- 若 mint 想加“使用统计”，可注册自己的 feedback/projection，不碰 OTel。
- 了解默认关闭很重要：不能假设用户开启了遥测。

## 其它审计钩子

- `dsh-message-feedback`：like/dislike + note
- `dsh-session-log-export`：人工导出
- `dsh-session-stats`：turn/step 统计 projection
- session log 本身是最完整审计源；OTel 只是可关闭的上报后端
