import pandas as pd
import json
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================
# 读取原始关系表
# ==========================

df = pd.read_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Literati_Relationships.xlsx")
)

print("原始记录数:", len(df))

# ==========================
# 六大核心人物
# ==========================

CORE = [
    "欧阳修",
    "司马光",
    "苏辙",
    "王安石",
    "苏轼",
    "曾巩"
]

# ==========================
# 关系分类函数
# ==========================

def classify_relation(desc):

    desc = str(desc)

    if any(x in desc for x in [
        "師",
        "师",
        "門人",
        "门人",
        "弟子"
    ]):
        return "teacher"

    elif any(x in desc for x in [
        "友",
        "交遊",
        "交游"
    ]):
        return "friend"

    elif any(x in desc for x in [
        "致書",
        "答書",
        "书",
        "被致書",
        "被致书"
    ]):
        return "letters"

    elif any(x in desc for x in [
        "書跋",
        "书跋",
        "序",
        "跋",
        "題",
        "题"
    ]):
        return "literature"

    elif any(x in desc for x in [
        "不合",
        "攻訐",
        "攻讦",
        "反對",
        "反对"
    ]):
        return "opposition"

    elif any(x in desc for x in [
        "推薦",
        "推荐",
        "薦舉",
        "荐举"
    ]):
        return "support"

    return "other"

# ==========================
# 仅保留核心人物相关关系
# ==========================

df = df[
    df["person1"].isin(CORE)
    |
    df["person2"].isin(CORE)
]

print("核心关系数:", len(df))

# ==========================
# 聚合
# ==========================

relations = {}

for _, row in df.iterrows():

    p1 = row["person1"]
    p2 = row["person2"]

    desc = str(row["c_assoc_desc_chn"])

    if pd.isna(p1) or pd.isna(p2):
        continue

    key = tuple(sorted([p1, p2]))

    if key not in relations:

        relations[key] = {

            "friend": 0,
            "letters": 0,
            "literature": 0,
            "teacher": 0,
            "support": 0,
            "opposition": 0,
            "other": 0,

            "records": []
        }

    category = classify_relation(desc)

    relations[key][category] += 1

    relations[key]["records"].append(desc)

# ==========================
# 构建边表
# ==========================

edges = []

for (p1, p2), data in relations.items():

    total = (
        data["friend"]
        + data["letters"]
        + data["literature"]
        + data["teacher"]
        + data["support"]
        + data["opposition"]
        + data["other"]
    )

    relation_scores = {

        "朋友": data["friend"],
        "师生": data["teacher"],
        "政治盟友": data["support"],
        "政敌": data["opposition"],
        "文人交往":
            data["letters"]
            + data["literature"]
    }

    main_relation = max(
        relation_scores,
        key=relation_scores.get
    )

    edges.append({

        "source": p1,
        "target": p2,

        "friend":
            data["friend"],

        "letters":
            data["letters"],

        "literature":
            data["literature"],

        "teacher":
            data["teacher"],

        "support":
            data["support"],

        "opposition":
            data["opposition"],

        "total_weight":
            total,

        "main_relation":
            main_relation,

        "records":
            json.dumps(
                data["records"],
                ensure_ascii=False
            )
    })

edges_df = pd.DataFrame(edges)

# ==========================
# tooltip
# ==========================

edges_df["tooltip"] = edges_df.apply(

    lambda r:

    f"""
关系类型：{r['main_relation']}

关系强度：{r['total_weight']}

书信：{r['letters']}
文学：{r['literature']}
朋友：{r['friend']}
师生：{r['teacher']}
盟友：{r['support']}
政敌：{r['opposition']}
""",

    axis=1
)

# ==========================
# 节点表
# ==========================

all_people = set()

for _, r in edges_df.iterrows():

    all_people.add(r["source"])
    all_people.add(r["target"])

nodes = []

for person in all_people:

    nodes.append({

        "name": person,

        "node_type":
            "core"
            if person in CORE
            else "normal"
    })

nodes_df = pd.DataFrame(nodes)

# ==========================
# 保存
# ==========================

nodes_df.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Nodes_Pro.xlsx"),
    index=False
)

edges_df.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Edges_Pro.xlsx"),
    index=False
)

print()
print("保存完成")
print()

print(
    "节点数:",
    len(nodes_df)
)

print(
    "边数:",
    len(edges_df)
)
