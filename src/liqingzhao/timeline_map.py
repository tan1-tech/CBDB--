import sqlite3
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ==========================
# 中文字体
# ==========================

rcParams["font.sans-serif"] = ["Microsoft YaHei"]
rcParams["axes.unicode_minus"] = False

# ==========================
# 文件路径
# ==========================

DB_PATH = r"D:\cbdb_20260530.sqlite3"

CHINA_JSON = os.path.join(PROJECT_ROOT, "data", "raw", "China.json")

# ==========================
# 李清照迁移节点
# ==========================

migration_data = [

    ("1084", "章丘", 117.461580, 36.754170),
    ("1086", "開封", 114.343330, 34.785477),
    ("1108", "青州", 118.478098, 36.697480),
    ("1121", "萊州", 119.938004, 37.175430),

    ("1128", "建康府", 118.768990, 32.052563),

    ("1129", "池州", 117.481834, 30.654661),
    ("1129", "越州", 120.578262, 30.004515),
    ("1129", "嵊縣", 120.815277, 29.587490),
    ("1129", "台州", 121.120598, 28.843132),

    ("1130", "溫州", 120.653221, 28.018291),
    ("1130", "衢州", 118.867645, 28.956821),

    ("1131", "紹興府", 120.578262, 30.004515),

    ("1132", "臨安府", 120.168625, 30.294125),

    ("1134", "金華", 119.649918, 29.104712)

]

df = pd.DataFrame(
    migration_data,
    columns=["year", "place", "lon", "lat"]
)

# ==========================
# 标签偏移
# ==========================

offsets = {

    "章丘": (0.12, 0.18),
    "開封": (0.12, 0.18),
    "青州": (0.12, 0.18),
    "萊州": (0.12, 0.18),

    "建康府": (0.12, 0.12),
    "池州": (0.12, 0.12),

    "越州": (-0.90, 0.10),
    "紹興府": (0.55, 0.20),

    "嵊縣": (0.30, -0.45),

    "台州": (0.55, -0.15),

    "溫州": (0.40, -0.45),

    "衢州": (-0.80, -0.25),

    "金華": (-0.45, 0.15),

    "臨安府": (0.12, 0.30)

}

# ==========================
# 中国地图
# ==========================

china = gpd.read_file(CHINA_JSON)

fig, ax = plt.subplots(
    figsize=(16, 12)
)

china.plot(
    ax=ax,
    facecolor="#F8F8F8",
    edgecolor="gray",
    linewidth=0.6
)

# ==========================
# 绘制迁移路线
# ==========================

for i in range(len(df) - 1):

    x1 = df.iloc[i]["lon"]
    y1 = df.iloc[i]["lat"]

    x2 = df.iloc[i + 1]["lon"]
    y2 = df.iloc[i + 1]["lat"]

    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            color="steelblue",
            lw=2.5,
            alpha=0.8
        ),
        zorder=2
    )

# ==========================
# 绘制节点
# ==========================

for _, row in df.iterrows():

    year = int(row["year"])

    if year <= 1127:

        color = "royalblue"

    elif year <= 1132:

        color = "crimson"

    else:

        color = "forestgreen"

    ax.scatter(
        row["lon"],
        row["lat"],
        s=260,
        color=color,
        edgecolor="black",
        linewidth=1.2,
        zorder=5
    )

# ==========================
# 年份标签
# ==========================

for _, row in df.iterrows():

    place = row["place"]

    dx, dy = offsets.get(
        place,
        (0.15, 0.15)
    )

    ax.text(
        row["lon"] + dx,
        row["lat"] + dy,
        row["year"],
        fontsize=13,
        weight="bold",
        color="black",
        zorder=10
    )

# ==========================
# 靖康之变
# ==========================

ax.annotate(
    "靖康之变\n1127",

    xy=(114.343330, 34.785477),

    xytext=(113.8, 36.8),

    fontsize=11,

    color="firebrick",

    ha="center",

    arrowprops=dict(
        arrowstyle="->",
        lw=1.2,
        color="firebrick",
        alpha=0.7
    ),

    bbox=dict(
        facecolor="white",
        edgecolor="none",
        alpha=0.7,
        pad=1
    )
)

# ==========================
# 图例
# ==========================

from matplotlib.lines import Line2D
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

legend_elements = [

    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="北宋时期（1084-1127）",
        markerfacecolor="royalblue",
        markeredgecolor="black",
        markersize=14
    ),

    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="南渡流亡（1128-1132）",
        markerfacecolor="crimson",
        markeredgecolor="black",
        markersize=14
    ),

    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="南宋定居（1133以后）",
        markerfacecolor="forestgreen",
        markeredgecolor="black",
        markersize=14
    )

]

ax.legend(
    handles=legend_elements,
    loc="upper left",
    fontsize=14
)

# ==========================
# 坐标范围
# ==========================

ax.set_xlim(112, 123)

ax.set_ylim(27, 39)

# ==========================
# 标题
# ==========================

ax.set_title(
    "李清照迁移时间轴地图（1084—1134）",
    fontsize=30,
    weight="bold"
)

ax.set_xlabel(
    "经度",
    fontsize=16
)

ax.set_ylabel(
    "纬度",
    fontsize=16
)

plt.tight_layout()

plt.savefig(
    os.path.join(PROJECT_ROOT, "output", "liqingzhao", "LiQingzhao_Final_Timeline_Map.png"),
    dpi=400,
    bbox_inches="tight"
)

plt.show()

print("已保存：LiQingzhao_Final_Timeline_Map.png")

