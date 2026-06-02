#!/usr/bin/env node
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const file = process.argv[2];

if (!file) {
  console.error('用法: node scripts/validate-blue-deck.mjs <index.html>');
  process.exit(2);
}

const allowedLayouts = new Set([
  'cover',
  'agenda',
  'section-divider',
  'overview',
  'problem',
  'solution',
  'architecture',
  'product-grid',
  'metrics',
  'data-dashboard',
  'chart-analysis',
  'financial-table',
  'comparison',
  'evidence-page',
  'roadmap',
  'case-study',
  'risk-action',
  'closing',
]);

const htmlPath = resolve(file);
const html = readFileSync(htmlPath, 'utf8');
const errors = [];
const warnings = [];

// 素材分类式的平行标签——用于检测目录页是否缺少叙事逻辑
const flatAgendaLabels = new Set([
  '组织概况',
  '核心使命',
  '枢纽角色',
  '工作基础',
  '核心能力',
  '展望建议',
  '组织架构',
  '业务范围',
  '产品矩阵',
]);

// 空泛词列表（扩充版）——无具体对象和数据支撑时禁止使用
const vagueTerms = [
  '赋能',
  '闭环',
  '提升能力',
  '全面提升',
  '显著提升',
  '强化管理',
  '推动发展',
  '打造平台',
  '高质量发展',
  '深度融合',
  '行业领先',
  '创新驱动',
  '全面覆盖',
  '显著增强',
  '构建生态',
  '数字化转型',
  '提质增效',
  '协同发展',
  '赋能发展',
  '全方位',
];

// 标签式标题检测——2-4 字的孤立名词标签，缺少判断和结论
const labelTitles = new Set([
  '公司概况',
  '核心能力',
  '产品矩阵',
  '合作伙伴',
  '技术架构',
  '解决方案',
  '行业背景',
  '问题与挑战',
  '案例展示',
  '工作基础',
  '推进计划',
  '组织架构',
  '市场分析',
  '总结展望',
  '数据分析',
  '业务范围',
  '发展历程',
  '核心价值',
  '服务体系',
  '团队介绍',
  '愿景使命',
  '战略规划',
  '成果展示',
  '未来展望',
  '项目概述',
  '背景介绍',
  '风险提示',
  '行动建议',
]);

function attr(tag, name) {
  return tag.match(new RegExp(`\\b${name}="([^"]*)"`))?.[ 1]?.trim() ?? '';
}

function plainText(fragment) {
  return fragment
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// 提取页面标题文本（h1 或 h2）
function extractTitles(slideHtml) {
  const titles = [];
  for (const m of slideHtml.matchAll(/<(h[12])[^>]*>([\s\S]*?)<\/\1>/gi)) {
    titles.push(plainText(m[2]));
  }
  return titles;
}

if (html.includes('[必填]')) errors.push('存在未替换的 [必填] 占位符。');
if (html.includes('<!-- SLIDES_HERE -->')) errors.push('模板中仍保留 SLIDES_HERE，占位内容未替换。');
if (/Escape['"]\)\s*go\(0\)|e\.key===['"]Escape['"][\s\S]{0,80}go\(0\)/.test(html)) {
  errors.push('Esc 不应返回首页，必须用于打开/关闭缩略图索引页。');
}
if (slidesNeedRuntimeCheck(html) && !/\bid=['"]overview['"]|overview\.id=['"]overview['"]/.test(html)) {
  errors.push('缺少缩略图索引页运行时，Esc 无法显示页面缩略图。');
}

function slidesNeedRuntimeCheck(source) {
  return source.includes('id="deck"') || source.includes("id='deck'");
}

const slideRe = /<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>[\s\S]*?<\/section>/g;
const slides = [...html.matchAll(slideRe)].map((m, index) => {
  const tag = m[0].match(/<section\b[^>]*>/)?.[0] ?? '';
  return { index: index + 1, html: m[0], tag };
});

if (!slides.length) errors.push('没有找到 <section class="slide"> 页面。');

if (slides.length) {
  const firstLayout = attr(slides[0].tag, 'data-layout');
  const secondLayout = slides[1] ? attr(slides[1].tag, 'data-layout') : '';
  if (firstLayout !== 'cover') errors.push('第一页必须使用 data-layout="cover"。');
  if (!/\bcover-full\b/.test(slides[0].tag)) errors.push('第一页封面必须使用 class="slide cover-full" 的全屏背景结构。');
  if (!/<div\b[^>]*class="[^"]*\bcover-bg\b[^"]*"[\s\S]*?<img\b[^>]*src="images\//.test(slides[0].html)) {
    errors.push('第一页封面必须包含来自 images/ 目录的 .cover-bg img，不能使用纯色背景代替主视觉。');
  }
  if (/\bfooter\b|\bdots\b|\bcover-meta\b|\blead\b|\bchrome\b/.test(slides[0].html)) {
    errors.push('第一页封面只保留背景图和中文大标题，不应包含页码、说明段落、导航点或页眉页脚。');
  }
  if (slides.length > 1 && secondLayout !== 'agenda') errors.push('第二页必须使用 data-layout="agenda" 作为目录页。');

  if (slides[1]) {
    const agendaText = plainText(slides[1].html);
    const flatCount = [...flatAgendaLabels].filter((label) => agendaText.includes(label)).length;
    if (flatCount >= 4) {
      errors.push('第二页目录过于像素材分类列表，请按"背景 -> 问题 -> 方案 -> 证明 -> 行动"的叙事链重写。');
    }
  }

  const titleText = plainText(html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? '');
  const reportLike = /年度|年报|报表|财报|经营|工作总结|复盘|完成情况/.test(titleText);
  if (reportLike && slides.length < 12) {
    warnings.push('报表、经营复盘或工作总结类 PPT 页数偏少，建议使用 14-22 页标准汇报结构。');
  }
}

for (const slide of slides) {
  const layout = attr(slide.tag, 'data-layout');
  if (!layout) {
    errors.push(`第 ${slide.index} 页缺少 data-layout。`);
  } else if (!allowedLayouts.has(layout)) {
    errors.push(`第 ${slide.index} 页 data-layout="${layout}" 不在允许版式中。`);
  }

  if (slide.index > 1) {
    if (!attr(slide.tag, 'data-question')) errors.push(`第 ${slide.index} 页缺少 data-question，无法判断本页回答的问题。`);
    if (!attr(slide.tag, 'data-message')) errors.push(`第 ${slide.index} 页缺少 data-message，无法判断本页核心结论。`);
  }

  const text = plainText(slide.html);
  const cardCount = (slide.html.match(/class="[^"]*\bcard\b/g) ?? []).length;
  const numberCount = (text.match(/\d+(?:\.\d+)?%?|\d+(?:\.\d+)?\s*(?:亿|万|GWh|GW|家|个|项|年|月)/g) ?? []).length;
  const vagueCount = vagueTerms.filter((term) => text.includes(term)).length;

  // ===== 新增：标题检查 =====

  // 正文页必须有 h2 或 h3 标题（封面和章节页除外）
  const titles = extractTitles(slide.html);
  const hasH2 = /<h2\b/.test(slide.html);
  const hasH3 = /<h3\b/.test(slide.html);
  if (slide.index > 1 && layout !== 'section-divider' && !hasH2) {
    errors.push(`第 ${slide.index} 页缺少 <h2> 页面标题，每个正文页必须有标题。`);
  }

  // 检测标签式标题
  for (const title of titles) {
    const trimmed = title.trim();
    if (labelTitles.has(trimmed)) {
      errors.push(`第 ${slide.index} 页标题"${trimmed}"是孤立标签，请改写为结论句。参考 content-guide.md 的标题对照表。`);
    }
  }

  // ===== 新增：卡片内容检查 =====

  // 检查卡片是否有实质内容（不只是空标签）
  if (cardCount > 0) {
    const cardMatches = [...slide.html.matchAll(/<div\b[^>]*class="[^"]*\bcard\b[^"]*"[^>]*>([\s\S]*?)<\/div>\s*(?=<div\b[^>]*class="[^"]*\bcard\b|<\/div>)/g)];
    let emptyCards = 0;
    for (const cm of cardMatches) {
      const cardText = plainText(cm[1]);
      if (cardText.length < 10) emptyCards++;
    }
    if (emptyCards > 0) {
      warnings.push(`第 ${slide.index} 页有 ${emptyCards} 个卡片内容过少（少于 10 字），请补充具体事实。`);
    }
  }

  // 正文信息偏少（门槛从 90 提升到 120 字符）
  if (slide.index > 2 && layout !== 'section-divider' && text.length < 120) {
    warnings.push(`第 ${slide.index} 页正文信息偏少（${text.length} 字符），可能显得空泛。建议至少 120 个字符。`);
  }

  // 卡片较多但缺少数字且空泛词多
  if (slide.index > 2 && layout !== 'section-divider' && cardCount >= 3 && numberCount === 0 && vagueCount >= 2) {
    warnings.push(`第 ${slide.index} 页卡片较多但缺少数字或具体对象，且存在较多抽象词，建议补充事实支撑。`);
  }

  // 内联超大字号
  if (slide.index > 1 && /font-size:\s*min\(\s*(?:5(?:\.\d+)?|[6-9](?:\.\d+)?|[1-9]\d+(?:\.\d+)?)vw/i.test(slide.html)) {
    warnings.push(`第 ${slide.index} 页存在偏大的内联标题字号，建议使用模板默认字号层级。`);
  }

  // CJK 字符密度
  const cjkCount = (text.match(/[\u4e00-\u9fff]/g) ?? []).length;
  if (layout === 'agenda' && cjkCount > 220) {
    warnings.push(`第 ${slide.index} 页目录文字偏多，建议控制为 4-6 个章节和短句说明。`);
  } else if (slide.index > 1 && cjkCount > 680) {
    warnings.push(`第 ${slide.index} 页正文文字偏多，可能会削弱汇报逻辑和阅读节奏。`);
  }

  // 英文词过多
  const englishWords = text.match(/[A-Za-z]{4,}/g) ?? [];
  if (englishWords.length > 16) {
    warnings.push(`第 ${slide.index} 页英文词较多，请确认不是无意义中英混排。`);
  }

  // ===== 新增：空泛词过多单独告警 =====
  if (slide.index > 2 && layout !== 'section-divider' && vagueCount >= 3) {
    warnings.push(`第 ${slide.index} 页使用了 ${vagueCount} 个空泛词（${vagueTerms.filter(t => text.includes(t)).join('、')}），请用具体事实替换。`);
  }

  // 图片检查
  for (const img of slide.html.matchAll(/<img\b[^>]*src="([^"]+)"/g)) {
    const imgTag = img[0];
    const src = img[1];
    if (/^(https?:)?\/\//.test(src) || src.startsWith('data:')) continue;
    const imgPath = resolve(dirname(htmlPath), src);
    if (!existsSync(imgPath)) {
      errors.push(`第 ${slide.index} 页图片不存在: ${src}`);
    }
    if (/(diagram|flow|loop|ecology|architecture|架构|流程|闭环|生态)/i.test(src) && /object-fit:\s*cover/i.test(imgTag) && !/\bimage-contain\b/.test(slide.html)) {
      errors.push(`第 ${slide.index} 页图表类图片不应使用 object-fit: cover，避免裁切关键文字: ${src}`);
    }
  }
}

if (warnings.length) {
  console.warn('提示:');
  for (const warning of warnings) console.warn(`- ${warning}`);
}

if (errors.length) {
  console.error('校验失败:');
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`校验通过: ${slides.length} 页。`);
