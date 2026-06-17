# PythonProject2 项目审计报告

**生成日期：** 2026-06-10
**项目范围：** `C:\Users\谭\PycharmProjects\PythonProject2`
**审计目标：** 结构诊断、重复/废弃文件分析、归档/保留建议

---

## 1. 项目概览

本项目是一个**数字人文研究工具集**，核心数据来源是 **CBDB（中国历史人物传记数据库）**。项目涵盖以下五个研究主题：

| 主题 | 核心内容 |
|------|---------|
| 宋代文人关系网络 | 六大核心人物（欧阳修、司马光、苏轼、苏辙、王安石、曾巩）的关系图谱抽取与可视化 |
| 李清照迁移路线 | 基于 CBDB 地点坐标生成李清照南渡路线时间轴地图 |
| 南宋人口迁移 | 南宋人物籍贯与最终活动地的空间分布对比（KDE / Hexbin 图） |
| 五朝人才分布 | 唐、宋、元、明、清人才籍贯散点 / Hexbin / KDE 热力图 |
| 唐宋元明清官职统计 | 官职记录数量、Top5 官职、官职结构变化热图 |

---

## 2. 项目结构诊断

### 当前结构

```
PythonProject2/
├── data/               # 原始数据文件（CSV / SQLite / JSON / XLSX）
│   ├── cbdb.sqlite              0B  占位符
│   ├── cbdb.sqlite3             0B  占位符
│   ├── cbdb_partB_people.csv   33MB  Part B 人物数据
│   ├── China.json             569KB  中国省级行政区划 GeoJSON
│   ├── family_size_*.csv       ~8MB  家族规模数据（clean + full）
│   ├── office_dynasty.csv    375KB  官职数据
│   ├── 官职统计.xlsx          295KB
│   ├── 人才籍贯数据.xlsx        25MB
│   └── 唐宋元明清官职交叉表.xlsx 268KB
├── output/
│   ├── family/         家族规模分析图表（5张 PNG）
│   ├── office/         官职统计图表（7张 PNG）
│   └── talent/         人才分布图表（6张 PNG, 1张 HTML）
├── src/
│   ├── *.py            34个 Python 脚本（下详）
│   ├── *.xlsx          20个 Excel 生成文件
│   ├── *.png           8张 嵌入图片
│   ├── *.html          2个 网络可视化页面
│   ├── *.csv           1个 CSV 数据文件
│   ├── *.db / *.sqlite 2个 占位数据库（0B）
│   ├── lib/            前端静态资源（vis-network, tom-select, bindings）
│   └── lib/vis-9.1.2   vis-network 9.1.2 本地完整库
├── test/
│   ├── *.py            6个 测试/探索脚本
│   └── *.xlsx         10个 测试生成文件
└── source/             空目录
```

### 结构性诊断

**问题 1 — `src/` 目录职责混叠**

`src/` 同时包含了源代码（.py）、生成的中间数据文件（.xlsx / .csv）、生成的成品（.html / .png）和静态库文件（.js / .css / vis-9.1.2）。这导致 `src/` 中有 **34 个 .py 文件 + 20 个 .xlsx 文件 + 2 个 .html + 多个 .png / .csv**，可读性极差。

**问题 2 — 生成物与输入数据层次不分**

许多 Python 脚本将生成的 .xlsx 或 .png 直接输出到运行目录（即 `src/` 自身），而不是 `output/` 或 `data/`。例如：
- `edgetable.py` → `Song_Network_Final_Nodes_v2.xlsx`（写到 `src/` 而非 `output/`）
- `talent_KDE.py` → `宋_KDE.png`（写到 `src/` 而非 `output/talent/`）

**问题 3 — 空文件/占位文件散落**

- `data/cbdb.sqlite`（0B）
- `data/cbdb.sqlite3`（0B）
- `src/cbdb.sqlite`（0B）
- `src/CBDB.db`（0B）
- `src/朝代分布.py`（0B，完全空文件）

**问题 4 — `test/` 与 `src/` 代码交叉依赖**

`test/` 中的脚本（如 `test.py`, `testli.py`）直接引用 `src/` 下的 Excel 文件路径，不是真正的单元测试，而是探索性查询。`test/` 也不包含任何测试框架（如 pytest）。

**问题 5 — 容器化 / 发布缺失**

项目无 `requirements.txt`, `pyproject.toml`, `Dockerfile`, `.gitignore`, 或 `README.md`。

---

## 3. 重复文件分析

### 3.1 宋代文人网络 — 数据抽取管线（严重重复）

存在 **6 条独立但功能高度重叠的数据抽取管线**，均从 CBDB 读取关系并合并为边表/节点表。差异仅在于：关系分类逻辑、输出列定义、是否计算中心性/社群。

| 管线文件 | 输出后缀 | 核心人物 | 关系分类方式 | 额外功能 |
|----------|---------|---------|------------|---------|
| `extension.py` | 无（v1） | 5 人（缺司马光） | 按类型代码 LIKE '05%' | 仅统计书信 |
| `edgetable.py` | `_v2` | 6 人 | 显式 code 映射 | 无向聚合、主关系判定 |
| `song_network_detail.py` | `_Detail.csv` | 6 人 | 无分类，只统计描述 | 仅输出 CSV 明细 |
| `song_network_builder.py` | `_Final` | 6 人 | 从 ASSOC_CODE_TYPE_REL 合并 | 第一圈得分计算 |
| `song_network_masterbulider.py` | `_v4` | 6 人 | 自定义 classify() 函数 | 中心性 + 社群发现 |
| `song_masterbuilder.py` | `_Pro` | 6 人 | classify_relation() 文本匹配 | 关系分类更精细 |

**结论：应保留最新/最完整的 1-2 条管线，其余归档。**

### 3.2 宋代文人网络 — HTML 可视化（中度重复）

| 文件 | 引擎 | 数据来源 | 交互性 |
|------|------|---------|-------|
| `southernsong liberti.py` → `Song_Literati_Network.html` | pyvis | 直接读 DB | 基础交互 |
| `Song_Network_Visualizer.py` → `Song_Literary_Network.html` | pyvis | 读 v2 xlsx | 图例 + 高级交互 |

两版 HTML 视觉风格接近。`Song_Literary_Network.html` 更成熟（有图例 + 导航按钮）。

### 3.3 宋代文人网络 — Dash 仪表盘（中度重复）

| 文件 | 可视化库 | 数据来源 | 交互功能 |
|------|---------|---------|---------|
| `song_dash_board.py` | Plotly | v2 xlsx | 点击节点查看详情 |
| `song_dashboard_v2.py` | Cytoscape | v2 xlsx | 筛选 + 滑块 |
| `SongScholarDashboard_Pro.py` | Cytoscape | v2 xlsx | 筛选 + 搜索 + 详情面板 |

`SongScholarDashboard_Pro.py` 功能最完备。

### 3.4 李清照迁移路线（中度重复）

| 文件 | 输出 | 风格差异 |
|------|------|---------|
| `Qingzhao Li.py` | `Li_Qingzhao_Migration_Map.png` | SimHei 字体，简中名 |
| `qingzhao route.py` | `LiQingzhao_Migration_Timeline.png` | 微软雅黑，FancyArrowPatch |
| `LiQingzhao_Timeline_Map.py` | `LiQingzhao_Final_Timeline_Map.png` | 微软雅黑，颜色编码阶段 |

`LiQingzhao_Timeline_Map.py` 是最终成品（标注靖康之变、三色图例）。

### 3.5 南宋空间分析（轻度重复）

| 文件 | 数据来源 | 可视化内容 |
|------|---------|-----------|
| `southernsong hexbin.py` | SouthernSong_Hometown.xlsx | 籍贯 Hexbin |
| `southernsong action.py` | 直接读 DB | 活动地点 Hexbin |
| `SouthernSong_MigrationFlow.py` | 直接读 DB | 籍贯 KDE vs 最终活动 KDE 对比 |

这三份脚本分析的是不同角度，可视为独立的。

### 3.6 人才分布可视化（中度重复）

| 文件 | 可视化类型 | 输出到 |
|------|-----------|-------|
| `talent_distribution_images.py` | 散点图 | `output/talent/` |
| `talent_hexbin.py` | Hexbin | 当前目录（`src/`） |
| `talent_KDE.py` | KDE 热力图 | 当前目录（`src/`） |

三者是渐进迭代（散点 → Hexbin → KDE），KDE 最精细。但散点图和 Hexbin 的输出既有在 `output/talent/` 中的也有在 `src/` 中的，路径混乱。

### 3.7 Excel 中间文件重复

以下文件实质上是同一数据在不同迭代中的不同版本：

| 迭代 | 节点文件 | 边文件 | 第一圈文件 |
|------|---------|-------|-----------|
| v1（extension） | — | — | `SongNetwork_FirstRing.xlsx` |
| v2（edgetable） | `Song_Network_Final_Nodes_v2.xlsx` | `Song_Network_Final_Edges_v2.xlsx` | `SongNetwork_FirstRing_v2.xlsx` |
| Final（song_network_builder） | `Song_Network_Nodes_Final.xlsx` | `Song_Network_Edges_Final.xlsx` | `SongNetwork_FirstRing_Final.xlsx` |
| v4（masterbulider） | `Song_Network_Nodes_v4.xlsx` | `Song_Network_Edges_v4.xlsx` | — |
| Pro（masterbuilder） | `Song_Network_Nodes_Pro.xlsx` | `Song_Network_Edges_Pro.xlsx` | — |

此外还有衍生文件如 `Song_Network_Final_Edges.xlsx`, `Song_Network_Final_Nodes.xlsx`, `Song_Network_Final_Edges_v2.xlsx`, `SongNetwork_FirstRing_v3.xlsx` 等。

---

## 4. 可能废弃文件分析

### 4.1 确定废弃（0B 空文件 / 完全无用）

| 文件 | 原因 |
|------|------|
| `data/cbdb.sqlite` | 0B 占位符 |
| `data/cbdb.sqlite3` | 0B 占位符 |
| `src/cbdb.sqlite` | 0B 占位符（同一数据集的副本） |
| `src/CBDB.db` | 0B 占位符 |
| `src/朝代分布.py` | 空文件（0B，无任何代码） |

### 4.2 废弃可能性高（被后续版本取代的早期文件）

| 文件 | 被取代者 |
|------|---------|
| `src/extension.py` | 产出 `SongNetwork_FirstRing.xlsx`（v1），已被 v2/Pro 取代 |
| `src/song_network_detail.py` | 产出 `Song_Network_Detail.csv`，功能被 `edgetable.py` 覆盖 |
| `src/song_network_builder.py` | 管线被 `song_network_masterbulider.py`（v4）取代 |
| `src/SongNetwork_FirstRing.xlsx` | v1 输出，被 `_v2.xlsx` / `_Pro.xlsx` 取代 |
| `src/Song_Network_Edges_Final.xlsx` | 与 `Song_Network_Edges_v4.xlsx` 功能重复 |
| `src/Song_Network_Nodes_Final.xlsx` | 与 `Song_Network_Nodes_v4.xlsx` 功能重复 |
| `src/SongNetwork_FirstRing_Final.xlsx` | 被 `_v2` 版取代 |
| `src/Song_Literati_Relationships.xlsx` | 中间产物，被后续边表覆盖 |
| `src/Song_Literati_Network.html` | 被 `Song_Literary_Network.html` 取代（功能更全） |
| `src/SongScholarNetwork.xlsx` | 早期版本，被后续节点表覆盖 |
| `src/SongLiteraryNetwork.xlsx` | 早期版本 |
| `src/song_dash_board.py` | 功能不完整的 Dash 版本，被 `SongScholarDashboard_Pro.py` 取代 |
| `src/song_dashboard_v2.py` | 功能不完整的 Dash 版本，被 `SongScholarDashboard_Pro.py` 取代 |
| `src/Qingzhao Li.py` | 早期李清照路线图，被 `LiQingzhao_Timeline_Map.py` 取代 |
| `src/qingzhao route.py` | 中间迭代版本 |
| `src/SouthernSong_Migration_Matrix.xlsx` | 早期数据探索产物 |
| `src/SouthernSong_TopPlaces.xlsx` | 早期数据探索产物 |

### 4.3 废弃可能性中（功能重复但可能仍有参考价值）

| 文件 | 原因 |
|------|------|
| `src/talent_distribution_images.py` | 散点图版本，被 Hexbin / KDE 取代但方法不同 |
| `src/talent_hexbin.py` | 中间迭代，被 KDE 取代 |
| `test/test.py` | 快速验证 xlsx 读取 |
| `test/testli.py` | 李清照地点探索查询 |
| `test/nansongrenwu.py` | 地址类型统计探索 |
| `test/testtable.py` | ASSOC 表结构探索 |
| `test/ASSOC_*.xlsx` | 表结构转储，探索用 |
| `test/BIOG_ADDR_TYPE_Statistics.xlsx` | 探索产物 |
| `test/LiQingzhao_Places_Check.xlsx` | 探索产物 |
| `test/testdata.py` | 查找大文件工具 |
| `test/testmap.py` | 地图加载测试 |
| `test/testmap1.py` | 地图结构探索 |

### 4.4 即兴/一次性脚本

| 文件 | 内容 |
|------|------|
| `src/test.py` | 打印 3 个 xlsx 表头 |
| `src/testfile.py` | 打印 Song_Literati_Relationships.xlsx 行数 |
| `src/partB_analysis.py` | 混合了数据导出 + 绘图代码（顶部与底部 import 重复） |

---

## 5. 推荐目录结构

```
PythonProject2/
├── data/                  # 只读原始数据
│   ├── raw/               # 从外部导入的原始数据
│   │   ├── China.json
│   │   ├── cbdb_partB_people.csv
│   │   └── family_size_*.csv
│   └── processed/         # 脚本生成的中间数据（.xlsx / .csv）
│       ├── talent/
│       ├── office/
│       ├── song_network/
│       └── southern_song/
├── src/                   # 仅 Python 源代码
│   ├── __init__.py
│   ├── config.py          # 共享路径常量、颜色方案
│   ├── db_utils.py        # CBDB 连接、简体转换等共享工具
│   ├── talent/            # 人才分布分析
│   ├── office/            # 官职分析
│   ├── song_network/      # 宋文人网络（抽取 + 可视化 + Dash）
│   ├── liqingzhao/        # 李清照路线
│   ├── southern_song/     # 南宋迁移
│   └── family/            # 家族规模分析
├── output/                # 成品输出（图片 / HTML / 最终报告）
│   ├── family/
│   ├── office/
│   ├── talent/
│   ├── song_network/
│   ├── southern_song/
│   └── liqingzhao/
├── static/                # 前端静态资源（迁移自 src/lib/）
│   └── lib/
│       ├── bindings/
│       ├── tom-select/
│       └── vis-9.1.2/
├── tests/                 # 真正的单元/集成测试
├── notebooks/             # Jupyter 探索笔记（可选）
├── archive/               # 迭代旧版，保留不删
│   └── song_network/
│       ├── v1_extension/
│       ├── v2_edgetable/
│       └── v3_network_builder/
├── requirements.txt       # 项目依赖
├── README.md              # 项目文档
├── .gitignore
└── PROJECT_AUDIT.md       # 本文件
```

### 迁移原则

1. **`src/` 只保留 `.py`**。所有 `.xlsx` / `.csv` / `.html` / `.png` 移入 `output/` 或 `data/processed/`。
2. **数据管线收敛**：仅保留 1-2 条宋代网络数据管线，其余移入 `archive/`。
3. **Dash 应用收敛**：仅保留 `SongScholarDashboard_Pro.py`，其余两个 Dash 版移入 `archive/`。
4. **`static/lib/`** 从 `src/lib/` 移出，保持 `src/` 仅为代码。
5. **删除或移走所有 0B 占位数据库文件**。
6. **测试脚本**：区分真正的测试（使用 pytest）和探索性脚本（移入 `notebooks/` 或 `archive/`）。

---

## 6. 保留建议

### 强烈保留（项目核心）

| 文件 | 理由 |
|------|------|
| `data/China.json` | 唯一中国地图底图 |
| `data/cbdb_partB_people.csv` | 33MB 人物核心数据集 |
| `data/family_size_clean.csv` | 家族规模清洗数据 |
| `data/family_size_full.csv` | 家族规模原始数据 |
| `data/office_dynasty.csv` | 官职原始数据 |
| `data/人才籍贯数据.xlsx` | 五朝人才坐标数据 |
| `src/edgetable.py` | 宋代网络核心抽取管线（v2） |
| `src/song_network_masterbulider.py` | 最完善的网络构建（含中心性+社群） |
| `src/song_masterbuilder.py` | Pro 版网络构建（精细分类） |
| `src/SongScholarDashboard_Pro.py` | 最完善的 Dash 可视化 |
| `src/Song_Network_Visualizer.py` | HTML 网络可视化生成器 |
| `src/LiQingzhao_Timeline_Map.py` | 李清照迁移最终版 |
| `src/southernsong action.py` | 南宋活动 Hexbin |
| `src/SouthernSong_MigrationFlow.py` | 南宋 KDE 对比 |
| `src/talent_KDE.py` | 五朝 KDE 热力图（最精细） |
| `src/office_dynasty.py` | 官职分析全套 |
| `src/partB_analysis.py` | Part B 家族+性别分析 |
| `src/字段统计.py` | 数据库字段统计工具 |
| `src/lib/` | 前端静态库（HTML 可视化需要） |
| `output/` 下所有文件 | 已生成的成品 |

### 可移入 `archive/`（保留不删）

| 移入 `archive/` | 理由 |
|-----------------|------|
| `src/extension.py` | v1 管线，被取代 |
| `src/song_network_detail.py` | 功能太基础，被覆盖 |
| `src/song_network_builder.py` | 被 v4/Pro 取代 |
| `src/song_dash_board.py` | 早期 Dash，被 Pro 取代 |
| `src/song_dashboard_v2.py` | 中间 Dash，被 Pro 取代 |
| `src/Qingzhao Li.py` | 早期版，被最终版取代 |
| `src/qingzhao route.py` | 中间版，被最终版取代 |
| `src/talent_distribution_images.py` | 散点图版，被 KDE 取代 |
| `src/talent_hexbin.py` | 中间版，被 KDE 取代 |
| `src/SouthernSong_Hometown.py` | 中间数据抽取 |
| `src/southernsong hexbin.py` | 中间版 |
| `src/southernsong liberti.py` | 被 Song_Network_Visualizer.py 取代 |
| `src/test.py` | 一次性验证 |
| `src/testfile.py` | 一次性验证 |
| `test/` 下所有文件 | 都是探索性脚本，非正式测试 |
| 所有 v1 / Final / 早期 xlsx 迭代文件 | 被 v2 / v4 / Pro 版覆盖 |

### 建议删除（直接移除）

| 文件 | 理由 |
|------|------|
| `data/cbdb.sqlite` | 0B 空占位符 |
| `data/cbdb.sqlite3` | 0B 空占位符 |
| `src/cbdb.sqlite` | 0B 空占位符 |
| `src/CBDB.db` | 0B 空占位符 |
| `src/朝代分布.py` | 空文件 |

---

## 7. 文件归类一览表

### `src/` 中的 Python 脚本功能分组

| 组 | 脚本 | 状态 |
|----|------|------|
| **宋代网络 - 抽取** | `edgetable.py`, `song_network_masterbulider.py`, `song_masterbuilder.py` | 保留 |
| **宋代网络 - 抽取（旧版）** | `extension.py`, `song_network_detail.py`, `song_network_builder.py` | 归档 |
| **宋代网络 - 可视化** | `Song_Network_Visualizer.py`, `SongScholarDashboard_Pro.py` | 保留 |
| **宋代网络 - 可视化（旧版）** | `song_dash_board.py`, `song_dashboard_v2.py`, `southernsong liberti.py` | 归档 |
| **李清照** | `LiQingzhao_Timeline_Map.py` | 保留 |
| **李清照（旧版）** | `Qingzhao Li.py`, `qingzhao route.py` | 归档 |
| **南宋迁移** | `SouthernSong_MigrationFlow.py`, `southernsong action.py` | 保留 |
| **南宋（旧版/中间）** | `SouthernSong_Hometown.py`, `southernsong hexbin.py` | 归档 |
| **人才分布** | `talent_KDE.py` | 保留 |
| **人才分布（旧版）** | `talent_distribution.py`, `talent_distribution_images.py`, `talent_hexbin.py` | 归档 |
| **官职分析** | `office_dynasty.py` | 保留 |
| **Part B 分析** | `partB_analysis.py` | 保留 |
| **数据库工具** | `字段统计.py` | 保留 |
| **一次性脚本** | `test.py`, `testfile.py` | 归档 |
| **空文件** | `朝代分布.py` | 删除 |

### `src/` 中的生成文件（应移入 `output/` 或 `data/processed/`）

| 移动至 `data/processed/song_network/` | 移动至 `output/song_network/` |
|--------------------------------------|-------------------------------|
| `Song_Network_Final_Nodes_v2.xlsx` | `Song_Literary_Network.html` |
| `Song_Network_Final_Edges_v2.xlsx` | `Song_Literati_Network.html` |
| `Song_Network_Nodes_v4.xlsx` | |
| `Song_Network_Edges_v4.xlsx` | |
| `Song_Network_Nodes_Pro.xlsx` | |
| `Song_Network_Edges_Pro.xlsx` | |
| `Song_Network_Centrality.xlsx` | |
| `Song_Network_Communities.xlsx` | |
| `Song_Network_Detail.csv` | |
| `Song_Network_Edges_Final.xlsx` | |
| `Song_Network_Nodes_Final.xlsx` | |
| `Song_Network_Final_Edges.xlsx` | |
| `Song_Network_Final_Nodes.xlsx` | |
| `Song_Network_Final_Edges_v2.xlsx` | |

| 移动至 `data/processed/southern_song/` | 移动至 `output/southern_song/` |
|----------------------------------------|-------------------------------|
| `SouthernSong_Hometown.xlsx` | `SouthernSong_Hometown_Hexbin.png` |
| `SouthernSong_Activity.xlsx` | `SouthernSong_Activity_Hexbin.png` |
| `SouthernSong_Migration_Matrix.xlsx` | `SouthernSong_Migration_Comparison.png` |
| `SouthernSong_TopPlaces.xlsx` | |

| 移动至 `data/processed/liqingzhao/` | 移动至 `output/liqingzhao/` |
|-------------------------------------|----------------------------|
| `liqingzhao_coordinates.xlsx` | `LiQingzhao_Final_Timeline_Map.png` |

| 移动至 `output/talent/` | 备注 |
|-------------------------|------|
| `宋_KDE.png`, `唐_KDE.png`, `元_KDE.png`, `明_KDE.png`, `清_KDE.png` | 从 `src/` 移入 |

---

## 8. 总结

### 优势

- 项目主题聚焦，围绕 CBDB 数据库展开五个明确的数字人文分析方向
- 最终产出的可视化成果（地图、网络图、热力图）质量较高
- Dash 仪表盘交互功能完整

### 主要问题

| 问题 | 严重程度 | 影响 |
|------|---------|------|
| `src/` 混合代码 + 数据 + 生成物 | 高 | 目录膨胀到近 70 个文件 |
| 宋代网络管线重复（6 条管线） | 高 | 维护成本高，不清楚哪个是"当前版本" |
| Excel 中间文件版本爆炸（20+ 文件） | 高 | 不清楚哪个是最新输出 |
| Dash 可视化重复（3 个版本） | 中 | 应收敛到 `SongScholarDashboard_Pro.py` |
| 0B 占位文件（4 个 + 1 个空 .py） | 低 | 无实际影响但造成噪音 |
| `test/` 与 `src/` 边界模糊 | 中 | 没有真正的测试 |
| 缺少 `requirements.txt` / `README.md` | 中 | 不可复现，不可分享 |
| 缺少 `.gitignore` | 中 | 生成文件可能被误提交 |

### 推荐优先级

1. **立即**：删除 5 个 0B 空文件
2. **短期**：收敛宋代网络管线至 `song_network_masterbulider.py` + `song_masterbuilder.py`，其余归档
3. **短期**：收敛 Dash 可视化至 `SongScholarDashboard_Pro.py`
4. **中期**：将 `src/` 生成物移入 `data/processed/` 和 `output/`
5. **中期**：添加 `requirements.txt` / `.gitignore` / `README.md`
6. **长期**：考虑将分析管线转化为可配置的 CLI 工具或 Jupyter notebooks

---

*本报告仅做诊断分析，未修改或删除任何文件。*
