# 安信短视频素材审核接口参考

## 来源

- Apifox 文档：`https://gpt-best.apifox.cn/api-139393491`
- 视频分析接口：`https://gpt-best.apifox.cn/api-321040299`
- Base URL 与 API Key：`https://gpt-best.apifox.cn/doc-6535931`

## 认证

```http
Authorization: Bearer {{YOUR_API_KEY}}
Content-Type: application/json
Accept: application/json
```

脚本默认读取：

- `ANXIN_API_BASE_URL`
- `ANXIN_API_KEY`
- `ANXIN_REQUEST_TIMEOUT`

## Chat 多模态审核格式

Apifox 视频分析页说明所有对话模型都可使用 `/v1/chat/completions`，但模型需要具备视频或图片读取能力，当前主要是 Gemini 系列。文档示例使用远程视频 URL；本技能会把本地短视频转为 `data:video/...;base64,...`，把分镜图、封面图或截图转为 `data:image/...;base64,...`，并把文稿、口播稿、字幕稿放入文本提示词。

```json
{
  "model": "gemini-3.1-flash-lite-preview-thinking-high",
  "stream": false,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "请审核这些发布素材是否适合发布到微信视频号和抖音。"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:video/mp4;base64,..."
          }
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,..."
          }
        }
      ]
    }
  ],
  "temperature": 0.2,
  "max_tokens": 4000,
  "response_format": {
    "type": "json_object"
  }
}
```

说明：

- 字段名 `image_url` 来自 OpenAI 兼容多模态格式，视频和图片都沿用该字段承载 URL 或 data URL。
- `stream` 默认关闭，便于脚本保存完整响应。
- `response_format` 请求模型尽量返回 JSON；如果服务端或模型不严格遵守，脚本会保存原文并生成 Markdown 报告。
- 纯文稿审核也使用同一接口，只发送文本消息，不附带视频或图片。
- Base URL 拼接方式为：`{{ANXIN_API_BASE_URL}}/v1/chat/completions`。

## Gemini 官方格式参考

Apifox 也提供 Gemini 官方格式路径：

```text
POST /v1beta/models/gemini-2.5-pro:generateContent
```

本技能默认不用该路径，因为用户指定参考 Chat 文档，并要求复用 `anxin-image-gen` 的 Base URL / API Key 约定。如后续服务商确认 `gemini-3.1-flash-lite-preview-thinking-high` 的官方格式路径更稳定，可新增脚本参数切换到：

```text
/v1beta/models/gemini-3.1-flash-lite-preview-thinking-high:generateContent
```

并用 `inlineData` 承载视频 base64。

## 常见失败处理

- `401` / `403`：检查 `ANXIN_API_KEY` 是否正确，避免把 Key 写入命令行历史。
- `404`：检查 `ANXIN_API_BASE_URL` 是否多拼了 `/v1/chat/completions`。
- `413`：视频或图片体积过大，压缩、截取关键片段或减少分镜图数量。
- 模型提示不支持视频：确认模型名是否为 `gemini-3.1-flash-lite-preview-thinking-high`，或切换到服务商实际支持的视频理解 Gemini 模型。
- 返回空结构：保留 `response-*.json`，检查 `choices[0].message.content` 是否为空。
