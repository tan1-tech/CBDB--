import os
import base64
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_cytoscape as cyto

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed" / "song_network"

NODES_FILE = DATA_DIR / "Song_Network_Final_Nodes_v2.xlsx"
EDGES_FILE = DATA_DIR / "Song_Network_Final_Edges_v2.xlsx"

# =====================================================
# 读取数据
# =====================================================

NODES_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Nodes_v2.xlsx")
EDGES_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Edges_v2.xlsx")

nodes_df = pd.read_excel(NODES_FILE)
edges_df = pd.read_excel(EDGES_FILE)

# =====================================================
# 核心人物档案
# =====================================================

CORE_NAMES = ["欧阳修", "司马光", "苏辙", "王安石", "苏轼", "曾巩"]

CORE_BIO = {
    "欧阳修": {
        "zi": "永叔", "hao": "醉翁，六一居士",
        "birth": "1007", "death": "1072",
        "hometown": "吉州庐陵",
        "works": "《醉翁亭记》《秋声赋》《新五代史》",
        "desc": "北宋文坛领袖，唐宋八大家之一。领导北宋诗文革新运动，开创一代文风。"
    },
    "司马光": {
        "zi": "君实", "hao": "迂叟",
        "birth": "1019", "death": "1086",
        "hometown": "陕州夏县",
        "works": "《资治通鉴》《训俭示康》",
        "desc": "北宋著名史学家、政治家。主持编纂中国第一部编年体通史《资治通鉴》。"
    },
    "王安石": {
        "zi": "介甫", "hao": "半山",
        "birth": "1021", "death": "1086",
        "hometown": "抚州临川",
        "works": "《游褒禅山记》《伤仲永》《桂枝香》",
        "desc": "北宋改革家、文学家。推行熙宁变法，诗文以雄健峭拔著称。"
    },
    "苏轼": {
        "zi": "子瞻", "hao": "东坡居士",
        "birth": "1037", "death": "1101",
        "hometown": "眉州眉山",
        "works": "《念奴娇·赤壁怀古》《赤壁赋》《水调歌头》",
        "desc": "北宋最伟大的文学家之一，诗词文赋书画无一不精。豁达旷放，千古风流。"
    },
    "苏辙": {
        "zi": "子由", "hao": "颍滨遗老",
        "birth": "1039", "death": "1112",
        "hometown": "眉州眉山",
        "works": "《黄州快哉亭记》《上枢密韩太尉书》",
        "desc": "苏轼之弟，唐宋八大家之一。散文汪洋澹泊，与兄齐名。"
    },
    "曾巩": {
        "zi": "子固", "hao": "南丰先生",
        "birth": "1019", "death": "1083",
        "hometown": "建昌南丰",
        "works": "《墨池记》《越州赵公救灾记》",
        "desc": "唐宋八大家之一，文章醇厚雅正，为欧阳修最为器重的弟子。"
    }
}

# =====================================================
# 篆书印章生成
# =====================================================

def make_seal_svg(name, size=90):
    """生成篆书风格印章 SVG（data URI），用作人物节点头像"""
    n = len(name)
    chars = list(name)
    font_size = max(int(size * 0.35), 24) if n <= 2 else max(int(size * 0.28), 20)
    line_h = size * 0.22
    start_y = size * 0.5 - (n - 1) * line_h * 0.5
    texts = ""
    for i, ch in enumerate(chars):
        y = start_y + i * line_h
        texts += f'<text x="{size/2}" y="{y}" text-anchor="middle" font-family="&apos;KaiTi&apos;,&apos;STKaiti&apos;,&apos;SimSun&apos;,serif" font-size="{font_size}" fill="white" font-weight="bold">{ch}</text>\n'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
<defs>
  <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#D43737"/>
    <stop offset="100%" style="stop-color:#9B1B1B"/>
  </linearGradient>
</defs>
<rect x="6" y="6" width="{size-12}" height="{size-12}" rx="10" fill="url(#sg)" stroke="#6B1010" stroke-width="3"/>
<rect x="12" y="12" width="{size-24}" height="{size-24}" rx="6" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
{texts}
<line x1="{size*0.25}" y1="{size*0.85}" x2="{size*0.75}" y2="{size*0.85}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/>
</svg>'''
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"

SEAL_CACHE = {}
def get_seal(name):
    if name not in SEAL_CACHE:
        SEAL_CACHE[name] = make_seal_svg(name)
    return SEAL_CACHE[name]

# =====================================================
# 传统配色方案（古籍风格）
# =====================================================

REL_COLORS = {
    "朋友":      "#5B8C5A",
    "师生":      "#4A7AA4",
    "政治盟友":  "#B8862D",
    "政敌":      "#B22222",
    "文人交往":  "#7B5B7A",
    "其他":      "#8B7D6B"
}

# =====================================================
# 连接度计算
# =====================================================

degree_dict = {}
for _, row in edges_df.iterrows():
    degree_dict[row["source"]] = degree_dict.get(row["source"], 0) + 1
    degree_dict[row["target"]] = degree_dict.get(row["target"], 0) + 1

# =====================================================
# 构建 Cytoscape Elements
# =====================================================

def build_elements(relation_filter="全部", min_weight=1, keyword=""):
    elements = []
    for _, row in nodes_df.iterrows():
        name = row["name"]
        if keyword and keyword not in name:
            continue
        is_core = name in CORE_NAMES
        node_class = "core" if is_core else "normal"
        el = {
            "data": {
                "id": name, "label": name,
                "degree": degree_dict.get(name, 0),
                "is_core": 1 if is_core else 0,
                "bio": CORE_BIO.get(name, {})
            },
            "classes": node_class
        }
        if is_core:
            el["style"] = {
                "background-image": get_seal(name),
                "background-fit": "contain",
                "background-clip": "none",
                "shape": "round-rectangle",
                "width": 80, "height": 80,
                "border-width": 3, "border-color": "#B8860B",
                "label": "data(label)",
                "font-size": 14, "color": "#2C1810",
                "font-family": "KaiTi, STKaiti, SimSun, serif",
                "font-weight": "bold",
                "text-valign": "bottom", "text-halign": "center",
                "text-margin-y": 6
            }
        else:
            el["style"] = {
                "background-color": "#8B7D6B",
                "shape": "ellipse",
                "width": 30, "height": 30,
                "label": "data(label)",
                "font-size": 11, "color": "#3E2723",
                "font-family": "KaiTi, STKaiti, SimSun, serif",
                "text-valign": "bottom", "text-halign": "center",
                "text-margin-y": 4
            }
        elements.append(el)

    visible_nodes = {e["data"]["id"] for e in elements}
    df = edges_df.copy()
    df = df[df["total_weight"] >= min_weight]
    if relation_filter != "全部":
        df = df[df["dominant_relation"] == relation_filter]

    for _, row in df.iterrows():
        if row["source"] not in visible_nodes or row["target"] not in visible_nodes:
            continue
        color = REL_COLORS.get(row["dominant_relation"], "#999999")
        width = min(max(int(row["total_weight"]), 1), 10)
        elements.append({
            "data": {
                "source": row["source"], "target": row["target"],
                "relation": row["dominant_relation"],
                "weight": int(row["total_weight"]),
                "tooltip": row["tooltip"],
                "friend": int(row["friend"]), "letters": int(row["letters"]),
                "literature": int(row["literature"]), "teacher": int(row["teacher"]),
                "support": int(row["support"]), "opposition": int(row["opposition"])
            },
            "style": {
                "line-color": color, "target-arrow-color": color,
                "width": width, "opacity": 0.75, "curve-style": "bezier"
            }
        })
    return elements

# =====================================================
# =====================================================
# Dash App
# =====================================================

app = dash.Dash(__name__)
app.title = "北宋文人知识图谱"

app.layout = html.Div([

    html.Div([
        html.H1("北宋文人知识图谱"),
        html.Div("Northern Song Literati Knowledge Graph", className="subtitle"),
        html.Div(className="decoration-line")
    ], className="main-header"),

    html.Div([

        # ---- 左侧 ----
        html.Div([
            html.Div([
                html.H3("探 索"),
                html.Div([
                    html.Label("人物检索"),
                    dcc.Input(id="search-box", type="text", placeholder="输入姓名", style={"width":"100%"})
                ], className="filter-section"),
                html.Div([
                    html.Label("关系类型"),
                    dcc.Dropdown(
                        id="relation-filter",
                        options=[{"label": x, "value": x} for x in ["全部", "朋友", "师生", "政治盟友", "政敌", "文人交往"]],
                        value="全部"
                    )
                ], className="filter-section"),
                html.Div([
                    html.Label("关系强度"),
                    dcc.Slider(
                        id="weight-slider",
                        min=1, max=int(edges_df["total_weight"].max()) if len(edges_df) > 0 else 10,
                        value=1,
                        marks={1:"弱", int(edges_df["total_weight"].max()) if len(edges_df) > 0 else 10:"强"}
                    )
                ], className="filter-section")
            ]),
            html.Hr(style={"border":"0.5px solid #C4A882", "margin":"12px 0"}),
            html.Div([
                html.H4("关 系"),
               ] + [html.Div([
                    html.Div(className="legend-color", style={"background-color": REL_COLORS[r]}),
                    html.Span(r)
                ], className="legend-item") for r in ["朋友", "师生", "政治盟友", "政敌", "文人交往"]] + [
                html.Div(className="legend-seal", children=[
                    html.Div(className="legend-seal-dot"),
                    html.Span("篆书印章 · 核心人物")
                ])
            ], className="legend")
        ], className="sidebar"),

        # ---- 中间 ----
        html.Div([
            cyto.Cytoscape(
                id="network",
                elements=build_elements(),
                style={"width":"100%", "height":"820px"},
                layout={"name":"concentric", "fit":True, "padding":80, "minNodeSpacing":80},
                stylesheet=[
                    {"selector": ".core", "style": {"shape": "round-rectangle"}},
                    {"selector": ".normal", "style": {"background-color": "#8B7D6B"}},
                    {"selector": "edge", "style": {
                        "target-arrow-shape": "triangle", "arrow-scale": 0.8,
                        "font-family": "KaiTi, STKaiti, SimSun, serif",
                        "font-size": "10px", "color": "#3E2723", "opacity": 0.7
                    }},
                    {"selector": "edge:selected", "style": {"opacity": 1, "width": 6, "z-index": 10}},
                    {"selector": "node:selected", "style": {
                        "border-width": 4, "border-color": "#B8860B",
                        "shadow-blur": 15, "shadow-color": "rgba(184,134,11,0.5)", "shadow-opacity": 1
                    }}
                ]
            )
        ], className="network-area"),

        # ---- 右侧 ----
        html.Div([
            html.H3("人 物 档 案"),
            html.Div(id="info-content", className="info-content")
        ], className="info-panel")

    ], className="main-container")
])

# =====================================================
# 回调
# =====================================================

@app.callback(
    Output("network", "elements"),
    Input("relation-filter", "value"),
    Input("weight-slider", "value"),
    Input("search-box", "value")
)
def update_network(rel, weight, keyword):
    if keyword is None:
        keyword = ""
    return build_elements(rel, weight, keyword)

@app.callback(
    Output("info-content", "children"),
    Input("network", "tapNodeData"),
    Input("network", "tapEdgeData")
)
def show_info(node_data, edge_data):
    if node_data:
        name = node_data["label"]
        degree = node_data["degree"]
        bio = node_data.get("bio", {})
        seal_uri = get_seal(name) if name in CORE_NAMES else ""

        if name in CORE_NAMES:
            return html.Div([
                html.Div([
                    html.Img(src=seal_uri, className="seal-corner") if seal_uri else "",
                    html.Div(name, className="person-name"),
                    html.Div(f"字 {bio.get('zi','')} 号 {bio.get('hao','')}", className="person-zi"),
                    html.Div([
                        html.Div([html.Span("朝 代", className="bio-label"), html.Span("北宋", className="bio-value")], className="bio-row"),
                        html.Div([html.Span("生 卒", className="bio-label"), html.Span(f"{bio.get('birth','')} — {bio.get('death','')}", className="bio-value")], className="bio-row"),
                        html.Div([html.Span("籍 贯", className="bio-label"), html.Span(bio.get("hometown",""), className="bio-value")], className="bio-row"),
                        html.Div([html.Span("代表作", className="bio-label"), html.Span(bio.get("works",""), className="bio-value")], className="bio-row"),
                    ]),
                    html.Div(bio.get("desc",""), className="bio-desc"),
                    html.Div(f"网络中连接 {degree} 人", className="connections")
                ], className="archive-card")
            ])
        else:
            return html.Div([
                html.Div([
                    html.Div(name, className="person-name", style={"fontSize":"20px"}),
                    html.Div(f"网络中连接 {degree} 人", style={"marginTop":"8px", "fontSize":"13px", "color":"#6B5B4E"}),
                    html.Div("该人物在知识图谱中处于第一圈层", style={"marginTop":"6px", "padding":"8px", "background":"rgba(139,107,58,0.08)", "borderLeft":"2px solid #B8860B", "fontSize":"12px", "lineHeight":"1.6", "color":"#4A3728"})
                ], className="archive-card")
            ])

    if edge_data:
        rel = edge_data.get("relation", "未知")
        rel_color = REL_COLORS.get(rel, "#999")
        total = edge_data.get("weight", 0)
        rels = {
            "书信往来": int(edge_data.get("letters", 0)),
            "文学交往": int(edge_data.get("literature", 0)),
            "朋友": int(edge_data.get("friend", 0)),
            "师生": int(edge_data.get("teacher", 0)),
            "政治盟友": int(edge_data.get("support", 0)),
            "政敌": int(edge_data.get("opposition", 0))
        }
        rels = {k:v for k,v in rels.items() if v > 0}
        max_val = max(rels.values()) if rels else 1

        return html.Div([
            html.Div([
                html.Div(f"{edge_data['source']} x {edge_data['target']}", className="rel-header",
                    style={"borderBottom": f"2px solid {rel_color}"}),
                html.Div([
                    html.Div([
                        html.Div("关系类型", className="rel-stat-label"),
                        html.Div(rel, className="rel-stat-value", style={"color": rel_color})
                    ], className="rel-stat-row"),
                    html.Div([
                        html.Div("关系强度", className="rel-stat-label"),
                        html.Div(str(total), className="rel-stat-value")
                    ], className="rel-stat-row"),
                ] + [html.Div([
                        html.Div(k, className="rel-stat-label"),
                        html.Div(className="rel-bar-bg", children=[
                            html.Div(className="rel-bar-fill",
                                style={"width": f"{v/max_val*100}%", "backgroundColor": rel_color, "opacity": 0.6 + 0.4 * v/max_val})
                        ]),
                        html.Div(str(v), className="rel-stat-value")
                    ], className="rel-stat-row", style={"display":"flex", "gap":"8px", "alignItems":"center", "justifyContent":"space-between"}) for k,v in rels.items()
                ], style={"marginTop":"8px"})
            ], className="relation-card")
        ])

    return html.Div([
        html.Div("点击人物", style={"fontSize":"16px", "fontWeight":"bold", "letterSpacing":"2px", "color":"#6B5B4E"}),
        html.Div("查看人物档案", style={"fontSize":"12px", "color":"#8B7D6B", "marginTop":"4px"}),
        html.Div("或点击关系线查看关系画像", style={"fontSize":"12px", "color":"#8B7D6B", "marginTop":"2px"})
    ], className="info-empty")

if __name__ == "__main__":
    app.run(debug=True, port=8050)
