# dsh 0.1.1-rc.2 Tool-owned UI Presentation

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 两端概念

- Host/工具端：ToolDefinition 可选返回 `presentCall` / `presentResult`，给出 `card` 类渲染意图。
- Client 端：业务包把 wire tool name 注册到 `tool.call.toolview` slot，提供自己的行/详情渲染。
- Runtime 保持 call/result pairing、lifecycle、`subCalls` 树权威；UI 只消费冻结的 block。

## 标准工具行链路

```
ui-conversation 生成 tool-call Conversation Node
 → conversation.chat.node 分发给 ui-tool
 → ui-tool 递归 root/subCalls
 → 每个原子 call 按 wire name dispatch 到 tool.call.toolview
 → 未注册的名字走 generic fallback
```

## Client 端注册业务工具视图

```ts
ctx.slots.inject('tool.call.toolview', () =>
  ctx.slots.register({
    name: 'tool.call.toolview',
    key: '<wire tool name>',   // 例如 mint_query
  }, BusinessToolRow))
```

- 只注册 wire Tool 名和原子视图。
- 不配对 session events、不重建 transcript、不拥有 root/subcall 拓扑。
- owner payload 提供 `callId`、`toolName`、frozen `block`、可选 cwd/home、`openFile`/`inspect` 回调。

## Host/工具端返回 card

- 工具 body 可返回 `ToolCallView` / `ToolResultView`，让 UI 知道如何渲染该工具。
- 例如 `read` 用 diff/read card，`web` 用 web card。
- 未知 card 类型回退为纯文本结果。

## dsh-mint 参考

- mint_query 如果要更好看，可在 host 侧工具返回 `presentCall/presentResult` 意图。
- 同时在 client bundle 注册 `tool.call.toolview` 的 `mint_query` key，实现专用 issue/commit/plan 卡片。
- 通用文本展示可作为第一版兜底。
