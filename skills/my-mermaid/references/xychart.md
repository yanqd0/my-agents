# XY Chart

## 选型

数值对比、benchmark 结果、多指标柱状图。框架性能横向对比、QPS/延迟/资源占用。

## 语法

```
xychart-beta
  title "Web 框架 QPS 对比 (req/s)"
  x-axis ["Express", "Fastify", "Hono", "Elysia"]
  y-axis "QPS" 0 --> 60000
  bar [12000, 28000, 35000, 45000]
  line [14000, 26000, 34000, 46000]
```

- `bar` 柱状图，`line` 折线图（可同时使用以对比两组数据）
- x-axis 类别用方括号 `["A", "B"]`
- y-axis `最小值 --> 最大值`
- 数值用绝对数字，不写单位

## 配色

xychart 不支持 classDef。多组 bar/line 自动分配不同颜色。建议最多 2 组 bar + 1 组 line。

语义建议：`bar` 用实际数据，`line` 用目标值/基线——利用形状差异而非颜色传达语义。

## 大小限制

x-axis 超 8 个类别时提示精简或分拆为多张小图。y-axis 覆盖数据极值 + 10% 头部空间。
