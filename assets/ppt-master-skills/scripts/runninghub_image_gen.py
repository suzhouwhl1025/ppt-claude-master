#!/usr/bin/env python3
"""
RunningHub Image Generator for PPT Master
使用 RunningHub API 生成高质量图片，替换 Gemini Nano Banana

Environment variables:
  RUNNINGHUB_API_KEY  (required) RunningHub API Key
    - 获取地址: https://www.runninghub.cn/enterprise-api/sharedApi
    - 注册地址: https://www.runninghub.cn
    - 充值地址: https://www.runninghub.cn/vip-rights/4

Usage:
  python runninghub_image_gen.py "prompt text" -o output_dir --aspect_ratio 16:9
  python runninghub_image_gen.py --check  # 检查账户状态
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

# RunningHub API 配置
BASE_URL = "https://www.runninghub.cn/openapi/v2"
ACCOUNT_STATUS_URL = "https://www.runninghub.cn/uc/openapi/accountStatus"
POLL_ENDPOINT = "/query"

# 默认使用的文生图端点（全能图片PRO）
DEFAULT_ENDPOINT = "rhart-image-n-pro-official/text-to-image"

# 支持的宽高比映射到 RunningHub 尺寸
ASPECT_RATIO_MAP = {
    "1:1": "1:1",
    "16:9": "16:9",
    "9:16": "9:16",
    "4:3": "4:3",
    "3:4": "3:4",
    "21:9": "21:9",
}


# ============================================================================
# API Key 解析
# ============================================================================

def resolve_api_key(provided_key: str | None = None) -> str | None:
    """解析 API Key，优先级：命令行参数 > 环境变量 > OpenClaw 配置"""
    # 1. 命令行提供的 key
    if provided_key and provided_key not in ("", "your_api_key_here", "<your_api_key>"):
        return provided_key.strip()

    # 2. 环境变量
    env_key = os.environ.get("RUNNINGHUB_API_KEY", "").strip()
    if env_key:
        return env_key

    # 3. OpenClaw 配置
    cfg_path = Path.home() / ".openclaw" / "openclaw.json"
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            entry = cfg.get("skills", {}).get("entries", {}).get("runninghub", {})
            api_key = entry.get("apiKey") or entry.get("env", {}).get("RUNNINGHUB_API_KEY")
            if api_key:
                return api_key.strip()
        except Exception:
            pass

    return None


def require_api_key(provided_key: str | None = None) -> str:
    """获取 API Key，如果不存在则退出并提示"""
    key = resolve_api_key(provided_key)
    if key:
        return key

    print("=" * 60, file=sys.stderr)
    print("❌ 错误: 未找到 RunningHub API Key", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)
    print("📋 请按以下步骤获取 API Key:", file=sys.stderr)
    print(file=sys.stderr)
    print("  1. 访问 https://www.runninghub.cn 注册账户", file=sys.stderr)
    print("  2. 访问 https://www.runninghub.cn/enterprise-api/sharedApi 创建 API Key", file=sys.stderr)
    print("  3. 访问 https://www.runninghub.cn/vip-rights/4 充值账户", file=sys.stderr)
    print(file=sys.stderr)
    print("📝 配置方式 (三选一):", file=sys.stderr)
    print("  方式1: 在对话中提供 API Key", file=sys.stderr)
    print("  方式2: 设置环境变量 export RUNNINGHUB_API_KEY='你的KEY'", file=sys.stderr)
    print("  方式3: 安装 runninghub skill 后自动配置", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    sys.exit(1)


def check_account_status(api_key: str) -> dict:
    """检查账户状态"""
    import urllib.request
    import urllib.error

    data = json.dumps({"apiKey": api_key}).encode("utf-8")
    req = urllib.request.Request(
        ACCOUNT_STATUS_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "message": e.read().decode("utf-8")}
    except Exception as e:
        return {"error": "Request failed", "message": str(e)}


# ============================================================================
# RunningHub API 调用
# ============================================================================

def call_api(api_key: str, endpoint: str, params: dict) -> dict:
    """调用 RunningHub API"""
    import urllib.request
    import urllib.error

    url = f"{BASE_URL}/{endpoint}"
    payload = {
        "apiKey": api_key,
        "parameter": params
    }
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}", "message": error_body}
    except Exception as e:
        return {"error": "Request failed", "message": str(e)}


def poll_task(api_key: str, task_id: str, max_wait: int = 300) -> dict:
    """轮询任务状态直到完成或超时"""
    url = f"{BASE_URL}{POLL_ENDPOINT}"
    payload = {"apiKey": api_key, "taskId": task_id}
    data = json.dumps(payload).encode("utf-8")

    start_time = time.time()
    interval = 3

    while time.time() - start_time < max_wait:
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            import urllib.request
            import urllib.error
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            status = result.get("data", {}).get("status", "")
            print(f"  状态: {status}", flush=True)

            if status == "completed":
                return result
            elif status in ("failed", "error", "cancelled"):
                return {"error": f"Task {status}", "data": result}

            time.sleep(interval)
        except Exception as e:
            print(f"  轮询异常: {e}", flush=True)
            time.sleep(interval)

    return {"error": "Timeout", "message": f"任务超过 {max_wait} 秒未完成"}


def download_image(url: str, output_path: str) -> bool:
    """下载图片"""
    import urllib.request
    import urllib.error

    try:
        # 处理 data URI
        if url.startswith("data:"):
            # Base64 编码的图片数据
            header, data = url.split(",", 1)
            img_data = base64.b64decode(data)
            with open(output_path, "wb") as f:
                f.write(img_data)
            return True

        # 下载 URL 图片
        with urllib.request.urlopen(url, timeout=120) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  下载失败: {e}", file=sys.stderr)
        return False


# ============================================================================
# 图片生成
# ============================================================================

def generate_image(
    prompt: str,
    api_key: str,
    output_dir: str = None,
    filename: str = None,
    aspect_ratio: str = "1:1",
    endpoint: str = DEFAULT_ENDPOINT,
    negative_prompt: str = None,
    image_size: str = "1K"
) -> str:
    """生成图片并返回保存路径"""

    # 解析尺寸
    size_map = {"512px": "512", "1K": "1024", "2K": "2048", "4K": "4096"}
    resolution = size_map.get(image_size, "1024")

    # 构建参数
    params = {
        "prompt": prompt,
        "aspectRatio": ASPECT_RATIO_MAP.get(aspect_ratio, "1:1"),
        "resolution": resolution,
    }
    if negative_prompt:
        params["negativePrompt"] = negative_prompt

    print(f"[RunningHub Image Generator]", flush=True)
    print(f"  端点: {endpoint}", flush=True)
    print(f"  提示词: {prompt[:80]}{'...' if len(prompt) > 80 else ''}", flush=True)
    print(f"  宽高比: {aspect_ratio}", flush=True)
    print(f"  分辨率: {resolution}", flush=True)
    print(flush=True)

    # 提交任务
    print("  提交任务...", flush=True)
    result = call_api(api_key, endpoint, params)

    if "error" in result:
        raise RuntimeError(f"提交任务失败: {result.get('error')} - {result.get('message', '')}")

    task_id = result.get("data", {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"未获取到任务ID: {result}")

    print(f"  任务ID: {task_id}", flush=True)
    print("  等待生成...", flush=True)

    # 轮询等待完成
    poll_result = poll_task(api_key, task_id)

    if "error" in poll_result:
        raise RuntimeError(f"任务执行失败: {poll_result.get('error')} - {poll_result.get('message', '')}")

    # 获取结果
    outputs = poll_result.get("data", {}).get("outputs", [])
    if not outputs:
        raise RuntimeError("未获取到生成结果")

    image_url = outputs[0].get("imageUrl") or outputs[0].get("url")
    if not image_url:
        raise RuntimeError(f"结果中无图片URL: {outputs[0]}")

    # 保存图片
    output_path = Path(output_dir or ".")
    output_path.mkdir(parents=True, exist_ok=True)

    if filename:
        final_path = output_path / f"{filename}.png"
    else:
        safe_name = "".join(c for c in prompt if c.isalnum() or c in (" ", "_")).rstrip()[:30]
        safe_name = safe_name.replace(" ", "_") or "generated"
        final_path = output_path / f"{safe_name}_{int(time.time())}.png"

    print(f"  下载图片...", flush=True)
    if download_image(image_url, str(final_path)):
        print(f"✅ 图片已保存: {final_path}", flush=True)
        return str(final_path)
    else:
        raise RuntimeError("图片下载失败")


# ============================================================================
# 主入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="使用 RunningHub API 生成图片"
    )
    parser.add_argument(
        "prompt", nargs="?", default=None,
        help="图片生成提示词"
    )
    parser.add_argument(
        "--api_key", "-k", default=None,
        help="RunningHub API Key"
    )
    parser.add_argument(
        "--aspect_ratio", "-r", default="1:1",
        choices=list(ASPECT_RATIO_MAP.keys()),
        help=f"图片宽高比，默认 1:1"
    )
    parser.add_argument(
        "--image_size", "-s", default="1K",
        choices=["512px", "1K", "2K", "4K"],
        help="图片尺寸，默认 1K (1024x1024)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="输出目录"
    )
    parser.add_argument(
        "--filename", "-f", default=None,
        help="输出文件名（不含扩展名）"
    )
    parser.add_argument(
        "--endpoint", "-e", default=DEFAULT_ENDPOINT,
        help="RunningHub 端点"
    )
    parser.add_argument(
        "--negative_prompt", "-n", default=None,
        help="反向提示词"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="检查账户状态"
    )

    args = parser.parse_args()

    # 检查账户状态
    if args.check:
        api_key = require_api_key(args.api_key)
        print("🔍 检查账户状态...", flush=True)
        status = check_account_status(api_key)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    # 生成图片
    if not args.prompt:
        print("错误: 请提供提示词", file=sys.stderr)
        print("用法: python runninghub_image_gen.py '一只可爱的小狗' -o ./images", file=sys.stderr)
        sys.exit(1)

    api_key = require_api_key(args.api_key)

    try:
        output_path = generate_image(
            prompt=args.prompt,
            api_key=api_key,
            output_dir=args.output,
            filename=args.filename,
            aspect_ratio=args.aspect_ratio,
            endpoint=args.endpoint,
            negative_prompt=args.negative_prompt,
            image_size=args.image_size
        )
        print(f"\n🎉 完成! 图片路径: {output_path}")
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
