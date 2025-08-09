
## Auto Anime DL

一个集“动漫资源采集、云盘自动下载、在线播放、数据增强与前端展示”为一体的自动化平台。

### 功能概览

- **RSS 采集与增强**：抓取 RSS，解析番剧与剧集、磁力、发布时间，并爬取封面生成结构化 JSON。
- **PikPak 扫描与直链补全**：递归扫描云盘，自动匹配剧集，补全在线播放直链 `play_url`。
- **自动化离线下载**：按番剧自动建目录、批量添加磁力下载、监控任务进度（可选）。
- **定时任务 + 去重**：默认每 6 小时自动抓取，仅为“新增剧集”添加下载，使用持久化状态文件避免重复。
- **后端 API + 前端**：后端提供 JSON 读接口与调度调试端点；前端展示番剧列表与详情并支持在线播放/外部播放器。

### 目录结构

```text
Auto_Anime_DL/
├── auto_anime_dl/
│   ├── __init__.py
│   ├── config.py            # 环境变量与默认路径集中管理
│   ├── utils.py             # JSON IO / env / fs 工具
│   ├── pikpak.py            # PikPakScanner / PikPakManager 封装
│   ├── rss.py               # RSS 采集与封面增强
│   ├── scheduler.py         # 定时抓取 + 去重 + 下发离线下载
│   └── state.py             # 状态文件（processed_keys）读写
├── main.py                  # FastAPI：/api/* + 前端静态目录
├── rssworker.py             # 入口：抓取 RSS 并增强封面
├── pikpak_dl.py             # 入口：扫描云盘并补全播放直链
├── pikpak_automation.py     # 入口：批量建目录、添加下载、监控任务（可选）
├── bangumi.json
├── bangumi_with_cover.json
├── bangumi_with_play_url.json
├── pikpak_folder_structure.json
├── .processed_state.json    # 持久化去重状态（自动生成）
└── frontend/
    ├── index.html
    ├── detail.html
    ├── app.js               # 请求 /api/bangumi_with_play_url
    ├── detail.js            # 请求 /api/bangumi_with_play_url
    └── style.css
```

### 数据流与产物

1) `rssworker.py`：抓取 RSS → 生成 `bangumi.json` → 爬封面 → 生成 `bangumi_with_cover.json`
2) `pikpak_dl.py`：扫描云盘 → 匹配剧集 → 回填直链 → 生成 `bangumi_with_play_url.json`
3) `pikpak_automation.py`（可选）：创建番剧目录、添加离线下载、监控状态
4) `main.py`：API 提供三份 JSON 的读取，前端从 API 渲染页面
5) `scheduler.py`：后台定时抓取，仅为“新增剧集”触发下载，状态写入 `.processed_state.json`

### 依赖要求

- Python >= 3.11
- 主要依赖见 `pyproject.toml`：FastAPI、Uvicorn、aiohttp、requests、feedparser、beautifulsoup4、pikpakapi 等

### 安装与启动

1) 安装依赖
```bash
pip install -e .
```

2) 配置环境变量（推荐）
在 `~/.zshrc` 末尾追加：
```bash
export PIKPAK_USERNAME="你的账号邮箱"
export PIKPAK_PASSWORD="你的账号密码"
# 可选：不设置则使用默认
export PIKPAK_ROOT_FOLDER_ID="你的根目录ID"

# 定时周期（秒），默认 21600 = 6 小时
export SCHEDULE_INTERVAL_SECONDS=21600

# 可替换为你的 RSS 源
export RSS_URL_ANIME_COLLECTION="https://api.animes.garden/collection/你的id/feed.xml"
```
生效并启动后端：
```bash
source ~/.zshrc
uvicorn main:app --reload
```

3) 采集与增强（可直接通过入口脚本运行）
```bash
python rssworker.py                # RSS -> bangumi.json -> 封面增强 -> bangumi_with_cover.json
python pikpak_dl.py                # 扫描云盘 -> 回填播放直链 -> bangumi_with_play_url.json
# 可选：自动化下载
python pikpak_automation.py        # 建目录 + 添加离线下载 + 监控
```

4) 访问前端
- 浏览器打开 `http://127.0.0.1:8000/`
- 前端会从 `/api/bangumi_with_play_url` 读取数据

### 后端 API

- `/api/bangumi`：返回 `bangumi.json`
- `/api/bangumi_with_cover`：返回 `bangumi_with_cover.json`
- `/api/bangumi_with_play_url`：返回 `bangumi_with_play_url.json`
- `/api/scheduler/status`（GET）：查看调度器状态
  - `interval_seconds`：当前周期（秒）
  - `processed_count`：状态文件中已记录的唯一键数量
- `/api/scheduler/run_once`（GET/POST）：立即执行一轮抓取与去重下发
  - 返回：`{ ok, rss: {titles, episodes}, new_items, skipped_no_hash, processed_total }`

### 定时任务与去重策略

- 后端启动时，调度器自动后台运行（默认每 6 小时）。
- 每轮流程：抓取 RSS → 合并条目 → 从 `magnet` 提取 `btih`（若存在）
  - **唯一键优先级**：
    1) infohash（从 magnet 提取的 btih）
    2) 组合键 `番剧名 || 文件名 || bt_url`（当无法解析 btih 时确保同链接不重复下载）
- 去重状态保存在仓库根 `.processed_state.json` 的 `processed_keys` 字段中，首次执行会自动生成。
- 仅对“未出现过的唯一键”触发 `PikPak` 离线下载。

### 常见问题

- 访问 `/api/*` 返回 404：请确认后端已重启，且静态目录挂载在 API 路由之后（本项目已处理）。
- 调度器没有动作：检查环境变量是否在当前终端生效；可临时将 `SCHEDULE_INTERVAL_SECONDS=60` 并重启观察。
- `.processed_state.json` 不生成：调用一次 `/api/scheduler/run_once`，即使没有新增也会写入空状态。
- 一直重复下载：请检查该源的 magnet 是否包含稳定的 btih；若无，已使用组合键去重。仍有问题请提供示例条目以便定制解析。

### 安全建议

- 不要把账号密码写入代码；优先使用环境变量。
- 请勿将 `.processed_state.json`、日志或私密配置上传到公开仓库。

---

## 文件职责与执行顺序（超详细）

### 1) 执行顺序（建议）
- 首次初始化：
  1. 运行 `rssworker.py` 产出 `bangumi.json` 与 `bangumi_with_cover.json`
  2. 运行 `pikpak_dl.py` 扫描云盘并补全直链，产出 `bangumi_with_play_url.json`
  3. 启动后端：`uvicorn main:app --reload`（前端访问首页）
  4. 可选：`pikpak_automation.py` 自动建目录与离线下载
- 长期运行：
  - 一直运行后端（`uvicorn`），后台 `scheduler` 会每 `SCHEDULE_INTERVAL_SECONDS` 自动抓取 RSS，并仅对“新增条目”离线下载
  - 需立刻执行一轮时：访问 `/api/scheduler/run_once`

### 2) 根目录脚本（入口层）
- `main.py`
  - 职责：FastAPI 后端；提供 JSON 读接口 + 调度调试端点；挂载 `frontend/` 为静态站点
  - 启动：`uvicorn main:app --reload`
  - 路由：
    - `/api/bangumi` → 读 `bangumi.json`
    - `/api/bangumi_with_cover` → 读 `bangumi_with_cover.json`
    - `/api/bangumi_with_play_url` → 读 `bangumi_with_play_url.json`
    - `/api/scheduler/status` → 调度周期与累计去重数量
    - `/api/scheduler/run_once`（GET/POST）→ 立即执行一轮抓取→去重→下发
  - 执行逻辑：
    - 应用启动时创建后台任务启动 `scheduler`（按 `SCHEDULE_INTERVAL_SECONDS` 周期执行）
    - 最后挂载静态目录，避免遮蔽 `/api/*` 路由

- `rssworker.py`
  - 职责：抓取 `config.RSS_URLS` 中各 RSS 源，解析为 `Bangumi` 结构并抓封面
  - 执行逻辑：
    - `get_rss_feed` 读取 RSS → `extract_rss_data` 解析为 `{title: [episodes]}`
    - 合并多个源的条目
    - 对每部番剧的详情页 `fetch_cover_from_link` 抓封面（间隔 1s），写入 `cover_info`
    - 写入 `bangumi.json` 与 `bangumi_with_cover.json`

- `pikpak_dl.py`
  - 职责：扫描 `ROOT_FOLDER_ID` 下的云盘结构，匹配番剧集数并补全 `play_url`
  - 执行逻辑：
    - `PikPakScanner.login` → `scan_folder_structure` 递归得到树状结构
    - 遍历 `bangumi_with_cover.json`：对每集用 `extract_episode` 提取集数
    - 在云盘结构中匹配，命中后 `get_file_info` 提取直链（优先 medias[0].link.url）
    - 结果写入 `bangumi_with_play_url.json`

- `pikpak_automation.py`（可选）
  - 职责：按番剧自动建目录并批量添加离线下载；可监控下载状态
  - 执行逻辑：
    - `PikPakManager.login` → `setup_root_folder` 校验根目录
    - `create_folder` 为番剧建目录（无则建，有则复用）
    - `add_download_task` 为每集磁力添加离线下载（节流 1s）
    - `monitor_downloads` 周期统计任务状态输出到日志 `pikpak_automation.log`

### 3) 包模块（核心逻辑层：`auto_anime_dl/`）
- `auto_anime_dl/__init__.py`
  - 职责：初始化包导出，便于在入口脚本中统一引用

- `auto_anime_dl/config.py`
  - 职责：集中管理环境与路径配置
  - 关键变量：
    - `PIKPAK_USERNAME`、`PIKPAK_PASSWORD`、`ROOT_FOLDER_ID`
    - `RSS_URLS`（可通过 `RSS_URL_ANIME_COLLECTION` 环境变量覆盖）
    - 数据路径：`BANGUMI_JSON_PATH`、`BANGUMI_WITH_COVER_JSON_PATH`、`BANGUMI_WITH_PLAY_URL_PATH`、`FOLDER_STRUCTURE_PATH`
    - 调度：`STATE_PATH`（`.processed_state.json`）与 `SCHEDULE_INTERVAL_SECONDS`（默认 21600）

- `auto_anime_dl/utils.py`
  - 职责：工具函数
  - `ensure_dir`、`read_json`、`write_json`、`get_env`

- `auto_anime_dl/rss.py`
  - 职责：RSS 解析与封面抓取
  - 主要函数：`get_rss_feed`、`extract_rss_data`、`fetch_cover_from_link`、`enhance_bangumi_data`
  - 说明：提供 `create_ssl_context` 以宽松 SSL（应对证书异常源）

- `auto_anime_dl/pikpak.py`
  - 职责：封装 PikPak 逻辑
  - `PikPakManager`：登录、根目录校验、创建目录、添加离线任务、监控任务
  - `PikPakScanner`：登录、递归扫描、标准化名称/提取集数、匹配剧集、获取直链

- `auto_anime_dl/state.py`
  - 职责：去重状态读写，使用 `processed_keys`（兼容历史 `processed_infohashes`）
  - `load_processed_keys` / `save_processed_keys`

- `auto_anime_dl/scheduler.py`
  - 职责：定时抓取 RSS → 去重 → 触发离线下载
  - 主要函数：
    - `run_once()`：
      - 读取配置 → 抓取与合并 RSS → 统计番剧和条目数量
      - 去重策略（见下）筛出“新增条目”
      - 调用 `PikPakManager` 对新增条目添加下载
      - 写入 `.processed_state.json` 的 `processed_keys`
      - 返回 `{ ok, rss: {titles, episodes}, new_items, skipped_no_hash, processed_total }`
    - `run_scheduler()`：按照 `SCHEDULE_INTERVAL_SECONDS` 周期执行 `run_once()`
  - 去重策略：
    - 优先使用从 `magnet` 中提取的 `btih`（v1 hex/base32 均可）
    - 若无法解析，则使用组合键 `番剧名 || 文件名 || bt_url` 保证幂等（同一条不重复下载）

### 4) 前端（`frontend/`）
- `index.html`：番剧列表页；`app.js` 从 `/api/bangumi_with_play_url` 拉数据并渲染
- `detail.html`：番剧详情页；`detail.js` 支持复制磁力、IINA/PotPlayer 打开播放直链、flv.js 播放
- `style.css`：页面样式

### 5) 数据文件与产物
- `bangumi.json`：RSS 原始整合
- `bangumi_with_cover.json`：封面增强
- `bangumi_with_play_url.json`：补全直链（前端展示）
- `pikpak_folder_structure.json`：云盘结构缓存
- `.processed_state.json`：调度去重状态
- `pikpak_automation.log`：自动化下载日志


# Auto Anime DL - 自动化动漫下载与在线播放平台

## 项目简介

Auto Anime DL 是一个集“动漫资源采集、云盘自动下载、在线播放、数据增强与美观前端”为一体的自动化动漫管理平台。适合动漫爱好者一键收集、整理、在线播放和管理自己的番剧资源。

---

## 功能亮点

- **RSS 自动采集**：通过 `rssworker.py` 自动抓取指定 RSS 源的最新动漫资源，解析剧集、磁力链接、发布时间等。
- **数据增强**：自动爬取动漫封面、完善剧集元数据，生成结构化 JSON 数据。
- **PikPak 云盘自动化**：
  - `pikpak_dl.py`：递归扫描 PikPak 云盘文件夹，自动匹配剧集，提取在线播放直链。
  - `pikpak_automation.py`：自动创建番剧文件夹、批量添加下载任务、监控下载进度。
- **后端 API**：`main.py` 基于 FastAPI，提供动漫数据查询、搜索、详情等接口。
- **响应式前端**：`frontend/` 目录下为现代化网页，支持动漫列表、详情、在线播放、磁力复制、外部播放器（IINA/PotPlayer）一键打开、主题切换等。

---

## 核心流程与数据流转

1. **采集与数据增强**
   - 运行 `rssworker.py`，采集 RSS，生成 `bangumi.json`，并自动抓取封面生成 `bangumi_with_cover.json`。
2. **云盘扫描与直链补全**
   - 运行 `pikpak_dl.py`，递归扫描 PikPak 云盘，自动为每集补全在线播放直链，生成 `bangumi_with_play_url.json`。
3. **自动化下载（可选）**
   - 运行 `pikpak_automation.py`，自动创建云盘文件夹并批量添加下载任务。
4. **API 服务与前端展示**
   - 运行 `main.py`（或 `uvicorn main:app --reload`），提供动漫数据 API。
   - 前端页面通过 JS 加载 `bangumi_with_play_url.json`，实现动漫展示与在线播放。

---

## 目录结构说明（已重构）

```text
Auto_Anime_DL/
├── auto_anime_dl/
│   ├── __init__.py
│   ├── config.py            # 环境变量与默认路径集中管理
│   ├── utils.py             # JSON IO / env / fs 工具
│   ├── pikpak.py            # PikPakScanner / PikPakManager 封装
│   └── rss.py               # RSS 采集与封面增强
├── main.py                  # FastAPI 后端，提供 /api/* JSON 读接口，并挂载前端
├── pikpak_dl.py             # 轻薄入口：扫描云盘并补全播放直链
├── pikpak_automation.py     # 轻薄入口：批量建目录、添加下载、监控任务
├── rssworker.py             # 轻薄入口：抓取 RSS 并增强封面
├── bangumi.json             # 原始动漫数据（采集自 RSS）
├── bangumi_with_cover.json  # 增强后带封面的动漫数据
├── bangumi_with_play_url.json # 带在线播放直链的动漫数据
├── pikpak_folder_structure.json # PikPak 云盘结构缓存
├── frontend/                # 前端网页
│   ├── index.html
│   ├── detail.html
│   ├── app.js               # 读取 /api/bangumi_with_play_url
│   ├── detail.js            # 读取 /api/bangumi_with_play_url
│   └── style.css
└── pyproject.toml
```

---

## 依赖环境

- Python >= 3.11
- FastAPI, Uvicorn, aiohttp, requests, feedparser, beautifulsoup4, pikpakapi

依赖可通过 `pyproject.toml` 管理，或直接：

```bash
pip install -r requirements.txt
# 或使用 poetry/pipenv 等工具
```

---

## 各模块详细说明

### 1. rssworker.py

- 采集指定 RSS 源，解析剧集标题、磁力链接、发布时间、详情页链接。
- 自动爬取每部番剧的封面图片，增强数据。
- 输出：`bangumi.json`（原始）、`bangumi_with_cover.json`（带封面）。

### 2. pikpak_dl.py

- 递归扫描 PikPak 云盘结构，自动匹配番剧与剧集。
- 为每集补全在线播放直链（play_url 字段），并标记匹配状态。
- 输出：`bangumi_with_play_url.json`。

### 3. pikpak_automation.py

- 自动化管理云盘：
  - 批量创建番剧文件夹
  - 批量添加磁力下载任务
  - 监控下载进度，统计任务状态
- 日志输出到 `pikpak_automation.log`

### 4. main.py

- FastAPI 后端，提供 `/api/bangumi`、`/api/bangumi_with_cover`、`/api/bangumi_with_play_url`，同时挂载 `frontend/` 为静态站点。

### 5. frontend/

- 响应式网页，支持深色/浅色主题切换
- 动漫列表页（index.html）：展示所有番剧，点击进入详情
- 动漫详情页（detail.html）：
  - 展示封面、剧集列表、磁力链接、在线播放按钮
  - 支持一键复制磁力、一键用 IINA/PotPlayer 打开直链
  - 支持 flv.js 播放器在线播放

---

## 数据结构示例

`bangumi_with_play_url.json` 结构如下：

```json
{
  "Bangumi": {
    "琉璃的宝石 / Ruri no Houseki": {
      "cover_info": {
        "cover_url": "https://s2.loli.net/2025/07/07/rBsCP832mfpX1MO.webp"
      },
      "episodes": [
        {
          "filename": "琉璃的宝石 / Ruri no Houseki E05.mp4",
          "bt_url": "magnet:?xt=urn:btih:...",
          "pubDate": "Wed, 06 Aug 2025 14:41:00 GMT",
          "original_title": "[喵萌奶茶屋&LoliHouse] ...",
          "page_link": "https://animes.garden/detail/dmhy/700711",
          "play_url": "https://dl-xxx.mypikpak.com/download/...?sign=...",
          "match_status": "found"
        },
        ...
      ]
    },
    ...
  }
}
```

---

## 前端交互说明

- 首页（index.html）：
  - 从 `/api/bangumi_with_play_url` 加载数据，渲染所有番剧卡片。
  - 支持主题切换，移动端自适应。
- 详情页（detail.html）：
  - 展示番剧封面、剧集列表、磁力链接、在线播放按钮。
  - 支持一键复制磁力、一键用 IINA/PotPlayer 打开直链。
  - 支持 flv.js 播放器在线播放（需浏览器支持）。

---

## 部署与运行

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 采集数据
   ```bash
   python rssworker.py                # 采集 RSS 并增强封面
   python pikpak_dl.py                # 扫描云盘并补全播放直链
   # 可选：python pikpak_automation.py  # 自动建目录+添加下载+监控
   ```
3. 启动后端 API
   ```bash
   uvicorn main:app --reload
   ```
4. 访问前端页面
   - 访问 `http://127.0.0.1:8000/`（静态前端由后端挂载），前端从 `/api/bangumi_with_play_url` 读取数据。

---

## 环境变量配置

为避免把敏感信息写入代码，推荐通过环境变量配置 PikPak 账号与根目录 ID：

- `PIKPAK_USERNAME`: PikPak 用户名
- `PIKPAK_PASSWORD`: PikPak 密码
- `PIKPAK_ROOT_FOLDER_ID`: PikPak 根文件夹 ID（默认 `VOXDJE957ERLA8IV6Wjc4z2So2`）
- `RSS_URL_ANIME_COLLECTION`: RSS 源，默认已配置 animes.garden 示例

macOS/Linux 可临时设置：

```bash
export PIKPAK_USERNAME="your_email"
export PIKPAK_PASSWORD="your_password"
export PIKPAK_ROOT_FOLDER_ID="your_root_folder_id"
```

---

## 常见问题与建议

- PikPak 账号、文件夹 ID、API 密钥等敏感信息请勿上传公开仓库，建议用环境变量或配置文件管理。
- 若遇到云盘 API 频率限制，可适当调整脚本中的延迟参数。
- 若需支持更多 RSS 源或云盘平台，可扩展 `rssworker.py` 和 `pikpak_dl.py`。
- 日志文件为 `pikpak_automation.log`，便于排查自动化下载问题。
- 前端支持移动端自适应，深色/浅色主题切换。

---

## 联系与反馈

如有问题、建议或合作意向，欢迎 issue/PR 或邮件联系作者。
