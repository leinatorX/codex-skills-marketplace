# 参考资产、定妆照与图生视频规划

## 使用场景

当用户要求完整 AI 视频制作方案、角色一致性、多镜头剧情、产品展示、图生视频、首尾帧、定妆照、参考图或关键帧时使用本文件。

核心规则：剧本完成后，不要立刻写视频提示词。先提炼全片关键资产，优先生成定妆照、场景图、道具图和关键帧，再决定每个序列用文生视频、图生视频、首帧视频、首尾帧视频还是多参考图视频。

## 剧本后的资产提炼

从剧本中提炼：

```text
人物：主角、配角、群体角色、年龄、职业、外观、服装、表情基准、动作特征。
道具：产品、工具、武器、文件、车辆、设备、品牌标识、手持物。
场景：主要地点、次要地点、时代背景、天气、光线、空间结构。
视觉符号：反复出现的颜色、标识、损伤、图案、关键物件。
风格：写实、胶片、纪录片、广告片、赛博、复古、动画、灾难片等。
关键帧：每个需要精准起止的序列首帧和尾帧。
```

## 参考资产优先级

1. 主要人物定妆照
   - 用于锁定脸、发型、体型、服装、材质和气质。
   - 默认先出全身正面，必要时补半身、表情和动作姿态。

2. 角色三视图或多角度图
   - 适合多镜头反复出现的人物、机器人、怪物、动物、车辆。
   - 要求正面、侧面、背面保持同一角色设计。

3. 道具和产品图
   - 适合产品广告、设备演示、事故道具、关键线索。
   - 需要干净背景或明确使用场景两种版本。

4. 场景参考图
   - 用于统一主场景空间、光线、时代和美术方向。
   - 可输出空场景版，后续作为视频镜头参考图。

5. 风格帧
   - 用于锁定全片色彩、影调、摄影质感和画质。
   - 风格帧不一定进入正片，但要指导后续镜头。

6. 序列首帧和尾帧
   - 用于需要精准动作起止、转场、变形、开合、爆炸前后、角色入画出画的序列。
   - 首尾帧要保持同一角色、同一场景、同一镜头方向和可连续的动作逻辑。

## 序列生成方式判断

| 生成方式 | 适合镜头 | 提示词重点 |
| --- | --- | --- |
| 文生视频 | 空镜、环境、抽象画面、角色不重复、低一致性要求 | 完整描述主体、动作、场景、镜头和风格 |
| 图生视频 | 角色、产品、品牌、道具、场景一致性重要 | 写清参考图保持项和运动项 |
| 首帧视频 | 必须从指定构图开始、需要保持角色外观 | 首帧锁定构图和主体，视频提示词只写运动和镜头变化 |
| 首尾帧视频 | 动作起点和终点都重要、转场要精准 | 分别描述首帧和尾帧关系，避免中途复杂动作过多 |
| 多参考图视频 | 同时锁定人物、道具、场景和风格 | 每张参考图必须标注用途，避免模型混用 |
| 局部编辑后视频 | 只有某个区域需要改，其他内容保持 | 用图像编辑先修好参考图，再进入视频生成 |

## 定妆照提示词模板

```text
用途：AI 视频主角定妆照，用于后续图生视频和角色一致性参考。
主体：{角色身份、年龄、体型、脸部特征、发型、肤色、气质}。
服装：{服装款式、颜色、材质、配饰、关键标识}。
姿态：全身正面站立，自然站姿，双手自然下垂，表情基准为 {表情}。
背景：干净中性背景，不遮挡主体。
风格：{写实/电影感/广告摄影/角色设定图/产品摄影}。
画幅：{1:1 / 3:4 / 9:16 / 16:9}。
限制：保持完整身体，避免裁切，避免多人物，避免文字乱码，避免脸部变形。
```

## 场景参考图提示词模板

```text
用途：AI 视频主场景参考图，用于统一后续镜头的空间、光线和美术方向。
场景：{地点、时代、天气、时间、空间结构}。
视觉元素：{建筑、道路、家具、设备、环境道具、标识物}。
光线：{自然光/霓虹/阴天/夜景/强背光/低调光}。
风格：{写实电影感/纪录片/广告片/灾难片/复古胶片}。
构图：{广角/远景/中景/对称/引导线/俯拍/低角度}。
限制：不要出现主角，避免无关文字，避免风格漂移。
```

## 首尾帧提示词模板

```text
序列编号：{Q01}
用途：为 {视频模型} 生成首尾帧参考。

首帧：
{主体} 位于 {场景}，处于 {动作起点}。构图为 {景别、主体位置、镜头角度}，光线和风格保持 {风格}。

尾帧：
同一主体、同一服装、同一场景和同一摄影风格。主体完成 {动作结果}，位置变化为 {空间变化}，构图与首帧可自然衔接。

连续性限制：
保持同一角色外观、同一环境结构、同一光线方向，不要改变服装、脸、道具和镜头轴线。
```

## GPT Image 2 写法

官方资料要点：

- `gpt-image-2` 是 OpenAI 的图像生成和编辑模型，支持文本和图像输入，输出图像。
- OpenAI 图像生成指南说明，Image API 可生成图像、编辑图像，也可以用一张或多张图作为参考生成新图。
- `gpt-image-2` 会以高保真方式处理图像输入，相关保真参数无需手动调整。
- 可设置尺寸、质量、格式、压缩等输出参数。
- 官方限制包括复杂提示可能较慢、精确文字仍可能出错、跨多次生成的一致性可能不稳定、精确构图仍可能困难。

提示词结构：

```text
Generate a {aspect ratio} image for AI video reference.
Purpose: {character look / scene reference / prop reference / first frame / last frame}.
Subject: {clear subject and stable identifiers}.
Composition: {shot size, angle, subject position, background}.
Details to preserve: {face, clothing, logo, material, prop, color}.
Style and lighting: {photorealistic, cinematic, product photography, lighting}.
Output use: this image will be used as {image-to-video reference / start frame / end frame}.
Constraints: avoid {cropping, distorted face, unreadable text, extra characters, inconsistent logo}.
```

适合：

- 定妆照、产品图、道具图、场景图。
- 多图参考组合，例如把人物、产品、包装和场景组合成统一参考图。
- 局部编辑，例如换服装、移除背景、修正道具、生成透明背景素材。

## Nano Banana Pro 写法

官方资料要点：

- Google 官方将 Nano Banana Pro 对应到 Gemini 3 Pro Image，面向专业资产生产、复杂指令和高保真文字渲染。
- Gemini API 图像生成支持文本、图像或组合输入，并支持对图像进行编辑和多轮迭代。
- Google 官方提示词建议包含主体、构图、动作、地点、风格；进一步细化相机角度、光线、画幅、文字集成和事实约束。
- 官方提示词文章提到不同产品表面对可输入图像数量的支持可能不同，最多可到 14 张图，需按具体平台确认。
- 官方仍提醒文字、事实准确性、复杂编辑、图像融合和角色一致性可能需要人工复核。

提示词结构：

```text
Create a {aspect ratio} professional AI video reference image.
Story purpose: {why this asset is needed in the film}.
Subject: {who/what appears, exact visual identity}.
Composition: {close-up / wide shot / low angle / portrait / product layout}.
Action or pose: {standing, holding, turning, running, object open/closed}.
Location: {environment, time, weather, background}.
Style: {photorealistic, cinematic, film noir, product photography, diagram, poster}.
Camera and lighting: {lens feel, depth of field, lighting direction, color grade}.
Text requirements: {exact visible text, font, placement}; if text is not needed, say no text.
Reference usage: {which input image controls character / prop / scene / style}.
Constraints: preserve {identity, logo, costume, color}; avoid {extra people, artifacts, illegible text}.
```

适合：

- 专业定妆照、角色多角度图、海报、信息图、带文字视觉、品牌视觉。
- 多参考图融合，例如人物 + 道具 + 场景 + 风格。
- 需要世界知识或事实约束的图表、示意图和科普视觉，但必须人工复核事实。

## 序列表新增字段

序列表中必须加入：

```text
生成方式：文生视频 / 图生视频 / 首帧视频 / 首尾帧视频 / 多参考图视频 / 局部编辑后视频
参考资产：角色定妆照 ID、场景图 ID、道具图 ID、风格帧 ID
首帧：是否需要，使用哪个资产或需生成什么画面
尾帧：是否需要，使用哪个资产或需生成什么画面
出图模型：GPT Image 2 / Nano Banana Pro / 其他
视频模型：Veo / Seedance / Runway / Sora / Kling / Grok
```

## 工作流建议

1. 剧本完成。
2. 提炼人物、道具、场景、风格和关键视觉符号。
3. 先输出定妆照、道具图、场景图和风格帧提示词。
4. 标记每个序列的生成方式。
5. 对需要图生视频的序列，补首帧或首尾帧提示词。
6. 再写序列级视频模型三段式提示词。
7. 质检时先查参考资产是否一致，再查视频动作是否完成。

## 官方来源

- OpenAI GPT Image 2 model page: https://developers.openai.com/api/docs/models/gpt-image-2
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- Google Gemini image generation guide: https://ai.google.dev/gemini-api/docs/image-generation
- Google Nano Banana Pro prompt tips: https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/
- Google Nano Banana Pro launch post: https://blog.google/innovation-and-ai/products/nano-banana-pro/
