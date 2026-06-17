import sqlite3
import pandas as pd
import geopandas as gpd

import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from scipy.stats import gaussian_kde
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================
# 中文显示
# ==========================

matplotlib.rcParams["font.family"] = "Microsoft YaHei"
matplotlib.rcParams["axes.unicode_minus"] = False

# ==========================
# 文件路径
# ==========================

DB_PATH = r"D:\cbdb_20260530.sqlite3"

CHINA_JSON = os.path.join(PROJECT_ROOT, "data", "raw", "China.json")

# ==========================
# 读取中国地图
# ==========================

china = gpd.read_file(CHINA_JSON)

# ==========================
# 数据库连接
# ==========================

conn = sqlite3.connect(DB_PATH)

# ==========================
# 朝代列表
# ==========================

dynasties = ["唐", "宋", "元", "明", "清"]

# ==========================
# 循环生成
# ==========================

for dynasty in dynasties:

    print(f"\n正在生成 {dynasty} 代热力图...")

    sql = f"""
    SELECT
        b.c_personid,
        b.c_name_chn,
        d.c_dynasty_chn AS dynasty,
        a.c_name_chn AS hometown,
        a.x_coord,
        a.y_coord

    FROM BIOG_MAIN b

    LEFT JOIN DYNASTIES d
        ON b.c_dy = d.c_dy

    LEFT JOIN ADDR_CODES a
        ON b.c_index_addr_id = a.c_addr_id

    WHERE d.c_dynasty_chn = '{dynasty}'
    """

    df = pd.read_sql(sql, conn)

    df = df.dropna(subset=["x_coord", "y_coord"])

    print("人物数量：", len(df))

    if len(df) < 100:
        print("数据过少，跳过")
        continue

    x = df["x_coord"].values
    y = df["y_coord"].values

    # ==========================
    # KDE
    # ==========================

    xmin, xmax = 73, 135
    ymin, ymax = 18, 54

    xx, yy = np.mgrid[
        xmin:xmax:300j,
        ymin:ymax:300j
    ]

    positions = np.vstack([xx.ravel(), yy.ravel()])

    values = np.vstack([x, y])

    kde = gaussian_kde(
        values,
        bw_method=0.15
    )

    density = np.reshape(
        kde(positions).T,
        xx.shape
    )
    density[density < np.percentile(density, 97)] = np.nan

    print(len(df))
    print(density.min())
    print(density.max())
    # ==========================
    # 绘图
    # ==========================

    # ==========================
    # 绘图
    # ==========================

    fig, ax = plt.subplots(
        figsize=(14, 10)
    )

    # 先画热力图
    heat = ax.imshow(
        density.T,
        origin="lower",
        extent=[xmin, xmax, ymin, ymax],
        cmap="YlOrRd",

        # 只显示高密度区域
        vmin=np.percentile(density, 92),
        vmax=np.percentile(density, 99.8),

        alpha=0.9,
        zorder=1
    )


    # 中国边界
    china.boundary.plot(
        ax=ax,
        color="steelblue",
        linewidth=0.6,
        zorder=2
    )

    # KDE等高线
    ax.contour(
        xx,
        yy,
        density,
        levels=10,
        colors="black",
        linewidths=0.4,
        alpha=0.4,
        zorder=3
    )

    plt.colorbar(
        heat,
        ax=ax,
        label="人才密度"
    )

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_title(
        f"{dynasty}代人才籍贯KDE热力图",
        fontsize=22
    )

    ax.set_xlabel("经度")
    ax.set_ylabel("纬度")

    plt.tight_layout()

    output = os.path.join(PROJECT_ROOT, "output", "talent", f"{dynasty}_KDE.png")

    plt.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"已保存：{output}")

conn.close()

print("\n全部完成！")
