/**
 * network.js — 北宋文人知识图谱 ECharts 渲染引擎
 * 完整重构版本，修复所有结构性问题
 */
const NETWORK = (function() {
    'use strict';

    // ============================================================
    // 模块变量
    // ============================================================
    let chart = null;
    let allData = null;
    let activeFilters = ['朋友', '师生', '政治盟友', '政敌', '文人交往'];
    let coreTimer = null;
    let searchTimer = null;
    let lastSearchReset = null;

    // ============================================================
    // 常量
    // ============================================================
    var REL_COLORS = {
        '朋友':     '#5B8C5A',
        '师生':     '#4A7AA4',
        '政治盟友': '#B8862D',
        '政敌':     '#B22222',
        '文人交往': '#7B5B7A',
        '兄弟':     '#C0722B'
    };

    var CORE_POSITIONS = {
        '欧阳修': { x: 400, y: 80 },
        '司马光': { x: 240, y: 200 },
        '苏轼':   { x: 560, y: 200 },
        '王安石': { x: 400, y: 340 },
        '曾巩':   { x: 240, y: 480 },
        '苏辙':   { x: 560, y: 480 }
    };

    var CORE_NAMES = ['欧阳修', '司马光', '苏轼', '王安石', '曾巩', '苏辙'];

    // 关系类型覆盖（数据本身无"兄弟"类型时使用）
    var REL_OVERRIDES = {};
    REL_OVERRIDES['苏轼\u2192苏辙'] = '兄弟';
    REL_OVERRIDES['苏辙\u2192苏轼'] = '兄弟';

    // 子关系中文名映射
    var SUB_REL_NAMES = {
        letters: '书信往来',
        literature: '文学交往',
        friend: '朋友',
        teacher: '师生',
        support: '政治盟友',
        opposition: '政敌'
    };

    // ============================================================
    // 篆刻印章 SVG 生成
    // ============================================================
    function createSealSVG(name, size) {
        var chars = name.split('');
        var n = chars.length;
        var fs = Math.round(size * 0.28);
        var lh = size * 0.26;
        var sy = size * 0.5 - (n - 1) * lh * 0.5 + fs * 0.35;
        var texts = '';
        for (var i = 0; i < n; i++) {
            texts += '<text x="' + (size / 2) + '" y="' + (sy + i * lh) + '" text-anchor="middle" font-family="KaiTi,STKaiti,SimSun,serif" font-size="' + fs + '" fill="white" font-weight="bold">' + chars[i] + '</text>';
        }
        var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + size + ' ' + size + '">'
            + '<defs><linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="100%">'
            + '<stop offset="0%" style="stop-color:#D43737"/>'
            + '<stop offset="100%" style="stop-color:#8B1A1A"/>'
            + '</linearGradient></defs>'
            + '<rect x="6" y="6" width="' + (size - 12) + '" height="' + (size - 12) + '" rx="8" fill="url(#sg)" stroke="#6B1010" stroke-width="3"/>'
            + '<rect x="12" y="12" width="' + (size - 24) + '" height="' + (size - 24) + '" rx="4" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>'
            + texts
            + '<line x1="' + (size * 0.25) + '" y1="' + (size * 0.88) + '" x2="' + (size * 0.75) + '" y2="' + (size * 0.88) + '" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>'
            + '</svg>';
        return 'image://data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
    }

    // 印章缓存
    var SEAL_CACHE = {};
    function getSeal(name) {
        if (!SEAL_CACHE[name]) SEAL_CACHE[name] = createSealSVG(name, 80);
        return SEAL_CACHE[name];
    }

    // ============================================================
    // 获取关系的显示类型（含覆盖）
    // ============================================================
    function getRelation(source, target, fallback) {
        var key = source + '\u2192' + target;
        return REL_OVERRIDES[key] || fallback;
    }

    // ============================================================
    // init — 初始化 ECharts
    // ============================================================
    function init(containerId) {
        var dom = document.getElementById(containerId);
        if (!dom) return null;
        chart = echarts.init(dom, null, { renderer: 'canvas' });
        window.addEventListener('resize', function () {
            if (chart) chart.resize();
        });
        startCoreMaintenance();
        return chart;
    }

    // ============================================================
    // render — 渲染图谱
    // ============================================================
    function render(data) {
        if (!chart || !data) return;
        allData = data;

        // ---- 1. 过滤边 ----
        var filteredLinks = [];
        for (var i = 0; i < data.links.length; i++) {
            var l = data.links[i];
            var relType = getRelation(l.source, l.target, l.relation);
            if (activeFilters.indexOf(relType) >= 0) {
                filteredLinks.push(l);
            }
        }

        // ---- 2. 确定可见节点 ----
        var visibleNodeIds = {};
        for (var c = 0; c < CORE_NAMES.length; c++) {
            visibleNodeIds[CORE_NAMES[c]] = true;
        }
        for (var li = 0; li < filteredLinks.length; li++) {
            visibleNodeIds[filteredLinks[li].source] = true;
            visibleNodeIds[filteredLinks[li].target] = true;
        }

        // ---- 3. 构建 ECharts 节点 ----
        var chartNodes = [];
        for (var ni = 0; ni < data.nodes.length; ni++) {
            var n = data.nodes[ni];
            if (!visibleNodeIds[n.id]) continue;

            var isCore = n.is_core ? true : false;
            var level = n.level || 3;
            var pos = CORE_POSITIONS[n.id];
            var nodeSize = isCore ? 90 : (level === 2 ? 28 : 16);

            var node = {
                id: n.id,
                name: n.name,
                value: n.degree || 0,
                category: isCore ? 0 : (level === 2 ? 1 : 2),
                symbolSize: nodeSize,
                x: pos ? pos.x : undefined,
                y: pos ? pos.y : undefined,
                label: {
                    show: true,
                    position: 'bottom',
                    fontFamily: 'KaiTi,STKaiti,SimSun,serif',
                    fontSize: isCore ? 14 : 11,
                    fontWeight: isCore ? 'bold' : 'normal',
                    color: '#2C1810',
                    offset: [0, isCore ? 8 : 4]
                },
                itemStyle: {
                    opacity: 1,
                    shadowBlur: 0
                },
                _raw: n
            };

            if (isCore) {
                node.symbol = getSeal(n.id);
                node.itemStyle = {
                    borderColor: '#8B1A1A',
                    borderWidth: 3,
                    shadowBlur: 10,
                    shadowColor: 'rgba(139,27,27,0.3)'
                };
            } else {
                node.symbol = 'circle';
                node.itemStyle = {
                    color: level === 2 ? '#8B7355' : '#A0926B',
                    borderColor: level === 2 ? '#6B5B4E' : '#8B7D6B',
                    borderWidth: 1
                };
            }
            chartNodes.push(node);
        }

        // ---- 4. 构建 ECharts 边 ----
        var chartLinks = [];
        for (var ei = 0; ei < filteredLinks.length; ei++) {
            var el = filteredLinks[ei];
            var relDisp = getRelation(el.source, el.target, el.relation);
            var color = REL_COLORS[relDisp] || '#999';

            chartLinks.push({
                source: el.source,
                target: el.target,
                value: el.total_weight || 0,
                lineStyle: {
                    color: color,
                    width: Math.min(Math.max((el.total_weight || 1), 1), 8),
                    curveness: 0.3,
                    opacity: 0.7
                },
                _raw: el,
                _relation: relDisp,
                _color: color
            });
        }

        // ---- 5. ECharts Option ----
        var option = {
            backgroundColor: 'transparent',
            series: [{
                type: 'graph',
                layout: "force",

                force: {
                    repulsion: 1000,
                    edgeLength: [200, 400],
                    gravity: 0.03,
                    friction: 0.2,
                    layoutAnimation: true
                },
                roam: true,
                draggable: true,
                data: chartNodes,
                links: chartLinks,
                categories: [
                    { name: '核心人物', itemStyle: { color: '#CC2929' } },
                    { name: '关联人物', itemStyle: { color: '#8B7355' } },
                    { name: '外围人物', itemStyle: { color: '#A0926B' } }
                ],
                edgeSymbol: ['none', 'none'],
                lineStyle: { curveness: 0.3, opacity: 0.6 },
                label: {
                    show: true,
                    fontSize: 12,
                    color: "#333"
                },
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: { width: 4 }
                },
                blur: { opacity: 0.2, lineStyle: { opacity: 0.1 } }
            }]
        };

        chart.setOption(option, true);
        chart.resize();
        setupEvents();
    }

    // ============================================================
    // setupEvents — 点击事件
    // ============================================================
    function setupEvents() {
        if (!chart) return;
        chart.off('click');
        chart.on('click', function (params) {
            if (params.dataType === 'node') {
                onNodeClick(params.data);
            } else if (params.dataType === 'edge') {
                onEdgeClick(params.data);
            }
        });
    }

    // ============================================================
    // onNodeClick — 点击节点 → 人物档案
    // ============================================================
    function onNodeClick(nodeData) {
        if (!nodeData || !nodeData._raw) return;
        renderPersonArchive(nodeData._raw);
    }

    // ============================================================
    // onEdgeClick — 点击边 → 关系画像
    // ============================================================
    function onEdgeClick(edgeData) {
        if (!edgeData || !edgeData._raw) return;
        renderRelationDetail(edgeData._raw, edgeData._relation, edgeData._color);
    }

    // ============================================================
    // renderPersonArchive — 人物档案卡片
    // ============================================================
    function renderPersonArchive(person) {
        var bio = person.bio || {};

        var sealHtml = person.is_core
            ? '<div class="ac-seal"><span>' + person.name.split('').join('</span><span>') + '</span></div>'
            : '';

        var ziHao = '';
        if (bio.zi || bio.hao) {
            ziHao = (bio.zi ? '字 ' + bio.zi : '') + (bio.zi && bio.hao ? '  ' : '') + (bio.hao ? '号 ' + bio.hao : '');
        }

        var infoRows = '';
        if (bio.birth) {
            infoRows += '<div class="ac-row"><span class="ac-label">生 卒</span><span class="ac-value">' + bio.birth + ' — ' + (bio.death || '?') + '</span></div>';
        }
        if (bio.hometown) {
            infoRows += '<div class="ac-row"><span class="ac-label">籍 贯</span><span class="ac-value">' + bio.hometown + '</span></div>';
        }
        if (bio.works) {
            infoRows += '<div class="ac-row"><span class="ac-label">代表作</span><span class="ac-value">' + bio.works + '</span></div>';
        }

        var descHtml = bio.desc ? '<div class="ac-desc">' + bio.desc + '</div>' : '';
        var degreeHtml = '<div class="ac-degree">网络中连接 ' + (person.degree || 0) + ' 人</div>';

        var html = '<div class="archive-card">'
            + '<div class="ac-header">'
                + sealHtml
                + '<div class="ac-name-area">'
                    + '<div class="ac-name">' + person.name + '</div>'
                    + (ziHao ? '<div class="ac-zi">' + ziHao + '</div>' : '')
                + '</div>'
            + '</div>'
            + (infoRows ? '<div class="ac-info">' + infoRows + '</div>' : '')
            + descHtml
            + degreeHtml
            + '</div>';

        var el = document.getElementById('detail-content');
        if (el) el.innerHTML = html;
    }

    // ============================================================
    // renderRelationDetail — 关系画像卡片
    // ============================================================
    function renderRelationDetail(rel, displayRelation, displayColor) {
        var color = displayColor || '#999';
        var relType = displayRelation || rel.relation || '未知';

        var subKeys = [
            { key: 'letters', label: '书信往来' },
            { key: 'literature', label: '文学交往' },
            { key: 'friend', label: '朋友' },
            { key: 'teacher', label: '师生' },
            { key: 'support', label: '政治盟友' },
            { key: 'opposition', label: '政敌' }
        ];

        var maxVal = 0;
        var items = [];
        for (var i = 0; i < subKeys.length; i++) {
            var val = parseInt(rel[subKeys[i].key] || 0, 10);
            if (val > 0) {
                items.push({ label: subKeys[i].label, value: val });
                if (val > maxVal) maxVal = val;
            }
        }
        if (maxVal === 0) maxVal = 1;

        var barsHtml = '';
        for (var j = 0; j < items.length; j++) {
            var pct = (items[j].value / maxVal * 100).toFixed(0);
            var opacity = (0.5 + 0.5 * items[j].value / maxVal).toFixed(2);
            barsHtml += '<div class="rel-bar">'
                + '<span class="rel-bar-label">' + items[j].label + '</span>'
                + '<div class="rel-bar-track"><div class="rel-bar-fill" style="width:' + pct + '%;background-color:' + color + ';opacity:' + opacity + '"></div></div>'
                + '<span class="rel-bar-count">' + items[j].value + '</span>'
                + '</div>';
        }

        var html = '<div class="rel-card">'
            + '<div class="rc-header" style="border-bottom:2px solid ' + color + '">'
                + rel.source + ' × ' + rel.target
            + '</div>'
            + '<div class="rc-row"><span class="rc-label">关系类型</span><span class="rc-value" style="color:' + color + '">' + relType + '</span></div>'
            + '<div class="rc-row"><span class="rc-label">关系强度</span><span class="rc-value">' + (rel.total_weight || 0) + '</span></div>'
            + barsHtml
            + '</div>';

        var el = document.getElementById('detail-content');
        if (el) el.innerHTML = html;
    }

    // ============================================================
    // setFilter — 关系筛选
    // ============================================================
    function setFilter(relation, enabled) {
        var idx = activeFilters.indexOf(relation);
        if (enabled && idx < 0) {
            activeFilters.push(relation);
        } else if (!enabled && idx >= 0) {
            activeFilters.splice(idx, 1);
        }
        if (allData) render(allData);
    }

    // ============================================================
    // searchNode — 搜索人物
    // ============================================================
    function searchNode(keyword) {
        if (searchTimer) clearTimeout(searchTimer);
        if (!keyword || keyword.trim() === '') {
            if (lastSearchReset) clearTimeout(lastSearchReset);
            lastSearchReset = setTimeout(function () {
                clearSearchInternal();
            }, 100);
            return;
        }

        searchTimer = setTimeout(function () {
            doSearch(keyword.trim());
        }, 200);
    }

    function doSearch(kw) {
        if (!allData || !chart) return;

        // 查找匹配人物
        var matchedNode = null;
        for (var i = 0; i < allData.nodes.length; i++) {
            if (allData.nodes[i].name.indexOf(kw) >= 0) {
                matchedNode = allData.nodes[i];
                break;
            }
        }
        if (!matchedNode) return;

        // 收集关联人物
        var highlightSet = {};
        highlightSet[matchedNode.id] = true;
        for (var j = 0; j < allData.links.length; j++) {
            var l = allData.links[j];
            if (l.source === matchedNode.id) highlightSet[l.target] = true;
            if (l.target === matchedNode.id) highlightSet[l.source] = true;
        }

        // 高亮节点
        var opt = chart.getOption();
        var data = opt.series[0] && opt.series[0].data;
        if (!data) return;

        for (var k = 0; k < data.length; k++) {
            var d = data[k];
            if (highlightSet[d.id]) {
                d.itemStyle = d.itemStyle || {};
                d.itemStyle.opacity = 1;
                d.itemStyle.shadowBlur = 20;
                d.itemStyle.shadowColor = 'rgba(184,134,11,0.8)';
                d.itemStyle.borderColor = '#B8860B';
                d.itemStyle.borderWidth = d._raw && d._raw.is_core ? 4 : 3;
            } else {
                d.itemStyle = d.itemStyle || {};
                d.itemStyle.opacity = 0.15;
                d.itemStyle.shadowBlur = 0;
                if (d._raw && !d._raw.is_core) {
                    d.itemStyle.borderWidth = 0;
                }
            }
        }
        chart.setOption({ series: [{ data: data }] });

        // 显示提示
        chart.dispatchAction({
            type: 'showTip',
            seriesIndex: 0,
            name: matchedNode.id
        });

        // 显示档案
        renderPersonArchive(matchedNode);
    }

    function clearSearchInternal() {
        if (!chart) return;
        var opt = chart.getOption();
        var data = opt.series[0] && opt.series[0].data;
        if (!data) return;
        for (var i = 0; i < data.length; i++) {
            data[i].itemStyle = data[i].itemStyle || {};
            data[i].itemStyle.opacity = 1;
            data[i].itemStyle.shadowBlur = data[i]._raw && data[i]._raw.is_core ? 10 : 0;
            data[i].itemStyle.borderColor = data[i]._raw && data[i]._raw.is_core ? '#8B1A1A' : undefined;
            data[i].itemStyle.borderWidth = data[i]._raw && data[i]._raw.is_core ? 3 : 0;
        }
        chart.setOption({ series: [{ data: data }] });
    }

    // ============================================================
    // 核心人物位置维护
    // ============================================================
    function startCoreMaintenance() {
        stopCoreMaintenance();
        coreTimer = setInterval(function () {
            try {
                if (!chart) return;
                var opt = chart.getOption();
                var data = opt.series[0] && opt.series[0].data;
                if (!data) return;
                var changed = false;
                for (var i = 0; i < data.length; i++) {
                    var pos = CORE_POSITIONS[data[i].id];
                    if (pos) {
                        var dx = Math.abs(parseFloat(data[i].x || 0) - pos.x);
                        var dy = Math.abs(parseFloat(data[i].y || 0) - pos.y);
                        if (dx > 2 || dy > 2) {
                            data[i].x = pos.x;
                            data[i].y = pos.y;
                            changed = true;
                        }
                    }
                }
                if (changed) chart.setOption({ series: [{ data: data }] });
            } catch (e) { /* core maintenance error ignored */ }
        }, 500);
    }

    function stopCoreMaintenance() {
        if (coreTimer) {
            clearInterval(coreTimer);
            coreTimer = null;
        }
    }

    // ============================================================
    // resize — 窗口调整
    // ============================================================
    function resize() {
        if (chart) chart.resize();
    }

    // ============================================================
    // Public API
    // ============================================================
    return {
        init: init,
        render: render,
        setFilter: setFilter,
        searchNode: searchNode,
        startCoreMaintenance: startCoreMaintenance,
        stopCoreMaintenance: stopCoreMaintenance,
        resize: resize
    };
})();
