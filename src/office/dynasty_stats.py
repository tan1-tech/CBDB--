import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 中文显示
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

conn = sqlite3.connect(r"D:\cbdb_20260530.sqlite3")

# ==========================
# 官职+朝代
# ==========================

office_df = pd.read_sql("""
SELECT
    d.c_dynasty_chn AS dynasty,
    o.c_office_chn AS office

FROM POSTED_TO_OFFICE_DATA p
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEFT JOIN OFFICE_CODES o
ON p.c_office_id = o.c_office_id

LEFT JOIN DYNASTIES d
ON p.c_dy = d.c_dy

WHERE o.c_office_chn IS NOT NULL
""", conn)

print(office_df.head())

# ==========================
# 图1
# 各朝代官职总量
# ==========================

order = ["唐","宋","元","明","清"]

dynasty_count = (
    office_df["dynasty"]
    .value_counts()
    .reindex(order)
    .fillna(0)
)

plt.figure(figsize=(10,6))

dynasty_count.plot(kind="bar")

plt.title("唐宋元明清官职记录数量")
plt.xlabel("朝代")
plt.ylabel("官职记录数")

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, "output", "office", "01_唐宋元明清官职数量.png"), dpi=300)
plt.show()

# ==========================
# 图2
# 各朝代Top5官职
# ==========================

top_dynasties = [
    "唐",
    "宋",
    "元",
    "明",
    "清"
]

for dy in top_dynasties:

    temp = office_df[
        office_df["dynasty"] == dy
    ]

    top_offices = (
        temp["office"]
        .value_counts()
        .head(5)
    )

    plt.figure(figsize=(10,5))

    top_offices.sort_values().plot(
        kind="barh"
    )

    plt.title(f"{dy}朝Top5官职")

    plt.xlabel("人数")

    plt.tight_layout()

    plt.savefig(
        os.path.join(PROJECT_ROOT, "output", "office", f"02_{dy}朝Top5官职.png"),
        dpi=300
    )

    plt.close()

# ==========================
# 图3
# 五大朝代官职结构
# ==========================

top20_offices = (
    office_df["office"]
    .value_counts()
    .head(20)
    .index
)

heatmap_df = office_df[
    office_df["office"].isin(top20_offices)
]

pivot = pd.crosstab(
    heatmap_df["dynasty"],
    heatmap_df["office"]
)

order = ["唐","宋","元","明","清"]

pivot = pivot.reindex(order)

plt.figure(figsize=(16,8))

plt.imshow(
    pivot,
    aspect="auto"
)

plt.colorbar()

plt.xticks(
    range(len(pivot.columns)),
    pivot.columns,
    rotation=90
)

plt.yticks(
    range(len(pivot.index)),
    pivot.index
)

plt.title("官职结构变化")

plt.tight_layout()

plt.savefig(
    os.path.join(PROJECT_ROOT, "output", "office", "03_官职结构变化.png"),
    dpi=300
)

plt.show()

# ==========================
# 导出统计表
# ==========================

office_stat = (
    office_df
    .groupby(
        ["dynasty","office"]
    )
    .size()
    .reset_index(name="count")
    .sort_values(
        "count",
        ascending=False
    )
)

order = {
    "唐":1,
    "宋":2,
    "元":3,
    "明":4,
    "清":5
}

office_stat["dynasty_order"] = (
    office_stat["dynasty"]
    .map(order)
)

office_stat = office_stat.sort_values(
    ["dynasty_order","count"],
    ascending=[True,False]
)

office_stat = office_stat.drop(
    columns=["dynasty_order"]
)

office_stat.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "office", "官职统计.xlsx"),
    index=False
)

pivot_table = pd.crosstab(
    office_df["dynasty"],
    office_df["office"]
)

pivot_table = pivot_table.reindex(
    ["唐","宋","元","明","清"]
)

pivot_table.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "office", "唐宋元明清官职交叉表.xlsx")
)


print("完成")