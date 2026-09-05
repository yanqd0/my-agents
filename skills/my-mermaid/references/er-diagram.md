# ER Diagram

## 选型

数据库表关系、实体关联。Schema 定义、ORM 模型中的外键分析。

## 语法

```
erDiagram
  USER ||--o{ ORDER: "places"
  ORDER ||--|{ ORDER_ITEM: "contains"
  PRODUCT ||--o{ ORDER_ITEM: "ordered in"

  USER {
    int id PK
    varchar name
    varchar email UK
    timestamp created_at
  }
```

## 关系标注

```
||--||  一对一（exactly one to exactly one）
||--o{  一对多（exactly one to zero or more）
}o--o{  多对多（zero or more to zero or more）
||--o|  一对零或一（exactly one to zero or one）
|o--o|  零或一对零或一（zero or one to zero or one）
||--|{  一对一到多（exactly one to one or more）
```

- `|` 必须一，`o` 零，`{` 多
- 左侧描述第一个实体，右侧描述第二个实体
- 关系标签放在 `:` 后，用简短英文描述业务语义（一律双引号包裹）
- 常用标签：`places`, `contains`, `belongs to`, `references`, `logs`

## 属性

- 类型用数据库类型：`int`/`varchar`/`text`/`timestamp`/`decimal`/`bool`/`uuid`/`jsonb`
- `PK` 主键、`FK` 外键、`UK` 唯一键
- 每个实体属性不超过 8 个，省略次要字段

## 配色

erDiagram 不支持 classDef，实体自动着色。同一实体属性同色，不同实体自动区分色相。

如需在正文中标注实体分组（如"核心域""通用域"），可在图外用表格或列表补充，不依赖于图的颜色。

## 大小限制

超 12 个实体时提示拆分（按业务边界，如"用户域"/"订单域"/"支付域"）。每个实体属性不超过 8 个。
