#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_TIMEOUT_SECONDS = 600
DEFAULT_FAL_START_TIMEOUT_SECONDS = 60


def default_timeout():
    value = os.environ.get("ANXIN_REQUEST_TIMEOUT")
    if not value:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        timeout = int(value)
    except ValueError:
        raise ValueError("ANXIN_REQUEST_TIMEOUT 必须是整数秒数")
    if timeout <= 0:
        raise ValueError("ANXIN_REQUEST_TIMEOUT 必须大于 0")
    return timeout


def parse_args():
    parser = argparse.ArgumentParser(description="调用安信 gpt-image-2 兼容接口生成图片")
    parser.add_argument("--provider", default="t8", choices=["t8", "fal"], help="生图通道，默认 t8")
    parser.add_argument("--fallback-provider", default="none", choices=["none", "fal"], help="t8 失败后的兜底通道，默认 none")
    parser.add_argument("--prompt", help="图片生成提示词")
    parser.add_argument("--size", default="1024x1024", help="图片尺寸，例如 1024x1024 或 auto")
    parser.add_argument("--quality", default="auto", choices=["low", "medium", "high", "auto"], help="图片质量")
    parser.add_argument("--model", default="gpt-image-2", help="模型名称")
    parser.add_argument("--t8-fallback-model", default="gpt-image-2-all", help="T8 主模型失败后的兜底模型，默认 gpt-image-2-all；设为 none 禁用")
    parser.add_argument("--t8-fallback-size", default="auto", help="T8 兜底模型尺寸，默认 auto，按原始比例映射到 1K 档")
    parser.add_argument("--image", action="append", default=[], help="参考图 URL 或路径，可重复传入")
    parser.add_argument("--response-format", default="b64_json", choices=["url", "b64_json"], help="响应格式，默认 b64_json")
    parser.add_argument("--output-dir", default="outputs", help="输出目录")
    parser.add_argument("--base-url", default=os.environ.get("ANXIN_API_BASE_URL"), help="Base URL，默认读取 ANXIN_API_BASE_URL")
    parser.add_argument("--api-key", default=os.environ.get("ANXIN_API_KEY"), help="API Key，默认读取 ANXIN_API_KEY")
    parser.add_argument("--timeout", type=int, default=default_timeout(), help="请求超时时间，单位秒，默认 600")
    parser.add_argument("--poll-interval", type=int, default=5, help="异步任务轮询间隔，单位秒，默认 5")
    parser.add_argument("--sync", action="store_true", help="使用同步 /v1/images/generations 接口")
    parser.add_argument("--no-wait", action="store_true", help="异步提交后只返回 task_id，不等待结果")
    parser.add_argument("--task-id", help="查询已有异步任务，不重新提交")
    parser.add_argument("--webhook", help="异步任务回调地址，可选")
    parser.add_argument("--fail-on-task-failure", action="store_true", help="异步任务状态为 FAILURE 时使用非 0 退出码")
    parser.add_argument("--fal-base-url", default=os.environ.get("ANXIN_FAL_BASE_URL"), help="Fal 中转 Base URL，默认复用 ANXIN_API_BASE_URL")
    parser.add_argument("--fal-text-model", default="fal-ai/gpt-image-2", help="Fal 文生图模型")
    parser.add_argument("--fal-edit-model", default="fal-ai/gpt-image-2/edit", help="Fal 图像编辑模型")
    parser.add_argument("--fal-request-id", help="查询已有 Fal request_id，不重新提交")
    parser.add_argument("--fal-start-timeout", type=int, default=DEFAULT_FAL_START_TIMEOUT_SECONDS, help="Fal 任务保持 IN_QUEUE 的最长等待秒数，默认 60；设为 0 表示不限制")
    parser.add_argument("--num-images", type=int, default=1, help="Fal 生成图片数量，默认 1")
    parser.add_argument("--output-format", default="png", choices=["jpeg", "png", "webp"], help="Fal 输出格式，默认 png")
    parser.add_argument("--mask-image", help="Fal 编辑遮罩图 URL 或本地路径")
    parser.add_argument("--fal-sync-mode", action="store_true", help="Fal sync_mode=true，通常返回 data URI")
    return parser.parse_args()


def validate_size(size):
    if size == "auto":
        return

    try:
        width_text, height_text = size.lower().split("x", 1)
        width = int(width_text)
        height = int(height_text)
    except ValueError:
        raise ValueError("size 必须是 auto 或类似 1024x1024 的格式")

    long_edge = max(width, height)
    short_edge = min(width, height)
    pixels = width * height

    if long_edge > 3840:
        raise ValueError("size 最大边不能超过 3840px")
    if width % 16 != 0 or height % 16 != 0:
        raise ValueError("size 宽高都必须是 16 的倍数")
    if long_edge / short_edge > 3:
        raise ValueError("size 长边与短边比例不能超过 3:1")
    if pixels < 655360 or pixels > 8294400:
        raise ValueError("size 总像素数必须在 655360 到 8294400 之间")


def validate_t8_all_size(size):
    if size == "auto":
        return
    try:
        width, height = parse_size(size)
    except ValueError:
        raise ValueError("size 必须是 auto 或类似 1024x1024 的格式")
    if width % 16 != 0 or height % 16 != 0:
        raise ValueError("gpt-image-2-all 的 size 宽高都必须是 16 的倍数")
    if max(width, height) > 1024:
        raise ValueError("gpt-image-2-all 只支持 1K 档尺寸，最大边不能超过 1024")
    if max(width, height) / min(width, height) > 3:
        raise ValueError("gpt-image-2-all 的 size 长边与短边比例不能超过 3:1")


def parse_size(size):
    width_text, height_text = size.lower().split("x", 1)
    return int(width_text), int(height_text)


def t8_fallback_size(source_size, fallback_size):
    if fallback_size != "auto":
        return fallback_size
    if source_size == "auto":
        return "1024x1024"

    width, height = parse_size(source_size)
    ratio = width / height

    candidates = [
        ("1024x1024", 1 / 1),
        ("1024x576", 16 / 9),
        ("576x1024", 9 / 16),
        ("1024x768", 4 / 3),
        ("768x1024", 3 / 4),
        ("1024x688", 3 / 2),
        ("688x1024", 2 / 3),
    ]
    return min(candidates, key=lambda item: abs(item[1] - ratio))[0]


def build_generation_url(base_url, async_mode=False, webhook=None):
    if not base_url:
        raise ValueError("缺少 ANXIN_API_BASE_URL 或 --base-url")
    url = base_url.rstrip("/") + "/v1/images/generations"
    if not async_mode:
        return url

    query = {"async": "true"}
    if webhook:
        query["webhook"] = webhook
    return url + "?" + urllib.parse.urlencode(query)


def build_task_url(base_url, task_id):
    if not base_url:
        raise ValueError("缺少 ANXIN_API_BASE_URL 或 --base-url")
    if not task_id:
        raise ValueError("缺少 task_id")
    return base_url.rstrip("/") + "/v1/images/tasks/" + urllib.parse.quote(task_id)


def normalize_fal_model(model):
    return model.removeprefix("fal-ai/").strip("/")


def fal_base_url(args):
    base_url = args.fal_base_url or args.base_url
    if not base_url:
        raise ValueError("缺少 ANXIN_API_BASE_URL 或 --fal-base-url")
    return base_url.rstrip("/")


def build_fal_model_url(base_url, model):
    base = base_url.rstrip("/")
    model_path = normalize_fal_model(model)
    if base.endswith("/fal-ai"):
        return base + "/" + model_path
    return base + "/fal-ai/" + model_path


def build_fal_status_url(base_url, model, request_id):
    return base_url.rstrip("/") + "/fal/" + model.strip("/") + "/requests/" + urllib.parse.quote(request_id) + "/status"


def build_fal_result_url(base_url, model, request_id):
    return base_url.rstrip("/") + "/fal/" + model.strip("/") + "/requests/" + urllib.parse.quote(request_id)


def is_http_url(value):
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in ("http", "https")


def image_mime_type(path):
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in (".jpg", ".jpeg"):
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    raise ValueError(f"不支持的参考图格式: {path.suffix}")


def encode_local_image(path_text):
    path = Path(path_text).expanduser()
    if not path.is_file():
        raise ValueError(f"参考图文件不存在: {path_text}")

    mime_type = image_mime_type(path)
    b64_text = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{b64_text}"


def normalize_image_inputs(image_values):
    normalized = []
    for value in image_values:
        if value.startswith("data:") or is_http_url(value):
            normalized.append(value)
            continue
        normalized.append(encode_local_image(value))
    return normalized


def post_json(url, api_key, payload, timeout):
    if not api_key:
        raise ValueError("缺少 ANXIN_API_KEY 或 --api-key")

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            try:
                return json.loads(body) if body else {}
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"接口返回非 JSON 内容: {body[:500]}") from exc
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"接口返回 HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"接口请求失败: {exc}") from exc


def get_json(url, api_key, timeout):
    if not api_key:
        raise ValueError("缺少 ANXIN_API_KEY 或 --api-key")

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            try:
                return json.loads(body) if body else {}
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"接口返回非 JSON 内容: {body[:500]}") from exc
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"接口返回 HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"接口请求失败: {exc}") from exc


def safe_suffix_from_url(url):
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix in [".png", ".jpg", ".jpeg", ".webp"] else ".png"


def safe_filename_part(value):
    # 只保留常见文件名安全字符，避免任务 ID 或 request_id 中的特殊字符影响路径。
    text = str(value or "").strip()
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "-" for ch in text).strip(".-")


def download_url(url, output_path, timeout):
    # 部分静态图片域名会拒绝默认 Python User-Agent，使用常见浏览器标识提高下载成功率。
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=timeout) as image_response:
        output_path.write_bytes(image_response.read())


def decode_b64_image(value):
    # 兼容纯 base64 和 data:image/png;base64,... 两种返回格式。
    image_suffix = ".png"
    b64_text = value.strip()
    if b64_text.startswith("data:"):
        header, b64_text = b64_text.split(",", 1)
        if "image/jpeg" in header or "image/jpg" in header:
            image_suffix = ".jpg"
        elif "image/webp" in header:
            image_suffix = ".webp"

    padding = (-len(b64_text)) % 4
    if padding:
        b64_text += "=" * padding

    return base64.b64decode(b64_text), image_suffix


def save_images(response_json, output_dir, timeout, name_prefix=None):
    saved = []
    urls = []
    download_errors = []
    data_items = response_json.get("data") if isinstance(response_json, dict) else None
    if not isinstance(data_items, list):
        return saved, urls, download_errors

    safe_prefix = safe_filename_part(name_prefix)
    for index, item in enumerate(data_items, start=1):
        if not isinstance(item, dict):
            continue
        image_stem = f"image-{safe_prefix}-{index}" if safe_prefix else f"image-{index}"

        if item.get("b64_json"):
            image_bytes, image_suffix = decode_b64_image(item["b64_json"])
            image_path = output_dir / f"{image_stem}{image_suffix}"
            image_path.write_bytes(image_bytes)
            saved.append(str(image_path))
            continue

        if item.get("url"):
            url = item["url"]
            urls.append(url)
            image_path = output_dir / f"{image_stem}{safe_suffix_from_url(url)}"
            try:
                download_url(url, image_path, timeout)
                saved.append(str(image_path))
            except Exception as exc:
                download_errors.append({"url": url, "error": str(exc)})

    return saved, urls, download_errors


def write_json(output_dir, filename, value):
    path = output_dir / filename
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def extract_task_id(response_json):
    if not isinstance(response_json, dict):
        return None
    task_id = response_json.get("task_id")
    if task_id:
        return task_id
    data = response_json.get("data")
    if isinstance(data, dict):
        return data.get("task_id")
    return None


def extract_fal_request_id(response_json):
    if not isinstance(response_json, dict):
        return None
    for key in ("request_id", "requestId", "id"):
        if response_json.get(key):
            return response_json[key]
    data = response_json.get("data")
    if isinstance(data, dict):
        for key in ("request_id", "requestId", "id"):
            if data.get(key):
                return data[key]
    return None


def extract_fal_response_url(response_json):
    if not isinstance(response_json, dict):
        return None
    return response_json.get("response_url") or extract_task_data(response_json).get("response_url")


def extract_fal_status_url(response_json):
    if not isinstance(response_json, dict):
        return None
    return response_json.get("status_url") or extract_task_data(response_json).get("status_url")


def extract_task_data(response_json):
    if not isinstance(response_json, dict):
        return {}
    data = response_json.get("data")
    return data if isinstance(data, dict) else response_json


def extract_image_response_from_task(response_json):
    task_data = extract_task_data(response_json)
    image_response = task_data.get("data")
    if isinstance(image_response, dict):
        return image_response
    return {}


def extract_task_error(response_json):
    task_data = extract_task_data(response_json)
    return (
        task_data.get("fail_reason")
        or task_data.get("error")
        or task_data.get("message")
        or task_data.get("failure_reason")
    )


def extract_fal_status(response_json):
    data = extract_task_data(response_json)
    return data.get("status") or response_json.get("status")


def extract_fal_error(response_json):
    data = extract_task_data(response_json)
    return (
        data.get("error")
        or data.get("message")
        or data.get("detail")
        or data.get("failure_reason")
        or response_json.get("error")
        or response_json.get("message")
    )


def query_task(base_url, api_key, task_id, timeout):
    return get_json(build_task_url(base_url, task_id), api_key, timeout)


def poll_task(base_url, api_key, task_id, timeout, poll_interval, fail_on_task_failure=False):
    deadline = time.monotonic() + timeout
    last_response = None

    while True:
        last_response = query_task(base_url, api_key, task_id, timeout)
        task_data = extract_task_data(last_response)
        status = task_data.get("status")

        if status == "SUCCESS":
            return last_response
        if status == "FAILURE":
            if fail_on_task_failure:
                fail_reason = extract_task_error(last_response) or "异步任务失败"
                raise RuntimeError(f"异步任务失败: {fail_reason}")
            return last_response

        if time.monotonic() >= deadline:
            progress = task_data.get("progress", "")
            raise TimeoutError(f"异步任务仍未完成: task_id={task_id} status={status} progress={progress}")

        time.sleep(max(1, poll_interval))


def build_payload(args, model=None, size=None):
    if not args.prompt:
        raise ValueError("缺少 --prompt")

    payload = {
        "model": model or args.model,
        "prompt": args.prompt,
        "size": size or args.size,
        "quality": args.quality,
        "response_format": args.response_format,
    }
    if args.image:
        payload["image"] = normalize_image_inputs(args.image)
    return payload


def fal_image_size(size):
    presets = {
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
        "auto",
    }
    if size in presets:
        return size
    width_text, height_text = size.lower().split("x", 1)
    return {"width": int(width_text), "height": int(height_text)}


def build_fal_payload(args):
    if not args.prompt:
        raise ValueError("缺少 --prompt")
    if args.num_images <= 0:
        raise ValueError("--num-images 必须大于 0")

    payload = {
        "prompt": args.prompt,
        "image_size": fal_image_size(args.size),
        "quality": args.quality,
        "num_images": args.num_images,
        "output_format": args.output_format,
    }
    if args.fal_sync_mode:
        payload["sync_mode"] = True

    if args.image:
        payload["image_urls"] = normalize_image_inputs(args.image)
    if args.mask_image:
        payload["mask_url"] = normalize_image_inputs([args.mask_image])[0]

    return payload


def fal_model_for_args(args):
    return args.fal_edit_model if args.image else args.fal_text_model


def query_fal_status(base_url, api_key, model, request_id, timeout, status_url=None):
    return get_json(status_url or build_fal_status_url(base_url, model, request_id), api_key, timeout)


def query_fal_result(base_url, api_key, model, request_id, timeout, response_url=None):
    return get_json(response_url or build_fal_result_url(base_url, model, request_id), api_key, timeout)


def poll_fal_request(
    base_url,
    api_key,
    model,
    request_id,
    timeout,
    poll_interval,
    fail_on_task_failure=False,
    status_url=None,
    response_url=None,
    start_timeout=DEFAULT_FAL_START_TIMEOUT_SECONDS,
):
    deadline = time.monotonic() + timeout
    start_deadline = time.monotonic() + start_timeout if start_timeout > 0 else None
    last_response = None

    while True:
        last_response = query_fal_status(base_url, api_key, model, request_id, timeout, status_url=status_url)
        status = extract_fal_status(last_response)

        if status in ("COMPLETED", "SUCCESS"):
            return query_fal_result(base_url, api_key, model, request_id, timeout, response_url=response_url)
        if status in ("FAILED", "FAILURE", "ERROR"):
            if fail_on_task_failure:
                fail_reason = extract_fal_error(last_response) or "Fal 异步任务失败"
                raise RuntimeError(f"Fal 异步任务失败: {fail_reason}")
            return last_response
        if status in ("IN_QUEUE", "QUEUED", "PENDING") and start_deadline and time.monotonic() >= start_deadline:
            return last_response

        if time.monotonic() >= deadline:
            raise TimeoutError(f"Fal 异步任务仍未完成: request_id={request_id} status={status}")

        time.sleep(max(1, poll_interval))


def extract_fal_image_response(response_json):
    if not isinstance(response_json, dict):
        return {}

    candidates = []
    data = response_json.get("data")
    if isinstance(data, dict):
        candidates.append(data)
        nested = data.get("data")
        if isinstance(nested, dict):
            candidates.append(nested)
    candidates.append(response_json)

    for candidate in candidates:
        images = candidate.get("images")
        if isinstance(images, list):
            return {"data": images}

        image = candidate.get("image")
        if isinstance(image, dict):
            return {"data": [image]}

        raw_data = candidate.get("data")
        if isinstance(raw_data, list):
            return {"data": raw_data}

    return {}


def run_fal(args, output_dir, timestamp, fallback_from=None):
    base_url = fal_base_url(args)
    model = fal_model_for_args(args)

    if args.fal_request_id:
        request_id = args.fal_request_id
        response_json = poll_fal_request(
            base_url,
            args.api_key,
            model,
            request_id,
            args.timeout,
            args.poll_interval,
            fail_on_task_failure=args.fail_on_task_failure,
            start_timeout=args.fal_start_timeout,
        )
        response_path = write_json(output_dir, f"fal-{request_id}-{timestamp}.json", response_json)
        submit_path = None
    else:
        submit_response = post_json(
            build_fal_model_url(base_url, model),
            args.api_key,
            build_fal_payload(args),
            args.timeout,
        )
        submit_path = write_json(output_dir, f"fal-submit-{timestamp}.json", submit_response)
        request_id = extract_fal_request_id(submit_response)
        status_url = extract_fal_status_url(submit_response)
        response_url = extract_fal_response_url(submit_response)
        if not request_id:
            raise RuntimeError(f"Fal 提交未返回 request_id: {json.dumps(submit_response, ensure_ascii=False)}")
        if args.no_wait:
            result = {
                "provider": "fal",
                "mode": "fal_async_submit",
                "fallback_from": fallback_from,
                "request_id": request_id,
                "status_url": status_url,
                "response_url": response_url,
                "fal_model": model,
                "task_submit_path": submit_path,
                "timeout": args.timeout,
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result

        response_json = poll_fal_request(
            base_url,
            args.api_key,
            model,
            request_id,
            args.timeout,
            args.poll_interval,
            fail_on_task_failure=args.fail_on_task_failure,
            status_url=status_url,
            response_url=response_url,
            start_timeout=args.fal_start_timeout,
        )
        response_path = write_json(output_dir, f"fal-{request_id}-{timestamp}.json", response_json)

    image_response = extract_fal_image_response(response_json)
    image_paths, image_urls, download_errors = save_images(image_response, output_dir, args.timeout, request_id or timestamp)
    status = extract_fal_status(response_json)

    result = {
        "provider": "fal",
        "mode": "fal_async",
        "fallback_from": fallback_from,
        "request_id": request_id,
        "fal_model": model,
        "task_status": status,
        "task_error": extract_fal_error(response_json),
        "status_url": extract_fal_status_url(response_json),
        "response_url": extract_fal_response_url(response_json),
        "task_submit_path": submit_path,
        "response_path": response_path,
        "image_paths": image_paths,
        "image_urls": image_urls,
        "download_errors": download_errors,
        "size": args.size,
        "quality": args.quality,
        "timeout": args.timeout,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def run_t8(args, output_dir, timestamp, model=None, size=None, label=""):
    task_id = args.task_id
    task_submit_path = None
    effective_model = model or args.model
    effective_size = size or args.size
    suffix = f"-{label}" if label else ""

    if args.task_id:
        response_json = query_task(args.base_url, args.api_key, args.task_id, args.timeout)
        response_path = write_json(output_dir, f"task-{args.task_id}{suffix}-{timestamp}.json", response_json)
    elif args.sync:
        response_json = post_json(
            build_generation_url(args.base_url),
            args.api_key,
            build_payload(args, model=effective_model, size=effective_size),
            args.timeout,
        )
        response_path = write_json(output_dir, f"response{suffix}-{timestamp}.json", response_json)
    else:
        submit_response = post_json(
            build_generation_url(args.base_url, async_mode=True, webhook=args.webhook),
            args.api_key,
            build_payload(args, model=effective_model, size=effective_size),
            args.timeout,
        )
        task_submit_path = write_json(output_dir, f"task-submit{suffix}-{timestamp}.json", submit_response)
        task_id = extract_task_id(submit_response)
        if not task_id:
            raise RuntimeError(f"异步提交未返回 task_id: {json.dumps(submit_response, ensure_ascii=False)}")
        if args.no_wait:
            result = {
                "provider": "t8",
                "mode": "async_submit",
                "task_id": task_id,
                "task_submit_path": task_submit_path,
                "model": effective_model,
                "size": effective_size,
                "quality": args.quality,
                "response_format": args.response_format,
                "timeout": args.timeout,
            }
            return result
        response_json = poll_task(
            args.base_url,
            args.api_key,
            task_id,
            args.timeout,
            args.poll_interval,
            fail_on_task_failure=args.fail_on_task_failure,
        )
        response_path = write_json(output_dir, f"task-{task_id}{suffix}-{timestamp}.json", response_json)

    image_response = extract_image_response_from_task(response_json) if (args.task_id or not args.sync) else response_json
    image_paths, image_urls, download_errors = save_images(image_response, output_dir, args.timeout, task_id or timestamp)
    task_data = extract_task_data(response_json)

    result = {
        "provider": "t8",
        "mode": "sync" if args.sync else "async",
        "task_id": task_id,
        "task_status": task_data.get("status"),
        "task_progress": task_data.get("progress"),
        "task_error": extract_task_error(response_json),
        "task_submit_path": task_submit_path,
        "response_path": response_path,
        "image_paths": image_paths,
        "image_urls": image_urls,
        "download_errors": download_errors,
        "model": effective_model,
        "size": effective_size,
        "quality": args.quality,
        "response_format": args.response_format,
        "timeout": args.timeout,
    }
    return result


def should_fallback_to_fal(result):
    return result.get("task_status") == "FAILURE"


def should_fallback_to_t8_model(args, result):
    return (
        args.t8_fallback_model
        and args.t8_fallback_model != "none"
        and args.model != args.t8_fallback_model
        and result.get("task_status") == "FAILURE"
    )


def main():
    args = parse_args()
    if args.poll_interval <= 0:
        raise ValueError("--poll-interval 必须大于 0")
    if args.timeout <= 0:
        raise ValueError("--timeout 必须大于 0")
    if args.t8_fallback_model != "none" and args.t8_fallback_size != "auto":
        validate_t8_all_size(args.t8_fallback_size)
    if not args.task_id and not args.fal_request_id:
        if args.provider == "t8" and args.model == "gpt-image-2-all":
            validate_t8_all_size(args.size)
        else:
            validate_size(args.size)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    if args.provider == "fal":
        run_fal(args, output_dir, timestamp)
        return

    try:
        result = run_t8(args, output_dir, timestamp)
    except Exception as exc:
        if args.t8_fallback_model != "none" and not args.task_id:
            try:
                result = run_t8(
                    args,
                    output_dir,
                    timestamp,
                    model=args.t8_fallback_model,
                    size=t8_fallback_size(args.size, args.t8_fallback_size),
                    label="fallback",
                )
                result["fallback_from"] = f"t8_error: {exc}"
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return
            except Exception as fallback_exc:
                if args.fallback_provider == "fal" and not args.sync:
                    run_fal(args, output_dir, timestamp, fallback_from=f"t8_fallback_error: {fallback_exc}")
                    return
                raise
        if args.fallback_provider == "fal" and not args.task_id and not args.sync:
            run_fal(args, output_dir, timestamp, fallback_from=f"t8_error: {exc}")
            return
        raise

    if not args.task_id and not args.sync and should_fallback_to_t8_model(args, result):
        fallback_result = run_t8(
            args,
            output_dir,
            timestamp,
            model=args.t8_fallback_model,
            size=t8_fallback_size(args.size, args.t8_fallback_size),
            label="fallback",
        )
        fallback_result["fallback_from"] = f"t8_failure: {result.get('task_error')}"
        print(json.dumps(fallback_result, ensure_ascii=False, indent=2))
        return

    if (
        args.fallback_provider == "fal"
        and not args.task_id
        and not args.sync
        and should_fallback_to_fal(result)
    ):
        run_fal(args, output_dir, timestamp, fallback_from=f"t8_failure: {result.get('task_error')}")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)
