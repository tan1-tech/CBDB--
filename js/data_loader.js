/**
 * data_loader.js — 加载 network_data.json
 */
const DATA_LOADER = (function() {
    'use strict';

    let cachedData = null;

    async function load() {
        if (cachedData) return cachedData;
        try {
            const resp = await fetch('network_data.json');
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            cachedData = await resp.json();
            console.log('[DataLoader] 加载完成:', cachedData.meta);
            return cachedData;
        } catch (err) {
            console.error('[DataLoader] 加载失败:', err);
            throw err;
        }
    }

    function get() { return cachedData; }

    function getPerson(name) {
        if (!cachedData) return null;
        return cachedData.nodes.find(function(n) { return n.id === name; }) || null;
    }

    function getRelations(name) {
        if (!cachedData) return [];
        return cachedData.links.filter(function(l) {
            return l.source === name || l.target === name;
        });
    }

    function getRelationBetween(a, b) {
        if (!cachedData) return null;
        return cachedData.links.find(function(l) {
            return (l.source === a && l.target === b) || (l.source === b && l.target === a);
        }) || null;
    }

    return { load: load, get: get, getPerson: getPerson, getRelations: getRelations, getRelationBetween: getRelationBetween };
})();
