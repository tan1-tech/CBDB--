import pandas as pd
import sqlite3

conn = sqlite3.connect(r"D:\cbdb_20260530.sqlite3")

# ==========================
# 人物基本信息
# ==========================

people = pd.read_sql("""
SELECT
    b.c_personid,

    b.c_name_chn AS name,

    CASE
        WHEN b.c_female=1 THEN '女'
        ELSE '男'
    END AS gender,

    d.c_dynasty_chn AS dynasty,

    b.c_birthyear,
    b.c_deathyear,

    a.c_name_chn AS native_place,

    a.x_coord,
    a.y_coord

FROM BIOG_MAIN b

LEFT JOIN DYNASTIES d
ON b.c_dy=d.c_dy

LEFT JOIN ADDR_CODES a
ON b.c_index_addr_id=a.c_addr_id

WHERE b.c_personid>0
""", conn)

print("人物数:", len(people))

family = pd.read_sql("""
SELECT
    c_personid,
    COUNT(*) AS family_size
FROM KIN_DATA
GROUP BY c_personid
""", conn)

people = people.merge(
    family,
    on="c_personid",
    how="left"
)

people["family_size"] = (
    people["family_size"]
    .fillna(0)
)

print("完成家族规模合并")

people.to_csv(
    os.path.join(PROJECT_ROOT, "data", "raw", "cbdb_partB_people.csv"),
    index=False,
    encoding="utf-8-sig"
)

print("已导出")

import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"]=["SimHei"]
plt.rcParams["axes.unicode_minus"]=False

dynasty_count = (
    people["dynasty"]
    .value_counts()
    .head(15)
)

plt.figure(figsize=(12,6))

dynasty_count.plot(
    kind="bar"
)

plt.title("CBDB人物朝代分布")

plt.ylabel("人数")

plt.tight_layout()

plt.savefig(
    os.path.join(PROJECT_ROOT, "output", "family", "dynasty_distribution.png"),
    dpi=300
)

plt.show()

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect(r"D:\cbdb_20260530.sqlite3")

people = pd.read_sql("""
SELECT
    d.c_dynasty_chn AS dynasty,

    CASE
        WHEN b.c_female=1 THEN '女'
        ELSE '男'
    END AS gender

FROM BIOG_MAIN b
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEFT JOIN DYNASTIES d
ON b.c_dy=d.c_dy

WHERE b.c_personid>0
""", conn)

plt.rcParams["font.sans-serif"]=["SimHei"]
plt.rcParams["axes.unicode_minus"]=False

gender_dynasty = pd.crosstab(
    people["dynasty"],
    people["gender"]
)

gender_dynasty = (
    gender_dynasty
    .sort_values(
        by="男",
        ascending=False
    )
    .head(10)
)

print(gender_dynasty)

gender_dynasty.plot(
    kind="bar",
    stacked=True,
    figsize=(12,6)
)

gender_ratio = gender_dynasty.div(
    gender_dynasty.sum(axis=1),
    axis=0
)
gender_ratio.plot(
    kind="bar",
    stacked=True
)

plt.title("不同朝代性别分布")
plt.xlabel("朝代")
plt.ylabel("人数")

plt.tight_layout()

plt.savefig(
    os.path.join(PROJECT_ROOT, "output", "family", "gender_dynasty.png"),
    dpi=300
)

plt.show()
