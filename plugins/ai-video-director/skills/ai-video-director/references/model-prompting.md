# 主流 AI 视频模型提示词适配

## 使用原则

模型能力更新很快。若用户要求最新官方指南、最新参数、最新模型名称或商业可用性，先联网核对官方文档或官方平台说明。

模型适配原则：

- 先确定目标模型，再用该模型的写法要求填充序列级三段式提示词。
- 不要先输出一份“通用三段式”，再额外输出一份“模型改写版”；这会造成重复和割裂。
- 指定单个模型时，每个序列只输出该模型可直接使用的一套三段式提示词。
- 指定多个模型时，同一序列分别输出各模型的三段式版本。
- 镜头层默认不输出视频生成提示词，只输出从序列中截取的剪辑说明。

默认模型：

- 默认视频模型：`Grok Imagine Video`。
- 默认图像模型：`GPT Image 2`。
- 用户本次明确指定模型时，以用户指定为准。

生成时长必须合法。先做序列规划和时长合法化，再写视频提示词。

通用母版：

```text
{合法生成时长} {画幅} 视频。
主体：{谁/什么，稳定外观和关键特征}。
动作链：{主体连续做什么，动作节奏如何，可剪辑节点在哪里}。
场景：{地点、时间、天气、环境细节}。
镜头变化：{景别变化、构图变化、运镜、镜头速度}。
风格：{写实/电影/广告/纪录片/动画/胶片/赛博等}。
光线色彩：{光源、影调、色彩倾向}。
声音：{对白/旁白/环境声/音效/音乐/不要音乐}。
限制：避免 {常见错误和不想要内容}。
```

## Seedance 2.0

适合“分层导演式提示词”。重点写清主体、动作链、场景、镜头变化、风格、声音和格式。

模板：

```text
{合法生成时长} 秒 {竖屏/横屏} 视频。
【主题与主体】{主体身份、外观、服装、关键稳定特征}。
【场景与风格】{地点、时代、天气、光线、整体视觉风格和情绪}。
【镜头与动作】{覆盖镜头、可剪辑节点、景别变化、构图变化、运镜、主体动作链、环境运动}。
【声音】{对白、环境声、音效、音乐；如不需要配乐则明确 no music}。
【格式】{清晰度、画幅、是否字幕、是否写实}。
【限制】避免 {动作僵硬、主体变形、CG 感等}。
```

写法要点：

- 中文提示词可用，结构要清楚。
- 多参考素材时说明每个素材用途：角色、场景、风格、动作，不要混用。
- 复杂多序列项目建议拆成多个合法时长序列生成，不要一次让模型完成完整短片。

## Grok Imagine Video

xAI 官方公开资料主要说明 Grok Imagine 的图像/视频生成能力和 API 模型能力；如果没有独立提示词指南，不要声称有完整官方提示词手册。

保守模板：

```text
Create a {legal duration} video sequence.
Subject: {clear subject}.
Action chain: {one continuous action chain with editable beats}.
Scene: {simple environment}.
Camera: {one camera style or simple camera progression}.
Style: {realistic/cinematic/playful/surreal}.
Audio intent: {ambient sound/music/dialogue if needed}.
Keep the subject consistent and avoid distorted faces or unreadable text.
```

写法要点：

- 更适合短、明确、动作导向的提示词。
- 一次只给一个连续动作链，减少复杂叙事。
- 图生视频时重点描述参考图如何动起来。
- 娱乐化、快速创意、社交短视频片段可以更大胆；严肃商业片要增加一致性约束。
- 默认按 6-15 秒规划，但 xAI 官方模型页未明确列出可选时长，实际调用前需按当前平台复核。

## Veo 3.1

适合导演式、结构化、带声音和时间控制的提示词。官方指南强调主体、动作、场景、镜头、美学、声音等元素。

模板：

```text
Generate a {legal duration} {aspect ratio} cinematic video sequence.
Subject: {who/what, appearance, stable details}.
Action chain: {what happens, sequence of movement, editable beats}.
Scene: {location, time, weather, props, background}.
Camera: {shot size changes, lens, composition, movement}.
Lighting and style: {lighting, color, texture, film style}.
Audio: {dialogue, ambient sound, music, sound effects}.
Timing: {optional timestamps or beat structure}.
Negative constraints: avoid {unwanted issues}.
```

Timestamp 模板：

```text
0-2s: {first visual beat}.
2-5s: {camera or action progression}.
5-8s: {reveal, reaction, or ending beat}.
```

写法要点：

- Veo 适合把声音作为提示词的一部分写清楚。
- 需要连续动作时，用时间点拆开。
- Ingredients、首尾帧、参考图等能力要按当前官方接口确认。
- 对话要短，口型和字幕不要过度依赖一次生成。
- Veo 3.1 文生视频按 4、6、8 秒规划；参考图转视频只按 8 秒规划。

## Sora

适合自然语言场景描述、Storyboard、Remix、Extend 等工作流。

模板：

```text
A {legal duration} video sequence of {subject} {action chain} in {scene}.
The camera {movement}, using {shot size/composition}.
The mood is {emotion}, with {lighting/color/style}.
Keep {character/scene details} consistent throughout.
Avoid {unwanted artifacts}.
```

写法要点：

- 具体描述主体、动作和环境，不要只写风格词。
- 复杂短片用 Storyboard 拆段控制。
- 少角色、少并行动作更稳定。
- 可先生成基础片段，再用重混或延展迭代。

## Runway Gen-4 / Gen-4.5

适合清晰直接的运动描述。图生视频时，不必重复描述参考图中已经存在的内容，应重点写运动。

Text to Video 模板：

```text
{Subject} {action chain} in {scene}. {Camera movement}. {Lighting/style}. {Mood}. Editable beats: {beat list}.
```

Image to Video 模板：

```text
Using the reference image, keep the subject's appearance unchanged.
The subject {motion chain}. The camera {movement}. The background {subtle motion}.
Maintain {style/lighting}. Avoid {errors}.
```

写法要点：

- 不要堆关键词，写成清楚的画面句子。
- 参考图越重要，越要强调保持主体、服装、脸部和构图。
- 对角色一致性要求高时，优先图生视频或参考图工作流。

## Kling

官方公式可概括为：

```text
Prompt = Subject + Subject Movement + Scene + Camera Language + Lighting + Atmosphere
```

模板：

```text
{主体} {连续主体运动}，位于 {场景}。
镜头语言：{景别、构图、运镜}。
光线：{光源、明暗、色彩}。
氛围：{情绪、风格、质感}。
负面约束：避免 {错误}。
```

写法要点：

- 适合短序列。
- 主体运动和镜头运动要分开写。
- 中文提示词可用，但结构要明确。

## 序列时长合法化规则

- 改成 Grok：默认按 6-15 秒序列规划；短镜头从序列中裁切。
- 改成 Veo：文生视频选择 4、6、8 秒；图生视频或参考图视频选择 8 秒。
- 改成 Seedance：按当前接入平台选择 5-15 秒或 4-15 秒；短镜头合并成序列。
- 改成 Runway 图生视频：删掉多余静态描述，强调参考图保持项和运动项，并按当前 Runway 时长限制复核。
- 改成 Sora：改成自然语言序列描述，复杂内容拆 Storyboard。
- 改成 Kling：压缩成主体、运动、场景、镜头、光线、氛围，并按当前 Kling 时长限制复核。
