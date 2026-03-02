# Daily World Quotes (中英双语)

自动生成每天一条不重复的世界名人名家语录（中英双语），用于抖音发布。

## 功能
- 每天抽取一条中文语录（来源：一言 hitokoto）
- 自动翻译成英文（MyMemory 免费翻译 API）
- 去重：不会重复使用同一条语录（通过 `data/used_ids.json` 记录）
- 漂亮展示页：`docs/index.html`
- 可部署到 GitHub Pages
- 本机可设置定时自动打开页面

## 本地生成今日语录
```bash
python3 scripts/generate_quote.py
```

## 目录
- `scripts/generate_quote.py` 生成今日语录
- `docs/index.html` 展示页面
- `docs/data/today.json` 今日语录
- `docs/data/history.json` 历史语录
- `.github/workflows/daily-quote.yml` 每日自动更新（GitHub Actions）
- `scripts/install_open_url_launchd.sh` 安装本机定时打开网址任务

## GitHub Pages 发布
1. 新建 GitHub 仓库并 push 本项目
2. 在 GitHub 仓库设置中启用 Pages（Source: GitHub Actions）
3. 默认每天 09:05 (Asia/Shanghai) 自动更新
