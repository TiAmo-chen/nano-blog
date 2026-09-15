# nano-blog

一个**几乎零 JavaScript** 的极简静态博客生成器 —— 架构参考 <https://nano-ai.tech/>。

```
Markdown  →  markdown-it-py (GFM)  →  Pygments(nowrap)  →  纯静态 HTML + 2 个 CSS
```

- 没有前端框架、没有打包器、没有数据库、没有服务端
- 全站 JS 只有主题切换的一小段内联脚本（约 20 行），没有外部脚本文件
- 代码高亮是构建期完成的（Pygments 短类名，和参考站同一套做法）
- 产出物只有 HTML / CSS / SVG，可以直接丢给任何静态托管（EdgeOne Pages、Cloudflare Pages、Vercel、GitHub Pages…）
- 附带 `sitemap.xml` / `robots.txt` / `feed.xml` / `404.html` / OG 标签（参考站这几项是缺的）

## 目录结构

```
nano-blog/
├── build.py              # 生成器（唯一的核心脚本）
├── serve.py              # 本地预览服务器
├── requirements.txt
├── content/              # 内容：Markdown 文章
│   ├── _about.md         # 「关于我」页（下划线开头 = 不当作文章）
│   └── <slug>.md         # 每篇文章一个文件
├── theme/                # 主题：手写 CSS + favicon
│   ├── styles.css        # 首页
│   ├── articles.css      # 内容页（Pygments 配色由 build.py 追加）
│   └── favicon.svg
├── tools/
│   └── import_note.py    # 从 Obsidian 导入笔记并自动补 front matter
└── public/               # 构建产物（已 gitignore）
```

## 快速开始

```bash
pip install -r requirements.txt

python build.py        # 生成 public/
python serve.py        # 打开 http://127.0.0.1:8000/
```

改完 Markdown 或 CSS 后重新 `python build.py` 即可；本地预览带 `no-store`，刷新就是最新内容。

## 写一篇文章

在 `content/` 下新建 `my-post.md`：

```markdown
---
title: 标题
date: 2026-09-14
tags: [工作记录, 笔记]
summary: 可选，不写就从正文首段自动摘
slug: my-post          # 可选，默认取文件名
---

正文（Markdown，支持表格 / 删除线 / 代码高亮，单个换行也会生效，和 Obsidian 一致）。
```

文件名以 `YYYY-MM-DD` 开头时，日期会自动从文件名取。

### 从 Obsidian 导入

```bash
python tools/import_note.py "D:\Obsidian\...\2026-09-10.md" \
  --title "S1100+ 课程分享：真正的计算机素养是什么" \
  --tags 计算机基础,学习笔记 --slug computer-literacy
```

脚本会补好 front matter、去掉与标题重复的 H1、写到 `content/<slug>.md`。

## 站点配置

改 `build.py` 顶部的 `SITE` 字典：

| 字段 | 作用 |
|---|---|
| `title` / `description` | 站点名与默认描述（进 `<title>`、OG、RSS） |
| `tagline` | 页脚与首页的口号 |
| `author` | `<meta name="author">` |
| `base_url` | **部署前必须改**，用于 sitemap / og:url / RSS 里的绝对链接 |
| `home_headline` | 首页大字标题 |
| `recent` | 首页「最近更新」条数 |

同文件里的 `ACTIVITY`（首页「最近在做」）和 `SOCIALS`（社交链接）也在这里改。

## 部署到 EdgeOne Pages

1. 把仓库推到 GitHub / Gitee / GitLab，或在本地直接构建。
2. 腾讯云 EdgeOne 控制台 → **Makers / Pages** → 新建项目。
3. 部署方式二选一：
   - **上传目录**：把 `public/` 整个拖进控制台。
   - **CLI**：`npm i -g edgeone && edgeone makers deploy -n nano-blog -e production`（默认发布 `public/`；本项目是纯静态站，不需要远端构建步骤，本地 `python build.py` 后上传即可）。
   - **Git 集成**：构建命令填 `pip install -r requirements.txt && python build.py`，输出目录填 `public`。
4. 域名管理 → 添加自定义域名 → 按提示做归属权验证 + 加 CNAME，再到 HTTPS 里配证书（可用 EdgeOne 免费证书）。
5. 加速区域包含「中国大陆」时，域名需要先完成**工信部备案**；只用海外区则不需要。

## 两种可选改进

- 装上 `linkify-it-py`，正文里的裸链接会自动变成 `<a>`。
- 深色模式已内置：默认跟随系统，右上角/顶栏的按钮可手动切换，选择记在 `localStorage`。

## 致谢

- 站点形态与首页布局参考了 [nano-ai.tech](https://nano-ai.tech/)（Hexo 转向自建静态站、单色排版、首页侧栏 + 大字标语的结构），生成器与样式均为本项目原创实现，未使用对方任何素材。
- 渲染管线依赖：[markdown-it-py](https://github.com/executablebooks/markdown-it-py)、[Pygments](https://pygments.org/)。
- 托管：[GitHub Pages](https://pages.github.com/) + [Cloudflare](https://www.cloudflare.com/)。
- 首页配图：`theme/hero.svg`（原创 SVG）；如果想换成你自己的 3D 头像，把图片放进 `theme/` 并在 `build.py` 里改 `page_home()` 的 `<img src>` 即可。
