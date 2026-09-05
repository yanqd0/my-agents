# 预处理操作目录

仅在步骤 3 执行预处理时读取。所有操作通过 `./scripts/preprocess.py` 的 CLI flag 链式指定。

## 操作表

| 操作 | CLI flag | 说明 |
|------|---------|------|
| 压缩/缩放 | `--resize WxH` | 目标像素尺寸。`0x` / `x0` 一侧为 0 时保持宽高比（如 `--resize 1024x0` 将宽度缩至 1024 且等比缩放高度）。LANCZOS 采样 |
| 剪裁 | `--crop L,T,R,B` | 像素坐标，逗号分隔 |
| 灰度 | `--grayscale` | 转为灰度（`L` 模式） |
| 模糊 | `--blur R` | 高斯模糊，radius 为像素值 |
| 锐化 | `--sharpen F` | >1 更锐，<1 更柔 |
| 二值化 | `--threshold V` | 先转灰度，再以 V（0-255）为阈值二值化 |
| 反色 | `--invert` | 反色（白底黑字 → 黑底白字；暗色截图 → 浅色） |
| 亮度 | `--brightness F` | >1 更亮，<1 更暗 |
| 对比度 | `--contrast F` | >1 更高对比，<1 更低 |

操作**按固定顺序**应用：resize → crop → grayscale → blur → sharpen → threshold →
invert → brightness → contrast。此顺序确保计算量大的操作优先执行（resize 先缩小可以
减少后续所有操作的计算量），空间变换在色彩/色调变换之前。

## 典型用例

```bash
# 压缩 + 灰度（常见：压缩大截图并去除无关颜色信息）
./scripts/preprocess.py shot.png --resize 1024x0 --grayscale -o out.png

# 暗色终端截图：反色 + 锐化
./scripts/preprocess.py terminal.png --invert --sharpen 1.5 -o out.png

# 灰度 + 二值化（OCR 前处理文档扫描件）
./scripts/preprocess.py scan.jpg --grayscale --threshold 128 -o out.png
```

## 合图（复合处理）

当需要对同一张图做多种处理并比较，或对多张相关图合并发送时：

```bash
./scripts/preprocess.py img.png --grayscale -o gray.png
./scripts/preprocess.py img.png --blur 3 -o blur.png
./scripts/composite.py img.png gray.png blur.png \
    --labels "原图,灰度,模糊" -o combined.png
```

合图后仅需一次 API 调用，节省轮次。
