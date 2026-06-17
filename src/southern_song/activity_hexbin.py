import sqlite3
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ==========================
# 中文字体
# ==========================

font_path = r"C:\Windows\Fonts\msyh.ttc"
font_manager.fontManager.addfont(font_path)

plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

# ==========================
# 路径
# ==========================

DB_PATH = r"D:\cbdb_20260530.sqlite3")

CHINA_JSON = os.path.join(PROJECT_ROOT, "data", "raw", "China.json")

# ==========================
# 连接数据库
# ==========================

conn = sqlite3.connect(DB_PATH)

# ==========================
# 提取南宋人物活动地点
# ==========================

sql = """
SELECT

    bad.c_personid,

    ac.c_name_chn AS place,

    ac.x_coord,
    ac.y_coord,

    bad.c_addr_type,

    b.c_name_chn

FROM BIOG_ADDR_DATA bad
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEFT JOIN BIOG_MAIN b
    ON bad.c_personid = b.c_personid

LEFT JOIN ADDR_CODES ac
    ON bad.c_addr_id = ac.c_addr_id

WHERE

    b.c_dy = 15

    AND bad.c_addr_type IN (2,3,5,6)

    AND ac.x_coord IS NOT NULL
    AND ac.y_coord IS NOT NULL
"""

df = pd.read_sql(sql, conn)

conn.close()

print("活动记录数量：", len(df))

# ==========================
# 保存原始数据
# ==========================

df.to_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "southern_song", "SouthernSong_Activity.xlsx"),
    index=False
)

print("已保存 SouthernSong_Activity.xlsx")

# ==========================
# 读取地图
# ==========================

china = gpd.read_file(CHINA_JSON)

# ==========================
# 绘图
# ==========================

fig, ax = plt.subplots(
    figsize=(16,12)
)

china.plot(
    ax=ax,
    facecolor="white",
    edgecolor="steelblue",
    linewidth=0.6
)

# ==========================
# Hexbin
# ==========================

hb = ax.hexbin(
    df["x_coord"],
    df["y_coord"],
    gridsize=60,
    cmap="YlOrRd",
    mincnt=1,
    alpha=0.85
)

# ==========================
# Colorbar
# ==========================

cbar = plt.colorbar(
    hb,
    ax=ax
)

cbar.set_label(
    "活动记录数量",
    fontsize=14
)

# ==========================
# 地图范围
# ==========================

ax.set_xlim(73,135)
ax.set_ylim(18,54)

# ==========================
# 标题
# ==========================

ax.set_title(
    "南宋人物活动地点空间分布图",
    fontsize=24,
    pad=20
)

ax.set_xlabel("经度")
ax.set_ylabel("纬度")

plt.tight_layout()

plt.savefig(
    os.path.join(PROJECT_ROOT, "output", "southern_song", "SouthernSong_Activity_Hexbin.png"),
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("已保存：SouthernSong_Activity_Hexbin.png")

print("活动记录数量：", len(df))

print("涉及人物数：", df["c_personid"].nunique())
