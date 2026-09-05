#!/usr/bin/env -S uv run
# /// script
# requires-python = "~=3.12"
# dependencies = ["pillow~=10.4"]
# ///
"""对单张图片按固定顺序应用 1+ 项预处理操作。

用法：
    ./preprocess.py input.png --resize 1024x768 --grayscale --blur 2 -o out.png

操作顺序（固定，先大后小以减少计算量）：
    resize → crop → grayscale → blur → sharpen → threshold →
    invert → brightness → contrast
"""

import argparse, sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def _parse_size(val: str) -> tuple[int, int]:
    """解析 '1024x768' 或 '1024x' 或 'x768'；0 = 保持宽高比。"""
    w_str, _, h_str = val.partition("x")
    w = int(w_str) if w_str else 0
    h = int(h_str) if h_str else 0
    return w, h


def _parse_crop(val: str) -> tuple[int, int, int, int]:
    """解析 'L,T,R,B' → (左, 上, 右, 下)。"""
    parts = [int(v.strip()) for v in val.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("crop 需要 4 个整数：L,T,R,B")
    return tuple(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("-o", "--output", required=True, help="输出图片路径")
    parser.add_argument("--resize", type=_parse_size, help="缩放到 WxH（0 侧保持宽高比）")
    parser.add_argument("--crop", type=_parse_crop, help="剪裁，像素坐标 L,T,R,B")
    parser.add_argument("--grayscale", action="store_true", help="转灰度")
    parser.add_argument("--blur", type=float, metavar="R", help="高斯模糊半径")
    parser.add_argument(
        "--sharpen", type=float, metavar="F", help="锐化系数（>1 更锐，<1 更柔）"
    )
    parser.add_argument(
        "--threshold", type=int, metavar="V", help="二值化阈值 0-255（先转灰度再阈值）"
    )
    parser.add_argument("--invert", action="store_true", help="反色")
    parser.add_argument(
        "--brightness", type=float, metavar="F", help="亮度系数（>1 更亮，<1 更暗）"
    )
    parser.add_argument(
        "--contrast", type=float, metavar="F", help="对比度系数（>1 更高对比，<1 更低）"
    )
    args = parser.parse_args()

    # ── 前置校验 ──────────────────────────────────────────────────
    if not Path(args.input).is_file():
        print(f"ERROR: 图片不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    img = Image.open(args.input)

    # ── 按固定顺序执行操作 ────────────────────────────────────────
    # 顺序设计：先做 resize（缩减后续计算截面），再做空间变换，
    # 最后做色彩/色调。此顺序在代码和文档中保持一致。

    if args.resize:
        w, h = args.resize
        if w == 0 and h == 0:
            print("ERROR: resize 至少需要 W 或 H 中的一侧", file=sys.stderr)
            sys.exit(1)
        orig_w, orig_h = img.size
        if w == 0:
            ratio = h / orig_h
            w = int(orig_w * ratio)
        elif h == 0:
            ratio = w / orig_w
            h = int(orig_h * ratio)
        img = img.resize((w, h), Image.LANCZOS)

    if args.crop:
        img = img.crop(args.crop)

    if args.grayscale:
        img = img.convert("L")

    if args.blur is not None:
        img = img.filter(ImageFilter.GaussianBlur(radius=args.blur))

    if args.sharpen is not None:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(args.sharpen)

    if args.threshold is not None:
        # 先转灰度再二值化。若后续还有 brightness/contrast 操作，
        # 保留 "L" 模式（0/255 值域）以使增强有效；否则转为 1-bit。
        has_later_tone = (
            args.brightness is not None or args.contrast is not None
        )
        img = img.convert("L").point(
            lambda p, t=args.threshold: 255 if p > t else 0
        )
        if not has_later_tone:
            img = img.convert("1")

    if args.invert:
        # ImageOps.invert 要求 L 或 RGB 模式
        if img.mode not in ("L", "RGB"):
            img = img.convert("RGB")
        img = ImageOps.invert(img)

    if args.brightness is not None:
        img = ImageEnhance.Brightness(img).enhance(args.brightness)

    if args.contrast is not None:
        img = ImageEnhance.Contrast(img).enhance(args.contrast)

    # ── 保存 ──────────────────────────────────────────────────────
    # JPEG 需转 RGB（无 alpha 通道），WebP 直接保存
    save_fmt = None
    if args.output.lower().endswith((".jpg", ".jpeg")):
        img = img.convert("RGB")
        save_fmt = "JPEG"
    elif args.output.lower().endswith(".webp"):
        save_fmt = "WEBP"
    img.save(args.output, format=save_fmt)
    print(f"已保存: {args.output}  ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
