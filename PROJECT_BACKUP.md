# 北宋文人知识图谱 — 项目备份

**备份版本：** song_literati_stable_v1
**备份时间：** 2026-06-10
**备份路径：** `archive/song_literati_stable_v1/`

---

## 当前版本功能

该备份记录了首次完成 **ECharts Graph 完整重构** 后的项目状态。

### 已完成模块

| 模块 | 状态 | 说明 |
|------|------|------|
| 首页淡墨山水 | ✅ 完成 | CSS 绘制的墨色山峦 + 水面 + 雾气 |
| 首页六枚印章 | ✅ 完成 | 欧阳修、司马光、苏轼、王安石、曾巩、苏辙 |
| 进入图谱按钮 | ✅ 完成 | 带过渡动画 |
| 三栏图谱布局 | ✅ 完成 | 左侧面板 + 中间图谱 + 右侧详情 |
| 篆刻印章节点 | ✅ 完成 | 动态 SVG 生成的红色纵向排列篆书印章 |
| ECharts 图谱 | ✅ 完成 | 主题配色、分类图例 |
| 核心人物固定坐标 | ✅ 完成 | 六人固定位置，500ms 自动校正 |
| 关系筛选复选框 | ✅ 完成 | 全部 / 朋友 / 师生 / 政治盟友 / 政敌 / 文人交往 / 兄弟 |
| 人物搜索 | ✅ 完成 | 模糊搜索 + 邻居高亮 + 自动打开档案 |
| 人物档案卡片 | ✅ 完成 | 姓名、字号、生卒、籍贯、代表作、简介、连接数 |
| 关系画像卡片 | ✅ 完成 | 关系类型、强度、子关系条形图 |
| 苏轼-苏辙 → 兄弟 | ✅ 完成 | 前端关系类型覆盖 |
| 星系力导向布局 | ✅ 完成 | repulsion 1000, gravity 0.03, edgeLength 200-400 |
| 宣纸纹理背景 | ✅ 完成 | #F4EBD6 + 古籍网格 + 淡墨晕染 |
| 导航栏 5 模块预留 | ✅ 完成 | 图谱（当前）+ 迁移/籍贯/官职/CBDB（占位） |

### 项目结构

```
archive/song_literati_stable_v1/
├── index.html                  # 主页面（首页 + 图谱 + 导航 + 搜索 + 筛选）
├── assets/
│   └── style.css               # 宣纸主题全套样式（15 KB）
├── js/
│   ├── data_loader.js          # JSON 数据加载器
│   └── network.js              # ECharts 图谱引擎（完全重构版，541 行）
├── python/
│   └── build_json.py           # XLSX → JSON 数据构建器
├── network_data.json           # 生成的图谱数据
├── requirements.txt            # Python 依赖
├── README.md                   # 项目文档
└── docs/
    └── PROJECT_AUDIT.md        # 项目审计报告
```

### network.js 函数清单

| 函数 | 行数 | 作用 |
|------|------|------|
| `createSealSVG()` | 25 | 生成篆刻印章 SVG data URI |
| `getRelation()` | 5 | 关系类型覆盖（苏轼-苏辙 → 兄弟） |
| `init()` | 10 | 初始化 ECharts + 启动核心维护 |
| `render()` | 110 | 核心渲染管线 |
| `setupEvents()` | 12 | 绑定 click 事件 |
| `onNodeClick()` | 5 | 点击节点回调 |
| `onEdgeClick()` | 5 | 点击边回调 |
| `renderPersonArchive()` | 40 | 渲染人物档案卡片 |
| `renderRelationDetail()` | 55 | 渲染关系画像卡片 |
| `setFilter()` | 12 | 关系筛选（勾选=显示） |
| `searchNode()` | 20 | 搜索入口（防抖） |
| `doSearch()` | 55 | 搜索执行（模糊匹配 + 高亮） |
| `clearSearchInternal()` | 18 | 清除搜索结果 |
| `startCoreMaintenance()` | 28 | 500ms 定时器校正核心坐标 |
| `stopCoreMaintenance()` | 7 | 停止定时器 |
| `resize()` | 4 | 窗口自适应 |

### 关键参数

| 参数 | 值 |
|------|-----|
| force.repulsion | 1000 |
| force.edgeLength | [200, 400] |
| force.gravity | 0.03 |
| coreTimer 间隔 | 500ms |
| 核心坐标容差 | 2px |
| 搜索防抖延迟 | 200ms |
| 核心节点尺寸 | 90px |
| 一级节点尺寸 | 28px |
| 二级节点尺寸 | 16px |

---

## 如何恢复备份

```bash
# 完全覆盖当前项目（谨慎操作）
cp -r archive/song_literati_stable_v1/* ./

# 或手动恢复特定文件
cp archive/song_literati_stable_v1/index.html ./
cp archive/song_literati_stable_v1/js/network.js js/
cp archive/song_literati_stable_v1/assets/style.css assets/
```

---

## 如何继续开发

```bash
# 1. 生成最新数据
cd C:\Users\谭\PycharmProjects\PythonProject2
pip install -r requirements.txt
python python/build_json.py

# 2. 启动调试
# 在浏览器中直接打开 index.html
start index.html

# 3. 修改后备份新版本
mkdir archive/song_literati_stable_v2
cp index.html archive/song_literati_stable_v2/
cp js/network.js archive/song_literati_stable_v2/
# ...
```

### 数据流

```
CBDB 数据库 (D:\cbdb_20260530.sqlite3)
  ↓  (由 edgetable.py / song_network_builder.py 等管线处理)
data/processed/song_network/*.xlsx
  ↓  (由 python/build_json.py 处理)
network_data.json
  ↓  (由 index.html → data_loader.js 加载)
ECharts 图谱 (network.js)
```

### 可扩展方向

1. **人物迁移地图** — 基于 CBDB 地址数据的地图可视化（ECharts Map 或 Leaflet）
2. **籍贯分布分析** — KDE / Hexbin 热力图
3. **官职体系分析** — 官职统计 + 结构变化 Sankey 图
4. **CBDB 数据库探索** — 在线查询界面
5. **人物详情页** — 从档案卡片升级为独立页面
6. **关系时间轴** — 基于书信/交往年份的时间线

---

*备份文件不包含 `.venv/`、`data/`、`output/`、`archive/`、`src/`、`static/` 等较大目录。*
*生成 `network_data.json` 需要先运行 `python python/build_json.py`。*
