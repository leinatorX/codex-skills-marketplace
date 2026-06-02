---
name: wechat-article-html-style
description: 将应急科普公众号文章整理成项目统一风格的本地 HTML 排版页，适用于生成可打开、可复制到微信公众平台的公众号正文页面。用户提到公众号 HTML、公众号排版版、复制到公众号、保持每期文章风格一致、统一排版模板时使用。
---

# 微信公众号 HTML 排版风格

## 使用边界

用于把已经完成的公众号文章和图片资产，整理成本项目统一风格的 HTML 发布页。

本 skill 不负责重新选题、事实核查或正文创作；这些应先由 `emergency-wechat-writer` 完成。当前 skill 只处理：

- 公众号正文 HTML 排版
- 本地图片引用
- 微信编辑器复制友好的内联样式
- 每期内容文件夹结构
- 统一标题、摘要、重点块、分节、结尾引导风格

## 默认产物结构

每期文章放在项目根目录下的独立文件夹：

```text
YYYY-MM-DD-文章主题/
├── 公众号排版版.html
├── 文章标题.md
└── assets/
    ├── cover-*-ai.png
    ├── *-ai.png
    └── ...
```

不要把最终 HTML 和文章成稿放在素材参考目录里。素材参考目录只保留原始参考图、资料或截图。

## 页面结构

HTML 页面必须包含两层：

1. 预览工具层：只给本地使用，不复制到公众号。
2. 正文内容层：`<main id="wechatArticle">`，复制按钮只复制这一层。

工具层包含：

- 页面标题：`公众号排版预览`
- 简短提示：复制正文区域后粘贴到微信公众平台编辑器
- 复制按钮：`复制公众号正文`

正文层包含：

- 封面图
- 栏目小字，例如 `应急科普 · 化工安全`
- H1 标题
- 摘要提示块
- 正文段落
- 分节 H2
- 重点提示块
- 图片
- 速记表或深色总结块
- 文末转发引导

## 视觉风格

整体风格：克制、清晰、专业、适合应急安全科普。

固定设计语言：

- 主色：深蓝黑 `#0f172a`
- 强调色：安全红 `#b91c1c`
- 正文色：`#1f2937`
- 次级文字：`#64748b`
- 浅底色：`#f8fafc`
- 警示浅红：`#fef2f2`
- 边框色：`#e2e8f0` 或 `#dbe4ee`

排版规则：

- 正文最大宽度：`720px`
- 正文字号：`16px`
- 正文行高：`1.95`
- H1：`28px`，居中，深蓝黑，粗体
- H2：`22px`，左侧编号标签，底部细线
- 段落间距：下边距 18px 左右
- 图片：宽度 100%，圆角 8px，正文图上下留白
- 重点句：使用红色粗体，不使用荧光高亮

## 微信复制兼容要求

正文区域必须尽量使用内联样式。

要求：

- 正文内容放在 `id="wechatArticle"` 的 `<main>` 中。
- 用 JavaScript 复制 `wechatArticle.outerHTML`，同时提供纯文本兜底。
- 图片使用相对路径，例如 `assets/cover-storage-tanks-ai.png`。
- 不依赖外部 CSS、CDN、字体或远程脚本。
- 不使用复杂交互、动画或需要构建工具的前端框架。

允许在页面 `<style>` 中写工具层样式；正文核心样式仍应内联，便于复制到公众号编辑器后保留主要效果。

## 内容处理规则

从 Markdown 转 HTML 时：

- 去掉“发布信息”“资料依据与说明”等后台说明，除非用户明确要求保留。
- 保留标题、摘要、正文、图片、结尾引导。
- 不把素材图当正文图；正文图应引用本期 `assets/` 中的最终图片。
- 图片顺序应服务阅读节奏，不机械堆图。
- 长列表尽量改成卡片或提示块，避免手机端太碎。
- 结尾必须保留一个可转发理由。

## 统一组件

### 摘要块

用于 H1 下方，样式：

```html
<p style="margin: 18px auto 0; padding: 14px 16px; border-left: 4px solid #b91c1c; background: #f8fafc; color: #475569; font-size: 15px; line-height: 1.8;">摘要内容</p>
```

### H2 标题

使用中文编号标签：

```html
<h2 style="margin: 34px 0 16px; padding: 0 0 10px; border-bottom: 2px solid #e2e8f0; color: #0f172a; font-size: 22px; line-height: 1.45; font-weight: 800;"><span style="display: inline-block; padding: 2px 10px; margin-right: 8px; border-radius: 4px; background: #0f172a; color: #ffffff; font-size: 15px;">一</span>小标题</h2>
```

### 重点提示块

普通重点：

```html
<section style="margin: 22px 0; padding: 18px 18px; border-left: 5px solid #f97316; background: #fff7ed;">
  <p style="margin: 0; color: #7c2d12; font-weight: 800;">重点内容</p>
</section>
```

风险提醒：

```html
<section style="margin: 22px 0; padding: 18px; border-radius: 8px; background: #fef2f2; border: 1px solid #fecaca;">
  <p style="margin: 0; color: #991b1b; font-weight: 800;">风险提醒内容</p>
</section>
```

深色总结：

```html
<section style="margin: 28px 0 0; padding: 20px 18px; border-radius: 8px; background: #0f172a; color: #ffffff; text-align: center;">
  <p style="margin: 0; font-size: 18px; line-height: 1.8; font-weight: 800;">总结或转发引导</p>
</section>
```

## 复制脚本

每个 HTML 页面保留复制脚本：

```html
<script>
  const copyBtn = document.getElementById('copyBtn');
  const article = document.getElementById('wechatArticle');

  copyBtn.addEventListener('click', async () => {
    const html = article.outerHTML;
    const text = article.innerText;
    try {
      if (navigator.clipboard && window.ClipboardItem) {
        await navigator.clipboard.write([
          new ClipboardItem({
            'text/html': new Blob([html], { type: 'text/html' }),
            'text/plain': new Blob([text], { type: 'text/plain' })
          })
        ]);
      } else {
        const range = document.createRange();
        range.selectNode(article);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        document.execCommand('copy');
        selection.removeAllRanges();
      }
      copyBtn.textContent = '已复制';
      setTimeout(() => copyBtn.textContent = '复制公众号正文', 1800);
    } catch (error) {
      const range = document.createRange();
      range.selectNode(article);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      copyBtn.textContent = '已选中，请按 Ctrl+C';
    }
  });
</script>
```

## 交付前检查

完成后检查：

- HTML 是否在对应本期文件夹下。
- 图片是否在同级 `assets/` 下，并使用相对路径引用。
- 正文是否没有引用素材目录中的原始参考图。
- `id="wechatArticle"` 是否只包住要复制到公众号的正文。
- 是否保留复制按钮。
- 是否去掉后台说明、资料依据、内部提示。
- 是否能直接用浏览器打开。
