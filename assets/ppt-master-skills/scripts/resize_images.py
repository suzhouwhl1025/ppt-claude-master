#!/usr/bin/env python3
"""
图片尺寸校验与缩放工具

将图片缩放到目标尺寸，保持宽高比不变形。
如果图片比例与目标比例不一致，可以选择：
1. fit - 完整放入目标区域，留白填充
2. fill - 填满目标区域，可能裁剪

Usage:
    python3 resize_images.py <image.png> -w 1920 -h 1080
    python3 resize_images.py <image.png> --target-width 1920 --target-height 1080 --mode fit
    python3 resize_images.py <image.png> --check-only  # 仅检查尺寸，不缩放

    # 批量处理目录
    python3 resize_images.py ./images/ -w 1920 -h 1080 --mode fill

Examples:
    python3 resize_images.py cover.png -w 1920 -h 1080
    python3 resize_images.py ./images/*.png -w 1280 -h 720 --mode fit
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[WARN] PIL not installed. Install with: pip install Pillow")
    print("       Will only perform size check without resizing.")


# ============================================================================
# 工具函数
# ============================================================================

def get_image_dimensions(image_path: str) -> tuple:
    """获取图片尺寸"""
    if not os.path.exists(image_path):
        return None, None

    try:
        with Image.open(image_path) as img:
            return img.width, img.height
    except Exception as e:
        print(f"  [ERROR] 无法读取图片: {e}")
        return None, None


def resize_image(
    image_path: str,
    target_width: int,
    target_height: int,
    mode: str = 'fit',
    output_path: str = None,
    background_color: tuple = (255, 255, 255)
) -> bool:
    """
    缩放图片到目标尺寸

    Args:
        image_path: 源图片路径
        target_width: 目标宽度
        target_height: 目标高度
        mode: 'fit' - 完整放入目标区域(留白) | 'fill' - 填满目标区域(可能裁剪)
        output_path: 输出路径，默认覆盖原图
        background_color: 背景色(用于 fit 模式留白)

    Returns:
        bool: 是否成功
    """
    if not HAS_PIL:
        print("[ERROR] PIL 未安装，无法缩放图片")
        return False

    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.width, img.height

            # 计算目标宽高比
            target_ratio = target_width / target_height
            original_ratio = original_width / original_height

            if mode == 'fit':
                # 完整放入模式：计算缩放比例使图片完整放入目标区域
                if original_ratio > target_ratio:
                    # 原图更宽，以宽度为准
                    new_width = target_width
                    new_height = int(target_width / original_ratio)
                else:
                    # 原图更高，以高度为准
                    new_height = target_height
                    new_width = int(target_height * original_ratio)

                # 创建目标尺寸的白色画布
                result = Image.new('RGB', (target_width, target_height), background_color)
                # 缩放图片
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                # 居中粘贴
                paste_x = (target_width - new_width) // 2
                paste_y = (target_height - new_height) // 2
                result.paste(resized, (paste_x, paste_y))

            elif mode == 'fill':
                # 填满模式：裁剪后填满
                if original_ratio > target_ratio:
                    # 原图更宽，裁剪左右
                    new_width = int(original_height * target_ratio)
                    left = (original_width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, original_height))
                else:
                    # 原图更高，裁剪上下
                    new_height = int(original_width / target_ratio)
                    top = (original_height - new_height) // 2
                    img = img.crop((0, top, original_width, top + new_height))

                # 缩放到目标尺寸
                result = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            else:
                print(f"[ERROR] 未知模式: {mode}")
                return False

            # 保存
            if output_path is None:
                output_path = image_path

            result.save(output_path, quality=95)
            return True

    except Exception as e:
        print(f"[ERROR] 缩放失败: {e}")
        return False


def check_image_size(
    image_path: str,
    target_width: int,
    target_height: int,
    tolerance: float = 0.02
) -> dict:
    """
    检查图片尺寸是否匹配

    Args:
        image_path: 图片路径
        target_width: 目标宽度
        target_height: 目标高度
        tolerance: 允许的误差比例(默认 2%)

    Returns:
        dict: {
            'match': bool,           # 是否匹配
            'actual': (w, h),        # 实际尺寸
            'expected': (w, h),      # 目标尺寸
            'ratio_diff': float,      # 宽高比差异
            'width_diff': float,      # 宽度差异百分比
            'height_diff': float,    # 高度差异百分比
            'need_resize': bool      # 是否需要缩放
        }
    """
    actual_w, actual_h = get_image_dimensions(image_path)

    if actual_w is None:
        return {
            'match': False,
            'actual': (None, None),
            'expected': (target_width, target_height),
            'error': '无法读取图片'
        }

    # 计算差异
    width_diff = abs(actual_w - target_width) / target_width
    height_diff = abs(actual_h - target_height) / target_height

    # 宽高比差异
    target_ratio = target_width / target_height
    actual_ratio = actual_w / actual_h
    ratio_diff = abs(actual_ratio - target_ratio) / target_ratio

    # 判断是否匹配
    match = width_diff <= tolerance and height_diff <= tolerance

    return {
        'match': match,
        'actual': (actual_w, actual_h),
        'expected': (target_width, target_height),
        'ratio_diff': ratio_diff,
        'width_diff': width_diff,
        'height_diff': height_diff,
        'need_resize': not match
    }


def process_image(
    image_path: str,
    target_width: int,
    target_height: int,
    mode: str = 'fit',
    check_only: bool = False,
    force: bool = False
) -> bool:
    """
    处理单张图片

    Returns:
        bool: 是否成功
    """
    print(f"\n处理: {image_path}")

    # 检查图片是否存在
    if not os.path.exists(image_path):
        print(f"  [ERROR] 图片不存在: {image_path}")
        return False

    # 检查尺寸
    check_result = check_image_size(image_path, target_width, target_height)

    if check_result.get('error'):
        print(f"  [ERROR] {check_result['error']}")
        return False

    actual_w, actual_h = check_result['actual']

    print(f"  实际尺寸: {actual_w}x{actual_h}")
    print(f"  目标尺寸: {target_width}x{target_height}")

    if check_result['match']:
        print(f"  [OK] 尺寸匹配，无需缩放")
        return True

    if check_only:
        print(f"  [WARN] 尺寸不匹配，需要缩放")
        print(f"    宽度差异: {check_result['width_diff']*100:.1f}%")
        print(f"    高度差异: {check_result['height_diff']*100:.1f}%")
        print(f"    宽高比差异: {check_result['ratio_diff']*100:.1f}%")
        return False

    print(f"  [INFO] 开始缩放 (mode={mode})...")

    # 备份原图
    backup_path = image_path + '.backup'
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(image_path, backup_path)
        print(f"  [INFO] 原图已备份到: {backup_path}")

    # 执行缩放
    success = resize_image(image_path, target_width, target_height, mode)

    if success:
        print(f"  [OK] 缩放完成")
        return True
    else:
        print(f"  [ERROR] 缩放失败")
        return False


def process_directory(
    dir_path: str,
    target_width: int,
    target_height: int,
    mode: str = 'fit',
    check_only: bool = False,
    recursive: bool = False
) -> dict:
    """
    批量处理目录中的所有图片

    Returns:
        dict: {'success': int, 'failed': int, 'skipped': int}
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
    dir_path = Path(dir_path)

    if recursive:
        image_files = [f for f in dir_path.rglob('*') if f.suffix.lower() in image_extensions]
    else:
        image_files = [f for f in dir_path.iterdir() if f.suffix.lower() in image_extensions]

    results = {'success': 0, 'failed': 0, 'skipped': 0}

    print(f"\n找到 {len(image_files)} 张图片")

    for img_file in image_files:
        success = process_image(
            str(img_file),
            target_width,
            target_height,
            mode,
            check_only
        )
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1

    return results


# ============================================================================
# 主入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="图片尺寸校验与缩放工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查单张图片尺寸
  python resize_images.py cover.png -w 1920 -h 1080 --check-only

  # 缩放单张图片(完整放入模式)
  python resize_images.py cover.png -w 1920 -h 1080 --mode fit

  # 缩放单张图片(填满模式，可能裁剪)
  python resize_images.py cover.png -w 1920 -h 1080 --mode fill

  # 批量处理目录
  python resize_images.py ./images/ -w 1920 -h 1080 --mode fit
        """
    )

    parser.add_argument(
        'path',
        help='图片文件路径或目录路径'
    )
    parser.add_argument(
        '-w', '--target-width',
        type=int,
        required=True,
        help='目标宽度(像素)'
    )
    parser.add_argument(
        '-h', '--target-height',
        type=int,
        required=True,
        help='目标高度(像素)'
    )
    parser.add_argument(
        '--mode',
        choices=['fit', 'fill'],
        default='fit',
        help='缩放模式: fit(完整放入,留白填充) | fill(填满,可能裁剪). 默认: fit'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='仅检查尺寸，不进行缩放'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制缩放，即使尺寸匹配也重新生成'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归处理子目录'
    )
    parser.add_argument(
        '--bg-color',
        default='white',
        help='fit 模式的背景色 (white/black/hex). 默认: white'
    )

    args = parser.parse_args()

    # 解析背景色
    bg_color_map = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'transparent': (0, 0, 0, 0)
    }
    if args.bg_color.startswith('#'):
        # 解析 hex 颜色
        hex_color = args.bg_color[1:]
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        bg_color = (r, g, b)
    else:
        bg_color = bg_color_map.get(args.bg_color.lower(), (255, 255, 255))

    path = args.path

    if os.path.isdir(path):
        results = process_directory(
            path,
            args.target_width,
            args.target_height,
            args.mode,
            args.check_only,
            args.recursive
        )
        print(f"\n处理完成: 成功 {results['success']}, 失败 {results['failed']}")
    else:
        success = process_image(
            path,
            args.target_width,
            args.target_height,
            args.mode,
            args.check_only,
            args.force
        )
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
