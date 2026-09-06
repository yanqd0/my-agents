# dsh 0.1.1-rc.2 Conversation Node / UI Slot 扩展

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 客户端核心

- `dsh-client-runtime` 提供 SlotRegistry、SessionRuntime、WorkspaceRuntime
- `ctx.slots` 是浏览器 UI 插槽注册入口
- 会话状态推荐通过 projection 读，不直接扫描 session events/chat collections

## 常用 Slot 概念

| 目标 | 用途 |
|---|---|
| `conversation.view` | 会话主体视图 tab，如 chat/trajectory；注册选项含 id/order/label |
| `conversation.chat.node` | 会话流里特定业务 Node 的 renderer |
| `conversation.input.dock` | 输入区上方的 dock，如 TodoDock/QueueDock |
| `conversation.composer` | 需要接管 composer 的场景（approval/question） |
| `conversation.session.header.*` | 会话头扩展点 |
| sidebar/settings 等 | 侧栏/设置页 Slot |

## 添加一个会话 tab（mint issue panel 方向）

1. 包内声明 `dsh.client`，预构建 client bundle。
2. 让该包有 host 侧已挂载行，client-modules 才能扫描到它。
3. 浏览器加载后通过 `ctx.slots.register('conversation.view', ...)` 注册：
   - 需提供稳定 id、order、label
   - 自己渲染整块 view
4. 数据不要自己另开连接；优先通过现有 SessionRuntime/Remote/projection 获取。

## 添加一个会话流 Node

标准路径（官方 cookbook 思路）：

1. 扩展 client `ChatNodeDataMap`，声明自己的 node kind。
2. 注册 `ConversationNodeDefinition` 到 `ctx.conversationEvents`：
   - 每个关联事件给稳定 business id
   - update 可按 log `seq` 回放
   - 只在当前事件做 local matching
3. 注册 keyed renderer 到 `conversation.chat.node`。
4. renderer 消费最终 Node data，不扫描 Session/Chat 集合。

## 添加 composer/dock 类 UI

- `conversation.input.dock` 是 list slot，可按 order 插入。
- `conversation.composer` 是可接管 seat，适合全屏交互（approval、提问）。
- 隐藏 composer 时，相关 dock 通常一起隐藏。

## dsh-mint 建议路径

- mint issue 面板首选用 `conversation.view` 注册一个 tab。
- 若要在聊天流内展示 mint 卡片，注册一个新的 Chat Node + `conversation.chat.node` renderer。
- 读 mint 数据应由 host RPC / mint_query 或 host projection 提供；浏览器端避免直接读外部 CLI/db。

## 增补：Slash Command / 自定义命令

- host 注册中心：`dsh-commands`，通过 `ctx.commands` 注册 `/xxx`
- command 不只给模型；它服务人类 UI（输入框 `/` 菜单）
- 常见 command 生命周期：command/run → command/executed/done 等 durable events
- UI 侧有 `ui-commands`，消费 command 类型并渲染多种 UI：
  - prompt/参数收集
  - popupSelect
  - 运行状态
  - 下载/回调
- 自定义 mint `/mint` 命令的最小路径：
  1. host 插件里注册一个 command id + handler/参数
  2. UI 侧通过 command surface/输入 trigger 暴露给用户
  3. 命令执行结果落到 session events，浏览器才能从历史恢复
- `/export` 是现成参考：host 注册 + 浏览器 header 按钮 + 下载控制器
