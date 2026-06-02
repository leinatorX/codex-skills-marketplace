import argparse
import base64
import json
import mimetypes
import os
from datetime import datetime
from pathlib import Path
import sys
import urllib.error
import urllib.request


def parse_timeout():
    value = os.environ.get("ANXIN_REQUEST_TIMEOUT")
    if not value:
        return 600
    try:
        timeout = int(value)
    except ValueError as exc:
        raise ValueError("ANXIN_REQUEST_TIMEOUT 必须是整数秒数") from exc
    if timeout <= 0:
        raise ValueError("ANXIN_REQUEST_TIMEOUT 必须大于 0")
    return timeout


def parse_args():
    parser = argparse.ArgumentParser(description="通过安信 Gemini 接口审核短视频发布素材合规风险")
    parser.add_argument("--video", action="append", default=[], help="本地短视频文件路径，可重复传入")
    parser.add_argument("--image", action="append", default=[], help="本地分镜图、封面图或截图路径，可重复传入")
    parser.add_argument("--script-text", default="", help="直接传入的文稿、口播稿、字幕稿或分镜说明")
    parser.add_argument("--script-file", action="append", default=[], help="文稿文件路径，支持 txt/md/srt/json 等纯文本文件，可重复传入")
    parser.add_argument("--title", default="", help="拟发布标题")
    parser.add_argument("--description", default="", help="拟发布文案、简介或补充说明")
    parser.add_argument("--hashtags", default="", help="拟发布话题，多个话题可用逗号分隔")
    parser.add_argument("--platform", choices=["both", "wechat", "douyin"], default="both", help="审核平台")
    parser.add_argument("--model", default="gemini-3.1-flash-lite-preview-thinking-high", help="多模态审核模型")
    parser.add_argument("--base-url", default=os.environ.get("ANXIN_API_BASE_URL"), help="Base URL，默认读取 ANXIN_API_BASE_URL")
    parser.add_argument("--api-key", default=os.environ.get("ANXIN_API_KEY"), help="API Key，默认读取 ANXIN_API_KEY")
    parser.add_argument("--timeout", type=int, default=parse_timeout(), help="请求超时时间，单位秒")
    parser.add_argument("--max-tokens", type=int, default=4000, help="模型最大输出 token 数")
    parser.add_argument("--temperature", type=float, default=0.2, help="模型温度")
    parser.add_argument("--output-dir", default="./outputs", help="输出目录")
    parser.add_argument("--max-file-size-mb", type=int, default=80, help="单个视频或图片最大体积提醒阈值，超过后仍会提交")
    parser.add_argument("--max-text-chars", type=int, default=20000, help="文稿最大读取字符数，超过后自动截断")
    return parser.parse_args()


def ensure_has_input(args):
    has_media = bool(args.video or args.image)
    has_text = bool(args.script_text.strip() or args.script_file or args.title.strip() or args.description.strip() or args.hashtags.strip())
    if not has_media and not has_text:
        raise ValueError("至少需要提供 --video、--image、--script-text、--script-file、--title 或 --description 中的一项")


def build_chat_url(base_url):
    if not base_url:
        raise ValueError("缺少 ANXIN_API_BASE_URL 或 --base-url")
    return base_url.rstrip("/") + "/v1/chat/completions"


def detect_mime(path, fallback):
    mime_type, _ = mimetypes.guess_type(str(path))
    return mime_type or fallback


def file_to_data_url(path, fallback_mime):
    mime_type = detect_mime(path, fallback_mime)
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}", mime_type


def resolve_file(path_text, label):
    path = Path(path_text).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"{label}不存在：{path}")
    if not path.is_file():
        raise ValueError(f"{label}不是文件：{path}")
    return path


def collect_media(paths, media_type, fallback_mime, max_file_size_mb):
    items = []
    for path_text in paths:
        path = resolve_file(path_text, "素材文件")
        file_size_mb = path.stat().st_size / 1024 / 1024
        if file_size_mb > max_file_size_mb:
            print(f"警告：{media_type} {path} 大小 {file_size_mb:.2f} MB 超过提醒阈值 {max_file_size_mb} MB，接口可能拒绝请求。", file=sys.stderr)
        data_url, mime_type = file_to_data_url(path, fallback_mime)
        items.append({
            "type": media_type,
            "path": str(path),
            "mime_type": mime_type,
            "file_size_mb": file_size_mb,
            "data_url": data_url,
        })
    return items


def read_text_file(path_text, max_text_chars):
    path = resolve_file(path_text, "文稿文件")
    raw = path.read_bytes()
    text = None
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode("utf-8", errors="replace")
    truncated = len(text) > max_text_chars
    if truncated:
        text = text[:max_text_chars] + "\n\n[文稿超过字符限制，后续内容已截断]"
    return {
        "path": str(path),
        "chars": len(text),
        "truncated": truncated,
        "text": text,
    }


def collect_texts(args):
    items = []
    if args.script_text.strip():
        text = args.script_text.strip()
        truncated = len(text) > args.max_text_chars
        if truncated:
            text = text[:args.max_text_chars] + "\n\n[文稿超过字符限制，后续内容已截断]"
        items.append({
            "path": "inline",
            "chars": len(text),
            "truncated": truncated,
            "text": text,
        })
    for path_text in args.script_file:
        items.append(read_text_file(path_text, args.max_text_chars))
    return items


def platform_label(platform):
    if platform == "wechat":
        return "微信视频号"
    if platform == "douyin":
        return "抖音"
    return "微信视频号和抖音"


def material_summary(media_items, text_items):
    videos = [item for item in media_items if item["type"] == "video"]
    images = [item for item in media_items if item["type"] == "image"]
    lines = [
        f"视频数量：{len(videos)}",
        f"分镜图/图片数量：{len(images)}",
        f"文稿数量：{len(text_items)}",
    ]
    for index, item in enumerate(videos, 1):
        lines.append(f"视频 {index}：{item['path']}，{item['mime_type']}，{item['file_size_mb']:.2f} MB")
    for index, item in enumerate(images, 1):
        lines.append(f"图片 {index}：{item['path']}，{item['mime_type']}，{item['file_size_mb']:.2f} MB")
    for index, item in enumerate(text_items, 1):
        lines.append(f"文稿 {index}：{item['path']}，{item['chars']} 字符，截断：{item['truncated']}")
    return "\n".join(lines)


def text_material_block(text_items):
    if not text_items:
        return "未提供"
    blocks = []
    for index, item in enumerate(text_items, 1):
        blocks.append(f"【文稿 {index}：{item['path']}】\n{item['text']}")
    return "\n\n".join(blocks)


def build_prompt(args, media_items, text_items):
    return f"""你是短视频发布前合规审核助手。请严格参考微信视频号运营规范和抖音社区自律公约，对用户提供的发布素材进行审核。

审核平台：{platform_label(args.platform)}
素材概况：
{material_summary(media_items, text_items)}

拟发布标题：{args.title or "未提供"}
拟发布文案：{args.description or "未提供"}
拟发布话题：{args.hashtags or "未提供"}

文稿、口播稿、字幕稿或分镜说明：
{text_material_block(text_items)}

请同时检查视频画面、分镜图、封面图、字幕、口播、背景文字、人物动作、品牌/商标、隐私信息、音乐/影视素材、标题、文案、话题和文稿承诺。重点关注：
1. 违法违规、政治与公共安全、暴力恐怖、血腥惊悚、危险动作、自残自杀、色情低俗、未成年人保护。
2. 虚假信息、标题党、夸大宣传、诱导互动、站外导流、二维码/联系方式、私域交易、诈骗或虚假福利。
3. 医疗、金融、法律、教育、招聘、公益救助、消防应急等需要资质或风险提示的内容。
4. 版权、肖像、隐私、商标、搬运、未经授权音乐或影视片段。
5. 视频、文稿和分镜图之间是否存在承诺不一致、画面误导、资质缺失或平台差异风险。

请只输出 JSON 对象，不要输出 Markdown。JSON 结构必须为：
{{
  "decision": "pass|revise|reject|manual_review",
  "risk_level": "low|medium|high",
  "summary": "一句话中文结论",
  "platforms": {{
    "wechat": {{"decision": "pass|revise|reject|manual_review", "reason": "中文说明"}},
    "douyin": {{"decision": "pass|revise|reject|manual_review", "reason": "中文说明"}}
  }},
  "findings": [
    {{
      "platform": "wechat|douyin|both",
      "risk_level": "low|medium|high",
      "category": "风险类别",
      "source": "video|image|script|title|description|hashtag|cross_material",
      "evidence": "具体证据，包含视频时间、图片序号、文稿片段、标题或文案位置；无法定位时写明原因",
      "reason": "为什么可能违规或需要复核",
      "suggestion": "具体修改建议"
    }}
  ],
  "revision_plan": [
    "按优先级排列的修改动作"
  ],
  "manual_review_needed": true,
  "limitations": [
    "本次审核未覆盖或不确定的部分"
  ]
}}"""


def build_payload(args, media_items, prompt):
    content = [{"type": "text", "text": prompt}]
    for item in media_items:
        content.append({"type": "image_url", "image_url": {"url": item["data_url"]}})
    return {
        "model": args.model,
        "stream": False,
        "messages": [{"role": "user", "content": content}],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "response_format": {"type": "json_object"},
    }


def post_json(url, api_key, payload, timeout):
    if not api_key:
        raise ValueError("缺少 ANXIN_API_KEY 或 --api-key")
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"接口请求失败：HTTP {exc.code} {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"接口请求失败：{exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"接口返回不是合法 JSON：{raw[:500]}") from exc


def extract_content(response_json):
    choices = response_json.get("choices")
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("text"):
                texts.append(str(item["text"]))
        return "\n".join(texts)
    return str(content)


def parse_audit_content(content):
    if not content.strip():
        return {"decision": "manual_review", "risk_level": "medium", "summary": "模型未返回审核内容", "findings": [], "revision_plan": [], "manual_review_needed": True, "limitations": ["接口响应中未找到 choices[0].message.content"]}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                pass
    return {"decision": "manual_review", "risk_level": "medium", "summary": "模型返回了非 JSON 审核文本，已保留原文", "audit_text": content, "findings": [], "revision_plan": [], "manual_review_needed": True, "limitations": ["模型未按 JSON 格式输出，需要人工整理"]}


def public_media_metadata(media_items):
    return [
        {
            "type": item["type"],
            "path": item["path"],
            "mime_type": item["mime_type"],
            "file_size_mb": item["file_size_mb"],
        }
        for item in media_items
    ]


def public_text_metadata(text_items):
    return [
        {
            "path": item["path"],
            "chars": item["chars"],
            "truncated": item["truncated"],
        }
        for item in text_items
    ]


def render_markdown(audit, metadata):
    lines = [
        "# 安信短视频素材审核报告",
        "",
        "## 结论",
        "",
        f"- 审核结论：{audit.get('decision', 'manual_review')}",
        f"- 风险等级：{audit.get('risk_level', 'medium')}",
        f"- 摘要：{audit.get('summary', '未提供')}",
        "",
        "## 素材信息",
        "",
        f"- 平台：{metadata['platform']}",
        f"- 模型：{metadata['model']}",
        f"- 视频数量：{metadata['counts']['videos']}",
        f"- 图片数量：{metadata['counts']['images']}",
        f"- 文稿数量：{metadata['counts']['texts']}",
        "",
    ]

    for index, item in enumerate(metadata["media"], 1):
        lines.append(f"- 素材 {index}：{item['type']}，{item['path']}，{item['mime_type']}，{item['file_size_mb']:.2f} MB")
    for index, item in enumerate(metadata["texts"], 1):
        lines.append(f"- 文稿 {index}：{item['path']}，{item['chars']} 字符，截断：{item['truncated']}")
    lines.append("")

    platforms = audit.get("platforms")
    if isinstance(platforms, dict):
        lines.extend(["## 平台判断", ""])
        for name, result in platforms.items():
            if isinstance(result, dict):
                lines.append(f"- {name}：{result.get('decision', 'manual_review')}，{result.get('reason', '未提供原因')}")
        lines.append("")

    findings = audit.get("findings") or []
    lines.extend(["## 主要风险", ""])
    if findings:
        for index, item in enumerate(findings, 1):
            if not isinstance(item, dict):
                continue
            lines.extend(
                [
                    f"### {index}. {item.get('category', '未分类风险')}",
                    "",
                    f"- 平台：{item.get('platform', 'both')}",
                    f"- 等级：{item.get('risk_level', 'medium')}",
                    f"- 来源：{item.get('source', '未提供')}",
                    f"- 证据：{item.get('evidence', '未提供')}",
                    f"- 原因：{item.get('reason', '未提供')}",
                    f"- 建议：{item.get('suggestion', '未提供')}",
                    "",
                ]
            )
    else:
        lines.extend(["未发现模型明确列出的风险点。", ""])

    revision_plan = audit.get("revision_plan") or []
    lines.extend(["## 修改建议", ""])
    if revision_plan:
        for index, item in enumerate(revision_plan, 1):
            lines.append(f"{index}. {item}")
    else:
        lines.append("暂无具体修改建议。")
    lines.append("")

    limitations = audit.get("limitations") or []
    if limitations:
        lines.extend(["## 局限与复核", ""])
        for item in limitations:
            lines.append(f"- {item}")
        lines.append("")

    if audit.get("audit_text"):
        lines.extend(["## 模型原文", "", str(audit["audit_text"]), ""])

    return "\n".join(lines)


def main():
    args = parse_args()
    ensure_has_input(args)

    media_items = []
    media_items.extend(collect_media(args.video, "video", "video/mp4", args.max_file_size_mb))
    media_items.extend(collect_media(args.image, "image", "image/png", args.max_file_size_mb))
    text_items = collect_texts(args)

    prompt = build_prompt(args, media_items, text_items)
    payload = build_payload(args, media_items, prompt)
    response_json = post_json(build_chat_url(args.base_url), args.api_key, payload, args.timeout)
    content = extract_content(response_json)
    audit = parse_audit_content(content)

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    media_public = public_media_metadata(media_items)
    text_public = public_text_metadata(text_items)
    metadata = {
        "platform": args.platform,
        "model": args.model,
        "media": media_public,
        "texts": text_public,
        "counts": {
            "videos": len([item for item in media_public if item["type"] == "video"]),
            "images": len([item for item in media_public if item["type"] == "image"]),
            "texts": len(text_public),
        },
    }
    audit_with_meta = {"metadata": metadata, "audit": audit}

    raw_path = output_dir / f"response-{timestamp}.json"
    audit_json_path = output_dir / f"audit-{timestamp}.json"
    audit_md_path = output_dir / f"audit-{timestamp}.md"

    raw_path.write_text(json.dumps(response_json, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_json_path.write_text(json.dumps(audit_with_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_md_path.write_text(render_markdown(audit, metadata), encoding="utf-8")

    print(json.dumps({
        "decision": audit.get("decision", "manual_review"),
        "risk_level": audit.get("risk_level", "medium"),
        "summary": audit.get("summary", ""),
        "audit_json": str(audit_json_path),
        "audit_markdown": str(audit_md_path),
        "raw_response": str(raw_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        sys.exit(1)
