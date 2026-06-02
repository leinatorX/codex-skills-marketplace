# 蓝白企业汇报版式

所有页面都使用：

```html
<section class="slide" data-layout="版式名" data-question="本页问题" data-message="本页结论">
  ...
</section>
```

页面文案默认中文。英文只用于必要技术名词。

除封面页外，每页都必须填写 `data-question` 和 `data-message`。这两个字段不展示在页面上，但用于约束汇报逻辑。

## 通用密度规则

- 每页只回答一个核心问题。
- 标题必须写成判断句或行动句，不能是"核心能力""公司概况"这类孤立标签。参考 `references/content-guide.md` 的标题对照表。
- 标题字号保持企业汇报尺度，不要使用发布会大屏式超大字。正文页标题不应占据页面上半屏。
- 普通内容页建议 4-8 个信息单元。少于 3 个信息单元时，容易变成网页式空页，必须补充图表、表格、证据或结论说明。
- 单页正文建议控制在 260-560 个中文字符；目录页不要超过 220 个中文字符。
- 每个正文页至少有 3 个具体事实、数字、对象、动作或来源支撑，不能只写抽象价值词。
- 每个卡片必须包含"对象 + 事实/数字 + 含义"三要素，参考 `references/content-guide.md`。

---

## 1. cover · 封面

用途：公司介绍、项目汇报、方案路演开场。

封面必须简洁，只保留背景图和中文大标题。不要放页码、目录、数据卡片、说明段落、底部导航点。

```html
<section class="slide cover-full" data-layout="cover">
  <div class="cover-bg">
    <img src="images/cover-visual.jpg" alt="[主视觉描述]">
  </div>
  <div class="cover-shade"></div>
  <div class="cover-copy">
    <h1>[结论式中文大标题，如：数智赋能安全应急，从被动响应走向主动预防]</h1>
  </div>
</section>
```

## 2. agenda · 汇报结构

用途：说明本次汇报讲什么。目录页必须放在第二页。

```html
<section class="slide" data-layout="agenda"
  data-question="[如：这份汇报讲什么、按什么逻辑推进]"
  data-message="[如：从行业压力出发，经过问题、方案、证明，最终给出合作建议]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">02 / [总页数]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">汇报结构</div>
      <h2>[结论式标题，如：今天的汇报围绕一个核心问题展开]</h2>
      <div class="bar"></div>
      <p class="lead">[1-2 行核心问题说明]</p>
    </div>
    <div class="grid-3">
      <div class="card"><h3>01 [章节名]</h3><p class="desc">[一句话说明]</p></div>
      <div class="card"><h3>02 [章节名]</h3><p class="desc">[一句话说明]</p></div>
      <div class="card"><h3>03 [章节名]</h3><p class="desc">[一句话说明]</p></div>
      <div class="card"><h3>04 [章节名]</h3><p class="desc">[一句话说明]</p></div>
      <div class="card"><h3>05 [章节名]</h3><p class="desc">[一句话说明]</p></div>
    </div>
  </div>
</section>
```

## 3. section-divider · 章节页

用途：把长汇报拆成清晰章节。标准 14-22 页建议 3-5 个章节页。

```html
<section class="slide" data-layout="section-divider"
  data-question="[本章要回答的问题]"
  data-message="[本章的核心结论]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div class="section-wrap">
      <div>
        <div class="section-mark">PART.01</div>
      </div>
      <div>
        <div class="section-title">[章节标题，用结论句]</div>
        <div class="section-points">
          <p>[本章回答的问题 1]</p>
          <p>[本章回答的问题 2]</p>
          <p>[本章回答的问题 3]</p>
        </div>
      </div>
    </div>
  </div>
</section>
```

## 4. overview · 公司概况

用途：快速建立公司认知。

```html
<section class="slide" data-layout="overview"
  data-question="[如：安信是什么公司、做什么]"
  data-message="[如：安信是数智赋能的安全应急解决方案平台]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content grid-2">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
      <p class="lead">[1-2 行核心定位说明，包含具体行业和客户]</p>
    </div>
    <div class="grid-3" style="grid-template-columns:1fr 1fr">
      <div class="card">
        <div class="num">[数字+单位]</div>
        <h3>[指标名]</h3>
        <p class="desc">[含义说明，不能只写空泛词]</p>
      </div>
      <!-- 重复 3-4 个数字卡片 -->
    </div>
  </div>
</section>
```

## 5. problem · 问题与挑战

用途：解释客户为什么需要方案。不要夸大风险，不要制造恐慌。

```html
<section class="slide" data-layout="problem"
  data-question="[如：传统安全管理到底缺什么]"
  data-message="[如：不是缺工具，而是缺串联平台]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题，说清核心缺口]</h2>
      <div class="bar"></div>
    </div>
    <div class="grid-3">
      <div class="card">
        <h3>[问题名称]</h3>
        <p class="desc">[具体现状 + 影响 + 案例或数据]</p>
      </div>
      <!-- 重复 2-3 个问题卡片 -->
    </div>
    <p class="lead">[总结一句结论]</p>
  </div>
</section>
```

## 6. solution · 整体方案

用途：展示解决方案闭环。如果使用整张流程图，必须用 `object-fit: contain`。

```html
<section class="slide" data-layout="solution"
  data-question="[如：用什么方式解决这些问题]"
  data-message="[如：五步闭环，每步有具体产品和数据支撑]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <div class="flow">
      <div class="step">
        <h3>[环节名]</h3>
        <p class="desc">[具体能力 + 数据支撑]</p>
      </div>
      <!-- 重复 4-5 个步骤 -->
    </div>
    <p class="lead">[一句话总结方案价值]</p>
  </div>
</section>
```

## 7. architecture · 技术架构

用途：展示系统如何工作。架构图若文字较多，优先改成 HTML 分层结构。

```html
<section class="slide" data-layout="architecture"
  data-question="[如：系统技术架构如何分层]"
  data-message="[如：三层架构实现秒级响应]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content grid-2">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
      <p class="lead">[架构核心逻辑说明]</p>
    </div>
    <div class="image-frame image-16x9 image-contain">
      <img src="images/[架构图].jpg" alt="[架构图描述]">
    </div>
  </div>
</section>
```

## 8. product-grid · 产品矩阵

用途：展示硬件、软件、服务。只突出关键产品，不堆完整清单。

```html
<section class="slide" data-layout="product-grid"
  data-question="[如：安信有哪些核心产品]"
  data-message="[如：硬件+AI+仿真构成完整产品线]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <div class="cards-6">
      <div class="card">
        <h3>[产品名]</h3>
        <p class="desc">[类型 + 价值说明 + 关键数据]</p>
      </div>
      <!-- 重复 4-6 个产品卡片 -->
    </div>
  </div>
</section>
```

## 9. metrics · 关键数据

用途：突出市场规模、项目成效、客户覆盖。数据必须来自用户材料或可核实来源。

```html
<section class="slide" data-layout="metrics"
  data-question="[如：这些能力是否经过验证]"
  data-message="[如：47 个园区的实际数据证明路径可行]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <div class="grid-4">
      <div class="card blue">
        <div class="num">[数字]</div>
        <h3>[指标名]</h3>
        <p class="desc">[含义 + 同比/环比]</p>
      </div>
      <!-- 重复 3-4 个数字卡片 -->
    </div>
    <p class="lead">[数据来源或代表项目]</p>
  </div>
</section>
```

## 10. data-dashboard · 多指标经营看板

用途：年度报表、经营复盘、项目绩效。每个 KPI 必须写单位和解释口径。

```html
<section class="slide" data-layout="data-dashboard"
  data-question="[如：今年经营表现如何]"
  data-message="[如：营收增长但利润率承压]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <div class="grid-4">
      <div class="card"><div class="num">[数字+单位]</div><h3>[KPI名]</h3><p class="desc">[同比/环比 + 判断]</p></div>
      <!-- 重复 3-5 个 KPI -->
    </div>
    <p class="lead">[关键结论 + 数据来源]</p>
  </div>
</section>
```

## 11. chart-analysis · 图表分析

用途：解释收入结构、成本变化、趋势。图表优先用 HTML/CSS 绘制。

```html
<section class="slide" data-layout="chart-analysis"
  data-question="[如：收入结构发生了什么变化]"
  data-message="[如：能源业务占比提升至 42%]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content grid-2">
    <div class="chart">
      <!-- 用 HTML 条形图 -->
      <div class="bar-row"><span>[项目A]</span><div class="bar-track"><div class="bar-fill" style="width:72%"></div></div><span>72%</span></div>
      <div class="bar-row"><span>[项目B]</span><div class="bar-track"><div class="bar-fill" style="width:54%"></div></div><span>54%</span></div>
      <!-- 重复 -->
    </div>
    <div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
      <div class="insight-list">
        <div><strong>[发现1]</strong><span>[原因 + 影响]</span></div>
        <div><strong>[发现2]</strong><span>[原因 + 影响]</span></div>
        <div><strong>[发现3]</strong><span>[原因 + 影响]</span></div>
      </div>
    </div>
  </div>
</section>
```

## 12. financial-table · 财务或经营数据表

用途：报表解读、预算复盘。不要把完整财报塞进 PPT，只摘关键项。

```html
<section class="slide" data-layout="financial-table"
  data-question="[如：关键财务指标有什么变化]"
  data-message="[如：营收增长但成本端需关注]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <table class="table">
      <tr><th>指标</th><th>2024</th><th>2025</th><th>变化</th><th>判断</th></tr>
      <tr><td>[指标名]</td><td>[数字]</td><td>[数字]</td><td class="up">+[X]%</td><td>[一句判断]</td></tr>
      <!-- 重复 4-7 行 -->
    </table>
  </div>
</section>
```

## 13. comparison · 对比页

用途：同比变化、方案对比、现状与目标。

```html
<section class="slide" data-layout="comparison"
  data-question="[如：新旧方案有什么区别]"
  data-message="[如：平台化方案在响应速度和覆盖率上优势明显]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <div class="grid-2">
      <div class="card">
        <h3>[对比对象A]</h3>
        <p class="desc">[关键事实和判断]</p>
      </div>
      <div class="card blue">
        <h3>[对比对象B]</h3>
        <p class="desc">[关键事实和判断]</p>
      </div>
    </div>
  </div>
</section>
```

## 14. evidence-page · 证明材料页

用途：案例、项目照片、客户名单、证据链。

```html
<section class="slide" data-layout="evidence-page"
  data-question="[如：有什么证据支撑这些能力]"
  data-message="[如：3 个代表项目验证了方案可行性]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content grid-2">
    <div class="grid-3" style="grid-template-columns:1fr 1fr">
      <div class="image-frame image-3x2"><img src="images/[证据图].jpg" alt="[描述]"></div>
      <!-- 重复 2-4 张 -->
    </div>
    <div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
      <p class="lead">[做了什么 + 结果 + 能证明什么]</p>
    </div>
  </div>
</section>
```

## 15. roadmap · 推进路径

用途：说明销售、交付或年度推进节奏。

```html
<section class="slide" data-layout="roadmap"
  data-question="[如：接下来怎么推进]"
  data-message="[如：分三步走，从试点到规模化]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <div class="grid-3">
      <div class="card soft">
        <div class="eyebrow">[阶段名 · 时间]</div>
        <h3>[目标]</h3>
        <p class="desc">[具体动作 + 交付物]</p>
      </div>
      <!-- 重复 3-5 个阶段 -->
    </div>
  </div>
</section>
```

## 16. case-study · 案例或场景

用途：展示客户场景、代表项目或典型应用。

```html
<section class="slide" data-layout="case-study"
  data-question="[如：某园区如何落地的]"
  data-message="[如：上线 6 个月事故率下降 37%]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content grid-2">
    <div class="image-frame image-3x2 image-contain">
      <img src="images/[场景图].jpg" alt="[描述]">
    </div>
    <div>
      <div class="eyebrow">[客户/场景名]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
      <p class="lead"><strong>问题：</strong>[客户面临的问题]</p>
      <p class="lead"><strong>方案：</strong>[安信提供了什么]</p>
      <p class="lead"><strong>结果：</strong>[具体数字和效果]</p>
    </div>
  </div>
</section>
```

## 17. risk-action · 风险与行动建议

用途：年度报表结论、管理建议、下一步计划。

```html
<section class="slide" data-layout="risk-action"
  data-question="[如：当前面临什么风险]"
  data-message="[如：3 个风险需要在 Q3 前采取行动]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content">
    <div>
      <div class="eyebrow">[板块标记]</div>
      <h2>[结论式标题]</h2>
      <div class="bar"></div>
    </div>
    <div class="action-list">
      <div class="action-item">
        <div class="tag">[优先级/时间]</div>
        <h3>[风险/问题名]</h3>
        <p class="desc">[行动建议 + 预期效果]</p>
      </div>
      <!-- 重复 3-4 个 -->
    </div>
  </div>
</section>
```

## 18. closing · 收尾总结

用途：总结优势和下一步行动。最多保留 3-4 个行动对象或建议。

```html
<section class="slide" data-layout="closing"
  data-question="[如：希望对方做什么]"
  data-message="[如：从一个试点开始验证价值]">
  <div class="chrome">
    <span class="brand">[公司名]</span>
    <span class="page">[页码]</span>
  </div>
  <div class="content grid-2">
    <div>
      <h2>[收束性结论标题]</h2>
      <div class="bar"></div>
      <p class="lead">[1-2 行总结]</p>
    </div>
    <div>
      <div class="action-list" style="grid-template-columns:1fr">
        <div class="action-item">
          <div class="tag">建议 1</div>
          <h3>[行动名]</h3>
          <p class="desc">[具体内容]</p>
        </div>
        <!-- 重复 2-3 个 -->
      </div>
    </div>
  </div>
</section>
```
