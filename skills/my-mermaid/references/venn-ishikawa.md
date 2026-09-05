# Venn / Ishikawa

## Venn (venn-beta)

集合关系、重叠分析。功能覆盖、技术方案差异与交集。

```
venn-beta
  title 技术方案覆盖分析
  set A(React 生态)
  set B(SSR 方案)
  set C(状态管理)
  A ∩ B: Next.js
  A ∩ C: Redux / Zustand
  B ∩ C: 服务端状态
```

- `∩` 交集，`∪` 并集
- 集合标签用简短中文
- 交集标注具体实现或概念

### 配色

venn 自动着色，不支持 classDef。最多 4 个集合，超出不可读。

### 大小限制

超 4 个集合或 6 个交集时提示精简——拆分多个小 venn 图。

---

## Ishikawa (ishikawa-beta)

根因分析（鱼骨图）。Bug 溯源、性能瓶颈分解、故障模式归类。

```
ishikawa-beta
  title 生产环境 502 根因分析
  现象[502 Bad Gateway]
  人员[缺少培训] --> 根因_配置错误
  流程[Code Review 缺失] --> 根因_配置错误
  流程[无变更审批] --> 根因_未测试回滚
  工具[lint 未覆盖] --> 根因_配置错误
  环境[灰度不充分] --> 根因_未测试回滚
```

- `现象[...]` 为鱼头（问题描述，放右侧）
- `分类[原因]` → `根因_具体原因` 每条鱼骨
- 分类维度建议 4-6 个：人员、流程、工具、环境、依赖、数据
- 根因标签用简短中文，`_` 分隔层次

### 配色

ishikawa 自动着色，不支持 classDef。

### 大小限制

超 4 个分类维度或每个维度超 3 个原因时提示精简，合并次要原因。

---

> beta 图类型（venn-beta, ishikawa-beta）渲染兼容性可能因 Mermaid 版本而异。若渲染异常，优先用 flowchart 替代 ishikawa，用表格替代 venn。
