/**
 * cui_data_loader.js — 加载清河崔氏数据
 */
const CUI_DATA = (function() {
    "use strict";
    var cached = null;
    async function load() {
        if (cached) return cached;
        var url = "data/processed/cui/cui_data.json";
        console.log("[CUI Loader] Fetching:", url);
        try {
            var r = await fetch(url);
            if (!r.ok) throw new Error("HTTP " + r.status);
            cached = await r.json();
            console.log("[CUI Loader] Data source CONFIRMED: data/processed/cui/cui_data.json");
            console.log("[CUI Loader] nodes:", cached.nodes ? cached.nodes.length : 0);
            console.log("[CUI Loader] edges:", cached.links ? cached.links.length : 0);
            if (cached.links) console.log("[CUI Loader] First 10 edges:", cached.links.slice(0, 10));
            if (cached.nodes) console.log("[CUI Loader] First 10 nodes:", cached.nodes.slice(0, 10));
            return cached;
        } catch (e) {
            console.error("[CUI Loader] FAILED:", e);
            throw e;
        }
    }
    function get() { return cached; }
    function getPerson(id) {
        return cached && cached.nodes.find(function(n){return n.id===id;});
    }
    return { load: load, get: get, getPerson: getPerson };
})();
