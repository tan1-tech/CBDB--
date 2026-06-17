"""
build_json.py — 北宋文人知识图谱数据构建器

从 Song_Network Excel 文件读取节点和边数据，
生成 network_data.json 供前端 ECharts 使用。

用法：
    python build_json.py
"""

import json
import os
import sys

try:
    import pandas as pd
except ImportError:
    print("错误：请先安装 pandas 和 openpyxl")
    print("pip install pandas openpyxl")
    sys.exit(1)

# ==========================================
# 路径
# ==========================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

NODES_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Nodes_v2.xlsx")
EDGES_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Edges_v2.xlsx")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "network_data.json")

# ==========================================
# 核心人物档案
# ==========================================

CORE_NAMES = ["欧阳修", "司马光", "苏辙", "王安石", "苏轼", "曾巩"]

CORE_BIO = {
    "欧阳修": {
        "zi": "永叔", "hao": "醉翁，六一居士",
        "birth": "1007", "death": "1072",
        "hometown": "吉州庐陵",
        "works": "《醉翁亭记》《秋声赋》《新五代史》",
        "desc": "北宋文坛领袖，唐宋八大家之一。领导北宋诗文革新运动，开一代文风。"
    },
    "司马光": {
        "zi": "君实", "hao": "迂叟",
        "birth": "1019", "death": "1086",
        "hometown": "陕州夏县",
        "works": "《资治通鉴》《训俭示康》",
        "desc": "北宋史学家、政治家。主持编纂中国第一部编年体通史《资治通鉴》。"
    },
    "王安石": {
        "zi": "介甫", "hao": "半山",
        "birth": "1021", "death": "1086",
        "hometown": "抚州临川",
        "works": "《游褒禅山记》《伤仲永》《桂枝香》",
        "desc": "北宋改革家、文学家。推行熙宁变法，诗文雄健峭拔。"
    },
    "苏轼": {
        "zi": "子瞻", "hao": "东坡居士",
        "birth": "1037", "death": "1101",
        "hometown": "眉州眉山",
        "works": "《念奴娇·赤壁怀古》《赤壁赋》《水调歌头》",
        "desc": "北宋最伟大的文学家之一，诗词文赋书画无一不精。豁达旷放，千古风流。"
    },
    "苏辙": {
        "zi": "子由", "hao": "颍滨遗老",
        "birth": "1039", "death": "1112",
        "hometown": "眉州眉山",
        "works": "《黄州快哉亭记》《上枢密韩太尉书》",
        "desc": "苏轼之弟，唐宋八大家之一。散文汪洋澹泊，与兄齐名。"
    },
    "曾巩": {
        "zi": "子固", "hao": "南丰先生",
        "birth": "1019", "death": "1083",
        "hometown": "建昌南丰",
        "works": "《墨池记》《越州赵公救灾记》",
        "desc": "唐宋八大家之一，文章醇厚雅正，为欧阳修最为器重的弟子。"
    }
}

# ==========================================
# 读取数据
# ==========================================

print("正在读取节点数据...")
nodes_df = pd.read_excel(NODES_FILE)
print(f"  节点数: {len(nodes_df)}")

print("正在读取边数据...")
edges_df = pd.read_excel(EDGES_FILE)
print(f"  边数: {len(edges_df)}")

# ==========================================
# 节点处理
# ==========================================

# 计算连接度
degree_dict = {}
for _, row in edges_df.iterrows():
    degree_dict[row["source"]] = degree_dict.get(row["source"], 0) + 1
    degree_dict[row["target"]] = degree_dict.get(row["target"], 0) + 1

# 计算第二圈（与核心人物直接相连的）
core_set = set(CORE_NAMES)
ring1_set = set()

for _, row in edges_df.iterrows():
    if row["source"] in core_set:
        ring1_set.add(row["target"])
    if row["target"] in core_set:
        ring1_set.add(row["source"])
ring1_set -= core_set

# 构建节点列表
nodes = []
for _, row in nodes_df.iterrows():
    name = row["name"]
    if name in core_set:
        level = 1
        node_type = "core"
    elif name in ring1_set:
        level = 2
        node_type = "ring1"
    else:
        level = 3
        node_type = "ring2"

    node = {
        "id": name,
        "name": name,
        "node_type": node_type,
        "level": level,
        "degree": degree_dict.get(name, 0),
        "is_core": 1 if name in core_set else 0
    }

    # 核心人物额外信息
    if name in CORE_BIO:
        node["bio"] = CORE_BIO[name]

    nodes.append(node)

print(f"\n节点分类:")
print(f"  核心人物 (L1): {sum(1 for n in nodes if n['level']==1)}")
print(f"  直接关联 (L2): {sum(1 for n in nodes if n['level']==2)}")
print(f"  外围人物 (L3): {sum(1 for n in nodes if n['level']==3)}")

# ==========================================
# 边处理
# ==========================================

links = []
for _, row in edges_df.iterrows():
    link = {
        "source": row["source"],
        "target": row["target"],
        "relation": row["dominant_relation"],
        "total_weight": int(row["total_weight"]),
        "friend": int(row.get("friend", 0)),
        "letters": int(row.get("letters", 0)),
        "literature": int(row.get("literature", 0)),
        "teacher": int(row.get("teacher", 0)),
        "support": int(row.get("support", 0)),
        "opposition": int(row.get("opposition", 0)),
        "tooltip": str(row.get("tooltip", ""))
    }
    links.append(link)

print(f"\n关系类型分布:")
rel_counts = {}
for l in links:
    rel_counts[l["relation"]] = rel_counts.get(l["relation"], 0) + 1
for rel, cnt in sorted(rel_counts.items(), key=lambda x: -x[1]):
    print(f"  {rel}: {cnt}")

# ==========================================
# 输出
# ==========================================

output = {
    "nodes": nodes,
    "links": links,
    "meta": {
        "total_nodes": len(nodes),
        "total_links": len(links),
        "core_count": sum(1 for n in nodes if n["level"] == 1),
        "ring1_count": sum(1 for n in nodes if n["level"] == 2),
        "ring2_count": sum(1 for n in nodes if n["level"] == 3),
        "relation_distribution": {k: v for k, v in sorted(rel_counts.items())}
    }
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✓ 已生成: {OUTPUT_FILE}")
print(f"  总节点: {len(nodes)}, 总关系: {len(links)}")
