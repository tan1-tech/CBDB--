# 北宋文人知识图谱

基于 CBDB（中国历史人物传记数据库）的北宋文人社会关系知识图谱。

## 快速开始

`ash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成图谱数据
python python/build_json.py

# 3. 打开网页
# 直接用浏览器打开 index.html
`

## 项目结构

`
├── index.html              # 主页面（首页 + 图谱）
├── assets/style.css        # 样式
├── js/
│   ├── data_loader.js      # 数据加载
│   └── network.js          # ECharts 图谱
├── python/build_json.py    # 数据构建脚本
├── network_data.json       # 生成的图谱数据
├── requirements.txt
└── README.md
`

## 模块计划

1. ✅ 人物关系图谱（当前）
2. ⏳ 人物迁移地图
3. ⏳ 籍贯分布分析
4. ⏳ 官职体系分析
5. ⏳ CBDB 数据库探索

## 技术栈

- Apache ECharts 5 — 图谱可视化
- 纯前端 HTML/CSS/JS — 无需后端
- Python — 数据预处理
