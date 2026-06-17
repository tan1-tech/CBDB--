import pandas as pd
import sqlite3

conn = sqlite3.connect(r"D:\cbdb_20260530.sqlite3")

# =====================
# 1. 人物总数
# =====================
total_people = pd.read_sql("""
SELECT COUNT(*) AS total_people
FROM BIOG_MAIN
WHERE c_personid > 0
""", conn)

print("\n===== 人物总数 =====")
print(total_people)

# =====================
# 2. 各朝代人数
# =====================
people = pd.read_sql("""
SELECT
    b.c_personid,
    d.c_dynasty_chn AS dynasty

FROM BIOG_MAIN b

LEFT JOIN DYNASTIES d
ON b.c_dy = d.c_dy

WHERE b.c_personid > 0
""", conn)

print("\n===== 各朝代人数TOP20 =====")
print(
    people["dynasty"]
    .value_counts()
    .head(20)
)

# =====================
# 3. 官职TOP20
# =====================
office = pd.read_sql("""
SELECT
    o.c_office_chn

FROM POSTED_TO_OFFICE_DATA p

LEFT JOIN OFFICE_CODES o
ON p.c_office_id = o.c_office_id

WHERE o.c_office_chn IS NOT NULL
""", conn)

print("\n===== 官职TOP20 =====")
print(
    office["c_office_chn"]
    .value_counts()
    .head(20)
)