#!/usr/bin/env -S uv run
# /// script
# requires-python = "~=3.12"
# dependencies = ["pillow~=10.4"]
# ///
"""将多张图片合并为一张网格图。

用法：
    ./composite.py a.png b.png c.png --labels "原图,灰度,模糊" -o combined.png
    ./composite.py *.png --cols 3 -o grid.png

每张输入图等比缩放到统一尺寸（所有输入的平均尺寸），按网格排列；
--labels 为顶部标签（逗号分隔，数量需与图片数一致）。
"""

import argparse, sys
from PIL import Image, ImageDraw, ImageFont


def _uniform_size(paths: list[str], max_dim: int = 1024) -> tuple[int, int]:
    """计算统一 cell 尺寸：所有图片平均宽高后裁剪到 max_dim。"""
    total_w = total_h = 0
    for p in paths:
        with Image.open(p) as im:
            total_w += im.width
            total_h += im.height
    w = total_w // len(paths)
    h = total_h // len(paths)
    # 若超过最大维度，等比缩放
    scale = min(1.0, max_dim / max(w, h))
    return int(w * scale), int(h * scale)


def _try_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """尝试加载系统 TrueType 字体，失败则回退到默认位图字体。"""
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", help="2 张及以上图片路径")
    parser.add_argument("--labels", default="", help="逗号分隔的标签，数量与图片一致")
    parser.add_argument(
        "--cols", type=int, default=0, help="网格列数（0=自动：按 4:3 宽高比推算）"
    )
    parser.add_argument("-o", "--output", required=True, help="输出图片路径")
    args = parser.parse_args()

    if len(args.images) < 2:
        print("ERROR: 至少需要 2 张图片才能合图", file=sys.stderr)
        sys.exit(1)

    # ── 标签解析 ──────────────────────────────────────────────────
    labels = [s.strip() for s in args.labels.split(",")] if args.labels else []
    if labels and len(labels) != len(args.images):
        print(
            f"WARNING: {len(labels)} 个标签对应 {len(args.images)} 张图"
            "——多余标签忽略，缺失标签留空",
            file=sys.stderr
        )
        labels = (labels + [""] * len(args.images))[:len(args.images)]

    # ── 网格计算 ──────────────────────────────────────────────────
    cell_w, cell_h = _uniform_size(args.images)

    n = len(args.images)
    cols = args.cols if args.cols > 0 else max(1, int((n * 4 / 3)**0.5 + 0.5))
    rows = (n + cols - 1) // cols

    label_h = 22 if labels and any(labels) else 0
    font = _try_font(14)

    canvas_w = cols * cell_w
    canvas_h = rows * (cell_h + label_h)
    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 逐格粘贴 ──────────────────────────────────────────────────
    # 已知优化点：每张图在此循环中再次打开，与 _uniform_size 中各打开
    # 一次合计 2n 次 I/O。大图场景可先全部加载到内存中（以内存换 I/O），
    # 当前实现优先内存安全。
    for i, img_path in enumerate(args.images):
        with Image.open(img_path) as src:
            # RGBA → RGB 时用白色背景合成，避免透明区域变黑色方块
            if src.mode == "RGBA":
                bg = Image.new("RGB", src.size, (255, 255, 255))
                bg.paste(src, mask=src.split()[3])
                src = bg
            else:
                src = src.convert("RGB")
            src = src.resize((cell_w, cell_h), Image.LANCZOS)
        row, col = divmod(i, cols)
        x, y = col * cell_w, row * (cell_h + label_h)
        canvas.paste(src, (x, y + label_h))

        # 顶部居中标签
        if label_h and i < len(labels) and labels[i]:
            text_x = x + cell_w // 2
            try:
                bbox = draw.textbbox((0, 0), labels[i], font=font)
                tw = bbox[2] - bbox[0]
            except AttributeError:
                tw = draw.textlength(labels[i], font=font)
            draw.text((text_x - tw // 2, y + 3),
                      labels[i],
                      fill=(50, 50, 50),
                      font=font)

    canvas.save(args.output)
    print(
        f"已保存: {args.output}  ({canvas_w}x{canvas_h}, "
        f"{cols}×{rows} 网格)"
    )


if __name__ == "__main__":
    main()
