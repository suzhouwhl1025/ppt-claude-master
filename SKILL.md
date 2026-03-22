# PPT Master - OpenClaw Skill

> AI 驱动的多格式 SVG 内容生成系统，将 PDF/URL/Markdown 转换为精美可编辑的 PowerPoint 演示文稿

[![Version](https://img.shields.io/badge/version-v2.2.0-blue.svg)](https://github.com/hugohe3/ppt-master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 功能特性

### 核心能力

- **多格式输入**：支持 PDF、URL、Markdown 文档直接转换为 PPT
- **AI 智能设计**：通过策略师-执行器多角色协作，自动生成专业设计
- **SVG 矢量导出**：生成 SVG 格式页面，导出后可在 PowerPoint 中自由编辑
- **多场景适配**：支持 PPT 16:9、4:3、小红书、朋友圈、Story 等 10+ 格式
- **丰富模板**：内置 24 种布局模板、35 种图表模板、640+ 矢量图标

### 设计风格

| 风格 | 适用场景 | 特点 |
|------|----------|------|
| **通用灵活** | 视觉冲击优先 | 创意展示、营销物料 |
| **咨询风格** | 数据清晰优先 | 团队汇报、数据分析 |
| **顶级咨询** | 逻辑说服优先 | MBB 级别高管汇报 |

---

## 工作流程

```
源文档 (PDF/URL/Markdown)
    ↓
Step 1: 项目初始化
    ↓
Step 2: 模板选择 (需用户确认)
    ↓
Step 3: 策略师阶段 - 八项确认 (需用户确认)
    ↓
Step 4: 图片生成 (可选)
    ↓
Step 5: 执行器阶段 - 生成 SVG + 演讲稿
    ↓
Step 6: 后处理 - 导出 PPTX
    ↓
输出: 可编辑的 PPTX 文件
```

---

## 使用方式

### 启动 PPT 生成

```typescript
import { main } from 'openclaw-ppt-master';

await main(ctx, {
  action: 'create_ppt',
  source: 'path/to/document.pdf',
  format: 'ppt169',
  style: 'consultant'
});
```

### 指定参数

```typescript
await main(ctx, {
  action: 'create_ppt',
  source: 'https://example.com/article',
  format: 'ppt169',
  style: 'general',
  pages: 10,
  template: 'google_style'
});
```

### 工作流步骤

```typescript
// 初始化项目
await main(ctx, {
  action: 'init_project',
  name: 'my-ppt',
  format: 'ppt169'
});

// 导入源文件
await main(ctx, {
  action: 'import_sources',
  projectPath: 'projects/my-ppt',
  sources: ['path/to/doc.pdf', 'https://example.com']
});

// 执行后处理
await main(ctx, {
  action: 'post_process',
  projectPath: 'projects/my-ppt'
});
```

---

## 配置参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | 是 | 操作类型：create_ppt, init_project, import_sources, post_process |
| `source` | string | 否 | 源文件路径或 URL |
| `format` | string | 否 | 输出格式：ppt169 (默认), ppt43, xhs, story 等 |
| `style` | string | 否 | 设计风格：general, consultant, consultant_top (默认 general) |
| `pages` | number | 否 | 预计页数 |
| `template` | string | 否 | 使用的模板名称 |

### 支持的格式

| 格式 | viewBox | 用途 |
|------|---------|------|
| ppt169 | 0 0 1280 720 | 16:9 演示文稿 |
| ppt43 | 0 0 1024 768 | 4:3 演示文稿 |
| xhs | 0 0 1242 1660 | 小红书笔记 |
| story | 0 0 1080 1920 | 短视频/抖音 |
| moments | 0 0 1080 1080 | 微信朋友圈 |

---

## 系统要求

- **Node.js**: >= 18.0.0
- **Python**: >= 3.8
- **操作系统**: macOS, Windows, Linux

### Python 依赖

```bash
pip install python-pptx>=0.6.21
pip install PyMuPDF>=1.23.0
pip install Pillow>=9.0.0
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.0
```

---

## 项目结构

```
openclaw-ppt-master/
├── skill.json              # Skill 元数据
├── package.json            # NPM 配置
├── tsconfig.json           # TypeScript 配置
├── SKILL.md                # 本文档
├── src/
│   └── index.ts            # TypeScript 入口
└── assets/                 # 资源链接
    └── ppt-master-skills/ # 指向原 ppt-master skills
```

---

## 示例输出

查看 [在线示例](https://hugohe3.github.io/ppt-master/) 了解生成的 PPT 效果。

### 示例项目

| 项目 | 页数 | 风格 |
|------|:----:|------|
| 心理治疗中的依恋 | 32 | 顶级咨询 |
| 构建有效AI代理 | 15 | 顶级咨询 |
| Google年度工作汇报 | 10 | 谷歌风 |
| Debug六步法 | 10 | 深色科技 |
| Git入门指南 | 10 | 像素复古 |

---

## 许可证

MIT License - see [LICENSE](../LICENSE)

## 作者

[hugohe3](https://github.com/hugohe3)

## 相关链接

- [GitHub 仓库](https://github.com/hugohe3/ppt-master)
- [在线示例](https://hugohe3.github.io/ppt-master/)
- [视频演示](https://www.youtube.com/watch?v=jM2fHmvMwx0)
