const CUI = (function() {
    "use strict";

    var data = null;
    var charts = {};
    var RC = { family: "#CC2929", gold: "#B8860B", text: "#2C1810", light: "#8B7D6B", bg: "transparent" };

    function initChart(id) {
        var d = document.getElementById(id);
        if (!d) return null;
        var c = echarts.init(d, null, { renderer: "canvas" });
        charts[id] = c;
        return c;
    }

    // ============================================================
    // renderAll
    // ============================================================
    async function renderAll() {
        try {
            data = await CUI_DATA.load();
            renderOverview(); renderDynastyEvolutionChart(); renderOfficeChart();
            renderKinshipNetwork(); renderMarriageNetwork(); renderConclusion();
        } catch (e) { console.error("[CUI] ERROR:", e); }
    }

    // ============================================================
    // renderOverview
    // ============================================================
    function renderOverview() {
        var el = document.getElementById("cui-overview");
        if (!el || !data) return;
        var m = data.meta || {};
        el.innerHTML = "<div class=\"overview-grid\">"
            + "<div class=\"overview-card\"><div class=\"ov-number\">" + (m.total_people || 0) + "</div><div class=\"ov-label\">清河崔氏</div></div>"
            + "<div class=\"overview-card\"><div class=\"ov-number\">" + (m.dynasty_count || 0) + "</div><div class=\"ov-label\">覆盖朝代</div></div>"
            + "<div class=\"overview-card\"><div class=\"ov-number\">" + (m.marriage_count || 0) + "</div><div class=\"ov-label\">联姻家族</div></div>"
            + "<div class=\"overview-card\"><div class=\"ov-number\">" + (m.total_kinship || 0) + "</div><div class=\"ov-label\">亲属关系</div></div>"
            + "<div class=\"overview-card\"><div class=\"ov-number\">" + (m.max_degree || 0) + "</div><div class=\"ov-label\">最高连接度</div></div>"
            + "</div>";
    }

    // ============================================================
    // renderDynastyEvolutionChart
    // ============================================================
    function renderDynastyEvolutionChart() {
        var c = initChart("cui-evolution-chart");
        if (!c || !data || !data.dynasty_evolution) return;
        var de = data.dynasty_evolution;
        var colors = ["#CC2929","#B8862D","#5B8C5A","#4A7AA4","#7B5B7A","#C0722B","#B22222","#8B7355","#A0926B","#6B5B4E"];
        c.setOption({
            tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
            grid: { left: 70, right: 20, top: 20, bottom: 50 },
            xAxis: { type: "category", data: de.map(function(d){ return d.dynasty; }), axisLabel: { fontFamily: "KaiTi,serif", color: RC.text, rotate: 35, fontSize: 10 }, axisLine: { lineStyle: { color: RC.light } } },
            yAxis: { type: "value", axisLabel: { fontFamily: "KaiTi,serif", color: RC.text, fontSize: 10 }, splitLine: { lineStyle: { color: "rgba(139,90,43,0.1)" } } },
            series: [{ type: "bar", data: de.map(function(d){ return d.cnt; }), itemStyle: { color: function(p){ return colors[p.dataIndex % colors.length]; }, borderRadius: [3,3,0,0] }, barMaxWidth: 28, label: { show: true, position: "top", fontFamily: "KaiTi,serif", fontSize: 9, color: RC.text } }]
        });
        c.resize();
    }

    // ============================================================
    // renderOfficeChart
    // ============================================================
    function renderOfficeChart() {
        var c = initChart("cui-office-chart");
        if (!c || !data || !data.office_distribution) return;
        var od = data.office_distribution.filter(function(d){ return d.office && d.office !== ""; }).slice(0, 12).reverse();
        c.setOption({
            tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
            grid: { left: 120, right: 30, top: 10, bottom: 20 },
            xAxis: { type: "value", axisLabel: { fontFamily: "KaiTi,serif", color: RC.text, fontSize: 10 }, splitLine: { lineStyle: { color: "rgba(139,90,43,0.1)" } } },
            yAxis: { type: "category", data: od.map(function(d){ return d.office; }), axisLabel: { fontFamily: "KaiTi,serif", color: RC.text, fontSize: 10 }, axisLine: { lineStyle: { color: RC.light } } },
            series: [{ type: "bar", data: od.map(function(d){ return d.cnt || d.count || 0; }), itemStyle: { color: RC.family, borderRadius: [0,3,3,0] }, barMaxWidth: 18, label: { show: true, position: "right", fontFamily: "KaiTi,serif", fontSize: 9, color: RC.text } }]
        });
        c.resize();
    }

    // ============================================================
    // renderKinshipNetwork
    // ============================================================
    function renderKinshipNetwork() {
        var c = initChart("cui-kinship-chart");
        if (!c || !data || !data.links) return;

        var connected = {};
        data.links.forEach(function(l){ connected[l.source] = true; connected[l.target] = true; });
        var visNodes = data.nodes.filter(function(n){ return connected[n.id]; });
        if (visNodes.length === 0) { c.resize(); return; }

        var catMap = {}, catList = [];
        visNodes.forEach(function(n){ var d = n.dynasty || ""; if (!catMap[d]){ catMap[d] = true; catList.push(d); } });

        var chartNodes = visNodes.map(function(n){
            var ci = catList.indexOf(n.dynasty || "");
            if (ci < 0) ci = 0;
            var sz = Math.min(Math.max(6 + (n.degree || 0) * 2, 8), 40);
            return {
                id: String(n.id), name: n.name, value: n.degree || 0, category: ci,
                symbolSize: sz,
                label: { show: (n.degree || 0) > 5, position: "bottom", fontFamily: "KaiTi,serif", fontSize: 10, color: RC.text },
                itemStyle: sz > 25 ? { borderColor: RC.gold, borderWidth: 2 } : {},
                _raw: n
            };
        });

        var catColors = ["#CC2929","#B8862D","#5B8C5A","#4A7AA4","#7B5B7A","#C0722B","#B22222","#8B7355","#A0926B","#6B5B4E"];
        catList.forEach(function(d, i){ if (!catMap[d]) catMap[d] = true; });

        var idSet = {};
        chartNodes.forEach(function(n){ idSet[n.id] = true; });
        var chartLinks = data.links.filter(function(l){ return idSet[String(l.source)] && idSet[String(l.target)]; }).map(function(l){
            return { source: String(l.source), target: String(l.target), lineStyle: { color: "rgba(139,90,43,0.25)", width: 0.8, curveness: 0.2 }, _raw: l };
        });

        c.setOption({
            backgroundColor: "transparent",
            series: [{
                type: "graph", layout: "force",
                force: { repulsion: 600, edgeLength: [80, 200], gravity: 0.05, friction: 0.2, layoutAnimation: true },
                roam: true, draggable: true,
                data: chartNodes, links: chartLinks,
                categories: catList.map(function(d, i){ return { name: d, itemStyle: { color: catColors[i % catColors.length] } }; }),
                edgeSymbol: ["none", "none"], lineStyle: { opacity: 0.3 },
                label: { show: false },
                emphasis: { focus: "adjacency", lineStyle: { width: 3 } },
                blur: { opacity: 0.15 }
            }]
        });
        c.resize();
    }

    // ============================================================
    // renderMarriageNetwork
    // ============================================================
    function renderMarriageNetwork() {
        var c = initChart("cui-marriage-chart");
        if (!c || !data || !data.clan_marriage) return;

        var cm = data.clan_marriage;
        var chartNodes = [];
        var allIds = {};
        cm.forEach(function(d){
            [d.source, d.target].forEach(function(id){
                if (!allIds[id]) {
                    allIds[id] = true;
                    var isSelf = (id === "\u6e05\u6cb3\u5d14\u6c0f");
                    chartNodes.push({
                        id: id, name: id,
                        symbolSize: isSelf ? 50 : 30,
                        category: isSelf ? 0 : 1,
                        itemStyle: { color: isSelf ? RC.family : "#8B7355", borderColor: isSelf ? "#8B1A1A" : "#6B5B4E", borderWidth: isSelf ? 3 : 1 },
                        label: { show: true, position: "bottom", fontFamily: "KaiTi,serif", fontSize: 10, color: RC.text }
                    });
                }
            });
        });

        var chartLinks = [];
        cm.forEach(function(d){
            if (d.source !== d.target) {
                var w = Math.min(1 + (d.count || 0) * 0.5, 8);
                chartLinks.push({
                    source: d.source, target: d.target,
                    value: d.count || 0,
                    lineStyle: { color: "rgba(204,41,41,0.3)", width: w, curveness: 0.2, opacity: 0.6 },
                    label: { show: true, formatter: (d.count || "1") + "\u6b21", fontFamily: "KaiTi,serif", fontSize: 9, color: "#2C1810" }
                });
            }
        });

        c.setOption({
            backgroundColor: "transparent",
            series: [{
                type: "graph", layout: "circular",
                circular: { rotateLabel: true },
                roam: true, draggable: true,
                data: chartNodes, links: chartLinks,
                categories: [{ name: "\u6e05\u6cb3\u5d14\u6c0f", itemStyle: { color: RC.family } }, { name: "\u8054\u59fb\u65cf", itemStyle: { color: "#8B7355" } }],
                edgeSymbol: ["none", "arrow"],
                edgeLabel: { show: true, fontSize: 9, fontFamily: "KaiTi,serif", color: "#2C1810" },
                emphasis: { focus: "adjacency", lineStyle: { width: 4 } },
                blur: { opacity: 0.2 }
            }]
        });
        c.resize();
    }

    // ============================================================
    // renderConclusion
    // ============================================================
    function renderConclusion() {
        var el = document.getElementById("cui-conclusion");
        if (!el || !data) return;
        var m = data.meta || {};
        var od = data.office_distribution || [];
        var cm = data.clan_marriage || [];
        var topOffice = od.length > 0 ? od[0].office : "--";
        var clans = cm.slice(0, 5).map(function(d){ return "\u300c" + d.target + "\u300d"; }).join("\u3001");

        var html = [
            '<div style="background:linear-gradient(135deg,#F8F0E0,#F0E4C8);border:1px solid #C4A882;border-radius:4px;padding:16px 20px">',
            '<h3 style="font-family:Noto Serif SC,KaiTi,serif;font-size:18px;color:#2C1810;letter-spacing:2px;border-left:3px solid #9B1B1B;padding-left:10px;margin-bottom:14px">\u5386\u53f2\u7ed3\u8bba</h3>',
            '<div style="font-size:13px;color:#4A3728;line-height:2">',

            '<p style="margin-bottom:12px"><strong>\u2460 \u5bb6\u65cf\u5ef6\u7eed\u80fd\u529b</strong><br>',
            '\u6e05\u6cb3\u5d14\u6c0f\u4eba\u7269\u8bb0\u5f55\u8986\u76d6' + (m.dynasty_count || "") + '\u4e2a\u671d\u4ee3\uff0c\u65f6\u95f4\u8de8\u5ea6\u8d85\u8fc7\u5343\u5e74\u3002\u4ece\u9b4f\u664b\u5357\u5317\u671d\u81f3\u660e\u6e05\u65f6\u671f\u5747\u80fd\u53d1\u73b0\u5176\u6210\u5458\u6d3b\u52a8\u75d5\u8ff9\u3002\u867d\u7136\u4e0d\u540c\u671d\u4ee3\u7684\u4eba\u6570\u5b58\u5728\u6ce2\u52a8\uff0c\u4f46\u6574\u4f53\u4e0a\u5448\u73b0\u51fa\u6301\u7eed\u5b58\u5728\u800c\u975e\u77ed\u6682\u5174\u76db\u7684\u7279\u5f81\u3002\u8fd9\u79cd\u8de8\u671d\u4ee3\u5ef6\u7eed\u80fd\u529b\u8bf4\u660e\u6e05\u6cb3\u5d14\u6c0f\u5e76\u975e\u4f9d\u8d56\u4e2a\u522b\u6770\u51fa\u4eba\u7269\uff0c\u800c\u662f\u5f62\u6210\u4e86\u8f83\u4e3a\u7a33\u5b9a\u7684\u5bb6\u65cf\u4f20\u627f\u673a\u5236\u3002</p>',

            '<p style="margin-bottom:12px"><strong>\u2461 \u5b98\u804c\u8d44\u6e90\u79ef\u7d2f</strong><br>',
            '\u5b98\u804c\u7edf\u8ba1\u663e\u793a\uff0c\u300c' + topOffice + '\u300d\u662f\u51fa\u73b0\u9891\u7387\u6700\u9ad8\u7684\u804c\u4f4d\u3002\u523a\u53f2\u5236\u5ea6\u59cb\u4e8e\u897f\u6c49\uff0c\u672c\u4e3a\u76d1\u5bdf\u5730\u65b9\u5b98\u5458\u7684\u4e2d\u592e\u6d3e\u51fa\u673a\u6784\uff1b\u81f3\u4e1c\u6c49\u4ee5\u540e\u9010\u6e10\u6f14\u53d8\u4e3a\u517c\u5177\u76d1\u5bdf\u4e0e\u884c\u653f\u6743\u529b\u7684\u91cd\u8981\u5730\u65b9\u957f\u5b98\u3002\u9664\u523a\u53f2\u5916\uff0c\u53bf\u4ee4\u3001\u53bf\u5c09\u7b49\u5730\u65b9\u5b98\u804c\u4e5f\u5360\u636e\u8f83\u9ad8\u6bd4\u4f8b\u3002\u8fd9\u8868\u660e\u6e05\u6cb3\u5d14\u6c0f\u6210\u5458\u957f\u671f\u6d3b\u8dc3\u4e8e\u5730\u65b9\u6cbb\u7406\u4f53\u7cfb\uff0c\u800c\u975e\u5355\u7eaf\u96c6\u4e2d\u4e8e\u4e2d\u592e\u671d\u5ef7\u3002\u901a\u8fc7\u6301\u7eed\u63a7\u5236\u5730\u65b9\u884c\u653f\u8d44\u6e90\u3001\u79ef\u7d2f\u653f\u6cbb\u7ecf\u9a8c\u5e76\u7ef4\u6301\u793e\u4f1a\u5f71\u54cd\u529b\uff0c\u5bb6\u65cf\u5f97\u4ee5\u5728\u671d\u4ee3\u66f4\u66ff\u4e2d\u4fdd\u6301\u7a33\u5b9a\u5730\u4f4d\uff0c\u8fd9\u53ef\u80fd\u6b63\u662f\u5176\u957f\u671f\u5ef6\u7eed\u7684\u91cd\u8981\u539f\u56e0\u4e4b\u4e00\u3002</p>',

            '<p style="margin-bottom:12px"><strong>\u2462 \u8054\u5a5a\u7f51\u7edc</strong><br>',
            '\u8054\u5a5a\u6570\u636e\u663e\u793a\uff0c\u6e05\u6cb3\u5d14\u6c0f\u4e0e' + cm.length + '\u4e2a\u95e8\u9600\u5bb6\u65cf\u5b58\u5728\u5a5a\u59fb\u8054\u7cfb\uff0c\u4e3b\u8981\u5305\u62ec' + clans + '\u7b49\u3002\u5728\u4e2d\u56fd\u4e2d\u53e4\u65f6\u671f\uff0c\u5a5a\u59fb\u4e0d\u4ec5\u662f\u5bb6\u5ead\u5173\u7cfb\uff0c\u66f4\u662f\u653f\u6cbb\u8054\u76df\u7684\u91cd\u8981\u5f62\u5f0f\u3002\u901a\u8fc7\u4e0e\u5176\u4ed6\u9ad8\u95e8\u58eb\u65cf\u5efa\u7acb\u8054\u5a5a\u5173\u7cfb\uff0c\u6e05\u6cb3\u5d14\u6c0f\u80fd\u591f\u6269\u5927\u793e\u4f1a\u7f51\u7edc\u3001\u5f3a\u5316\u653f\u6cbb\u5408\u4f5c\uff0c\u5e76\u5728\u4e0d\u540c\u5730\u533a\u548c\u653f\u6cbb\u96c6\u56e2\u4e4b\u95f4\u5efa\u7acb\u8054\u7cfb\u3002\u8054\u5a5a\u7f51\u7edc\u4e0d\u4ec5\u53cd\u6620\u5bb6\u65cf\u5173\u7cfb\uff0c\u4e5f\u4f53\u73b0\u4e86\u4e2d\u53e4\u95e8\u9600\u793e\u4f1a\u4e2d\u653f\u6cbb\u8d44\u6e90\u5171\u4eab\u4e0e\u6743\u529b\u6574\u5408\u7684\u673a\u5236\u3002</p>',

            '<p style="margin-bottom:4px"><strong>\u2463 \u7efc\u5408\u7ed3\u8bba</strong><br>',
            '\u6e05\u6cb3\u5d14\u6c0f\u80fd\u591f\u8de8\u8d8a\u591a\u4e2a\u671d\u4ee3\u6301\u7eed\u5b58\u5728\uff0c\u5e76\u975e\u4f9d\u8d56\u5355\u4e00\u56e0\u7d20\uff0c\u800c\u662f\u5bb6\u65cf\u4f20\u627f\u3001\u5730\u65b9\u5b98\u804c\u8d44\u6e90\u79ef\u7d2f\u4e0e\u58eb\u65cf\u8054\u5a5a\u7f51\u7edc\u5171\u540c\u4f5c\u7528\u7684\u7ed3\u679c\u3002\u4eceCBDB\u6570\u636e\u53ef\u4ee5\u770b\u5230\uff0c\u653f\u6cbb\u8d44\u6e90\u3001\u793e\u4f1a\u5173\u7cfb\u4e0e\u5bb6\u65cf\u7ed3\u6784\u4e4b\u95f4\u5b58\u5728\u660e\u663e\u5173\u8054\u3002\u6e05\u6cb3\u5d14\u6c0f\u7684\u53d1\u5c55\u8f68\u8ff9\u5c55\u793a\u4e86\u4e2d\u56fd\u4e2d\u53e4\u65f6\u671f\u95e8\u9600\u58eb\u65cf\u8fd0\u4f5c\u7684\u5178\u578b\u6a21\u5f0f\uff0c\u56e0\u6b64\u53ef\u4ee5\u89c6\u4e3a\u7814\u7a76\u4e2d\u56fd\u53e4\u4ee3\u5927\u5bb6\u65cf\u653f\u6cbb\u4e0e\u793e\u4f1a\u5f71\u54cd\u529b\u7684\u91cd\u8981\u6848\u4f8b\u3002</p>',

            '</div></div>'
        ].join("");
        el.innerHTML = html;
    }

    // ============================================================
    // resize
    // ============================================================
    function resize() {
        Object.keys(charts).forEach(function(k) { if (charts[k]) charts[k].resize(); });
    }

    // ============================================================
    // Public API
    // ============================================================
    return { renderAll: renderAll, resize: resize };
})();
