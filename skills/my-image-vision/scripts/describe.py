#!/usr/bin/env -S uv run
# /// script
# requires-python = "~=3.12"
# dependencies = ["pillow~=10.4", "httpx~=0.28"]
# ///
"""将图片发送到 DeepSeek V4.1 Vision API，输出文本描述。

用法：
    ./describe.py <image_path> [--prompt "指令"] [--max-tokens 1024]

API key 从环境变量 `DEEPSEEK_API_KEY` 读取（宿主无关，无则报错）。
仅走 DeepSeek Vision API；失败时退出码 1。
"""

import argparse, base64, mimetypes, os, sys
from pathlib import Path

import httpx

DEFAULT_PROMPT = "请详细描述这张图片的内容。"
DEEPSEEK_VISION_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"


def _b64_image(path: str) -> tuple[str, str]:
    """返回 (base64_data, media_type)。文件缺失时 exit(1)。"""
    img_path = Path(path)
    if not img_path.is_file():
        print(f"ERROR: 图片不存在: {path}", file=sys.stderr)
        sys.exit(1)
    mime, _ = mimetypes.guess_type(str(img_path))
    if mime is None:
        mime = "image/png"
    return base64.b64encode(img_path.read_bytes()).decode(), mime


def _call_deepseek_vision(
    image_path: str, prompt: str, token: str, max_tokens: int
) -> str:
    """调 DeepSeek V4.1 原生 Vision API（OpenAI Chat Completions 格式）。
    返回 choices[0].message.content；失败时 exit(1)。"""
    b64, mime = _b64_image(image_path)
    data_url = f"data:{mime};base64,{b64}"

    body = {
        "model": DEEPSEEK_MODEL,
        "max_tokens": max_tokens,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ],
        }],
    }

    resp = httpx.post(
        DEEPSEEK_VISION_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60,
    )

    if resp.status_code != 200:
        print(
            f"ERROR: DeepSeek Vision API 返回 {resp.status_code}\n"
            f"{resp.text[:500]}",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        print(f"ERROR: API 响应格式异常: {exc}", file=sys.stderr)
        print(resp.text[:500], file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="图片文件路径")
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="自定义 vision 指令"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=1024, help="响应最大 token 数（默认 1024）"
    )
    args = parser.parse_args()

    token = os.environ.get("DEEPSEEK_API_KEY", "")
    if not token:
        print(
            "ERROR: 未设置环境变量 DEEPSEEK_API_KEY（DeepSeek Vision API key）",
            file=sys.stderr,
        )
        sys.exit(1)

    text = _call_deepseek_vision(
        args.image, args.prompt, token, args.max_tokens
    )
    print(text)


if __name__ == "__main__":
    main()
