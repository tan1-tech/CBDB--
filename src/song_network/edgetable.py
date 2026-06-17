import sqlite3
import pandas as pd
from opencc import OpenCC

# ==================================================
# 配置
# ==================================================

DB_PATH = r"D:\cbdb_20260530.sqlite3"

cc = OpenCC("t2s")

CORE_PERSONS = {
    1384: "欧阳修",
    1488: "司马光",
    1493: "苏辙",
    1762: "王安石",
    3767: "苏轼",
    7364: "曾巩"
}

# ==================================================
# 数据库连接
# ==================================================

conn = sqlite3.connect(DB_PATH)

# ==================================================
# 读取关系
# ==================================================

sql = """
SELECT

p1.c_name_chn AS source,
p2.c_name_chn AS target,

ac.c_assoc_desc_chn,

r.c_assoc_type_code,
t.c_assoc_type_desc_chn

FROM ASSOC_DATA a
$PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEFT JOIN BIOG_MAIN p1
ON a.c_personid = p1.c_personid

LEFT JOIN BIOG_MAIN p2
ON a.c_assoc_id = p2.c_personid

LEFT JOIN ASSOC_CODES ac
ON a.c_assoc_code = ac.c_assoc_code

LEFT JOIN ASSOC_CODE_TYPE_REL r
ON a.c_assoc_code = r.c_assoc_code

LEFT JOIN ASSOC_TYPES t
ON r.c_assoc_type_code = t.c_assoc_type_code

WHERE a.c_personid IN (
1384,
1488,
1493,
1762,
3767,
7364
)

AND a.c_assoc_id IS NOT NULL
"""

df = pd.read_sql(sql, conn)

# ==================================================
# 简体转换
# ==================================================

for col in [
    "source",
    "target",
    "c_assoc_desc_chn"
]:
    df[col] = (
        df[col]
        .astype(str)
        .apply(cc.convert)
    )

# ==================================================
# CBDB关系类型映射
# ==================================================

REL_MAP = {

    "0202": "teacher",

    "0203": "literature",

    "0207": "literature",

    "0301": "friend",

    "0405": "support",

    "0406": "support",

    "0407": "opposition",

    "0509": "letters"
}

df["relation_group"] = (
    df["c_assoc_type_code"]
    .astype(str)
    .map(REL_MAP)
)

df = df[df["relation_group"].notna()].copy()

print("保留记录数：", len(df))

# ==================================================
# 第一圈人物（按关系种类数）
# ==================================================

first_ring = []

for core in CORE_PERSONS.values():

    temp = df[
        df["source"] == core
    ]

    score = (
        temp.groupby("target")["c_assoc_desc_chn"]
        .nunique()
        .reset_index(name="relation_variety")
        .sort_values(
            "relation_variety",
            ascending=False
        )
        .head(5)
    )

    score["core_person"] = core

    first_ring.append(score)

first_ring = pd.concat(
    first_ring,
    ignore_index=True
)

print()
print("第一圈人物")
print(first_ring.head(30))

# ==================================================
# 节点表
# ==================================================

ring_nodes = sorted(
    set(first_ring["target"])
)

nodes = []

for person in CORE_PERSONS.values():

    nodes.append({
        "name": person,
        "node_type": "core"
    })

for person in ring_nodes:

    if person not in CORE_PERSONS.values():

        nodes.append({
            "name": person,
            "node_type": "ring1"
        })

nodes_df = pd.DataFrame(nodes)

# ==================================================
# 保留节点
# ==================================================

all_nodes = set(
    nodes_df["name"]
)

edges = df[
    df["source"].isin(all_nodes)
    &
    df["target"].isin(all_nodes)
].copy()

# ==================================================
# 无向边
# ==================================================

edges["node1"] = edges[
    ["source","target"]
].min(axis=1)

edges["node2"] = edges[
    ["source","target"]
].max(axis=1)

# ==================================================
# 关系种类统计
# ==================================================

pivot = pd.pivot_table(
    edges,
    index=["node1","node2"],
    columns="relation_group",
    values="c_assoc_desc_chn",
    aggfunc=lambda x: x.nunique(),
    fill_value=0
)

pivot = pivot.reset_index()

# ==================================================
# 补列
# ==================================================

for col in [
    "teacher",
    "friend",
    "literature",
    "letters",
    "support",
    "opposition"
]:
    if col not in pivot.columns:
        pivot[col] = 0

# ==================================================
# 总关系丰富度
# ==================================================

pivot["total_weight"] = (

      pivot["teacher"]
    + pivot["friend"]
    + pivot["literature"]
    + pivot["letters"]
    + pivot["support"]
    + pivot["opposition"]

)

# ==================================================
# 主导关系
# ==================================================

def dominant_relation(row):

    scores = {

        "师生": row["teacher"],

        "朋友": row["friend"],

        "文人交往":
            row["literature"]
            + row["letters"],

        "政治盟友":
            row["support"],

        "政敌":
            row["opposition"]
    }

    return max(
        scores,
        key=scores.get
    )

pivot["dominant_relation"] = (
    pivot.apply(
        dominant_relation,
        axis=1
    )
)

# ==================================================
# Tooltip
# ==================================================

pivot["tooltip"] = pivot.apply(
    lambda r:
f"""
关系画像：{r['dominant_relation']}

关系丰富度：{r['total_weight']}

文学：{r['literature']}
书信：{r['letters']}
朋友：{r['friend']}
师生：{r['teacher']}
政治支持：{r['support']}
政治对抗：{r['opposition']}
""",
    axis=1
)

# ==================================================
# 排序
# ==================================================

pivot = pivot.sort_values(
    "total_weight",
    ascending=False
)

# ==================================================
# 重命名
# ==================================================

edges_df = pivot.rename(
    columns={
        "node1":"source",
        "node2":"target"
    }
)

# ==================================================
# 保存
# ==================================================

nodes_df.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Nodes_v2.xlsx"),
    index=False
)

edges_df.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Edges_v2.xlsx"),
    index=False
)

first_ring.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "SongNetwork_FirstRing_v2.xlsx"),
    index=False
)

print()
print("====================================")
print("保存完成")
print(os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Nodes_v2.xlsx"))
print(os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Edges_v2.xlsx"))
print(os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "SongNetwork_FirstRing_v2.xlsx"))
print("====================================")

print()
print("节点数：", len(nodes_df))
print("边数：", len(edges_df))

print()
print(
    edges_df[
        [
            "source",
            "target",
            "dominant_relation",
            "total_weight"
        ]
    ].head(30)
)
