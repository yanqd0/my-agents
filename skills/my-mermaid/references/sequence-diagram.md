# Sequence Diagram

## 选型

跨组件/跨服务请求-响应交互：API 调用链、消息传递、认证流程、中间件链路。

## 参与者

```
sequenceDiagram
  actor User as "用户"
  participant FE as "前端"
  participant BE as "后端"
  participant DB as "数据库"
  participant MQ as "消息队列"
```

- `actor` 人形图标（用户），`participant` 矩形
- 别名用中文，ID 用简洁英文；中文或含特殊字符的名称**一律经 `as` 别名承载**，不直接作 ID
- 消息文本内 `;` 用 `#59;` 转义；半角 `:` 只作消息分隔符出现一次，文本内需要时用全角"："

## 消息类型

```
A->>B:  实线箭头（同步调用）
A-->>B: 虚线箭头（返回/响应）
A-)B:   异步箭头
A-xB:   异步带叉（超时/失败）
A->>+B: 激活生命线（开始处理）
B-->>-A: 结束生命线（处理完成）
```

## 结构块

```
loop 每分钟执行
  A->>B: 定期检查
end

alt 登录成功
  A->>B: 进入主页
else 登录失败
  A->>B: 显示错误
end

opt 可选步骤
  A->>B: 发送通知
end
```

## 注释

```
Note over A,B: 跨参与者说明
Note left of A: 左侧注释
Note right of B: 右侧注释
```

## 配色

sequenceDiagram 的参与者通过 theme 控制，不支持 classDef。用注释中的颜色标注（如 `%% 红色组 → 危险路径`）辅助理解即可。

消息标签本身已足够表达语义，不需要额外着色。复杂时序图用 `rect rgb(...)` 高亮关键区域：

```
rect rgb(200, 230, 255)
  A->>B: 关键认证步骤
end
```

使用浅色：关键区域用 `rgb(220, 240, 255)`（蓝）、错误区域用 `rgb(255, 220, 220)`（红）。

## 大小限制

超 25 条消息时提示拆分。按 alt 分支或 API 边界拆分。

## 常见模式

- **认证流程**：User → FE → Auth → DB → Token → FE
- **CRUD**：FE → API → Service → DB → Response
- **消息队列**：Producer → MQ → Consumer → DB
- **错误处理**：用 `alt success / else error` + `-x` 标注失败路径
