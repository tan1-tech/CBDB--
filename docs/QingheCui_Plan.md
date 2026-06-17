# 清河崔氏政治网络研究 — 可行性报告与实施方案

**版本：** v1.0
**日期：** 2026-06-10
**数据库：** data/raw/cbdb_20260530.sqlite3（549.6 MB，79 表）

---

## 一、数据库可行性分析

### 1.1 数据可用性

| 指标 | 数值 | 结论 |
|------|------|------|
| CBDB 总人物数 | 658,670 | 足够 |
| 清河崔氏（籍贯清河+崔姓） | 252 人 | 充分 |
| 清河崔氏（郡望代码清河） | 393 人 | 充分 |
| 覆盖朝代 | 16 个 | 西汉→五代 |
| 主要集中朝代 | 唐（215 人） | 数据密集 |
| 内部亲属关系 | 478 条 | 可构建网络 |
| 外部亲属关系 | 622 条 | 可扩展 |
| 社会关系 | 36 条 | 辅助数据 |
| 官职记录 | 249 条 | 可分析 |

### 1.2 关键数据表

| 表名 | 行数 | 用途 |
|------|------|------|
| BIOG_MAIN | 658,670 | 人物基本信息 |
| KIN_DATA | 557,265 | 亲属关系网络 |
| ASSOC_DATA | 188,649 | 社会关系网络 |
| POSTED_TO_OFFICE_DATA | 588,501 | 官职信息 |
| OFFICE_CODES | 34,052 | 官职名称 |
| DYNASTIES | 85 | 朝代信息 |
| ADDR_CODES | 30,099 | 籍贯地址 |
| CHORONYM_CODES | 173 | 郡望/族望代码 |

### 1.3 可行性判断

**结论：完全可行。**

CBDB 中包含充足数量的清河崔氏人物及其亲属关系、社会关系和官职记录，足以支持家族规模统计分析、核心人物识别、联姻网络构建和政治影响力分析。

---

## 二、数据抽取方案

### 2.1 人物识别策略

使用三重验证确保人物归属：

策略 A：籍贯在清河 + 姓崔 → 252 人（基准集）
策略 B：郡望代码 4（清河）+ 姓崔 → 约 400 人（扩展集）
策略 C：文本提及"清河崔氏" → 补充集

主数据集：策略 A + 策略 B 去重合并。

### 2.2 字段映射

| CBDB 字段 | 对应概念 | 备注 |
|-----------|---------|------|
| BIOG_MAIN.c_personid | 人物 ID | 主键 |
| BIOG_MAIN.c_name_chn | 姓名 | 用于显示 |
| BIOG_MAIN.c_female | 性别 | 1=女 |
| BIOG_MAIN.c_birthyear | 出生年 | 可能存在缺失 |
| BIOG_MAIN.c_deathyear | 逝世年 | 可能存在缺失 |
| BIOG_MAIN.c_dy | 朝代代码 | 关联 DYNASTIES |
| DYNASTIES.c_dynasty_chn | 朝代名称 | 显示用 |
| BIOG_MAIN.c_index_addr_id | 籍贯地址 ID | 关联 ADDR_CODES |
| BIOG_MAIN.c_choronym_code | 郡望代码 | 关联 CHORONYM_CODES |
| KIN_DATA.c_personid | 人物 ID | 亲属关系发起方 |
| KIN_DATA.c_kin_id | 亲属 ID | 亲属关系接收方 |
| KIN_DATA.c_kin_code | 亲属关系代码 | 父子/夫妻/兄弟等 |
| KINSHIP_CODES.c_kin_code | 亲属关系代码 | 关系描述 |
| ASSOC_DATA.c_personid | 社交关系发起方 | |
| ASSOC_DATA.c_assoc_id | 社交关系目标 | |
| ASSOC_DATA.c_assoc_code | 社交关系类型 | |
| POSTED_TO_OFFICE_DATA.c_personid | 任职人物 | |
| POSTED_TO_OFFICE_DATA.c_office_id | 官职 ID | |
| POSTED_TO_OFFICE_DATA.c_dy | 任职朝代 | |
| OFFICE_CODES.c_office_chn | 官职名称 | |

---

## 三、网络构建方案

### 3.1 网络类型

| 网络 | 节点 | 边 | 数据来源 |
|------|------|-----|---------|
| 家族关系网络 | 清河崔氏人物 | 亲属关系 | KIN_DATA + KINSHIP_CODES |
| 联姻网络 | 清河崔氏 + 联姻家族 | 婚姻关系 | KIN_DATA（姻亲代码） |
| 社会关系网络 | 清河崔氏 + 关联人物 | 社交关系 | ASSOC_DATA |
| 政治网络 | 清河崔氏 | 共官关系 | POSTED_TO_OFFICE_DATA |

### 3.2 NetworkX 分析指标

| 指标 | 用途 |
|------|------|
| Degree Centrality | 谁是家族网络核心 |
| Betweenness Centrality | 谁是关键桥梁人物 |
| Eigenvector Centrality | 谁与重要人物相连 |
| PageRank | 全局影响力排名 |
| Louvain 社区发现 | 家族内部派系结构 |

### 3.3 亲属关系分类

CBDB 的 KINSHIP_CODES 表中包含各类亲属关系代码。将按以下分类处理：

| 类别 | 包含关系 | 网络用途 |
|------|---------|---------|
| 直系 | 父子、母子 | 核心家族树 |
| 旁系 | 兄弟、叔侄、从兄弟 | 家族扩展 |
| 联姻 | 夫妻、岳婿、姻亲 | 联姻网络 |
| 其他 | 养子、嗣子等 | 补充 |

---

## 四、可视化方案

### 4.1 统计图表

| 图 | 类型 | 工具 |
|----|------|------|
| 家族规模（各朝人数） | 柱状图 | ECharts |
| 朝代分布 | 堆叠柱状图 | ECharts |
| 核心人物排名（中心性） | 横向柱状图 | ECharts |

### 4.2 网络图

| 图 | 布局 | 工具 |
|----|------|------|
| 家族关系网络 | 力导向图 | ECharts Graph |
| 联姻网络 | 力导向图 | ECharts Graph |
| 社区结构 | 按社区着色 | ECharts Graph |

### 4.3 风格

与现有北宋文人知识图谱保持一致：宣纸背景（#F4EBD6）、古籍卡片样式、深红/金色配色、古风字体。

---

## 五、网站集成方案

### 5.1 导航栏更新

在现有导航栏中新增标签：北宋文人知识图谱（已有）、清河崔氏专题（新增）、AI历史问答（预留）。

### 5.2 文件计划

| 文件 | 作用 |
|------|------|
| index.html | 新增导航标签 + 清河崔氏页面区域 |
| assets/style.css | 扩展样式（共用现有宣纸主题） |
| js/cui_graph.js | 清河崔氏网络图谱（ECharts） |
| js/cui_stats.js | 统计图表（ECharts） |
| python/build_cui_data.py | 数据库→JSON 数据构建 |
| data/processed/cui/network_data.json | 生成的网络数据 |

### 5.3 数据流

CBDB → python/build_cui_data.py → JSON 文件 → js/cui_*.js → index.html（清河崔氏模块）

---

## 六、实施计划

| 阶段 | 内容 |
|------|------|
| 1 | 数据抽取脚本 build_cui_data.py |
| 2 | NetworkX 分析 + JSON 输出 |
| 3 | 统计图表 ECharts 渲染 |
| 4 | 网络图谱 ECharts 渲染 |
| 5 | 网站集成 + 导航更新 |

---

## 七、输出文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| python/build_cui_data.py | Python | 清河崔氏数据构建器 |
| data/processed/cui/cui_network.json | JSON | 网络数据（节点+边） |
| data/processed/cui/cui_stats.json | JSON | 统计数据 |
| js/cui_graph.js | JavaScript | 网络图谱渲染 |
| js/cui_stats.js | JavaScript | 统计图表渲染 |
| docs/QingheCui_Plan.md | 文档 | 本方案文档 |

---

*数据库版本：cbdb_20260530*
*分析工具：Python + NetworkX + ECharts*
*网站框架：现有北宋文人知识图谱扩展*
