import sqlite3
import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

# =====================================================
# 数据库
# =====================================================

DB_PATH = r"D:\cbdb_20260530.sqlite3"

conn = sqlite3.connect(DB_PATH)

# =====================================================
# 核心人物
# =====================================================

CORE = [
    "欧阳修",
    "司马光",
    "王安石",
    "苏轼",
    "苏辙",
    "曾巩"
]

NAME_MAP = {
    "歐陽修": "欧阳修",
    "司馬光": "司马光",
    "王安石": "王安石",
    "蘇軾": "苏轼",
    "蘇轍": "苏辙",
    "曾鞏": "曾巩"
}

# =====================================================
# 人物
# =====================================================

people = pd.read_sql("""
SELECT
    c_personid,
    c_name_chn
FROM BIOG_MAIN
""", conn)

people["name"] = (
    people["c_name_chn"]
    .replace(NAME_MAP)
)

# =====================================================
# 关系数据
# =====================================================

assoc = pd.read_sql("""
SELECT
    c_personid,
    c_assoc_id,
    c_assoc_code
FROM ASSOC_DATA
WHERE c_assoc_id IS NOT NULL
""", conn)

# =====================================================
# 类型映射
# =====================================================

rel = pd.read_sql("""
SELECT
    r.c_assoc_code,
    r.c_assoc_type_code,
    t.c_assoc_type_desc_chn
FROM ASSOC_CODE_TYPE_REL r
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEFT JOIN ASSOC_TYPES t
ON r.c_assoc_type_code=t.c_assoc_type_code
""", conn)

def classify(code):

    code = str(code)

    if code.startswith("0202"):
        return "teacher"

    elif code.startswith("0301"):
        return "friend"

    elif code.startswith("0509"):
        return "letters"

    elif code.startswith("0407"):
        return "opposition"

    elif code.startswith("0405") or code.startswith("0406"):
        return "support"

    elif code.startswith("0402") \
         or code.startswith("0403") \
         or code.startswith("0404"):
        return "official"

    elif code.startswith("05") \
         or code.startswith("0203") \
         or code.startswith("0207"):
        return "literature"

    else:
        return "other"

rel["relation_group"] = (
    rel["c_assoc_type_code"]
    .astype(str)
    .apply(classify)
)

assoc = assoc.merge(
    rel[["c_assoc_code", "relation_group"]],
    on="c_assoc_code",
    how="left"
)

# =====================================================
# 加人物名
# =====================================================

assoc = assoc.merge(
    people[["c_personid", "name"]],
    on="c_personid",
    how="left"
)

assoc.rename(
    columns={"name": "person1"},
    inplace=True
)

assoc = assoc.merge(
    people[["c_personid", "name"]],
    left_on="c_assoc_id",
    right_on="c_personid",
    how="left"
)

assoc.rename(
    columns={"name": "person2"},
    inplace=True
)

assoc = assoc[
    assoc["person1"].notna()
]

assoc = assoc[
    assoc["person2"].notna()
]

# =====================================================
# 第一圈人物
# =====================================================

ring_rows = []

for core in CORE:

    tmp = assoc[
        (assoc["person1"] == core)
        |
        (assoc["person2"] == core)
    ].copy()

    tmp["target"] = tmp.apply(
        lambda x:
        x["person2"]
        if x["person1"] == core
        else x["person1"],
        axis=1
    )

    score = (
        tmp.groupby("target")
        .agg(
            relation_variety=("relation_group","nunique"),
            total=("relation_group","count")
        )
        .reset_index()
    )

    score["score"] = (
        score["relation_variety"] * 3
        + score["total"]
    )

    score = score.sort_values(
        "score",
        ascending=False
    )

    score = score.head(5)

    ring_rows.append(score)

first_ring = pd.concat(ring_rows)

ring_people = set(first_ring["target"])

# =====================================================
# 节点
# =====================================================

all_nodes = set(CORE) | ring_people

nodes = []

for n in all_nodes:

    if n in CORE:
        tp = "core"
    else:
        tp = "ring1"

    nodes.append([n,tp])

nodes = pd.DataFrame(
    nodes,
    columns=[
        "name",
        "node_type"
    ]
)

# =====================================================
# 保留边
# =====================================================

edges = assoc[
    assoc["person1"].isin(all_nodes)
]

edges = edges[
    edges["person2"].isin(all_nodes)
]

# =====================================================
# 无向化
# =====================================================

edges["node1"] = edges.apply(
    lambda x:
    min(x["person1"], x["person2"]),
    axis=1
)

edges["node2"] = edges.apply(
    lambda x:
    max(x["person1"], x["person2"]),
    axis=1
)

# =====================================================
# 边统计
# =====================================================

edge_rows = []

priority = [
    "opposition",
    "support",
    "teacher",
    "friend",
    "literature",
    "official",
    "other"
]

for (a,b), g in edges.groupby(
    ["node1","node2"]
):

    counts = (
        g["relation_group"]
        .value_counts()
        .to_dict()
    )

    total = len(g)

    main_relation = "other"

    for p in priority:

        if counts.get(p,0) > 0:
            main_relation = p
            break

    tooltip = f"""
主关系：{main_relation}

关系强度：{total}

书信：{counts.get('letters',0)}
文学：{counts.get('literature',0)}
朋友：{counts.get('friend',0)}
师生：{counts.get('teacher',0)}
政治盟友：{counts.get('support',0)}
政敌：{counts.get('opposition',0)}
官场：{counts.get('official',0)}
"""

    edge_rows.append([
        a,
        b,
        counts.get("friend",0),
        counts.get("letters",0),
        counts.get("literature",0),
        counts.get("teacher",0),
        counts.get("support",0),
        counts.get("opposition",0),
        counts.get("official",0),
        total,
        main_relation,
        tooltip
    ])

edges_final = pd.DataFrame(
    edge_rows,
    columns=[
        "source",
        "target",
        "friend",
        "letters",
        "literature",
        "teacher",
        "support",
        "opposition",
        "official",
        "total_weight",
        "main_relation",
        "tooltip"
    ]
)

# =====================================================
# NetworkX
# =====================================================

G = nx.Graph()

for _, row in edges_final.iterrows():

    G.add_edge(
        row["source"],
        row["target"],
        weight=row["total_weight"]
    )

# =====================================================
# 中心性
# =====================================================

degree = nx.degree_centrality(G)

between = nx.betweenness_centrality(
    G,
    weight="weight"
)

eigen = nx.eigenvector_centrality(
    G,
    weight="weight",
    max_iter=500
)

centrality = pd.DataFrame({
    "name": list(G.nodes()),
    "degree": [degree[n] for n in G.nodes()],
    "betweenness": [between[n] for n in G.nodes()],
    "eigenvector": [eigen[n] for n in G.nodes()]
})

centrality = centrality.sort_values(
    "eigenvector",
    ascending=False
)

# =====================================================
# 社群发现
# =====================================================

communities = list(
    greedy_modularity_communities(G)
)

community_rows = []

for idx, comm in enumerate(communities):

    for person in comm:

        community_rows.append([
            person,
            idx + 1
        ])

community_df = pd.DataFrame(
    community_rows,
    columns=[
        "name",
        "community"
    ]
)

# =====================================================
# 保存
# =====================================================

nodes.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Nodes_v4.xlsx"),
    index=False
)

edges_final.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Edges_v4.xlsx"),
    index=False
)

centrality.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Centrality.xlsx"),
    index=False
)

community_df.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Communities.xlsx"),
    index=False
)

print("="*60)
print("构建完成")
print("="*60)
print("节点数:", len(nodes))
print("边数:", len(edges_final))
print("社群数:", len(communities))
