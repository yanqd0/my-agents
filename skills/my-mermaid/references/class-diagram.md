# Class Diagram

## 选型

类层次、接口、继承/组合关系。也适合 Go struct 嵌套、Rust trait 体系（非严格 OOP）。

## 语法

```
classDiagram
  class Animal {
    +String name
    +int age
    +makeSound()* void
  }
  class Dog {
    +fetch() void
  }
  class Cat {
    +purr() void
  }
  Animal <|-- Dog: extends
  Animal <|-- Cat: extends
```

- `+` public, `-` private, `#` protected, `*` abstract
- 泛型用 `~T~` 写法（如 `List~User~`），**不写 `<T>`**（尖括号被当 HTML 吞掉）
- `<|--` 继承, `*--` 组合, `o--` 聚合, `-->` 关联, `<..` 实现, `..>` 依赖
- `<<Interface>>` `<<Abstract>>` `<<Service>>` 标注

## 配色（通过 `<<stereotype>>`）

classDiagram 不支持 classDef，通过泛型标注 + 外部说明来区分层次：

```
classDiagram
  class UserService {
    <<Service>>
  }
  class UserRepository {
    <<Repository>>
  }
```

在正文描述中说明各层次的含义和分组，无需在图上着色。

如需在支持着色的渲染器中突出关键类，可在代码块后附注说明。

## 非 OOP 语言

- Go：struct 用 `<<Struct>>` 标注，嵌入用 `*--` 组合
- Rust：trait 用 `<<Interface>>`，impl 用 `<..` 实现
- TypeScript：interface 用 `<<Interface>>`，type alias 用 `<<Type>>`

## 大小限制

超 15 个类时提示精简（只保留核心类）或按包/模块拆分。属性超过 5 个时省略次要属性。
