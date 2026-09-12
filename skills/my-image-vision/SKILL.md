---
name: my-image-vision
description: >-
  图片识图与预处理：对图片进行压缩/剪裁/灰度/模糊等预处理后，调用 DeepSeek V4.1 Vision API
  返回文本描述。当用户说"看这张图/分析截图/图片里有什么/识别这张图/OCR/描述图片内容"
  等识图意图时可自主调用；支持多重处理合并为一张图后一次识别。
allowed-tools: Read Write Bash question
---

对用户指定的图片进行预处理（可选），然后调用 DeepSeek V4.1 Vision API 返回文本描述。
需宿主已导出 `DEEPSEEK_API_KEY`。

**交互约定**：需用户选择/确认处，若宿主提供反问 tool（`question`/`ask_user_question`）则用之；无交互 tool 或 headless 时退化为纯文本列出选项等用户回答。

## 执行步骤

1. **解析意图**：提取图片路径（相对/绝对路径均可）和预处理需求——用户可能说
   "压一下再识别"、"灰度后看"、"把这张图模糊掉再 OCR"等。图片路径不存在时
   用 `question`（单选）确认，选项为邻近的候选图片路径。
2. **确认预处理计划**：列出拟执行的操作清单（0~N 个，需复合处理时标明合并为一张图），
   用 `question`（单选）确认——"按此预处理并识别"（推荐）、
   "调整预处理"、"不做预处理，直接识别"。
3. **执行预处理**（如需）：
   - 单图 1+ 操作：`<宿主 skills 目录>/my-image-vision/scripts/preprocess.py`
     `<input> --op1 ... --opN -o <output>`（pi 为 `~/.agents/skills/`）
   - 单图多处预处理后需合并 → 多次 `preprocess.py` 后
     `<宿主 skills 目录>/my-image-vision/scripts/composite.py`
     `<a> <b> ... --labels "标签1,标签2" -o <output>`
   操作语法详见 `Read` `references/preprocessing.md`（条件触发，仅此步读）。
4. **发送识图**：`<宿主 skills 目录>/my-image-vision/scripts/describe.py`
   `<image> [--prompt "指令"] [--max-tokens N]`（pi 为 `~/.agents/skills/`）。
   脚本从环境变量 `DEEPSEEK_API_KEY` 读 key，走 DeepSeek Vision API。
   退出码 **0** → stdout 为识别文本，直接进入步骤 5；
   **其他** → 错误，stdout/stderr 为错误信息，不尝试替代路径。
   若需补充前置上下文（之前讨论的结构体定义、变量含义等），经 `--prompt` 传入
   ——脚本为无状态单轮接口，skill 负责从对话中提取上下文组织提示词。
5. **输出结果**：将描述嵌入对话上下文。如涉及预处理操作链，简要标注（如
   "（经灰度+二值化后识别）"）。

## 约束

- API key 由环境变量 `DEEPSEEK_API_KEY` 提供，不传参数、不硬编码到脚本或 skill 正文。
- 图片仅送 DeepSeek Vision API（与当前对话模型同一供应商），不送第三方。
- `--prompt` 中不包含敏感信息（凭证、token 等）。
