# SkillsHub Codex Marketplace

这是 SkillsHub 的 Codex plugin marketplace 仓库。每个 skill 独立包装成一个 Codex plugin，方便按需安装和管理。

## 市场名称

```text
skillshub-codex
```

## 目录结构

```text
.agents/plugins/marketplace.json
plugins/
  anxin-image-gen/
    .codex-plugin/plugin.json
    skills/anxin-image-gen/
  anxin-ppt/
    .codex-plugin/plugin.json
    skills/anxin-ppt/
```

## 本地测试

从本地目录添加 marketplace：

```powershell
codex plugin marketplace add E:\YuHonglei\Skills\codex-skills-marketplace
```

查看可安装插件：

```powershell
codex plugin list
```

安装单个技能插件：

```powershell
codex plugin add anxin-ppt@skillshub-codex
```

## GitHub 使用

发布到 GitHub 后，可以使用：

```powershell
codex plugin marketplace add leinatorX/codex-skills-marketplace --ref main
codex plugin add anxin-ppt@skillshub-codex
```

## 源仓库关系

原始 skill 内容建议以 `SkillsHub Skills` 仓库为唯一源。此仓库是 Codex marketplace 发布形态；更新 skill 时，应从源仓库同步后再校验每个 plugin。
