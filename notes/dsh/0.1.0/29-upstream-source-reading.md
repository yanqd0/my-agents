# dsh 0.1.1-rc.2 上游 deepseek-harness 源码阅读方法

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 信息源优先级

1. GitHub/本地 clone 的 TS 源码
2. 已安装 npm 包内的 `lib/*.js` 产物
3. 已安装包 README 和 `lib/types/**/*.d.ts`
4. 运行时 `dsh --profile web --dump-config` / session log 验证
5. `cordis_inspect`（如果 cordis preset 可用）

## 包到源码目录

每个已安装包的 `package.json` 有 repository 字段，例如：

- `@deepseek-ai/dsh-base` → `packages/bundle/base`
- `@deepseek-ai/dsh-web-app` → `packages/bundle/web-app`
- `@deepseek-ai/cordis` → `vendor/cordis`
- `@deepseek-ai/cordis-plugin-loader` → `vendor/loader`

上游 monorepo 根一般为：

```text
apps/cli           # dsh CLI / bin
packages/*         # 各 dsh 插件/服务
vendor/*           # Cordis 与周边 fork
docs/              # 子系统文档、cookbook
```

## 读一个插件的顺序

1. `package.json`：description、repository、exports、dependencies
2. `README.md`：Service/API/Config/事件/设计意图
3. `src/index.ts` 与主要源码：实际注册的 service/events/tools
4. `cordis.patch.yml`：该 bundle 如何被挂载/默认配置
5. `.d.ts`：精确类型签名；类型声明比 README 更可信
6. 运行时验证：工具是否出现、事件是否触发、session log 内容

## 无源码时的替代

- 已安装产物路径：
  `~/.nvm/versions/node/.../lib/v11/.../node_modules/@deepseek-ai/<pkg>`
- 包中可能带 `lib/*.js` 单文件 bundle，可 grep `ctx.*`、事件名、方法名。
- 类型定义 `lib/types/**/*.d.ts` 常保留大量 JSDoc，足够定位接口。

## 搜索技巧

```bash
# 在已安装包树中找事件/API
grep -RIn "tools/pre-execute\|agent/session-start\|cordis_inspect" \
  ~/.nvm/versions/node/*/lib/*/node_modules/@deepseek-ai

# 看一个包所有 exports
python3 - <<'PY'
import json,glob,os
p='@deepseek-ai/dsh-tools'
for f in glob.glob(os.path.expanduser('~/.pnpm/store/v11/links/@deepseek-ai/dsh-tools/*/*/node_modules/@deepseek-ai/dsh-tools/package.json')):
    print(json.load(open(f))['exports'])
PY
```

## 开发/验证闭环

```bash
# 组合树与 patch 警告
dsh --profile web --dump-config

# 本仓库构建后挂载 mint
cd /home/user/yanqd0/dsh-mint && pnpm build

# 查看真实运行结果
# ~/.dsh/sessions/<project>/<session>/session.jsonl.zstd
```

## 注意

- 已安装版本可能与上游 main 有偏差；文档/代码结论要标注版本。
- `dsh --dump-config` 会写 profile 文件，需要 profile 可写。
- 阅读官方 README 里指向 `docs/` 的链接时，若安装包未带 docs，可在上游 monorepo 对应路径查找。
