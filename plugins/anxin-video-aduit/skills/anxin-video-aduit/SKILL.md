---
name: anxin-video-aduit
description: Audit short-video publishing materials through the Anxin Gemini-compatible API for WeChat Channels and Douyin compliance. Use this skill whenever the user asks to 审核短视频, 视频合规审核, 判断视频是否违规, 审核文稿, 审核口播稿, 审核字幕稿, 审核分镜图, 审核封面图, 微信视频号审核, 抖音审核, 短视频运营规则检查, 内容安全评估, 视频发布前检查, or wants to send local videos/images as base64 plus scripts to gemini-3.1-flash-lite-preview-thinking-high and receive violation risks plus revision advice.
---

# 安信短视频素材审核

## 目标

通过安信接口把短视频、分镜图、封面图、截图、文稿、口播稿、字幕稿等发布素材提交给 `gemini-3.1-flash-lite-preview-thinking-high`，参考微信视频号和抖音平台运营规则，判断素材是否存在违规风险，并给出可执行的修改建议。

优先使用 `scripts/audit_video.py`，避免在对话、命令说明或输出文件中暴露 API Key。接口与认证约定复用 `anxin-image-gen`：

- `ANXIN_API_BASE_URL`：服务商提供的 Base URL，不要包含末尾 `/v1/chat/completions`。
- `ANXIN_API_KEY`：Bearer API Key。
- `ANXIN_REQUEST_TIMEOUT`：可选，请求超时时间，单位秒；默认 `600`。

接口细节见 `references/api.md`。平台规则审核口径见 `references/rules.md`。

## 快速流程

1. 确认用户提供了至少一种待审核素材：
   - `--video`：本地短视频文件，可重复传入。
   - `--image`：分镜图、封面图、截图，可重复传入。
   - `--script-text`：直接传入文稿、口播稿、字幕稿或分镜说明。
   - `--script-file`：本地纯文本稿件文件，可重复传入。
   - `--title` / `--description` / `--hashtags`：拟发布标题、文案和话题。
   如果素材只有远程 URL，先下载到本地或让用户提供本地文件。
2. 明确审核平台：
   - 默认同时审核 `wechat,douyin`。
   - 用户只要求微信视频号或抖音时，用 `--platform wechat` 或 `--platform douyin`。
3. 如用户提供商品/服务信息、活动报名方式、投放目标或账号主体资质，也应放入 `--description` 或 `--script-text`，这些信息会影响诱导、夸张宣传、违规引流和资质类判断。
4. 调用 `scripts/audit_video.py`，脚本会自动识别视频和图片 MIME 类型、转为 `data:*/*;base64,...`，并把文稿内容放入提示词提交到 `/v1/chat/completions`。
5. 返回审核结论、风险等级、命中项、素材来源、证据位置、平台差异和修改建议。不要回显 API Key。

## 调用脚本

```bash
python scripts/audit_video.py \
  --video "D:/videos/demo.mp4" \
  --title "一分钟了解家庭消防隐患" \
  --description "用于微信视频号和抖音发布的安全科普短视频" \
  --platform both \
  --output-dir ./outputs
```

审核文稿和分镜图：

```bash
python scripts/audit_video.py \
  --script-file "D:/drafts/script.md" \
  --image "D:/storyboard/shot-01.png" \
  --image "D:/storyboard/shot-02.png" \
  --title "危险化学品应急处置培训报名" \
  --platform both \
  --output-dir ./outputs
```

只审核一段口播稿：

```bash
python scripts/audit_video.py \
  --script-text "本期培训名额有限，扫码添加老师领取内部资料。" \
  --platform both \
  --output-dir ./outputs
```

只审核微信视频号：

```bash
python scripts/audit_video.py \
  --video "D:/videos/demo.mp4" \
  --platform wechat \
  --output-dir ./outputs
```

只审核抖音：

```bash
python scripts/audit_video.py \
  --video "D:/videos/demo.mp4" \
  --platform douyin \
  --output-dir ./outputs
```

## 输出要求

脚本会在输出目录生成：

- `audit-<timestamp>.json`：结构化审核结果。
- `audit-<timestamp>.md`：适合直接阅读的中文审核报告。
- `response-<timestamp>.json`：接口原始响应，便于排错。

最终回复用户时优先总结：

1. `结论`：可发布、建议修改后发布、高风险不建议发布、无法判断。
2. `主要风险`：按严重程度列出命中规则、证据和平台。
3. `修改建议`：给出画面、旁白、字幕、标题、文案、资质说明的具体调整。
4. `验证信息`：说明使用的脚本、模型、输入素材类型、输出路径和是否成功调用接口。

## 审核口径

- 以平台公开规则和常见运营治理口径为审核依据，但不要声称等同于平台最终审核结果。
- 对不确定内容使用“疑似”“需人工复核”，不要伪装为确定违规。
- 同时检查视频画面、分镜图、封面图、语音、字幕、背景文字、标题、描述、话题、文稿承诺、商品/服务承诺和引流信息。
- 对高风险内容优先给出降风险方案，而不是只给“违规”结论。
- 对医疗、金融、法律、教育、招聘、功效承诺、救助众筹、未成年人、危险动作等内容，要求补充资质或删改夸张承诺。
- 涉及第三方版权、肖像、隐私、商标、新闻素材、影视片段或音乐时，明确提示授权风险。

## 安全边界

- 不要把 API Key 写入 `SKILL.md`、命令参数、聊天回复、报告或日志。
- 如果环境变量缺失，提示用户配置，不要猜测 Base URL 或 Key。
- 如果视频或图片过大导致接口失败，建议用户压缩、截取关键片段、减少分镜数量或改用远程 URL 后再审。
- 如果接口返回非 JSON 文本，保留原始响应并将文本整理成报告。
- 如果用户要求绕过平台审核、规避关键词、隐匿违规内容或生成违法违规内容，不提供规避方案，只能给合规修改建议。
- 如果模型无法识别音频、字幕、分镜图或画面细节，明确说明未覆盖部分需要人工复核。
