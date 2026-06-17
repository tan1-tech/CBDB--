import sqlite3
import pandas as pd
import geopandas as gpd
import numpy as np

import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

from matplotlib import font_manager

# ==================================
# 字体
# ==================================

font_path = "C:/Windows/Fonts/msyh.ttc"

font_manager.fontManager.addfont(font_path)

plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

# ==================================
# 路径
# ==================================

DB_PATH = r"D:\cbdb_20260530.sqlite3"

CHINA_JSON = os.path.join(PROJECT_ROOT, "data", "raw", "China.json")

# ==================================
# 连接数据库
# ==================================

conn = sqlite3.connect(DB_PATH)

# ==================================
# 籍贯
# ==================================

sql_home = """
SELECT

    b.c_personid,

    a.x_coord,
    a.y_coord

FROM BIOG_MAIN b

LEFT JOIN ADDR_CODES a
    ON b.c_index_addr_id = a.c_addr_id

WHERE
    b.c_dy = 15
"""

home = pd.read_sql(sql_home, conn)

home = home.dropna()

print("籍贯人数：", len(home))

# ==================================
# 最终活动地点
# ==================================

sql_final = """
WITH last_place AS (

    SELECT

        c_personid,

        MAX(c_firstyear) AS last_year

    FROM BIOG_ADDR_DATA

    WHERE c_firstyear > 0

    GROUP BY c_personid
)

SELECT

    b.c_personid,

    ac.x_coord,
    ac.y_coord

FROM last_place lp
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEFT JOIN BIOG_ADDR_DATA bad
    ON lp.c_personid = bad.c_personid
   AND lp.last_year = bad.c_firstyear

LEFT JOIN ADDR_CODES ac
    ON bad.c_addr_id = ac.c_addr_id

LEFT JOIN BIOG_MAIN b
    ON lp.c_personid = b.c_personid

WHERE
    b.c_dy = 15
"""

final = pd.read_sql(sql_final, conn)

final = final.dropna()

print("最终地点人数：", len(final))

conn.close()

# ==================================
# 中国地图
# ==================================

china = gpd.read_file(CHINA_JSON)

# ==================================
# KDE函数
# ==================================

xmin, xmax = 73, 135
ymin, ymax = 18, 54

xx, yy = np.mgrid[
    xmin:xmax:300j,
    ymin:ymax:300j
]

positions = np.vstack([
    xx.ravel(),
    yy.ravel()
])

# ==================================
# 籍贯KDE
# ==================================

values_home = np.vstack([
    home["x_coord"],
    home["y_coord"]
])

kde_home = gaussian_kde(
    values_home,
    bw_method=0.25
)

density_home = np.reshape(
    kde_home(positions),
    xx.shape
)

# ==================================
# 最终地点KDE
# ==================================

values_final = np.vstack([
    final["x_coord"],
    final["y_coord"]
])

kde_final = gaussian_kde(
    values_final,
    bw_method=0.25
)

density_final = np.reshape(
    kde_final(positions),
    xx.shape
)

# ==================================
# 绘图
# ==================================

fig, ax = plt.subplots(
    figsize=(16, 12)
)

china.plot(
    ax=ax,
    facecolor="white",
    edgecolor="gray",
    linewidth=0.5
)

# 蓝色 = 籍贯

ax.contourf(
    xx,
    yy,
    density_home,
    levels=10,
    cmap="Blues",
    alpha=0.55
)

# 红色 = 最终地点

ax.contourf(
    xx,
    yy,
    density_final,
    levels=10,
    cmap="Reds",
    alpha=0.55
)

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

ax.set_title(
    "南宋人物籍贯与最终活动地空间分布对比",
    fontsize=24
)

ax.set_xlabel("经度")
ax.set_ylabel("纬度")

plt.tight_layout()

plt.savefig(
    os.path.join(PROJECT_ROOT, "output", "southern_song", "SouthernSong_Migration_Comparison.png"),
    dpi=400,
    bbox_inches="tight"
)

plt.show()
