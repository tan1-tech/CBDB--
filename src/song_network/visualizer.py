import pandas as pd
from pyvis.network import Network
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================================
# 读取数据
# ==========================================

nodes = pd.read_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Nodes_v2.xlsx")
)

edges = pd.read_excel(
    os.path.join(PROJECT_ROOT, "data", "processed", "song_network", "Song_Network_Final_Edges_v2.xlsx")
)

# ==========================================
# 网络
# ==========================================

net = Network(
    height="900px",
    width="100%",
    bgcolor="#ffffff",
    font_color="black",
    notebook=False
)

# ==========================================
# 物理引擎
# ==========================================

net.barnes_hut(
    gravity=-5000,
    central_gravity=0.2,
    spring_length=180,
    spring_strength=0.03,
    damping=0.9
)

# ==========================================
# 节点
# ==========================================

for _, row in nodes.iterrows():

    name = row["name"]

    if row["node_type"] == "core":

        net.add_node(
            name,
            label=name,
            size=45,
            color="#c0392b",
            shape="dot",
            borderWidth=4
        )

    else:

        net.add_node(
            name,
            label=name,
            size=18,
            color="#3498db",
            shape="dot"
        )

# ==========================================
# 边颜色
# ==========================================

def edge_color(relation):

    if relation == "政敌":
        return "#e74c3c"

    elif relation == "政治盟友":
        return "#2980b9"

    elif relation == "师生":
        return "#27ae60"

    elif relation == "朋友":
        return "#f39c12"

    elif relation == "文人交往":
        return "#8e44ad"

    else:
        return "#95a5a6"

# ==========================================
# 边
# ==========================================

for _, row in edges.iterrows():

    relation = row["dominant_relation"]

    color = edge_color(relation)

    weight = max(
        1,
        min(
            row["total_weight"],
            10
        )
    )

    net.add_edge(
        row["source"],
        row["target"],
        title=row["tooltip"],
        color=color,
        width=weight
    )

# ==========================================
# 图例
# ==========================================

legend_html = """
<div style="
position:absolute;
top:20px;
right:20px;
z-index:9999;
background:white;
padding:15px;
border:1px solid #ccc;
font-size:14px;
">

<b>关系类型</b><br><br>

<span style="color:#e74c3c;">■</span> 政敌<br>
<span style="color:#2980b9;">■</span> 政治盟友<br>
<span style="color:#27ae60;">■</span> 师生<br>
<span style="color:#f39c12;">■</span> 朋友<br>
<span style="color:#8e44ad;">■</span> 文人交往<br>

</div>
"""

net.html += legend_html

# ==========================================
# 高级交互
# ==========================================

net.set_options("""
var options = {

  "interaction": {

      "hover": true,
      "navigationButtons": true,
      "keyboard": true

  },

  "nodes": {

      "font": {
          "size": 20
      }

  },

  "edges": {

      "smooth": {
          "type": "dynamic"
      }

  },

  "physics": {

      "enabled": true

  }

}
""")

# ==========================================
# 导出
# ==========================================

net.save_graph(
    os.path.join(PROJECT_ROOT, "output", "song_network", "Song_Literary_Network.html")
)

print("完成")



