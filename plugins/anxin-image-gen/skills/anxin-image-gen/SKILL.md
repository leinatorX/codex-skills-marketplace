---
name: anxin-image-gen
description: Generate images for OpenClaw through the Anxin gpt-image-2 compatible image API. Use when the user asks OpenClaw to create, generate, redraw, produce, edit, modify, download, or save images with prompts, reference images, sizes, quality levels, or OpenAI Dall-e style /v1/images/generations requests. Also use for Chinese requests such as 安信图片生成器, 图片生成, AI出图, 生图, 改图, 局部编辑, 参考图生成, 图生图, 公众号封面, 公众号配图, 小红书封面, 视频号封面, 抖音封面, 海报生成, 中文海报, 知识图谱, 信息图, 消防车改图, and OpenClaw 图片生成.
---

# 安信图片生成器

## 目标

使用安信 `gpt-image-2` 兼容异步接口为 OpenClaw 生成图片。优先走随技能提供的脚本，避免在对话里暴露 API Key。默认只走 T8 OpenAI Images 兼容接口；T8 主模型 `gpt-image-2` 失败后，先回退到 `gpt-image-2-all` 并按原始比例映射到 1K 档图片。fal.ai GPT-Image2 通道仅在手动指定 `--provider fal` 或显式传入 `--fallback-provider fal` 时使用。

详细接口约束见 `references/api.md`。需要优化提示词、选择平台比例、生成中文海报或封面时，读取 `references/prompting.md`。

## 快速流程

1. 确认运行环境存在：
   - `ANXIN_API_BASE_URL`：服务商提供的 Base URL，不要包含末尾 `/v1/images/generations`。
   - `ANXIN_API_KEY`：Bearer API Key。
   - `ANXIN_REQUEST_TIMEOUT`：可选，请求超时时间，单位秒；默认 `600`。
2. 从用户需求提取使用场景、平台、主题、文字、主体、风格、尺寸、质量和参考图。需要把简短需求改写成完整视觉设计任务书时，按 `references/prompting.md` 组织提示词。
   - 如无特殊要求，提交给接口的 `prompt` 一律使用简体中文编写。
   - 只有用户明确要求英文提示词、目标图片必须包含英文文案、或专有英文术语不可翻译时，才在提示词中保留英文。
3. 校验尺寸：最大边不超过 `3840px`，宽高都是 `16` 的倍数，长短边比例不超过 `3:1`，总像素数在 `655360` 到 `8294400` 之间。
4. 调用 `scripts/generate_image.py`。默认异步提交并轮询查询结果。
5. 返回 `task_id`、图片路径、原始响应路径和关键参数。不要回显 API Key。

## 调用脚本

```bash
python scripts/generate_image.py \
  --prompt "一张写实风格的未来城市夜景" \
  --size 1024x1024 \
  --quality auto \
  --timeout 600 \
  --output-dir ./outputs
```

只走 fal GPT-Image2 通道时：

```bash
python scripts/generate_image.py \
  --provider fal \
  --prompt "一张写实风格的未来城市夜景" \
  --size 1024x1024 \
  --quality high \
  --output-dir ./outputs
```

只提交任务、不等待结果时：

```bash
python scripts/generate_image.py \
  --prompt "一张写实风格的未来城市夜景" \
  --size 1024x1024 \
  --quality high \
  --no-wait \
  --output-dir ./outputs
```

查询已有异步任务时：

```bash
python scripts/generate_image.py \
  --task-id "3dad96708a77485e97ac7ef652796d7b" \
  --output-dir ./outputs
```

带参考图时：

```bash
python scripts/generate_image.py \
  --prompt "保留主体，改成高级科技海报风格" \
  --image "/tmp/anxin-output/ref-poster.png" \
  --size 1536x1024 \
  --quality high \
  --output-dir ./outputs
```

## 参数选择

- `provider` 默认 `t8`。默认先走 `/v1/images/generations?async=true`；如果失败且 `fallback-provider=fal`，自动切到 fal GPT-Image2。
- `fallback-provider` 默认 `none`。不要自动 fallback 到 fal，除非用户明确要求；如需 T8 失败后兜底 fal，显式传 `--fallback-provider fal`。
- `model` 默认使用 `gpt-image-2`。
- `t8-fallback-model` 默认使用 `gpt-image-2-all`。这是 T8 主模型失败后的同通道兜底模型，只支持 1K 图片。
- `t8-fallback-size` 默认 `auto`。调用 `gpt-image-2-all` 时会根据原始 `size` 的比例映射到 1K 档：`1024x1024`、`1024x576`、`576x1024`、`1024x768`、`768x1024`、`1024x688`、`688x1024`。如果用户显式指定 `--t8-fallback-size`，则按指定尺寸执行。
- fal 通道实际仍使用同一个 T8 中转 Base URL 和 API Key，不直接调用 fal 官方平台。
- fal 文生图模型默认 `fal-ai/gpt-image-2`，fal 图像编辑模型默认 `fal-ai/gpt-image-2/edit`。这是当前 T8 fal 中转实际可提交的路径；fal 官方页面里的 `openai/gpt-image-2` 仅作为字段参考。
- fal 中转任务可能长时间停在 `IN_QUEUE` / “未启动”，实际可能十几到几十分钟后才完成。脚本默认等待 `60` 秒后返回 `request_id`、`status_url` 和 `response_url`，不继续挂满 600 秒；稍后用 `--fal-request-id` 查询结果。可用 `--fal-start-timeout` 调整，设为 `0` 表示不限制。
- 默认使用异步模式：`POST /v1/images/generations?async=true`，再用 `GET /v1/images/tasks/{task_id}` 查询结果。
- `--no-wait` 只提交任务并返回 `task_id`，适合 OpenClaw 外层容易超时的场景；之后用 `--task-id` 查询结果。
- `--task-id` 查询已有异步任务，不会重新提交生成请求。
- `--sync` 才使用旧的同步 `/v1/images/generations` 接口，仅作为兼容兜底。
- 服务端异步任务返回 `FAILURE` 时，默认输出失败状态 JSON 并正常退出，避免 OpenClaw 把它当作命令错误反复重新提交。只有明确需要命令失败语义时才加 `--fail-on-task-failure`。
- 只有用户明确指定其它平台兼容模型时才改 `model`。
- `quality` 默认使用 `auto`。用户要求更快或低成本时用 `low`，要求成品质量时用 `high`。
- `response_format` 默认使用 `b64_json`，但异步查询结果可能仍只返回 `url`，脚本会兼容下载。
- `timeout` 默认使用 `600` 秒。在默认异步轮询模式下，它也是等待任务完成的最长时间；如果只想规避 OpenClaw 长等待，使用 `--no-wait`。
- `poll-interval` 默认 `5` 秒，用于异步任务轮询。
- `size` 默认使用 `1024x1024`。公众号封面、海报、横图等场景按用户给定比例换算到接口合法尺寸，不要直接使用不符合接口约束的平台展示尺寸。
- `image` 支持一个或多个参考图 URL、本地路径或 `data:image/...;base64,...`。传本地路径时，脚本会自动转成 data URL base64 再提交，避免远端 API 读不到 OpenClaw 本地文件。
- fal 通道有参考图时使用 `image_urls` 字段并走 `openai/gpt-image-2/edit`；无参考图时走 `openai/gpt-image-2` 文生图。

## 提示词语言

- 默认用简体中文编写最终 `prompt`，即使用户只给了很短的中文需求，也要扩写成中文视觉设计任务书。
- 技术名词、品牌名、API 名、模型名和画面中必须出现的英文原文可以保留英文。
- 如果用户明确要求英文提示词或英文画面文案，按用户要求执行，但仍要确保约束、保留项和负面提示表达清楚。

## OpenClaw 使用边界

- 不要把 API Key 写入 `SKILL.md`、命令参数、聊天回复或日志说明。
- 如果环境变量缺失，先提示用户配置，不要猜测 Base URL 或 Key。
- 如果 OpenClaw 外层任务容易超时，优先使用 `--no-wait` 拿到 `task_id`，后续再用 `--task-id` 查询。
- 如果任务状态为 `FAILURE`，向用户报告 `task_id` 和失败原因，不要自动重新提交同一任务；只有用户明确要求重试时才重新调用生图。
- 如果用户显式开启 fal fallback 且 fal 成功，向用户说明实际使用的是 fal GPT-Image2 兜底结果。
- 如果 fal 返回 `IN_QUEUE` / “未启动”，向用户说明 fal 中转排队较慢，并保留 `request_id` 供稍后查询；不要自动重复提交。
- 如果接口返回 `{}` 或非标准结构，保留 `response.json` 并说明服务端没有返回可直接下载的图片字段。
- 如果用户要求生成违法、侵权、隐私泄露或高风险内容，拒绝该部分请求，并给出安全替代提示词。
- 图片生成失败时，先检查尺寸合法性、认证头、Base URL 拼接和服务端原始错误。
