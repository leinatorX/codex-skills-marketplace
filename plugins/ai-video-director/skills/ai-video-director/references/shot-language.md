# 景别、构图、运镜与提示词表达

## 景别

| 景别 | 适合剧情 | 提示词写法 |
| --- | --- | --- |
| 特写 | 情绪爆发、关键道具、眼神、危险细节 | `close-up of the character's face` / `面部特写，眼神紧张` |
| 近景 | 人物反应、对话、轻动作 | `medium close-up, upper body visible` / `上半身近景` |
| 中景 | 人物动作、人与环境关系 | `medium shot, full upper body and surrounding props` / `中景，人物和周围道具同时可见` |
| 远景 | 建立场景、展示行动路线 | `wide shot showing the character in the environment` / `远景，展示主体与街道空间关系` |
| 大全景 | 史诗感、灾难、城市、战争、巨大尺度 | `extreme wide shot, epic scale` / `史诗级大全景` |
| 微距 | 细节、质感、产品、危险微小线索 | `macro shot of water droplets on metal` / `微距镜头，展示金属表面的水珠` |
| 广角 | 空间压迫、速度感、夸张透视 | `wide-angle lens, exaggerated perspective` / `广角镜头，夸张透视` |
| 监控视角 | 犯罪、异常、真实记录、冷静旁观 | `security camera footage, fixed high angle` / `监控视角，固定高位俯拍` |
| 第一人称 | 沉浸、追逐、恐惧、游戏感 | `first-person point of view, shaky movement` / `第一人称视角，轻微晃动` |

## 构图

| 构图 | 适合剧情 | 提示词写法 |
| --- | --- | --- |
| 三分法 | 稳定、商业、人物介绍、自然观看 | `rule of thirds, subject on the right third` |
| 黄金分割 | 高级感、人物肖像、产品展示 | `golden ratio composition, visual focus on the product` |
| 对角线 | 追逐、冲突、速度、危险 | `diagonal composition, road cutting across the frame` |
| 引导线 | 路径、压迫、目标、纵深 | `leading lines guide the eye toward the subject` |
| 荷兰角 | 失衡、惊悚、混乱、心理异常 | `Dutch angle, tilted horizon, uneasy mood` |
| 居中构图 | 仪式感、压迫、对称、强主体 | `centered composition, symmetrical background` |
| 前景遮挡 | 偷窥、纵深、悬念、现场感 | `foreground obstruction, subject partially hidden behind glass` |
| 背景压迫 | 危机逼近、环境威胁 | `threatening background crowd closing in behind the subject` |

## 运镜

| 运镜 | 适合剧情 | 提示词写法 |
| --- | --- | --- |
| 固定镜头 | 冷静观察、监控感、荒诞反差 | `static camera, no camera movement` |
| 推镜头 | 发现、压迫、情绪逼近、重点强化 | `slow dolly in toward the subject` |
| 拉镜头 | 揭示环境、孤独、危险规模 | `camera slowly pulls back to reveal the ruined city` |
| 摇镜头 | 展示空间、跟随视线、发现新信息 | `slow pan from left to right, revealing...` |
| 移镜头 | 横向跟随、速度、场景浏览 | `tracking shot moving alongside the running character` |
| 跟拍 | 追逐、运动、现场感 | `camera follows behind the subject at running speed` |
| 手持 | 紧张、纪录片、战争、灾难、真实感 | `handheld camera, subtle shake, documentary realism` |
| 第一人称 | 沉浸、逃亡、探索、恐怖 | `first-person POV, breathing and shaky steps` |
| 特殊变焦 | 惊讶、心理变化、超现实 | `dolly zoom, background stretches while subject remains centered` |
| 无人机 | 大场面、路径、地理关系 | `drone aerial shot, high angle, sweeping forward` |

## 提示词写法原则

- 使用一个明确镜头目标：例如“让观众感到危险正在靠近”。
- 景别、构图、运镜不要互相冲突。例：`固定监控视角` 不要同时写 `高速环绕运镜`。
- 复杂运镜要写速度：`slow`、`fast`、`subtle`、`smooth`、`shaky`。
- 图生视频时不要重复描述参考图已有静态内容，重点写“保持什么”和“如何运动”。
- 同一镜头不要同时要求太多摄影机动作，优先一个主运镜加一个轻微辅助效果。

## 常用负面约束

```text
避免主体变形，避免脸部漂移，避免手指畸形，避免文字乱码，避免动作僵硬，避免漂浮感，避免游戏 CG 感，避免过度磨皮，避免塑料皮肤，避免镜头突然跳切。
```
